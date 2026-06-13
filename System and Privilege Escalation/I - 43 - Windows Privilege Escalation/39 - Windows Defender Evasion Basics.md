---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.39 Defender Evasion"
---

# Windows Defender Evasion Basics

## Introduction
Microsoft Defender Antivirus (formerly Windows Defender) is the built-in anti-malware component of Microsoft Windows. Over the years, it has evolved from a basic signature-based scanner into a formidable Endpoint Protection Platform (EPP) integrating Next-Generation Antivirus (NGAV) capabilities, behavioral monitoring, cloud-delivered protection, and deep OS integration.

For a red teamer, evading Windows Defender is a mandatory skill. While zero-day evasion techniques are closely guarded, understanding the fundamental architecture and common evasion methodologies provides the necessary foundation for bypassing endpoint security during an engagement.

## How Windows Defender Operates
Defender relies on a multi-layered defense strategy:

1.  **Static Signature Scanning:** Traditional hash matching and byte-sequence scanning of files on disk.
2.  **Heuristics:** Analyzing file structure, imports, and metadata to identify suspicious characteristics.
3.  **Behavioral Monitoring:** Utilizing kernel-level callbacks (e.g., via `CbOb` - Callback Object) to monitor process creation, API calls, and memory allocation in real-time.
4.  **Cloud-Delivered Protection:** Uploading suspicious files or metadata to Microsoft's cloud for advanced machine learning analysis and detonating them in a sandbox.
5.  **AMSI (Anti-Malware Scan Interface):** Scanning in-memory scripts (PowerShell, VBScript) post-deobfuscation. (See [[37 - AMSI Bypass Techniques]]).
6.  **Attack Surface Reduction (ASR):** Rules designed to block specific malicious behaviors (e.g., blocking Office macros from creating child processes).

## ASCII Architecture Diagram

```text
+---------------------------------------------------------------+
|             Windows Defender Evasion Landscape                |
|                                                               |
|   +-------------------+                                       |
|   | Attacker Payload  |                                       |
|   +---------+---------+                                       |
|             |                                                 |
|             v                                                 |
|   [ EVASION LAYER 1: Disk / Static ]                          |
|   Obfuscation, Packing, Encryption                            |
|             |                                                 |
|             v                                                 |
|   +---------+---------+     [ Cloud ML / Sandbox ]            |
|   | MsMpEng.exe       | <-------+ Network Isolation /         |
|   | (Defender Engine) |           Block Telemetry             |
|   +---------+---------+                                       |
|             |                                                 |
|             v                                                 |
|   [ EVASION LAYER 2: Memory / Runtime ]                       |
|   Process Injection, Unhooking, Sleep Obfuscation             |
|             |                                                 |
|             v                                                 |
|   +---------+---------+                                       |
|   | Kernel / OS APIs  |                                       |
|   | (ntdll.dll, etc.) |                                       |
|   +-------------------+                                       |
|                                                               |
|   [ EVASION LAYER 3: Configuration ]                          |
|   Add Exclusions, Disable Real-Time Protection (Requires Admin|
+---------------------------------------------------------------+
```

## Evasion Methodologies

Evasion techniques are broadly categorized into static, dynamic (runtime), and configuration abuse.

### 1. Static Evasion (Bypassing Scans on Disk)
The goal is to prevent Defender from flagging the executable file before it even runs.

*   **Packing and Crypters:** Using tools to compress or encrypt the payload. The payload is only decrypted in memory upon execution. While naive packers are easily detected, custom or heavily modified packers remain effective.
*   **Obfuscation:** Modifying the source code (changing variable names, inserting junk code) or compiling it in ways that alter the final binary structure to break known byte signatures.
*   **Living Off The Land:** Avoiding dropping executables entirely by utilizing built-in tools. (See [[34 - LOLBins]]).
*   **Environmental Keying:** The payload checks its environment (e.g., hostname, domain, presence of specific files) and only decrypts the malicious code if it confirms it is on the target network, preventing detonation in Microsoft's cloud sandbox.

### 2. Dynamic Evasion (Bypassing Runtime Detection)
Once the code starts executing, it must evade behavioral monitoring and memory scanning.

*   **API Unhooking:** Modern AV/EDR injects DLLs into userland processes to "hook" crucial Windows APIs (like `VirtualAlloc` or `CreateRemoteThread`) to monitor their usage. Evasion involves mapping a clean copy of `ntdll.dll` from disk and overwriting the hooked functions in memory, restoring their original, unmonitored state.
*   **Direct System Calls (Syscalls):** Bypassing userland APIs entirely (which are hooked) by making direct system calls to the Windows kernel. Tools like `SysWhispers` dynamically generate the necessary assembly code to perform these direct calls.
*   **Process Injection/Hollowing:** Injecting malicious code into a legitimate, running process (e.g., `explorer.exe` or `svchost.exe`). This masks the malicious activity under the guise of a trusted process.
*   **Sleep Obfuscation:** Defender periodically scans process memory. Advanced malware uses techniques like `Ekko` or `Foliage` to encrypt its own memory space while sleeping and only decrypts it for brief execution windows, minimizing the time it is exposed in cleartext.

### 3. Configuration Abuse (Requires Administrative Privileges)
If an attacker has elevated privileges, they can interact with the Defender configuration to blind it.

*   **Adding Exclusions:** Using PowerShell or command-line utilities to add a folder, file, or process to Defender's exclusion list.
    ```powershell
    Add-MpPreference -ExclusionPath "C:\temp\"
    Add-MpPreference -ExclusionProcess "malware.exe"
    ```
*   **Disabling Real-Time Protection:** Turning off the core engine.
    ```powershell
    Set-MpPreference -DisableRealtimeMonitoring $true
    ```
*   **Disabling Cloud/Telemetry:** Preventing Defender from phoning home for advanced analysis.
*   **Removing Signatures:** Using `MpCmdRun.exe` to remove all intelligence updates, reverting Defender to a base, less capable state.

## Defensive Strategies & Mitigation

Defending against modern evasion requires deep visibility and strict configuration management.

1.  **Tamper Protection:** Microsoft provides "Tamper Protection," which locks down Defender's configuration. Even if an attacker gains Administrator privileges, they cannot disable Real-Time Protection or add exclusions via PowerShell if Tamper Protection is enabled (it must be disabled via Intune or physical interaction).
2.  **Attack Surface Reduction (ASR) Rules:** Implement strict ASR rules to block common infection vectors, such as blocking credential stealing from LSASS and blocking office applications from creating child processes.
3.  **Endpoint Detection and Response (EDR):** While Defender Antivirus is the base, Microsoft Defender for Endpoint (MDE) or other EDR solutions provide deeper behavioral analysis, anomaly detection, and cross-machine correlation that static AV engines miss.
4.  **Monitor Configuration Changes:** Alert heavily on Event ID 5007 (Defender configuration changed), particularly focusing on added exclusions or disabled features.
5.  **Network Telemetry:** Monitor network traffic to detect Command and Control (C2) communications, even if the endpoint agent is blinded.

## Chaining Opportunities
- Bypassing Defender is a prerequisite for dropping credential dumping tools required for [[33 - NTDS.dit Extraction]].
- Often used in conjunction with [[37 - AMSI Bypass Techniques]] to ensure both disk and memory defenses are neutralized.
- Administrative configuration abuse relies on initial privilege escalation techniques detailed in [[10 - Windows Privilege Escalation Basics]].

## Related Notes
- [[37 - AMSI Bypass Techniques]]
- [[38 - Event Log Clearing and Evasion]]
- [[35 - AppLocker and WDAC Bypass]]
- [[34 - LOLBins]]
