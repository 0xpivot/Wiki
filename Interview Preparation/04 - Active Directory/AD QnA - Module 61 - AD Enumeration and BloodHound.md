---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 61"
---

# Expert Active Directory Q&A: Enumeration & BloodHound

```text
+-------------------+        LDAP/SAMR/RPC        +-------------------+
|                   | --------------------------> |                   |
|   Attacker Node   |                             | Domain Controller |
|   (SharpHound)    | <-------------------------- |    (AD DS DB)     |
|                   |     AD Objects / ACLs       |                   |
+-------------------+                             +-------------------+
         |
         | JSON output (.zip)
         v
+-------------------+          Cypher             +-------------------+
|                   | <-------------------------> |                   |
|     Neo4j DB      |                             |  BloodHound GUI   |
|                   | --------------------------> |                   |
+-------------------+       Graph Rendering       +-------------------+
```

## Formal Technical Questions

### Q1: Dissect the mechanics of SharpHound's collection methods under the hood. Specifically, contrast the differences between LDAP enumeration, SAMR, and RPC in the context of the `All`, `Stealth`, and `DCOnly` collection loops.
**Expert Answer:**
SharpHound relies heavily on standard Active Directory protocols to query object properties, group memberships, and ACLs. 
- **LDAP (Lightweight Directory Access Protocol):** Used to query object attributes natively from the Domain Controller. Almost all collections start by fetching the directory tree via LDAP (port 389/636). Attributes like `nTSecurityDescriptor` (ACLs), `servicePrincipalName` (Kerberoasting), and `memberOf` are extracted this way.
- **SAMR (Security Account Manager Remote):** Used to resolve local group memberships on remote machines (e.g., finding who is in the local Administrators group of a workstation). SAMR operates over RPC (port 445/135/high-ports).
- **RPC (Remote Procedure Call):** Used for Session enumeration (NetSessionEnum) to map where users are currently logged in.
When running `CollectionMethod All`, SharpHound queries LDAP for the domain structure, then reaches out to *every single computer* in the domain via SAMR/RPC to enumerate local groups and active sessions. This is highly noisy. 
`DCOnly` relies purely on LDAP queries to the Domain Controller, meaning it generates zero lateral network traffic to endpoints. It gathers ACLs, domain groups, and object properties but misses local admin rights and session data.
`Stealth` uses LDAP primarily and performs session enumeration only against Domain Controllers and high-value targets. It attempts to stay under the radar of endpoint EDRs by not touching standard workstations via RPC/SAMR.

### Q2: Explain the significance of the `nTSecurityDescriptor` attribute. How does BloodHound translate SDDL (Security Descriptor Definition Language) into graph edges like `GenericAll` or `WriteDacl`?
**Expert Answer:**
The `nTSecurityDescriptor` is an LDAP attribute containing the security descriptor for an AD object. It includes the Owner, Group, Discretionary Access Control List (DACL), and System Access Control List (SACL). This data is typically returned in raw binary format or SDDL string format.
When SharpHound parses this attribute, it looks at the DACL Access Control Entries (ACEs). 
- If an ACE grants a specific identity `ActiveDirectoryRights.GenericAll` (Full Control), BloodHound maps this as a `GenericAll` edge.
- If it grants `ActiveDirectoryRights.WriteDacl`, it maps it as a `WriteDacl` edge, indicating the identity can modify the permissions of the target object, potentially granting itself `GenericAll`.
- If an ACE grants `ExtendedRight` with the specific GUID for "User-Force-Change-Password" (`00299570-246d-11d0-a768-00aa006e0529`), BloodHound draws a `ForceChangePassword` edge.
BloodHound's data processor converts these complex, granular Windows API rights into simplified, actionable graph relationships.

### Q3: How does the Neo4j Graph Database utilize Cypher queries to calculate the "Shortest Path to Domain Admin"? Provide an example of a raw Cypher query for this operation.
**Expert Answer:**
Neo4j is a property graph database perfectly suited for AD's interconnected nature. The nodes are AD objects (Users, Computers, Groups), and the relationships (edges) are permissions or memberships (MemberOf, GenericAll, HasSession).
Cypher uses pattern matching to traverse the graph. To find the shortest path, it employs algorithms like Dijkstra or BFS under the hood. 
A raw Cypher query to find the shortest path from any owned node to the Domain Admins group looks like this:
```cypher
MATCH (owned:User {owned: true}), (target:Group {name: "DOMAIN ADMINS@DOMAIN.LOCAL"})
MATCH p = shortestPath((owned)-[*1..]->(target))
RETURN p
```
This tells Neo4j: "Find me nodes marked as owned, find the Domain Admins group, and return the shortest variable-length path (`[*1..]`) connecting them regardless of the relationship type."

