---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.05 Direct and Indirect Syscalls using HellsGates"
---

# 05 - Direct and Indirect Syscalls using HellsGates

## 1. The Evolution Beyond Unhooking
In [[04 - Unhooking Userland APIs EDR Bypass]], we explored how modifying memory to remove EDR hooks is highly effective but inherently noisy. EDRs now aggressively monitor the integrity of `ntdll.dll` and track calls to `VirtualProtect` targeting system modules. 

The modern approach to EDR evasion abandons the idea of modifying the environment. Instead, malware developers bypass the userland hooks entirely. This is achieved by manually recreating the transition from user-mode (Ring 3) to kernel-mode (Ring 0) that `ntdll.dll` normally handles. This technique is known as executing System Calls (Syscalls).

## 2. Understanding System Calls (Syscalls)

When an application calls a high-level API like `VirtualAlloc`, the call flows down the Windows architecture:
1.  `kernel32.dll` (`VirtualAlloc`)
2.  `ntdll.dll` (`NtAllocateVirtualMemory`)
3.  **The Syscall:** `ntdll.dll` sets up the CPU registers (specifically placing the System Service Number (SSN) into `EAX`) and executes the `syscall` instruction.
4.  **Kernel Transition:** Execution jumps to the kernel (`ntoskrnl.exe`), which reads the SSN, looks up the corresponding kernel function in the System Service Descriptor Table (SSDT), and executes the request.

EDR hooks reside in step 2. By executing Direct or Indirect Syscalls, we jump directly from step 1 to step 3, bypassing the EDR sensor entirely.

## 3. Direct Syscalls

Direct Syscalls involve the malware hardcoding the assembly instructions normally found in `ntdll.dll` directly into its own executable.

**The Assembly Stub:**
```nasm
; Custom implementation of NtAllocateVirtualMemory inside the malware
mov r10, rcx
mov eax, 0x18      ; Hardcoded System Service Number (SSN) for Windows 10
syscall
ret
```

### 3.1 The Challenge: Dynamic SSNs
The primary challenge with Direct Syscalls is that the System Service Number (SSN)—e.g., `0x18` for `NtAllocateVirtualMemory`—is not static. Microsoft frequently changes SSNs between major OS updates and even minor builds (Windows 7 vs Windows 10 vs Windows 11). Hardcoding an SSN will result in the malware calling the wrong kernel function on a different OS build, causing an immediate Blue Screen of Death (BSOD) or crash.

### 3.2 Dynamic Resolution (Hell's Gate)
To solve the dynamic SSN problem, the "Hell's Gate" technique was developed. Instead of hardcoding SSNs, the malware dynamically resolves them at runtime.
1.  The malware reads the `ntdll.dll` loaded in its own memory space.
2.  It parses the Export Address Table (EAT) to find the address of the desired function (e.g., `NtAllocateVirtualMemory`).
3.  It inspects the memory at that address.
4.  If the function is clean (no `JMP` instruction from an EDR), it extracts the SSN directly from the `mov eax, [SSN]` instruction.
5.  It then uses this dynamically resolved SSN in its own custom assembly stub to execute the direct syscall.

### 3.3 Overcoming Hooked Functions (Halo's Gate / Tartarus' Gate)
Hell's Gate fails if the EDR has hooked the function, because the hook overwrites the bytes containing the SSN. "Halo's Gate" solves this by inspecting neighboring functions.
*   Functions in `ntdll.dll` are arranged sequentially by SSN (e.g., `func A` is `0x18`, `func B` is `0x19`).
*   If `NtAllocateVirtualMemory` is hooked, Halo's Gate looks at the function immediately above or below it.
*   If the neighboring function is clean, it reads its SSN and mathematically calculates the hooked function's SSN (e.g., if the function below is `0x19`, the target is `0x18`).

## 4. Indirect Syscalls

While Direct Syscalls bypass userland hooks, they introduced a new IoC (Indicator of Compromise). EDRs and ETW-TI began inspecting the origin of the `syscall` instruction. 
*   **The Anomaly:** Legitimate syscalls *always* originate from within the memory address space of `ntdll.dll` or `win32u.dll`. A direct syscall originates from the memory space of the malware executable (e.g., `malware.exe`). This is highly anomalous.

Indirect Syscalls solve this problem.
1.  The malware dynamically resolves the SSN (using Hell's/Halo's Gate).
2.  The malware searches `ntdll.dll` memory for an existing, legitimate `syscall` instruction (`0x0F 0x05`).
3.  The malware prepares the registers (setting `R10` and `EAX` with the SSN).
4.  Instead of executing its own `syscall` instruction, the malware executes a `JMP` (Jump) instruction pointing to the legitimate `syscall` instruction found inside `ntdll.dll`.

