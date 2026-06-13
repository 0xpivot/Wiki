---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.05 Detecting PowerShell Downgrade and Obfuscation"
---

# Detecting PowerShell Downgrade and Obfuscation

## 1. Introduction

PowerShell has been a favored weapon for threat actors for over a decade. As a Turing-complete, native administration framework with deep access to the Windows API, .NET framework, and WMI, it provides unparalleled post-exploitation capabilities. 

To combat this, Microsoft heavily invested in PowerShell security, culminating in PowerShell Version 5.0. Modern PowerShell includes robust telemetry via Script Block Logging (Event 4104), Module Logging, and profound runtime defense via the Antimalware Scan Interface (AMSI). 

Consequently, modern adversaries rarely use "vanilla" PowerShell. Instead, they rely on **Obfuscation** to hide their scripts from static analysis, **AMSI Bypasses** to evade runtime detection, and **Downgrade Attacks** to force execution in older, unmonitored versions of PowerShell.

## 2. The Antimalware Scan Interface (AMSI)

AMSI is an open standard that allows applications to interface natively with the installed antivirus (e.g., Windows Defender). Before PowerShell (v5+) executes a script, it passes the *deobfuscated* script content to AMSI. AMSI scans the content in memory, and if it detects a malicious signature (like `Invoke-Mimikatz`), it blocks the execution entirely.

### 2.1 Visualizing AMSI and Bypasses

```text
+-------------------------------------------------------------+
|                     PowerShell Execution                    |
|                                                             |
|  1. Attacker runs:  powershell -enc <Base64_Payload>        |
|                                                             |
|  2. PowerShell runtime decodes the Base64 in memory.        |
|                                                             |
|  3. AmsiScanBuffer() API is called by PowerShell.           |
|     +-------------------------------------------------+     |
|     |  AMSI Interface                                 |     |
|     |  Passes decoded script to Windows Defender      |     |
|     |  Result: MALICIOUS -> Execution Blocked!        |     |
|     +-------------------------------------------------+     |
|                                                             |
|  [ATTACKER BYPASS SCENARIO]                                 |
|                                                             |
|  4. Attacker runs an "AMSI Bypass" script first.            |
|     (e.g., Memory patching AmsiScanBuffer to always       |
|      return "AMSI_RESULT_CLEAN")                            |
|                                                             |
|  5. AmsiScanBuffer() API is called for subsequent payload.  |
|     +-------------------------------------------------+     |
|     |  AMSI Interface (Patched/Corrupted)             |     |
|     |  Result: CLEAN -> Execution Allowed!            |     |
|     +-------------------------------------------------+     |
+-------------------------------------------------------------+
```

## 3. PowerShell Downgrade Attacks

Because AMSI and Script Block Logging were introduced in PowerShell v5, they do not exist in PowerShell v2. By default, Windows 10/11 and Windows Server 2016+ still include the .NET Framework 2.0/3.5, which allows the PowerShell v2 engine to run if requested.

An attacker can simply execute: `powershell.exe -version 2 -Command "Malicious-Code"`

When this occurs, the script executes blindly. AMSI is not invoked, and Event ID 4104 (Script Block Logging) is completely silent. 

### 3.1 Detecting Downgrade Attacks
Hunting for downgrade attacks involves looking at **Windows PowerShell Event Log (Event ID 400 - Engine Lifecycle)**.
- **Event ID 400**: Logs when the PowerShell engine starts. The event details will clearly show `EngineVersion=2.0`.
- **Command Line Telemetry**: Windows Event 4688 or Sysmon Event 1 will capture the `-version 2` or `-v 2` argument in the process command line.

## 4. PowerShell Obfuscation Techniques

