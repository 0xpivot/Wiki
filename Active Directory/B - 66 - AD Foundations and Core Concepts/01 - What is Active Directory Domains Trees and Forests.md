---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.01 What is Active Directory? Domains, Trees, and Forests"
---

# Active Directory Core Architecture: Domains, Trees, and Forests

Active Directory (AD) is Microsoft's proprietary directory service designed for Windows domain networks. It serves as a centralized and standardized system that automates network management of user data, security, and distributed resources, and enables interoperation with other directories. For a Penetration Tester or Red Teamer, understanding the architecture of Active Directory is paramount because it dictates how access controls are enforced, how lateral movement can be achieved, and how privileges can be escalated across trust boundaries.

Active Directory is not just a single database but a distributed hierarchical system of components. At its core, AD provides a mechanism to logically store objects (users, computers, groups, printers, and services) and centrally manage them via Group Policy Objects (GPOs) and access control lists (ACLs).

## The Logical Structure of Active Directory

Active Directory's architecture is divided into logical and physical structures. The logical structure dictates how network resources are organized and secured. It consists of Domains, Trees, and Forests.

### 1. The Domain: The Core Administrative Boundary
The domain is the fundamental logical building block of Active Directory. A domain is a collection of objects—such as users, computers, and groups—that share the same Active Directory database, security policies, and trust relationships. 

- **Security Policies:** Account policies, such as password complexity and lockout thresholds, are primarily enforced at the domain level.
- **Administrative Boundary:** By default, Domain Admins have complete control over all objects within their specific domain, but they do not automatically have administrative rights in other domains (even within the same forest).
- **Authentication and Authorization:** The domain acts as the authentication boundary. When a user logs in, a Domain Controller (DC) within that domain authenticates the user and provides a Ticket Granting Ticket (TGT) in a Kerberos environment.

For a penetration tester, compromising a domain typically means gaining control over its Domain Controllers, giving the attacker the ability to extract all password hashes (NTDS.dit) and create persistent backdoors (like Golden Tickets) valid for that specific domain.

### 2. The Tree: The Namespace Hierarchy
A domain tree is a collection of one or more Active Directory domains that share a contiguous namespace. When a new domain is added as a child to an existing domain, it automatically forms a tree and inherits the parent's namespace.

For example, if the parent domain is `corp.local`, a child domain could be created as `us.corp.local` and another as `eu.corp.local`. 

- **Contiguous Namespace:** Every domain in the tree shares the root domain's top-level namespace (`corp.local`).
- **Automatic Trusts:** When a child domain is added to a tree, a two-way transitive trust is automatically established between the parent and the new child domain. This means users in `us.corp.local` can potentially access resources in `eu.corp.local` if they are explicitly granted the necessary permissions, because `us` trusts `corp`, and `corp` trusts `eu`.

From an attacker's perspective, a tree provides a map for potential lateral movement. While domains are administrative boundaries, the default two-way transitive trusts mean that cross-domain authentication is seamlessly supported, setting the stage for cross-domain privilege escalation (e.g., using SID History to escalate from a child domain to a parent domain).

### 3. The Forest: The Ultimate Security Boundary
An Active Directory forest is the highest logical container in an AD configuration. It consists of one or more domain trees that share a common Global Catalog, directory schema, logical structure, and directory configuration. 

Crucially, **the forest, not the domain, is the true security boundary in Active Directory.**

- **Forest Root Domain:** The first domain created in a new forest is designated as the Forest Root Domain. It contains critical enterprise-wide administrative groups: the Enterprise Admins and the Schema Admins.
- **Shared Schema:** The schema defines the classes of objects and attributes that can be created in the directory. All domains in a forest share the same schema. If the schema is modified in one domain, the change replicates forest-wide.
- **Global Catalog (GC):** A searchable, partial representation of every object in every domain within the forest. It enables users to locate objects anywhere in the forest without needing to know which domain they belong to.
- **Transitive Trusts:** All domains within the same forest are linked by two-way transitive trusts, routing back to the forest root domain.

For VAPT, the concept of the forest as the true security boundary is critical. If an attacker compromises a child domain, they can often exploit trust relationships (such as the intra-forest Kerberos trust) to compromise the forest root domain, granting them absolute control over the entire forest architecture. 

