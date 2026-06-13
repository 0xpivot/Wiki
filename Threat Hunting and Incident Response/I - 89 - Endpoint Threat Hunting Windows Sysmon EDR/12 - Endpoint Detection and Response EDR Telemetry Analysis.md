---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.12 Endpoint Detection and Response EDR Telemetry Analysis"
---

# 89.12 Endpoint Detection and Response EDR Telemetry Analysis

## Introduction to EDR and Telemetry Collection

Endpoint Detection and Response (EDR) solutions are the cornerstone of modern defensive architectures. Unlike legacy Antivirus (AV), which relies heavily on static file signatures and heuristics, EDR systems operate on behavior-based telemetry. They continuously record endpoint activities—process executions, memory manipulations, network connections, file system modifications, and registry changes—streaming this data to a centralized data lake for real-time analysis, anomaly detection, and historical threat hunting.

To achieve deep visibility, EDRs must integrate tightly into the operating system. In Windows environments, EDRs leverage a combination of Kernel Callbacks, Event Tracing for Windows (ETW), and User-Mode API Hooking to monitor system behavior. Understanding how EDRs collect this data is crucial for threat hunters to interpret telemetry accurately and for red teamers/attackers to understand how evasive techniques (like unhooking or direct syscalls) operate.

### Mechanisms of Telemetry Collection

1. **Kernel Callbacks (Minifilter Drivers):** EDRs install kernel-mode drivers to intercept critical system events. Microsoft provides APIs (e.g., `PsSetCreateProcessNotifyRoutine`, `CmRegisterCallback`) that allow security products to be notified synchronously when a process is created, a thread is spawned, or a registry key is modified. Because these operate in ring-0 (kernel mode), they are difficult for user-mode malware to evade or tamper with directly.
2. **Event Tracing for Windows (ETW):** ETW is a high-performance, low-overhead logging mechanism built into Windows. EDRs often subscribe to specific ETW providers (like `Microsoft-Windows-Threat-Intelligence` or `Microsoft-Windows-Kernel-Process`) to gather granular telemetry without the overhead of heavy hooking. ETW provides deep insights into network activity, file operations, and even .NET assembly loading.
3. **User-Mode API Hooking:** This is the most common technique for monitoring in-memory behavior and complex user-mode interactions. The EDR injects a DLL (e.g., `cybkernel.dll`, `atc.dll`, `umppc.dll`) into every new user-mode process. This DLL overwrites the first few instructions of critical Windows API functions (like `VirtualAlloc`, `CreateRemoteThread`, `WriteProcessMemory`) in `ntdll.dll` or `kernel32.dll` with a `JMP` instruction. This redirects execution to the EDR's inspection engine before the actual system call is made.

## ASCII Diagram: EDR User-Mode Hooking Architecture

The diagram below illustrates how an EDR intercepts API calls using inline hooking. When an application calls a function like `NtAllocateVirtualMemory`, execution is diverted to the EDR's injected DLL, which logs the request and evaluates its maliciousness before passing control to the kernel.

```text
+-----------------------------------------------------------------------------------+
|                        EDR User-Mode API Hooking Flow                             |
+-----------------------------------------------------------------------------------+

     [User Application]
             |
             | 1. Calls VirtualAlloc()
             v
     +-------------------+
     |   kernel32.dll    |
     |   VirtualAlloc()  | ---> Translates to NtAllocateVirtualMemory
     +-------------------+
             |
             | 2. Calls NtAllocateVirtualMemory in ntdll.dll
             v
     +-------------------+        3. EDR JMP Instruction (The Hook)
     |    ntdll.dll      | -------------------------------------------+
     |                   |                                            |
     | 0x00 JMP <EDR>    | <--- Overwritten by EDR injected DLL       |
     | 0x05 ...          |                                            v
     | 0x0A syscall      |                                 +---------------------+
     | 0x0C ret          |                                 |   EDR Sensor DLL    |
     +-------------------+                                 |   (Injected)        |
             ^                                             |                     |
             |                                             | - Inspects args     |
             | 5. If benign, EDR executes original inst.   | - Logs telemetry    |
             +-------------------------------------------- | - Blocks if evil    |
                                                           +---------------------+
                                                                      |
                                                                      | 4. Telemetry sent
                                                                      v
                                                           [Centralized EDR Console]

             | 6. Execution proceeds to kernel
             v
     +-------------------+
     |    Kernel (Ring 0)| ---> Memory is allocated.
     +-------------------+
```

