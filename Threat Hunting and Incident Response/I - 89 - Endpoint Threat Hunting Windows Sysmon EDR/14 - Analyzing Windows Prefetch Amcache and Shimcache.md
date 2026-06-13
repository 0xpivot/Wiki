---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.14 Analyzing Windows Prefetch Amcache and Shimcache"
---

# 89.14 Analyzing Windows Prefetch Amcache and Shimcache

## Introduction to Application Execution Artifacts

When a threat hunter investigates a potentially compromised endpoint, one of the most critical questions to answer is: *"What programs executed on this machine, and when?"* Attackers often delete their tools, scripts, and payloads after achieving their objectives. However, the Windows operating system generates numerous forensic artifacts specifically designed to optimize performance or ensure application compatibility. These artifacts inadvertently record detailed evidence of execution, serving as a goldmine for forensic analysts and threat hunters.

The "Big Three" execution artifacts in Windows are **Prefetch**, **Amcache**, and **Shimcache** (AppCompatCache). Even if an attacker successfully deletes their malware (e.g., `mimikatz.exe`), traces of its execution, its location on disk, and its cryptographic hashes often remain preserved in these artifacts for weeks or months.

Understanding the nuances, limitations, and parsing methodologies for each of these artifacts is essential for reconstructing the timeline of an attack.

## 1. Windows Prefetch (.pf)

Prefetch was introduced in Windows XP to speed up the boot process and application launch times. When an application runs, Windows monitors the files and directories it accesses during the first 10 seconds of execution. It saves this information in a `.pf` file. The next time the application runs, Windows uses this `.pf` file to load the necessary resources into memory efficiently.

### Key Forensic Value
Prefetch files are stored in `C:\Windows\Prefetch\`. They provide definitive proof that an executable was run on the system.
- **Execution Times:** Contains the precise timestamp of the last execution. Windows 8+ stores up to the last 8 execution timestamps.
- **Run Count:** The total number of times the application has been executed.
- **Loaded Files:** A comprehensive list of files (DLLs, configuration files, scripts) accessed by the executable during its first 10 seconds.
- **Volume Information:** Details about the volume (e.g., serial number, creation time) from which the executable ran, useful for tracking execution from USB drives.

### Caveats and Constraints
- Windows 10/11 limits the Prefetch directory to 1024 files. Older files are deleted as new ones are created.
- The file naming convention is `[EXECUTABLE_NAME]-[HASH_OF_PATH].pf` (e.g., `CMD.EXE-087B4001.pf`). If an attacker renames `mimikatz.exe` to `svchost.exe` and runs it from `C:\Temp`, a new Prefetch file `SVCHOST.EXE-[HashOfTempPath].pf` is created, which stands out compared to the legitimate `SVCHOST.EXE-[HashOfSystem32Path].pf`.
- Prefetch is enabled by default on Windows workstations but is **disabled by default on Windows Servers**.

## 2. Amcache (Amcache.hve)

Amcache is a registry hive (`C:\Windows\AppCompat\Programs\Amcache.hve`) introduced in Windows 8, replacing the older RecentFileCache.bcf. It is part of the Application Experience and Compatibility feature. Its primary purpose is to store metadata about recently executed applications, installed programs, and device drivers to facilitate compatibility checks.

### Key Forensic Value
Amcache is highly prized for its depth of metadata and its retention of cryptographic hashes.
- **File Hashes:** Amcache often stores the SHA-1 hash of the executable. This is incredibly valuable because it allows threat hunters to definitively identify renamed malware or look up the hash on VirusTotal, long after the physical file is gone.
- **First Execution Time:** Records when the application was first run.
- **File Metadata:** Stores the File Description, Publisher, Version, and Compilation Time pulled from the executable's PE headers.
- **Installed Applications:** Keeps a historical record of installed applications, including uninstalled ones.

### Caveats and Constraints
- Amcache data is populated by a scheduled task (`Microsoft\Windows\Application Experience\ProgramDataUpdater`). Therefore, there might be a delay between execution and the artifact appearing in Amcache.
- It does not track every single execution like Prefetch, focusing more on the "first time" an application is seen or when compatibility checks run.

## 3. Shimcache (AppCompatCache)

The Shimcache, officially known as the Application Compatibility Cache, is a mechanism designed to identify application compatibility issues with the operating system. It tracks executable files and decides whether they require "shims" (compatibility fixes) to run correctly. 

### Key Forensic Value
Shimcache data is stored within the SYSTEM registry hive (`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment\AppCompatCache`).
- **File Path:** The full path of the executed (or interacted with) binary.
- **Last Modified Time:** The $Standard_Information Last Modified time of the file at the time it was cached. *Crucially, this is NOT the execution time.*
- **Execution Flag (Older Windows):** In older versions of Windows, an 'execution flag' explicitly denoted execution.
- **Broad Coverage:** Shimcache can contain thousands of entries, offering a very long historical tail compared to Prefetch.

### Caveats and Constraints
- **Execution Intent vs. Actual Execution:** Just because a file is in the Shimcache does not guarantee it was executed. Simply browsing to a folder containing an executable in Windows Explorer, or an AV scanning the file, can cause it to be added to the Shimcache. Threat hunters must correlate Shimcache entries with Prefetch or Event Logs to confirm execution.
- **Volatility:** Shimcache data is maintained in memory and only written to the SYSTEM registry hive during a clean shutdown or restart. If an attacker pulls the plug on the machine (hard crash), recent Shimcache entries are lost.

## ASCII Diagram: Execution Artifacts Lifecycle

The diagram below maps how these artifacts relate to the timeline of an attacker executing a malicious payload on disk.

```text
+-----------------------------------------------------------------------------------------+
|                           Application Execution Artifacts Timeline                      |
+-----------------------------------------------------------------------------------------+

  [Attacker Drops Payload]
  C:\Temp\evil.exe
         |
         | (1) Attacker executes C:\Temp\evil.exe
         v
  +-----------------------+      (2) Windows Kernel monitors first 10 seconds
  |    evil.exe runs      |--------------------------------------------------+
  +-----------------------+                                                  |
         |                                                                   v
         | (3) OS checks compatibility                            +-----------------------+
         v                                                        |    Prefetch (.pf)     |
  +-----------------------+                                       | EVIL.EXE-A1B2C3D4.pf  |
  | Application Compat.   |                                       | - Run Count: 1        |
  | Subsystem             |                                       | - Exec Time: 14:05:01 |
  +-----------------------+                                       | - Loaded: ntdll.dll.. |
         |                                                        +-----------------------+
         | (4) Cached in Memory
         v
  +-----------------------+      (5) Scheduled Task Updates     +-----------------------+
  |   Memory Shimcache    |------------------------------------>|     Amcache.hve       |
  | (Written to Registry  |                                     | - Path: C:\Temp\evil  |
  |  on system shutdown)  |                                     | - SHA1: 5E884898D...  |
  +-----------------------+                                     | - First Run: 14:05    |
                                                                +-----------------------+

  [Attacker Deletes Payload]
  del C:\Temp\evil.exe
         |
         v
  [Artifacts Remain!] <--- Threat Hunter parses .pf, Amcache, and Shimcache
                           to prove evil.exe existed, ran, and what its hash was.
