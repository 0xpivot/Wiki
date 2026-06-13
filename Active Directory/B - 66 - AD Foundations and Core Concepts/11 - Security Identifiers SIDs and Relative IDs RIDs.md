---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.11 Security Identifiers SIDs and RIDs"
---

# Security Identifiers (SIDs) and Relative IDs (RIDs)

Security Identifiers (SIDs) are fundamental building blocks of authorization and identity in Microsoft Windows and Active Directory (AD) environments. Every user, group, computer, and built-in principal is assigned a unique SID. Understanding SIDs and their sub-component, the Relative Identifier (RID), is crucial for security assessments, as manipulating these can lead to persistent backdoors and privilege escalation.

## What is a Security Identifier (SID)?

A SID is a variable-length data structure that uniquely identifies a security principal or a security group. Whenever an object is created in Active Directory or a local SAM (Security Account Manager) database, Windows generates a SID for it.

### Anatomy of a SID

SIDs follow a specific string format: `S-R-I-S...`
*   `S`: Literal string 'S' indicating the string represents a SID.
*   `R`: Revision level. For Windows, this is always `1`.
*   `I`: Identifier Authority. A 48-bit value that identifies the authority that issued the SID (e.g., NT Authority is `5`).
*   `S...`: Sub-authorities. Variable-length values that uniquely identify the domain or local computer.
*   `RID`: Relative Identifier. The very last sub-authority in the SID, which uniquely identifies the specific object relative to the domain or local computer.

**Example SID:** `S-1-5-21-3623811015-3361044348-30300820-500`

Let's break down this example:
*   `S`: Security Identifier
*   `1`: Revision 1
*   `5`: NT Authority
*   `21`: Sub-authority (Indicates an NT domain or local computer)
*   `3623811015-3361044348-30300820`: The Domain Identifier. This is unique to the specific AD domain. All objects created in this domain will share this base SID.
*   `500`: The Relative ID (RID). In this case, `500` designates the built-in Administrator account.

## Well-Known SIDs and RIDs

Windows pre-defines several SIDs and RIDs that are consistent across all deployments. Attackers often target or impersonate these.

### Important Built-in RIDs (Domain/Local)
*   **`500`**: Administrator (Default Built-in)
*   **`501`**: Guest Account
*   **`502`**: KRBTGT (Key Distribution Center Service Account)
*   **`512`**: Domain Admins
*   **`513`**: Domain Users
*   **`514`**: Domain Guests
*   **`515`**: Domain Computers
*   **`516`**: Domain Controllers
*   **`519`**: Enterprise Admins

### Important Universal Well-Known SIDs
*   `S-1-1-0`: Everyone (Includes all users, even anonymous prior to Server 2003)
*   `S-1-5-7`: Anonymous Logon
*   `S-1-5-18`: Local System (NT AUTHORITY\SYSTEM)
*   `S-1-5-19`: NT Authority\Local Service
*   `S-1-5-20`: NT Authority\Network Service

## The RID Master (FSMO Role)

In a multi-DC Active Directory environment, it is critical that two Domain Controllers do not issue the same SID (and thus the same RID) to two different newly created objects. To prevent this, AD uses the **RID Master**, which is one of the Flexible Single Master Operations (FSMO) roles.

The RID Master is responsible for allocating pools of RIDs to all other Domain Controllers in the domain. 
*   By default, the RID Master gives out pools in chunks of 500 RIDs.
*   When a DC uses up its pool, it requests another 500 from the RID Master.
*   If the RID Master goes offline, DCs can only create objects until their current pool of 500 RIDs is depleted.

## ASCII Diagram: SID Construction & Object Creation

```text
+-------------------------------------------------------------+
|               ACTIVE DIRECTORY OBJECT CREATION              |
+-------------------------------------------------------------+
                            |
                            v
+-------------------------------------------------------------+
|                       DOMAIN CONTROLLER                     |
|  1. Admin requests new user creation (e.g., 'evil_user')    |
|  2. DC pulls next available RID from its RID Pool           |
+-------------------------------------------------------------+
          |                                 ^ (If pool is empty, 
          | Assigns RID                     | requests new pool)
          v                                 |
+---------------------+           +---------------------------+
| DOMAIN IDENTIFIER   |   +   +   |        RID MASTER         |
| S-1-5-21-XXX-YYY-ZZZ|       |   | (FSMO Role Holder)        |
+---------------------+       |   +---------------------------+
          |                   |
          +---------+---------+
                    |
                    v
+-------------------------------------------------------------+
|                    NEW USER OBJECT SID                      |
|          S-1-5-21-XXX-YYY-ZZZ-1104                          |
|                                                             |
| [ SID defines access tokens, ACLs, and privilege mapping ]  |
+-------------------------------------------------------------+
```

