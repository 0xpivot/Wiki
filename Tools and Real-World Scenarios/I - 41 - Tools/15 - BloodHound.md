---
tags: [tools, vapt, utility, active-directory, bloodhound]
difficulty: intermediate
module: "41 - Tools"
topic: "41.15 BloodHound"
---

# BloodHound: Attack Path Management and Active Directory Domination

## 1. Overview and Introduction

BloodHound is an incredibly powerful single-page Javascript web application, built on top of Linkurious, compiled with Electron, and utilizing a Neo4j graph database backend. Its primary purpose is to visually map out complex, hidden, and unintended relationships within an Active Directory (AD) or Azure AD (Entra ID) environment. 

By employing graph theory, BloodHound allows security professionals, penetration testers, and adversaries to easily identify highly complex attack paths that would otherwise be virtually impossible to spot manually. These attack paths often lead from an unprivileged user to Domain Admin or Global Administrator privileges.

In the context of API Security (Module 31), BloodHound is increasingly relevant. BloodHound Enterprise and newer versions of BloodHound Community Edition utilize extensive REST APIs to manage data ingestion, query execution, and user management. Understanding how to interact with these APIs allows for extreme automation during red team engagements.

## 2. Graph Theory in Active Directory

Active Directory is fundamentally a relational database, but traditional tools view it in a tabular or tree-like format. Graph theory changes this paradigm by viewing AD as a series of:
- **Nodes (Vertices):** Represent entities like Users, Groups, Computers, Domains, Organizational Units (OUs), and Group Policy Objects (GPOs).
- **Edges (Relationships):** Represent the permissions or connections between nodes, such as `MemberOf`, `AdminTo`, `HasSession`, `GenericAll`, `WriteDacl`, etc.

When an attacker compromises a node, they can traverse any outgoing edge to compromise the next node.

## 3. Architecture and Components

BloodHound consists of three primary components:

1.  **Data Collector (Ingestor):** Tools like SharpHound (for on-prem AD) and AzureHound (for Entra ID/Azure) collect data from the target environment. They output JSON files.
2.  **Database (Neo4j):** A highly scalable native graph database that stores the nodes and relationships.
3.  **Front-End GUI:** The Electron-based application that allows users to visualize the graph and execute Cypher queries.

### 3.1 Custom ASCII Architecture Diagram

```text
+-------------------------------------------------------+
|                 BloodHound Ecosystem                  |
+-------------------------------------------------------+
|                                                       |
|  +----------------+             +------------------+  |
|  | SharpHound     |             | AzureHound       |  |
|  | (C# / .NET)    |             | (Go / APIs)      |  |
|  +-------+--------+             +--------+---------+  |
|          |                               |            |
|          |    REST API / File Drop       |            |
|          v                               v            |
|  +-------------------------------------------------+  |
|  |                BloodHound GUI                   |  |
|  |               (Electron / Web)                  |  |
|  +-----------------------+-------------------------+  |
|                          |                            |
|                          v                            |
|  +-------------------------------------------------+  |
|  |                Neo4j Database                   |  |
|  |               (Graph Database)                  |  |
|  +-------------------------------------------------+  |
|                                                       |
+-------------------------------------------------------+
```

## 4. Data Collection Techniques

### 4.1 SharpHound
SharpHound is the official C# data collector for BloodHound. It uses native Windows APIs and LDAP queries to extract AD information. 

**Standard Execution:**
```powershell
Invoke-BloodHound -CollectionMethod All -Domain target.local -ZipFileName BH_Data.zip
```

**Stealth Execution:**
To avoid detection, operators often limit the collection scope:
```powershell
Invoke-BloodHound -CollectionMethod Session,Trusts -Stealth
```

### 4.2 API Integration
Newer BloodHound deployments allow data to be pushed directly to the BloodHound API, rather than manually uploading ZIP files. This is highly advantageous for persistent engagements where continuous monitoring of attack paths is desired.

```bash
curl -X POST -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d @computers.json \
     https://bloodhound.target.local/api/v2/ingest
```

## 5. Key Node and Edge Types

Understanding the edges is critical for attack path execution.

