---
tags: [interview, threat-hunting, ir, qna, scenario]
difficulty: expert
module: "Interview Prep - Threat Hunting and IR"
topic: "QnA - TH Module 92"
---

# Threat Hunting QnA: Advanced Memory Forensics and Rootkit Detection

## Formal Technical Questions

### Q1: Explain Direct Kernel Object Manipulation (DKOM). How does a rootkit use DKOM to hide processes, and how can Volatility be used to detect it?
**Expert Answer:**
Direct Kernel Object Manipulation (DKOM) is a technique used by advanced rootkits to modify kernel-level data structures in memory without using standard API calls. This bypasses many traditional security monitoring tools that rely on API hooking.
*   **Hiding a Process:** In Windows, the kernel maintains a doubly linked list of `EPROCESS` structures (the `ActiveProcessLinks`). Each `EPROCESS` block represents a running process. To hide a process, a rootkit modifies the `Blink` (Backward Link) and `Flink` (Forward Link) of the adjacent `EPROCESS` structures to point to each other, effectively "unlinking" the target process from the list. The target process continues to run because the Windows thread scheduler uses threads (not the process list) for execution, but tools like Task Manager or `pslist` (which iterate the `ActiveProcessLinks`) will not see it.
*   **Detection with Volatility:**
    *   `windows.pslist`: Reads the `ActiveProcessLinks`. It will *not* show the hidden process.
    *   `windows.psscan`: Scans the memory image for pool tags (e.g., `Proc` for EPROCESS) associated with `EPROCESS` structures, regardless of whether they are linked. 
    *   By comparing the output of `pslist` and `psscan` (using a plugin like `windows.psxview`), a forensic investigator can identify "unlinked" processes—a strong indicator of DKOM. If `psxview` shows `False` in the `pslist` column but `True` in the `psscan` column, you have found a hidden process.

### Q2: What is the Virtual Address Descriptor (VAD) tree? How do you hunt for injected code (like a DLL or shellcode) using VAD analysis?
**Expert Answer:**
The Virtual Address Descriptor (VAD) tree is a self-balancing binary search tree maintained by the Windows Memory Manager to track the virtual address space allocated to a process. Every time a process allocates memory or maps a file (like a DLL), a new VAD node is created.
*   **Hunting for Injected Code:**
    *   **VAD Attributes:** When memory is allocated via `VirtualAllocEx` (often used in code injection), the memory protection is usually set to `PAGE_EXECUTE_READWRITE` (RWX). A legitimate DLL mapped into memory generally has `PAGE_EXECUTE_READ` for its text segment and `PAGE_READWRITE` for data, but rarely both. We hunt for VAD nodes with `PAGE_EXECUTE_READWRITE` protection.
    *   **Memory Mapping:** Legitimate executables and DLLs are mapped as `Mapped` or `Image` file types. Injected shellcode or unbacked code often resides in `Private` memory.
    *   **Volatility Plugin:** We use `windows.malfind` or `windows.vadinfo`. `malfind` specifically looks for VAD nodes with `PAGE_EXECUTE_READWRITE` (or similar executable protections) where the memory region contains executable code (e.g., starting with an MZ header or standard x86/x64 shellcode prologues) but is *not* mapped to a file on disk (unbacked).
    *   **Advanced Tip:** Attackers know about RWX detection. Sophisticated injectors map memory as RW, write the payload, and use `VirtualProtectEx` to flip it to RX. `malfind` might miss this. Advanced hunters must dump RX memory segments that are unbacked by files and scan them with YARA or inspect them for anomalous entropy.

## Scenario-Based Questions

### Q3: You are a senior incident responder. Antivirus software is silently disabled on a critical domain controller. The event logs are missing, and no suspicious processes are visible in Task Manager. You capture a memory dump. Walk me through your forensic process to uncover a suspected kernel-level rootkit.
**Expert Answer:**
**Phase 1: Environment Baseline & Process Analysis**
*   I will load the memory dump into Volatility 3 and run `windows.info` to determine the kernel profile and KDBG address.
*   Next, I execute `windows.psxview` to cross-reference multiple process listing techniques (pslist, psscan, thrdproc, csrss, session). If a process shows as `False` in `pslist` but `True` in `psscan`, I immediately suspect DKOM is hiding a user-land agent.

