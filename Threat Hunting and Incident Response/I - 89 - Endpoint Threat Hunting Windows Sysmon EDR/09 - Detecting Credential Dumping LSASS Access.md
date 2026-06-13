---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.09 Detecting Credential Dumping LSASS Access"
---

# 89.09 Detecting Credential Dumping LSASS Access

## Introduction to LSASS and Credential Dumping

The Local Security Authority Subsystem Service (`lsass.exe`) is an absolutely critical Windows process responsible for enforcing the security policy on the local system. It is the gatekeeper of authentication. LSASS verifies users logging on to a Windows computer or server, handles password changes, and generates access tokens that dictate user privileges across the OS.

Crucially, to facilitate Single Sign-On (SSO) and seamless network authentication across a domain environment, LSASS stores active user credentials dynamically in memory. Depending on the system configuration, the Windows version, and legacy protocols, this memory space can contain:
*   Plaintext passwords (historically via WDigest, though mostly mitigated now).
*   NT Hashes (used for NTLM authentication).
*   Kerberos Tickets (TGTs and TGSs used for Kerberos authentication).
*   DPAPI master keys (used to decrypt secrets stored by browsers and applications).

**Credential Dumping** is the technique where adversaries attempt to aggressively access and extract these sensitive artifacts from the protected memory space of the `lsass.exe` process. Once extracted, attackers leverage these credentials for Pass-the-Hash (PtH), Pass-the-Ticket (PtT), Golden/Silver Ticket attacks, or offline password cracking, enabling rapid lateral movement and domain escalation.

## The Mechanics of LSASS Memory Access

Because `lsass.exe` contains the keys to the kingdom, it is heavily protected. To read the memory of `lsass.exe`, an attacker's process must obtain a handle to the LSASS process with very specific access rights. This action fundamentally requires the attacker to have already achieved local Administrator or `NT AUTHORITY\SYSTEM` privileges, specifically requiring the `SeDebugPrivilege`.

### Standard OS APIs Used for Memory Dumping
Adversaries typically use a sequence of standard Windows API calls to extract the memory:

1.  **`OpenProcess()`:** The attacker's tool calls this Win32 API function to request a handle to the target `lsass.exe` process. The critical parameter here is the `dwDesiredAccess` flag. To successfully dump memory, the tool typically requests `PROCESS_VM_READ` (0x0010) and `PROCESS_QUERY_INFORMATION` (0x0400). Aggressive tools like Mimikatz often request `PROCESS_ALL_ACCESS` (0x1FFFFF), which is highly anomalous and easily flagged by EDRs.
2.  **`ReadProcessMemory()`:** Once a valid handle is obtained, this API is used to read the raw bytes from LSASS's virtual address space, copying them into the attacker's own process memory for parsing.
3.  **`MiniDumpWriteDump()`:** This is a highly abused, legitimate function exported by `dbghelp.dll` and `comsvcs.dll`. It is designed to create memory dumps of crashing processes for debugging purposes. Attackers leverage this API to dump the entirety of LSASS memory to a `.dmp` file on disk, which they then exfiltrate for safe, offline analysis.

### ASCII Diagram: The LSASS Memory Dumping Process

```text
+-----------------------+                         +-----------------------------------+
| Attacker Process      | 1. OpenProcess()        | Windows OS Kernel                 |
| (e.g., mimikatz.exe,  |------------------------>|                                   |
|  procdump.exe,        | Request Handle with     | 1. Checks Privileges (SeDebugPriv)|
|  taskmgr.exe,         | PROCESS_VM_READ and     | 2. Checks PPL Status              |
|  Custom C# Loader)    | PROCESS_QUERY_INFO      | 3. Returns Process Handle (0x4A)  |
+-----------------------+                         +-----------------------------------+
           |                                                        |
           |                                                        |
           | 2. ReadProcessMemory() or MiniDumpWriteDump()          |
           | Using Authorized Handle 0x4A                           |
           |                                                        |
           v                                                        v
+-----------------------+                         +-----------------------------------+
| System Disk (Offline) | <---------------------- | target: lsass.exe (PID 652)       |
|                       |  3. Writes LSASS memory | Memory Space:                     |
| C:\Temp\lsass.dmp     |     contents to disk    | - NTLM Hashes                     |
|                       |     or parses in-memory | - Kerberos TGT/TGS                |
| (Offline parsing via  |     and prints to stdout| - WDigest Cleartext (if enabled)  |
| Mimikatz/Pypykatz)    |                         | - DPAPI Keys                      |
+-----------------------+                         +-----------------------------------+
```

## Hunting for LSASS Access with Sysmon and EDR

