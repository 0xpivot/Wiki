---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 31"
---

# Object Level Authorization (Active Directory DACL/SACL Abuse)

Object-level authorization is the cornerstone of access control in enterprise environments, particularly within Active Directory (AD). When Security Descriptors (SDs) and Discretionary Access Control Lists (DACLs) are misconfigured, attackers can bypass intended authorization models, leading to complete domain compromise. This module explores the technical depth, offensive methodologies, and defensive strategies surrounding object-level authorization failures.

## Formal Technical Questions

### Q1: Explain how Active Directory Discretionary Access Control Lists (DACLs) implement Object Level Authorization and how misconfigurations lead to domain compromise.
Active Directory utilizes a complex security model based on Security Descriptors (SDs). Every object in AD (users, groups, computers, OUs) has an SD that contains a DACL and a SACL (System Access Control List). The DACL is an ordered list of Access Control Entries (ACEs). Each ACE defines an identity (SID) and the specific permissions (Access Mask) granted or denied to that identity over the object.

Misconfigurations occur when excessive permissions are granted to non-administrative principals. For instance, if `Domain Users` is granted `GenericAll` (Full Control) over a target user object, any authenticated user can reset that target's password, modify its attributes, or configure Resource-Based Constrained Delegation (RBCD). When this target is a highly privileged account (e.g., Domain Admin) or a system critical to the domain's function (e.g., a Domain Controller), this object-level authorization failure creates a direct path to total domain compromise. The most critical misconfigurations involve rights like `GenericAll`, `GenericWrite`, `WriteOwner`, `WriteDACL`, and extended rights such as `DS-Replication-Get-Changes` (required for DCSync).

### Q2: What is the exact sequence of LDAP and RPC calls when a user attempts an unauthorized DCSync attack, and why does the object level authorization fail?
The DCSync attack simulates the behavior of a Domain Controller via the Directory Replication Service (DRS) Remote Protocol (MS-DRSR).
1. **Binding:** The attacker authenticates and binds to the target DC via RPC over SMB/TCP, targeting the `drsuapi` RPC interface (UUID `e3514235-4b06-11d1-ab04-00c04fc2dcd2`).
2. **CrackNames:** The attacker calls `DRSCrackNames` to resolve the target domain name into a Distinguished Name (DN).
3. **GetNCChanges:** The attacker calls `IDL_DRSGetNCChanges`, requesting replication data for specific objects (e.g., `krbtgt`).

Object-level authorization fails if the executing principal holds the `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` extended rights on the Domain NC (Naming Context) object. By default, only Domain Controllers and Domain Admins possess these rights. If an attacker has previously abused an object-level authorization flaw (e.g., `WriteDACL` on the domain root) to inject an ACE granting themselves these rights, the DC evaluates the SDDL, sees the malicious ACE, and authorizes the replication request, returning the NTLM hashes.

### Q3: How do Access Control Entries (ACEs) with `WriteOwner` or `WriteDACL` permissions allow an attacker to bypass object-level authorization?
`WriteOwner` and `WriteDACL` represent structural control over an object's authorization boundaries. 
- **WriteOwner:** Allows the principal to change the owner of the object to themselves. By default, the owner of an object has implicit rights to modify the DACL (known as `WRITE_DAC` or `WriteDACL`).
- **WriteDACL:** Allows the principal to modify the DACL directly without needing to be the owner.

An attacker holding `WriteOwner` will first change the object's owner to their compromised account. They then implicitly gain `WriteDACL`. With `WriteDACL`, the attacker modifies the object's DACL to add an ACE granting themselves `GenericAll`. At this point, the attacker has complete object-level authorization over the target, entirely bypassing the original intended security posture. This is often executed via PowerView's `Add-DomainObjectAcl` or impacket's `dacledit.py`.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You have a foothold as a low-privileged user. BloodHound shows a path `GenericWrite` to a server object. Walk me through the exploitation.
**Scenario Context:** `GenericWrite` grants the ability to write to all non-protected properties of an object.
**Execution:**
1. I would utilize `GenericWrite` to modify the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of the target server object. This attribute controls Resource-Based Constrained Delegation (RBCD).
2. I would create a new computer account in the domain (using `StandIn` or `addcomputer.py`), exploiting the default `MachineAccountQuota` (usually 10). Let's call it `EVILPC$`.
3. I update the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of the target server to include the SID of `EVILPC$`.
4. Using Rubeus or Impacket (`getST.py`), I request a Service Ticket (S4U2Self/S4U2Proxy) acting as a high-privileged user (e.g., Administrator) from `EVILPC$` to the target server.
5. The DC grants the ticket because of the RBCD configuration I instituted via the object-level authorization flaw (`GenericWrite`). I then Pass-the-Ticket to gain SYSTEM access on the server.

