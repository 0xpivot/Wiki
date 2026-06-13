---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 70"
---

# QnA - AD Module 70: DCSync Attacks

## Architecture Overview: DCSync Mechanism

```text
+-------------------------------------------------------------+
|                      DCSync Architecture                    |
+-------------------------------------------------------------+
| [Attacker Machine]                                          |
| (Running Mimikatz / Impacket secretsdump)                   |
| Requires: Replicating Directory Changes Privileges          |
|                                                             |
|  1. Attacker binds to Domain Controller via RPC             |
|     (MS-DRSR Protocol - Directory Replication Service)      |
|                                                             |
|  2. Sends IDL_DRSGetNCChanges request                       |
|     "Hello, I am a Domain Controller. Please send me        |
|      the updated password hashes for User X."               |
+-------------------------------------------------------------+
               |
               | (RPC over TCP/IP)
               v
+-------------------------------------------------------------+
| [Target Domain Controller]                                  |
|                                                             |
|  3. Validates privileges of requesting account              |
|     (Checks for DS-Replication-Get-Changes, etc.)           |
|                                                             |
|  4. Retrieves requested secrets from NTDS.dit               |
|                                                             |
|  <-- 5. Returns NTLM hashes, Kerberos keys, and history     |
+-------------------------------------------------------------+
```

## Formal Technical Questions

### Q1: Explain the exact underlying API and protocol that a DCSync attack abuses. Why is it so difficult to patch?
**Answer:**
A DCSync attack abuses the **Directory Replication Service Remote Protocol (MS-DRSR)**. This protocol is the legitimate mechanism that Microsoft Domain Controllers use to replicate Active Directory objects and password hashes among themselves to ensure consistency across the forest.
Specifically, DCSync tools (like Mimikatz `lsadump::dcsync`) utilize the `IDL_DRSGetNCChanges` (or `DSGetNCChanges`) API call. The tool impersonates a Domain Controller and asks the target DC to replicate the AD objects (including the NT hash, LM hash, and password history) of a specific user or the entire domain.
**Why it's difficult to patch:** It cannot be "patched" because it is not a vulnerability; it is a core feature of Active Directory. AD relies on MS-DRSR to function. If you block this API, Domain Controllers will stop synchronizing passwords and objects, effectively breaking the Active Directory environment. Mitigation relies entirely on strict Access Control List (ACL) management.

### Q2: What specific Active Directory permissions are required to execute a DCSync attack?
**Answer:**
To successfully execute a DCSync attack, the executing account must possess specific extended rights at the domain root level (the Domain Naming Context). These permissions are:
1. **Replicating Directory Changes** (`DS-Replication-Get-Changes`)
2. **Replicating Directory Changes All** (`DS-Replication-Get-Changes-All`)
3. **Replicating Directory Changes In Filtered Set** (Optional, but required for certain restricted attributes).
By default, these privileges are only granted to highly privileged groups: `Domain Controllers`, `Enterprise Domain Controllers`, `Administrators`, and `Domain Admins`. 

### Q3: How does DCSync differ fundamentally from executing NTDS.dit extraction via Volume Shadow Copy (VSS)?
**Answer:**
**VSS Extraction (NTDS.dit):**
- Requires local administrative execution *on* the Domain Controller itself.
- Involves interacting with the local file system (creating a snapshot, copying the `NTDS.dit` database and `SYSTEM` registry hive).
- Extracts the entire database at once; requires offline extraction tools (like `secretsdump.py -local`) to parse the database and decrypt the hashes using the BootKey.
**DCSync:**
- Executed *remotely* over the network from any domain-joined (or even non-joined, via proxy) machine.
- Operates at the API level (RPC). The target DC does the work of reading the database and returns the decrypted hashes directly to the attacker over the network.
- Highly targeted: An attacker can request the hash of a *single* user (e.g., `KRBTGT`) rather than downloading a massive multi-gigabyte database file.

---

## Scenario-Based Questions

