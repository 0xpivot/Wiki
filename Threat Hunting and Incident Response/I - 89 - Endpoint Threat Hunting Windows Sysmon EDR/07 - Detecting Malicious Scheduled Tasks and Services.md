---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.07 Detecting Malicious Scheduled Tasks and Services"
---

# 89.07 Detecting Malicious Scheduled Tasks and Services

## Introduction to Scheduled Tasks and Services Abuse

The Windows operating system relies heavily on automated, background execution mechanisms to maintain system health, install software updates, manage hardware drivers, and run legitimate third-party applications. The two primary mechanisms facilitating this automation are **Scheduled Tasks** and **Windows Services**. Due to their inherent nature of executing code system-wide, autonomously, and often with the highest level of privileges (`NT AUTHORITY\SYSTEM`), they represent prime targets for adversaries across the entire attack lifecycle.

Threat actors abuse these mechanisms primarily for three reasons:
1.  **Persistence:** Ensuring malicious code survives reboots and user logoffs.
2.  **Privilege Escalation:** Exploiting misconfigurations in existing tasks/services to elevate from a standard user to an administrator or SYSTEM.
3.  **Lateral Movement:** Utilizing remote service creation or remote task scheduling to execute code on adjacent machines within a domain.

Unlike highly complex techniques like rootkits or WMI repository modification, abusing scheduled tasks and services is conceptually simple, highly reliable, and natively supported by the OS, making it a staple technique in both commodity malware (like ransomware) and advanced persistent threat (APT) campaigns.

## Mechanism 1: Windows Services Deep Dive

A Windows Service is a long-running executable application that runs in its own Windows session. It does not require user interaction or a graphical interface. The Service Control Manager (SCM), accessible via `services.exe`, is the core component responsible for managing the state of these services (starting, stopping, pausing) based on boot configurations or on-demand requests.

### How Attackers Abuse Services

Attackers typically abuse services through three distinct methodologies:

1.  **Direct Service Creation (Persistence & Lateral Movement):** 
    Attackers with administrative privileges create entirely new services pointing to their malicious binary. They utilize native tools like the `sc.exe` command-line utility, PowerShell (`New-Service`), or direct Windows API calls (`CreateServiceW`). 
    *   *Lateral Movement Context:* This is the exact mechanism utilized by PsExec and Impacket's `psexec.py`. These tools connect to the target machine over SMB, copy a binary to the `ADMIN$` share, connect to the remote SCM, create a temporary service pointing to that binary, start the service, and then delete it to cover their tracks.

2.  **Service Modification (Defense Evasion):** 
    Instead of creating a noisy new service, an attacker may modify an existing, legitimate service. They often target services that are set to "Disabled" or "Manual" start types to avoid disrupting critical OS functions. The attacker modifies the `ImagePath` (also known as `binPath`) registry value of the service to point to their malicious executable instead of the original Microsoft binary.

3.  **Unquoted Service Path (Privilege Escalation):** 
    This is a classic local privilege escalation technique arising from poor software development practices. If a service's `ImagePath` contains spaces but lacks surrounding quotation marks (e.g., `C:\Program Files\Enterprise App\service.exe`), the Windows API `CreateProcess` attempts to execute the path sequentially.
    *   It will first look for `C:\Program.exe`.
    *   If not found, it looks for `C:\Program Files\Enterprise.exe`.
    *   If an attacker has write permissions to the root of `C:\` or the `C:\Program Files\` directory, they can drop a malicious binary named `Program.exe` or `Enterprise.exe`. When the service starts (often as SYSTEM), the attacker's binary intercepts the execution flow.

### ASCII Diagram: Service Execution Flow and Exploitation

```text
+---------------------+      RPC/Local APIs     +---------------------------+
| Attacker Tooling    | ==================> | Service Control Manager   |
| (sc.exe / PsExec /  |   CreateService() / | (services.exe)            |
|  Custom Malware)    |   ChangeServiceConfig|                           |
+---------------------+                     +-------------+-------------+
                                                          |
                                                          | Modifies Registry
                                                          v