## Analyzing Core EDR Telemetry Categories

When hunting through EDR data, analysts typically focus on several key categories of telemetry. A deep understanding of what normal looks like in these categories is essential for spotting anomalies.

### 1. Process and Thread Execution
Process trees are the foundation of endpoint hunting. Telemetry usually includes:
- **Process ID (PID) / Parent PID (PPID):** Establishing the hierarchy.
- **Image Path & Command Line:** The exact location of the executable and the arguments passed.
- **Hashes:** MD5, SHA-1, SHA-256 for reputation lookups.
- **User Context:** Which account initiated the process.
- **Thread Injection:** Events where one process creates a thread in another process (e.g., `CreateRemoteThread`).

**Hunting Focus:** Look for anomalous parent-child relationships. For example, `winword.exe` spawning `cmd.exe` or `powershell.exe` is highly indicative of macro-based attacks. Look for instances of living-off-the-land binaries (LOLBins) like `certutil.exe` or `rundll32.exe` executing with unusual network arguments or executing from `C:\Users\Public`.

### 2. File System Modifications
EDRs track file creations, modifications, and deletions. 
- **File Path:** Where the file is located.
- **Extensions:** Changes to extensions (e.g., `.docx` to `.encrypted`).
- **File Attributes:** Hidden flags or system attributes.

**Hunting Focus:** Mass file modifications (indicative of ransomware). Executables being dropped into high-risk directories like `AppData\Local\Temp`, `C:\ProgramData`, or `C:\Users\Public`. Creation of files with unusual extensions or double extensions (e.g., `invoice.pdf.exe`).

### 3. Network Connections
Telemetry covering network interactions initiated by processes.
- **Source/Destination IP and Port:** Who is talking to whom.
- **Protocol:** TCP, UDP.
- **Process attribution:** Which specific PID initiated the connection.

