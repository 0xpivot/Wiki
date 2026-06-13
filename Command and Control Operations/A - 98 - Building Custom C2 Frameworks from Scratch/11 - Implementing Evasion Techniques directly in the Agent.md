---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.11 Implementing Evasion Techniques directly in the Agent"
---

# 98.11 Implementing Evasion Techniques directly in the Agent

## Overview of Advanced Agent Evasion
When developing custom Command and Control (C2) agents, the primary challenge is surviving in heavily monitored environments protected by modern Endpoint Detection and Response (EDR) solutions. An agent must not only execute its payloads but also remain undetected during its idle phases (sleep). This document explores the theoretical concepts and defensive engineering aspects of advanced evasion techniques implemented directly within the agent's core architecture.

Modern EDRs employ a combination of userland hooking, Event Tracing for Windows (ETW), kernel-level callbacks (e.g., `ObRegisterCallbacks`, `PsSetCreateProcessNotifyRoutine`), and periodic memory scanning (YARA rules). To survive, an agent must blend into legitimate processes, mask its execution flow, and hide its memory footprint when not actively communicating.

## Core Evasion Concepts

### 1. Sleep Obfuscation
Agents spend the vast majority of their lifecycle sleeping, waiting for the next beacon interval. During this time, they are highly susceptible to memory scanners.
- **Concept:** By encrypting or obfuscating the agent's memory segments (specifically `.text` and `.data` sections) while sleeping, the agent evades static signature detection in memory.
- **Mechanism:** Techniques like Ekko, Foliage, or Gargoyle utilize Asynchronous Procedure Calls (APCs), waitable timers, and Return-Oriented Programming (ROP) chains to alter memory protections (e.g., from `RX` to `RW`), encrypt the memory region, sleep, decrypt the region, and restore executable permissions.
- **Defensive View:** Defenders look for anomalous thread states (e.g., threads in a `Wait:UserRequest` state originating from unbacked memory) and abnormal memory protection changes (`VirtualProtect` calls) executed via hardware breakpoints or kernel telemetry.

### 2. Thread Stack Spoofing
When an agent executes an action, the EDR may capture the thread's call stack via ETW-Ti (Event Tracing for Windows - Threat Intelligence). If the call stack originates from an unbacked memory region (a region not associated with a mapped DLL on disk), it is flagged as highly suspicious.
- **Concept:** Stack spoofing involves manipulating the call stack to make it appear as though the execution originated from a legitimate, benign function within a known Windows DLL (e.g., `ntdll.dll` or `kernel32.dll`).
- **Mechanism:** By carefully crafting fake stack frames and pushing them onto the stack before invoking a sensitive API, the agent creates a synthetic, legitimate-looking stack trace.
- **Defensive View:** Advanced telemetry can detect stack spoofing by analyzing stack frame unwinding metadata (unwind codes) and identifying logical inconsistencies in the return addresses.