| Edge Type | Description | Exploitation Technique |
| :--- | :--- | :--- |
| `HasSession` | User has an interactive logon on a computer. | Dump credentials using Mimikatz. |
| `AdminTo` | User has local admin rights on a computer. | Pass-the-Hash, PsExec. |
| `MemberOf` | User is a member of a group. | Inherit group privileges. |
| `GenericAll` | Full control over an AD object. | Reset passwords, add to groups. |
| `GenericWrite`| Write privileges to an object. | Modify SPNs, update attributes. |
| `WriteDacl` | Can modify permissions of an object. | Grant self `GenericAll`. |
| `ForceChangePassword` | Can reset the user's password. | Reset password to known value. |

## 6. Advanced Cypher Queries

Neo4j uses the Cypher Query Language (CQL). While BloodHound has pre-built queries, mastering Cypher is essential for advanced analysis.

**Find all Domain Admins:**
```cypher
MATCH (n:User)-[:MemberOf*1..]->(g:Group {name:'DOMAIN ADMINS@DOMAIN.LOCAL'}) RETURN n
```

**Find all users with DCSync Rights:**
```cypher
MATCH p=(n)-[:GetChangesAll]->(d:Domain) RETURN p
```

**Find shortest path from a specific user to Domain Admin:**
```cypher
MATCH (n:User {name:'JSMITH@DOMAIN.LOCAL'}), (g:Group {name:'DOMAIN ADMINS@DOMAIN.LOCAL'}), p=shortestPath((n)-[*1..]->(g)) RETURN p
```

**Identify highly privileged service accounts (Kerberoasting candidates):**
```cypher
MATCH (u:User {hasspn:true})-[r:MemberOf*1..]->(g:Group) 
WHERE g.name CONTAINS "ADMIN" 
RETURN u.name, g.name
```

## 7. Evasion and Detection

### 7.1 Evasion
- Run SharpHound from a non-domain joined machine using a compromised user's credentials via runas /netonly.
- Use targeted LDAP queries rather than querying the entire domain.
- Limit concurrent threads to reduce network noise.

### 7.2 Detection
- **Event ID 4624 (Logon):** Frequent network logons from a single host.
- **Event ID 5145 (Network Share Object Access):** SharpHound connects to the `IPC$` share on computers to check for sessions and local admins.
- **Event ID 2889 (LDAP Queries):** High volume of LDAP queries, especially unencrypted.
- **Honeytokens:** Create fake high-privileged accounts that alert upon access or querying.

## 8. Defending Against BloodHound

Defending against BloodHound means breaking the attack paths it discovers.
1.  **Tiered Administration:** Implement the Microsoft Tier Model (Tier 0, Tier 1, Tier 2). Ensure Tier 0 admins never log onto Tier 1 or Tier 2 machines.
2.  **LAPS (Local Administrator Password Solution):** Randomize local admin passwords to break `AdminTo` lateral movement paths.
3.  **Restrict LDAP Binding:** Prevent anonymous LDAP binding and require LDAP signing.
4.  **Clean up Permissions:** Regularly review and remove excessive `GenericAll`, `WriteDacl`, and `GenericWrite` permissions from AD objects.

## 9. Conclusion

BloodHound fundamentally altered the landscape of Active Directory security. By providing an attacker's perspective of the environment, it forced defenders to shift from focusing solely on vulnerabilities to managing and eliminating attack paths. In modern VAPT, running BloodHound is no longer optional; it is a mandatory step for thorough AD assessment.

---

## Chaining Opportunities
- **[[18 - Mimikatz]]:** Use BloodHound to find a machine where a Domain Admin has a session (`HasSession` edge), compromise the machine, and use Mimikatz to dump their credentials from memory.
- **[[16 - Impacket]]:** After identifying an `AdminTo` edge, utilize Impacket's `psexec.py` or `wmiexec.py` to gain execution on the target system.
- **[[06 - Lateral Movement]]:** BloodHound visually maps all lateral movement opportunities.

## Related Notes
- [[01 - Active Directory Basics]]
- [[02 - LDAP Enumeration]]
- [[03 - Graph Theory in Cybersecurity]]
- [[04 - Entra ID Security]]
