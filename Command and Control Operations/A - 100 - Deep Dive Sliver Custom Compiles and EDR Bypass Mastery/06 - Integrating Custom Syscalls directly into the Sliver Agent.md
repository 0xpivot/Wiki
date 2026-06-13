---
tags: [sliver, custom-compile, edr-bypass, red-team, vapt]
difficulty: advanced
module: "100 - Deep Dive: Sliver Custom Compiles & EDR Bypass Mastery"
topic: "100.06 Integrating Custom Syscalls directly into the Sliver Agent"
---

# 100.06 Integrating Custom Syscalls directly into the Sliver Agent (Theoretical Framework)

## Introduction to Syscall Architecture

Understanding how user-mode applications interact with the kernel is fundamental for both offensive development and defensive telemetry engineering. In Windows environments, user applications (Ring 3) cannot directly interact with hardware or critical system structures. Instead, they must request the operating system kernel (Ring 0) to perform these actions on their behalf. This transition is facilitated through System Calls, or "syscalls".

When an application calls a high-level API, such as `CreateFile` in `kernel32.dll`, the execution flow typically traverses through several layers of the Windows subsystem before reaching the kernel. The final user-mode stop is usually `ntdll.dll`, which contains the actual syscall stubs.

### The Role of NTDLL

`ntdll.dll` acts as the primary bridge between user mode and kernel mode. It exports a myriad of functions prefixed with `Nt` or `Zw` (e.g., `NtAllocateVirtualMemory`). These functions are incredibly small and generally follow a strict structural pattern:

1.  **Move the System Service Number (SSN) into a specific CPU register.** On x64 architectures, this is the `EAX` register. The SSN is a unique identifier for the specific kernel function being requested.
2.  **Execute the transition instruction.** On modern x64 systems, this is the `syscall` instruction. On older x86 systems, it might be `sysenter` or an interrupt like `int 0x2e`.
3.  **Return.** After the kernel completes the request, execution returns to the instruction immediately following the syscall.

## Concept of Direct Syscalls

The theoretical goal of integrating custom or "direct" syscalls into an agent like Sliver is to bypass the standard API call flow. Security products often place hooks within user-mode DLLs, particularly `ntdll.dll`. By overwriting the initial bytes of a function with a `JMP` instruction, the EDR can redirect execution to its own analysis engine before allowing the system call to proceed.

If an agent executes the syscall instruction directly, it entirely bypasses these user-mode hooks.

### Mechanisms of Direct Syscalls

The primary challenge in implementing direct syscalls is dynamically determining the correct System Service Number (SSN). SSNs change between Windows versions, service packs, and sometimes even minor updates. Hardcoding SSNs is brittle and leads to immediate crashes on unsupported systems.

Theoretical methods for dynamic resolution include:

*   **Reading NTDLL from Disk:** The agent can load a fresh copy of `ntdll.dll` directly from `C:\Windows\System32\` into memory. This copy will not contain the EDR hooks that are applied to the `ntdll.dll` loaded into the process during initialization. The agent can then parse this clean copy to extract the SSNs.
*   **Sorting by Address (e.g., Hell's Gate/Halo's Gate):** This method involves parsing the in-memory `ntdll.dll`. Even if functions are hooked, their exported addresses remain in the same relative order. By sorting the exported `Nt` functions by their memory addresses, an agent can infer the SSN, as they are typically assigned sequentially.
*   **Exception Directory Parsing:** Analyzing the exception directory to find the original syscall stubs, potentially bypassing hooks placed at the very beginning of the function.

## Architecture Diagram: Standard vs. Direct Syscalls

```ascii
================================================================================
                        USER MODE (Ring 3)
================================================================================

[ Standard Execution Flow ]             [ Direct Syscall Flow (Theoretical) ]

+-------------------------+             +-------------------------+
|    Sliver Agent         |             |    Sliver Agent         |
|  (Standard API Call)    |             |  (Direct Syscall Imp)   |
+-----------+-------------+             +-----------+-------------+
            |                                       |
            v                                       |
+-------------------------+                         |
|    kernel32.dll         |                         |
| (e.g., VirtualAlloc)    |                         |
+-----------+-------------+                         |
            |                                       |
            v                                       |
