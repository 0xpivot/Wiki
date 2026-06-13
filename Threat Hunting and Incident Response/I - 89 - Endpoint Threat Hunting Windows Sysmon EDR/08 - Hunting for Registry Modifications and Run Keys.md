---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.08 Hunting for Registry Modifications and Run Keys"
---

# 89.08 Hunting for Registry Modifications and Run Keys

## Introduction to Windows Registry as an Attack Surface

The Windows Registry is a hierarchical database that stores low-level settings for the Windows operating system and for applications that opt to use the registry. It acts as the central nervous system of Windows, managing hardware configurations, user preferences, software execution paths, network configurations, and core security policies.

For threat actors, the Registry is a primary, high-value target. It serves multiple tactical objectives: establishing persistent footholds, storing malicious payloads directly within keys (enabling "fileless" malware), bypassing security controls, and modifying system configurations to weaken defenses (e.g., disabling Windows Defender or altering firewall rules). Because the registry is continually read and written to by millions of legitimate OS components and application processes per hour, hunting for malicious modifications is a classic "needle in a haystack" problem. Success requires understanding precise, high-risk registry locations—often referred to as "Autostart Extensibility Points" (ASEPs)—and establishing rigorous environmental baselines.

## Run Keys and Autostart Extensibility Points (ASEPs)

The most common and historically prevalent method for registry-based persistence is the abuse of "Run Keys." These are specific registry values that the operating system queries during the system startup sequence or during the user logon process to determine which applications should be automatically executed in the background.

### Common Registry Run Keys

**System-Wide Execution (Requires Administrator or SYSTEM privileges):**
Modifications to these keys affect all users on the system. Payloads configured here typically execute during the system boot sequence or when any user logs in, running with elevated privileges.
*   `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
*   `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce`
*   `HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run`
*   `HKLM\Software\Microsoft\Windows\CurrentVersion\RunServices`

**User-Specific Execution (Requires Standard User privileges):**
These keys execute only when the specific user whose registry hive is modified logs in. This is heavily abused by commodity malware, phishing payloads, and initial access brokers, as it does not require privilege escalation to establish persistence.
*   `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
*   `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce`
*   `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run`

### Beyond the Basic Run Keys: Advanced ASEPs

While standard `Run` keys are heavily monitored by AV and EDR solutions, sophisticated attackers often target more obscure, deeply integrated ASEPs to achieve stealthier, harder-to-detect persistence:

1.  **Image File Execution Options (IFEO) - Debugger Injection:** 
    Path: `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<process.exe>`
    Originally designed for developers to automatically attach debuggers to crashing applications. By setting a `Debugger` string value to point to a malicious binary, the attacker ensures that every time the target `process.exe` (e.g., `calc.exe`, `notepad.exe`, or `sethc.exe` for Sticky Keys abuse) is launched by the user or system, the malicious debugger runs *instead*. The malware can then optionally spawn the original process to hide its presence.

2.  **AppInit_DLLs (Broad DLL Injection):** 
    Path: `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs`
    Any DLL specified in this comma-separated list is loaded into the memory space of *every single process* that loads `User32.dll` (which is nearly every GUI application and many background processes). This provides incredibly broad persistence, massive code injection capabilities, and excellent opportunities for API hooking and credential harvesting. (Note: Microsoft requires these DLLs to be signed in modern Windows versions with Secure Boot enabled, but bypasses exist).

3.  **Winlogon Userinit / Shell Modification:** 
    Path: `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`
    During the logon sequence, `winlogon.exe` reads these keys to determine how to initialize the user environment.
    *   `Userinit`: Normally points to `C:\Windows\system32\userinit.exe`. Attackers append their payload: `userinit.exe, C:\Temp\backdoor.exe`.
    *   `Shell`: Normally points to `explorer.exe`. Attackers modify it to launch their shell alongside or instead of the standard desktop: `explorer.exe, C:\Temp\malware.exe`.

4.  **Component Object Model (COM) Hijacking:** 
    Path: `HKCU\Software\Classes\CLSID\{...}\InprocServer32`
    When a legitimate application attempts to load a specific COM object by its GUID (Class ID), the OS queries the registry to find the corresponding DLL. An attacker can create a fake entry in the `HKCU` hive (which takes precedence over `HKLM`) pointing to a malicious DLL. When the legitimate application requests the COM object, it unwittingly loads the attacker's code.

### ASCII Diagram: Registry Persistence Execution Flow

