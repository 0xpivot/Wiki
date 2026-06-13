---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.06 Process Hollowing and Injection OPSEC"
---

# Process Hollowing and Injection OPSEC

## 1. Introduction

Process Hollowing and Process Injection are foundational techniques utilized by advanced threat actors and penetration testers to execute arbitrary code within the address space of a separate, legitimate process. 

This technique serves multiple purposes: it helps evade detection by hiding malicious activity behind trusted processes, it can bypass host-based firewalls that trust specific applications (like web browsers), and it provides access to the target process's memory space for credential theft or data manipulation.

This educational document explores the mechanics of process hollowing, the operational security (OPSEC) challenges it presents, and how defenders can detect and mitigate these techniques using modern Endpoint Detection and Response (EDR) solutions.

## 2. Theoretical Background and Mechanics

Process Injection encompasses a wide array of methods where an attacker forces a legitimate process to execute malicious code. Process Hollowing (sometimes referred to as RunPE) is a specific variant of injection.

In a traditional process hollowing attack, a legitimate executable is started in a suspended state. Its memory is unmapped (hollowed out) and replaced with a malicious payload before execution is resumed. This causes the operating system to view the process as the legitimate executable, while the code actually running is controlled by the attacker.

### 2.1 The Classic Process Hollowing Workflow

1.  **Process Creation:** The malware creates a target legitimate process in a suspended state using the `CreateProcess` API with the `CREATE_SUSPENDED` flag.
    
2.  **Memory Unmapping:** The primary image of the new process is unmapped from memory using the undocumented `NtUnmapViewOfSection` API.
    
3.  **Memory Allocation:** New memory is allocated in the suspended process using `VirtualAllocEx` with `PAGE_EXECUTE_READWRITE` permissions.
    
4.  **Payload Writing:** The malicious payload is written into the newly allocated memory space using `WriteProcessMemory`.
    
5.  **Context Manipulation:** The thread context is modified using `SetThreadContext` to point the entry point (e.g., EAX or RCX register) to the malicious payload.
    
6.  **Thread Resumption:** The primary thread is resumed using `ResumeThread`, executing the payload within the context of the legitimate process.

## 3. Deep Dive into Advanced OPSEC Considerations

From an operational security perspective, traditional process hollowing is highly scrutinized and easily detected by modern EDRs.

### 3.1 The Flaws of Traditional Hollowing

-   **Suspicious API Sequences:** The sequence of `CreateProcess` -> `NtUnmapViewOfSection` -> `WriteProcessMemory` -> `ResumeThread` is a massive indicator of compromise (IoC). EDRs aggressively hook these APIs.
    
-   **Unbacked Executable Memory:** Executing code from memory regions that are not backed by a physical file on disk (unbacked memory) is highly anomalous and easily caught by memory scanners.
    
-   **RWX Memory:** `PAGE_EXECUTE_READWRITE` (RWX) allocations are rare in normal application behavior and are closely monitored.
    
### 3.2 Modern Evasion Adaptations

To counter EDR detection, modern implementations utilize refined tradecraft:

-   **Module Stomping (Module Overloading):** Instead of allocating unbacked memory, an attacker forces the target process to load a legitimate DLL. The attacker then overwrites the `.text` section of this legitimate DLL with their malicious payload. This ensures the executable memory region is backed by a file on disk.
    
-   **Direct Syscalls:** Attackers bypass user-mode API hooking (e.g., hooks placed in `ntdll.dll` by EDRs) by executing system calls directly to the kernel, masking the use of injection-related APIs.
    
-   **Thread Execution Hijacking:** Suspending an existing thread in a remote process, modifying its instruction pointer to point to shellcode, and resuming it, avoiding the anomalous `CreateProcess` step.

## 4. ASCII Architecture Diagram: Process Hollowing

```text
+-----------------------------------------------------------------------+
|                       ATTACKER PROCESS                                |
+-----------------------------------------------------------------------+
|  1. CreateProcess(CREATE_SUSPENDED)                                   |
|       |                                                               |
|       v                                                               |
|  +-----------------------------------------------------------------+  |
|  |                    TARGET PROCESS (Suspended)                   |  |
|  +-----------------------------------------------------------------+  |
|  |                                                                 |  |
|  |  [Original Legitimate Image (e.g., svchost.exe)]                |  |
|  |                                                                 |  |
|  +-----------------------------------------------------------------+  |
|       |                                                               |
|  2. NtUnmapViewOfSection()                                            |
|       |                                                               |
|       v                                                               |
|  +-----------------------------------------------------------------+  |
|  |                    TARGET PROCESS (Hollowed)                    |  |
|  +-----------------------------------------------------------------+  |
|  |                                                                 |  |
|  |  [Empty Memory Space]                                           |  |
|  |                                                                 |  |
|  +-----------------------------------------------------------------+  |
|       |                                                               |
|  3. VirtualAllocEx(PAGE_EXECUTE_READWRITE)                            |
|  4. WriteProcessMemory(Malicious Payload)                             |
|       |                                                               |
|       v                                                               |
|  +-----------------------------------------------------------------+  |
|  |                    TARGET PROCESS (Injected)                    |  |
|  +-----------------------------------------------------------------+  |
|  |                                                                 |  |
|  |  [Malicious Payload Code]                                       |  |
|  |                                                                 |  |
|  +-----------------------------------------------------------------+  |
|       |                                                               |
|  5. SetThreadContext(Entry Point -> Payload)                          |
|  6. ResumeThread()                                                    |
|       |                                                               |
|       v                                                               |
|  [ MALICIOUS CODE EXECUTES AS LEGITIMATE PROCESS ]                    |
+-----------------------------------------------------------------------+
```