+-------------------------+                         |
|      ntdll.dll          |                         |
| (e.g., NtAllocate...)   |                         |
|  [ EDR HOOK PLACED ] <--+--- Detection            |
+-----------+-------------+    Occurs Here          |
            |                                       |
            | (syscall)                             | (syscall instruction
            |                                       |  executed manually)
============|=======================================|===========================
            |           KERNEL MODE (Ring 0)        |
============|=======================================|===========================
            v                                       v
+-----------------------------------------------------------------+
|                        ntoskrnl.exe                             |
|                  System Service Dispatcher                      |
+-----------------------------------------------------------------+
```

## Defensive Telemetry and Detection

While direct syscalls bypass user-mode hooking, they are not invisible. Modern defensive architectures have evolved to detect this behavior through various mechanisms.

### 1. Event Tracing for Windows (ETWti)

ETW Threat Intelligence (ETWti) provides kernel-level visibility into system operations. Because ETWti operates in Ring 0, it is unaffected by user-mode hooks or the bypass thereof. When a syscall transitions into the kernel, the kernel itself can log the action.

Defenders monitor specific high-value syscalls (e.g., memory allocation, thread creation in remote processes) via ETWti. If an agent uses a direct syscall to allocate memory, ETWti will still record the event.

### 2. Call Stack Analysis

This is currently one of the most potent detection mechanisms against direct syscalls. When a legitimate application makes a syscall, the call stack (the record of active subroutines) should reflect the expected execution flow:

`Kernel -> ntdll.dll -> kernelbase.dll -> kernel32.dll -> Application.exe`

When an agent executes a direct syscall, the call stack is anomalous. The stack will show the transition directly from the agent's memory region into the kernel, bypassing the expected `ntdll.dll` frames:

`Kernel -> Application.exe (or unknown memory region)`

EDR solutions actively profile threads and analyze their call stacks, particularly when suspicious APIs are invoked or when a thread is resting. An anomalous call stack that resolves outside of known system modules is a strong indicator of direct syscall usage or injected code.

### 3. Kernel Callbacks

Windows provides mechanisms for security drivers to register callbacks for specific events, such as process creation, thread creation, and image loading. Like ETWti, these callbacks operate in the kernel and provide robust telemetry regardless of how the user-mode request was initiated.

## Real-World Attack Scenario

In a post-incident analysis of a sophisticated intrusion, responders identified a highly obfuscated beacon operating within the environment. Initial telemetry from user-mode EDR sensors showed no anomalous API calls originating from the suspicious process, indicating a potential bypass of standard monitoring.

Further investigation utilizing kernel-level telemetry (ETWti) revealed the process was dynamically allocating executable memory and creating remote threads in `explorer.exe`. Memory forensics confirmed the presence of an implant that was utilizing dynamic SSN resolution (similar to the Halo's Gate technique) to execute syscalls directly, effectively blinding the user-mode hooks of the deployed security solution. The attack was ultimately detected through behavioral analysis of the resulting remote thread creation and anomalous network communication, rather than the initial execution phase.

## Chaining Opportunities

The theoretical application of direct syscalls is often combined with other techniques to create a more resilient execution chain:

*   [[07 - Building Custom Loaders for Sliver Shellcode]]: Custom loaders often employ direct syscalls to allocate the initial memory for the shellcode, attempting to hide the allocation from user-mode analysis.
*   [[11 - Advanced Memory Evasion Techniques]]: To counter call stack analysis, theoretical implementations may attempt to spoof the call stack before executing the direct syscall, making it appear as though the call originated from a legitimate `ntdll.dll` function.
*   [[15 - Defeating ETW and AMSI]]: If ETWti is active, attackers may attempt to blind ETW telemetry prior to utilizing direct syscalls, although this typically requires elevated privileges and carries high risk.

## Related Notes

*   [[Architecture of the Windows NT Kernel]]
*   [[Understanding User-Mode Hooking Mechanisms]]
*   [[Analyzing Event Tracing for Windows (ETW)]]
*   [[Memory Forensics: Identifying Injected Code]]
*   [[Call Stack Spoofing Concepts]]
