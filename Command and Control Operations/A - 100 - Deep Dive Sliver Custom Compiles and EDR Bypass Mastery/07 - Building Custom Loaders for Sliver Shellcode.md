---
tags: [sliver, custom-compile, edr-bypass, red-team, vapt]
difficulty: advanced
module: "100 - Deep Dive: Sliver Custom Compiles & EDR Bypass Mastery"
topic: "100.07 Building Custom Loaders for Sliver Shellcode"
---

# 100.07 Building Custom Loaders for Sliver Shellcode (Theoretical Concepts)

## Introduction to Custom Loaders

In the context of red teaming and adversary simulation, a loader is a specialized application designed to execute a payload (such as a Sliver agent) within memory. The primary objective of a custom loader is to transition the payload from a dormant state (e.g., resting on disk, embedded within a file, or fetched from a network resource) into an active, executing state while attempting to minimize forensic artifacts and evade detection mechanisms.

Sliver, like many C2 frameworks, can generate its payload as shellcode. Shellcode is Position-Independent Code (PIC), meaning it is designed to execute correctly regardless of where it is loaded in memory. This characteristic is crucial, as the loader cannot predict the exact memory address where the allocation will occur.

## The Anatomy of a Loader

A theoretical custom loader typically follows a structured execution sequence:

1.  **Retrieval:** Obtaining the shellcode. This could involve reading it from a local file, decrypting it from an embedded resource within the loader itself, or fetching it dynamically from a remote server.
2.  **Allocation:** Reserving memory space within a process (either the loader's own process or a remote process) to house the shellcode.
3.  **Copying:** Transferring the shellcode into the allocated memory region.
4.  **Execution:** Instructing the CPU to begin executing instructions at the start of the newly populated memory region.

### Memory Allocation Concepts

The most critical aspect of a loader is how it handles memory. Security products heavily scrutinize memory allocations, particularly those that result in executable regions.

*   **VirtualAlloc / VirtualAllocEx:** These are standard Windows APIs used to reserve and commit memory pages. By default, malware often requests `PAGE_EXECUTE_READWRITE` (RWX) permissions. This allows the memory to be written to and subsequently executed.
*   **The RWX Problem:** Memory regions marked as RWX are highly anomalous in standard applications. Defensive scanners specifically target RWX regions, as they are a strong indicator of injected code or unpacked malware.
*   **Theoretical Evasion - RW to RX:** A more sophisticated approach involves allocating memory as `PAGE_READWRITE` (RW), copying the payload, and then using `VirtualProtect` to change the permissions to `PAGE_EXECUTE_READ` (RX) immediately before execution. This minimizes the time the memory is writable and executable simultaneously.

### Execution Mechanisms

Once the shellcode is in memory, the loader must redirect execution flow to it.

*   **CreateThread / CreateRemoteThread:** The most straightforward method. The loader creates a new thread within the target process, specifying the start address as the location of the shellcode. This is heavily monitored.
*   **Function Pointers:** The loader can cast the memory address of the shellcode to a function pointer and call it directly. This executes the shellcode within the context of the current thread.
*   **Asynchronous Procedure Calls (APCs):** Queuing an APC to a thread forces that thread to execute a specific function (the shellcode) when it enters an alertable state.
*   **Thread Hijacking:** Suspending a legitimate thread, modifying its instruction pointer (RIP) to point to the shellcode, and resuming the thread.

## Architecture Diagram: Remote Process Injection

```ascii
=========================================================================
                      REMOTE PROCESS INJECTION FLOW
=========================================================================

[ Loader Process ]                                  [ Target Process ]
(e.g., update.exe)                                  (e.g., notepad.exe)

 1. Obtain Payload
    (Decrypt embedded
     Sliver shellcode)
        |
        v
 2. OpenTargetProcess()  ------------------------>  [ HANDLE Acquired ]
        |
        v
 3. VirtualAllocEx()     ------------------------>  [ Allocated Memory ]
    (Request PAGE_RW)                               | (Status: RW  )   |
        |                                           |                  |
        v                                           |                  |
 4. WriteProcessMemory() ------------------------>  [ Shellcode Copied ]
    (Write payload)                                 | (Status: RW  )   |
        |                                           |                  |
        v                                           |                  |
 5. VirtualProtectEx()   ------------------------>  [ Perms Changed    ]
    (Change to PAGE_RX)                             | (Status: R-X )   |
        |                                           |                  |
        v                                           |                  |
 6. CreateRemoteThread() ------------------------>  [ Execution Starts ]
    (Start address points                           | (Sliver Beacon   |
     to allocated memory)                           |  Active)         |

=========================================================================
```

## Defensive Telemetry and Analysis

Defenders utilize several techniques to identify and analyze custom loaders and the resulting in-memory payloads.

### 1. Memory Scanning and YARA

EDR solutions and memory forensic tools periodically scan the memory space of running processes. They look for specific byte sequences (signatures) associated with known malware, including common C2 frameworks like Sliver.

Furthermore, scanners analyze memory regions for anomalous characteristics:
*   Unbacked executable memory: Legitimate executable code is typically "backed" by a file on disk (e.g., a loaded DLL). Executable memory that has no corresponding file on disk (unbacked memory) is highly suspicious and often indicates injection.
*   High Entropy: Encrypted or packed payloads often exhibit high entropy (randomness). Scanners may flag memory regions with unusually high entropy for further analysis.

### 2. API Monitoring and Telemetry

The sequence of APIs used by loaders (e.g., `VirtualAllocEx` -> `WriteProcessMemory` -> `CreateRemoteThread`) is a classic injection pattern. EDR solutions monitor these sequences. While attackers may attempt to obscure the calls (e.g., using indirect syscalls), the underlying OS mechanisms are still invoked and can be monitored via kernel callbacks.

### 3. Thread Call Stack Analysis

As discussed in the context of syscalls, thread call stacks are a primary detection vector. If a thread is executing out of unbacked memory, its call stack will reflect this anomaly. Defenders analyze threads to ensure their execution origin traces back to legitimate, signed modules.

## Real-World Attack Scenario

During an engagement, an adversary utilized an obfuscated PowerShell script to act as the initial loader. The script did not write the Sliver payload to disk. Instead, it allocated memory dynamically within the PowerShell process space, base64-decoded the payload, and used a .NET delegate to execute it via a function pointer.

Defensive systems failed to detect the payload statically because it never touched the disk in its raw form. However, runtime memory analysis identified an anomalous, unbacked, executable memory region within the PowerShell process that contained high-entropy data. Subsequent dumping and analysis of this memory region revealed the decrypted Sliver shellcode, leading to the identification and containment of the C2 channel.

## Chaining Opportunities

Custom loaders are rarely used in isolation. They are typically part of a broader execution strategy:

*   [[06 - Integrating Custom Syscalls directly into the Sliver Agent]]: Loaders may incorporate custom syscalls to perform the memory allocation and execution steps, attempting to evade user-mode API monitoring.
*   [[08 - Bypassing CrowdStrike Falcon with Custom Sliver Profiles]]: The loader's execution methods must align with the behavioral profiles designed to evade specific EDR heuristics.
*   [[12 - Advanced Obfuscation and Packing Techniques]]: The shellcode embedded within the loader is almost always obfuscated or encrypted to prevent static analysis of the loader binary itself.

## Related Notes

*   [[Position-Independent Code (PIC) Analysis]]
*   [[Memory Injection Techniques Overview]]
*   [[Analyzing Thread Execution Chains]]
*   [[Identifying Unbacked Executable Memory]]
*   [[Windows API: Memory Management]]
