---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.02 Microsoft Sysmon Configuration and Telemetry"
---

# Microsoft Sysmon Configuration and Telemetry

## 1. Introduction

System Monitor (Sysmon), part of the Sysinternals suite, is a profound Windows system service and device driver. Once installed on a host, it remains resident across system reboots to continuously monitor and log system activity to the Windows event log. Unlike default Windows Security Event Logs, which can be noisy and sometimes lack contextual depth, Sysmon provides granular, highly configurable telemetry.

It captures detailed information about process creations, network connections, changes to file creation times, registry modifications, WMI activity, and inter-process memory access. By collecting the events it generates using Windows Event Collection (WEC) or SIEM agents, threat hunters and incident responders can identify malicious activity, track lateral movement, and deeply understand how intruders and malware operate within their network.

## 2. Sysmon Architecture

Sysmon operates using a dual-layered architecture, functioning in both user mode and kernel mode to securely and efficiently capture system events without significant performance degradation.

1. **Kernel-Mode Device Driver (`SysmonDrv.sys`)**: This driver registers callbacks with the Windows kernel to intercept critical system events (e.g., process creation, thread creation, image loading). Because it operates in kernel mode, it can capture events before user-land API hooks can be bypassed by advanced malware.
2. **User-Mode Service (`Sysmon.exe`)**: The driver passes the raw event data to the user-mode service. The service parses the XML configuration file, applies inclusion and exclusion filters, enriches the data (e.g., hashing files, resolving IP addresses), and writes the final event to the ETW (Event Tracing for Windows) channel, which is then visible in the Event Viewer.

### 2.1 Visualizing Sysmon's Architecture

```text
+-------------------------------------------------------------+
|                       USER MODE                             |
|                                                             |
|  +----------------+    Filter/Enrich    +----------------+  |
|  | Sysmon Service | <------------------ | Sysmon Config. |  |
|  |  (Sysmon.exe)  |                     |     (XML)      |  |
|  +----------------+                     +----------------+  |
|          |                                                  |
|          v (Writes to Event Log)                            |
|  +----------------+                                         |
|  |  Event Viewer  | (Applications and Services Logs ->      |
|  | (ETW Channel)  |  Microsoft -> Windows -> Sysmon ->      |
|  +----------------+  Operational)                           |
+----------^--------------------------------------------------+
           |
+----------|--------------------------------------------------+
|          |            KERNEL MODE                           |
|          | (Raw Event Data)                                 |
|  +----------------+                                         |
|  | Sysmon Driver  |                                         |
|  | (SysmonDrv.sys)|                                         |
|  +----------------+                                         |
|      ^   ^   ^ (Kernel Callbacks)                           |
|      |   |   |                                              |
|  +----------------+                                         |
|  | Windows Kernel | (Process, Network, File, Registry, WMI) |
|  +----------------+                                         |
+-------------------------------------------------------------+
```

## 3. Key Sysmon Event IDs for Threat Hunting

While Sysmon generates over two dozen event IDs, several stand out as critical for endpoint threat hunting.

### 3.1 Event ID 1: Process Creation
Similar to Windows Event 4688, but significantly enhanced. Sysmon Event 1 captures the `CommandLine`, `ParentCommandLine`, `User`, `LogonGuid`, and cryptographic hashes of the binary (MD5, SHA1, SHA256, IMPHASH).
- **Hunting Value**: IMPHASH is incredibly valuable. It hashes the import table of a Portable Executable (PE). Attackers frequently recompile or pad malware to change the SHA256 hash, but if the imported APIs remain the same, the IMPHASH remains static. This allows hunters to track malware families across recompilations.

### 3.2 Event ID 3: Network Connection
Logs TCP/UDP connections. It captures `SourceIp`, `SourcePort`, `DestinationIp`, `DestinationPort`, and the `Image` (process) responsible for the connection.
- **Hunting Value**: Correlating Event 1 (Process Creation) with Event 3 reveals LOLBins (e.g., `certutil.exe`, `powershell.exe`) making unexpected outbound connections to the internet, a prime indicator of Command and Control (C2) or payload downloading.

### 3.3 Event ID 8: CreateRemoteThread
Logs when a process creates a thread in the memory space of another process.
- **Hunting Value**: This is a classic indicator of Process Injection. If `rundll32.exe` creates a remote thread in `explorer.exe`, it strongly suggests malware is attempting to hide its execution within a trusted system process.

### 3.4 Event ID 10: ProcessAccess
Logs when a process opens a handle to another process (using `OpenProcess`).
- **Hunting Value**: Crucial for detecting credential dumping. When tools like Mimikatz or `procdump.exe` attempt to read the memory of `lsass.exe`, Sysmon logs an Event 10 where `TargetImage` is `lsass.exe` and `GrantedAccess` often reflects `0x1010` or `0x143a` (PROCESS_VM_READ).

