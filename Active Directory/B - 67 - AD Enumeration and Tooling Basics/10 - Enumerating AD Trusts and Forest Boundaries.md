---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.10 Enumerating AD Trusts"
---

# 10 - Enumerating AD Trusts and Forest Boundaries

## 1. Introduction to Active Directory Trusts

In complex, enterprise-level network environments, a single Active Directory domain is rarely sufficient to manage the entire organizational structure. Companies frequently expand through mergers and acquisitions, or segment their networks for geopolitical and security reasons. This necessitates the creation of multiple domains and forests.

An **Active Directory Trust** is a relationship established between two domains (or forests) that allows users in one domain to access resources in another domain. It establishes an authentication link. Understanding and enumerating these trusts is a critical phase of a penetration test, as trusts often provide pathways to escalate privileges from a low-security subsidiary domain to the highly-secured parent/root domain.

### 1.1 Key Trust Concepts
- **Directionality:**
  - **One-Way Trust:** Domain A trusts Domain B. Users in Domain B can access resources in Domain A. Users in Domain A *cannot* access resources in Domain B. (Think of trust as pointing in the direction of the resource, while access flows in the opposite direction).
  - **Two-Way Trust:** Domain A and Domain B trust each other equally.
- **Transitivity:**
  - **Transitive Trust:** If Domain A trusts Domain B, and Domain B trusts Domain C, then Domain A inherently trusts Domain C.
  - **Non-Transitive Trust:** The trust relationship strictly applies only to the two domains explicitly involved.
- **Forest Boundaries:** The forest is generally considered the ultimate security boundary in Active Directory. However, Cross-Forest Trusts can bridge this boundary, creating massive, sprawling attack surfaces.

## 2. Architecture and Trust Flow Diagram

The following ASCII diagram illustrates a complex multi-domain architecture with transitive, non-transitive, and forest trusts.

```text
    FOREST A (corp.local)                           FOREST B (acquired.local)
+---------------------------+                     +---------------------------+
|                           |   Two-Way Forest    |                           |
|      corp.local (Root)    |<------------------->|    acquired.local (Root)  |
|                           |      Transitive     |                           |
+-------------+-------------+                     +-------------+-------------+
              ^                                                 ^
              | Two-Way                                         | One-Way External
              | Transitive                                      | Non-Transitive
              v                                                 | (Acquired trusts US)
+-------------+-------------+                                   |
|                           |                                   |
|    us.corp.local (Child)  |-----------------------------------+
|                           |
+---------------------------+

ATTACK SCENARIO:
1. Attacker compromises a workstation in 'us.corp.local'.
2. Due to the Two-Way Transitive trust, attacker maps a path to compromise 'corp.local' Root.
3. Due to the One-Way External trust, attacker in 'us.corp.local' can attempt to access 
   resources in 'acquired.local' (but not vice versa).
```

## 3. Enumeration Tooling Deep Dive

Trust enumeration involves querying the Domain Controller to pull the Trusted Domain Objects (TDOs). These queries can be performed securely and native tools are often sufficient.

### 3.1 PowerView (PowerShell)

PowerView is the premier tool for programmatic AD enumeration, making trust mapping incredibly straightforward.

**Get Trusts for Current Domain:**
```powershell
Get-DomainTrust
```

**Get Trusts for a Specific Domain:**
```powershell
Get-DomainTrust -Domain us.corp.local
```

**Output Snippet:**
```text
SourceName      : us.corp.local
TargetName      : corp.local
TrustType       : WINDOWS_ACTIVE_DIRECTORY
TrustAttributes : WITHIN_FOREST
TrustDirection  : Bidirectional
WhenCreated     : 10/15/2015 10:20:00 AM
```

### 3.2 BloodHound

BloodHound excels at visualizing complex trust relationships. By running the SharpHound collector, BloodHound automatically queries and maps all inter-domain and inter-forest trusts.

**In the BloodHound UI:**
- The pre-built query **"Map Domain Trusts"** creates a visual graph showing nodes as Domains and edges defining the trust directionality and transitivity.
- This visualization is crucial for finding "Foreign Group Membership" (e.g., a user in Domain A is a member of the Administrators group in Domain B).

### 3.3 Native Windows Tooling (nltest)

`nltest` is a native binary that administrators use to query domain trusts. It is highly effective for living-off-the-land techniques.

**List all trusted domains:**
```cmd
nltest /domain_trusts
```

**Output snippet:**
```text
List of domain trusts:
    0: corp.local (NT 5) (Forest Tree Root) (Primary Domain) (Native)
    1: acquired.local (NT 5) (Forest) (Direct Outbound) (Direct Inbound)
The command completed successfully
```

### 3.4 NetExec (formerly CrackMapExec)

NetExec can also perform rapid trust enumeration across targeted Domain Controllers.

**Command:**
```bash
nxc ldap 192.168.1.10 -u jsmith -p Password123 -M enum_trusts
```

## 4. Exploiting Trusts: The Concepts

Simply enumerating a trust does not equate to exploiting it; it just maps the pathways. Exploitation relies on abusing the technical implementations of these trusts.