## ASCII Architecture Diagram

Below is a visualization of the logical components of Active Directory, demonstrating how forests, trees, and domains interact via trust relationships.

```text
=============================================================================
                          ACTIVE DIRECTORY ARCHITECTURE
=============================================================================

                   [ THE FOREST ] (The Ultimate Security Boundary)
                         |
   +---------------------+---------------------+
   |                                           |
   |                                           |
[ TREE 1: corp.local ]               [ TREE 2: acquired.com ]
(Forest Root Domain)                 (New Tree in same Forest)
   |                                           |
   +---[ Two-Way Transitive Trust ]------------+
   |
   |
   +---[ PARENT DOMAIN ]
   |     corp.local
   |     (Domain Admins, Enterprise Admins)
   |
   +---> [ Two-way Transitive Trust (Parent-Child) ]
   |
   +---[ CHILD DOMAIN A ]            +---[ CHILD DOMAIN B ]
         us.corp.local                     eu.corp.local
         (Domain Admins)                   (Domain Admins)
               |
               +---> [ One-Way External Trust ] ---> [ Partner Forest ]
                                                     partner.local
```

## Deep Dive into Trust Relationships

Trusts are the mechanisms that allow users in one domain to access resources in another. Understanding trusts is vital for Red Teams planning lateral movement.

### Trust Directionality
- **One-Way Trust:** Domain A trusts Domain B. Users in Domain B can access resources in Domain A. Users in Domain A CANNOT access resources in Domain B. (Direction of trust is opposite to the direction of access).
- **Two-Way Trust:** Domain A trusts Domain B, and Domain B trusts Domain A. Users in either domain can be granted access to resources in the other domain.

### Trust Transitivity
- **Transitive Trust:** If Domain A trusts Domain B, and Domain B trusts Domain C, then Domain A inherently trusts Domain C. All default intra-forest trusts (Parent-Child and Tree-Root) are transitive.
- **Non-Transitive Trust:** The trust is strictly bound to the two domains involved. If A trusts B non-transitively, and B trusts C, A does NOT trust C.

### Types of Trusts
1. **Parent-Child Trust:** Automatically created, two-way, transitive intra-forest trust.
2. **Tree-Root Trust:** Automatically created, two-way, transitive trust between the root domains of different trees in the same forest.
3. **External Trust:** Manually created, non-transitive trust between domains in different forests, or between an AD domain and an NT4 domain. Often used when a full forest trust is not desired.
4. **Forest Trust:** Manually created, transitive trust between the root domains of two different forests. Allows users in one forest to access resources in another.
5. **Shortcut Trust:** Manually created, transitive trust between two domains within the same forest to optimize authentication traffic. Prevents authentication requests from having to walk up and down the tree hierarchy.
6. **Realm Trust:** Manually created trust between an AD domain and a non-Windows Kerberos v5 realm (e.g., a Linux Kerberos environment).

## Physical Structure vs. Logical Structure

While Domains and Forests are logical constructs, Active Directory must map to the physical layout of the network to optimize performance and replication.

- **Sites:** A site represents a physical location with highly reliable, fast network connectivity (typically a LAN). Sites dictate how AD replication occurs. Intra-site replication is fast and uncompressed; inter-site replication is compressed and scheduled.
- **Subnets:** IP ranges are assigned to Sites. When a client boots up, it uses its IP address to determine its AD Site and attempts to authenticate against a Domain Controller within that specific Site to minimize latency.
- **Domain Controllers (DCs):** The physical or virtual servers that host a copy of the AD database (`NTDS.dit`). Every DC in a domain holds a complete replica of the domain's objects.

## Attack Surface Implications

1. **SID Filtering & Trust Abuse:** When navigating across trusts, Active Directory utilizes a mechanism called SID Filtering to prevent users in one domain from improperly injecting high-privileged SIDs (like Enterprise Admins) from another domain. However, within the same forest, SID filtering is often relaxed for the `SIDHistory` attribute. Attackers can leverage tools like Mimikatz or Rubeus to forge ExtraSIDs in their Kerberos tickets, escalating from a child domain directly to the Forest Root domain.
2. **Reconnaissance with BloodHound:** Penetration testers map the logical structure and trust relationships using tools like BloodHound (via the SharpHound ingestor). BloodHound queries the directory for trust metadata, group memberships, and ACLs to graphically render the shortest path to Domain Admin or Enterprise Admin.
3. **Cross-Forest Trust Vulnerabilities:** Even in a one-way inbound trust from a highly secure forest to a less secure forest, misconfigurations in name suffix routing or unconstrained delegation can sometimes be abused to compromise the trusting domain.

