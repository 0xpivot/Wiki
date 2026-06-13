---
tags: [chaining, advanced, real-world, vapt]
difficulty: expert
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.12 Chain Phishing to Domain Admin"
---

# Advanced Chaining: Spear-Phishing to Domain Admin

## Introduction

In enterprise environments, the perimeter is often highly secured with Next-Generation Firewalls (NGFW), IDS/IPS, and WAFs. Therefore, the most reliable vector for initial access into a corporate network remains the human element: **Phishing**. 

However, modern endpoint defenses (EDR, XDR) and Active Directory security have matured significantly. An attacker cannot simply send an executable in an email and expect domain compromise. This document outlines an advanced, highly sophisticated kill-chain that chains highly targeted spear-phishing, EDR evasion, local privilege escalation, and Active Directory exploitation to achieve complete Domain Admin compromise.

This is the quintessential "Red Team" engagement scenario, mimicking Advanced Persistent Threat (APT) behavior.

---

## The Attack Kill-Chain Architecture

The following ASCII diagram illustrates the progression from external payload delivery to total domain dominance.

```text
+-----------------------+
|  Attacker Infrastructure|
| (Cobalt Strike / C2)  |
+-----------+-----------+
            | 1. Weaponized Payload Delivery (Spear-Phishing)
            |    (HTML Smuggling -> ISO -> LNK)
            v
+-----------------------+       2. User Clicks / Execution
|    Victim Endpoint    |  <------------------------------------+
|  (Windows 11 / EDR)   |                                       |
+-----------+-----------+                                       |
            | 3. EDR Bypass & Memory Injection                  |
            | (Direct Syscalls / Unhooking)                     |
            v                                                   |
+-----------------------+                                       |
|   C2 Beacon Running   |  ---- (HTTPS C2 Traffic) -------------+
|  (Standard User Ctx)  |
+-----------+-----------+
            | 4. Local Privilege Escalation (LPE)
            | (e.g., UAC Bypass, PrintNightmare)
            v
+-----------------------+
|   SYSTEM Privileges   |
|  (LSASS Dump / Hash)  |
+-----------+-----------+
            | 5. Internal AD Reconnaissance (BloodHound)
            | 6. Lateral Movement (Pass-the-Hash / WMI)
            v
+-----------------------+
|  Intermediate Server  | (e.g., File Server or Dev Box)
| (Contains DA Tokens)  |
+-----------+-----------+
            | 7. Token Impersonation / Kerberoasting
            v
+-----------------------+
|  Domain Controller    | (ntds.dit extraction / DCSync)
|  (Domain Admin)       |
+-----------------------+
  [ TOTAL AD COMPROMISE ]
```

---

## Phase 1: OSINT and Pretext Development

The success of a spear-phishing campaign relies entirely on the pretext. The attacker must craft a scenario that compels the user to bypass warnings and execute the payload.

### 1.1 Target Identification
Using tools like LinkedIn, Hunter.io, and corporate "About Us" pages, the attacker identifies a high-value target. Let's assume the target is the VP of Finance. 

### 1.2 Crafting the Pretext
The attacker registers a typosquatted domain (e.g., `target-finance-portal.com`). They craft an email appearing to come from the organization's external auditing firm, referencing a critical discrepancy in the Q3 tax filings. The email implies urgency and directs the VP to review an attached "Secure Document".

---

## Phase 2: Weaponization and Delivery

Due to modern email gateways blocking standard macro-enabled documents (VBA) and the implementation of Mark-of-the-Web (MotW), attackers utilize complex delivery mechanisms.

### 2.1 HTML Smuggling
The attacker uses HTML Smuggling to deliver the payload. The email contains a link to a seemingly benign HTML page. When the victim visits the page, obfuscated JavaScript dynamically generates an ISO file locally within the victim's browser and prompts a download. 
Because the file is generated entirely client-side, it bypasses network-based perimeter scanning.

