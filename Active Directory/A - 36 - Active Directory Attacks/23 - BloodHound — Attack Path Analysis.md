---
tags: [bloodhound, active-directory, graph-theory, reconnaissance]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.23 BloodHound"
---

# BloodHound — Attack Path Analysis

## 1. Introduction to BloodHound and Graph Theory

In complex Active Directory (AD) environments containing tens of thousands of users, groups, and computers, it is impossible for human operators (both attackers and defenders) to manually track the cascading permissions that link an unprivileged user to a Domain Admin. 

**BloodHound** solves this problem by applying Graph Theory to Active Directory. Developed by SpecterOps, BloodHound maps the hidden, complex relationships within AD. It reveals hidden attack paths that traditional vulnerability scanners completely miss. 

BloodHound relies on three primary components:
1. **SharpHound (The Ingestor):** A C# data collector that queries the AD environment using LDAP and RPC to gather users, groups, computers, ACLs, and session data.
2. **Neo4j (The Database):** A highly performant graph database that stores the collected data as Nodes (objects) and Edges (relationships).
3. **BloodHound GUI:** An Electron-based application that visually renders the graph and allows operators to run custom Cypher queries to find attack paths.

BloodHound shifted the paradigm of AD security from "finding misconfigurations" to "finding identity attack paths."

---

## 2. Visual Architecture: Nodes, Edges, and Attack Paths

```ascii
+---------------------------------------------------------------------------------+
|                         THE BLOODHound GRAPH CONCEPT                            |
|                                                                                 |
|  [Node: User]                [Edge: Relationship]               [Node: Group]   |
|                                                                                 |
|  (Bob) ---------------------- [MemberOf] ---------------------> (IT Support)    |
|                                                                       |         |
|                                                                       |         |
|                                                                 [AdminTo]       |
|                                                                       |         |
|                                                                       V         |
|  (Domain Admins) <----------- [ForceChangePassword] ----------- (SQLServer_01)  |
|         ^                                                             |         |
|         |                                                             |         |
|     [MemberOf] <------------- [HasSession] <--------------------------+         |
|         |                                                                       |
|  (Alice)                                                                        |
|                                                                                 |
|---------------------------------------------------------------------------------|
| ATTACK PATH RESOLUTION:                                                         |
| 1. Compromise Bob.                                                              |
| 2. Bob is in IT Support, granting Local Admin on SQLServer_01.                  |
| 3. Alice (Domain Admin) has a live session on SQLServer_01.                     |
| 4. Dump LSASS on SQLServer_01 to steal Alice's credentials.                     |
| 5. Become Domain Admin.                                                         |
+---------------------------------------------------------------------------------+
```

---

## 3. Data Collection with SharpHound

SharpHound is the tool run on the compromised endpoint to map the network. Because any authenticated domain user can read almost all of Active Directory via LDAP, SharpHound requires zero administrative privileges to map the entire forest.

### 3.1 Standard Collection
By default, SharpHound collects local admins, session data, object properties, ACLs, and trust relationships.
```powershell
# Running SharpHound locally
Invoke-BloodHound -CollectionMethod All -OutputDirectory C:\temp\
```
Or running the compiled executable:
```cmd
SharpHound.exe -c All --zipfilename results.zip
```

### 3.2 Collection Methods and Telemetry
SharpHound uses different protocols to gather different data:
- **LDAP (Port 389/636):** Used to enumerate Users, Computers, Groups, OUs, GPOs, and Access Control Lists (ACLs). This is extremely quiet, as AD is designed to answer LDAP queries continuously.
- **RPC / SMB (Port 445/135):** Used to enumerate Local Administrators (`SAMR`), logged-on users (`NetSessionEnum`), and RDP sessions. This requires SharpHound to touch every single computer in the domain, which is highly noisy and often caught by EDR network sensors.

### 3.3 Stealth Mode
To avoid triggering alerts for massive RPC sweeps, attackers use stealthier flags, collecting only LDAP data or targeting specific OUs.
```cmd
# Collect only LDAP structure (No RPC sweeps against endpoints)
SharpHound.exe -c DCOnly
```

---

## 4. Core Edge Types (Relationships)

Understanding BloodHound requires understanding the meaning of its edges. Edges define exactly *how* an attacker can pivot from one node to another.

### 4.1 Privilege Escalation / ACL Edges
- **GenericAll:** Full control over an object. Attackers can reset passwords, add members to a group, or register SPNs.
- **ForceChangePassword:** The attacker can reset the target user's password without knowing their current password.
- **WriteDacl:** The attacker can modify the ACL of the target object, allowing them to grant themselves `GenericAll`.
- **AddMember:** The attacker can add any user (including themselves) to the target security group.

### 4.2 Lateral Movement Edges
- **AdminTo:** The user or group is a member of the local Administrators group on the target computer. The attacker can execute code remotely (via WMI/PsExec) and dump memory.
- **HasSession:** The target user has an active logon session on the target computer. If the attacker gains Admin on this computer, they can dump LSASS to steal the user's credentials.
- **CanRDP:** The user is permitted to RDP into the target machine.

