---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.12 Active Directory Schema and Attributes"
---

# Active Directory Schema and Attributes

Active Directory is, at its core, a highly optimized hierarchical database (Extensible Storage Engine - ESE, stored in `NTDS.dit`). Like any database, it requires a structural blueprint that dictates what kind of data can be stored, how it is formatted, and how it interrelates. This blueprint is known as the **Active Directory Schema**. 

Understanding the schema and object attributes is critical for attackers, as many post-exploitation persistence methods, lateral movement vectors, and privilege escalation attacks abuse misconfigurations in these foundational structures.

## The Active Directory Schema

The schema resides in its own partition (the Schema Naming Context) and is replicated across all Domain Controllers in the forest. It defines two primary components:
1.  **Classes (ObjectClasses):** Blueprints for objects that can be created in the directory (e.g., `User`, `Group`, `Computer`, `DomainDNS`).
2.  **Attributes:** The individual properties that can be associated with an object class (e.g., `sAMAccountName`, `userPassword`, `memberOf`, `servicePrincipalName`).

When a new object is created, AD looks at the ObjectClass definition to determine which attributes are mandatory and which are optional.

### The Schema Master (FSMO Role)
Changes to the schema (like installing Microsoft Exchange or creating custom application attributes) have forest-wide implications. To avoid conflicts, only one Domain Controller can make changes to the schema at any given time. This DC holds the **Schema Master** FSMO role. 

*   By default, the schema is locked to prevent accidental corruption.
*   Only members of the **Schema Admins** group can authorize schema modifications.

## ASCII Diagram: Schema Architecture

```text
+-------------------------------------------------------------------------+
|                       THE SCHEMA PARTITION                              |
|                CN=Schema,CN=Configuration,DC=lab,DC=local               |
+-------------------------------------------------------------------------+
       |                                              |
       v                                              v
+-----------------------+                  +-----------------------+
|    CLASS DEFINITIONS  |                  | ATTRIBUTE DEFINITIONS |
|                       |                  |                       |
| - classSchema: User   |                  | - attributeSchema:    |
| - classSchema: Group  |                  |   sAMAccountName      |
| - classSchema: Comp   |                  | - attributeSchema:    |
|                       |                  |   userPassword        |
+-----------------------+                  +-----------------------+
       |                                              |
       |             [ BLUEPRINT MAPPING ]            |
       +----------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------------+
|                       DOMAIN PARTITION (Data)                           |
|                          DC=lab,DC=local                                |
+-------------------------------------------------------------------------+
|                                                                         |
|  Object: CN=John Doe,CN=Users,DC=lab,DC=local                           |
|  [Object Class]: User                                                   |
|                                                                         |
|  [Attributes]:                                                          |
|    - sAMAccountName: jdoe                                               |
|    - userAccountControl: 512 (Normal Account)                           |
|    - memberOf: CN=Domain Admins,CN=Users,DC=lab,DC=local                |
|                                                                         |
+-------------------------------------------------------------------------+
```

## Critical Attributes for VAPT

Attackers heavily rely on querying specific attributes via LDAP (Lightweight Directory Access Protocol) to map the domain, discover attack paths, and extract sensitive data.

### 1. `userAccountControl` (UAC)
This is a bitmask attribute that dictates the behavioral properties of an account. It is one of the most heavily enumerated attributes during an assessment.
*   **Bit 512 (0x0200):** NORMAL_ACCOUNT (Standard user).
*   **Bit 4194304 (0x400000):** DONT_REQ_PREAUTH. If this flag is set, the account is vulnerable to **AS-REP Roasting**.
*   **Bit 524288 (0x80000):** TRUSTED_TO_AUTH_FOR_DELEGATION. Indicates the account is configured for Constrained Delegation with Protocol Transition.
*   **Bit 8192 (0x2000):** SERVER_TRUST_ACCOUNT (Domain Controller account).

### 2. `servicePrincipalName` (SPN)
SPNs are used by Kerberos to associate a service instance with a service logon account. 
*   **Attack Vector:** If a standard user account has an SPN assigned, it is vulnerable to **Kerberoasting**. An attacker can request a TGS (Ticket Granting Service) ticket for that SPN and crack the ticket offline to recover the user's plaintext password.

