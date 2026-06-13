---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.02 Understanding FSMO Roles and Domain Controllers"
---

# Understanding FSMO Roles and Domain Controllers

At the heart of an Active Directory environment are the Domain Controllers (DCs). These servers respond to authentication requests, manage Active Directory data, and enforce security policies. While Active Directory utilizes a multi-master replication model—meaning most changes can be written to any Domain Controller and will be replicated to the others—there are specific tasks that are too sensitive or complex to be handled in a decentralized manner. This is where Flexible Single Master Operations (FSMO) roles come into play.

Understanding the behavior of Domain Controllers, the Global Catalog, and the distribution of FSMO roles is critical for offensive security professionals. Attackers often target specific DCs based on the roles they hold to execute advanced attacks, such as DCSync, DCShadow, or manipulating the password replication policies.

## Domain Controllers: The Core Infrastructure

A Domain Controller is a server running Windows Server with the Active Directory Domain Services (AD DS) role installed. Every DC hosts a complete, writable copy of the directory partition for its specific domain, stored in the `NTDS.dit` database file.

### Read/Write vs. Read-Only Domain Controllers (RODC)
- **Read/Write DC:** The standard implementation. Administrators can create, modify, or delete AD objects by connecting to any read/write DC. The changes replicate across the environment.
- **Read-Only DC (RODC):** Introduced to deploy DCs in branch offices with poor physical security. An RODC holds a read-only copy of the `NTDS.dit`. Critically, it does not store user passwords by default, relying instead on a Password Replication Policy (PRP) which dictates which specific accounts (usually branch office users) can have their credentials cached on the RODC.

### The Global Catalog (GC)
The Global Catalog is a partial, read-only representation of every domain within the forest. Every DC holds a full copy of its own domain's objects, but a DC configured as a Global Catalog server also holds a subset of attributes (like user principal names and group memberships) for all objects in *every other domain* in the forest.
- The GC operates on TCP ports 3268 (LDAP) and 3269 (LDAPS).
- It is crucial for forest-wide authentication, particularly for resolving universal group memberships when users log in.

## FSMO Roles Explained

To prevent conflicting updates in a multi-master environment, Active Directory assigns five specific roles to designated Domain Controllers. These are the FSMO (Flexible Single Master Operations) roles. Two are forest-wide (only one exists per forest), and three are domain-wide (one exists per domain).

### Forest-Wide Roles

1. **Schema Master**
   - **Scope:** One per Forest.
   - **Function:** Controls all updates and modifications to the Active Directory schema. The schema dictates what attributes and classes of objects can exist in the directory (e.g., adding an "employeeID" field to user objects).
   - **Impact of Loss:** Temporary loss has minimal impact on end-users. Schema modifications are rare in a mature environment.
   - **Security Context:** Only members of the `Schema Admins` group can initiate changes here.

2. **Domain Naming Master**
   - **Scope:** One per Forest.
   - **Function:** Controls the addition or removal of domains within the forest. It ensures that domain names are unique and manages the creation of cross-reference objects to external directories.
   - **Impact of Loss:** New domains cannot be added or removed, but day-to-day operations continue seamlessly.
   - **Security Context:** Only members of the `Enterprise Admins` group can add or remove domains.

### Domain-Wide Roles

3. **PDC (Primary Domain Controller) Emulator**
   - **Scope:** One per Domain.
   - **Function:** The most heavily utilized and critical FSMO role. It acts as the authoritative time server for the domain (Kerberos relies heavily on synchronized time to prevent replay attacks). The PDC Emulator also handles password updates immediately—if a user changes their password, it is rushed to the PDC Emulator to prevent authentication failures before normal replication occurs. Furthermore, if a user fails authentication against a standard DC, the DC will forward the request to the PDC Emulator to check if the password was recently changed before locking the account out.
   - **Impact of Loss:** Immediate disruption. Password changes won't be universally recognized immediately, account lockouts may become erratic, and time desynchronization will rapidly break Kerberos authentication.
   - **Attacker Focus:** Because the PDC Emulator processes password changes and lockouts, it is a primary target for attackers performing password spraying or attempting to change passwords of high-value targets.