*   **The Result:** When the kernel executes the syscall, the Return Instruction Pointer (RIP) points to a valid location within `ntdll.dll`. To the EDR and ETW-TI, the call appears completely legitimate.

## 5. Visualizing Indirect Syscalls

```ascii
+-----------------------------------------------------------------------------------+
|                           INDIRECT SYSCALL ARCHITECTURE                           |
|                                                                                   |
|  [ MALWARE PROCESS MEMORY ]                                                       |
|                                                                                   |
|  1. Resolve SSN (e.g., EAX = 0x18 for NtAllocateVirtualMemory)                    |
|  2. Find 'syscall' instruction address in ntdll.dll (e.g., 0x7FF...A12)           |
|                                                                                   |
|  [ Assembly Execution ]                                                           |
|  mov r10, rcx                                                                     |
|  mov eax, 0x18                                                                    |
|  jmp 0x7FF...A12  ----------------------------------+                             |
|                                                     |                             |
|-----------------------------------------------------|-----------------------------|
|  [ ntdll.dll MEMORY SPACE ]                         |                             |
|                                                     |                             |
|  ...                                                v                             |
|  NtAllocateVirtualMemory:                           |                             |
|  E9 xx xx xx xx (EDR HOOK - BYPASSED)               |                             |
|  ...                                                |                             |
|  0x7FF...A12:  syscall   <--------------------------+ (Execution jumps here)      |
|                ret                                                                |
|-----------------------------------------------------------------------------------|
|                                 KERNEL MODE (Ring 0)                              |
|                                                                                   |
|  SSDT checks Origin RIP. Origin is ntdll.dll. Call is permitted and unlogged.     |
+-----------------------------------------------------------------------------------+
```

## 6. Real-World Attack Scenario

### The Scenario: Evasive Process Injection
An advanced red team needs to inject a beacon into `explorer.exe`. They are facing an industry-leading EDR that utilizes userland hooking, ETW-TI call stack analysis, and kernel callbacks.

1.  **Preparation:** The red team's loader implements Tartarus' Gate to dynamically resolve SSNs for `NtOpenProcess`, `NtAllocateVirtualMemory`, `NtWriteVirtualMemory`, and `NtCreateThreadEx`.
2.  **Execution:** The loader initiates the injection process utilizing Indirect Syscalls.
3.  **The Bypass:**
    *   The userland hooks in `ntdll.dll` are bypassed because execution jumps directly to the `syscall` instruction.
    *   ETW-TI call stack analysis passes because the RIP points to `ntdll.dll`, making the call appear as if it originated from a benign system library.
    *   To evade the kernel callback for `NtCreateThreadEx`, the loader spoofs the thread start address to point to `RtlUserThreadStart` (a legitimate thread entry point), hiding the true location of the malicious shellcode.
4.  The beacon executes flawlessly. The EDR fails to correlate the memory allocation and thread creation to the loader executable.

## 7. Defensive Mitigations

Defending against Indirect Syscalls is notoriously difficult for software-based EDRs.
1.  **Hardware-Assisted Telemetry:** Utilizing Intel PT (Processor Trace) to track execution flow at the CPU level, identifying jumps from unbacked memory directly to syscall instructions.
2.  **Call Stack Validation (Advanced):** While the immediate RIP points to `ntdll.dll`, deep inspection of the entire call stack by the kernel driver can reveal that frames further up the stack originate from unbacked memory (the malware). EDRs are increasingly implementing inline stack walking on sensitive kernel callbacks.
3.  **Heuristics on Process Memory:** Regardless of *how* the memory was allocated (via hooked API or indirect syscall), periodic scanning of the target process (`explorer.exe`) will eventually find the injected, executable payload if Sleep Obfuscation is not utilized.

## 8. Chaining Opportunities

Indirect Syscalls are the ultimate foundation for evasive operations. They should be used to implement the behavioral bypasses discussed previously:
*   Use Indirect Syscalls to perform the stealthy memory allocations required for [[03 - Bypassing Heuristics and Behavioral Analysis]].
*   Use Indirect Syscalls to load custom encryption routines to bypass static analysis as discussed in [[02 - Bypassing Static Signatures and YARA]].

## 9. Related Notes

*   [[99.01 - Modern EDR Architecture and Detection Mechanisms]]
*   [[99.04 - Unhooking Userland APIs EDR Bypass]]
*   [[System Service Descriptor Table (SSDT) Hooking]]
*   [[x64 Assembly and Calling Conventions]]
*   [[Syswhispers3 Configuration and Usage]]