### Q2: During a threat hunt, you notice anomalous Event ID 4662 logs targeting the Domain partition. How do you determine if this is a legitimate replication event or an object authorization bypass?
**Investigation Methodology:**
Event ID 4662 records an operation performed on an object.
1. **Filter by Access Mask:** I would look for the specific Access Mask `0x100` (Control Access) and the Object Type `%{19195a5b-6da0-11d0-afd3-00c04fd930c9}` or `%{1131f6aa-9c07-11d1-f79f-00c04fc2dcd2}` (Replicating Directory Changes).
2. **Identify the Subject:** Legitimate replication is performed by machine accounts of Domain Controllers (e.g., `DC01$`). If the `SubjectUserName` is a standard user, a service account, or a non-DC machine account, this is highly anomalous.
3. **Correlate with 4670 (Permissions Change):** I would query the SIEM for preceding Event ID 4670 (Authorization Rule Changed) or 5136 (Directory Service Object Modified) targeting the Domain Head object. This would reveal if the attacker recently modified the DACL to grant themselves the necessary object-level authorization rights before executing the DCSync.

### Q3: You've acquired `WriteDACL` over a Group Policy Object (GPO). How do you abuse this object-level authorization flaw to compromise the domain, and what artifacts are left behind?
**Exploitation:**
1. With `WriteDACL`, I grant myself `GenericAll` over the GPO.
2. I use tools like SharpGPOAbuse or native Group Policy PowerShell modules to inject a malicious Immediate Task or modify the Registry settings within the GPO.
3. This task executes an obfuscated payload (e.g., Cobalt Strike beacon) running as SYSTEM.
4. Once Group Policy refreshes on the clients/servers linked to the GPO (or upon reboot), the payload executes, granting me widespread SYSTEM access across the domain.

**Artifacts:**
- Event ID 5136 (Directory Service Object Modified) showing changes to the `nTSecurityDescriptor` attribute of the GPO's AD object.
- Event ID 5136 showing modifications to the `versionNumber` attribute.
- File system artifacts in the SYSVOL share (`\\domain.local\SYSVOL\domain.local\Policies\{GPO-GUID}\Machine\Preferences\ScheduledTasks\ScheduledTasks.xml`).
- Event ID 4698 (A scheduled task was created) on the endpoint systems executing the payload.

## Deep-Dive Defensive Questions

### Q1: How do you architect a detection engineering pipeline to identify anomalous DACL modifications on high-value AD objects in near real-time?
**Architecture Design:**
1. **Audit Policy:** Ensure "Audit Directory Service Changes" and "Audit Directory Service Access" are set to Success/Failure via Default Domain Controllers Policy.
2. **SACL Configuration:** Apply granular SACLs specifically to high-value objects (AdminSDHolder, Domain Root, Tier 0 OUs, Domain Admins group). The SACL must audit `WriteDACL`, `WriteOwner`, and `GenericAll` modifications.
3. **Log Collection:** Forward Event IDs 4670, 5136, and 4662 from all DCs via Windows Event Forwarding (WEF) to a central SIEM.
4. **Enrichment & Parsing:** Use a parsing pipeline (e.g., Logstash or Splunk Heavy Forwarder) to translate the raw SDDL strings in the logs into human-readable formats (identifying the SIDs and access masks).
5. **Detection Logic:** Implement stateful KQL/SPL rules. For example, trigger an alert if Event ID 5136 modifies `nTSecurityDescriptor` on `CN=AdminSDHolder,CN=System,DC=domain,DC=com` and the `SubjectUserName` is not in the "Approved AD Administrators" lookup table.

### Q2: Discuss the role of Security Descriptor Definition Language (SDDL) in auditing object-level authorization, and provide a PowerShell snippet to extract and parse SDDL for sensitive groups.
SDDL is a string representation of a Security Descriptor. It encodes the Owner (O:), Group (G:), DACL (D:), and SACL (S:). In auditing, SDDL provides the exact, immutable cryptographic truth of an object's authorization boundaries. Security tools must parse SDDL to determine effective permissions.

**PowerShell Snippet:**
```powershell
Import-Module ActiveDirectory
$GroupDN = (Get-ADGroup "Domain Admins").DistinguishedName
$ACL = Get-Acl "AD:\$GroupDN"
$SDDL = $ACL.Sddl

Write-Host "Raw SDDL: $SDDL" -ForegroundColor Yellow

# Parse the Access Control Entries manually via ADSI
$DirectoryEntry = [ADSI]"LDAP://$GroupDN"
$SecurityDescriptor = $DirectoryEntry.psbase.ObjectSecurity
foreach ($Access in $SecurityDescriptor.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])) {
    Write-Output "Identity: $($Access.IdentityReference)"
    Write-Output "AccessControlType: $($Access.AccessControlType)"
    Write-Output "ActiveDirectoryRights: $($Access.ActiveDirectoryRights)"
    Write-Output "----------------------------------"
}
```

