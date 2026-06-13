---
tags: [cobalt-strike, malleable-c2, red-team, vapt]
difficulty: advanced
module: "96 - Cobalt Strike and Advanced Malleable C2"
topic: "96.11 Elevate Kit for Privilege Escalation"
---

# 96.11 Elevate Kit for Privilege Escalation

## 1. Executive Summary
The Cobalt Strike Elevate Kit is a powerful framework extension designed to enhance the privilege escalation capabilities of the Cobalt Strike Beacon. By default, Cobalt Strike includes standard privilege escalation methods, but modern security environments often require custom or newly discovered exploits. The Elevate Kit provides a standardized interface for integrating third-party exploits, allowing operators to execute local privilege escalation (LPE) techniques seamlessly within the framework. Understanding the mechanisms of the Elevate Kit is critical for Threat Hunters, Incident Responders, and Red Teamers to effectively simulate, detect, and mitigate advanced persistent threats (APTs).

## 2. Core Mechanics of the Elevate Kit
The Elevate Kit utilizes Cobalt Strike's built-in Aggressor Scripting engine to hook into the `elevate` command. When an operator types `elevate <exploit_name> <listener>`, the script intercepts this command, processes the required exploit binaries or reflective DLLs, and injects them into memory for execution.

### Key Components:
- **Aggressor Script (.cna):** The glue that binds the exploit to the Cobalt Strike UI and command parser. It defines how the exploit payload is passed to the Beacon.
- **Reflective DLLs / Binaries:** The actual exploit payloads compiled to execute reflectively in memory without touching the disk.
- **Listener Integration:** The capability to automatically spawn a new Beacon session with elevated privileges upon successful exploitation.

### Registration Process:
Aggressor scripts use the `beacon_exploit_register` function to add new techniques to the `elevate` menu and command-line autocomplete.
```perl
beacon_exploit_register("ms16-032", "MS16-032 Secondary Logon Handle Privilege Escalation", &invoke_ms16_032);
```

## 3. Privilege Escalation Categories Handled

### 3.1 Token Manipulation
Exploits that manipulate access tokens often rely on stealing tokens from higher-privileged processes (e.g., `winlogon.exe` or `lsass.exe`). The Elevate Kit can deploy reflective DLLs that duplicate SYSTEM tokens and apply them to the current thread, completely bypassing normal access controls.

### 3.2 Named Pipe Impersonation
This technique involves creating a malicious named pipe and tricking a highly privileged service (like the `SYSTEM` account or `Print Spooler`) into writing to it. Once the service connects, the exploit calls `ImpersonateNamedPipeClient()`.

### 3.3 User Account Control (UAC) Bypasses
UAC bypasses do not necessarily exploit kernel vulnerabilities. Instead, they abuse Windows features like auto-elevating COM objects, DLL hijacking in privileged directories, or environment variable manipulation.

## 4. Architecture Diagram: Elevate Kit Execution Flow

```text
+-------------------------------------------------------------------+
|                       Cobalt Strike Team Server                   |
|                                                                   |
|  [Operator] --> Types: `elevate uac-schtasks default`             |
|                                |                                  |
+--------------------------------|----------------------------------+
                                 | 1. Command and DLL sent to Beacon
                                 v
+-------------------------------------------------------------------+
|                       Compromised Endpoint                        |
|                                                                   |
| +-------------------------+                                       |
| |       Beacon.exe        |  2. Aggressor script intercepts       |
| |                         |  3. Reflective DLL packaged           |
| | [ In-Memory Execution ] |  4. Injection into target process     |
| +-------------------------+                                       |
|            |                                                      |
|            | 5. Exploit Execution (e.g., COM Elevation)           |
|            v                                                      |
| +-------------------------+                                       |
| |   High-Priv Process     |  6. Spawns new elevated Beacon        |
| | (e.g., svchost.exe)     |-------------------------------------->[New SYSTEM Beacon]
| +-------------------------+                                       |
+-------------------------------------------------------------------+
```

## 5. Deep Dive: Named Pipe Impersonation
Named Pipe Impersonation is a staple in the Elevate Kit arsenal and widely abused by malware families.

### Execution Steps:
1. **Pipe Creation:** The exploit creates a named pipe with a predictable or randomly generated name, e.g., `\\.\pipe\ElevatePipe_1234`.
2. **Triggering the Client:** The exploit forces a SYSTEM-level process to connect to the pipe. This is often done by invoking an RPC call to a vulnerable service.
3. **Impersonation:** As soon as the connection is established, the exploit thread invokes the `ImpersonateNamedPipeClient()` API.
4. **Execution:** The thread now operates with SYSTEM privileges. It then injects the new Beacon payload into memory or spawns a new process.

### Threat Hunting Telemetry:
Defenders must monitor for anomalous named pipe creation and access.
- **Sysmon Event ID 17 (Pipe Created):** Look for unusual pipe names or pipes created by non-standard processes (e.g., `cmd.exe` or `powershell.exe` creating pipes).
- **Sysmon Event ID 18 (Pipe Connected):** Look for SYSTEM processes connecting to pipes created by user-level, low-integrity processes.

## 6. Deep Dive: UAC Bypasses via Auto-Elevation
Many UAC bypasses in the Elevate Kit abuse auto-elevating COM interfaces. Windows allows certain COM objects to bypass UAC prompts if they are requested by an auto-elevating binary (e.g., `explorer.exe`).

### The ICMLuaUtil Bypass:
1. The exploit injects code into `explorer.exe` or uses a mock directory structure (e.g., `C:\Windows \System32`).
2. It instantiates the `ICMLuaUtil` COM interface.
3. It calls the `ShellExec` method of the interface, passing the path to the Cobalt Strike payload or a proxy binary.
4. Because the COM object auto-elevates, the payload runs as High Integrity without prompting the user, effectively bypassing UAC restrictions.

