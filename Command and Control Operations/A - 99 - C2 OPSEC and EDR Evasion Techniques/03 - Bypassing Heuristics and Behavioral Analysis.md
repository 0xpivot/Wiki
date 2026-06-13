---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.03 Bypassing Heuristics and Behavioral Analysis"
---

# 03 - Bypassing Heuristics and Behavioral Analysis

## 1. Introduction to Heuristics and Behavioral Analysis
If you have successfully navigated the pre-execution static analysis (as detailed in [[02 - Bypassing Static Signatures and YARA]]), your payload is now running in memory. This is where the true challenge begins. Modern EDRs rely heavily on dynamic, behavioral analysis—monitoring *what* a program does rather than *how it looks*.

Heuristics engines build execution graphs, tracking parent-child process relationships, API call sequences, network connections, and memory manipulations. Evasion at this stage requires fundamentally altering the execution flow of your malware to mimic benign activity, break telemetry chains, or exploit blind spots in the EDR's behavioral models.

## 2. Core Behavioral Detection Mechanisms

EDRs monitor behavior primarily through user-mode API hooking and kernel-mode callbacks.

### 2.1 Process Trees and Parent-Child Relationships
EDRs flag anomalies in process lineage. A common detection is `winword.exe` (Microsoft Word) suddenly spawning `cmd.exe` or `powershell.exe`. Similarly, `services.exe` spawning an unknown binary from the `%TEMP%` directory is highly suspicious.
*   **Detection:** High confidence indicator of compromise (IoC) regardless of payload obfuscation.

### 2.2 Memory Injection and Cross-Process Access
The Holy Grail of malware detection. EDRs strictly monitor APIs used for cross-process memory manipulation (e.g., `OpenProcess`, `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread`).
*   **Detection:** Process A allocating `PAGE_EXECUTE_READWRITE` (RWX) memory in Process B and subsequently creating a thread there is an almost guaranteed conviction for Process Injection.

### 2.3 API Call Call Stacks
When a monitored API (e.g., `NtAllocateVirtualMemory`) is called, the EDR examines the call stack. If the call stack reveals that the execution originated from an unbacked memory region (memory not associated with a legitimate DLL on disk), the EDR infers the presence of injected shellcode.
*   **Detection:** Detecting reflective DLL injection or shellcode execution within the current process.

## 3. Advanced Behavioral Evasion Techniques

To survive in-memory, Red Teamers must employ techniques that decouple the malicious action from the monitored context.

### 3.1 Parent Process ID (PPID) Spoofing
To defeat process tree analysis, malware can spoof its parent process. When calling `CreateProcess`, the attacker uses the `UpdateProcThreadAttribute` API to set the `PROC_THREAD_ATTRIBUTE_PARENT_PROCESS` attribute to a handle of a benign, expected parent (e.g., `explorer.exe`).
*   **Evasion:** The EDR's telemetry shows the new process originating from `explorer.exe` rather than the malicious dropper, blending into normal OS noise.

### 3.2 Advanced Process Injection (Beyond CreateRemoteThread)
Standard injection techniques are dead. Modern evasion requires stealthier memory manipulation.
*   **Module Stomping / Module Overloading:** Instead of allocating new, suspicious RWX memory, the attacker forces the target process to load a benign Windows DLL (e.g., `amsi.dll` or `xpsprint.dll`). The attacker then overwrites the executable sections of that legitimate, file-backed DLL in memory with their malicious payload. This defeats memory scanners looking for unbacked executable memory.
*   **Process Hollowing (with modifications):** Creating a legitimate process in a suspended state, unmapping its memory, and replacing it with malicious code. To evade modern EDRs, this must be combined with PPID spoofing and thread context manipulation (SetThreadContext) rather than `CreateRemoteThread`.

### 3.3 Call Stack Spoofing
To execute shellcode safely within the current process without triggering call stack anomalies, attackers spoof the call stack before invoking sensitive APIs.
*   **Mechanism:** By manipulating the stack frames (RBP/RSP registers) before a function call, the attacker constructs a fake, legitimate-looking call stack pointing to benign functions within `ntdll.dll` or `kernel32.dll`. When the EDR inspects the stack during the API call, it sees a normal execution flow, hiding the true unbacked origin of the shellcode.

