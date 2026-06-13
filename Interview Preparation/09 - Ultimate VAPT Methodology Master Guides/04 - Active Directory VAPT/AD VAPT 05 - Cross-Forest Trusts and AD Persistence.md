---
tags: [vapt, methodology, active-directory, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - AD"
topic: "Master Guide - AD VAPT 05"
---

# AD VAPT 05 - Cross-Forest Trusts and AD Persistence

## Introduction
The final phase of an advanced Active Directory VAPT engagement is demonstrating impact beyond a single domain and proving the ability to maintain long-term, stealthy access. Enterprise networks rarely consist of a single domain; they are composed of multiple domains linked by Trusts forming Trees and Forests. Furthermore, once an attacker achieves Domain Admin, they will deploy persistence mechanisms to survive password resets, server reboots, and incident response remediation efforts.

## Interview Strategy: Architectural Attacks & AP T-Level Persistence
Interviewers for senior red team roles want to see if you understand multi-domain architecture and Advanced Persistent Threat (APT) survival tactics.

**The Expert's Pitch:**
> *"Achieving Domain Admin in a child domain is just a stepping stone. My next phase is analyzing Trust Relationships. If there is a bidirectional transitive trust between a child and a root domain, I will extract the trust key. Using this, I can forge an Inter-Realm Golden Ticket, injecting the Enterprise Admins SID into the SID History attribute. This allows me to pass the ticket to the parent forest and execute DCSync at the Root level.
> For persistence, I avoid noisy techniques like creating new admin users. Instead, I utilize cryptographic persistence via Golden and Silver tickets, manipulate the AdminSDHolder container to ensure my ACL backdoors are continually reapplied by the SDProp process, and modify the DSRM (Directory Services Restore Mode) password to allow deep, stealthy domain controller access even if all other credentials are rotated."*

---

## Phase 1: Cross-Domain and Cross-Forest Trust Attacks

A Trust allows users in Domain A to access resources in Domain B. 

### 1. Understanding Trust Types
*   **Parent-Child (Intra-Forest):** Default two-way, transitive trust. Exploitable via SID History.
*   **External Trust:** Usually one-way, non-transitive, between different forests.
*   **Forest Trust:** Transitive between two entire forests. Subject to SID Filtering.

### 2. The Inter-Realm TGT Attack (Child to Forest Root)
If an attacker compromises a child domain (e.g., `dev.target.local`) and wants to compromise the parent root domain (`target.local`), they can abuse the trust relationship. 
The vulnerability lies in **SID History**. When a user migrates between domains, their old SID is kept in the SID History attribute so they don't lose access to old files. 

**The Attack:**
1. Compromise the Child Domain (Get DA).
2. Extract the `krbtgt` hash of the Child Domain OR the Trust Key (the password connecting the two domains).
3. Forge a Golden Ticket. Inside this ticket, set the `sIDHistory` attribute to the SID of the `Enterprise Admins` group of the Parent Domain.
4. Present this ticket to the Parent Domain Controller. The Parent DC trusts the Child DC, reads the SID History, and grants Enterprise Admin rights.

**Execution (Mimikatz):**
```cmd
# 1. Get the SID of the Child Domain and the Parent Domain Enterprise Admins group
# 2. Get the krbtgt hash of the Child Domain
# 3. Forge the ticket
mimikatz.exe "kerberos::golden /user:Administrator /domain:dev.target.local /sid:<Child_SID> /sids:<Parent_SID>-519 /krbtgt:<Child_krbtgt_hash> /ptt" "exit"

# You now have Enterprise Admin rights over the parent forest.
dir \\parent-dc.target.local\C$
```

---

## Phase 2: Advanced Active Directory Persistence

Once control is established, Red Teamers install backdoors. 

### 1. Golden Ticket (Cryptographic Persistence)
By extracting the `krbtgt` hash via DCSync (See Guide 04), the attacker can forge their own Ticket Granting Tickets (TGTs). 
*   **Advantage:** As long as the `krbtgt` password isn't changed (twice), the attacker can generate valid TGTs for any user (even non-existent ones) for up to 10 years.
*   **Execution:**
```cmd
mimikatz.exe "kerberos::golden /domain:targetdomain.local /sid:<Domain_SID> /user:FakeAdmin /krbtgt:<krbtgt_hash> /id:500 /ptt"
```

### 2. Silver Ticket
Forging a Service Ticket (TGS) instead of a TGT. Requires the password hash of a specific machine or service account.
*   **Advantage:** Does not communicate with the DC. Purely localized to the target server. Extremely stealthy.

### 3. DSRM Password Modification
Every Domain Controller has a local Administrator account used for Directory Services Restore Mode (DSRM). By default, you cannot log in with it over the network. 
*   **The Attack:** Change the DSRM password to a known value, and modify a registry key to allow network logon using the DSRM account.
*   **Execution:**
```powershell
# On the DC, set network logon behavior for DSRM
New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -Name "DsrmAdminLogonBehavior" -Value 2 -PropertyType DWORD

# Change the password using ntdsutil
ntdsutil "set dsrm password" "reset password on server null" "Password123!" q q
```
Now, you can PtH or log in directly to the DC using `Administrator` and the DSRM password.

### 4. AdminSDHolder Abuse
`AdminSDHolder` is a special AD container. A background process called `SDProp` runs every 60 minutes and copies the ACLs from the `AdminSDHolder` object and applies them to all protected groups (like Domain Admins, Enterprise Admins).
*   **The Attack:** Give a low-privileged attacker account `GenericAll` over the `AdminSDHolder` container. 
*   **Impact:** Even if the Blue Team removes the attacker from the `Domain Admins` group, `SDProp` will run within an hour and automatically re-grant the attacker full control over the `Domain Admins` group based on the backdoored AdminSDHolder ACL.

### 5. Skeleton Key
An in-memory backdoor injected into the LSASS process on a Domain Controller. 
*   **Impact:** It allows the attacker to log in as *any* user in the domain using a master password of their choosing, while still allowing the legitimate user's password to work.
*   **Execution:**
```cmd
mimikatz.exe "privilege::debug" "misc::skeleton"
```

---

## Custom ASCII Attack Diagram (Inter-Realm Trust Exploitation)

```text
  [Child Domain (dev.corp.local)]             [Parent Domain (corp.local)]
         SID: S-1-5-21-111...                        SID: S-1-5-21-222...
                 |                                          ^
                 | (1) DCSync for krbtgt hash               |
                 v                                          |
        [Attacker Machine]                                  |
                 |                                          |
                 | (2) Forge Golden Ticket                  |
                 |     User: Administrator                  |
                 |     SID History: S-1-5-21-222...-519     |
                 |     (Enterprise Admins)                  |
                 v                                          |
         [Forged TGT in Memory]                             |
                 |                                          |
                 | (3) Request Service Ticket (TGS)         |
                 +------------------------------------------+
                 |     Presenting forged TGT to Parent DC
                 v
     [Parent Domain Controller]
                 | (4) Trusts Child Domain.
                 |     Reads SID History.
                 v
   [Grants Enterprise Admin Access]
                 |
                 | (5) Attacker executes DCSync on Root Domain
                 v
       [TOTAL FOREST COMPROMISE]
```

---

## Real-World Attack Scenario

**The Setup:** During a red team engagement, the team compromised a subsidiary company's domain (`eu.global-corp.local`), achieving Domain Admin. The ultimate objective was the parent corporation's domain (`global-corp.local`).
**The Execution:**
1. The team verified a two-way transitive trust existed between `eu.global-corp.local` and `global-corp.local`.
2. Using Mimikatz on the compromised child DC, they extracted the `krbtgt` hash of the `eu` domain.
3. They enumerated the SID of the parent domain using PowerView.
4. They forged a Golden Ticket, injecting the `Enterprise Admins` SID (`-519`) of the parent domain into the `sIDHistory` attribute.
5. With the forged ticket in memory, they ran `secretsdump.py` against the parent domain's primary Domain Controller.
6. The parent DC accepted the ticket due to the trust and SID History, and returned the NT hash for the `krbtgt` account of the root forest.
7. To maintain persistence, the red team modified the `AdminSDHolder` ACL in the root domain, granting a standard user (`service_backup`) full control over the `Enterprise Admins` group.

## Chaining Opportunities
*   **DCSync to Golden Ticket to Cross-Forest:** Once DCSync is achieved in a child domain (Guide 04), you immediately move to Golden Ticket forging, leading directly to Cross-Forest compromise.
*   **LPE to Skeleton Key:** If an attacker achieves LPE on a Domain Controller (Guide 02), they can bypass dumping hashes entirely and simply inject a Skeleton Key for universal access.

## Related Notes
*   [[Master Guide - AD VAPT 01]] - Initial Breach and AD Enumeration Methodology
*   [[Master Guide - AD VAPT 04]] - Domain Privilege Escalation DCSync DCShadow
*   [[Advanced Threat Persistence Techniques]]
*   [[Active Directory Trust Architecture]]

---
**End of File**