```text
+-------------------+       User Logon /       +-----------------------------+
| User Session      |       System Boot        | Windows Subsystem           |
| Authentication    | =======================> | (e.g., winlogon.exe,        |
| (Interactive/RDP) |                          |  explorer.exe)              |
+-------------------+                          +-------------+---------------+
                                                             |
                 +-------------------------------------------+
                 |
                 | Reads Autostart Extensibility Points (ASEPs)
                 v
+------------------------------------------------------------+
|  Registry Database Hives                                   |
|                                                            |
|  [Standard Persistence]                                    |
|  HKCU\Software\Microsoft\Windows\CurrentVersion\Run        |
|  "Updater" = "C:\Users\AppData\Roaming\malware.exe"        |
|                                                            |
|  [Advanced Persistence - Winlogon]                         |
|  HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon|
|  "Shell" = "explorer.exe, C:\Temp\backdoor.exe"            |
|                                                            |
|  [Advanced Persistence - IFEO Injection]                   |
|  HKLM\...\Image File Execution Options\notepad.exe         |
|  "Debugger" = "C:\Temp\malicious_debugger.exe"             |
+-----------------------------+------------------------------+
                              |
                              |  Executes defined payloads based on context
                              v
+-----------------------------+------------------------------+
| Memory / Process Execution                                 |
|                                                            |
| - malware.exe (Runs in Context: Standard User)             |
| - backdoor.exe (Runs in Context: Elevated System/Admin)    |
| - malicious_debugger.exe (Intercepts notepad.exe launch)   |
+------------------------------------------------------------+
```

## Hunting Registry Modifications with Sysmon

Sysmon provides granular, high-fidelity visibility into registry operations. However, due to the extreme volume of registry events generated by standard Windows operations, Sysmon must be carefully configured via XML to only monitor specific, high-risk registry paths. Monitoring everything will instantly overwhelm local storage and SIEM ingestion limits.

### Key Sysmon Event IDs for Registry Hunting

*   **Event ID 12 (RegistryEvent - Object create and delete):** Detects when new registry keys or values are created or deleted. Useful for detecting the initial staging of COM hijacking keys.
*   **Event ID 13 (RegistryEvent - Value Set):** Detects when the data within a registry value is modified. This is the primary and most critical event for hunting Run key abuse, IFEO modification, and Winlogon tampering.
*   **Event ID 14 (RegistryEvent - Key and Value Rename):** Detects renaming of registry objects, which can occasionally be indicative of defense evasion or specific malware families trying to hide their tracks.

### Advanced Detection Strategies: Splunk / KQL

```kusto
// 1. Detect Modifications to standard Run Keys (Sysmon Event ID 13)
// Focuses on executable files and script engines being added to startup.
DeviceRegistryEvents
| where ActionType == "RegistryValueSet"
| where RegistryKey has_any (
    @"Software\Microsoft\Windows\CurrentVersion\Run",
    @"Software\Microsoft\Windows\CurrentVersion\RunOnce"
)
// Look for common payload extensions and LOLBins
| where RegistryValueData has_any (".exe", ".ps1", ".bat", ".vbs", "cmd.exe", "powershell.exe", "rundll32.exe", "regsvr32.exe", "mshta.exe", "cscript.exe")
// CRITICAL: Filter out common, noisy legitimate updaters based on path and signer.
// This requires careful environmental baselining to avoid false positives.
| where not(RegistryValueData contains @"C:\Program Files" and InitiatingProcessFileName has_any ("msiexec.exe", "tiworker.exe", "chrome.exe"))
| project TimeGenerated, DeviceName, InitiatingProcessFileName, RegistryKey, RegistryValueName, RegistryValueData, AccountName
| sort by TimeGenerated desc
```

```kusto
// 2. Detect Image File Execution Options (IFEO) Debugger Injection
// This is an extremely high-fidelity alert. Legitimate use of this outside of developer workstations is rare.
DeviceRegistryEvents
| where ActionType == "RegistryValueSet"
| where RegistryKey contains @"\Image File Execution Options\"
| where RegistryValueName =~ "Debugger"
| project TimeGenerated, DeviceName, InitiatingProcessFileName, RegistryKey, RegistryValueData, AccountName
```

```kusto
// 3. Detect Suspicious Process Modifying the Registry via Command Line Tools
// Attackers often use native tools like reg.exe to make modifications, leaving a clear process execution trail.
DeviceProcessEvents
| where FileName =~ "reg.exe"
| where ProcessCommandLine has_any ("add", "delete")
// Target high-value ASEPs in the command line arguments
| where ProcessCommandLine has_any ("CurrentVersion\\Run", "CurrentVersion\\RunOnce", "Winlogon", "AppInit_DLLs")
| project TimeGenerated, DeviceName, InitiatingProcessFileName, ProcessCommandLine, AccountName
```

## Real-World Attack Scenario

### Fileless Malware Stored in the Registry (Kovter/Poweliks Methodology)
A sophisticated crimeware group, operating as an Initial Access Broker, utilized advanced "fileless" techniques to establish persistent access while completely evading traditional Antivirus file-scanning engines. The entire malicious payload was stored as a registry value, and only native Windows tools were used to execute it.

**Detailed Attack Flow:**