### 3. Execution Flow Masking
Instead of directly executing shellcode or sensitive APIs, advanced agents proxy their execution through legitimate Windows components.
- **Concept:** Techniques such as Module Stomping (overwriting a loaded legitimate DLL with the agent's code) or APC Injection into suspended legitimate threads.

## Architectural ASCII Diagram: Sleep Obfuscation Lifecycle

```text
    +---------------------------------------------------+
    |             C2 Agent Execution Flow               |
    +---------------------------------------------------+
                             |
                             v
              +-----------------------------+
              | 1. Check-in with Teamserver |
              |    (HTTP/HTTPS/DNS/SMB)     |
              +-----------------------------+
                             |
                             v
              +-----------------------------+
              | 2. Receive Tasking & Sleep  |
              |    Interval (e.g., 60s)     |
              +-----------------------------+
                             |
                             v
    +---------------------------------------------------+
    |               SLEEP OBFUSCATION INIT              |
    +---------------------------------------------------+
    | a. Create Waitable Timer (Delay = 60s)            |
    | b. Build ROP Chain for Context Swapping           |
    | c. Queue APCs to execute ROP Chain                |
    +---------------------------------------------------+
                             |
                             v
    +---------------------------------------------------+
    |                 ROP CHAIN EXECUTION               |
    +---------------------------------------------------+
    | 1. VirtualProtect(Agent_Mem, PAGE_READWRITE)      |
    | 2. SystemFunction032(RC4_Encrypt, Agent_Mem)      |
    | 3. WaitForSingleObject(Timer_Handle, INFINITE)    | <--- AGENT IS NOW ASLEEP
    |    [MEMORY IS ENCRYPTED, YARA SCANS FAIL]         |
    | 4. SystemFunction032(RC4_Decrypt, Agent_Mem)      |
    | 5. VirtualProtect(Agent_Mem, PAGE_EXECUTE_READ)   |
    +---------------------------------------------------+
                             |
                             v
              +-----------------------------+
              | 3. Agent Wakes Up & Resumes |
              |    Execution cleanly        |
              +-----------------------------+
```

## Educational Implementation: Conceptual APC Sleep Obfuscation

The following abstract C++ code snippet demonstrates the *theoretical* mechanism of using waitable timers and APCs to queue a sequence of events that encrypts the process memory, sleeps, and decrypts it. This is strictly for understanding how threat actors abuse asynchronous execution.

```cpp
#include <windows.h>
#include <iostream>

// Abstract concept: Using undocumented NTAPIs for execution
typedef NTSTATUS(NTAPI* NtTestAlert_t)();

void ConceptualSleepObfuscation(DWORD sleepDurationMs) {
    // 1. Create a waitable timer
    HANDLE hTimer = CreateWaitableTimerW(NULL, TRUE, NULL);
    LARGE_INTEGER dueTime;
    dueTime.QuadPart = -(LONGLONG)sleepDurationMs * 10000;
    SetWaitableTimer(hTimer, &dueTime, 0, NULL, NULL, FALSE);

    // 2. Prepare Contexts and ROP Chain (Abstracted)
    // In a real scenario, this involves capturing the thread context
    // and setting up ROP gadgets (e.g., finding `VirtualProtect` in kernel32)
    CONTEXT ropContext1 = { 0 };
    CONTEXT ropContext2 = { 0 };
    CONTEXT ropContext3 = { 0 };

    // Abstract definition of the ROP steps:
    // ropContext1: Calls VirtualProtect to make memory RW
    // ropContext2: Calls SystemFunction032 (RC4) to encrypt memory
    // ropContext3: Calls WaitForSingleObject on hTimer
    // ropContext4: Calls SystemFunction032 (RC4) to decrypt memory
    // ropContext5: Calls VirtualProtect to restore RX permissions

    // 3. Queue APCs to the current thread
    // The APCs will execute sequentially when the thread enters an alertable state
    /*
    QueueUserAPC((PAPCFUNC)VirtualProtectGadget, GetCurrentThread(), (ULONG_PTR)&ropContext1);
    QueueUserAPC((PAPCFUNC)EncryptionGadget, GetCurrentThread(), (ULONG_PTR)&ropContext2);
    QueueUserAPC((PAPCFUNC)SleepGadget, GetCurrentThread(), (ULONG_PTR)&ropContext3);
    QueueUserAPC((PAPCFUNC)DecryptionGadget, GetCurrentThread(), (ULONG_PTR)&ropContext4);
    QueueUserAPC((PAPCFUNC)RestoreProtectGadget, GetCurrentThread(), (ULONG_PTR)&ropContext5);
    */

    // 4. Trigger the APC chain by entering an alertable state
    NtTestAlert_t pNtTestAlert = (NtTestAlert_t)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtTestAlert");
    if (pNtTestAlert) {
        pNtTestAlert(); // Thread enters alertable state, APCs fire, agent goes to sleep encrypted.
    }
}
```

*Note: The above code is heavily abstracted and non-functional without the explicit ROP gadget resolution and context manipulation functions. It serves only to illustrate the control flow of APC-based evasion.*

## Defensive Strategies & Detection Engineering

Defenders have evolved to detect these sophisticated evasion mechanisms. To build an effective C2, a Red Teamer must understand how Blue Teams hunt.

1.  **Memory Scanning Innovations:** Modern EDRs don't just rely on static YARA rules. They look for entropy. An encrypted `.text` section will have extremely high entropy compared to normal executable code. EDRs can flag processes with high-entropy executable regions.
2.  **Call Stack Analysis (ETW-Ti):** When `VirtualProtect` or `VirtualAlloc` is called, the kernel emits an ETW-Ti event. Defenders correlate this event with the call stack. If the stack is spoofed poorly (e.g., missing frame pointers or invalid unwind data), the EDR flags the behavior as malicious.
3.  **Thread State Monitoring:** Hunting for threads in an abnormal `Wait` state. If a thread is sleeping via an APC chain, its start address might point to `RtlUserThreadStart` but its actual execution context might be highly irregular. Tools like Hunt-Sleeping-Beacons analyze thread start addresses and wait reasons to identify obfuscated sleeps.
4.  **Hardware Breakpoints:** EDRs can utilize hardware breakpoints (via Debug Registers DR0-DR3) to monitor access to critical memory regions or functions without placing inline hooks, making detection harder for the agent to bypass.

## Real-World Attack Scenario

### Operation "Silent Night"
During a Red Team engagement against a tier-1 financial institution, the operators needed to establish a foothold on a workstation protected by a leading EDR. Standard commercial C2 agents (like default Cobalt Strike or Sliver) were being caught within minutes due to in-memory scanning.

The Red Team deployed a custom C2 agent written in C++ that implemented thread stack spoofing and Ekko-based sleep obfuscation.
1.  **Initial Access:** A tailored spear-phishing email delivered an ISO file containing an LNK payload.
2.  **Execution:** The LNK executed a legitimate signed binary vulnerable to DLL side-loading, loading the custom agent.
3.  **Evasion:** Upon execution, the agent dynamically resolved its APIs (avoiding the IAT) and immediately initiated a 60-minute sleep cycle using the APC/ROP chain method. The `.text` section of the DLL was XOR-encrypted in memory.
4.  **Action on Objectives:** When the agent woke up, it spoofed its call stack to mimic the execution flow of `explorer.exe` before querying the domain controller via LDAP. The EDR's telemetry recorded the LDAP query but attributed it to a benign process flow, resulting in zero alerts. The agent successfully maintained presence for 3 weeks.

## Chaining Opportunities

In-agent evasion techniques are rarely used in isolation. To maximize effectiveness, they should be chained with other operational security measures:
1.  Combine **Sleep Obfuscation** with **Direct Syscalls** to bypass userland hooks entirely while preparing the sleep cycle.
2.  Chain **Thread Stack Spoofing** with **Process Injection** techniques like Early Bird APC injection to ensure the injected payload starts with a clean, spoofed stack.
3.  Integrate **Environmental Keying**. The agent does not decrypt its core payload unless specific environmental variables (e.g., domain name, specific installed software) match the target environment, frustrating sandbox analysis.

## Related Notes

- [[13 - Obfuscating the Custom Agent AV EDR Evasion]]
- [[17 - Advanced Process Injection and Memory Allocation]]
- [[22 - Bypass ETW and ETW-Ti Telemetry]]
- [[34 - Designing Custom Malleable C2 Profiles]]
- [[05 - Red Team Infrastructure Setup and OPSEC]]
