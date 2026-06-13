---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.01 Modern EDR Architecture and Detection Mechanisms"
---

# 01 - Modern EDR Architecture and Detection Mechanisms

## 1. Introduction and Scope
Endpoint Detection and Response (EDR) solutions have fundamentally shifted the paradigm of endpoint security. Unlike legacy Antivirus (AV) that relied predominantly on static file signatures, modern EDRs are complex, multi-layered telemetry gathering and analysis engines. As Red Teamers, understanding the exact anatomical structure of these defensive systems is the first critical step in designing evasive Command and Control (C2) architectures. 

This document explores the architectural design of modern EDRs, diving deep into both user-mode and kernel-mode components, telemetry pipelines, and heuristic decision engines. Understanding the source of the telemetry allows us to blind, bypass, or spoof the data before it reaches the analysis engine.

## 2. Core Architectural Components

Modern EDR platforms operate across several privilege boundaries to ensure deep visibility and self-protection.

### 2.1 User-Mode Components (Ring 3)
In user-mode, EDRs inject dynamic link libraries (DLLs) into all running processes. This is typically achieved via `AppInit_DLLs`, Image File Execution Options (IFEO), or more commonly, through kernel-mode callbacks that notify the EDR when a new process is created (e.g., `PsSetCreateProcessNotifyRoutine`).
*   **API Hooking:** The EDR's injected DLL intercepts critical Windows APIs (like `VirtualAlloc`, `CreateRemoteThread`, `WriteProcessMemory`) by modifying the first few bytes of the function in memory (usually in `ntdll.dll` or `kernel32.dll`) to place a `JMP` instruction pointing to the EDR's inspection routine.
*   **AMSI (Anti-Malware Scan Interface):** A built-in Windows standard interface that allows applications (like PowerShell, VBScript, .NET) to pass memory buffers to the installed security product for scanning before execution.
*   **ETW (Event Tracing for Windows):** EDRs heavily consume ETW feeds, specifically `Microsoft-Windows-Threat-Intelligence` (ETW-TI), which provides insight into API calls, memory allocations, and RPC activity.

### 2.2 Kernel-Mode Components (Ring 0)
The kernel-mode driver is the brain and shield of the EDR. It operates at the highest privilege level, making it difficult for user-mode malware to tamper with it.
*   **Kernel Callbacks:** Utilizing the Windows Kernel API, the EDR registers callbacks such as:
    *   `PsSetCreateProcessNotifyRoutineEx`: Process creation/termination.
    *   `PsSetCreateThreadNotifyRoutine`: Thread creation (vital for detecting remote thread injection).
    *   `ObRegisterCallbacks`: Protecting its own processes, files, and registry keys from termination or modification by malware.
    *   `CmRegisterCallbackEx`: Registry monitoring.
*   **Minifilter Drivers:** Used to intercept file system I/O operations. Every read, write, or execute operation on the disk passes through the EDR's minifilter, allowing for real-time scanning of executables before they are mapped into memory.
*   **ELAM (Early Launch Anti-Malware):** A Microsoft standard that allows the EDR driver to load before any third-party drivers or applications, ensuring the EDR is active before the OS finishes booting and before persistent malware can execute.

## 3. Visualizing the EDR Architecture

```ascii
+-----------------------------------------------------------------------------------+
|                                 CLOUD INFRASTRUCTURE                              |
|   +-----------------------+     +-----------------------+                         |
|   |   Threat Intel Feed   |     | Machine Learning Model|                         |
|   +-----------------------+     +-----------------------+                         |
|              ^                             ^                                      |
+--------------|-----------------------------|--------------------------------------+
               |                             | (Telemetry Upload & Conviction)
               v                             v
+-----------------------------------------------------------------------------------+
|                                 ENDPOINT (USERLAND - Ring 3)                      |
|                                                                                   |
|  +-------------------------+      +-------------------------+                     |
|  |   Benign Process.exe    |      |    Malicious.exe        |                     |
|  |                         |      |                         |                     |
|  | [ntdll.dll (Hooked)]<---|------|--->[ntdll.dll (Hooked)] |                     |
|  | [EDR_Sensor.dll]        |      |    [EDR_Sensor.dll]     |                     |
|  +-------------------------+      +-------------------------+                     |
|              |                             | (API Calls / AMSI / ETW)             |
+--------------|-----------------------------|--------------------------------------+
               |                             |
               v                             v
+-----------------------------------------------------------------------------------+
|                                 ENDPOINT (KERNEL - Ring 0)                        |
|                                                                                   |
|  +-------------------------------------------------------------+                  |
|  |                    EDR KERNEL DRIVER (.sys)                 |                  |
|  |                                                             |                  |
|  |  +-----------------+  +-----------------+  +-------------+  |                  |
|  |  | Process Notify  |  |  Thread Notify  |  | Minifilter  |  |                  |
|  |  +-----------------+  +-----------------+  +-------------+  |                  |
|  |                                                             |                  |
|  |            [ ETW-TI Telemetry Consumer ]                    |                  |
|  +-------------------------------------------------------------+                  |
+-----------------------------------------------------------------------------------+
```

