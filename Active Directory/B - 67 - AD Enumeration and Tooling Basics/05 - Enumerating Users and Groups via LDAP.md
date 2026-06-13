---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.05 Enumerating Users and Groups via LDAP"
---

# 67.05 Enumerating Users and Groups via LDAP

## 1. Introduction to LDAP in Active Directory

The Lightweight Directory Access Protocol (LDAP) serves as the foundational protocol used to query, read, and modify objects within Active Directory. While abstraction tools like PowerView, BloodHound, and NetExec hide LDAP interactions behind automated scripts and compiled binaries, understanding how to interact with and query LDAP directly provides a profound understanding of AD structures. Furthermore, it allows for extreme precision when "living off the land" and evading behavioral detection systems.

Active Directory Domain Controllers natively run LDAP services on TCP/UDP port 389 (Cleartext) and 636 (LDAPS/TLS). Additionally, the Global Catalog (GC)—a specialized, distributed data repository containing a searchable, partial representation of every object across every domain in a multidomain AD forest—listens on ports 3268 (Cleartext) and 3269 (TLS).

### 1.1 The Power of Default Permissions (The Core AD Flaw)
The most critical vulnerability leveraged by attackers in default AD configurations is that **any authenticated user (even a low-privileged guest, a standard user, or a compromised computer account) possesses `Read` access to almost the entire directory via LDAP**. You do not need to be a Domain Administrator to dump comprehensive user lists, analyze group memberships, inspect domain policies, and extract sensitive object attributes.

## 2. LDAP Architecture, Trees, and Syntax

Understanding how Active Directory structures data is essential for crafting precise LDAP queries.

```text
+-------------------------+
|     Active Directory    |
|                         |
|  [DC=target,DC=local]   | <--- Base DN (Distinguished Name)
|           |             |
|    +------+------+      |
|    |             |      |
| [CN=Users]   [OU=IT]    | <--- Organizational Units / Containers
|    |             |      |
| [CN=jdoe]   [CN=admin]  | <--- Leaf Objects (Users, Computers)
|                         |
+-------------------------+
```

### 2.1 LDAP Search Components
A formal LDAP query consists of three mandatory components:
1. **Base DN**: The starting point in the directory tree for the search (e.g., `DC=corp,DC=local` restricts the search to that specific domain).
2. **Search Filter**: The specific criteria an object must meet to be returned in the results.
3. **Attributes**: The specific data fields you wish to retrieve (e.g., `sAMAccountName`, `description`, `pwdLastSet`), preventing the return of massive, unnecessary data blobs.

### 2.2 LDAP Filter Syntax Logic
LDAP filters are enclosed in parentheses and utilize prefix notation for logical operators:
- `&` (Logical AND)
- `|` (Logical OR)
- `!` (Logical NOT)

**Practical Examples:**
- `(objectClass=User)`: Find all objects categorized as Users.
- `(&(objectClass=User)(name=admin*))`: Find objects that are Users AND whose name begins with the string 'admin'.
- `(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))`: Find all active (non-disabled) users. (The OID `1.2.840.113556.1.4.803` performs a bitwise AND match against the UserAccountControl attribute to check the disabled flag).

## 3. Practical Enumeration Tools and Techniques

While PowerShell wrappers are common, native system tools and cross-platform clients are highly effective and often more stealthy.

### 3.1 Using Native Windows Tools (Living off the Land)

**Active Directory Module (RSAT)**
If the Remote Server Administration Tools (RSAT) are installed on the endpoint, native cmdlets are extremely powerful and easy to use:
```powershell
# Enumerate all users and return all properties
Get-ADUser -Filter * -Properties *

# Enumerate all users within a highly privileged group
Get-ADGroupMember -Identity "Domain Admins"
```

**ADSI (Active Directory Service Interfaces)**
If RSAT is not installed (which is typical for standard workstations), you can interface with ADSI directly from PowerShell, requiring zero external dependencies:
```powershell
$domain = [ADSI]"LDAP://DC=target,DC=local"
$searcher = New-Object DirectoryServices.DirectorySearcher($domain)
# Set the LDAP filter
$searcher.Filter = "(objectClass=User)"
# Execute the search
$results = $searcher.FindAll()
foreach ($result in $results) {
    Write-Host $result.Properties["samaccountname"]
}
```

### 3.2 Using Linux Tools (Impacket & ldapsearch)

When operating from an attacker machine (e.g., Kali Linux), `ldapsearch` and Impacket are the industry standards.