4. **RID (Relative ID) Master**
   - **Scope:** One per Domain.
   - **Function:** Every object in AD has a Security Identifier (SID). The SID is composed of a Domain SID (which is identical for all objects in the domain) and a Relative ID (RID) which is unique to each object. The RID Master allocates pools of RIDs (usually in blocks of 500) to each Domain Controller in the domain. When a DC creates a new object (like a user), it assigns an unused RID from its local pool.
   - **Impact of Loss:** DCs will eventually run out of their local RID pools. Once exhausted, no new objects (users, computers, groups) can be created on that DC until the RID Master comes back online.

5. **Infrastructure Master**
   - **Scope:** One per Domain.
   - **Function:** Responsible for updating object references across domains. For example, if a user from Domain A is added to a group in Domain B, and the user's name is later changed in Domain A, the Infrastructure Master in Domain B is responsible for updating the group's membership display to reflect the new name.
   - **Note on GC:** The Infrastructure Master should *not* be placed on a Global Catalog server unless the forest contains only one domain, or every DC in the domain is a GC. Otherwise, the Infrastructure Master will fail to update object references properly.

## ASCII Diagram: FSMO Role Distribution

Below is a visualization mapping out how FSMO roles are typically distributed in a multi-domain forest.

```text
=============================================================================
                     FSMO ROLE DISTRIBUTION HIERARCHY
=============================================================================

                      [ FOREST: ROOT.LOCAL ]
                      +------------------------------------------+
                      | DC-ROOT-01 (Forest Root DC)              |
                      | ---------------------------------------- |
                      | * Schema Master    (Forest-Wide)         |
                      | * Naming Master    (Forest-Wide)         |
                      | * PDC Emulator     (Domain: root.local)  |
                      | * RID Master       (Domain: root.local)  |
                      | * Infrastructure   (Domain: root.local)  |
                      | * Global Catalog Server                  |
                      +------------------------------------------+
                                          |
                                [ Intra-Forest Trust ]
                                          |
                      [ DOMAIN: CHILD.ROOT.LOCAL ]
        +------------------------------------------+
        | DC-CHILD-01 (Primary DC in Child)        |
        | ---------------------------------------- |
        | * PDC Emulator     (Domain: child)       |
        | * RID Master       (Domain: child)       |
        | * Global Catalog Server                  |
        +------------------------------------------+
                              |
                              | (Replication)
                              |
        +------------------------------------------+
        | DC-CHILD-02 (Secondary DC in Child)      |
        | ---------------------------------------- |
        | * Infrastructure   (Domain: child)       |
        | * No GC (Best Practice for Infra Master) |
        +------------------------------------------+
```

## Attacking Domain Controllers and FSMO Roles

From an offensive perspective, Domain Controllers are the ultimate prize. The compromise of a DC effectively equals the compromise of the domain.

### DCSync Attacks
The DCSync attack simulates the behavior of a Domain Controller utilizing the Directory Replication Service (DRS) Remote Protocol (MS-DRSR). By sending `DSGetNCChanges` requests, an attacker can ask a DC to replicate user credentials (including password hashes) over the network.
- Requires `Replicating Directory Changes` and `Replicating Directory Changes All` privileges.
- By default, Domain Admins and Enterprise Admins possess these rights.
- DCSync targets the domain controller directly, meaning no code execution on the DC is required.

### DCShadow Attacks
DCShadow is an extremely stealthy post-exploitation attack designed to bypass traditional logging. Instead of modifying objects using standard LDAP or RPC calls, the attacker registers a rogue Domain Controller (using their own workstation) by modifying the Configuration partition.
- The attacker then pushes raw AD object changes (e.g., modifying the SID History of a standard user, or injecting a new DA) via malicious replication into the legitimate AD infrastructure.
- Because the changes arrive via standard replication protocols, many SIEM and Event Log monitoring solutions that hook into LDAP modifications or API calls fail to detect the change.

