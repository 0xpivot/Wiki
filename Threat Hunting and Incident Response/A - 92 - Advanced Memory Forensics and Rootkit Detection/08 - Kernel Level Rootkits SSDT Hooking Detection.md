---
tags: [threat-hunting, forensics, memory, rootkits, vapt]
difficulty: advanced
module: "92 - Advanced Memory Forensics and Rootkit Detection"
topic: "92.08 Kernel Level Rootkits SSDT Hooking Detection"
---

# 92.08 Kernel Level Rootkits SSDT Hooking Detection

## Introduction

In the continuous arms race between advanced persistent threats (APTs) and defensive security teams, kernel-level rootkits represent the apex of evasion and persistence. Once an attacker breaches the kernel boundary (Ring 0), they possess the ultimate authority over the operating system, allowing them to subvert almost any security control, hide processes, mask network connections, and alter file system views. One of the classic and most powerful techniques utilized by kernel rootkits is System Service Descriptor Table (SSDT) Hooking. 

Detecting SSDT hooking is a fundamental requirement in advanced memory forensics. Because a hooked SSDT manipulates the very answers the operating system provides to user-land applications (including antivirus and EDR agents), live response tools running on the infected system cannot be trusted. Memory forensics, operating on an offline dump of physical RAM, provides an unvarnished view of the kernel structures, allowing analysts to identify where hooks have been placed, map them back to the malicious driver, and understand the rootkit's capabilities.

## Understanding the SSDT

The System Service Descriptor Table (SSDT), also known as the `KeServiceDescriptorTable`, is a critical data structure within the Windows kernel. It acts as the routing table or bridge between user-mode applications (Ring 3) and the core kernel-mode execution (Ring 0).

When a user-mode application needs to perform a privileged operation—such as allocating memory, writing to a file, or creating a process—it calls a function in `ntdll.dll` (e.g., `NtCreateFile`). `ntdll.dll` acts as a wrapper that sets up the system call number in a CPU register (like EAX) and triggers a transition to kernel mode via the `syscall` or `sysenter` instruction.

Once in kernel mode, the System Service Dispatcher (the `KiSystemService` routine) reads the system call number and looks it up in the SSDT. The SSDT contains an array of function pointers. The system call number is used as an index into this array, and the dispatcher jumps to the corresponding kernel function (e.g., `NtCreateFile` inside `ntoskrnl.exe`).

### The Mechanics of SSDT Hooking

SSDT Hooking occurs when a malicious kernel driver overwrites one or more of the function pointers in the SSDT array. Instead of pointing to the legitimate Windows kernel function, the overwritten pointer directs execution flow to a function controlled by the rootkit.

For example, to hide a malicious process from the Task Manager:
1. Task Manager calls `NtQuerySystemInformation` to get a list of active processes.
2. The user-mode call transitions to the kernel.
3. The System Service Dispatcher looks up `NtQuerySystemInformation` in the SSDT.
4. Because the SSDT is hooked, the dispatcher jumps to the rootkit's custom function instead of the legitimate `NtQuerySystemInformation`.
5. The rootkit calls the original `NtQuerySystemInformation` to get the real process list.
6. The rootkit then filters out its own malicious process from the list.
7. The rootkit returns the tampered list back to user mode.
8. Task Manager displays the list, entirely unaware that a process has been hidden.

```text
+-----------------------------------------------------------------------------------+
|                                SSDT Hooking Architecture                          |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  Ring 3 (User Mode)                                                               |
|  +--------------------+                                                           |
|  | Task Manager       |                                                           |
|  | (API Call)         |                                                           |
|  +---------+----------+                                                           |
|            | 1. Calls NtQuerySystemInformation                                    |
|            v                                                                      |
|  +--------------------+                                                           |
|  | ntdll.dll          |                                                           |
|  | (Syscall Wrapper)  |                                                           |
|  +---------+----------+                                                           |
|            | 2. syscall instruction                                               |
|  ==========|====================================================================  |
|            |                                                                      |
|  Ring 0 (Kernel Mode)                                                             |
|            v                                                                      |
|  +--------------------+       3. Looks up Index                                   |
|  | System Service     |-----------------------+                                   |
|  | Dispatcher         |                       |                                   |
|  +--------------------+                       v                                   |
|                                     +--------------------+                        |
|                                     |        SSDT        |                        |
|                                     +--------------------+                        |
|                                     | [0] NtCreateFile   |                        |
|                                     | [1] NtOpenFile     |                        |
|                                     | ...                |                        |
|                                     | [X] Malicious_Func | <--- HOOKED!           |
|                                     | ...                | (Points to Rootkit.sys)|
|                                     +---------+----------+                        |
|                                               |                                   |
|                                               | 4. Execution Redirected           |
|                                               v                                   |
|                                     +--------------------+                        |
|                                     | Rootkit.sys        |                        |
|                                     | (Filters output)   |                        |
|                                     +---------+----------+                        |
|                                               | 5. Calls original                 |
|                                               v                                   |
|                                     +--------------------+                        |
|                                     | ntoskrnl.exe       |                        |
|                                     | (Original Func)    |                        |
|                                     +--------------------+                        |
+-----------------------------------------------------------------------------------+
```

