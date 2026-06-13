---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.04 Unhooking Userland APIs EDR Bypass"
---

# 04 - Unhooking Userland APIs EDR Bypass

## 1. Introduction to API Hooking
As established in [[01 - Modern EDR Architecture and Detection Mechanisms]], the primary mechanism EDRs use to monitor process behavior in user-mode is API Hooking. When a process starts, the EDR injects its sensor DLL. This DLL patches the first few bytes of critical functions within `ntdll.dll` and `kernel32.dll` (e.g., `NtAllocateVirtualMemory`, `NtWriteVirtualMemory`, `NtCreateThreadEx`). 

Instead of the function executing normally, the patched bytes contain a `JMP` (Jump) instruction redirecting execution flow into the EDR's DLL. The EDR inspects the parameters, the call stack, and makes a heuristic decision (as seen in [[03 - Bypassing Heuristics and Behavioral Analysis]]). If benign, execution is returned to the original function; if malicious, the process is terminated.

To operate stealthily, malware must remove these hooks, restoring the APIs to their original, unmonitored state. This process is known as "Unhooking."

## 2. The Mechanics of a Hook

Let's examine a typical `ntdll.dll` function before and after an EDR hook.

### 2.1 Unhooked State (Clean)
A clean `syscall` stub in `ntdll.dll` (e.g., `NtReadVirtualMemory`) looks like this in assembly:
```nasm
4C 8B D1          mov r10, rcx       ; Setup for syscall
B8 3F 00 00 00    mov eax, 3Fh       ; Syscall Number (SSN) into EAX
F6 04 25 08 03..  test byte ptr [7FFE0308h], 1 ; Check if syscalls are enabled
75 03             jne ...
0F 05             syscall            ; Transition to Kernel Mode
C3                ret
```

### 2.2 Hooked State (EDR Monitored)
The EDR overwrites the first 5 bytes with an unconditional jump (`E9`) to its own memory space:
```nasm
E9 45 67 89 0A    jmp EDR_Sensor.dll+0x12345 ; Jump to EDR inspection routine
B8 3F 00 00 00    mov eax, 3Fh       ; This is never reached directly
...
```

## 3. Techniques for Unhooking

The goal of unhooking is to restore the original bytes (the `mov r10, rcx` instruction) over the `jmp` instruction, effectively blinding the EDR for that specific process.

### 3.1 Classic Unhooking (Reading from Disk)
The most common and fundamental approach. The malware relies on the fact that the `ntdll.dll` file on disk (`C:\Windows\System32\ntdll.dll`) is clean; the EDR only hooks the version loaded into memory.

**The Workflow:**
1.  **Map:** The malware manually reads the raw `ntdll.dll` file from disk and maps it into its own memory space as a data file.
2.  **Locate:** It finds the `.text` section (where executable code resides) of both the hooked `ntdll.dll` (currently loaded in the process) and the clean `ntdll.dll` (mapped from disk).
3.  **Overwrite:** Using `VirtualProtect` to change memory permissions to `PAGE_EXECUTE_READWRITE`, it copies the clean `.text` section from the disk-mapped DLL over the hooked `.text` section in the loaded DLL.
4.  **Restore:** It restores the original memory permissions (`PAGE_EXECUTE_READ`).

*   **Pros:** Highly effective; completely restores all `ntdll.dll` APIs simultaneously.
*   **Cons:** Calling `VirtualProtect` on `ntdll.dll` is itself highly anomalous. Modern EDRs heavily monitor attempts to modify their hooks or `ntdll.dll` permissions.

### 3.2 Perun's Fart (Suspended Process Unhooking)
A more advanced variation of the classic technique designed to avoid reading `ntdll.dll` from disk, which might be monitored by minifilters.
1.  The malware spawns a benign process (e.g., `notepad.exe`) in a **suspended** state.
2.  When a process is suspended upon creation, the EDR often hasn't had the opportunity to inject its DLL and place its hooks yet.
3.  The malware reads the clean `ntdll.dll` from the memory of the suspended `notepad.exe` process.
4.  It overwrites its own hooked `ntdll.dll` with the clean version retrieved from the suspended process.
5.  It terminates the suspended process.

