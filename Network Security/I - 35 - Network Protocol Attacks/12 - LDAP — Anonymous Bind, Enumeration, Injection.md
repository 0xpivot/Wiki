---
tags: [ldap, active-directory, enumeration, injection, protocol-attack]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.12 LDAP"
---

# Lightweight Directory Access Protocol (LDAP) Exploitation

The Lightweight Directory Access Protocol (LDAP) is the core application protocol for querying and modifying directory services. In enterprise environments, it serves as the primary backbone for Microsoft Active Directory (AD), allowing applications, users, and systems to look up information about domain objects (users, groups, computers, policies). It typically runs on TCP/UDP port 389 (Cleartext/STARTTLS) and TCP 636 (LDAPS/SSL).

Because it acts as the centralized phonebook for an organization's entire IT infrastructure, exploiting or maliciously querying LDAP provides an attacker with a profound map of the network, trust relationships, and potential privilege escalation paths.

## Protocol Architecture and Naming Conventions

LDAP structures data in a hierarchical tree. Every object has a Distinguished Name (DN) that uniquely identifies it.
- **DC (Domain Component):** E.g., `DC=corp,DC=local` for `corp.local`.
- **OU (Organizational Unit):** E.g., `OU=IT,OU=Users`.
- **CN (Common Name):** E.g., `CN=Administrator` or `CN=Computers`.

A typical user object DN looks like this:
`CN=John Doe,OU=Sales,DC=corp,DC=local`

---

## Attack Surface Overview

```ascii
+----------------+                              +-------------------------------+
|                |      1. Anonymous Bind       |                               |
|   Attacker     |      (No credentials)        |       Domain Controller       |
|                |----------------------------->|       (LDAP Service)          |
| Tools:         |                              |       Port: 389 / 636         |
| - ldapsearch   |      2. Base Naming Context  |                               |
| - BloodHound   |<-----------------------------|       Tree Structure:         |
| - Nmap         |                              |       DC=corp,DC=local        |
| - AdExplorer   |      3. LDAP Query           |        |- OU=Admins           |
|                |      (e.g., objectClass=User)|        |- CN=Administrator    |
|                |----------------------------->|        |- OU=ServiceAccounts  |
|                |                              |                               |
|                |      4. Full Dump of AD      |                               |
|                |<=============================|                               |
+----------------+                              +-------------------------------+
```

---

## 1. Anonymous Binding and Information Disclosure

By default, an LDAP client must "bind" (authenticate) to the server before issuing queries. An **Anonymous Bind** occurs when a server is misconfigured to allow queries without requiring a username or password.

Historically, older versions of Windows Server allowed anonymous binds to dump the entire Active Directory structure. While modern Windows Server deployments block deep anonymous queries by default, they still permit access to the **RootDSE** (Root Directory Specific Entry).

### Querying RootDSE (Unauthenticated)
Even without credentials, an attacker can query the RootDSE to gather critical domain information, such as the Domain Name, server configuration, and supported authentication mechanisms.
```bash
# Using ldapsearch with an empty (-x) anonymous bind
ldapsearch -x -H ldap://10.10.10.10 -s base -b ""

# Using Nmap
nmap -p 389 --script ldap-rootdse 10.10.10.10
```

### Deep Anonymous Binding (Misconfiguration)
If the administrator explicitly enabled anonymous binding, an attacker can dump every object in the directory.
```bash
# Dumping the entire directory via anonymous bind
ldapsearch -x -H ldap://10.10.10.10 -b "DC=corp,DC=local"
```

---

## 2. Authenticated Enumeration (The Goldmine)

Once an attacker compromises any valid domain account—even the lowest-privileged intern account—they can perform an authenticated bind. **By default, any authenticated user in Active Directory has Read access to almost the entire LDAP directory.**

This is how tools like BloodHound map the network.

### Powerful LDAP Filters for Attackers

Using `ldapsearch` with valid credentials:
```bash
# Authenticated Bind
ldapsearch -x -H ldap://10.10.10.10 -D "CORP\jdoe" -w "Password123" -b "DC=corp,DC=local"
```

Attackers use specific LDAP filters to find high-value targets:

**1. Finding Domain Admins:**
```text
(&(objectCategory=user)(memberOf=CN=Domain Admins,CN=Users,DC=corp,DC=local))
```