## Detection Strategies in Memory Forensics

Because SSDT hooks alter the behavior of the entire OS by manipulating centralized pointers, memory forensics can reliably detect these alterations by examining the SSDT array offline.

### 1. Volatility `ssdt` Plugin
The primary method for detecting SSDT hooking in memory is using Volatility’s `ssdt` (or `windows.ssdt`) plugin. This plugin performs the following actions:
1. Locates the `KeServiceDescriptorTable` in memory.
2. Iterates through every pointer in the SSDT array.
3. Resolves the memory address that each pointer references.
4. Checks which kernel module (driver or executable) owns that memory address range.

In a clean system, the vast majority of SSDT entries should point directly into the memory space of `ntoskrnl.exe` or `win32k.sys` (for GUI-related system calls in the Shadow SSDT). 

If an SSDT entry points to an address outside of these standard OS modules—especially if it points to an unknown, unsigned, or suspiciously named driver (e.g., `hidden_rootkit.sys`) or an unbacked/unallocated memory region—it is highly indicative of an SSDT hook.

### 2. Identifying the Hooked Function
When `ssdt` identifies an anomaly, the output will show the hooked index, the original function name, and the malicious address. 
Example Output:
```text
Index   Function Name                Hooked Address       Owning Module
-----   -------------------------    ------------------   ------------------
0x105   NtQuerySystemInformation     0xFFFFF80012345000   rootkit_hidden.sys
0x111   NtEnumerateKey               0xFFFFF80012346000   rootkit_hidden.sys
```
By analyzing *which* functions are hooked, the threat hunter can deduce the rootkit's capabilities:
- `NtQuerySystemInformation`: Process hiding.
- `NtEnumerateKey` / `NtEnumerateValueKey`: Registry hiding (masking persistence mechanisms).
- `NtQueryDirectoryFile`: File and folder hiding.
- `NtDeviceIoControlFile`: Manipulating direct device communications (often used to hide network traffic).

### 3. Dealing with Unbacked Hooks
Sophisticated rootkits often try to avoid leaving an identifiable driver footprint in memory (module hiding). If a rootkit hooks the SSDT but places the malicious code in a dynamically allocated, anonymous block of memory that does not belong to a loaded module, the `ssdt` plugin might show the owner as `UNKNOWN`. 
In this case, the analyst must dump the raw memory at the hooked address (using `volshell` or extracting the memory segment) and reverse-engineer the shellcode to understand its purpose and potentially find C2 configurations or decryption keys.

## Challenges with Modern Windows (PatchGuard)

It is crucial to understand that on modern 64-bit Windows operating systems, classic SSDT hooking is heavily mitigated by Kernel Patch Protection (KPP), widely known as **PatchGuard**. 

PatchGuard periodically checks critical kernel structures, including the SSDT, for any unauthorized modifications. If PatchGuard detects an anomaly (like a changed pointer in the SSDT), it immediately triggers a Blue Screen of Death (BSOD) with bug check code `0x109: CRITICAL_STRUCTURE_CORRUPTION`.