### 4.3 Domain/Forest Trust Edges
- **TrustedBy:** Indicates a domain trust. If Domain A is TrustedBy Domain B, attackers compromising Domain A can potentially pivot to Domain B.

---

## 5. Custom Cypher Queries

BloodHound relies on Neo4j, which uses the **Cypher** query language. While the BloodHound GUI has built-in queries (e.g., "Find Shortest Path to Domain Admins"), advanced operators write custom Cypher to find nuanced paths.

**Example 1: Find all users with Kerberoastable accounts (SPNs) that have a path to Domain Admins.**
```cypher
MATCH (u:User {hasspn:true})
MATCH (g:Group {name:'DOMAIN ADMINS@CORP.LOCAL'})
MATCH p=shortestPath((u)-[*1..]->(g))
RETURN p
```

**Example 2: Find all computers where the current compromised user (Bob) is a Local Administrator.**
```cypher
MATCH (u:User {name:'BOB@CORP.LOCAL'})
MATCH (c:Computer)
MATCH p=(u)-[:AdminTo]->(c)
RETURN p
```

**Example 3: Identify High-Value Targets (Tier 0) vulnerable to DCSync.**
```cypher
MATCH p=(n)-[:GetChangesAll]->(d:Domain) 
RETURN p
```

---

## 6. Defensive BloodHound (BlueHound)

BloodHound is not just an offensive tool. Mature blue teams run BloodHound regularly to proactively sever attack paths.

### 6.1 Finding and Remediation
Defenders use BloodHound to:
- Identify and remove unprivileged users from highly privileged groups (e.g., standard users in `Account Operators`).
- Identify over-privileged service accounts (e.g., an IT service account that is Admin on all workstations but also logged into Domain Controllers).
- Audit active sessions to enforce Tiered Administration (preventing Tier 0 admins from logging into Tier 2 workstations).

### 6.2 Detection of SharpHound
Detecting SharpHound execution involves monitoring network traffic and directory service access.
- **LDAP Query Anomalies:** SharpHound generates massive, rapid LDAP queries. Defenders baseline normal LDAP traffic and alert on sudden spikes originating from standard user workstations.
- **RPC Sweeps (Event ID 4624 / 5145):** A single host rapidly authenticating via SMB/RPC to thousands of machines in the domain to check for local admins or sessions.
- **Honeypot Objects:** Blue teams can create a fake "Domain Admin" account with no real rights. If they see someone querying its ACLs or attempting to Kerberoast it, it indicates active reconnaissance.

---

## Real-World Attack Scenario

During a presumed breach assessment for a healthcare provider, the red team secured standard user credentials (`j.smith`) via a password spray attack. The environment was sprawling, consisting of three domains and tens of thousands of endpoints. Manually identifying a privilege escalation path was impossible.

The attacker dropped a heavily obfuscated version of SharpHound to memory via a PowerShell cradle. Knowing the SOC was actively monitoring for internal RPC sweeps (Event ID 4624/5145 anomalies), the attacker avoided the default `All` collection method. Instead, they ran SharpHound in `DCOnly` mode to purely harvest LDAP data without touching any workstations:
```powershell
Invoke-BloodHound -CollectionMethod DCOnly -Domain health.local -ZipFileName results.zip
```

The data was exfiltrated and ingested into a local Neo4j database on the attacker's machine. By executing a custom Cypher query to find the shortest path from `j.smith` to `Domain Admins`, the attacker uncovered a surprising ACL misconfiguration:
`j.smith` was a member of the `Helpdesk_T2` group. That group had `WriteDacl` permissions over an inactive service account, `svc_backup`. Furthermore, `svc_backup` had `GenericAll` rights over the `Server_Admins` group, which ultimately had local admin rights on the Domain Controller.

Following the BloodHound graph step-by-step, the attacker executed the attack path:
1. They used PowerView to grant themselves `FullControl` over `svc_backup` (abusing `WriteDacl`).
2. They reset the password for `svc_backup`.
3. Authenticating as `svc_backup`, they added their own `j.smith` account to the `Server_Admins` group (abusing `GenericAll`).
4. Finally, they used WMI to execute a remote payload on the Domain Controller as a `Server_Admin`, resulting in a full domain compromise. BloodHound successfully turned a complex, invisible network of permissions into a straightforward, actionable checklist.

## 7. Chaining Opportunities

- **[[18 - Active Directory ACL and ACE Abuse]]**: BloodHound highlights the precise ACLs (GenericAll, WriteDacl) that need to be abused to progress the attack path.
- **[[24 - Domain Privilege Escalation via Trust Relationships]]**: BloodHound seamlessly maps forest trusts and identifies cross-domain attack paths.
- **[[19 - AdminSDHolder Abuse]]**: BloodHound will visually identify if an attacker has backdoored the AdminSDHolder object, displaying a `GenericAll` edge from the attacker to all protected groups.

## 8. Related Notes
- [[18 - Active Directory ACL and ACE Abuse]]
- [[24 - Domain Privilege Escalation via Trust Relationships]]
- [[19 - AdminSDHolder Abuse]]
- [[13 - Active Directory Enumeration]]