## Scenario-Based Questions

### Q4: You are on a Red Team engagement. You have a foothold on a Windows 10 workstation as a low-privileged user. The EDR is hyper-aggressive and immediately kills `SharpHound.exe` and `SharpHound.ps1` in memory. How do you gather BloodHound data?
**Expert Answer:**
In highly monitored environments, executing SharpHound directly on the endpoint is poor OPSEC. Alternative approaches include:
1. **SOCKS Proxy + Python BloodHound:** I would deploy a lightweight reverse proxy (like Chisel or Ligolo-ng) on the compromised host. From my attacker C2 infrastructure, I would route my traffic through the proxy and execute `bloodhound.py`. This moves the enumeration logic and heavy processing off the target endpoint.
2. **BofHound:** Execute the BloodHound collection as a Beacon Object File (BOF) if using Cobalt Strike or a compatible C2. BOFs run within the existing beacon process, avoiding `fork&run` indicators and staying entirely in memory without relying on `powershell.exe` or .NET assemblies.
3. **Manual LDAP Queries:** If I only need specific data (e.g., finding vulnerable ACLs), I would use built-in tools like `ADSI Accelerator`, `DirectoryServices.DirectorySearcher` via a custom C# reflective assembly, or simply `net.exe` and `Get-ADUser` if RSAT is installed, avoiding the SharpHound signature entirely.

### Q5: Reviewing the BloodHound GUI, you notice that an unprivileged group you control has `GenericAll` rights over a Group Policy Object (GPO). Walk through the exact steps to weaponize this path to compromise a target Organizational Unit (OU).
**Expert Answer:**
Having `GenericAll` over a GPO means I have full control to modify its settings. If that GPO is linked to an OU containing target workstations or servers, I can compromise them.
1. **Verification:** I first use `Get-DomainGPO` (PowerView) to confirm the GPO's scope and `Get-DomainOU` to see where it is linked.
2. **Weaponization:** I will use the `New-GPOImmediateTask` cmdlet from PowerView or SharpGPOAbuse. This technique injects a Scheduled Task into the GPO.
3. **Payload Execution:** The task is configured to run as `NT AUTHORITY\SYSTEM` on the target machines. The payload could be adding a local admin user, executing a PowerShell download cradle, or launching a reverse shell.
4. **Trigger:** The GPO will naturally update on the target machines within 90-120 minutes. To accelerate this, if I have network visibility, I might attempt to trigger `gpupdate /force` via WMI or wait for normal replication.
5. **Cleanup:** After gaining the required access, I must immediately revert the GPO to its original state to avoid disrupting the environment and leaving persistent, obvious indicators.

### Q6: BloodHound identifies a path, but it requires crossing a "disconnected graph"—a jump server in a separate tier where standard RPC/SMB is blocked from your current segment. How do you validate and traverse this path?
**Expert Answer:**
Disconnected graphs or heavily segmented networks break standard lateral movement. BloodHound assumes a flat network topology for its paths.
1. **Network Validation:** I would first validate the network boundary. I'd perform targeted port scans (e.g., checking 3389, 5985, 445) from my current foothold against the Jump Server.
2. **Alternative Protocols:** If SMB is blocked but WinRM (5985) or RDP (3389) is open, I can execute code or authenticate over those channels.
3. **Pivoting via Proxies:** If there is a dual-homed host or a management proxy (like a Squid proxy or an SSH jump box) in my current segment that *is* allowed to talk to the jump server, I will pivot my traffic through it.
4. **Finding Overlaps:** If the direct path is blocked by the firewall, I must look for "Shadow Admins" or alternative BloodHound paths (e.g., compromising a user in my segment who happens to have a concurrent session on the Jump Server, and hijacking their session token).

## Deep-Dive Defensive Questions

