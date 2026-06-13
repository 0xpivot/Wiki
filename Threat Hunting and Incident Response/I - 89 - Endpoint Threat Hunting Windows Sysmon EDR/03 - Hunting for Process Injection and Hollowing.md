---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.03 Hunting for Process Injection and Hollowing"
---

# Hunting for Process Injection and Hollowing

## 1. Introduction

Process Injection and Process Hollowing are advanced evasion techniques heavily utilized by malware authors, Advanced Persistent Threats (APTs), and offensive security tools (like Cobalt Strike and Metasploit). These techniques allow malicious code to execute within the memory space of a legitimate, trusted Windows process (e.g., `svchost.exe`, `explorer.exe`, or `notepad.exe`). 

By masquerading as a benign process, the attacker can evade process-level blocking, bypass firewall restrictions that only allow specific applications to communicate over the network, and obscure their execution from basic task managers. Hunting for these techniques requires a deep understanding of the Windows API, memory management, and specialized endpoint telemetry (like Sysmon or EDR ETWti feeds).

This note provides an in-depth breakdown of how these techniques function at the OS level, how they differ, and how threat hunters can systematically identify them.

## 2. Process Hollowing: The Mechanics

Process Hollowing (also known as RunPE) is a specific type of injection where an attacker creates a legitimate process in a suspended state, hollows out its memory, replaces the original code with a malicious payload, and then resumes the thread. 

### 2.1 The Windows API Call Sequence

The classic Process Hollowing attack relies on a very specific sequence of Windows API calls:

1. **`CreateProcess`**: The attacker calls this API to start a legitimate process (e.g., `C:\Windows\System32\svchost.exe`). Crucially, they pass the `CREATE_SUSPENDED` (0x00000004) flag. The OS allocates memory and creates the primary thread, but does not start executing instructions.
2. **`NtUnmapViewOfSection` / `ZwUnmapViewOfSection`**: The attacker uses this native API to "hollow out" the legitimate code from the process's memory space, leaving an empty shell.
3. **`VirtualAllocEx`**: The attacker allocates a new block of memory within the suspended process, ensuring the memory protections are set to `PAGE_EXECUTE_READWRITE` (RWX) or `PAGE_READWRITE` (followed by `PAGE_EXECUTE_READ` later to evade RWX detection).
4. **`WriteProcessMemory`**: The attacker writes their malicious payload (usually a PE file) into the newly allocated memory space.
5. **`GetThreadContext` & `SetThreadContext`**: The attacker retrieves the context of the suspended thread and modifies the instruction pointer (EIP/RIP) to point to the entry point of the injected malicious code.
6. **`ResumeThread`**: The attacker resumes the thread. The OS believes it is executing the legitimate `svchost.exe`, but it is actually executing the malware.

## 3. Classic Process Injection: The Mechanics

Unlike hollowing, standard Process Injection (like DLL Injection or PE Injection) typically targets a process that is *already running*. The attacker forces the running process to load a malicious DLL or execute an injected shellcode payload.

### 3.1 DLL Injection via CreateRemoteThread

This is the most common form of basic injection:
1. **`OpenProcess`**: The attacker gets a handle to a target process (e.g., `explorer.exe`) with `PROCESS_ALL_ACCESS` or `PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE`.
2. **`VirtualAllocEx`**: Memory is allocated in the target process.
3. **`WriteProcessMemory`**: The attacker writes the *path* to their malicious DLL (e.g., `C:\Temp\evil.dll`) into the allocated memory.
4. **`GetProcAddress` & `GetModuleHandle`**: The attacker finds the memory address of `LoadLibraryA` within `kernel32.dll`.
5. **`CreateRemoteThread`**: The attacker creates a new thread in the target process, pointing the starting address to `LoadLibraryA` and passing the allocated memory (containing the DLL path) as the argument. The target process is forced to load and execute the malicious DLL.

## 4. Visualizing the API Flow

```text
+---------------------+                      +-------------------------+
| Attacker Process    |                      | Target Legitimate Proc  |
| (e.g., dropper.exe) |                      | (e.g., svchost.exe)     |
+---------------------+                      +-------------------------+
          |                                               |
          | 1. CreateProcess(CREATE_SUSPENDED)            |
          |---------------------------------------------->| [Created, Suspended]
          |                                               |
          | 2. NtUnmapViewOfSection()                     |
          |---------------------------------------------->| [Memory Unmapped]
          |                                               |
          | 3. VirtualAllocEx(RWX)                        |
          |---------------------------------------------->| [Memory Allocated]
          |                                               |
          | 4. WriteProcessMemory(Payload)                |
          |---------------------------------------------->| [Payload Injected]
          |                                               |
          | 5. SetThreadContext(Point to Payload)         |
          |---------------------------------------------->| [EIP/RIP Modified]
          |                                               |
          | 6. ResumeThread()                             |
          |---------------------------------------------->| [Executing Malware!]
          |                                               |
+---------v-----------+                      +------------v------------+
```

## 5. Telemetry and Detection Strategies

Detecting injection and hollowing relies on identifying these specific API sequences, abnormal memory access, and anomalous process behaviors.

### 5.1 Sysmon Telemetry
Sysmon is highly effective at catching the symptoms of injection.
- **Event ID 8 (CreateRemoteThread)**: This event is triggered directly by the `CreateRemoteThread` API used in classic DLL injection.
    - *Detection Logic*: Look for remote threads created into critical system processes (`lsass.exe`, `explorer.exe`, `svchost.exe`, `winlogon.exe`) originating from unexpected source images (e.g., PowerShell, Word, or binaries in Temp directories).
