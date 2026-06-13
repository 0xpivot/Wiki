---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.09 ETW Event Tracing for Windows Patching"
---

# ETW Event Tracing for Windows Patching

## 1. Introduction

Event Tracing for Windows (ETW) is a high-performance, low-overhead kernel-level tracing facility provided by the Windows operating system. It is the backbone of modern Windows telemetry, heavily relied upon by Endpoint Detection and Response (EDR) agents, Sysmon, and Windows Event Logs to gain deep visibility into system activity.

Because ETW provides such granular insight into process creation, memory allocation, API calls, and network connections, it represents a significant obstacle for threat actors. To operate stealthily, advanced attackers utilize ETW Patching—a technique designed to dynamically disable ETW logging from within a compromised process, effectively blinding the EDR.

This educational document explores the ETW architecture, how memory patching disrupts it, and how defenders can detect this tampering.

## 2. ETW Architecture Overview

ETW is built on a publish-subscribe model consisting of three main components:

1.  **Providers:** Applications or kernel components that generate events. (e.g., `Microsoft-Windows-Kernel-Process`, `.NET Common Language Runtime`).
2.  **Controllers:** Applications that configure and manage ETW sessions, turning providers on or off.
3.  **Consumers:** Applications that subscribe to ETW sessions to read and analyze the events (e.g., EDR agents, Event Viewer).

### 2.1 The Event Generation Flow

When an application wants to log an event, it typically calls the `EtwEventWrite` or `EtwEventWriteFull` functions exported by `ntdll.dll`. These functions then transition to the kernel to hand the event data to the ETW subsystem for distribution to consumers.

## 3. Deep Dive into ETW Patching Mechanics

ETW Patching (also known as ETW blinding) targets the `EtwEventWrite` function within the memory space of the attacker-controlled process.

Since `ntdll.dll` is loaded into every user-mode process, an attacker who has code execution within a process can modify the `ntdll.dll` memory resident in that specific process.

### 3.1 The Patching Process

1.  **Resolve Function Address:** The malware uses `GetModuleHandle` and `GetProcAddress` to find the memory address of `EtwEventWrite` inside `ntdll.dll`.
    
2.  **Change Memory Protections:** The `.text` section of `ntdll.dll` is normally read-only and executable (`PAGE_EXECUTE_READ`). The malware calls `VirtualProtect` to change the permissions of the memory page containing `EtwEventWrite` to `PAGE_EXECUTE_READWRITE` (RWX).
    
3.  **Overwrite Instructions:** The malware overwrites the first few bytes of the `EtwEventWrite` function with an assembly instruction that immediately returns execution to the caller, bypassing the event logging logic entirely.
    -   *Common Patch (x64):* Overwriting with `c3` (the `RET` instruction) or `33 c0 c3` (`XOR EAX, EAX; RET` to return a success code without doing anything).
    
4.  **Restore Protections:** The malware restores the memory permissions back to `PAGE_EXECUTE_READ` using `VirtualProtect` to avoid leaving RWX memory artifacts.

Once patched, whenever the .NET runtime or any other component in that process attempts to log an event via `EtwEventWrite`, the function immediately returns. The event is never sent to the kernel, and the EDR never sees it.

## 4. ASCII Architecture Diagram: ETW Flow and Patching

```text
NORMAL ETW EVENT LOGGING FLOW
+-------------------+        +--------------------+       +-------------------+
|  Target Process   |        |     ntdll.dll      |       |      Kernel       |
|  (e.g., malware)  |        |                    |       |                   |
|                   |        |                    |       |                   |
|  .NET Assembly    | -----> |  EtwEventWrite()   | ----> | ETW Subsystem     |
|  Calls Event      |        |  [Normal Code]     |       | Logs Event to EDR |
+-------------------+        +--------------------+       +-------------------+


PATCHED ETW EVENT LOGGING FLOW (BLINDED)
+-------------------+        +--------------------+       +-------------------+
|  Target Process   |        |     ntdll.dll      |       |      Kernel       |
|  (e.g., malware)  |        |                    |       |                   |
|                   |        |                    |       |                   |
|  .NET Assembly    | -----> |  EtwEventWrite()   |   X   | ETW Subsystem     |
|  Calls Event      |        |  [RET Instruction] |--/    | (Receives Nothing)|
+-------------------+        +--------------------+       +-------------------+
                                      |
                                      v
                             Function returns immediately.
                             EDR is completely blind to activity.
```

