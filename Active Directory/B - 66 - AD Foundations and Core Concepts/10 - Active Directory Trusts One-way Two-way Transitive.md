---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.10 Active Directory Trusts"
---

# Active Directory Trusts: One-way, Two-way, and Transitive

## 1. Introduction to Trust Boundaries

In Active Directory, a **Domain** acts as an administrative boundary, but a **Forest** acts as the ultimate security boundary. 
However, large organizations often consist of multiple domains, or even multiple forests, which emerge through acquisitions, geographic separation, or intentional compartmentalization.

To allow users in Domain A to access resources located in Domain B, an **Active Directory Trust** must be established. A trust provides a secure mechanism for authentication traffic to pass between different domains or forests, effectively extending the authentication capabilities of one domain into another.

## 2. Core Concepts of Trusts

### 2.1 Trust Direction (Trusting vs. Trusted)
Trust direction is notoriously counter-intuitive. 
- **The Trusting Domain**: The domain where the *Resources* (files, servers) are located. It "trusts" the other domain to verify user identities.
- **The Trusted Domain**: The domain where the *Accounts* (users) are located. It is trusted to perform the authentication.

*Rule of thumb*: The "arrow of trust" points in the opposite direction of the "arrow of access." 
If Domain A trusts Domain B, users in B can access resources in A.

### 2.2 Transitivity
Transitivity dictates whether trusts can be chained together.
- **Transitive Trust**: If Domain A trusts Domain B, and Domain B trusts Domain C, then Domain A inherently trusts Domain C. Authentication flows transparently through the trust path.
- **Non-Transitive Trust**: The trust relationship is strictly bound to the two domains involved. If A trusts B, and B trusts C, A does *not* automatically trust C.

## 3. Types of AD Trusts

Active Directory supports several distinct types of trusts depending on the architecture and requirement:

1. **Parent-Child Trust**: Automatically created when a new child domain is added to an existing domain tree (e.g., `hq.domain.com` and `domain.com`). These are always Two-way and Transitive.
2. **Tree-Root Trust**: Automatically created when a new domain tree is added to an existing forest. Always Two-way and Transitive.
3. **Forest Trust**: Manually created to link two separate AD Forests. They can be one-way or two-way, but they are Transitive only across the domains within the two connected forests.
4. **External Trust**: Manually created to connect a domain in one forest to a specific domain in another forest. These are explicitly **Non-Transitive**.
5. **Shortcut Trust**: Manually created between two domains in the same forest to optimize authentication routing and bypass long trust paths up and down the domain tree.
6. **Realm Trust**: Used to establish a trust between an AD domain and a non-Windows Kerberos realm (like a Linux/UNIX Kerberos implementation).

## 4. Architecture Visualization

```text
    FOREST 1 (Corp)                             FOREST 2 (Acquired)
                                                     
    [ corp.local ] <======= FOREST TRUST =======> [ acquired.local ]
    (Tree Root)             (Two-way, Transitive)   (Tree Root)
         |                                               |
         | Parent-Child Trust                            |
         | (Two-way, Transitive)                         |
         v                                               v
  [ emea.corp.local ]                        [ sales.acquired.local ]
         |
         | External Trust (One-way, Non-Transitive)
         +----------------------------------------------> [ partner.com ]
                                                          (Trusted to auth
                                                           partner users)

Arrows of Access:
- emea.corp.local users can access corp.local
- corp.local users can access acquired.local
- partner.com users can access emea.corp.local
```

## 5. Trust Keys and Inter-Realm Authentication

When a trust is established, AD creates a **Trusted Domain Object (TDO)**. The two domains negotiate and securely store a shared secret known as the **Trust Key** (or Trust Password). This password is automatically rotated by the DCs every 30 days.

### 5.1 Inter-Realm Kerberos Flow
When a user from Domain A needs to access a resource in Domain B:
1. Client requests a Service Ticket for Domain B from Domain A's KDC.
2. Domain A's KDC cannot issue it. Instead, it issues an **Inter-Realm TGT** encrypted with the shared Trust Key.
3. The Client takes this Inter-Realm TGT and presents it to Domain B's KDC.
4. Domain B's KDC decrypts it using the Trust Key, validates the PAC, and issues the final Service Ticket.

## 6. SID History and SID Filtering

When organizations migrate users between domains, they use the `sIDHistory` attribute. This attribute stores the user's old SID from the previous domain so they do not lose access to their old resources while the migration is pending.

### 6.1 The Abuse of sIDHistory
If an attacker compromises a child domain, they can forge a Golden Ticket and inject the **Enterprise Admins** SID of the parent root domain into the `sIDHistory` of the ticket. Because the child and parent share a transitive trust, the parent domain will read the ticket, see the Enterprise Admins SID in the history, and grant the attacker full Forest compromise.

### 6.2 SID Filtering
To prevent this exact attack across different forests, Microsoft enforces **SID Filtering**. When an Inter-Realm TGT crosses an External or Forest trust boundary, the receiving KDC actively strips out any SIDs that do not natively belong to the trusting domain (especially highly privileged SIDs like Enterprise Admins). 
*Note: SID Filtering is disabled by default between parent-child domains within the same forest, which is why compromising a child domain inherently means compromising the entire forest.*