Attackers use obfuscation (popularized by tools like Daniel Bohannon's `Invoke-Obfuscation`) to evade command-line monitoring and static AV signatures.

### 4.1 Base64 Encoding
The most common technique, used to bypass character restrictions and hide initial intent.
- `powershell.exe -EncodedCommand JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACgAWwBDAG8AbgB2AGUAcgB0AF0AOgA6AEYAcgBvAG0AQgBhAHMAZQA2ADQAUwB0AHIAaQBuAGcAKAAiAEgA...`

### 4.2 Tick Marks and String Concatenation
PowerShell ignores the backtick (`) character if it is not escaping a functional character. Attackers sprinkle tick marks to break up known signatures.
- **Signature**: `Invoke-Expression`
- **Obfuscated**: `I`nv`o`k`e-E`xp`re`ss`io`n
- **String Concatenation**: `( "In" + "voke-Exp" + "ression" )`

### 4.3 Variable Randomization and Format Strings
Attackers randomize variable names and use format strings (`{0}{1}-f`) to dynamically build malicious commands in memory at runtime.
- `$rXy = 'IEX'; &( $rXy )`
- `&( "{1}{0}" -f 'EX','I' )`

## 5. Event ID 4104: Script Block Logging

To combat obfuscation, defenders must rely on **Event ID 4104 (Script Block Logging)** located in the `Microsoft-Windows-PowerShell/Operational` log.

When a script executes, the PowerShell engine evaluates the code. Regardless of how heavily obfuscated the initial command line is, PowerShell *must* deobfuscate the code in memory to execute it. Event ID 4104 captures this deobfuscated code block just before execution.

If an attacker runs a massive Base64 string, Event 4688 will only show the Base64. Event 4104 will log the actual human-readable script payload that the Base64 decoded into.

## 6. Real-World Attack Scenario

### Fileless Malware using Obfuscation and AMSI Bypass

1. **Initial Access**: A macro executes a heavily obfuscated PowerShell one-liner using string concatenation and tick marks.
   - *Sysmon Event 1 / Event 4688*: Captures the heavily obfuscated `powershell.exe` command line.
2. **AMSI Patching**: The first instruction in the deobfuscated payload loads `kernel32.dll`, finds the memory address for `amsi.dll!AmsiScanBuffer`, and overwrites the first few bytes with a `RET` (Return) instruction.
   - *Sysmon Event 10 (ProcessAccess)*: May log PowerShell requesting a handle to its own process to modify memory, though this is difficult to tune.
3. **Payload Download**: With AMSI effectively lobotomized, the script invokes `Net.WebClient` to download a secondary stage (like a Cobalt Strike beacon or Empire agent) directly into memory.
   - *Event ID 4104*: Logs the deobfuscated AMSI bypass script.
   - *Sysmon Event 3*: Logs `powershell.exe` making an outbound HTTPS connection to the C2 server.

## 7. Advanced Hunting Queries

### KQL Query: Detecting Base64 Encoded Commands (Event 4688/Sysmon 1)
```kusto
SecurityEvent
| where EventID == 4688
| where ProcessName endswith "powershell.exe" or ProcessName endswith "pwsh.exe"
| where CommandLine has_any ("-enc", "-EncodedCommand", "-ec", "-en", "-e")
| project TimeGenerated, Computer, Account, CommandLine
```

### KQL Query: Detecting PowerShell Downgrade (Event 400)
```kusto
Event
| where EventLog == "Windows PowerShell"
| where EventID == 400
| parse EventData with * "EngineVersion=" EngineVersion "<" *
| where EngineVersion startswith "2."
| project TimeGenerated, Computer, EngineVersion
```

### KQL Query: Hunting for Suspicious Keywords in Script Blocks (Event 4104)
```kusto
Event
| where EventLog == "Microsoft-Windows-PowerShell/Operational"
| where EventID == 4104
| where EventData has_any ("AmsiUtils", "amsiInitFailed", "System.Management.Automation.AmsiUtils", "VirtualAlloc", "WriteProcessMemory", "kernel32", "MiniDumpWriteDump")
| project TimeGenerated, Computer, EventData
```

## 8. Mitigation and Hardening

1. **Enable Script Block Logging**: Ensure `Turn on PowerShell Script Block Logging` is enabled via Group Policy.
2. **Remove PowerShell v2**: Uninstall the legacy PowerShell v2 engine from all endpoints. It is an optional Windows feature that can be removed via `Disable-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root`.
3. **Constrained Language Mode (CLM)**: Implement CLM via AppLocker or WDAC. CLM severely limits the capabilities of PowerShell for non-administrative users, blocking the use of COM objects, arbitrary .NET types, and direct Windows API calls (which prevents almost all AMSI bypasses and memory injection techniques).

## 9. Chaining Opportunities
- **[[01 - Windows Event Logs Deep Dive Event IDs 4624 4688]]**: Event 4688 is the first line of defense for spotting the initial PowerShell invocation.
- **[[03 - Hunting for Process Injection and Hollowing]]**: Once AMSI is bypassed, attackers use PowerShell to inject shellcode into other processes.
- **[[04 - Hunting for Living off the Land Binaries LOLBAS]]**: PowerShell is the most critical LOLBin; securing it forces attackers to use more fragile, less capable binaries.

## 10. Related Notes
- [[Windows AppLocker and Constrained Language Mode]]
- [[AMSI Bypass Tradecraft]]
- [[Malware Analysis of Obfuscated Scripts]]