**Phase 2: Driver & Module Inspection**
*   Rootkits operate at Ring 0, usually via a malicious `.sys` driver. I will run `windows.modules` (traverses the kernel's doubly linked list of loaded modules) and `windows.modscan` (scans for module pool tags).
*   If `modscan` finds a driver that `modules` misses, the rootkit has unlinked itself from the loaded module list (Driver DKOM).
*   I will extract the suspicious driver using `windows.dumpfiles` for reverse engineering and static analysis.

**Phase 3: Hooking & Callback Analysis**
*   Rootkits often hook the System Service Descriptor Table (SSDT), Interrupt Descriptor Table (IDT), or specific I/O Request Packets (IRP) to intercept system calls (e.g., disabling AV, hiding files).
*   I will use plugins like `windows.ssdt` to look for function pointers that point outside the normal kernel module (`ntoskrnl.exe`) and point into an unknown driver's memory space.
*   I will also check for malicious kernel callbacks (Process/Thread creation callbacks, registry callbacks) which are commonly used by modern rootkits to block AV from starting. `windows.callbacks` will reveal unregistered or suspicious functions intercepting kernel events.

### Q4: An adversary has used the "Bring Your Own Vulnerable Driver" (BYOVD) technique to load an unsigned malicious driver. How does this work, and what artifacts are left in memory?
**Expert Answer:**
*   **The Technique:** Modern Windows enforces Driver Signature Enforcement (DSE), blocking unsigned drivers. To bypass this, attackers bring a legitimate, cryptographically signed driver (e.g., an old `capcom.sys`, `RTCore64.sys`, or `gdrv.sys`) that contains a known vulnerability (like an arbitrary memory read/write flaw). They load this signed driver, exploit the flaw from user-mode to overwrite kernel memory (specifically disabling DSE by modifying the `g_CiEnabled` or `g_CiOptions` variable in the `ci.dll` module), load their unsigned malicious rootkit, and then optionally re-enable DSE to cover their tracks.
*   **Memory Artifacts:**
    *   **The Vulnerable Driver:** Even if the attacker unloads the vulnerable driver, remnants may exist in memory. `windows.modscan` might find the unlinked driver object, or `windows.poolscanner` could find specific pool tags associated with the vulnerable driver's allocations.
    *   **DSE State Modification:** If we catch the machine while DSE is disabled, memory analysis of `ci.dll` will show the specific bits flipped.
    *   **Unbacked Kernel Memory:** The unsigned rootkit often has to be mapped manually into kernel space. We can hunt for anomalous executable memory pools in Ring 0 using advanced memory scanning, looking for MZ headers in non-module kernel memory areas.
    *   **Event Logs:** If Sysmon is running, Event ID 6 (Driver Loaded) will capture the initial load of the signed, vulnerable driver. Correlating this with sudden AV disabling is a classic BYOVD signature.

## Deep-Dive Defensive Questions

### Q5: Discuss the difference between IAT (Import Address Table) hooking and Inline Hooking. How are they executed, and how do you detect them via memory forensics?
**Expert Answer:**
*   **IAT Hooking:** The Import Address Table is an array of function pointers used by a PE (Portable Executable) file to resolve addresses of functions exported by other DLLs (like `kernel32.dll` or `ntdll.dll`). To hook via IAT, the attacker overwrites the target function's address in the IAT with the address of their malicious function.
    *   *Detection:* Memory forensics tools map the PE structure in memory and compare the function pointers in the IAT against the actual base addresses of the loaded DLLs. If a pointer inside an application's IAT resolves to a memory address outside the expected DLL bounds (e.g., pointing to a dynamically allocated RWX region), an IAT hook is confirmed.
*   **Inline Hooking (Detours):** Instead of modifying pointers, the attacker modifies the actual executable code of the target function itself (usually the first 5 bytes) with a `JMP` instruction pointing to the malicious payload.
    *   *Detection:* This requires comparing the in-memory `.text` segment of a loaded DLL with the legitimate version on disk (or comparing known good opcodes). Volatility plugins like `windows.apihooks` disassemble the first few instructions of common exported functions and check for anomalous `JMP`, `CALL`, or `PUSH/RET` instructions that hijack execution flow.

### Q6: How does Linux memory forensics differ from Windows, specifically regarding process structures and rootkit detection?
**Expert Answer:**
*   Linux does not use `EPROCESS` structures. Instead, it uses `task_struct` to represent processes.
*   Kernel modules (LKM rootkits) hide by unlinking themselves from the `modules` list (similar to Windows driver unlinking).
*   Volatility plugins like `linux.check_afinfo`, `linux.check_creds`, and `linux.hidden_modules` are essential.
*   Linux rootkits often hook the `sys_call_table`. Analysis involves comparing the in-memory `sys_call_table` pointers to the expected kernel text segment bounds.

## Custom ASCII Diagram: EPROCESS Unlinking (DKOM)

```text
Normal State (ActiveProcessLinks):
+----------------+      +----------------+      +----------------+
| EPROCESS A     |      | EPROCESS B     |      | EPROCESS C     |
| (lsass.exe)    |      | (malware.exe)  |      | (svchost.exe)  |
| Flink -------->|----->| Flink -------->|----->| Flink          |
| Blink          |<-----|<-------- Blink |<-----|<-------- Blink |
+----------------+      +----------------+      +----------------+

After DKOM (Unlinking EPROCESS B):
+----------------+                              +----------------+
| EPROCESS A     |                              | EPROCESS C     |
| (lsass.exe)    |----------------------------->| (svchost.exe)  |
| Flink -------->|        +----------------+    | Flink          |
| Blink          |<-------| EPROCESS B     |<---|-------- Blink  |
+----------------+        | (malware.exe)  |    +----------------+
                          | Flink (stale)  |
                          | Blink (stale)  |
                          +----------------+
                          *Hidden from APIs, but Thread Scheduler
                           still executes threads inside EPROCESS B.
                           Detected by comparing pslist with psscan.
```

## Real-World Attack Scenario
**The Turla Uroburos Rootkit**
The Turla APT group is known for deploying the Uroburos/Snake rootkit. In a high-security environment, incident responders noticed anomalous outbound C2 traffic via network flow analysis but found no associated process or socket on the endpoint.
A memory dump was acquired via FTK Imager. Analysts utilized Volatility to uncover advanced techniques: Uroburos was using custom NDIS (Network Driver Interface Specification) hooking to intercept network packets at the lowest level, bypassing user-land firewalls and host IDS. The rootkit also used kernel-mode DKOM to hide its user-land components and injected its C2 beaconing threads into the `svchost.exe` process space via asynchronous procedure calls (APCs), completely unbacked by files on disk. The investigation succeeded purely through aggressive pool scanning and IRP hook identification in memory, dumping the hidden driver for IDA Pro analysis.

## Chaining Opportunities
*   Memory forensics often chains with **Disk Forensics (NTFS/MFT Analysis)**; when an unlinked driver or unbacked memory region is dumped, its hash or YARA matches can be cross-referenced against the USN Journal or MFT to track exactly when and how the file dropped onto the disk.
*   **Reverse Engineering:** Suspicious injected memory segments (`.dmp` files extracted via `malfind`) are directly passed to decompilers like Ghidra or IDA Pro for payload analysis, uncovering C2 domains and encryption routines.

## Related Notes
*   [[14 - Direct Kernel Object Manipulation Techniques]]
*   [[33 - Windows Memory Management and VAD Structures]]
*   [[51 - Bypassing Driver Signature Enforcement BYOVD]]
*   [[66 - Advanced Volatility 3 Plugin Development]]
*   [[89 - Linux LKM Rootkits and Memory Forensics]]