1.  **Initial Compromise:** A user was tricked into enabling macros on a malicious Word document. The VBA macro spawned `powershell.exe` in the background.
2.  **Registry Staging (The Payload):** The PowerShell script downloaded a secondary payload, created a massive, base64-encoded, encrypted blob of data, and wrote it to a custom, seemingly random registry key: `HKCU\Software\Classes\CLSID\{Random-GUID}\Data`. *Crucially, no binary executable file (.exe or .dll) was ever written to the physical disk.*
3.  **Persistence Mechanism (The Trigger):** To ensure the payload executed on reboot, the script added a value to the standard user Run key: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
4.  **The LOLBin Execution Chain:** The value placed in the Run key did not point to an executable. Instead, it used Living-off-the-Land Binaries (LOLBins) to read and execute the hidden registry payload. The registry Run entry looked similar to this deeply nested command:
    `mshta.exe "javascript:var sh=new ActiveXObject('WScript.Shell'); sh.Run('powershell -nop -w hidden -c \"IEX (Get-ItemProperty HKCU:\\Software\\Classes\\CLSID\\{Random-GUID}).Data\"',0);close();"`
5.  **Execution & Impact:** Upon system reboot, the Windows OS reads the Run key. It executes `mshta.exe` (a legitimate, Microsoft-signed binary used for HTML applications). `mshta.exe` executes the embedded JavaScript. The JavaScript launches `powershell.exe`. PowerShell reads the encrypted blob from the registry, decrypts it in memory, and executes the backdoor directly within the powershell process space. The malware is running, but no malicious file exists on the hard drive.

## Advanced Evasion Techniques

*   **Null Byte Injection:** Attackers have historically used null bytes (`\x00`) in registry key names. Many older native Windows tools (like standard `regedit.exe` or `reg.exe`) use null-terminated strings and will fail to display or interact with keys containing null bytes, effectively hiding them from manual inspection and amateur forensic tools. Modern EDRs generally parse these correctly.
*   **Registry Key Time Stomping:** Modifying the 'Last Write Time' of a registry key using low-level APIs to make it appear much older than it actually is. This allows the malicious key to blend in with original OS installation artifacts during a timeline analysis.
*   **Hiding via Permissions (DACL Manipulation):** An attacker might create a persistent registry key and then modify the Discretionary Access Control List (DACL) of that specific key. They can deny `READ` access to the `Administrators` group, the `SYSTEM` account, and standard security tools. This makes the key invisible to standard registry enumeration scripts until the permissions are forcibly taken ownership of and reset.
*   **Ghost Registries / Hives:** Advanced rootkits can manipulate the kernel to redirect registry queries. When an EDR or admin queries `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, the rootkit intercepts the call and returns a clean, fake version of the key, hiding the persistence mechanism from user-mode analysis.

## Mitigation and Hardening Strategies

*   **Attack Surface Reduction (ASR) Rules:** Implement Microsoft Defender ASR rules. Specifically, configure rules to block the execution of potentially obfuscated scripts or executable content originating from Office applications. This severs the initial infection chain, preventing the malware from ever writing to the registry.
*   **Enforce Strict Registry Permissions:** While complex to manage at scale, strict enforcement of registry permissions for sensitive keys (like IFEO, Winlogon, or AppInit_DLLs) can prevent standard users or compromised low-privilege services from making modifications.
*   **Sysmon XML Tuning and Maintenance:** Continually tune Sysmon configurations (starting with industry standards like SwiftOnSecurity or Olaf Hartong's baselines) to include new, obscure ASEPs discovered by the threat intelligence community. The registry is vast, and attackers constantly find new execution points.
*   **Disable Windows Script Host:** If VBScript and JScript are not required in the environment, modify the registry (`HKLM\SOFTWARE\Microsoft\Windows Script Host\Settings`) to set `Enabled` to `0`. This severely degrades the capability of fileless malware relying on `wscript`, `cscript`, or `mshta`.

## Chaining Opportunities
- **Defense Evasion:** Chaining Registry modifications with LOLBins (e.g., executing `reg.exe` or `regedit.exe /s` via a scheduled task) to bypass application whitelisting and EDR monitoring during the persistence establishment phase.
- **Privilege Escalation:** Combining weak registry permissions on service configurations (`ImagePath` in `HKLM\SYSTEM\CurrentControlSet\Services`) to alter a SYSTEM-level service, escalating from a local user to an administrator.
- **Credential Access & Exfiltration:** Storing dumped credentials, Kerberos tickets, or configuration data temporarily in encrypted, obscure registry keys before exfiltrating them over the network, using the registry as a covert staging ground.

## Related Notes
- [[06 - Hunting for WMI Abuse and Persistence]]
- [[07 - Detecting Malicious Scheduled Tasks and Services]]
- [[10 - Identifying Suspicious Parent-Child Process Trees]]
- [[09 - Detecting Credential Dumping LSASS Access]]