- **Event ID 10 (ProcessAccess)**: Triggered by `OpenProcess`.
    - *Detection Logic*: Look for processes requesting `GrantedAccess` masks like `0x1FFFFF` (PROCESS_ALL_ACCESS) or `0x103A` (PROCESS_CREATE_THREAD, PROCESS_VM_OPERATION, PROCESS_VM_WRITE) to other processes, especially if the source is an Office application or a scripting engine.

### 5.2 EDR and ETWti (Event Tracing for Windows Threat Intelligence)
Modern EDRs hook user-land APIs (like `ntdll.dll`) or consume Microsoft's ETWti feed from the kernel to monitor memory allocations directly.
- **Detecting RWX Memory**: Threat hunters should alert on `VirtualAlloc` or `NtAllocateVirtualMemory` calls that request `PAGE_EXECUTE_READWRITE` (RWX) permissions, as this is rarely used by legitimate applications but is essential for shellcode execution.
- **Unbacked Memory Regions**: A massive indicator of injection is a thread executing from a memory region that is *not backed by a file on disk*. Legitimate code runs from mapped `.dll` or `.exe` files. Injected shellcode runs from dynamically allocated heap memory. EDRs flag this as "Execution from Unbacked Memory."

## 6. Real-World Attack Scenario

### Trickbot Banking Trojan Using Process Hollowing
A user downloads a malicious PDF that executes an embedded JavaScript, dropping a Trickbot executable into `C:\Users\Public\update.exe`.

1. **Initial Execution**: The user clicks the fake update. `update.exe` starts.
2. **Hollowing Phase**: `update.exe` calls `CreateProcess` to launch `C:\Windows\System32\wermgr.exe` (Windows Error Reporting) in a suspended state. 
3. **Injection**: The malware unmaps the legitimate `wermgr.exe` code, allocates memory, and writes the core Trickbot payload into the suspended process.
4. **Resumption**: Trickbot calls `ResumeThread`. `update.exe` terminates itself to hide its tracks.
5. **Execution**: The system task manager shows `wermgr.exe` running perfectly normally. However, this `wermgr.exe` process is now establishing a C2 connection to a Russian IP address (visible in Sysmon Event 3) and attempting to hook browser processes to steal banking credentials.

*Hunting Catch*: A defender reviewing Sysmon Event 1 sees `update.exe` spawning `wermgr.exe`. This is highly anomalous; `wermgr.exe` is normally spawned by the system, not random user-space binaries. Furthermore, an EDR memory scan flags `wermgr.exe` for containing an unbacked RWX memory region.

## 7. Advanced Hunting Queries

### KQL: Sysmon Event 8 (Remote Thread Creation)
```kusto
SysmonEvent
| where EventID == 8
| where TargetImage in~ ("C:\\Windows\\System32\\explorer.exe", 
                         "C:\\Windows\\System32\\svchost.exe",
                         "C:\\Windows\\System32\\lsass.exe")
// Exclude known legitimate injectors like EDR agents or debuggers
| where SourceImage !endswith "MsMpEng.exe" 
  and SourceImage !endswith "Sysmon64.exe"
| project TimeGenerated, Computer, SourceImage, TargetImage, StartAddress
```

### Volatility Memory Forensics (Post-Incident)
If an endpoint is suspected of containing injected processes, threat hunters can capture a RAM image and use Volatility:
- `vol.py -f memory.raw windows.malfind`: Scans for hidden/injected code by looking for memory segments marked with `PAGE_EXECUTE_READWRITE` (RWX) that do not map to a file on disk. The output includes a hex dump of the suspicious memory, often revealing a hidden PE header (`MZ`).
- `vol.py -f memory.raw windows.hollowfind`: Specifically designed to detect process hollowing by analyzing VAD (Virtual Address Descriptor) inconsistencies, process path discrepancies, and suspended threads.

## 8. Mitigation and Hardening

1. **Attack Surface Reduction (ASR) Rules**: Implement Windows Defender ASR rules, specifically: "Block credential stealing from the Windows local security authority subsystem (lsass.exe)" and "Block Office applications from injecting code into other processes."
2. **EDR Deployment**: Legacy Antivirus relying on file signatures cannot stop memory injection. A behavioral EDR capable of consuming ETWti and analyzing memory allocations is mandatory.
3. **Exploit Guard**: Enable Windows Defender Exploit Guard features like Arbitrary Code Guard (ACG), which prevents processes from dynamically generating code or modifying executable memory pages.

## 9. Chaining Opportunities
- **[[02 - Microsoft Sysmon Configuration and Telemetry]]**: Directly ties into Event IDs 8 and 10 for telemetry generation.
- **[[04 - Hunting for Living off the Land Binaries LOLBAS]]**: LOLBins like `msbuild.exe` or `installutil.exe` are frequently targets for hollowing or injection to proxy execution.
- **[[01 - Windows Event Logs Deep Dive Event IDs 4624 4688]]**: Event 4688 will show the `CreateProcess` (Suspended) event, providing the initial parent-child anomaly indicator.

## 10. Related Notes
- [[Windows APIs for Red Teaming]]
- [[Memory Forensics with Volatility]]
- [[Cobalt Strike Malleable C2 Profiles]]