Detecting credential dumping relies on monitoring API calls targeting LSASS, analyzing the process arguments of known dumping utilities (LOLBins), and observing anomalous file creation events (specifically dump files).

### Key Sysmon Event IDs

*   **Event ID 10 (ProcessAccess):** This is the most vital event for LSASS monitoring. It logs when a process successfully opens a handle to another process.
    *   **TargetImage:** Will be `C:\Windows\system32\lsass.exe`.
    *   **SourceImage:** The process attempting the access (e.g., `mimikatz.exe`, `rundll32.exe`, `powershell.exe`).
    *   **GrantedAccess:** The specific access rights requested. Hunting focuses on masks associated with reading memory: `0x1010` (`PROCESS_VM_READ` | `PROCESS_QUERY_INFORMATION`), `0x1410`, `0x1438`, `0x143A`, or `0x1FFFFF` (All Access).
*   **Event ID 11 (FileCreate):** Hunting for the creation of `.dmp` files. LSASS dumps typically have a characteristic file size (usually between 30MB and 150MB, depending on the system load). The creation of large dump files by suspicious processes or in unusual locations (`%TEMP%`, `C:\Users\Public`) is a strong indicator.
*   **Event ID 1 (ProcessCreate):** Monitoring command lines for known credential dumping tools or specific Living-off-the-Land Binaries (LOLBins) used to proxy dump commands.

### Advanced Detection Strategies: KQL (Microsoft Sentinel)

```kusto
// 1. Detect Suspicious Process Access to LSASS (Sysmon Event ID 10)
// Looking for anomalous GrantedAccess rights targeting the LSASS process.
DeviceEvents
| where ActionType == "OpenProcess" or ActionType == "ProcessAccessed"
| where TargetProcessName =~ "lsass.exe"
// CRITICAL: Filter known legitimate system processes that must access LSASS.
// This list requires extensive baselining per environment.
| where InitiatingProcessFileName !in~ ("svchost.exe", "csrss.exe", "wininit.exe", "smss.exe", "services.exe", "msmpeng.exe", "taskmgr.exe")
// Look for specific access masks associated with reading or dumping memory
// 0x1FFFFF (All Access - Mimikatz default), 0x1010, 0x1410, 0x1438, 0x143A (Common Dump Access Masks)
| where AdditionalFields contains "0x1FFFFF" or AdditionalFields contains "0x1010" or AdditionalFields contains "0x1410"
| project TimeGenerated, DeviceName, InitiatingProcessFileName, InitiatingProcessCommandLine, TargetProcessName, AdditionalFields
| sort by TimeGenerated desc
```

```kusto
// 2. Detect comsvcs.dll LSASS Dump (Living off the Land Technique)
// Attackers frequently abuse the MiniDumpW function exported by comsvcs.dll to dump LSASS.
DeviceProcessEvents
| where FileName =~ "rundll32.exe"
| where ProcessCommandLine has_all ("comsvcs.dll", "MiniDump")
// Attackers often specify the PID of LSASS on the command line
| project TimeGenerated, DeviceName, InitiatingProcessFileName, ProcessCommandLine, AccountName
```

```kusto
// 3. Detect Procdump targeting LSASS
// Sysinternals Procdump is a legitimate tool frequently co-opted by attackers.
DeviceProcessEvents
| where FileName =~ "procdump.exe" or FileName =~ "procdump64.exe" or ProcessCommandLine contains "procdump"
| where ProcessCommandLine has_any ("-ma", "-mp") and ProcessCommandLine has "lsass"
| project TimeGenerated, DeviceName, InitiatingProcessFileName, ProcessCommandLine, AccountName
```

## Real-World Attack Scenario

### Dumping via Task Manager and Custom MiniDump (Evading EDR)
An attacker successfully compromised a server but realized that dropping standard tools like `mimikatz.exe` or `procdump.exe` directly onto the disk immediately triggered the EDR, terminating their session. To remain stealthy and achieve their objective, they opted for Living-off-the-Land techniques and offline extraction.

**Detailed Attack Flow:**

1.  **Bypass/Evasion:** The attacker avoided running known malware signatures and focused on native OS capabilities.
2.  **RDP Access:** Having previously acquired local admin credentials, they established an RDP session to the target server, granting them a GUI environment.
3.  **GUI Memory Dump (The 'Click' Method):** They simply opened Task Manager (`taskmgr.exe`), located `lsass.exe` in the Details tab, right-clicked, and selected "Create dump file". Task manager, being a trusted system process, was allowed by the EDR to open a handle to LSASS and call `MiniDumpWriteDump`.
4.  **Exfiltration:** The resulting file, `lsass.DMP`, was saved to the user's `%TEMP%` directory. The attacker compressed it using 7zip to reduce size and exfiltrated the ~50MB file via a covert HTTPS C2 channel or an external file-sharing site.
5.  **Offline Cracking:** On their own infrastructure (where no AV/EDR was present), the attacker ran Mimikatz against the offline dump file:
    `sekurlsa::minidump lsass.DMP`
    `sekurlsa::logonpasswords`
    They successfully extracted the plaintext password (or NTLM hash) of a Domain Administrator who had previously logged onto the compromised server, granting them keys to the entire domain.
