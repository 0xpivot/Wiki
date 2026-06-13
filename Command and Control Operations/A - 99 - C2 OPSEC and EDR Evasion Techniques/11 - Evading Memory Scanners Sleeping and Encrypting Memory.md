---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.11 Evading Memory Scanners Sleeping and Encrypting Memory"
---

# 99.11 Evading Memory Scanners Sleeping and Encrypting Memory

## Overview
Memory scanning is a foundational component of modern Endpoint Detection and Response (EDR) systems. EDRs periodically scan the memory space of processes to identify malicious patterns (using YARA rules) or suspicious memory allocations (such as unbacked RWX pages). In response, threat actors have developed memory evasion techniques, specifically sleep obfuscation and memory encryption, to hide payloads while they are inactive. From a defensive standpoint, understanding these mechanisms is crucial for developing robust memory forensics and behavioral detection strategies.

## In-Depth Technical Mechanics
When a Command and Control (C2) beacon goes idle, it typically enters a sleep state. If it remains unencrypted during this period, memory scanners can easily identify its signature. To circumvent this, advanced adversaries encrypt their memory space and alter memory protections before sleeping.

The general process involves:
1. **Identifying Payload Location:** The beacon locates its own base address and size in memory.
2. **Encryption:** The payload encrypts itself using algorithms like XOR or RC4.
3. **Changing Protections:** The memory region's protection is changed from executable (`PAGE_EXECUTE_READWRITE` or `PAGE_EXECUTE_READ`) to benign states like `PAGE_READWRITE` (RW) or `PAGE_NOACCESS` (NA) using `VirtualProtect`.
4. **Execution Delegation:** Since the payload cannot execute its own decryption routine while encrypted or residing in non-executable memory, it delegates this task. It queues Asynchronous Procedure Calls (APCs), utilizes Windows timers (`CreateTimerQueueTimer`), or employs Return-Oriented Programming (ROP) chains. These mechanisms trigger native Windows APIs (e.g., `SystemFunction032` for decryption) and restore memory protections (`VirtualProtect`) when the sleep period concludes.

## Memory and Kernel Structures
Understanding how these techniques interact with Windows internals is vital for detection:
- **Thread Environment Block (TEB) / Process Environment Block (PEB):** EDRs monitor threads associated with suspended or sleeping processes, analyzing their TEB for anomalies.
- **Virtual Address Descriptor (VAD):** The memory manager uses the VAD tree to track memory allocations. Defenders analyze the VAD to detect rapid transitions between RWX/RX and RW states on the same memory region.
- **Call Stacks:** When a thread is in a `DelayExecution` state, its call stack is scrutinized. Abnormal call stacks that point directly to ROP gadgets or unbacked memory rather than legitimate module execution flow are strong indicators of sleep obfuscation.

## Architectural Diagram
```text
+-------------------+       +-------------------+
|   C2 Framework    |       |   EDR Scanner     |
+--------+----------+       +--------+----------+
         |                           |
         | 1. Allocate Mem           |
         v                           |
+--------+----------+                |
|   RX/RWX Region   |                |
+--------+----------+                |
         |                           |
         | 2. Encrypt & Sleep        |
         v                           |
+--------+----------+                |
|   RW Region (Enc) | <--------------+ 3. Scan (No Detections)
+--------+----------+                | (Sees non-executable data)
         |                           |
         | 4. Wake via Timer/APC     |
         v                           |
+--------+----------+                |
|   RX/RWX Region   |                |
+-------------------+                |
```

## Real-World Attack Scenario
In a theoretical intrusion scenario, an adversary compromises an endpoint and injects a beacon into a legitimate process like `notepad.exe`. To evade the EDR's periodic 15-minute memory scans, the beacon uses an advanced sleep obfuscation technique (e.g., similar to Ekko or Foliage). Before entering a 30-minute sleep cycle, it sets up ROP chains via timers to handle its decryption. It then encrypts its own `.text` section and toggles the memory to `PAGE_READWRITE`. When the EDR scans the process, it only observes high-entropy, non-executable data. Upon waking, the timer executes the ROP chain, decrypting the payload and restoring `PAGE_EXECUTE_READ` so the beacon can communicate. The attack is eventually detected by threat hunters analyzing ETW-Ti telemetry for anomalous `VirtualProtect` sequences.

