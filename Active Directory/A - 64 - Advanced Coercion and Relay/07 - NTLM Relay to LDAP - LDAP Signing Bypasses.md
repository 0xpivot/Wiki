---
tags: [active-directory, coercion, relay, vapt]
difficulty: expert
module: "64 - Advanced Coercion and Relay Attacks"
topic: "64.07 NTLM Relay to LDAP"
---

# 07 - NTLM Relay to LDAP - LDAP Signing Bypasses

## 1. Introduction to NTLM Relay to LDAP

NTLM Relaying to LDAP is one of the most devastating attack paths in an Active Directory environment. LDAP (Lightweight Directory Access Protocol) is the core directory service of Active Directory, running on ports 389 (LDAP) and 636 (LDAPS). Because LDAP dictates the permissions, structures, and configurations of the entire domain, relaying a highly privileged authentication (like a Domain Admin or a Domain Controller machine account) to LDAP allows an attacker to execute domain-altering actions without knowing the victim's password.

By default, NTLM authentication over LDAP was historically not secured against relay attacks. Attackers could coerce an authentication (using tools like Coercer or PetitPotam), capture the incoming SMB or HTTP request, and forward the NTLM Type 1, 2, and 3 messages to the Domain Controller's LDAP service.

Once the relay is successful, the attacker possesses an LDAP session running under the context of the coerced account.

## 2. Architectural Flow & ASCII Diagram

```text
  +-----------------------+                            +-----------------------+
  |    Victim Machine     |                            |   Domain Controller   |
  | (e.g., SQL Srv / DC)  |                            |   (LDAP Port 389)     |
  +-----------+-----------+                            +-----------+-----------+
              |                                                    ^
              | 1. Attacker Coerces Auth                           |
              |    (PetitPotam, PrinterBug)                        |
              V                                                    |
  +-----------+-----------+                                        |
  |    Attacker Node      |  3. Relays NTLM messages to LDAP       |
  |    (ntlmrelayx.py)    |========================================+
  +-----------+-----------+                                        |
              ^                                                    |
              | 2. Victim sends NTLM Negotiate                     |
              |    (SMB or HTTP)                                   |
              |                                                    |
              |                                                    |
              |                                                    |
              | 4. Attacker performs LDAP actions as Victim        |
              |    - Create Machine Account                        |
              |    - Modify msDS-AllowedToActOnBehalfOfOtherIdentity
              |    - Write Dacl (Shadow Credentials)               |
              +----------------------------------------------------+
```

## 3. Mechanisms of LDAP Attacks via Relay

When `ntlmrelayx.py` establishes an authenticated LDAP session on behalf of the victim, it can execute several predefined or custom attacks depending on the privileges of the relayed account.

### 3.1. Relaying a Standard User Account
If a standard user is relayed to LDAP, the attacker typically has limited write access but extensive read access.
- **Information Gathering:** Dumping the domain user list, groups, and ACLs (equivalent to BloodHound enumeration).
- **Machine Account Creation:** By default, the `MachineAccountQuota` (MAQ) in AD is set to 10. This means any authenticated user can create up to 10 computer accounts in the domain. `ntlmrelayx` can do this automatically:
  ```bash
  ntlmrelayx.py -t ldap://192.168.1.100 --add-computer
  ```
  The newly created machine account (and its known password) can later be used for attacks like RBCD.

### 3.2. Relaying a High Privileged Account (Domain Admin / Enterprise Admin)
If a DA is relayed, the attacker effectively has complete control over LDAP.
- **DCSync Preparation:** The attacker can grant their own low-privileged account `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` rights on the domain root. This enables the low-privileged account to run secretsdump/DCSync.
  ```bash
  ntlmrelayx.py -t ldap://192.168.1.100 --escalate-user attacker_user
  ```
- **Password Resets:** Forcing a password change for other administrative users via LDAP modification.