### 3. `ms-DS-MachineAccountQuota`
This attribute is defined at the domain root level. It dictates how many computer accounts a standard, unprivileged user is allowed to join to the domain.
*   **Default Value:** `10`
*   **Attack Vector:** Attackers abuse this to create dummy computer accounts, which are heavily used in Resource-Based Constrained Delegation (RBCD) attacks, relay attacks (like exploiting WebDAV), or simply to generate an account with a known password and SPN for further exploitation.

### 4. `AdminCount`
When an account is added to a highly privileged group (like Domain Admins), a background process called **SDProp** runs and sets the `AdminCount` attribute to `1`. It also overwrites the object's ACL with the `AdminSDHolder` template.
*   **Attack Vector:** Attackers query LDAP for `(adminCount=1)` to quickly map all high-value targets in the domain, even if they have been temporarily removed from the Domain Admins group.

### 5. `sAMAccountName` vs `userPrincipalName`
*   `sAMAccountName`: The legacy pre-Windows 2000 logon name (e.g., `JDOE`). Max 20 characters.
*   `userPrincipalName` (UPN): The modern, email-like logon name (e.g., `john.doe@lab.local`).
Attackers query these to build wordlists for password spraying or brute forcing.

## Offensive Schema Modification

If an attacker achieves `Schema Admin` privileges, they can theoretically introduce malicious classes or attributes into the schema. This is considered an Advanced Persistent Threat (APT) level persistence mechanism.

**Concept: Hidden Attributes**
An attacker could create a new attribute, e.g., `ms-DS-RecoveryPass`, attach it to the `User` class, and set the `searchFlags` bitmask to `RO` (Read-Only) or mark it as Confidential. They can then store plaintext backdoor passwords for all users in this attribute, invisible to standard sysadmins using standard MMC snap-ins.

## LDAP Querying with PowerView / ADSearch
Enumerating attributes is typically done via LDAP queries.

**Example 1: Finding AS-REP Roastable accounts (UAC bitwise math)**
```powershell
# Using PowerView to find DONT_REQ_PREAUTH
Get-DomainUser -UACFilter DONT_REQ_PREAUTH -Properties samaccountname, useraccountcontrol
```

**Example 2: Finding Kerberoastable accounts (Accounts with SPNs)**
```bash
# Using Impacket's GetUserSPNs to target the servicePrincipalName attribute
impacket-GetUserSPNs 'lab.local/jdoe:Password123!' -request
```

## Defensive Considerations

*   **Restrict LDAP Enumeration:** Ensure unauthenticated LDAP access is blocked. Implement Network Security settings to require LDAP Signing and LDAP over TLS (LDAPS) to prevent credential capture and tampering.
*   **Monitor `ms-DS-MachineAccountQuota`:** Change the default value from `10` to `0` to prevent unprivileged users from injecting computer objects into the domain.
*   **Schema Modification Alerts:** Monitor Event ID 5136 (A directory service object was modified) focusing on changes within the `CN=Schema,CN=Configuration...` partition. Schema changes are exceptionally rare in production outside of major upgrades.

---

## Real-World Attack Scenario

Operating from a compromised workstation as a standard user, an attacker uses PowerView to systematically query LDAP for valuable Active Directory attributes. They first filter for `(userAccountControl:1.2.840.113556.1.4.803:=4194304)` to identify accounts with `DONT_REQ_PREAUTH` enabled, immediately executing an AS-REP Roasting attack to capture a crackable hash. Concurrently, they search for the `ms-DS-MachineAccountQuota` attribute at the domain root, discovering it's set to the default value of 10. Realizing they can add computer objects to the domain, the attacker provisions a dummy machine account (`evilpc$`), setting the stage for a Resource-Based Constrained Delegation (RBCD) attack against a vulnerable server to achieve lateral movement and privilege escalation.

## Chaining Opportunities

*   **Attribute Enumeration -> Kerberoasting**: Discovering populated `servicePrincipalName` attributes on user objects allows for immediate transition into Kerberoasting. See [[16 - Kerberos Authentication and AS-REP Roasting]].
*   **UAC Bit Manipulation -> RBCD**: If an attacker has write access over a machine object's attributes, they can manipulate the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute to perform Resource-Based Constrained Delegation. 

## Related Notes
*   [[11 - Security Identifiers SIDs and Relative IDs RIDs]]
*   [[13 - Local Administrator vs Domain Administrator]]
*   [[16 - Kerberos Authentication and AS-REP Roasting]]
*   [[17 - Access Control Lists ACLs and ACEs]]
