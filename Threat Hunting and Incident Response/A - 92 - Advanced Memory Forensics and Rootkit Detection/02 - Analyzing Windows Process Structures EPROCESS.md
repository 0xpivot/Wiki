---
tags: [threat-hunting, forensics, memory, rootkits, vapt]
difficulty: advanced
module: "92 - Advanced Memory Forensics and Rootkit Detection"
topic: "92.02 Analyzing Windows Process Structures EPROCESS"
---

# Deep Dive into EPROCESS and Windows Process Internals

## The Executive Process (EPROCESS) Block
In the realm of Windows memory forensics, no structure is more pivotal than the `EPROCESS` block. The Windows kernel, specifically the Executive subsystem, tracks every running process using this monolithic, opaque kernel structure. Understanding `EPROCESS` is critical for memory analysts because nearly all process-related plugins in Volatility (like `pslist`, `psscan`, `dlllist`, `handles`) rely on dissecting this structure.

The `EPROCESS` block resides purely in kernel space (`System` memory) and cannot be directly accessed by user-mode applications. It acts as the central hub connecting all metadata, threading information, access tokens, and memory maps related to a specific process.

## Crucial Members of EPROCESS
The `EPROCESS` structure is enormous, containing hundreds of fields (members) that change subtly between Windows versions and builds. However, certain fields remain conceptually identical and are vital for forensics.

### 1. `UniqueProcessId` (PID)
This is the process identifier (PID). While straightforward, verifying the PID against other structures helps detect anomalies.

### 2. `ActiveProcessLinks`
This is arguably the most important field for forensics. It is a `LIST_ENTRY` structure (a doubly linked list) that links all active processes together.
- The `FLINK` (Forward Link) points to the `ActiveProcessLinks` field of the *next* process's `EPROCESS` block.
- The `BLINK` (Backward Link) points to the *previous* process's `EPROCESS` block.
The head of this list is typically stored in a kernel global variable like `PsActiveProcessHead`. Tools like Task Manager and `pslist` walk this exact linked list to display running processes.

### 3. `Token`
The `Token` member points to an `EX_FAST_REF` structure, which ultimately points to the `TOKEN` object for the process. This object defines the process's security context, including its privileges, user SID, and group SIDs. Analysts inspect this to identify privilege escalation (e.g., a standard user process running with a `SYSTEM` token).

### 4. `VadRoot`
This points to the root of the Virtual Address Descriptor (VAD) tree, an AVL tree that maps the virtual address space of the process. We will explore this deeper in later modules, but it tracks every memory allocation, memory-mapped file, and loaded DLL for the process.

### 5. `Peb` (Process Environment Block)
While `EPROCESS` is a kernel-mode structure, the `PEB` is a user-mode structure. The `EPROCESS.Peb` field is a pointer that bridges the gap, pointing to the PEB in user space. The PEB contains user-mode data like the image base address, loaded modules (DLLs via `InLoadOrderModuleList`), and process heap details.

## Thread Environment Block (TEB) & Process Environment Block (PEB)
Every process has exactly one PEB, but multiple threads. Each thread is managed in the kernel by an `ETHREAD` structure (similar to `EPROCESS`), and each thread has a user-mode counterpart called the Thread Environment Block (TEB).

- **PEB Location:** Can be accessed in user-mode via `FS:[0x30]` on 32-bit, or `GS:[0x60]` on 64-bit systems.
- **TEB Location:** Can be accessed via `FS:[0]` (32-bit) or `GS:[0]` (64-bit).

Malware often modifies the PEB directly (e.g., altering the `ImageBaseAddress` or hiding DLLs from the `Ldr` lists) because it is accessible from user mode without requiring kernel privileges.

## Walking the ActiveProcessLinks
Volatility's `windows.pslist` plugin works by reading the `PsActiveProcessHead` symbol and jumping from `FLINK` to `FLINK` through physical memory.

```text
=============================================================================
                  ASCII Diagram: EPROCESS Doubly Linked List
=============================================================================

       PsActiveProcessHead
               |
               v
  +--------------------------+          +--------------------------+
  |       EPROCESS 1         |          |       EPROCESS 2         |
  |       (System)           |          |       (smss.exe)         |
  |--------------------------|          |--------------------------|
  | PID: 4                   |          | PID: 348                 |
  |--------------------------|          |--------------------------|
  | ActiveProcessLinks       |          | ActiveProcessLinks       |
  |   FLINK ----------------------------> FLINK -----------------------> ...
  |   BLINK <---------------------------- BLINK <----------------------- ...
  |--------------------------|          |--------------------------|
  | Token (SYSTEM)           |          | Token (SYSTEM)           |
  | VadRoot                  |          | VadRoot                  |
  +--------------------------+          +--------------------------+
=============================================================================
```

## DKOM (Direct Kernel Object Manipulation) Principles
Direct Kernel Object Manipulation (DKOM) is an advanced rootkit technique that directly alters kernel structures in memory to hide activity.
Because the operating system relies on structures like `ActiveProcessLinks` to track processes, a rootkit operating in kernel mode (Ring 0) can simply overwrite the `FLINK` and `BLINK` pointers to bypass a specific `EPROCESS` block. 

When a process is "unlinked" from `ActiveProcessLinks`:
1. Task Manager, `pslist`, and other standard APIs will no longer see the process.
2. However, the `EPROCESS` block still exists in memory.
3. The process continues to execute because thread scheduling is handled by `ETHREAD` blocks linked to the dispatcher database, not the `ActiveProcessLinks` list.

## Real-World Attack Scenario
**Scenario:** During a threat hunt on a high-value database server, an analyst notices an abnormal spike in database queries originating locally. 

**Incident Response Steps:**
1. A memory capture is analyzed with Volatility 3.
2. The analyst runs `windows.pslist` and identifies a suspicious process named `svchost.exe` running from `C:\Users\Public\svchost.exe`.
3. To understand its capabilities, the analyst inspects the EPROCESS Token using `windows.privileges.Privs`.
4. The investigation reveals that this instance of `svchost.exe` has the exact same security token address as the `lsass.exe` process (a process that normally runs as `NT AUTHORITY\SYSTEM`).
5. This indicates an attacker has successfully performed a "Token Stealing" attack. They used an exploit to read memory, locate the `EPROCESS` block for `lsass.exe`, copied its `Token` pointer, and overwrote the `Token` pointer in the `EPROCESS` block of their malicious `svchost.exe`. 
6. By manipulating the `EPROCESS` structure directly, the malware seamlessly elevated its privileges from standard user to `SYSTEM` without spawning noisy `cmd.exe` instances or utilizing known exploit primitives tracked by EDRs.

## Chaining Opportunities
- If you suspect a process has been manipulated out of the `ActiveProcessLinks`, proceed to [[03 - Detecting Hidden and Unlinked Processes]] to learn how to find them.
- `EPROCESS` heavily relies on the VAD tree for memory mapping, which is essential for identifying injected code as covered in [[04 - Hunting for Injected Threads and Hollowed Processes]].

## Related Notes
- [[Windows Privilege Escalation Techniques]]
- [[Kernel Security and Ring Architecture]]
- [[Direct Kernel Object Manipulation (DKOM)]]
- [[Exploitation: Token Stealing and Access Controls]]