**2. Finding User Accounts with SPNs (Kerberoasting Targets):**
Service Principal Names (SPNs) indicate the account is tied to a service. These accounts are vulnerable to Kerberoasting.
```text
(&(objectCategory=user)(servicePrincipalName=*))
```

**3. Finding Accounts that do not require Kerberos Pre-Authentication (AS-REP Roasting Targets):**
`userAccountControl` bit 4194304 denotes `DONT_REQ_PREAUTH`.
```text
(&(objectCategory=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))
```

**4. Extracting Descriptions (Cleartext Passwords):**
IT staff frequently put passwords or sensitive deployment notes in the `description` or `info` fields of user and computer objects.
```bash
ldapsearch -x -H ldap://10.10.10.10 -D "CORP\jdoe" -w "Password123" -b "DC=corp,DC=local" "(description=*pass*)"
```

### Tooling: BloodHound and SharpHound
Manual LDAP querying is tedious. Attackers deploy `SharpHound.exe` or `bloodhound.py` to automate thousands of LDAP queries, mapping ACLs, group delegations, and session data, and exporting it into a graph database to visually plot the path to Domain Admin.

---

## 3. LDAP Injection

LDAP Injection is a web application vulnerability, but it directly attacks the underlying LDAP protocol. It occurs when user input is unsanitized and passed directly into an LDAP search filter by a backend application (like a web login portal or a directory search feature).

### Mechanics of Injection
Consider a backend PHP script that searches for a user to log them in:
```php
$filter = "(&(USER=" . $_POST['user'] . ")(PASSWORD=" . $_POST['password'] . "))";
```

If an attacker inputs `admin)(|(USER=*` into the user field, the resulting query becomes:
```text
(&(USER=admin)(|(USER=*)(PASSWORD=random_text)))
```
Because `(|(USER=*))` evaluates to True (Match any user), the password requirement is bypassed, and the application logs the attacker in as `admin`.

### Advanced LDAP Injection (Data Extraction)
If a web application has an active directory search field (e.g., "Find Employee"), an attacker can use wildcards and boolean inference to blindly extract attributes of other users.
Inputting `admin)(description=A*` might return the admin user if their description starts with 'A'. By scripting this, an attacker can extract sensitive LDAP attributes character by character through a web interface.

---

## Defensive Countermeasures & Hardening

1. **Disable Anonymous Binding:** Ensure that `LdapEnforceChannelBinding` and `LdapServerIntegrity` (LDAP Signing) are enforced via Group Policy to prevent anonymous access and man-in-the-middle attacks.
2. **Implement LDAP over SSL (LDAPS):** Standard LDAP (Port 389) transmits credentials and directory data in cleartext. LDAPS (Port 636) encrypts the transport layer, protecting data from network sniffers.
3. **Restrict Attribute Read Access:** While regular users need to read the directory, they do not need to read sensitive attributes like LAPS passwords, BitLocker keys, or internal administrative notes. Edit the Active Directory Schema and ACLs to restrict Read permissions on sensitive attributes.
4. **Sanitize Inputs for LDAP Queries:** Applications that interface with LDAP must strictly sanitize user inputs, escaping characters like `(`, `)`, `*`, `\`, and `\0` to prevent LDAP injection attacks. Framework-specific parameterized queries for LDAP should be used where available.

---

## Chaining Opportunities

- **LDAP -> Kerberoasting**: Use LDAP to extract a list of users with the `servicePrincipalName` attribute set, then switch to Kerberos to request TGS tickets for those accounts and crack them offline.
- **LDAP -> Cleartext Passwords**: Dump the `description` or `userParameters` attributes of all AD objects to find hardcoded passwords left by lazy administrators, using them to escalate privileges or move laterally.
- **LDAP Injection -> Application Takeover**: Bypass authentication portals via LDAP injection, gaining administrative access to enterprise web applications (e.g., VPN portals, internal wikis, or HR systems) backed by AD authentication.

## Related Notes
- [[13 - Kerberos — Pass-the-Hash, Pass-the-Ticket, Golden-Silver Ticket, Kerberoasting, AS-REP Roasting]]
- [[02 - Active Directory Architecture and Trust Relationships]]
- [[11 - NetBIOS — Enumeration, NBNS Poisoning]]
- [[04 - Port Scanning and Enumeration]]