6.  **Alternative LoL Method (Command Line):** In a subsequent phase on a machine where RDP was unavailable, they used the command line equivalent: `rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump 652 C:\temp\lsass.dmp full` (where 652 was the PID of LSASS).

## Advanced Evasion Techniques

*   **API Unhooking / Direct Syscalls:** Modern EDRs detect LSASS access by placing "hooks" (inline modifications) in user-mode API functions like `NtOpenProcess` within `ntdll.dll`. Attackers use tools like Dumpert or custom C# loaders to either remove these hooks dynamically ("unhooking") or execute Direct System Calls to the Windows kernel. This entirely bypasses the EDR's user-mode visibility, making the memory dump invisible to standard telemetry.
*   **Duplicating Existing Handles:** Instead of calling `OpenProcess` and generating a highly suspicious Event ID 10, advanced malware scans the system for existing, legitimate processes (like `svchost.exe` or `csrss.exe`) that already possess a valid handle to LSASS. The malware then duplicates this existing handle using the `DuplicateHandle()` API, bypassing the initial access checks and alerting mechanisms.
*   **SSP/AP Injection:** Instead of reading memory externally, an attacker can inject a custom Security Support Provider (SSP) or Authentication Package (AP) DLL directly into the LSASS process. This DLL acts as a keylogger for LSASS; it intercepts passwords in plaintext at the exact moment a user authenticates, saving them to a hidden file on disk or sending them directly over the network.
*   **In-Memory Loaders (Cobalt Strike `execute-assembly`):** Compiling custom, obfuscated variants of Mimikatz or using loaders to run C# dumping tools entirely in memory. This avoids writing signatures to disk, relying entirely on the evasion of memory scanning techniques.

## Mitigation and Hardening Strategies

*   **Windows Defender Credential Guard:** Enable Credential Guard via Group Policy. This is the most effective mitigation. It utilizes Virtualization-Based Security (VBS) to isolate the LSASS process in a separate, hardware-backed virtual container (a "trustlet"). Even if an attacker has `SYSTEM` privileges, they cannot read the memory of the isolated LSASS process, rendering Mimikatz largely ineffective.
*   **LSA Protection (RunAsPPL):** Configure LSASS to run as a Protected Process Light (PPL). When enabled (via registry: `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\RunAsPPL=1`), the Windows kernel restricts non-protected processes (even those running as `SYSTEM`) from obtaining handles to LSASS with `PROCESS_VM_READ` access. *(Note: Attackers can bypass PPL using "Bring Your Own Vulnerable Driver" (BYOVD) attacks to load kernel code that strips the PPL protection).*
*   **Disable WDigest Authentication:** Ensure WDigest authentication is explicitly disabled in the registry (`HKLM\System\CurrentControlSet\Control\SecurityProviders\WDigest\UseLogonCredential` set to `0`). This prevents LSASS from caching plaintext passwords in memory entirely, a historical vulnerability often abused.
*   **Attack Surface Reduction (ASR):** Enable the ASR rule "Block credential stealing from the Windows local security authority subsystem (lsass.exe)". This rule prevents many common dumping tools from opening handles to LSASS.

## Chaining Opportunities
- **Initial Access -> Privilege Escalation -> Credential Dumping:** Attackers must escalate to Admin or SYSTEM before attempting to dump LSASS. This is the standard attack progression.
- **Lateral Movement:** Extracted NTLM hashes are immediately chained into Pass-the-Hash (PtH) attacks using tools like Impacket's `psexec.py` or `wmiexec.py` to move laterally to other network segments or domain controllers without needing to crack the hash.
- **Defense Evasion:** LSASS dumping is frequently chained with API Unhooking or BYOVD (Bring Your Own Vulnerable Driver) techniques to selectively blind or disable EDR sensors prior to executing the noisy memory dump operation.

## Related Notes
- [[06 - Hunting for WMI Abuse and Persistence]]
- [[07 - Detecting Malicious Scheduled Tasks and Services]]
- [[08 - Hunting for Registry Modifications and Run Keys]]
- [[10 - Identifying Suspicious Parent-Child Process Trees]]