### 3.4 Sleep Obfuscation (Ekko / Foliage / Gargoyle)
C2 beacons spend most of their time sleeping, waiting for commands. EDR memory scanners hunt for dormant shellcode during these sleep cycles.
*   **Mechanism:** Before calling `Sleep()`, the beacon encrypts its own executable memory pages (usually using ROP chains to call `VirtualProtect` and an encryption function). It then registers an Asynchronous Procedure Call (APC) or a timer to decrypt itself after the sleep period expires.
*   **Evasion:** While sleeping, the beacon appears as benign, encrypted data. It only becomes executable for the fraction of a second required to check in, significantly reducing the window of opportunity for memory scanners.

## 4. Visualizing Sleep Obfuscation (Ekko-style ROP)

```ascii
+-----------------------------------------------------------------------------------+
|                           SLEEP OBFUSCATION WORKFLOW                              |
|                                                                                   |
|  [ BEACON ACTIVE ] -> Time to Sleep (e.g., 60 seconds)                            |
|         |                                                                         |
|         v                                                                         |
|  1. Setup ROP Chain in Context Structure                                          |
|  2. Create Timer Queue (CreateTimerQueueTimer)                                    |
|         |                                                                         |
|         +--> Timer 1 (t=100ms): VirtualProtect (RWX -> RW)                        |
|         +--> Timer 2 (t=200ms): SystemFunction032 (RC4 Encrypt Memory)            |
|         +--> Timer 3 (t=300ms): Sleep (60,000ms)                                  |
|         |                                                                         |
|         v                                                                         |
|  [ BEACON SLEEPING (Memory is RW and Encrypted - Invisible to Scanners) ]         |
|         |                                                                         |
|         v (60 seconds later)                                                      |
|         |                                                                         |
|         +--> Timer 4 (t=60100ms): SystemFunction032 (RC4 Decrypt Memory)          |
|         +--> Timer 5 (t=60200ms): VirtualProtect (RW -> RWX)                      |
|         |                                                                         |
|         v                                                                         |
|  [ BEACON ACTIVE ] -> Check in with C2 -> Repeat                                  |
+-----------------------------------------------------------------------------------+
```

## 5. Real-World Attack Scenario

### The Scenario: Lateral Movement via WMI
An attacker has compromised a workstation and wants to move laterally to a high-value server using Windows Management Instrumentation (WMI).
1.  Using a standard WMI payload to spawn `powershell.exe -enc <payload>` on the remote server will immediately trigger the EDR's behavioral engine (WMI spawning an obfuscated command line).
2.  Instead, the attacker uses WMI to remotely spawn `dllhost.exe`, utilizing PPID spoofing to make it appear as if it was launched by `svchost.exe -k DcomLaunch` (the normal behavior for DCOM/WMI).
3.  The attacker then uses a stealthy injection technique (like Module Stomping) over SMB to write their shellcode into a loaded DLL within that remote `dllhost.exe` process.
4.  Finally, they trigger execution via an APC queue (QueueUserAPC) directed at a sleeping thread within `dllhost.exe`.
5.  Once executing, the C2 beacon utilizes Sleep Obfuscation. 

The EDR observes a normal process tree, no suspicious `CreateRemoteThread` calls, and memory scanners fail to find the beacon while it sleeps. The lateral movement is successful.

## 6. Defensive Mitigations

Detecting advanced behavioral evasion requires deep OS telemetry and correlation:
1.  **ETW-TI Analysis:** EDRs must heavily analyze Event Tracing for Windows - Threat Intelligence (ETW-TI) logs. ETW-TI provides kernel-level visibility into thread creation, memory allocation, and APC queuing that cannot be easily spoofed from user-mode.
2.  **Call Stack Validation via ETW:** Correlating ETW-TI thread creation events with the thread's start address and initial call stack to identify spoofing attempts.
3.  **Detecting ROP Chains:** Implementing heuristic checks for repeated, rapid executions of memory protection APIs (`VirtualProtect`) from unusual origins, which is indicative of sleep obfuscation ROP chains.

## 7. Chaining Opportunities

To execute the advanced techniques discussed here, you must ensure the APIs you are calling are not hooked by the EDR:
*   Before attempting Process Injection or Sleep Obfuscation, you must neutralize the user-mode sensors via [[04 - Unhooking Userland APIs EDR Bypass]].
*   For ultimate stealth, avoid hooked APIs entirely by implementing [[05 - Direct and Indirect Syscalls using HellsGates]].

## 8. Related Notes

*   [[99.01 - Modern EDR Architecture and Detection Mechanisms]]
*   [[Process Injection Techniques Anatomy]]
*   [[Return Oriented Programming (ROP) in Evasion]]
*   [[Windows Thread Pools and APCs]]
*   [[Advanced Cobalt Strike Malleable C2 Profiles]]