**How Attackers Adapt:**
Because PatchGuard makes permanent SSDT hooking highly unstable on 64-bit systems, modern rootkits often utilize alternative methods:
- **Infinity Hooking:** Abusing the `EtwpDebuggerData` and Windows event tracing mechanisms to intercept system calls without directly modifying the SSDT.
- **DKOM (Direct Kernel Object Manipulation):** Modifying kernel data structures (like the active process linked list) directly, rather than hooking the functions that query them.
- **Bootkits:** Compromising the boot process to disable PatchGuard entirely before the OS fully loads, allowing classic SSDT hooking to proceed.

Therefore, if you detect a classic SSDT hook on a modern 64-bit system, it almost certainly implies that the attacker has successfully bypassed or disabled PatchGuard, often indicating the presence of a deeply embedded bootkit or a highly sophisticated hypervisor-level rootkit.

## Real-World Attack Scenario

### Initial Foothold and Bootkit Installation
A state-sponsored threat group targets a critical infrastructure provider. After gaining initial access via a spear-phishing campaign, they deploy an advanced bootkit (similar to BlackLotus). The bootkit exploits a vulnerability in the UEFI secure boot process to gain execution before the Windows kernel loads.

### PatchGuard Subversion and SSDT Hooking
Because the bootkit runs before the OS, it locates and patches the Windows bootloader (`winload.efi`) in memory to disable Kernel Patch Protection (PatchGuard) and Driver Signature Enforcement (DSE). With PatchGuard disabled, the bootkit loads a malicious, unsigned kernel driver (`nvstor64_update.sys`).
The driver hooks several functions in the SSDT:
- `NtQueryDirectoryFile` to hide its payload files on disk.
- `NtQuerySystemInformation` to hide a custom listener process handling C2 traffic.

### Detection via Memory Forensics
The organization's SOC notices strange beaconing patterns from the server, but live endpoint tools report no anomalous processes or files. An IR team is dispatched and takes a full physical memory dump.

The analyst runs Volatility’s `ssdt` plugin:
```text
volatility -f srv_mem.raw windows.ssdt
```
The output immediately flags multiple anomalies:
```text
Index   Function Name                Hooked Address       Owning Module
0x33    NtQueryDirectoryFile         0xFFFFF88004567010   nvstor64_update.sys
0x105   NtQuerySystemInformation     0xFFFFF88004568A00   nvstor64_update.sys
```
The analyst notes that `nvstor64_update.sys` is not a legitimate Microsoft driver, despite its disguised name. The presence of SSDT hooks on a modern Windows Server system instantly alerts the analyst that PatchGuard has been disabled, pointing towards a pre-OS bootkit compromise. 

The analyst then uses Volatility to dump the malicious driver:
```text
volatility -f srv_mem.raw windows.dumpfiles --physaddr 0xFFFFF88004567000
```
Reverse-engineering the dumped driver reveals the logic used to filter out the C2 listener process, confirming the stealth mechanism and providing the necessary IOCs to hunt the threat across the network.

## Conclusion

Detecting SSDT hooking remains a cornerstone of advanced memory forensics. While PatchGuard has made this technique less common on modern systems, its presence signifies a severe, low-level compromise that live response tools are completely blind to. By analyzing the SSDT offline, threat hunters can uncover the exact mechanisms an attacker is using to maintain invisibility, map out the rootkit's capabilities, and extract the underlying malicious code for further analysis.

## Chaining Opportunities
- If SSDT hooking is detected on a modern 64-bit OS, immediately pivot to `[[10 - Analyzing Master Boot Record MBR and VBR Infections]]` or UEFI forensic analysis, as PatchGuard must have been disabled.
- Correlate the hidden processes identified via `ssdt` hooking with `[[06 - Analyzing Network Connections in Memory Netscan]]` to find the C2 channels that the rootkit is attempting to mask.
- If the hook points to an unbacked memory region, use techniques from `[[01 - Process Memory Analysis and Injection Detection]]` to carve out and analyze the injected shellcode.
- Compare the findings of `ssdt` with `[[09 - Direct Kernel Object Manipulation DKOM Detection]]`; advanced rootkits often use a combination of both techniques.

## Related Notes
- `[[01 - Process Memory Analysis and Injection Detection]]`
- `[[06 - Analyzing Network Connections in Memory Netscan]]`
- `[[09 - Direct Kernel Object Manipulation DKOM Detection]]`
- `[[10 - Analyzing Master Boot Record MBR and VBR Infections]]`
- `[[03 - Memory Acquisition and Preservation Techniques]]`
