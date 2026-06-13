---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.05 Attacking RODC Read-Only Domain Controllers"
---

# 78.05 - Attacking RODC (Read-Only Domain Controllers)

## 1. Deep Dive into Read-Only Domain Controllers (RODCs)

Read-Only Domain Controllers (RODCs) were introduced in Windows Server 2008 specifically to address physical security concerns in branch offices or perimeter networks (DMZs) where physical security cannot be guaranteed.

Unlike a standard, fully writeable Domain Controller (RWDC), an RODC holds a **read-only** replica of the Active Directory database (NTDS.DIT). It cannot originate changes to AD objects. More importantly, to limit the blast radius if an RODC is physically stolen or compromised, the RODC *does not cache user passwords by default*. It must forward authentication requests to a writeable DC across the WAN link.

However, caching no passwords defeats the purpose of local authentication if the WAN link goes down. Therefore, administrators configure a **Password Replication Policy (PRP)**, which dictates which specific accounts' credentials the RODC is allowed to cache locally. 

### 1.1 The Architecture of the RODC

1. **Filtered Attribute Set (FAS):** The RODC database lacks sensitive attributes by default (like LAPS passwords or BitLocker recovery keys).
2. **Krbtgt Account:** An RODC has its own unique Kerberos Ticket Granting Ticket account (e.g., `krbtgt_12345`). It does *not* possess the primary domain `krbtgt` password hash. This is critical: if an RODC is compromised, the attacker cannot forge standard Golden Tickets for the entire domain. They can only forge tickets signed by the RODC's specific krbtgt account.
3. **Local Administrator Role:** Unlike standard DCs, RODCs allow standard domain users to be designated as "Local Administrators" of the RODC server itself, without granting them Domain Admin privileges.

---

## 2. Attack Vectors and Exploitation

Compromising an RODC is structurally different from compromising an RWDC. If an attacker gains SYSTEM on an RODC, they do not automatically own the domain. The severity of the compromise depends entirely on the **Password Replication Policy (PRP)** and architectural misconfigurations.

### 2.1 Password Replication Policy (PRP) Abuse

The PRP consists of an **Allowed List** and a **Denied List**.
* **Allowed:** Users whose hashes can be cached.
* **Denied:** Users whose hashes are strictly forbidden from being cached (usually Domain Admins, Enterprise Admins, etc.). The Denied list overrides the Allowed list.

**The Attack:**
If an attacker compromises an RODC, they will extract the local NTDS.DIT. The database will only contain the password hashes of the users currently cached via the PRP.

```bash
# Dumping the RODC's local database via DCSync or NTDS extraction
secretsdump.py corp.local/rodc_admin@RODC-01 -just-dc-user target_user
```

**The Misconfiguration:**
Often, administrators mistakenly place highly privileged accounts (e.g., a custom `IT_Helpdesk_Admins` group that happens to have Domain Admin rights) into the Allowed list, or fail to explicitly place them in the Denied list. If a privileged user authenticates through the RODC, their hash is cached. An attacker extracting the RODC database will acquire this privileged hash, leading to total domain compromise.

### 2.2 The RODC Golden Ticket

Because the RODC has its own `krbtgt_XXXXX` account, an attacker who compromises the RODC can extract its specific krbtgt hash.

They can then forge a Golden Ticket. However, there is a massive restriction: **The forged ticket is only valid for users whose passwords are cached on the RODC.**

If the attacker attempts to forge a Golden Ticket for `Administrator` (who is on the Denied list), the target service will validate the ticket against the writeable DC, discover the RODC is not allowed to cache that user, and reject the ticket.

```bash
# Forging an RODC specific Golden Ticket using Mimikatz
mimikatz # kerberos::golden /domain:corp.local /sid:S-1-5-21-XXX-XXX-XXX /rc4:<RODC_KRBTGT_HASH> /user:Cached_User /id:500 /ptt
```

### 2.3 Local Administrator Pivot

A common attack path involves compromising the delegated Local Administrator of the RODC.
1. The attacker compromises a branch office user.
2. BloodHound reveals the user is in the `Branch_IT` group, which is delegated as the local administrator of the RODC.
3. The attacker moves laterally to the RODC via PSRemoting or WMI.
4. From the RODC, the attacker monitors network traffic (PCAP) or intercepts credentials of other users authenticating through the server, waiting for a higher-privileged user to cross the wire.

---

## 3. Advanced Scenario: The "Key List" Attack