### Scenario 1: You are performing an internal penetration test. You find a forgotten service account named `svc_ad_backup` whose password was hardcoded in a script. You discover this account is not in the Domain Admins group. However, you suspect it might have DCSync rights. How do you enumerate and verify this without executing the attack?
**Answer:**
To verify DCSync rights stealthily, I need to inspect the Access Control List (ACL) of the domain root object. I would use tools like **PowerView** or the native Active Directory PowerShell module.
Using PowerView:
```powershell
Get-ObjectAcl -Identity "DC=corp,DC=local" -ResolveGUIDs | Where-Object {
    ($_.SecurityIdentifier -match "S-1-5-21-...-RID_OF_SVC_ACCOUNT") -and 
    ($_.ObjectType -match "Replicating Directory Changes")
}
```
Alternatively, I could ingest the AD environment into **BloodHound** using `SharpHound.exe`. In the BloodHound GUI, I would select the `svc_ad_backup` node and check its outbound object control. If there is a `DCSync` or `GetChangesAll` edge originating from the service account and pointing to the Domain object, the account possesses the necessary rights.

### Scenario 2: You have compromised a Domain Admin account. You want to execute a DCSync attack to obtain the `KRBTGT` hash. However, the organization's EDR immediately blocks `Mimikatz` and `secretsdump.py`, and the network firewall blocks RPC traffic (Port 135 and High Ports) originating from standard user VLANs to the Domain Controllers. How do you proceed?
**Answer:**
This scenario presents two constraints: EDR blocking standard tooling, and network segmentation blocking RPC from the attacker machine.
1. **Bypassing Network Restrictions:** I must execute the attack from a machine that *is* allowed to communicate with the DC over RPC. Since I have DA credentials, I can use WMI or WinRM (which operate over HTTP/HTTPS ports 5985/5986 or DCOM 135, assuming those are open for management) to pivot to a management server (e.g., an SCCM server or an IT Admin jump box) that resides in a trusted VLAN.
2. **Bypassing EDR (Custom Tooling):** Once on the jump box, I cannot drop Mimikatz. Instead, I would use a custom or obfuscated implementation of the MS-DRSR protocol. For example, using a pure-C# implementation of DCSync (like `SharpKatz` or a custom .NET assembly invoking `DirectoryReplicationService` namespaces) and executing it entirely in memory via `execute-assembly` from a C2 beacon.
Alternatively, I could deploy an Impacket SOCKS proxy on the jump box, route my traffic through it, and run a modified, signature-stripped version of `secretsdump.py` from my external Kali machine. The traffic originates from the jump box, satisfying the firewall, and no malicious binaries hit the jump box's disk.

### Scenario 3: As a Red Teamer, you successfully execute DCSync to extract the `KRBTGT` hash. You forge a Golden Ticket. A week later, the Blue Team detects your Golden Ticket and initiates an incident response plan. They reset the `KRBTGT` password. Are you immediately locked out of the environment? Why or why not, and how could you have maintained persistence?
**Answer:**
**Am I immediately locked out?** No. 
Active Directory maintains a password history for the `KRBTGT` account (specifically, the current password and the *previous* password). When the Blue Team resets the `KRBTGT` password *once*, the KDC will still accept TGTs encrypted with the previous hash to prevent catastrophic disruptions to legitimate, active user sessions across the domain. Therefore, my Golden Ticket forged with the old hash will still work perfectly.
To fully invalidate a Golden Ticket, the Blue Team must roll the `KRBTGT` password **twice** (typically with a delay in between to allow replication).
**Maintaining Persistence:** Anticipating a double-reset, I would have used my DA access to create deeper persistence, such as:
- Modifying the ACLs on the Domain object to grant DCSync rights to an unprivileged, hidden user account (Sneaky DCSync).
- Injecting an SID History attribute into a standard user account.
- Utilizing [[AD QnA - Module 71 - DCShadow Attacks]] to register a rogue Domain Controller.

---

## Deep-Dive Defensive Questions

### Q1: DCSync is a legitimate protocol. How can a SOC build high-fidelity detections to alert on malicious DCSync activity without generating false positives from normal Domain Controller replication?
**Answer:**
The key to detecting DCSync is identifying *who* or *what* is making the `DSGetNCChanges` request.
1. **Network Telemetry (Zeek / Suricata):** Monitor RPC traffic for the `DRSUAPI` interface (`e3514235-4b06-11d1-ab04-00c04fc2dcd2`) and specifically the `DSGetNCChanges` operation (Opnum 3). 
2. **Source IP Baselining:** Legitimate replication should *only* occur between the IP addresses of known, authorized Domain Controllers. If a `DSGetNCChanges` request originates from a workstation IP address, an IT jump box, or a VPN subnet, it is almost certainly a DCSync attack.
3. **Event Log Auditing (Event ID 4662):** Enable auditing for Directory Service Access. Look for Event ID 4662 (An operation was performed on an object) where the `Properties` field contains the GUIDs for DCSync privileges:
   - `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` (DS-Replication-Get-Changes)
   - `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2` (DS-Replication-Get-Changes-All)
   Filter out events where the `Account Name` ends with `$` (Computer accounts of valid DCs). Any user account triggering this event warrants an immediate critical alert.