### 2.2 ISO and LNK Weaponization
The downloaded ISO file contains a deceptive LNK (shortcut) file named `Q3_Tax_Audit_Report.pdf.lnk` and a hidden folder containing the malicious payload (a custom DLL or executable).

When the user double-clicks the ISO (which Windows natively mounts), and then clicks the LNK file, the LNK executes a native Windows binary (like `cmd.exe` or `rundll32.exe`) to execute the hidden payload. This bypasses MotW because files within a mounted ISO do not inherit the MotW attribute.

---

## Phase 3: Initial Access and EDR Evasion

The payload executed by the LNK file is a heavily obfuscated dropper designed to establish a Command and Control (C2) beacon (e.g., Cobalt Strike, Brute Ratel, or Havoc) while evading Endpoint Detection and Response (EDR) solutions like CrowdStrike or SentinelOne.

### 3.1 EDR Evasion Techniques
EDR solutions monitor API calls by injecting "hooks" into user-land DLLs (like `ntdll.dll`). To bypass this, the attacker's payload employs:
- **Direct System Calls (Syscalls):** Instead of calling `VirtualAllocEx` or `CreateRemoteThread` from the Windows API, the payload manually executes the assembly instructions for the kernel syscalls, bypassing the user-land hooks entirely.
- **API Unhooking:** The payload reads a clean version of `ntdll.dll` from disk and overwrites the hooked version in memory.
- **Process Injection:** The payload injects the C2 shellcode into a legitimate, running process (e.g., `explorer.exe` or `svchost.exe`) using techniques like Process Hollowing or Module Stomping.

### 3.2 Establishing C2
Once injected, the shellcode reaches out to the attacker's Team Server via encrypted HTTPS traffic, blending in with normal web browsing. The attacker now has a shell as the standard user (VP of Finance).

---

## Phase 4: Local Privilege Escalation (LPE)

To dump credentials or manipulate the system at a deep level, the attacker needs elevated privileges (`NT AUTHORITY\SYSTEM`).

### 4.1 Enumeration
The attacker runs automated enumeration scripts (like `Seatbelt` or `WinPEAS`) through the C2 framework, executing them entirely in memory to avoid dropping files to disk.

### 4.2 UAC Bypass and Exploitation
The attacker discovers the user is part of the local Administrators group but is running under a medium integrity context due to User Account Control (UAC). The attacker utilizes a UAC bypass technique (e.g., exploiting COM interfaces or auto-elevating binaries like `fodhelper.exe`) to spawn a high-integrity beacon.

Alternatively, if the user is unprivileged, the attacker might exploit a local service misconfiguration (Unquoted Service Path) or a known vulnerability (e.g., PrintNightmare / CVE-2021-1675) to execute code as SYSTEM.

---

## Phase 5: Internal Recon and Lateral Movement

With SYSTEM access on the endpoint, the attacker shifts focus to the Active Directory network.

### 5.1 Credential Dumping
The attacker dumps the LSASS (Local Security Authority Subsystem Service) memory process.
- **Evasion:** To avoid EDR alerts on LSASS access, the attacker might use a custom tool that utilizes a vulnerable, signed driver (Bring Your Own Vulnerable Driver - BYOVD) to read kernel memory, or use `MiniDumpWriteDump` with specific access flags.
- **Result:** The attacker extracts the NTLM hash of the VP of Finance.

### 5.2 Active Directory Reconnaissance
The attacker maps the AD environment using BloodHound. To stay stealthy, they execute the ingestor (`SharpHound.exe`) in memory and utilize LDAP queries instead of noisy remote API calls.

```powershell
# Executing SharpHound in memory via C2
execute-assembly /path/to/SharpHound.exe -c All -d target.local
```

The resulting BloodHound graph reveals a path to Domain Admin:
1. The VP of Finance has local admin rights on a secondary File Server (`FILE-SRV-02`).
2. A Domain Admin recently logged into `FILE-SRV-02`, meaning their credentials/tokens are likely cached in memory.