## 7. Offensive Perspective: Trust Enumeration

Attackers rely on mapping out trusts to identify paths from low-privilege domains into high-value targets (like the corporate root domain).

- **Native Tools**: `nltest /domain_trusts`
- **PowerView**: 
  ```powershell
  Get-DomainTrust
  Get-DomainTrustMapping # Maps the entire forest trust structure
  ```
- **BloodHound**: BloodHound visualizes these trusts explicitly, making it easy to see if a compromised user in an acquired domain has a trust path into the main corporate network.

## 8. Offensive Perspective: Abusing Trusts

### 8.1 Forging Inter-Realm TGTs
If an attacker compromises a Domain Controller in a trusting domain, they can dump the trust keys (using Mimikatz `lsadump::trust`). With the trust key, the attacker can use tools like Rubeus or Impacket to forge an Inter-Realm TGT. This allows them to seamlessly pivot into the trusted domain without triggering standard authentication alerts.

### 8.2 The "ExtraSids" Attack (Child to Forest Root)
As mentioned, the forest is the security boundary. If you compromise a child domain (e.g., `emea.corp.local`):
1. Dump the `krbtgt` hash of the child domain.
2. Get the SID of the child domain.
3. Get the SID of the Enterprise Admins group in the parent domain (`corp.local`).
4. Forge a Golden Ticket using the child's `krbtgt`, inserting the parent Enterprise Admin SID into the `sIDHistory` (often called the `ExtraSids` attack).
5. Pass the ticket and execute `dcsync` against the parent domain controller.

## 9. Remediation and Hardening

- **Enforce the Forest Boundary**: Do not treat domains as strict security boundaries. Assume that if a child domain is compromised, the forest root is compromised. 
- **Enable SID Filtering**: Where possible, manually enable SID filtering on inter-forest trusts to strip out forged privileged SIDs.
- **Selective Authentication**: Instead of allowing Forest-wide authentication, enable Selective Authentication on External or Forest trusts. This explicitly requires users from the trusted domain to be granted the `Allowed to Authenticate` permission on specific resources in the trusting domain.
- **Monitor Trust Additions**: Alert on Event ID **4706** (A new trust was created) and **4716** (Trusted domain information modified).

## Real-World Attack Scenario

**The Context:** An attacker has compromised the `dev.corp.local` domain, a child domain within the `corp.local` forest. They have successfully extracted the `krbtgt` password hash for the child domain. Their ultimate objective is to access sensitive financial documents stored on a highly restricted server in the forest root domain (`corp.local`).

**The Thought Process:** Because the child and parent domains exist in the same forest, they share a two-way transitive trust. Furthermore, SID Filtering is disabled by default for intra-forest trusts. The attacker knows that if they forge a Golden Ticket using the child domain's `krbtgt` key, they can inject the Security Identifier (SID) of the parent domain's `Enterprise Admins` group into the `sIDHistory` attribute of the ticket. When the parent domain reads this ticket, it will honor the `sIDHistory` and grant administrative access.

**The Execution:**
1. **Information Gathering:** The attacker queries the active directory to find the SID of the child domain and the SID of the `Enterprise Admins` group in the root domain.
   *Child SID: `S-1-5-21-11111-22222-33333`*
   *Enterprise Admin SID: `S-1-5-21-99999-88888-77777-519`*
2. **Ticket Forgery:** Using `Mimikatz` on the compromised child Domain Controller, the attacker crafts the Inter-Realm Golden Ticket. Crucially, they use the `/sids` flag to inject the `Enterprise Admins` SID.
   `mimikatz # kerberos::golden /user:Administrator /domain:dev.corp.local /sid:S-1-5-21-11111-22222-33333 /sids:S-1-5-21-99999-88888-77777-519 /krbtgt:<child_krbtgt_hash> /ptt`
3. **Cross-Domain Execution:** The forged ticket is automatically injected into the attacker's current session. The attacker then attempts to list the contents of the `C$` share on the primary Domain Controller of the root domain.
   `dir \\DC01.corp.local\C$`

**The Outcome:** The root Domain Controller (`DC01`) receives the Kerberos ticket, validates its cryptographic signature (since it trusts the child domain), and processes the `sIDHistory`. Believing the user is an Enterprise Admin, it grants full access. The attacker has successfully escalated from a compromised child domain to total forest takeover in seconds.

## 10. Chaining Opportunities

- **DCSync -> Child-to-Parent Escalation**: Execute DCSync in a compromised child domain to extract the `krbtgt` hash, then chain it with an `ExtraSids` Golden Ticket attack to escalate to Enterprise Admin and take over the forest root.
- **BloodHound -> Trust Hopping**: Use BloodHound to discover a misconfigured bidirectional Forest Trust, then utilize Rubeus to forge Inter-Realm tickets to pivot laterally into an entirely separate organization.

## 11. Related Notes

- [[08 - NTLM vs Kerberos Authentication Basics]]
- [[07 - Access Control Lists ACLs and Access Control Entries ACEs]]
- [[01 - Active Directory Structure and Components]]