What if an attacker wants to know exactly who is cached on the RODC before initiating a noisy extraction? They can query the `msDS-RevealedUsers` attribute on the RODC computer object. This attribute explicitly lists all accounts whose passwords currently reside in the RODC's local database.

```powershell
# Using PowerView to query cached users on an RODC
Get-DomainObject -Identity "RODC-01$" -Properties msDS-RevealedUsers
```

If the attacker finds a valuable target in this list, they proceed with NTDS extraction. If the list only contains low-value branch users, the attacker may deploy credential stealers or wait for a privileged authentication event.

---

## 4. Visualizing RODC Architecture and Attack Flow (ASCII Diagram)

```text
  [ Central Office - Tier 0 ]                  [ Branch Office - DMZ ]
  
  +-------------------------+                  +-------------------------+
  | Writeable DC (RWDC)     |                  | Read-Only DC (RODC)     |
  | Primary Krbtgt Hash     |  WAN Link (Replication) Local Krbtgt_123   |
  | ALL Passwords Stored    |<================>| Cached Passwords ONLY   |
  +-------------------------+                  +-------------------------+
            ^                                            ^    |
            | (Auth Request Forwarded if                 |    |
            |  not cached & allowed)                     |    |
            |                                            |    |
            |                                            v    v
            |                                  +-------------------------+
            |                                  | Attacker                |
            |                                  | 1. Compromises RODC     |
            |                                  | 2. Extracts Cached Hashes
            |                                  | 3. Forges RODC-Ticket   |
            |                                  +-------------------------+
            |                                            |
            v                                            v
     [ Access Denied ]                          [ Access Granted ]
  If attacker forges DA ticket                 If attacker forges ticket
  (Domain detects invalid cache)               for cached branch user
```

---

## 5. Defense, Mitigation, and Response

### 5.1 Securing the Password Replication Policy (PRP)

The absolute most critical defense for an RODC is a strictly maintained PRP.
* **Denied List:** Ensure that all privileged groups (Domain Admins, Enterprise Admins, Schema Admins, Server Operators, Backup Operators, Account Operators, Print Operators) are explicitly in the Denied list.
* **Allowed List:** Only allow specific, necessary users (e.g., local branch employees) to be cached. Never use generic groups like `Domain Users`.

### 5.2 Responding to an RODC Compromise

If an RODC is compromised, standard incident response protocols must be modified:
1. **Identify the Blast Radius:** Query the compromised RODC to see exactly which passwords were cached at the time of compromise.
2. **Reset Cached Accounts:** Every account that was cached on the RODC must have its password reset immediately.
3. **Reset the RODC Krbtgt:** The specific `krbtgt_XXXXX` account for that RODC must be reset twice (to clear history), just like a standard krbtgt during a golden ticket response.
4. **Delete and Rebuild:** Destroy the RODC computer object in Active Directory to sever its replication ties, and rebuild the server from scratch.

### 5.3 Detection Mechanisms

* **Event ID 4624 / 4625:** Monitor for anomalous logins originating from the RODC itself to other critical infrastructure.
* **Event ID 4742 (A computer account was changed):** Monitor changes to the `msDS-NeverRevealGroup` (Denied List) or `msDS-RevealOnDemandGroup` (Allowed List) attributes. Attackers who gain rights might attempt to modify the PRP to allow caching of higher-privileged users.

---

## 6. The False Sense of Security

Many organizations treat RODCs as "set and forget" appliances that require less monitoring because they are "read-only." This is a fatal flaw. While an RODC prevents immediate direct AD modification, it is still an authentication broker. If an attacker uses an RODC to capture the hash of a Backup Operator who logged in to perform maintenance, the read-only boundary is shattered, and the attacker will pivot to the main network with elevated privileges.

---

## Chaining Opportunities
* **DCSync and Local Extraction:** Extracting the limited NTDS.DIT from the RODC. [[05 - DCSync and LSA Extraction]]
* **Golden Tickets:** Forging scoped Golden Tickets using the RODC's secondary krbtgt account. [[04 - Kerberos Golden and Silver Tickets]]
* **Lateral Movement:** Pivoting from the compromised RODC into the internal network utilizing cached credentials. [[08 - Intra-Forest Privilege Escalation]]

## Related Notes
* [[01 - Active Directory Architecture and NTDS.DIT]]
* [[09 - Kerberos Delegation Abuse]]
* [[03 - Kerberoasting and SPN Exploitation]]

---
*End of Document*