### Q3: What are the forensic implications of an attacker using an invisible LDAP modify operation (e.g., modifying `msDS-KeyCredentialLink`) versus standard RPC calls to bypass object authorization?
When attackers modify properties via direct LDAP calls, they bypass many traditional RPC-based logging mechanisms.
- **RPC Context:** Standard administration tools (like ADUC) often use RPC (SAMR/LSARPC) which generate specific Event IDs and are easily intercepted by EDR solutions monitoring RPC endpoints.
- **LDAP Context:** Modifying `msDS-KeyCredentialLink` via raw LDAP operations (using tools like Whisker) directly manipulates the Directory Information Tree. This generates Event ID 5136 (Directory Service Object Modified) but lacks the rich context of RPC logs.
- **Forensic Challenge:** The payload for `msDS-KeyCredentialLink` is a complex binary blob (KeyCredential structure). Forensically, analysts must extract this blob from the 5136 log or the live AD database (`ntds.dit`), parse the BCRYPT_RSAKEY_BLOB, and compare the public key against known attacker tools or legitimate MDM solutions (like Intune or Windows Hello for Business) to determine if the object-level authorization was maliciously bypassed.

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
|               Active Directory Object Level Authorization Abuse                   |
|                                                                                   |
|  [Attacker] (Low Priv)                               [Target Object (GPO)]        |
|      |                                                        |                   |
|      | 1. BloodHound identifies path: WriteDACL               |                   |
|      |------------------------------------------------------->|                   |
|      |                                                        |                   |
|      | 2. Add-DomainObjectAcl (Modify SDDL)                   |                   |
|      |    O:DA G:DA D:(A;;GA;;;S-1-5-21...[Attacker SID])     |                   |
|      |=======================================================>|                   |
|      |                                                        |                   |
|      | 3. Authorization Bypass Successful                     |                   |
|      |<=======================================================|                   |
|      |                                                        |                   |
|      | 4. Inject Malicious Scheduled Task                     |                   |
|      |------------------------------------------------------->|                   |
|                                                                                   |
|  [Domain Controller]                              [Domain Joined Workstations]    |
|      |                                                        |                   |
|      | 5. Event ID 5136 (nTSecurityDescriptor modified)       |                   |
|      |    -> Alert triggered in SIEM                          |                   |
|      |                                                        |                   |
|      |                                  6. GPUpdate /force    |                   |
|      |------------------------------------------------------->|                   |
|                                                               |                   |
|                                                               * SYSTEM Shell Call |
+-----------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

During a major incident response engagement for a financial institution, the threat actors gained their initial foothold via a classic spear-phishing payload, compromising a standard user account in the HR department. The perimeter was heavily secured, and network-level segmentation prevented lateral movement via SMB or RDP.

The attackers utilized BloodHound via a SOCKS proxy to map the Active Directory authorization structures. They discovered a long-forgotten object-level authorization flaw: an IT Helpdesk group, which the compromised HR user was inadvertently nested into, possessed `GenericWrite` permissions over the `Exchange Servers` organizational unit (OU). 

Instead of noisy exploits, the attackers used this object-level authorization bypass to push a malicious Computer object into the OU and modified the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of a primary Exchange server. By generating a forged service ticket via RBCD, they bypassed standard network authentication protocols. They gained SYSTEM on the Exchange server, extracted the domain's machine account hash, and subsequently escalated to Domain Admin, executing a devastating ransomware deployment 48 hours later. The entire operation hinged on a single misconfigured Access Control Entry in the directory.

## Chaining Opportunities

- **BOLA to Broken Authentication:** Gaining object-level authorization to modify a user's `UserAccountControl` attribute to set `DONT_REQUIRE_PREAUTH`, chaining directly into AS-REP Roasting (Broken Authentication).
- **BOLA to Function Level Authorization Bypass:** Modifying group memberships via `GenericAll` to add an attacker to a group with `SeEnableDelegationPrivilege`, allowing them to manipulate function-level impersonation mechanisms.
- **BOLA to Resource Consumption:** Gaining `GenericWrite` over DNS Node objects in AD-Integrated DNS to corrupt essential records, causing massive network misdirection and resource starvation across the domain.

## Related Notes
- [[Active Directory Access Control and ACEs]]
- [[BloodHound Edge Types and Graph Theory]]
- [[Resource-Based Constrained Delegation (RBCD)]]
- [[Windows Event Logging for Threat Hunters]]
- [[DCSync and Directory Replication Services]]
- [[SDDL Parsing and Security Descriptors]]