## Defensive Strategies and Hardening

To protect the AD logical architecture, administrators should:
- Implement a **Tiered Administrative Model** (Tier 0 for DCs and core identity, Tier 1 for servers, Tier 2 for workstations).
- Utilize **Enhanced Security Administrative Environment (ESAE)** concepts, commonly known as a "Red Forest" or administrative bastion forest, though Microsoft's modern guidance leans towards cloud-based privileged access workstations (PAWs).
- Enable and enforce **Strict SID Filtering** on all external and forest trusts to prevent forged SID injection across forest boundaries.
- Limit the use of two-way external trusts, preferring one-way trusts where strict operational requirements mandate them.

## Real-World Attack Scenario

**The Context:** An attacker has compromised a low-privileged workstation in `dev.corp.local`, a child domain within the `corp.local` forest. The primary goal is to compromise the forest root domain (`corp.local`), which holds the Enterprise Admin credentials and primary financial data.

**The Thought Process:** The attacker knows that security boundaries in Active Directory are drawn at the forest level, not the domain level. The trust between `dev.corp.local` and `corp.local` is a two-way, transitive trust created implicitly by the forest structure. By compromising a Domain Admin in the child domain, the attacker can leverage the SID History attribute to forge a Golden Ticket that includes the Enterprise Admins SID from the root domain.

**The Execution:**
1. **Local Privilege Escalation & Recon:** The attacker uses PowerUp on the initial workstation to find an unquoted service path, elevating to local `SYSTEM`. They then run `BloodHound` to map the path to Domain Admin in `dev.corp.local`.
2. **Child Domain Takeover:** Following the BloodHound attack path, the attacker dumps LSASS memory using `Mimikatz`, finding a cleartext password for a Helpdesk user who has `GenericAll` rights over the `Domain Admins` group in the child domain. They add themselves to the group, taking over the child domain.
3. **KRBTGT Extraction:** Using DCSync, the attacker extracts the `krbtgt` hash for `dev.corp.local`.
   `mimikatz # lsadump::dcsync /domain:dev.corp.local /user:krbtgt`
4. **SID Harvesting:** The attacker queries the root domain to find the SID of the Enterprise Admins group.
   `Get-DomainGroup -Domain corp.local -Identity "Enterprise Admins" | Select-Object objectsid`
   *(Let's assume the SID is `S-1-5-21-ROOT-519`)*
5. **Forging the Golden Ticket:** The attacker creates a Golden Ticket for the child domain but injects the Enterprise Admins SID into the `sids` parameter (SID History).
   `mimikatz # kerberos::golden /user:Administrator /domain:dev.corp.local /sid:S-1-5-21-CHILD /sids:S-1-5-21-ROOT-519 /krbtgt:<child-krbtgt-hash> /ptt`

**The Outcome:** The forged Kerberos ticket is injected into the attacker's session. When the attacker attempts to list the `C$` share on the primary Domain Controller of the root domain (`dir \\dc01.corp.local\C$`), the root DC reads the SID History, sees the Enterprise Admins SID, and grants access. The attacker has successfully escalated from a child domain to full forest compromise.

## Chaining Opportunities

- **Privilege Escalation across Child/Parent Domains:** Once a child domain is compromised (e.g., Domain Admin acquired), attackers can extract the `krbtgt` hash of the child domain and forge an inter-realm Golden Ticket containing the SID of the Enterprise Admins group from the parent domain.
- **Trust Key Extraction:** If a DC is compromised, extracting the LSA secrets allows the attacker to obtain the trust passwords, enabling the forgery of inter-realm TGTs manually.

## Related Notes
- [[02 - Understanding FSMO Roles and Domain Controllers]]
- [[03 - Active Directory DNS and Name Resolution]]
- [[04 - LDAP Structure and Querying Basics]]
- [[05 - Users Groups and Computers OUs vs Containers]]