**ldapsearch**
A highly flexible, highly configurable standard Unix tool for LDAP interaction.
```bash
# Query the DC for all users, returning only specific attributes
ldapsearch -x -H ldap://dc01.target.local -D "target\jdoe" -w "Password123" -b "DC=target,DC=local" "(objectClass=user)" sAMAccountName description

# Query for Kerberoastable users (Users where the SPN attribute is not empty)
ldapsearch -x -H ldap://dc01.target.local -D "target\jdoe" -w "Password123" -b "DC=target,DC=local" "(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))" sAMAccountName servicePrincipalName
```

**Impacket GetADUsers.py**
A Python script specifically designed to dump AD users and their properties cleanly into a readable format.
```bash
# Dump all users and output to terminal
impacket-GetADUsers target.local/jdoe:Password123 -all
```

## 4. Key Attributes to Enumerate

When querying LDAP, attackers do not just pull everything; they specifically look for attributes that indicate vulnerabilities, poor hygiene, or provide direct paths to privilege escalation.

### 4.1 High-Value User Attributes
- `sAMAccountName`: The pre-Windows 2000 login name. This is essential for building target lists for password spraying.
- `description`: IT Administrators frequently leave plaintext passwords, infrastructure details, deployment notes, or sensitive contextual information in the description field of users or computers.
- `userAccountControl` (UAC): A critical bitmask integer that dictates overarching account properties.
  - Value containing `DONT_REQ_PREAUTH` (4194304): The account is explicitly vulnerable to AS-REP Roasting.
  - Value containing `TRUSTED_FOR_DELEGATION` (524288): The account is configured for Unconstrained Delegation, a massive security risk.
- `servicePrincipalName` (SPN): If this attribute exists on a User object (not a computer), the account is highly vulnerable to Kerberoasting.
- `adminCount`: If set to `1`, the object is (or historically was) a member of a protected administrative group (e.g., Domain Admins), and its permissions are strictly managed by the internal `AdminSDHolder` object.
- `memberOf`: A multi-value attribute showing exactly which groups the user belongs to.

### 4.2 Group Enumeration Focus Areas
- **Domain Admins / Enterprise Admins**: The ultimate, Tier-0 targets.
- **DnsAdmins**: Members can load arbitrary DLLs into the DNS service running on the Domain Controller, leading to trivial Remote Code Execution (RCE) on the DC.
- **Server Operators / Backup Operators**: Members can bypass standard file system ACLs and dump the Active Directory database (`NTDS.dit`).
- **Account Operators**: Members can manage user accounts and reset passwords for non-protected standard users across the domain.

## 5. Defensive Perspectives and Mitigation Strategies

### 5.1 Analyzing and Detecting LDAP Traffic
- **Network Level Telemetry**: Monitoring for large, unpaginated LDAP queries is crucial. Legitimate applications usually query specific users individually or use paginated searches. Scripts dumping the entire directory will generate massive, easily detectable LDAP response traffic bursts.
- **Log Level Telemetry**: Windows Event ID 1644 (Directory Service) can be explicitly configured via registry edits to log expensive, inefficient, or high-volume LDAP queries.
- **Honeypot Attributes (Deception)**: Defenders can populate fake, highly-enticing user accounts (e.g., `svc_admin_backup`) with fake SPNs or place decoy passwords in `description` fields. If an attacker queries these specific honeypots or attempts to use the decoy credentials, it acts as a high-fidelity, zero-false-positive alert.

### 5.2 Hardening LDAP Access
- **Restrict Anonymous Binds**: Ensure that anonymous, unauthenticated access to LDAP is completely disabled (this is the default in modern AD but is frequently re-enabled for legacy application compatibility).
- **Enforce LDAP Signing and Channel Binding**: Enforce LDAPS or LDAP Signing at the domain level to prevent Man-in-the-Middle (MitM) attacks and credential relaying (e.g., NTLM Relay to LDAP).
- **Hide Sensitive Data**: Utilize the Active Directory permission model to explicitly deny `Read Property` rights on highly sensitive attributes (like LAPS passwords, BitLocker keys, or specific administrative OUs) to standard users.

## Real-World Attack Scenario

Operating from a compromised Linux host without RSAT or PowerShell, an attacker leverages the native `ldapsearch` utility to quietly enumerate the Active Directory environment. Authenticating as a low-privileged user, they craft a specific LDAP query `(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))` to extract all active users. Inspecting the returned attributes, the attacker finds a forgotten service account where the IT administrator mistakenly stored the plaintext deployment password in the `description` field. The attacker uses these credentials to elevate privileges, fully exploiting the fact that LDAP grants read access to sensitive object attributes by default to any authenticated user.