## 5. Real-World Attack Scenario

A Red Team operator uses a Cobalt Strike `execute-assembly` command to run a post-exploitation .NET tool (like Seatbelt or SharpHound) in memory.

1.  **Preparation:** Before executing the .NET payload, the operator's beacon executes a BOF (Beacon Object File) that performs ETW patching.
    
2.  **Patching:** The BOF finds `EtwEventWrite` in the current process and overwrites it with a `RET` instruction.
    
3.  **Execution:** The beacon injects the .NET assembly into a temporary process and executes it.
    
4.  **Evasion:** Normally, the .NET CLR generates massive amounts of ETW telemetry regarding assembly loads, method executions, and AppDomain creation. However, because `EtwEventWrite` is patched, these events are dropped. The EDR fails to detect the in-memory execution of SharpHound.

## 6. Defender's Perspective and Telemetry

While ETW patching blinds the logging mechanism, the act of patching itself is an aggressive memory manipulation technique that can be detected.

### 6.1 Detecting Memory Modification

-   **Integrity Verification:** Advanced EDRs periodically scan the memory space of critical DLLs (like `ntdll.dll` and `kernel32.dll`) and compare the in-memory byte sequences against the on-disk file. If the `EtwEventWrite` function in memory differs from the file on disk, it indicates tampering.
    
-   **VirtualProtect Monitoring:** EDRs monitor calls to `NtProtectVirtualMemory`. If a process attempts to change the memory protections of `ntdll.dll` to RWX, it is a massive red flag.

### 6.2 ETW Threat Intelligence (ETW-Ti)

-   Microsoft introduced ETW-Ti (Threat Intelligence) specifically to counter user-mode patching. ETW-Ti operates entirely in the kernel. Even if user-mode `EtwEventWrite` is patched, kernel-level events (like memory allocation, thread creation, and handle operations) are still logged by ETW-Ti and consumed by the EDR driver.

## 7. Mitigation and Remediation Strategies

Defending against telemetry blinding requires ensuring the integrity of the logging pipeline.

1.  **Kernel-Level Telemetry:** Ensure your EDR relies heavily on kernel-mode callbacks (like `ObRegisterCallbacks` and `PsSetCreateProcessNotifyRoutine`) and ETW-Ti, rather than solely relying on user-mode ETW providers which are vulnerable to patching.
    
2.  **Memory Integrity Checks:** Utilize EDR configurations that actively enforce the integrity of core operating system modules in memory.
    
3.  **Detecting the Setup:** Focus on detecting the precursor activities required for patching, such as anomalous API resolution or unusual memory protection alterations targeting `ntdll.dll`.
    
4.  **Hardware Enforced Security:** Utilize features like Virtualization-based Security (VBS) and Hypervisor-Enforced Paging Translation (HVCI) to prevent unauthorized modification of code pages, even by processes running with administrative privileges.

## 8. Chaining Opportunities

ETW Patching is the ultimate enabler technique, designed to pave the way for noisier operations.

-   Chaining with [[10 - AMSI Antimalware Scan Interface Bypass Techniques]] provides complete blinding for script and assembly execution. Patching AMSI bypasses content scanning, and patching ETW bypasses execution telemetry.
    
-   Utilizing ETW patching prior to [[06 - Process Hollowing and Injection OPSEC]] prevents the EDR from logging the suspicious memory allocation and thread creation events associated with injection.
    
-   Combining with [[08 - PPID Spoofing and Command Line Obfuscation]] ensures that even if some minimal process creation metadata is logged by the kernel, the context surrounding it is entirely fabricated.

## 9. Summary

ETW Patching is a critical evasion technique that targets the fundamental visibility mechanisms of Windows. By modifying the execution flow of logging functions in memory, attackers can render EDRs blind to subsequent malicious actions. Defenders must rely on kernel-level telemetry, strict memory integrity validation, and behavioral analysis to detect and overcome this capability.

## 10. Related Notes

-   [[06 - Process Hollowing and Injection OPSEC]]
-   [[07 - Thread Stack Spoofing and Call Stack Evasion]]
-   [[08 - PPID Spoofing and Command Line Obfuscation]]
-   [[10 - AMSI Antimalware Scan Interface Bypass Techniques]]
-   [[11 - Direct and Indirect Syscalls]]

***
*Disclaimer: This material is intended strictly for educational and defensive purposes. Understanding these techniques is critical for developing robust detection engineering, incident response capabilities, and securing enterprise networks.*