### Q7: SharpHound is notoriously noisy, but modern threat actors use `DCOnly` or `Stealth` modes. How can a SOC dynamically detect BloodHound-style LDAP and SAMR enumeration?
**Expert Answer:**
Defending against enumeration requires behavior-based analytics rather than static signatures.
- **LDAP Anomalies:** SharpHound's `DCOnly` makes heavy LDAP queries. We can enable Event ID `1644` (Directory Service Search) on Domain Controllers. We look for single users requesting massive amounts of data (e.g., thousands of objects returned in a few seconds) or specific filters commonly used by SharpHound (e.g., queries explicitly looking for `nTSecurityDescriptor` or `ms-MCS-AdmPwd`).
- **SAMR Anomalies:** If an attacker uses `CollectionMethod All`, they generate massive SAMR traffic (Event ID `4624` Type 3 network logons followed rapidly by SAMR RPC calls). Detecting a single workstation authenticating to 50+ other workstations within a 1-minute window is a high-fidelity indicator of a BloodHound sweep or a worm.
- **HoneyTokens:** Deploying fake AD accounts or computer objects with highly attractive (but heavily monitored) SPNs or ACLs. If an attacker queries these specific, undocumented objects, an alert is triggered.

### Q8: How can a Blue Team proactively use BloodHound and Cypher queries to enforce Tiered Administration (e.g., Tier-0, Tier-1, Tier-2 boundaries)?
**Expert Answer:**
The Blue Team should run BloodHound internally to audit their own environment continuously.
1. **Custom Cypher Queries for Tier Violations:** We can tag nodes in Neo4j based on their tier (e.g., tagging Domain Admins and DCs as Tier-0). We then write a Cypher query to identify violations:
   ```cypher
   MATCH p=(n)-[*1..]->(t:Tier0)
   WHERE NOT n:Tier0
   RETURN p
   ```
   This query instantly reveals any path where a non-Tier-0 object has control or access over a Tier-0 asset.
2. **Identifying Inadvertent ACLs:** Often, helpdesk groups (Tier-1) are accidentally given `GenericAll` over the domain root or critical Tier-0 service accounts. BloodHound visualizes these misconfigurations so they can be remediated.
3. **Session Management:** By monitoring `HasSession` edges, the Blue Team can detect if Domain Admins are logging into Tier-2 workstations, exposing their credentials to memory scraping (LSASS).

### Q9: Discuss the implementation and impact of `NetCease` and SAMR restriction policies in stopping BloodHound's lateral reconnaissance.
**Expert Answer:**
`NetCease` is a defensive script that alters the permissions on the `NetSessionEnum` RPC endpoint. 
By default, any authenticated user in AD can query a remote server to see who is logged in. BloodHound uses this to map `HasSession` edges. `NetCease` modifies the security descriptor of the Server Service (`LanmanServer`) to explicitly deny standard users from invoking `NetSessionEnum`, restricting it to Administrators or specific service accounts.
Furthermore, SAMR restrictions can be applied via Group Policy: `Network access: Restrict clients allowed to make remote calls to SAM`. By setting this policy, defenders can prevent low-privileged accounts from enumerating local group memberships on remote machines over SAMR.
Implementing these two controls severely degrades BloodHound's ability to map out lateral movement paths, forcing the attacker to operate blindly or resort to much noisier, targeted exploitation techniques.

## Real-World Attack Scenario
During an internal penetration test for a financial institution, the Red Team landed on a developer's workstation. Standard SharpHound execution triggered Microsoft Defender for Endpoint (MDE). The team pivoted to using `python-bloodhound` via a SOCKS5 proxy established through Ligolo-ng. 
The resulting graph revealed a complex, multi-step attack path. The developer account had `GenericWrite` over an outdated IT Support group. The team added themselves to this group. The IT Support group had `WriteDacl` on a custom GPO linked to the Server OU. By injecting a scheduled task into the GPO via SharpGPOAbuse, the team obtained `SYSTEM` on an application server. 
From the application server, BloodHound showed a `HasSession` edge for a Domain Admin who had logged in earlier that week and left a disconnected RDP session. The team dumped LSASS on the application server, extracted the DA's NTLM hash, and executed a Pass-the-Hash attack to compromise the Domain Controller.

## Chaining Opportunities
- **BloodHound + Kerberoasting:** Use BloodHound to identify the shortest path to DA, then identify if any accounts on that path have `servicePrincipalName` set, prioritizing them for targeted Kerberoasting.
- **BloodHound + RBCD (Resource-Based Constrained Delegation):** If BloodHound shows `GenericWrite` or `Owns` over a computer object, the attacker can configure RBCD to compromise that machine entirely.
- **BloodHound + DCSync:** Identify paths leading to accounts with `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` rights to execute a DCSync attack.

## Related Notes
- [[01 - Active Directory Basics]]
- [[62 - AS-REP Roasting]]
- [[63 - Kerberoasting]]
- [[Privilege Escalation - Windows ACLs]]
- [[Red Teaming - Evading EDR]]