```

## Real-World Attack Scenario

### The Incident
A company suspected that data exfiltration occurred over the weekend from a critical file server. EDR logs were largely purged by the attacker, and the AV showed no active alerts. The incident response team acquired forensic images of the server.

### The Investigation and Artifact Analysis
The analyst began by parsing the execution artifacts to rebuild the timeline of attacker activity. Because the system was a Windows Server, Prefetch was naturally disabled. The analyst relied heavily on Amcache and Shimcache.

1. **Shimcache Analysis:** The analyst parsed the SYSTEM registry hive using a tool like `AppCompatCacheParser`. Filtering for executions over the weekend, they identified a suspicious entry: `C:\Users\Public\Music\rar.exe`. 
   - *Discovery:* The last modified time matched the suspected window of intrusion. However, this only proved the file existed and was interacted with, not necessarily executed.

2. **Amcache Analysis:** To confirm execution and gather more details, the analyst parsed the `Amcache.hve` using `AmcacheParser`. They searched for the path `C:\Users\Public\Music\rar.exe`.
   - *Discovery:* The Amcache parser returned a hit. Crucially, it provided the SHA-1 hash of the binary and confirmed the "First Run" timestamp. 
   - *Hash Lookup:* The analyst checked the SHA-1 hash on VirusTotal. It was a known hash for a legitimate command-line version of WinRAR.

3. **Event Log Correlation:** Knowing the exact execution time from Amcache, the analyst pivoted to the surviving Windows Security Event Logs (Event ID 4688 - Process Creation).
   - *Discovery:* At the exact time specified in Amcache, Event ID 4688 showed `rar.exe` executing with the command line: `rar.exe a -r -hpfakeP@ssw0rd C:\Users\Public\Music\archive.rar C:\ConfidentialData\*`.

### The Hunt and Remediation
The combination of Shimcache and Amcache allowed the analyst to prove that the attacker dropped a legitimate WinRAR binary into a hidden directory, executed it to archive and password-protect sensitive data, and then deleted the `rar.exe` binary. The artifacts provided the path, the hash, and the execution timestamp, bridging the gap left by the deleted tools. The team subsequently found the `archive.rar` file staged for exfiltration and remediated the breach.

## Parsing Tools and Methodologies

Threat hunters and forensic analysts rely on specialized tools (often from the Eric Zimmerman Tools suite) to parse these complex binary files and registry hives into human-readable CSV formats.

- **Prefetch:** `PECmd.exe` parses `.pf` files, highlighting the execution count, timestamps, and the directories accessed.
- **Amcache:** `AmcacheParser.exe` extracts the registry hive data, outputting files that correlate application paths with their SHA-1 hashes and PE metadata.
- **Shimcache:** `AppCompatCacheParser.exe` pulls the cache from the SYSTEM hive. Analysts must export the SYSTEM hive and run the tool against it, sorting the output chronologically to spot outliers executing from `Temp`, `AppData`, or `Public` directories.

## Chaining Opportunities
- **Execution -> Defense Evasion:** Attackers frequently execute living-off-the-land binaries (LOLBins) to bypass defenses. Analyzing Prefetch and Amcache is critical for identifying exactly which LOLBins (e.g., `certutil.exe`, `bitsadmin.exe`) were used and when.
- **Execution -> Discovery/Collection:** Artifacts will show the execution of staging tools (like WinRAR or 7zip) or network scanners (like Advanced IP Scanner) that attackers drop on disk to map the network or bundle data.
- **Impact -> Cleanup:** Analyzing the absence or clearing of these artifacts (e.g., an attacker running `del C:\Windows\Prefetch\*.pf`) is a high-fidelity indicator of deliberate anti-forensics and malicious intent.

## Related Notes
- [[12 - Endpoint Detection and Response EDR Telemetry Analysis]]
- [[13 - Hunting for Fileless Malware and In-Memory Execution]]
- [[04 - Living Off The Land Binaries (LOLBins)]]
- [[09 - Windows Event Logs for Threat Hunting]]
- [[06 - Introduction to Digital Forensics and Incident Response DFIR]]