### 3.3. Relaying a Machine Account
When a machine account (e.g., `SERVER01$`) is relayed, it usually only has modification rights over *itself*. This is the core of the **Resource-Based Constrained Delegation (RBCD)** attack and **Shadow Credentials**.
- **RBCD:** The attacker modifies the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of `SERVER01$` to point to an attacker-controlled machine account.
- **Shadow Credentials:** The attacker writes a new Key Credential Link (`msDS-KeyCredentialLink`) to `SERVER01$`, allowing them to request a TGT as the machine account using PKINIT.

## 4. LDAP Security Mechanisms: Signing and Channel Binding

Over the years, Microsoft has introduced mitigations to prevent LDAP relaying. Understanding these is crucial for modern VAPT engagements.

### 4.1. LDAP Signing
LDAP Signing requires that the LDAP session be protected by a session key negotiated during the NTLM exchange. 
- If an attacker relays NTLM to an LDAP server requiring signing, the Domain Controller will accept the authentication but will demand that all subsequent LDAP queries be signed with the NTLM session key.
- Because the attacker does not have the victim's password, they cannot calculate the NTLM session key. Thus, the attacker cannot sign the LDAP packets, and the attack fails.
- **Default State:** Historically disabled. Modern environments usually enforce this via GPO ("Domain controller: LDAP server signing requirements" set to "Require signing").

### 4.2. LDAP Channel Binding (EPA - Extended Protection for Authentication)
When an attacker tries to bypass LDAP signing by relaying to **LDAPS** (LDAP over SSL, port 636), the traffic is encrypted by TLS.
- Channel Binding Tokens (CBT) tie the inner NTLM authentication to the outer TLS channel.
- The client hashes the TLS certificate of the server it thinks it is connecting to and includes this hash in the NTLM authentication message.
- If the attacker relays this to the DC, the DC compares the hash in the NTLM message with its own TLS certificate hash. Since the client generated the hash based on the attacker's TLS certificate, they won't match, and the DC drops the authentication.

## 5. Bypasses and Downgrade Attacks

Despite these defenses, misconfigurations and protocol flaws have allowed attackers to bypass them.

### 5.1. Drop MIC (Message Integrity Code) Bypass
CVE-2019-1040 (Drop MIC) was a critical vulnerability where an attacker could strip the Message Integrity Code (MIC) from the NTLM Type 3 message.
- The MIC ensures that the NTLM negotiation flags (like the requirement for signing) have not been tampered with.
- By dropping the MIC, attackers could modify the flags to tell the server "I don't support signing", bypassing SMB and LDAP signing requirements.
- **Status:** Patched in 2019, but unpatched legacy systems may still exist.

### 5.2. Relaying to LDAPS without Channel Binding Enforced
Many organizations enable LDAPS but fail to enforce Channel Binding.
- If `LdapEnforceChannelBinding` is set to `0` (Disabled) or `1` (Supported but not required), an attacker can relay NTLM from an unencrypted channel (SMB/HTTP) to LDAPS.
- Because the relay is happening over TLS, the session is naturally protected by the SSL layer, satisfying the "LDAP Signing" requirement dynamically without needing the NTLM session key for individual packet signing.
- **Tooling:**
  ```bash
  ntlmrelayx.py -t ldaps://192.168.1.100 --delegate-access
  ```

### 5.3. WebDAV / HTTP Coercion to bypass SMB Signing Flags
When coercing over SMB, the client includes flags indicating SMB signing support. By forcing the victim to authenticate to the attacker via HTTP (using WebDAV coercion like `\\attacker@80\path`), the authentication originates from the WebClient service.
- HTTP does not enforce signing natively like SMB.
- The NTLM messages generated over HTTP lack certain flags, making them cleaner for relaying to LDAP.

## 6. Execution Examples

### Example 1: Relaying to LDAP for DCSync
1. Setup relay targeting DC LDAP:
   ```bash
   ntlmrelayx.py -t ldap://10.10.10.10 -smb2support --escalate-user lowprivuser
   ```
2. Coerce a Domain Admin or the DC itself (if another DC exists) to authenticate to the attacker over HTTP or SMB.
3. Observe `lowprivuser` gaining DCSync rights.