### 3.5 Event ID 11: FileCreate
Logs when a file is created or overwritten.
- **Hunting Value**: Useful for tracking malware drops, particularly in suspicious directories like `C:\Users\Public\` or `\AppData\Local\Temp\`. It is also useful for tracking ransomware encrypting files, though this can be very noisy and requires careful tuning.

### 3.6 Event ID 22: DNSEvent
Logs DNS queries executed by processes.
- **Hunting Value**: Detects malware resolving C2 domains, even if the actual network connection (Event 3) is blocked by a firewall. It helps bypass network-layer encryption by showing the intended destination at the DNS layer.

## 4. Sysmon Configuration and Tuning Deep Dive

Sysmon is practically useless—or worse, a performance bottleneck—without a meticulously crafted XML configuration file. The configuration dictates what is explicitly logged (`include`) and what is ignored (`exclude`). 

The industry standard starting point is often the SwiftOnSecurity or Olaf Hartong (SysmonModular) configurations.

### 4.1 Filtering Logic
Sysmon evaluates rules based on the `onmatch` attribute of a RuleGroup.
- `<RuleGroup name="process_creation" groupRelation="or">`
- `<ProcessCreate onmatch="include">`: This means "Log NOTHING by default, ONLY log what matches the rules below."
- `<ProcessCreate onmatch="exclude">`: This means "Log EVERYTHING by default, EXCEPT what matches the rules below."

For high-volume events like Event ID 3 (Network) or Event ID 10 (Process Access), `onmatch="exclude"` is typically used to filter out known, noisy, benign processes (like Chrome, Spotify, or Windows Defender).

### 4.2 Example Configuration Snippet
```xml
<Sysmon schemaversion="4.81">
  <HashAlgorithms>md5,sha256,imphash</HashAlgorithms>
  <EventFiltering>
    <!-- Event ID 1: Process Creation -->
    <RuleGroup name="" groupRelation="or">
      <ProcessCreate onmatch="include">
        <!-- Log all instances of command shells -->
        <Image condition="end with">cmd.exe</Image>
        <Image condition="end with">powershell.exe</Image>
        <Image condition="end with">pwsh.exe</Image>
      </ProcessCreate>
    </RuleGroup>

    <!-- Event ID 10: Process Access -->
    <RuleGroup name="" groupRelation="or">
      <ProcessAccess onmatch="include">
        <!-- Alert on ANY process accessing LSASS -->
        <TargetImage condition="is">C:\Windows\system32\lsass.exe</TargetImage>
      </ProcessAccess>
      <ProcessAccess onmatch="exclude">
        <!-- Exclude known good processes accessing LSASS to reduce noise -->
        <SourceImage condition="is">C:\ProgramData\Microsoft\Windows Defender\Platform\MsMpEng.exe</SourceImage>
        <SourceImage condition="is">C:\Windows\system32\svchost.exe</SourceImage>
      </ProcessAccess>
    </RuleGroup>
  </EventFiltering>
</Sysmon>
```

## 5. Real-World Attack Scenario

### Cobalt Strike Beacon Execution and Credential Dumping

An attacker sends a spear-phishing email with a malicious macro-enabled Word document.

1. **Initial Execution (Event ID 1)**: 
   - `winword.exe` (Parent) spawns `cmd.exe` (Child) with a command line invoking PowerShell. 
   - Sysmon Event 1 logs this abnormal parent-child relationship. The `CommandLine` field shows a massive Base64 encoded string.
2. **Network C2 Callback (Event ID 22 & Event ID 3)**:
   - The PowerShell process performs a DNS lookup for `malicious-c2.com`. (Sysmon Event 22).
   - PowerShell then establishes a TCP connection over port 443 to the resolved IP. (Sysmon Event 3).
3. **Process Injection (Event ID 8)**:
   - The attacker decides to migrate the Cobalt Strike beacon from `powershell.exe` into a more stable, less suspicious process. They choose `explorer.exe`.
   - Sysmon Event 8 is generated: `SourceImage` is `powershell.exe`, `TargetImage` is `explorer.exe`.
4. **Credential Dumping (Event ID 10)**:
   - Operating from within the `explorer.exe` process space, the attacker uses the beacon's built-in Mimikatz module (`logonpasswords`).
   - `explorer.exe` requests a handle to `lsass.exe` with `GrantedAccess` `0x1410` or `0x1010`.
   - Sysmon Event 10 logs this critical access violation, providing defenders with the exact moment credentials were compromised.

## 6. Advanced Threat Hunting Queries (KQL)

### Detecting Suspicious LSASS Access (Event 10)
```kusto
SysmonEvent
| where EventID == 10
| where TargetImage endswith "lsass.exe"
// Filter out common false positives (requires tuning for your environment)
| where SourceImage !endswith "MsMpEng.exe" 
  and SourceImage !endswith "csrss.exe"
  and SourceImage !endswith "taskhostw.exe"
| project TimeGenerated, Computer, SourceImage, TargetImage, GrantedAccess, CallTrace
```

### Detecting LOLBin Network Connections (Event 1 + Event 3)
```kusto
SysmonEvent
| where EventID == 3
| where Image endswith "certutil.exe" 
     or Image endswith "regsvr32.exe" 
     or Image endswith "wmic.exe"
| where DestinationIp !in ("127.0.0.1", "::1") // Exclude loopback
| project TimeGenerated, Computer, Image, DestinationIp, DestinationPort, Protocol
```

## 7. Chaining Opportunities
- **[[01 - Windows Event Logs Deep Dive Event IDs 4624 4688]]**: Sysmon Event 1 enhances Event 4688 by adding hashes and parent command lines.
- **[[03 - Hunting for Process Injection and Hollowing]]**: Sysmon Event 8 is the primary telemetry source for detecting classic thread injection techniques.
- **[[04 - Hunting for Living off the Land Binaries LOLBAS]]**: Sysmon Event 1 (CommandLine) and Event 3 (Network) are critical for spotting LOLBin abuse.

## 8. Related Notes
- [[Windows Privilege Escalation Techniques]]
- [[Active Directory Lateral Movement]]
- [[05 - Detecting PowerShell Downgrade and Obfuscation]]