### 4.1 SID History and SID Filtering
When a user is migrated from one domain to another, AD uses an attribute called `SIDHistory` to retain their old Security Identifier (SID). This ensures they do not lose access to resources in the old domain. 
An attacker with Domain Admin in a child domain can forge a Golden Ticket containing the `SIDHistory` of the Enterprise Admin group (from the root domain).
- **SID Filtering:** To prevent this attack across Forest boundaries, Microsoft enforces SID Filtering by default on Forest Trusts. It strips out foreign privileged SIDs from incoming tickets.
- **Intra-Forest:** SID Filtering is generally *disabled* between domains within the same forest, making child-to-root escalation trivial if the child domain is compromised.

### 4.2 Cross-Domain Authentication
If Domain A trusts Domain B, an attacker who compromises Domain B can perform password spraying, Kerberoasting, or pass-the-hash attacks against targets in Domain A, routing their authentication requests across the trust boundary.

## 5. Defensive Considerations and Remediation

### 5.1 Enforcing Forest Boundaries
The only true security boundary in Active Directory is the Forest. Child domains are merely management boundaries. If a child domain (e.g., `dev.corp.local`) is compromised, the root domain (`corp.local`) should be considered compromised due to intra-forest trust mechanisms and SID History abuse. High-security environments should implement separate Forests, not separate domains within the same Forest.

### 5.2 Implementing SID Filtering
Ensure SID Filtering is enabled on all External and Forest trusts. This prevents attackers from injecting high-privileged SIDs across the trust boundary.
```cmd
netdom trust corp.local /domain:acquired.local /quarantine:Yes
```

### 5.3 Selective Authentication
Instead of allowing Forest-wide authentication across a trust, administrators should configure **Selective Authentication**. This requires explicit permission grants on individual computer objects before users from the trusted forest can authenticate to them, drastically reducing the attack surface.

### 5.4 Tiered Administration
Implement Tiered Admin models (Tier 0, Tier 1, Tier 2). Ensure that Enterprise Admins and Domain Admins from the root domain *never* log into workstations or servers in lower-tier child domains, preventing credential theft that leads to root domain compromise.

## 6. Chaining Opportunities

- **Golden Ticket with SID History:** Compromise Child Domain Admin -> Extract KRBTGT hash -> Forge Golden Ticket adding the Enterprise Admin SID to `SIDHistory` -> Compromise Root Domain.
- **Foreign BloodHound Paths:** Trust enumeration reveals cross-domain group memberships. An attacker in Domain A might find they have DCSync rights over Domain B via a nested group membership across an external trust.
- **Cross-Forest Kerberoasting:** If a Forest Trust exists, an attacker can use `GetUserSPNs.py` targeting the remote Domain Controller across the trust boundary to extract Kerberos tickets for services in the other forest.

## 7. Related Notes
- [[05 - Active Directory Architecture Overview]]
- [[09 - Identifying Domain Controllers and Global Catalogs]]
- [[26 - Golden Tickets and SID History Abuse]]
- [[13 - BloodHound and Active Directory Graph Analysis]]

## Real-World Attack Scenario
## Real-World Attack Scenario

While conducting a penetration test for a recently merged logistics company, I compromised a low-privileged user account in the `apac.logistics.local` child domain. The ultimate objective was to compromise the overarching parent domain, `global.logistics.local`, which housed the critical financial and administrative infrastructure. 

**Thought Process:**
Active Directory environments often utilize trusts to allow users in one domain to access resources in another. However, these trust relationships—especially two-way transitive trusts or poorly configured external trusts—can provide a pathway for lateral movement and privilege escalation across domain boundaries. My goal was to enumerate all domain trusts to identify a path from the child domain (`apac`) up to the parent domain (`global`), looking specifically for SID History vulnerabilities or overly permissive cross-domain group memberships.

**Execution:**
Operating from a compromised Windows 10 workstation within the `apac` domain, I needed to perform the enumeration stealthily. I used the native PowerShell Active Directory module (which was already installed for administrative purposes) to list all trusts for the current domain.
```powershell
Import-Module ActiveDirectory
Get-ADTrust -Filter *
```
The output confirmed a two-way transitive trust with `global.logistics.local` and an unexpected one-way outgoing trust to a seemingly legacy domain, `acquired-company.local`.

To gain deeper insight from my Linux attack machine, I used BloodHound's Python ingestor (`bloodhound-python`) to map the trust relationships and cross-domain group memberships visually, pointing it at the child DC.
```bash
bloodhound-python -u 'jdoe' -p 'Summer2025!' -ns 192.168.10.10 -d apac.logistics.local -c All
```
Upon importing the data into the BloodHound GUI, the attack graph revealed a critical misconfiguration: the `Domain Admins` group of the `apac.logistics.local` domain was nested inside the `Server Operators` group of the parent `global.logistics.local` domain.

**Outcome:**
By enumerating the AD trusts and mapping cross-domain group memberships, I discovered a direct exploitation path. Because the child domain admins were effectively server operators in the parent domain, compromising the child domain (which had weaker security controls) immediately allowed me to take over the parent domain. I elevated privileges to Domain Admin in `apac`, and then trivially used those credentials to compromise the primary `global` Domain Controller, entirely bypassing the parent domain's strict security perimeter.