### 5.3 Lateral Movement
The attacker uses "Pass-the-Hash" (PtH) to move laterally to the File Server without needing the plaintext password.

```bash
# Using impacket or C2 built-in lateral movement
jump psexec FILE-SRV-02 target\vp_finance <NTLM_HASH>
```
The attacker creates a new beacon on `FILE-SRV-02`.

---

## Phase 6: Domain Privilege Escalation

The attacker is now on a server where a Domain Admin (`DA_AdminUser`) has an active or disconnected session.

### 6.1 Token Impersonation
Using the C2 framework (often utilizing built-in capabilities derived from Mimikatz or `incognito`), the attacker steals the access token of the Domain Admin process.

```bash
# Cobalt Strike command to steal token
steal_token <PID_OF_DA_PROCESS>
```

With the DA token impersonated, the attacker's beacon now operates with Domain Admin privileges.

### 6.2 DCSync and Persistence (Golden Ticket)
To cement their control and ensure access even if the current session is terminated, the attacker performs a **DCSync** attack. This simulates the behavior of a legitimate Domain Controller to request password data via the Directory Replication Service (DRS) Remote Protocol.

```bash
# Dumping the KRBTGT hash
mimikatz @lsadump::dcsync /domain:target.local /user:krbtgt
```

By obtaining the `krbtgt` account's NTLM hash, the attacker can forge a **Golden Ticket**. A Golden Ticket is an offline-forged Kerberos Ticket Granting Ticket (TGT) that grants persistent, undetectable, full administrative access to the entire domain, valid for up to 10 years.

---

## Impact and Business Risk

The impact of a Domain Admin compromise is absolute. 
- The attacker owns the entire corporate network.
- They can deploy enterprise-wide ransomware via Group Policy Objects (GPOs).
- They can access any file share, database, or email inbox.
- They can disable security products (EDR/Antivirus) across all endpoints globally.

---

## Mitigation and Defense in Depth

Defending against this advanced chain requires a robust, multi-layered approach:

1. **Anti-Phishing and Endpoint:**
   - Implement strong email filtering and sandbox analysis.
   - Educate users on the risks of ISO/LNK files and HTML Smuggling.
   - Configure Windows to block the mounting of ISO files from the internet, or enforce strict MotW policies.
   - Deploy advanced EDR configured in aggressive blocking mode, utilizing heuristics and behavioral analysis, not just signatures.

2. **Credential Hygiene and Local Security:**
   - Remove standard users from the Local Administrators group.
   - Implement LAPS (Local Administrator Password Solution) to randomize local admin passwords, preventing lateral movement via local account hashes.
   - Enable Windows Defender Credential Guard to protect LSASS from memory dumping.

3. **Active Directory Hardening:**
   - Enforce the **Tiered Administrative Model**. Domain Admins should *never* log into workstations or standard file servers. They should only log into dedicated, highly secure Privileged Access Workstations (PAWs) and Domain Controllers.
   - Monitor for anomalous LDAP queries and BloodHound activity.
   - Detect and alert on DCSync activities (Event ID 4662) originating from non-Domain Controller IP addresses.
   - Regularly rotate the `krbtgt` password (twice consecutively) to invalidate existing Golden Tickets.

---

## Chaining Opportunities

- **Cloud Pivot:** If the AD is federated with Azure AD (Microsoft Entra ID) using ADFS or seamless SSO, the attacker can use their Golden Ticket or DA privileges to extract the SAML signing certificates, forging a "Golden SAML" ticket to pivot from the on-premise network directly into the Cloud infrastructure.
- **Supply Chain Pivot:** The attacker can modify internal SCCM (System Center Configuration Manager) packages to deploy malware to every machine in the organization.

## Related Notes
- [[17 - Advanced Phishing and Payload Delivery]]
- [[24 - Active Directory Exploitation]]
- [[26 - Local Privilege Escalation (Windows)]]
- [[33 - Evasion Techniques and EDR Bypasses]]