### Example 2: Relaying to LDAPS for RBCD
1. Setup relay to LDAPS, assuming Channel Binding is not strictly enforced:
   ```bash
   ntlmrelayx.py -t ldaps://10.10.10.10 -smb2support --delegate-access
   ```
2. Coerce target machine `VICTIM_SRV$` to authenticate to the attacker.
3. `ntlmrelayx` creates a new machine account and modifies `VICTIM_SRV$`'s `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute.

## 7. Mitigations and Defenses

1. **Enforce LDAP Signing:** Set the `LdapEnforceChannelBinding` registry key and configure the GPO "Domain controller: LDAP server signing requirements" to "Require signing".
2. **Enforce LDAP Channel Binding:** Set `LdapEnforceChannelBinding` to `2` (Strict) on Domain Controllers. This explicitly prevents relaying to LDAPS.
3. **Patching:** Ensure all DCs are patched against CVE-2019-1040 and related NTLM relay vulnerabilities.
4. **Disable NTLM:** The ultimate fix is to phase out NTLM entirely in favor of Kerberos. Disable NTLM on specific high-risk servers or globally if infrastructure permits.
5. **EPA Enforcement:** Ensure Extended Protection for Authentication is enabled across the domain for all compatible services.

## Real-World Attack Scenario

During an internal red team engagement, an attacker gained initial access as a standard domain user (`t.stark`) on `10.10.10.50`. The environment consisted of several Windows Server 2016 Domain Controllers, but legacy applications prevented the administrators from enforcing LDAP Signing domain-wide.

The attacker configured `ntlmrelayx.py` to target the primary Domain Controller's LDAP service, instructing it to grant DCSync privileges to their compromised account if a high-privileged authentication was captured:
```bash
impacket-ntlmrelayx -t ldap://10.10.10.10 -smb2support --escalate-user t.stark
```

Knowing that a Domain Admin routinely logged into a jump server (`JUMP01`), the attacker utilized an LLMNR poisoning attack via Responder to spoof a mistyped network share (`\\FILESRV-BAK`). When the Domain Admin attempted to access the non-existent share, their machine broadcasted an LLMNR request, which Responder answered, directing the SMB authentication to the attacker's IP.

`ntlmrelayx` intercepted the incoming NTLM authentication from the Domain Admin. Because the authentication occurred over SMB, but the relay target was LDAP, the tool repackaged the NTLM messages. Since the DC did not strictly enforce LDAP Signing (`LDAPServerIntegrity = 1`), it accepted the relayed Type 3 authentication message.

Operating under the context of the Domain Admin via the relayed LDAP session, `ntlmrelayx` automatically modified the ACLs on the domain root object (`DC=corp,DC=local`), granting the `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` extended rights to the `t.stark` user account.

With DCSync rights successfully provisioned, the attacker stopped the relay listener and used `secretsdump.py` with their original, low-privileged credentials to dump the domain's password hashes:
```bash
secretsdump.py corp.local/t.stark:Password123@10.10.10.10 -just-dc-user krbtgt
```
The attacker secured the `krbtgt` hash, effectively achieving complete forest compromise in under an hour.

## 8. Chaining Opportunities
- [[06 - Coercer - The Universal Coercion Toolkit]] – Used to generate the incoming NTLM traffic required for the relay.
- [[10 - Resource-Based Constrained Delegation RBCD via Relay]] – The primary post-relay attack path when targeting machine accounts.
- [[11 - Shadow Credentials Abuse]] – An alternative to RBCD when relaying a machine account to LDAP.
- [[12 - Active Directory Certificate Services AD CS ESC8]] – Another highly impactful relay target if LDAP signing is enforced.

## 9. Related Notes
- [[02 - NTLM Authentication Deep Dive]]
- [[03 - Extended Protection for Authentication EPA]]
- [[15 - Machine Account Quota MAQ Abuse]]
- [[16 - Kerberos Delegation Deep Dive]]

## 10. Packet Level Analysis of Drop MIC

The Drop MIC attack (CVE-2019-1040) is fundamentally a manipulation of the NTLM Type 3 message. To understand how `ntlmrelayx` performs this, one must inspect the NTLMSSP packets.

