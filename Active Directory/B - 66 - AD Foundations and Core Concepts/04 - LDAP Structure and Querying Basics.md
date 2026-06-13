---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.04 LDAP Structure and Querying Basics"
---

# LDAP Structure and Querying Basics

Active Directory Domain Services (AD DS) is fundamentally built upon the Lightweight Directory Access Protocol (LDAP). While Kerberos handles authentication and DNS handles location routing, LDAP is the protocol used to read, write, and search the directory database itself. 

For an attacker, LDAP is the ultimate reconnaissance tool. By mastering LDAP querying, an attacker can enumerate users, identify high-value targets, map group policies, discover unconstrained delegation, and locate vulnerable objects—often without triggering security alerts, as LDAP queries are standard, expected traffic in a Windows domain.

## What is LDAP?

LDAP is an open, vendor-neutral, industry-standard application protocol for accessing and maintaining distributed directory information services. In an Active Directory environment, the LDAP service runs on the Domain Controllers.
- **Port 389 (TCP/UDP):** Unencrypted LDAP (or LDAP wrapped in SASL/GSSAPI for integrity).
- **Port 636 (TCP):** LDAPS (LDAP over SSL/TLS).
- **Port 3268 (TCP):** Global Catalog (Unencrypted).
- **Port 3269 (TCP):** Global Catalog over SSL/TLS.

## The Directory Information Tree (DIT)

Active Directory organizes objects in a hierarchical structure known as the Directory Information Tree (DIT). Every object in AD has a unique path in this tree, defined by its Distinguished Name (DN).

### Naming Contexts
A Distinguished Name is constructed using a series of naming components (Relative Distinguished Names, or RDNs) that trace the path from the object up to the root of the domain.
- **DC (Domain Component):** Represents the domain namespace. Example: `DC=corp,DC=local`.
- **OU (Organizational Unit):** A logical container used for grouping objects for administrative delegation and Group Policy application. Example: `OU=IT,OU=Employees`.
- **CN (Common Name):** Represents leaf objects (like users, groups, or computers) or default built-in containers. Example: `CN=John Doe` or `CN=Users`.

**Example of a full Distinguished Name (DN):**
`CN=John Doe,OU=IT,OU=Employees,DC=corp,DC=local`

## ASCII Diagram: The LDAP Directory Information Tree

```text
=============================================================================
                   DIRECTORY INFORMATION TREE (DIT)
=============================================================================

                           [ DC=corp, DC=local ]
                             (Domain Root)
                                   |
           +-----------------------+-----------------------+
           |                       |                       |
    [ CN=Builtin ]           [ CN=Users ]          [ OU=Departments ]
   (Built-in Groups)     (Default User Cont.)     (Organizational Unit)
           |                       |                       |
    +------+------+         +------+------+         +------+------+
    |             |         |             |         |             |
[CN=Admin] [CN=Guests] [CN=Alice]  [CN=Bob]     [OU=HR]       [OU=IT]
                                                    |             |
                                              [CN=HR-Grp]  [CN=S-Admin]
                                                           (John Doe)
```

## Core AD Schema Attributes

When querying LDAP, you are essentially asking the Domain Controller to return objects that possess specific attributes. Understanding these attributes is vital for reconnaissance.

- `sAMAccountName`: The pre-Windows 2000 logon name (e.g., `jdoe`). This is the most common username format used in AD.
- `userPrincipalName` (UPN): The modern logon name, formatted like an email (e.g., `jdoe@corp.local`).
- `objectClass`: Defines what type of object it is (e.g., `user`, `computer`, `group`).
- `objectCategory`: Similar to `objectClass`, but typically used for optimization in indexing and searching.
- `memberOf`: A multi-valued attribute containing the DNs of the groups the object belongs to.
- `userAccountControl` (UAC): A bitmask integer that dictates account properties (e.g., password never expires, account disabled, trusted for unconstrained delegation).
- `pwdLastSet`: The timestamp of when the password was last changed. (Useful for finding stale accounts).
- `servicePrincipalName` (SPN): Identifies services running under the context of the account (Crucial for Kerberoasting).

## LDAP Query Syntax and Operators

LDAP filters use prefix notation, where the operator comes *before* the operands, enclosed in parentheses.

**Basic Syntax:**
`(attribute=value)`
Example: `(sAMAccountName=Administrator)`

**Wildcards:**
`(sAMAccountName=admin*)` (Finds any user starting with "admin")

### Logical Operators
- **AND (`&`):** `(&(objectClass=user)(sAMAccountName=jdoe))` -> Finds a user object with the name jdoe.
- **OR (`|`):** `(|(sAMAccountName=jdoe)(sAMAccountName=asmith))` -> Finds either jdoe or asmith.
- **NOT (`!`):** `(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))` -> Finds user objects where the account is NOT disabled.