## 5. Real-World Attack Scenario

In a real-world scenario, a threat actor gains initial access via an Office macro embedded in a phishing email.

1.  **Initial Execution:** The user enables macros, executing the attacker's VBA code.
    
2.  **Defense Evasion:** The macro uses Direct Syscalls to evade user-mode EDR hooks, loading the actual shellcode runner.
    
3.  **Process Creation:** The runner launches `svchost.exe` in a suspended state.
    
4.  **Injection:** It maps a new view of sections to avoid the heavily monitored `WriteProcessMemory` API, injecting a Command and Control (C2) beacon.
    
5.  **Execution:** It sets the thread context and resumes the thread.
    
6.  **Impact:** The C2 beacon now runs inside `svchost.exe`. Because `svchost.exe` normally communicates over the network, the beacon's outbound HTTP/S traffic blends in with normal system network activity, evading network-level anomalies.

## 6. Defender's Perspective and Telemetry

Defenders rely on multiple telemetry sources and analytical techniques to detect process injection and hollowing.

### 6.1 Process Creation Anomalies

-   **Suspended Processes:** Legitimate processes rarely start in a suspended state. Monitoring for `CreateProcess` with `CREATE_SUSPENDED` followed by remote thread manipulation is a critical detection analytic.
    
-   **Parent-Child Relationships:** `svchost.exe` spawning from `winword.exe`, `powershell.exe`, or an unknown binary is highly anomalous and easily flagged.
    
### 6.2 Memory Scanning and Analysis

-   **Unbacked Executable Memory:** Memory scanners periodically check processes for `PAGE_EXECUTE_READ` or `PAGE_EXECUTE_READWRITE` memory regions that do not map to a loaded file on disk.
    
-   **PE Header Anomalies:** Finding MZ/PE headers in unusual memory locations, or detecting that the in-memory PE header differs significantly from the corresponding on-disk file, indicates hollowing or module stomping.
    
### 6.3 API Monitoring and Event Tracing

-   **User-Mode Hooking:** EDRs inject DLLs into user processes to hook APIs like `NtWriteVirtualMemory`, `NtCreateThreadEx`, and `NtProtectVirtualMemory`, inspecting the arguments in real-time.
    
-   **Event Tracing for Windows (ETW):** ETW provides deep visibility.
    -   *Event ID 8 (Sysmon):* `CreateRemoteThread` detects when a process creates a thread in another process.
    -   *Event ID 10 (Sysmon):* `ProcessAccess` detects when a process opens a handle to another process with invasive access rights (e.g., `PROCESS_VM_WRITE`).

## 7. Mitigation and Remediation Strategies

Defending against process injection requires a defense-in-depth approach.

1.  **Endpoint Detection and Response (EDR):** Deploy and properly configure modern EDR solutions capable of kernel-level telemetry collection and periodic memory scanning.
    
2.  **Attack Surface Reduction (ASR):** Implement ASR rules to block Office applications and other vulnerable software from creating child processes.
    
3.  **Application Control:** Utilize solutions like Windows Defender Application Control (WDAC) or AppLocker to strictly control which binaries are allowed to execute, limiting the pool of potential "hollowable" targets.
    
4.  **Network Segmentation and Egress Filtering:** Restrict outbound network access for processes that do not require it, limiting the effectiveness of injected C2 beacons.
    
5.  **Behavioral Analytics:** Baseline normal process behavior and alert on deviations, such as a process making unexpected network connections or writing to sensitive registry keys.

## 8. Chaining Opportunities

Process hollowing is rarely utilized as an isolated technique. Advanced threat actors chain it with other methods to maximize operational security and stealth.

-   Chaining with [[08 - PPID Spoofing and Command Line Obfuscation]] to disguise the true parent of the hollowed process, making the process tree appear benign.
    
-   Utilizing [[09 - ETW Event Tracing for Windows Patching]] to blind the EDR's telemetry before performing the injection, preventing the event logs from being generated.
    
-   Leveraging [[10 - AMSI Antimalware Scan Interface Bypass Techniques]] if the initial injection vector is script-based (e.g., PowerShell or JScript) to prevent the script content from being scanned.
    
-   Implementing [[07 - Thread Stack Spoofing and Call Stack Evasion]] within the injected payload to hide the true origin of the thread execution when the C2 beacon is sleeping.

## 9. Summary

Process hollowing remains a potent technique in the attacker's arsenal. While traditional methods are easily detected by modern security tooling, the continuous evolution of injection techniques—such as module stomping and direct syscalls—requires defenders to maintain a deep understanding of Windows internals and employ advanced memory analysis and behavioral monitoring to protect their environments.

## 10. Related Notes

-   [[07 - Thread Stack Spoofing and Call Stack Evasion]]
-   [[08 - PPID Spoofing and Command Line Obfuscation]]
-   [[09 - ETW Event Tracing for Windows Patching]]
-   [[10 - AMSI Antimalware Scan Interface Bypass Techniques]]
-   [[11 - Direct and Indirect Syscalls]]

***
*Disclaimer: This material is intended strictly for educational and defensive purposes. Understanding these techniques is critical for developing robust detection engineering, incident response capabilities, and securing enterprise networks.*