## Offensive Applications

### 1. Enumerating SIDs via Null Sessions / RPC
If a machine allows unauthenticated RPC access (or if you have a low-privilege user), you can enumerate the users on a machine or domain by iterating through RIDs starting from 500 and going upwards.

**Tool: Impacket's `lookupsid.py`**
```bash
# Enumerating domain users via an unauthenticated/authenticated session
impacket-lookupsid 'domain.local/username:password@10.0.0.10'
```
This tool automatically translates the base domain SID and loops through RIDs (500, 501, 502, 1000, 1001, etc.) mapping them to usernames.

### 2. RID Hijacking
RID Hijacking is a stealthy persistence technique where an attacker modifies the RID of a low-privileged account in the registry (on a local machine) or directly in AD (highly complex) to match the RID of a high-privileged account (like 500). 

When the system builds the access token upon logon, it reads the overridden RID, effectively granting the low-privileged account Domain Admin or Local Admin rights without adding the user to the actual group.
*   **Registry Path for Local RID Hijacking**: `HKLM\SAM\SAM\Domains\Account\Users\`

### 3. SID History Injection (Golden Ticket / Migrations)
The `sIDHistory` attribute exists to allow users to retain their access to resources when migrating from one domain to another. 
If an attacker compromises a domain, they can forge a Kerberos Golden Ticket and inject the SID of the `Enterprise Admins` group (from the parent domain) into the `sIDHistory` field.
When the user authenticates across the trust boundary, the target domain reads the `sIDHistory`, sees the Enterprise Admin SID, and grants unrestricted access.

**Tool: Mimikatz / Impacket `ticketer.py`**
```bash
# Creating a Golden ticket with sIDHistory injection
impacket-ticketer -nthash <krbtgt_hash> -domain-sid <child_sid> -domain <child_domain> -sid <parent_da_sid> Administrator
```

## Defensive Considerations & Detection

### Mitigations
1.  **Disable SMB Null Sessions**: Prevent unauthenticated RID walking by enforcing `RestrictAnonymous` in the registry and GPO.
2.  **Monitor sIDHistory Modifications**: Legitimate `sIDHistory` changes only happen during domain migrations using tools like ADMT. Any dynamic modification of this attribute outside a migration window is highly suspicious.
3.  **Monitor FSMO Role Uptime**: Ensure the RID Master is highly available, though an offline RID Master does not strictly denote an attack, sudden exhaustion of RID pools might indicate mass object creation (e.g., AD spamming).

### Detections
*   **Event ID 4769**: A Kerberos service ticket was requested. Check the PAC for anomalous `sIDHistory` SIDs.
*   **Event ID 4742**: A computer account was changed.
*   **Event ID 4720**: A user account was created. Rapid succession of this event can indicate automated RID consumption.
*   **Registry Monitoring**: Alert on modifications to `HKLM\SAM\SAM\Domains\Account\Users\*` to catch local RID hijacking.

---

## Real-World Attack Scenario

An attacker gains a foothold on a child domain controller within a large corporate forest. Their goal is to compromise the forest root, but they only have child domain credentials. They dump the `krbtgt` hash of the child domain and note the SID of the Enterprise Admins group in the parent domain. Using Mimikatz, the attacker forges a Golden Ticket (TGT) and leverages the `sIDHistory` attribute by injecting the parent domain's Enterprise Admins SID (`S-1-5-21-<Root-Domain-SID>-519`) into the ticket. When the attacker attempts to access the `C$` share on the root domain controller using this forged ticket, the target DC reads the `sIDHistory` field, believes the attacker is a legitimate Enterprise Admin, and grants full access, effectively yielding total control over the entire AD forest.

## Chaining Opportunities

*   **Enumeration to AS-REP Roasting**: Use `lookupsid.py` to enumerate valid usernames via RID cycling, then pass that wordlist to tools like `GetNPUsers.py` to hunt for accounts that have "Do not require Kerberos preauthentication" enabled. See [[16 - Kerberos Authentication and AS-REP Roasting]].
*   **Trust Exploitation**: SIDs are the primary mechanism for cross-forest privilege escalation. Mastering SID History mapping is essential for Forest Trust abuse.

## Related Notes
*   [[12 - Active Directory Schema and Attributes]]
*   [[13 - Local Administrator vs Domain Administrator]]
*   [[16 - Kerberos Authentication and AS-REP Roasting]]
*   [[21 - Domain Trust Attacks and SID Filtering]]