+---------------------+                     +---------------------------+
| Malicious Payload   | <================== | Windows Registry:         |
| (C:\Temp\svchost.exe|  Executes payload   | HKLM\SYSTEM\CurrentControl|
| OR C:\Program.exe)  |   at next boot or   | Set\Services\NewService   |
+---------------------+   manual start      |                           |
                                            | ImagePath = "C:\Temp\..." |
                                            | OR Unquoted Path Vulnerab |
                                            +---------------------------+
```

## Mechanism 2: Scheduled Tasks Deep Dive

The Windows Task Scheduler executes pre-configured actions at specified times or in response to specific system events. Tasks are defined by XML files stored in `C:\Windows\System32\Tasks\` and are managed via the `schtasks.exe` utility, the `taskschd.msc` GUI console, or the Task Scheduler COM API.

### How Attackers Abuse Scheduled Tasks

1.  **Reliable Persistence:** Attackers create tasks configured to trigger on common events, ensuring constant execution. Frequent triggers include:
    *   `On Logon`: Executes when any user logs in.
    *   `On Startup`: Executes during the boot process.
    *   `Time-Based`: Executes every X minutes or daily at a specific time.
    *   *Deception:* Attackers heavily rely on deceptive naming conventions to blend in with hundreds of legitimate tasks (e.g., naming tasks `WindowsUpdateBrowserTask`, `AdobeAcrobatUpdater`, or `SystemHealthCheck`).

2.  **System Privilege Execution & UAC Bypass:** Tasks can be configured to run under a specific principal, including `NT AUTHORITY\SYSTEM` or `Highest Privileges`. An attacker with local admin rights can create a scheduled task to execute a secondary payload as SYSTEM. Furthermore, tasks configured to run with highest privileges do not trigger a User Account Control (UAC) prompt, making them a common mechanism for UAC bypass tools.

3.  **Lateral Movement via Remote Scheduling:** The `schtasks.exe` utility inherently supports remote execution (e.g., `schtasks /create /s \\target_ip /tn "Updater" /tr "C:\malware.exe" /sc onstart`). Similar to remote services, this provides a native, LotL method to execute commands across the network using compromised credentials.

## Hunting Strategies and Telemetry

Detecting malicious services and scheduled tasks requires a deep understanding of environment baselines and robust endpoint telemetry. You are primarily looking for anomalies in process creation, registry modifications, and specific OS security event logs.

### Critical Event Logs

*   **System Event ID 7045 (A service was installed in the system):** 
    This is arguably one of the most critical events for threat hunting. **Every single 7045 event should be collected and analyzed.**
    *   *Hunting Focus:* Look for `ImagePath` values pointing to user profiles (`C:\Users\*`), temporary directories (`%TEMP%`), or public folders (`C:\Users\Public\`). Scrutinize any service that executes a command interpreter or script engine (e.g., `cmd.exe`, `powershell.exe`, `wscript.exe`) directly in the image path.

*   **Security Event ID 4698 (A scheduled task was created):** 
    Requires 'Audit Object Access' to be configured. This event captures the raw XML of the task being created.
    *   *Hunting Focus:* Parse the XML to identify tasks running as SYSTEM, executing from unusual directories, or executing highly obfuscated command lines.

*   **Security Event ID 4699 (A scheduled task was deleted):** 
    Attackers frequently create a task, execute their payload, and immediately delete the task to destroy forensic evidence. Rapid creation (4698) followed by deletion (4699) of the same task name is highly suspicious.

*   **Sysmon Event ID 1 (Process Creation):** 
    Monitor the command-line arguments of `sc.exe` and `schtasks.exe`.

### Advanced Detection Strategies: KQL (Microsoft Sentinel)

```kusto
// 1. Detect Suspicious Service Creation via OS Logs (Event ID 7045)
// Filtering for script engines and unusual execution paths
Event
| where EventLog == "System" and EventID == 7045
| extend ServiceName = extract(@"Service Name:\s+(.*)", 1, RenderedDescription)
| extend ImagePath = extract(@"Service File Name:\s+(.*)", 1, RenderedDescription)
| extend ServiceType = extract(@"Service Type:\s+(.*)", 1, RenderedDescription)
| where ImagePath has_any ("cmd.exe", "powershell.exe", "pwsh.exe", "wscript.exe", "cscript.exe", "rundll32.exe", "mshta.exe")
   or ImagePath matches regex @"(?i)(C:\\Users\\.*|C:\\Temp\\.*|C:\\Windows\\Temp\\.*|C:\\ProgramData\\.*)"