### Q2: What is an "ACL Backdoor" in the context of DCSync, and how can administrators audit their environment to hunt for it?
**Answer:**
An ACL Backdoor occurs when an attacker, having achieved Domain Admin privileges, grants the `Replicating Directory Changes` and `Replicating Directory Changes All` privileges to a low-privileged, inconspicuous standard user account (e.g., `janitor_svc`). The attacker then abandons their DA access. Months later, they can use the `janitor_svc` account to execute a DCSync attack, retrieve the latest hashes, and re-escalate to DA seamlessly.
**Auditing & Hunting:**
Administrators must regularly audit the DACL of the Domain Root object (`DC=domain,DC=local`). 
1. Use scripts (like BloodHound or custom PowerShell using `Get-Acl`) to enumerate all principals holding the DCSync extended rights.
2. Cross-reference this list against a strict whitelist of known Domain Controllers, Exchange Servers (which sometimes require limited replication rights), and authorized sync accounts (like Azure AD Connect).
3. Any standard user or unknown service account possessing these rights must be investigated and stripped of the privileges immediately.

### Q3: Microsoft introduced the "Protected Users" security group. Does adding highly privileged accounts to this group prevent them from being targeted by a DCSync attack?
**Answer:**
**No.** This is a common misconception.
The Protected Users group applies advanced security controls to the accounts *within* the group (e.g., disabling NTLM authentication, forcing Kerberos AES, and preventing credential delegation). 
However, DCSync does not interact with the user account directly, nor does it attempt to authenticate as the user. DCSync asks the Active Directory database (NTDS) to return the cryptographic secrets stored within it. Since the hashes for accounts in the Protected Users group are still stored in the NTDS.dit database, a DCSync attack will successfully extract them. 
To protect against DCSync, defenses must focus on restricting the *accounts executing the attack* (limiting who has DCSync privileges), not the accounts being targeted.

---

## Real-World Attack Scenario
**The Vendor VPN to Forest Compromise:**
A sophisticated threat group phished a third-party vendor who had VPN access to the target organization's network. The vendor's account was unprivileged but allowed network access to the internal IT subnets. 
The attackers ran BloodHound and identified a complex attack path: The vendor account had `GenericWrite` over a Helpdesk group. The Helpdesk group had `ForceChangePassword` over a legacy Application Service Account. The Application Service Account had an ACL granting it `DS-Replication-Get-Changes-All` over the domain root (a severe misconfiguration left over from an old directory migration tool).
The attackers abused `GenericWrite` to add themselves to the Helpdesk group. They then forced a password reset on the Application Service Account. Finally, they authenticated as the Application Service Account from their VPN connection and used `secretsdump.py` to perform a DCSync attack. They requested the `KRBTGT` hash directly, forged a Golden Ticket, and compromised the entire forest without ever compromising a Domain Admin credential or touching a Domain Controller filesystem.

---

## Chaining Opportunities
- **Golden Ticket Forgery:** DCSync is the primary method for extracting the `KRBTGT` hash, which is the immediate prerequisite for forging a Golden Ticket as described in [[AD QnA - Module 68 - Pass the Ticket PtT]].
- **Pass the Hash / Overpass the Hash:** DCSync returns the NTLM hashes and AES keys for any user. Attackers can immediately chain this into [[AD QnA - Module 67 - Pass the Hash PtH]] or [[AD QnA - Module 69 - Overpass the Hash]].
- **DCShadow:** Attackers can take DCSync a step further by registering a fake Domain Controller to push malicious attributes *into* the AD database, exploring [[AD QnA - Module 71 - DCShadow Attacks]].

---

## Related Notes
- [[Active Directory Access Control Lists (ACLs)]]
- [[BloodHound Attack Path Analysis]]
- [[Golden and Silver Ticket Forgery]]
- [[Domain Controller Replication Mechanisms]]