### Advanced Bitwise Queries
Because attributes like `userAccountControl` are bitmasks (a single integer representing multiple boolean flags), you cannot query them with simple equals statements. You must use LDAP Matching Rules.
- **Bitwise AND:** `1.2.840.113556.1.4.803`
  - Example: `(userAccountControl:1.2.840.113556.1.4.803:=512)` -> Finds normal accounts.
  - Example: `(userAccountControl:1.2.840.113556.1.4.803:=524288)` -> Finds accounts trusted for unconstrained delegation.
- **In-Chain (Nested Group Lookup):** `1.2.840.113556.1.4.1941`
  - Example: `(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=corp,DC=local)` -> Recursively finds all members of the Domain Admins group, including those nested inside other groups.

## Offensive LDAP Querying Tools

Reconnaissance in an AD environment relies heavily on automated and manual LDAP queries.

1. **PowerView:** A PowerShell tool integrated into PowerSploit used extensively by red teams.
   - Example: `Get-DomainUser -LDAPFilter "(&(objectCategory=person)(objectClass=user)(adminCount=1))"` (Finds high-privileged users protected by AdminSDHolder).
2. **BloodHound / SharpHound:** Automates the collection of LDAP data (group memberships, ACLs, trusts) to map attack paths. It heavily utilizes LDAP search requests in the background.
3. **ldapsearch:** A built-in Linux utility perfect for attacking from a non-domain joined machine.
   - Example: `ldapsearch -x -H ldap://192.168.1.10 -D "corp\user" -w "password" -b "DC=corp,DC=local" "(servicePrincipalName=*)"`
4. **ADSearch / Standalone C# tools:** Security tools written in .NET that hook into standard `DirectorySearcher` classes to evade PowerShell logging.

## Anonymous Binds & Null Sessions

Historically, Active Directory allowed **Anonymous Binds** (connecting to LDAP without any credentials). Modern AD DS configurations disable this by default, but it is sometimes re-enabled for legacy application support.
If an attacker finds an Anonymous Bind enabled, they can enumerate the entire directory (users, computers, groups, descriptions) without possessing a single valid domain credential, drastically accelerating the attack chain.

## Real-World Attack Scenario

**The Context:** An attacker has connected a personal laptop to the corporate guest network but found a poorly configured VLAN trunk allowing them to reach a Domain Controller (`DC01.corp.local`). They possess no credentials but need a foothold.

**The Thought Process:** While modern AD restricts anonymous binds, the attacker tests for legacy misconfigurations. If anonymous bind is enabled, they can query LDAP without credentials. Their goal is to find user accounts configured with "Do not require Kerberos preauthentication" (`userAccountControl` flag 4194304). By identifying these users, the attacker can request their Ticket Granting Tickets (TGT) directly and attempt to crack the encrypted timestamp offline.

**The Execution:**
1. **Testing Anonymous Bind:** The attacker uses `ldapsearch` from their Kali Linux machine.
   `ldapsearch -x -H ldap://10.10.10.5 -b "DC=corp,DC=local" "(objectClass=user)" sAMAccountName`
   *The query returns a list of usernames, confirming anonymous bind is enabled.*
2. **Targeted LDAP Query:** The attacker queries the directory for accounts susceptible to AS-REPRoasting using a bitwise filter on the `userAccountControl` attribute.
   `ldapsearch -x -H ldap://10.10.10.5 -b "DC=corp,DC=local" "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" sAMAccountName`
   *The output reveals the account `svc_sql_backup`.*
3. **AS-REPRoasting:** The attacker uses Impacket's `GetNPUsers.py` to target the vulnerable account.
   `GetNPUsers.py -no-pass -dc-ip 10.10.10.5 corp.local/svc_sql_backup`
   *The tool requests a TGT and outputs a crackable hash string (e.g., `$krb5asrep$23$...`).*
4. **Offline Cracking:** The attacker loads the hash into `Hashcat` and cracks it against a dictionary.
   `hashcat -m 18200 hash.txt rockyou.txt`

**The Outcome:** The weak password for the `svc_sql_backup` account is cracked in under 10 minutes. The attacker has escalated from completely unauthenticated network access to a valid domain user account, providing the foothold necessary for further internal reconnaissance and lateral movement.

## Chaining Opportunities

- **LDAP Recon -> Kerberoasting:** An attacker uses an LDAP filter `(&(objectClass=user)(servicePrincipalName=*))` to find user accounts associated with SPNs. The attacker then requests Kerberos TGS tickets for these services and cracks them offline.
- **LDAP Recon -> AS-REPRoasting:** Using the filter `(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))` to find accounts where "Do not require Kerberos preauthentication" is checked, allowing the attacker to request ticket granting tickets and crack the encrypted component offline.
- **Description Field Harvesting:** Admins often leave plaintext passwords in the `description` or `info` attributes. Querying `(&(objectClass=user)(description=*pass*))` can yield immediate privilege escalation.

## Related Notes
- [[01 - What is Active Directory Domains Trees and Forests]]
- [[02 - Understanding FSMO Roles and Domain Controllers]]
- [[05 - Users Groups and Computers OUs vs Containers]]