### 3.3 Targeted Unhooking (Patching specific bytes)
Instead of overwriting the entire `.text` section, the malware identifies the specific APIs it needs (e.g., `NtAllocateVirtualMemory`) and only patches those specific 5 bytes back to `4C 8B D1`. 
*   **Pros:** Smaller footprint, potentially avoiding blanket anomaly detections on the `.text` section.
*   **Cons:** Still requires `VirtualProtect`.

## 4. Visualizing the Unhooking Process

```ascii
+-----------------------------------------------------------------------------------+
|                           THE UNHOOKING WORKFLOW (Disk to Memory)                 |
|                                                                                   |
|  [ Disk: C:\Windows\System32\ntdll.dll ] (CLEAN)                                  |
|         |                                                                         |
|         | (1. ReadFile & MapViewOfFile)                                           |
|         v                                                                         |
|  [ Mapped Clean ntdll.dll ] --------+                                             |
|                                     |                                             |
|                                     | (2. Copy .text section bytes)               |
|                                     v                                             |
|  [ In-Memory Hooked ntdll.dll ] <---+                                             |
|   +--------------------------+                                                    |
|   | NtProtectVirtualMemory   |                                                    |
|   | JMP EDR.dll              | <--- OVERWRITTEN WITH CLEAN BYTES (4C 8B D1)       |
|   +--------------------------+                                                    |
|                                                                                   |
|   Result: EDR is blind to subsequent API calls originating from this process.     |
+-----------------------------------------------------------------------------------+
```

## 5. Real-World Attack Scenario

### The Scenario: Delivering a Ransomware Payload
A threat actor has gained access via a compromised credential and wants to deploy ransomware across the domain. The environment uses an aggressive EDR known for deep userland hooking.

The attacker drops a custom loader executable.
1.  The loader executes and immediately implements the "Perun's Fart" technique. It spawns `werfault.exe` (Windows Error Reporting) in a suspended state.
2.  It extracts the pristine, unhooked `ntdll.dll` from the suspended process and overwrites its own memory space.
3.  *Crucially*, the loader then restores the original memory protections so the EDR's periodic memory scans don't flag anomalous RWX regions.
4.  Now operating in a blind spot, the loader uses previously hooked APIs (`NtAllocateVirtualMemory`, `NtWriteVirtualMemory`) to decrypt the ransomware payload into memory.
5.  Because the userland telemetry pipeline is broken, the EDR fails to build a behavioral graph of the injection process. The ransomware executes, begins encrypting files, and the EDR only detects the intrusion at the kernel/minifilter level (file system modifications), which is often too late to stop the encryption entirely.

## 6. Defensive Mitigations

EDRs counter unhooking techniques through several advanced methods:
1.  **Kernel Callbacks (The Ultimate Defense):** Recognizing that userland hooks can be bypassed, EDRs increasingly rely on kernel callbacks (e.g., `PsSetCreateThreadNotifyRoutine`) and ETW-TI. Even if `ntdll.dll` is unhooked, the transition to the kernel still triggers these telemetry points.
2.  **Hook Integrity Monitoring:** The EDR driver periodically hashes the `.text` section of `ntdll.dll` in running processes or checks the first few bytes of critical APIs. If it detects the hooks have been removed, it immediately terminates the process.
3.  **Bypassing VirtualProtect:** EDRs heavily monitor the `NtProtectVirtualMemory` API. If a process attempts to change permissions on `ntdll.dll` to RWX, the action is blocked or flagged.

## 7. Chaining Opportunities

Unhooking is powerful but noisy. Advanced actors are moving away from unhooking entirely, opting instead to bypass the hooks without modifying memory:
*   Instead of unhooking, you can implement [[05 - Direct and Indirect Syscalls using HellsGates]] to bypass `ntdll.dll` entirely.
*   Once operating securely (either via unhooking or syscalls), you can safely execute techniques outlined in [[03 - Bypassing Heuristics and Behavioral Analysis]].

## 8. Related Notes

*   [[99.01 - Modern EDR Architecture and Detection Mechanisms]]
*   [[Understanding Windows Memory Management]]
*   [[Reflective DLL Injection Deep Dive]]
*   [[Bypassing ETW (Event Tracing for Windows)]]