**Hunting Focus:** Native Windows processes (that shouldn't communicate externally) initiating outbound connections. For example, `notepad.exe` or `svchost.exe` (without standard arguments) connecting to external IPs over port 4444 or 8080. High volumes of data egressing from unexpected processes.

### 4. Registry Activity
Modifications to the Windows Registry.
- **Target Key and Value:** The exact location being modified.
- **Action:** Create, Set, Delete.

**Hunting Focus:** Modifications to ASEP (Auto-Start Extensibility Points) such as `Run` and `RunOnce` keys. Changes to security configuration keys, such as disabling Windows Defender (`DisableAntiSpyware`), modifying UAC settings, or creating unusual services.

### 5. Cross-Process Access and Memory Manipulation
This is where EDRs shine compared to traditional logging.
- **Process Access:** When one process opens a handle to another with specific access rights (e.g., `PROCESS_ALL_ACCESS`, `PROCESS_VM_READ`).
- **Memory Allocation/Writing:** `VirtualAllocEx` or `WriteProcessMemory` events indicating code injection.

**Hunting Focus:** Standard processes opening handles to `lsass.exe` requesting `PROCESS_VM_READ` (indicative of credential dumping). An unknown binary allocating memory and injecting code into `explorer.exe` or `svchost.exe` (Process Injection/Hollowing).

## Real-World Attack Scenario

### The Incident
An alert was triggered in the EDR console indicating that a process named `spoolsv.exe` was making an outbound network connection to a known Tor exit node IP address.

### The Attack Progression and Telemetry Analysis
The threat hunting team pivoted on the initial alert and analyzed the historical telemetry for the affected endpoint.

1. **Initial Access:** The team searched backward in the process tree. They found that 3 hours prior, `msedge.exe` downloaded a file named `update_installer.zip`.
2. **Execution:** The user extracted the ZIP, yielding `installer.js`. The user double-clicked the JavaScript file, causing `wscript.exe` to execute it.
   - *Telemetry observed:* `wscript.exe` running with the command line `wscript.exe C:\Users\jdoe\Downloads\installer.js`.
3. **Persistence and Evasion:** The JavaScript file contained an obfuscated payload. It utilized WMI to spawn a new, hidden PowerShell process.
   - *Telemetry observed:* `wmiapsrv.exe` spawning `powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand <base64>`.
4. **Process Injection:** The PowerShell script downloaded a reflective DLL payload and injected it into a legitimate running instance of the Print Spooler service (`spoolsv.exe`) to mask its C2 communication.
   - *Telemetry observed:* EDR captured an `OpenProcess` event where `powershell.exe` requested `PROCESS_ALL_ACCESS` rights to `spoolsv.exe`. Following this, EDR captured a `WriteProcessMemory` and `CreateRemoteThread` event targeting the `spoolsv.exe` PID.
5. **C2 Communication:** The injected payload within `spoolsv.exe` established a persistent connection back to the attacker's infrastructure.
   - *Telemetry observed:* `spoolsv.exe` initiating a TCP connection to `192.0.2.55:443`.

### The Hunt and Remediation
The entire attack lifecycle was reconstructed purely from EDR telemetry. Because the EDR monitored cross-process access, the team could link the initial `wscript.exe` execution directly to the compromised `spoolsv.exe` process, despite the attacker's attempt to use process injection for stealth. The host was immediately isolated via the EDR network containment feature. The malicious `installer.js` was purged, the malicious scheduled tasks created for persistence were removed, and the associated IP addresses were added to the corporate blocklist.

## EDR Evasion Techniques and Blind Spots

Threat hunters must acknowledge that EDRs are not infallible. Sophisticated adversaries continually develop methods to blind or bypass EDR telemetry.
- **User-Mode Unhooking:** Malware can read a clean copy of `ntdll.dll` from disk and overwrite the EDR's inline hooks in memory, effectively blinding the user-mode telemetry engine.
- **Direct System Calls (Syscalls):** Instead of calling functions in `ntdll.dll` (which are hooked), malware can implement the system calls directly in assembly language. The execution jumps straight to the kernel, completely bypassing the EDR's user-mode hooks.
- **Bring Your Own Vulnerable Driver (BYOVD):** Attackers load a legitimately signed, but vulnerable, kernel driver. They exploit the driver to gain ring-0 execution, allowing them to disable EDR kernel callbacks or terminate EDR protected processes from the kernel level.
- **ETW Patching:** Attackers can patch functions like `EtwEventWrite` in memory, preventing the process from sending ETW telemetry to the EDR.

Hunting for these evasion techniques involves looking for anomalies such as unsigned drivers being loaded, unexpected crashes of EDR components, or suspicious processes that generate process creation events but exhibit absolutely no API telemetry.

## Chaining Opportunities
- **Initial Access -> EDR Evasion:** Modern payloads often execute an unhooking routine immediately upon execution to ensure subsequent actions (like process injection or credential dumping) go unnoticed.
- **Defense Evasion -> Credential Access:** Disabling or blinding the EDR is almost always a precursor to targeting highly monitored processes like LSASS.
- **Persistence -> C2:** Attackers inject their C2 beacons into long-running, legitimate processes (like `explorer.exe` or `svchost.exe`) to maintain a stealthy connection without triggering anomalous network telemetry alerts.

## Related Notes
- [[11 - Hunting for UAC Bypasses]]
- [[13 - Hunting for Fileless Malware and In-Memory Execution]]
- [[14 - Analyzing Windows Prefetch Amcache and Shimcache]]
- [[04 - Living Off The Land Binaries (LOLBins)]]
- [[07 - Memory Forensics and Volatility]]