| project TimeGenerated, Computer, ServiceName, ImagePath, ServiceType
| sort by TimeGenerated desc
```

```kusto
// 2. Detect Scheduled Task Creation via schtasks.exe with Suspicious Arguments (Sysmon ID 1)
// Looking for creation commands that specify high privileges or execute scripts.
DeviceProcessEvents
| where FileName =~ "schtasks.exe"
| where ProcessCommandLine has_any ("/create", "-create")
// Isolate tasks requesting SYSTEM or highest privileges, or running on startup/logon
| where ProcessCommandLine has_any ("SYSTEM", "HIGHEST", "ONLOGON", "ONSTART", "MINUTE")
// Correlate with payloads that are often malicious in this context
| where ProcessCommandLine has_any ("powershell", "cmd", "certutil", ".ps1", ".bat", ".vbs", "rundll32", "regsvr32")
| project TimeGenerated, DeviceName, InitiatingProcessFileName, InitiatingProcessCommandLine, ProcessCommandLine, AccountName
```

```kusto
// 3. Detect PsExec Lateral Movement Pattern (Temporary Service Creation)
// PsExec connects, creates a service (often named PSEXESVC), runs it, and deletes it.
DeviceEvents
| where ActionType == "ServiceInstalled"
| where AdditionalFields contains "PSEXESVC" or (FileName =~ "services.exe" and InitiatingProcessFileName =~ "services.exe")
// Join with Named Pipe creation, a strong indicator of PsExec SMB communication
| join kind=inner (
    DeviceEvents
    | where ActionType == "NamedPipeCreated"
    | where AdditionalFields contains "PSEXESVC"
) on DeviceName
| project TimeGenerated, DeviceName, ActionType, AdditionalFields, InitiatingProcessFileName
```

## Real-World Attack Scenario

### Ransomware Deployment via Group Policy and Scheduled Tasks
During a prolonged incident involving a major ransomware syndicate (similar to Conti or Ryuk operations), the threat actors achieved domain dominance. They needed a reliable, instantaneous method to deploy their encryptor across thousands of endpoints simultaneously to overwhelm defenders.

**Detailed Attack Flow:**

1.  **Preparation & Staging:** The attackers staged the ransomware binary (`svchost_update.exe`) on the central `SYSVOL` share of the primary Domain Controller. `SYSVOL` is replicated across all DCs and is accessible by default to all domain-joined machines for fetching policies.
2.  **GPO Modification:** Instead of writing complex, noisy deployment scripts, the attackers chose a stealthier route. They edited a central Group Policy Object (GPO) that was already linked to the main workstation Organizational Unit (OU).
3.  **Scheduled Task Preference Creation:** Inside the Group Policy Management Editor, they navigated to *Preferences -> Control Panel Settings -> Scheduled Tasks*. They configured a new "Scheduled Task (At least Windows 7)" preference item.
    *   **Name:** `MicrosoftEdgeUpdateTaskMachineCore` (Deceptive naming)
    *   **Action:** Execute program: `\\domain.local\SYSVOL\scripts\svchost_update.exe`
    *   **Trigger:** Daily at 2:00 AM local time.
    *   **Security Options:** Run whether user is logged on or not; Run with highest privileges; Account: `NT AUTHORITY\SYSTEM`.
4.  **Propagation:** Over the next 90-120 minutes, all online domain workstations refreshed their Group Policy and silently downloaded the new scheduled task configuration from the `SYSVOL` share. The task was registered locally on thousands of machines.
5.  **Simultaneous Execution:** At exactly 2:00 AM, the local `Task Scheduler` service (`svchost.exe`) on every infected endpoint triggered. It reached out to the DC, pulled the ransomware binary into memory, and executed it as `SYSTEM`. The environment was entirely encrypted within minutes.

## Advanced Evasion Techniques

*   **API Obfuscation & Direct Syscalls:** Advanced malware and C2 frameworks (like Cobalt Strike or Brute Ratel) bypass `sc.exe` and standard Win32 APIs (like `CreateServiceW`). Instead, they opt to use Direct System Calls or undocumented APIs to interact directly with the SCM. This effectively circumvents user-mode EDR hooks that monitor `services.exe` for API calls, resulting in a silent service creation.
*   **COM Object Hijacking inside Scheduled Tasks:** Instead of executing an `.exe` directly, a scheduled task can be configured in its XML to instantiate a Custom COM Handler (via a CLSID). The attacker registers a malicious DLL to that specific CLSID in the registry. When the task runs, the Task Scheduler process loads the malicious DLL natively into its own address space. This leaves a very minimal command-line footprint and appears as legitimate OS behavior.
*   **Timestamp Stomping (Timestomping):** After creating the XML task definition file in `C:\Windows\System32\Tasks`, attackers use API calls to modify the file's 'Creation' and 'Last Modified' timestamps. They set these timestamps to match the installation date of the operating system. When hunters perform forensic analysis and sort tasks by creation date, the malicious task blends in with hundreds of legitimate tasks created years ago.
*   **SDDL Manipulation:** Attackers can modify the Security Descriptor Definition Language (SDDL) of a service to hide it completely from standard API enumeration tools (like `Get-Service` or `sc query`), effectively rendering it invisible to basic administrative checks.

## Mitigation and Hardening Strategies

*   **Principle of Least Privilege (PoLP):** This is the most critical mitigation. Strictly limit who can create services or scheduled tasks. End users must operate as standard users, never local administrators. Creating a SYSTEM-level task or service requires elevated privileges; removing local admin rights stops this attack vector cold.
*   **Application Control (AppLocker/WDAC):** Implement strict Application Control policies. Even if an attacker manages to create a scheduled task, AppLocker can block the execution if the binary resides in an untrusted location (e.g., `%TEMP%`, `C:\Users\Public`) or lacks a trusted digital signature.
*   **Monitor and Restrict Temporary Paths:** Actively monitor for binary execution originating from user profile directories and temporary folders. Utilize Microsoft Defender ASR rules to block processes originating from these paths.
*   **Hardening Service Configurations:** Regularly audit services for unquoted service path vulnerabilities using automated scripts. Enforce proper path quoting and ensure that standard users do not have modify permissions on service directories.

## Chaining Opportunities
- **Privilege Escalation:** Combining Unquoted Service Paths or weak service directory permissions with arbitrary file write vulnerabilities to elevate from a standard user to SYSTEM.
- **Lateral Movement & Credential Access:** Utilizing Pass-the-Hash (PtH) techniques combined with WMI or PsExec to remotely instantiate services on target machines, often dumping credentials (via LSASS access) as the service payload.
- **Defense Evasion:** Chaining scheduled task execution with Living-off-the-Land Binaries (LOLBins). For example, scheduling a task that runs `mshta.exe` to pull a remote payload, hiding the true malicious intent behind a trusted Microsoft binary.

## Related Notes
- [[06 - Hunting for WMI Abuse and Persistence]]
- [[08 - Hunting for Registry Modifications and Run Keys]]
- [[10 - Identifying Suspicious Parent-Child Process Trees]]
- [[09 - Detecting Credential Dumping LSASS Access]]