1. **NTLM Type 1 (Negotiate):** The victim sends its supported features.
2. **NTLM Type 2 (Challenge):** The server (or relay tool acting as the server) responds with a challenge and its supported features (including `NTLMSSP_NEGOTIATE_SIGN` and `NTLMSSP_NEGOTIATE_ALWAYS_SIGN`).
3. **NTLM Type 3 (Authenticate):** The victim calculates the response.

In a normal exchange, the Type 3 message contains a `MIC` (Message Integrity Code) calculated over all three NTLM messages. It also contains the `NTLMSSP_NEGOTIATE_SIGN` flags. 
If an attacker simply changes the flags to remove the signing requirement, the target server will recalculate the MIC, see that it doesn't match the one in the packet (since the attacker changed the flags), and reject the authentication.

**The Bypass:** The CVE-2019-1040 vulnerability existed because Microsoft's NTLM implementation allowed an attacker to completely remove the MIC field from the Type 3 message and remove the `MSVAvFlags` (which indicate a MIC is present). If these were missing, the server would happily process the authentication without verifying the integrity of the negotiation flags, allowing the attacker to strip the signing requirement without rejection.

## 11. Auditing LDAP Configurations via PowerShell

Pentesters and defenders must regularly audit the Active Directory environment to identify if it is vulnerable to LDAP relaying. This can be done efficiently using PowerShell and built-in AD cmdlets.

### Auditing LDAP Signing Requirement
You can query the registry of the Domain Controllers to verify the `LDAPServerIntegrity` setting.
```powershell
# Run from a domain-joined machine with appropriate permissions
Invoke-Command -ComputerName (Get-ADDomainController -Filter *).Name -ScriptBlock {
    Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\NTDS\Parameters" -Name "LDAPServerIntegrity" -ErrorAction SilentlyContinue
}
```
- `Value = 1` : Disabled (Vulnerable)
- `Value = 2` : Required (Secure)

### Auditing LDAP Channel Binding (EPA)
To check if LDAPS enforcement is configured:
```powershell
Invoke-Command -ComputerName (Get-ADDomainController -Filter *).Name -ScriptBlock {
    Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\NTDS\Parameters" -Name "LdapEnforceChannelBinding" -ErrorAction SilentlyContinue
}
```
- `Value = 0` : Disabled (Vulnerable to LDAPS relay)
- `Value = 1` : Supported but not required (Vulnerable to LDAPS relay)
- `Value = 2` : Always (Secure)

## 12. Cross-Forest Relaying Considerations

Relaying to LDAP is not strictly limited to intra-domain targets. If a two-way forest trust exists, an attacker can coerce a DC from Forest A and relay it to the LDAP service of a DC in Forest B.
However, Foreign Security Principals and trust boundaries introduce complexities:
- Cross-forest delegations and RBCD are often restricted by SID filtering.
- If SID filtering is relaxed or specifically configured to allow certain delegations across the trust, the attacker might compromise Forest B using credentials extracted from Forest A.
- `ntlmrelayx` must be targeted carefully, specifying the correct domain and LDAP endpoint, and the attacker must ensure the coerced account actually has privileges in the foreign domain.

## 13. Attack Surface Reduction Tactics

To systematically eliminate the attack surface for LDAP Relaying, organizations should adopt the following tiered strategy:

1. **Immediate Tier:** 
   Identify and remove unneeded RPC services on critical assets. Disable the WebClient service globally using GPO to prevent WebDAV coercion methods from triggering HTTP traffic towards attacker listeners.
2. **Short-term Tier:** 
   Enable LDAP Signing in Audit Mode. Review Event ID 2889 (which logs unsigned LDAP binds) in the Directory Service event log to identify legacy applications that will break when enforcement is enabled.
3. **Long-term Tier:** 
   Move all domain clients to LDAPS with strict EPA enforcement and disable NTLM entirely in favor of Kerberos for LDAP queries. Implement Tiered Administration models to ensure high-privilege accounts cannot be coerced from low-tier segments.