## EDR Telemetry and Detection Engineering
Detecting these techniques requires advanced behavioral telemetry and memory analysis:
- **Event Tracing for Windows - Threat Intelligence (ETW-Ti):** Monitoring `VirtualProtect` events is critical. Rapid or cyclical transitions of memory regions from executing states (RX/RWX) to non-executing states (RW) and back are highly suspicious.
- **Thread Call Stack Analysis:** Analyzing threads waiting in states like `DelayExecution` or `UserRequest`. If the call stack contains frames pointing outside of mapped image files (unbacked memory) or to known ROP gadgets, it warrants investigation.
- **Memory Scanning Tools:** Utilizing tools like `pe-sieve` or `Moneta` to identify unbacked memory regions, modified PE headers, or memory that is executing despite not being linked to a legitimate file on disk.

## Mitigation Strategies
Mitigation focuses on reducing the attack surface and enhancing visibility:
- **Strict Memory Policies:** Implement Endpoint Protection policies that block dynamic code generation or overly permissive memory allocations (RWX) where not strictly required by legitimate applications.
- **Application Control:** Use solutions like Windows Defender Application Control (WDAC) to prevent the initial execution of unauthorized binaries that might attempt these injection and evasion techniques.
- **Enhanced Telemetry Collection:** Ensure EDR sensors are configured to fully leverage ETW-Ti and kernel-level callbacks to gain visibility into memory manipulation and thread context changes.

## Chaining Opportunities
Sleep obfuscation and memory encryption are rarely used in isolation. They are frequently chained with:
- [[13 - Living off the Land C2 using Native APIs]] to perform the necessary memory protection changes and timer setups without triggering user-mode API hooks.
- Process injection techniques to hide within legitimate processes while sleeping.

## Related Notes
- [[11 - Evading Memory Scanners Sleeping and Encrypting Memory]]
- [[12 - Malicious Driver loading and Bring Your Own Vulnerable Driver BYOVD]]
- [[13 - Living off the Land C2 using Native APIs]]
- [[14 - Creating FUD Fully Undetectable Payloads]]
- [[15 - Continuous Testing against EDR Sandboxes]]

## Extended Technical Glossary and Context
- **ETW-Ti:** Event Tracing for Windows - Threat Intelligence, providing deep visibility.
- **ROP:** Return-Oriented Programming, chaining existing executable instructions.
- **APC:** Asynchronous Procedure Call, executes asynchronously in a thread context.
- **Syscalls:** Direct system calls used to bypass user-mode hooks.
- **VAD:** Virtual Address Descriptor, tracks virtual address spaces.
- **TEB:** Thread Environment Block, heavily analyzed during thread start validation.
- **PEB:** Process Environment Block, contains process-specific information.
- **Code Cave:** Unused memory section in an executing process.
- **Process Hollowing:** A technique where malicious code replaces a legitimate process.
- **Heuristic Analysis:** Detection method using behavioral rules.
- **Entropy:** Measure of randomness; high entropy indicates encryption or packing.
- **Obfuscation:** Making code difficult to read to bypass static signatures.
- **VBS:** Virtualization-Based Security.
- **HVCI:** Hypervisor-Protected Code Integrity.
- **Sleep Obfuscation:** Hiding executable payloads in memory by modifying protections.
- **Inline Hooking:** Interception method where instructions are overwritten.
- **TIB:** Thread Information Block.
- **IAT:** Import Address Table, used by executables to locate imported functions.
- **API Hashing:** Resolving functions by hashed name instead of plain text.
- **YARA:** Tool used to identify malware based on text/binary patterns.
- **NTAPI:** Native API used by Windows, often residing in ntdll.dll.
- **WDAC:** Windows Defender Application Control.
- **DSE:** Driver Signature Enforcement.
- **PPL:** Protected Process Light.
- **Memory Scanners:** Security tools that read RAM to find malicious code.