### Targeting the PDC Emulator
Because the PDC Emulator serves as the time-sync master and password authority:
- Attackers performing Time-Based Kerberos attacks (such as Golden Tickets with forged timestamps) must ensure their injected time is in sync with the PDC emulator.
- When performing targeted password resets to hijack accounts, verifying the change has propagated to the PDC emulator ensures the new credentials can be used immediately across the entire domain.

### Exploiting RODCs
When an attacker compromises a Read-Only Domain Controller, they cannot dump the entire domain's `NTDS.dit`. However, they *can* extract the cached credentials allowed by the Password Replication Policy (PRP). Additionally, if the attacker discovers excessive permissions allowing the RODC computer account to modify properties of administrative accounts, they might escalate privileges.

## Real-World Attack Scenario

**The Context:** An attacker has gained a foothold as a standard user (`jsmith`) in the `finance.local` domain. The goal is complete domain compromise. The environment is large, spanning multiple physical sites with over 15 Domain Controllers.

**The Thought Process:** The attacker knows that not all Domain Controllers are equal. While any DC can authenticate users, the PDC (Primary Domain Controller) Emulator holds the authoritative copy of passwords and processes account lockouts. Furthermore, password updates are immediately sent to the PDC Emulator. By targeting the PDC Emulator for a DCSync attack, the attacker ensures they extract the absolute most up-to-date credential material, avoiding replication delays inherent in multi-site environments.

**The Execution:**
1. **FSMO Role Reconnaissance:** The attacker first identifies which Domain Controller holds the PDC Emulator role using built-in Windows binaries, avoiding noisy third-party tools.
   `netdom query fsmo`
   *Output shows `DC-Core-01.finance.local` holds the PDC role.*
2. **Finding the Path:** The attacker runs BloodHound and queries for paths from `jsmith` to the `Domain Admins` group. They find that `jsmith` has `WriteDACL` permissions over a custom group `Tier1_Admins`, which in turn has RDP access to a server where a Domain Admin session is disconnected.
3. **Escalation:** The attacker uses `PowerView` to grant themselves full control over `Tier1_Admins`, adds themselves to the group, RDPs into the server, and uses `Taskmgr.exe` to dump LSASS, recovering the Domain Admin's cleartext credentials.
4. **Targeted DCSync:** Armed with Domain Admin credentials, the attacker performs a DCSync attack. Crucially, they specify the PDC Emulator as the target to ensure they get the latest NTLM hashes for all users.
   `mimikatz # lsadump::dcsync /domain:finance.local /dc:DC-Core-01.finance.local /all /csv`

**The Outcome:** By specifically targeting the PDC Emulator, the attacker avoids any AD replication lag. They successfully extract the NT hashes for all domain users, including the `krbtgt` account. With the `krbtgt` hash, they forge a Golden Ticket, ensuring persistent, undetectable access to the domain even if the compromised Domain Admin's password is reset.

## Chaining Opportunities

- **DCSync to Golden Ticket:** Once a user gains the required DCSync privileges (e.g., via ACL abuse on the domain root), they can DCSync the `krbtgt` account hash from any Domain Controller. With the `krbtgt` hash, the attacker can forge a Golden Ticket granting infinite, undetectable persistence within the domain.
- **Rogue DC injection:** Compromising an account with privileges over the Configuration naming context allows an attacker to spawn a DCShadow instance, silently altering the `adminCount` or `primaryGroupID` of an attacker-controlled account without raising standard LDAP modification alerts.

## Related Notes
- [[01 - What is Active Directory Domains Trees and Forests]]
- [[03 - Active Directory DNS and Name Resolution]]
- [[04 - LDAP Structure and Querying Basics]]
- [[05 - Users Groups and Computers OUs vs Containers]]