## 4. Detection Pipelines

When an executable runs, the EDR processes it through a multi-stage pipeline:

1.  **Pre-Execution (Static Analysis):** The minifilter driver intercepts the file creation/execution. The file is hashed and checked against Cloud Threat Intel. Static properties (Entropy, PE headers, imports, YARA signatures) are analyzed.
2.  **In-Memory Analysis (AMSI & Emulation):** If the file is a script or a known container (.NET, Office Macro), AMSI buffers are scanned. The EDR may momentarily suspend execution and emulate the first few thousand instructions in a lightweight sandbox.
3.  **Post-Execution (Behavioral & Heuristic):** As the process runs, userland hooks and kernel callbacks feed telemetry to the local EDR service. The service builds a process tree and behavior graph.
    *   *Example:* Process `A` allocates executable memory in Process `B`, writes data, and creates a remote thread. This exact sequence triggers a classic "Process Injection" heuristic.
4.  **Cloud Analysis:** Suspicious metadata, unknown hashes, and complex behavioral graphs are sent to the EDR vendor's cloud for heavyweight Machine Learning (ML) analysis and correlation across the global fleet.

## 5. Real-World Attack Scenario

### The Scenario: APT29 and EDR Blind Spots
Advanced Persistent Threats (APTs) often target the telemetry collection mechanisms rather than the analysis engine itself. In a modern intrusion, an attacker might compromise an endpoint but find it heavily monitored by an aggressive EDR.

Instead of deploying their primary C2 implant directly, the attacker drops a lightweight reconnaissance tool. This tool enumerates the loaded modules in its own process space and identifies the EDR's userland hook DLL (e.g., `amsi.dll`, `CylanceMemDef64.dll`). 

Knowing that the EDR relies on these hooks to monitor `ntdll.dll` API calls, the attacker's loader uses a technique like "Unhooking" or "Direct Syscalls" (covered in subsequent modules) to bypass the userland telemetry. The loader then injects the primary C2 payload into a benign process using APIs that the EDR is now blind to. Because the kernel-mode callbacks still see thread creation, the attacker spoof the thread's start address to point to a legitimate Windows DLL function, defeating the kernel telemetry and blending into normal system noise.

## 6. Defensive Mitigations

From a defensive perspective, relying solely on userland hooks is increasingly insufficient against modern malware. Defenses should focus on:
1.  **Kernel-level Telemetry:** Prioritizing ETW-TI and kernel callbacks over user-mode hooking. EDRs should validate call stacks originating from suspicious memory regions.
2.  **Memory Scanning:** Periodically scanning the memory of running processes for anomalous executable pages (e.g., `PAGE_EXECUTE_READWRITE` without a backing file on disk), regardless of how the memory was allocated.
3.  **Hardware-Assisted Telemetry:** Leveraging Intel TDT (Threat Detection Technology) or similar hardware-level heuristics to detect anomalous execution patterns that software cannot easily spoof.

## 7. Chaining Opportunities

Understanding the architecture is purely foundational. To successfully evade the EDR, you must chain specific bypasses targeting each telemetry pipeline:
*   Bypass the Pre-Execution phase via [[02 - Bypassing Static Signatures and YARA]].
*   Bypass the Post-Execution/Behavioral phase via [[03 - Bypassing Heuristics and Behavioral Analysis]].
*   Blind the User-Mode API Hooks via [[04 - Unhooking Userland APIs EDR Bypass]].

## 8. Related Notes

*   [[99.02 - Bypassing Static Signatures and YARA]]
*   [[99.03 - Bypassing Heuristics and Behavioral Analysis]]
*   [[Windows Kernel Internals]]
*   [[Event Tracing for Windows (ETW) Fundamentals]]
*   [[AMSI Architecture and Bypass Techniques]]