## Chaining Opportunities
- Discover users with SPNs via manual LDAP queries and immediately use Impacket's `GetUserSPNs.py` or NetExec to perform **Kerberoasting**.
- Use the list of extracted active user accounts (`sAMAccountName`) to perform targeted, low-and-slow password spraying using tools discussed in [[04 - NetExec CrackMapExec Basics and Module Usage]].
- For a graphical, comprehensive representation of the complex LDAP relationships discovered, feed this data into **BloodHound** as seen in [[01 - Introduction to BloodHound and SharpHound]].
- Alternatively, use PowerShell wrappers to perform these queries as outlined in [[02 - Using PowerView for AD Enumeration]].

## Related Notes
- [[01 - Introduction to BloodHound and SharpHound]]
- [[02 - Using PowerView for AD Enumeration]]
- [[03 - Ping Sweeping and Host Discovery in AD]]
- [[04 - NetExec CrackMapExec Basics and Module Usage]]

## Advanced Threat Hunting and Behavioral Analytics

As evasion techniques evolve, reliance on static indicators of compromise (IoCs) is insufficient. Defenders must pivot to behavioral analytics.

### Baseline Deviation Analysis
Instead of hunting for specific tool signatures (like `SharpHound.exe` or `PowerView.ps1`), mature SOCs establish baselines of administrative behavior.
1. **Administrative Logon Baselines**: Identify the standard jump boxes and IP ranges used by authorized administrators. Any high-privileged authentication originating from a non-standard workstation (e.g., a receptionist's PC) triggers an immediate severity-high alert, regardless of the tool used.
2. **Protocol Baselines**: Standard users rarely, if ever, initiate raw RPC or WMI connections to other workstations. Detecting a high volume of lateral SMB/RPC traffic originating from a standard subnet is a strong behavioral indicator of enumeration or lateral movement.

### Leveraging Graph Databases for Defense
Defenders can utilize the exact same graph theory concepts employed by attackers to secure the environment proactively.
- **Continuous Ingestion**: By scheduling daily or weekly automated ingestions of AD data into a defensive Neo4j database, defenders can track changes over time.
- **Chokepoint Identification**: Graph analysis reveals "chokepoints"—specific users or groups that serve as critical bridges in numerous attack paths. Removing privileges from these chokepoint accounts fractures the attack graph, significantly increasing the effort required by an attacker.
- **Unintended Permission Auditing**: Graph databases easily highlight misconfigurations such as standard users accidentally granted `GenericAll` rights over critical infrastructure OUs due to complex, nested group memberships.

### Conclusion
Active Directory enumeration is a delicate balance of noise versus insight. Attackers must constantly adapt to increasingly sophisticated telemetry and detection mechanisms. For defenders, understanding the mechanics of these enumeration tools is paramount. Security is no longer just about preventing the initial compromise; it is about anticipating the attacker's post-exploitation reconnaissance and disrupting their ability to discover the pathways to domain dominance.

### Real-World Incident Response Scenarios
When responding to suspected AD enumeration:
1. **Isolate Suspect Endpoints**: Immediately quarantine the endpoint initiating the anomalous LDAP or RPC queries.
2. **Review TGT Requests**: Correlate the endpoint activity with Event ID 4768 (A Kerberos authentication ticket (TGT) was requested) to identify the compromised account.
3. **Analyze BloodHound Execution**: If SharpHound is suspected, search for Event ID 4688 containing command-line arguments like `--CollectionMethod` or `--Loop`.
4. **Implement Tiered Administration**: If widespread enumeration is detected, immediately restrict Tier-0 accounts from authenticating to lower-tier systems to break potential `HasSession` escalation paths.

## Glossary of Advanced Terms
- **TGT (Ticket Granting Ticket)**: The primary Kerberos ticket used to request access to other services.
- **SPN (Service Principal Name)**: A unique identifier for a service instance, used in Kerberos authentication.
- **ACL (Access Control List)**: A list of permissions attached to an object.
- **DCSync**: An attack technique simulating a Domain Controller to request password hashes via the Directory Replication Service (DRS) Remote Protocol.
- **Pass-the-Hash (PtH)**: Authenticating to a remote system using the underlying NTLM hash of a user's password, rather than the plaintext password itself.