## 7. Threat Hunting and Detection Engineering

Detecting Elevate Kit usage requires a defense-in-depth approach, focusing on the behavioral artifacts of the exploits rather than the framework itself. Standard AV signatures rarely catch reflective memory execution.

### Detection Strategies:
- **Reflective DLL Injection:** Monitor for `CreateRemoteThread` or anomalous `VirtualAllocEx` calls, especially those allocating `PAGE_EXECUTE_READWRITE` memory in remote processes.
- **Parent-Child Process Anomalies:** A low-privileged process suddenly spawning a high-privileged process is highly suspicious (e.g., Medium Integrity `powershell.exe` spawning System Integrity `rundll32.exe`).
- **File System Artifacts:** Some UAC bypasses drop temporary DLLs in `C:\Windows\Tasks` or `C:\Temp` to facilitate DLL hijacking.

### KQL Query: Suspicious Named Pipe Impersonation
```kusto
DeviceEvents
| where ActionType == "NamedPipeEvent"
| where InitiatingProcessAccountName != "SYSTEM"
| where TargetAccountName == "SYSTEM"
| where PipeName contains "Elevate" or PipeName matches regex @"\\[a-f0-9]{8}-[a-f0-9]{4}"
| project TimeGenerated, DeviceName, InitiatingProcessFileName, PipeName, TargetAccountName
```

### KQL Query: COM Object Abuse
```kusto
DeviceProcessEvents
| where InitiatingProcessFileName =~ "dllhost.exe"
| where ProcessCommandLine contains "3E5FC7F9-9A51-4367-9063-A120244FBEC7" // CMSTPLUA COM Object
| project TimeGenerated, DeviceName, InitiatingProcessFileName, ProcessCommandLine, FileName
```

## 8. Real-World Attack Scenario

### The Setup
An Advanced Persistent Threat (APT) group gains initial access to a corporate network via a spear-phishing email. The victim executes a macro-enabled Word document, which downloads and executes a Cobalt Strike Beacon payload. The initial beacon operates under the context of the user `jdoe` (Medium Integrity).

### The Escalation
1. The red team operator queries the system for vulnerabilities and notices the system is missing a critical patch for the Print Spooler service (PrintNightmare vulnerability).
2. The operator loads a custom Elevate Kit module containing the PrintNightmare exploit.
3. They execute `elevate printnightmare tcp_local` in the Cobalt Strike console.
4. The exploit reflectively loads into memory, interacts with the local Spooler service via RPC, and leverages the vulnerability to execute a payload as `NT AUTHORITY\SYSTEM`.
5. A new SMB beacon checks in, providing the operator with full SYSTEM control over the endpoint.

### The Defender's View
The SOC receives an alert triggered by Sysmon Event ID 1 (Process Creation). The alert flags `spoolsv.exe` spawning `rundll32.exe` with anomalous command-line arguments. Further investigation using EDR telemetry reveals a dropped driver file in the spooler directory, a classic signature of the PrintNightmare exploit deployed via a C2 framework.

## 9. Incident Response Playbook
If an Elevate Kit exploit is detected:
1. **Containment:** Immediately isolate the affected endpoint from the network to prevent lateral movement.
2. **Memory Forensics:** Capture a RAM dump (using tools like WinPmem or FTK Imager) before rebooting, as the reflective DLLs reside entirely in memory.
3. **Eradication:** Identify the root cause vulnerability (e.g., missing patch, misconfigured UAC) and apply the necessary updates. Terminate the active Beacon processes.
4. **Hunting:** Search the environment for identical named pipe connections, anomalous COM object instantiations, and unauthorized SYSTEM-level process creations.

## 10. MITRE ATT&CK Mapping
- **TA0004 Privilege Escalation**
- **T1134 Access Token Manipulation:** Duplicating and impersonating tokens.
- **T1548 Abuse Elevation Control Mechanism:** Bypassing UAC via COM interfaces.
- **T1068 Exploitation for Privilege Escalation:** Executing kernel or service exploits.

## 11. Mitigation Strategies
- **Patch Management:** Ensure all systems are regularly patched against known LPE vulnerabilities (e.g., Windows Kernel, Print Spooler, ALPC).
- **LAPS:** Implement the Local Administrator Password Solution (LAPS) to prevent credential reuse and lateral movement if one host is compromised.
- **UAC Configuration:** Set UAC to "Always Notify" to prevent silent auto-elevation bypasses and ensure all users operate with standard accounts.
- **Attack Surface Reduction (ASR):** Enable ASR rules to block Office applications from creating child processes and block executable files from running unless they meet strict trust criteria.

## 12. Chaining Opportunities
- After successful privilege escalation using the Elevate Kit, operators typically proceed to dump credentials using tools like Mimikatz, NanoDump, or specialized BOFs. See [[14 - Lateral Movement and Pivoting with Cobalt Strike]] for the next steps in an attack lifecycle.
- High-integrity beacons are essential for installing deep persistence mechanisms (like WMI event subscriptions) or disabling security tooling via kernel drivers. This directly ties into EDR evasion strategies discussed in [[15 - EDR Evasion with Custom Cobalt Strike Kits]].

## 13. Related Notes
- [[05 - Windows Privilege Escalation Fundamentals]]
- [[12 - Aggressor Scripts Automating Red Team Tasks]]
- [[13 - Cobalt Strike BOFs Beacon Object Files Development]]
- [[Threat Hunting Event IDs Reference]]
- [[Bypassing User Account Control (UAC)]]
