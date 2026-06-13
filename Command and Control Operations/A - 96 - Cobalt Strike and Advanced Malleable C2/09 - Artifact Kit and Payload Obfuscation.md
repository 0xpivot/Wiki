---
tags: [cobalt-strike, malleable-c2, red-team, vapt]
difficulty: advanced
module: "96 - Cobalt Strike and Advanced Malleable C2"
topic: "96.09 Artifact Kit and Payload Obfuscation"
---

# Artifact Kit and Payload Obfuscation

## Introduction to the Artifact Kit
When an operator generates an executable (e.g., an `.exe` or `.dll`) from Cobalt Strike—whether it's an initial stager, a stageless payload, or a lateral movement artifact—it does not simply dump raw shellcode to disk. The raw shellcode is highly signatureable. Instead, Cobalt Strike uses the **Artifact Kit**.

The Artifact Kit is a source code framework that provides templates for generating these executables. It acts as a wrapper, taking the raw Beacon shellcode, obfuscating it, packaging it within a compiled executable, and providing the execution logic to execute that shellcode in memory upon execution. By default, the Artifact Kit uses predictable templates that are immediately flagged by almost all Antivirus (AV) and Endpoint Detection and Response (EDR) solutions. Customizing the Artifact Kit is mandatory for any serious Red Team engagement to bypass static analysis, heuristics, and sandbox execution.

## Core Concepts of Payload Obfuscation
The goal of the Artifact Kit is to take a piece of malicious code (the shellcode) and deliver it to memory safely. This involves several stages of obfuscation and evasion.

### Static Evasion
Static analysis by AV involves scanning the file on disk without executing it. To bypass this, the shellcode within the artifact must be obfuscated.
- **Encoding/Encryption:** The Artifact Kit can use XOR, AES, or custom encryption routines to hide the shellcode. The decryption key is often hardcoded in the stub or generated dynamically.
- **String Obfuscation:** Import Address Table (IAT) reconstruction and string encryption ensure that suspicious API calls (like `VirtualAlloc`, `CreateThread`) are not visible in the binary's import table.
- **Resource Stuffing/Padding:** Adding large, benign resources (like icons, version information, or large blocks of null bytes) can change the file hash, disrupt entropy analysis, and sometimes bypass sandboxes that have file size limits.

### Heuristic and Behavioral Evasion
Once the executable runs, heuristic engines and sandboxes monitor its behavior.
- **Anti-Debugging/Anti-Sandbox:** The artifact can perform checks to determine if it is running in a virtual machine or debugger (e.g., checking CPU cores, memory size, uptime, or looking for specific VM driver files). If detected, the artifact terminates benignly.
- **Execution Delays:** Introducing sleep mechanisms (using techniques that bypass standard `Sleep` API hooking, such as mathematical loops or waitable timers) can outlast the execution time limits of automated sandboxes.

## Deep Dive: Customizing the Artifact Kit Templates

The Artifact Kit is provided as a zip file containing C source code and a build script (usually targeting MinGW). To use a custom kit, the operator compiles it and loads the resulting `.cna` (Cobalt Strike Aggressor Script) file into the client.

### The Bypass Techniques

The standard Artifact Kit provides several techniques for hiding and executing the shellcode:

1. **Mailbox (VirtualAlloc):** The classic technique. It allocates memory, copies the decrypted shellcode, and creates a thread. Highly signatureable.
2. **Pipe:** Creates a named pipe, writes the shellcode to it, and reads it back into executable memory. This breaks up the sequential flow of standard injection, confusing some basic behavioral analysis engines.
3. **Read/Write:** Uses `CreateFile`, `WriteFile`, and `ReadFile` to move the shellcode around before execution.

### Implementing Direct System Calls (Syscalls)
The most significant upgrade to a custom Artifact Kit is the integration of Direct System Calls (often utilizing frameworks like SysWhispers2 or TartarusGate). EDRs place hooks in `ntdll.dll` to intercept API calls like `NtAllocateVirtualMemory`. By implementing direct syscalls within the Artifact Kit, the compiled executable contains the necessary assembly instructions to interface directly with the Windows kernel, completely bypassing user-mode hooks.

## Detailed Table: Anti-Sandbox Techniques

| Technique | Method | Goal | Evasion Target |
| :--- | :--- | :--- | :--- |
| **CPU Core Check** | Query `GetSystemInfo` for `dwNumberOfProcessors`. Exit if < 4. | Sandboxes usually run on 1-2 vCPUs to save resources. | Cuckoo Sandbox, FireEye AX |
| **Memory Size Check** | Query `GlobalMemoryStatusEx`. Exit if < 4GB RAM. | Sandboxes are often heavily resource-constrained. | Cloud-based AV Emulators |
| **Uptime Verification** | Call `GetTickCount64`. Exit if uptime is under 15 minutes. | Sandboxes restart frequently and have low uptimes. | Automated triage systems |
| **Domain Join Check** | Query `NetGetJoinInformation`. Exit if not joined to a domain. | Corporate endpoints are domain-joined; sandboxes are not. | Generic isolated analysis networks |

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
|                            Artifact Kit Obfuscation Pipeline                      |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Cobalt Strike Client ]                                                         |
|         | 1. Request payload generation (e.g., Windows Executable)                |
|         v                                                                         |
|  [ Team Server ]                                                                  |
|         | 2. Generate raw Beacon Shellcode                                        |
|         | 3. Pass Shellcode to customized Artifact Kit (.cna script)              |
|         v                                                                         |
|  [ Artifact Kit Engine ]                                                          |
|         |                                                                         |
|         |-- a. Encrypt Shellcode (e.g., AES-256)                                  |
|         |-- b. Inject into C Template (e.g., bypass-pipe.c)                       |
|         |-- c. Add Anti-Sandbox logic (Check System Uptime > 2 hours)             |
|         |-- d. Implement Direct Syscalls (Bypass NTDLL hooks)                     |
|         |                                                                         |
|         v                                                                         |
|  [ MinGW Compiler ]                                                               |
|         | 4. Compile to executable (.exe / .dll)                                  |
|         v                                                                         |
|  [ Obfuscated Artifact ] (Delivered to Target)                                    |
|         |                                                                         |
|         |--> Target Execution Flow:                                               |
|              1. Anti-Sandbox Check (Passes)                                       |
|              2. Syscall: NtAllocateVirtualMemory (Bypasses EDR Hook)              |
|              3. Decrypt Shellcode into Memory                                     |
|              4. Syscall: NtCreateThreadEx (Executes Payload)                      |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

### Scenario: Bypassing Static AV and Sandbox Analysis via Custom Syscall Artifact

**Context:** The Red Team needs to deliver a stageless Beacon executable via a spear-phishing campaign. The target organization uses a prominent cloud-based AV solution that performs aggressive static analysis and executes unknown binaries in an isolated sandbox environment.

**Execution:**
1. **Kit Customization:** The operator modifies the Artifact Kit to incorporate SysWhispers2 for direct syscalls. They also implement an AES-256 encryption routine for the shellcode, rather than the default XOR.
2. **Sandbox Evasion:** The operator adds logic to the C template: before decryption occurs, the executable checks the number of CPU cores and the total system memory. If cores < 4 or memory < 4GB (common sandbox configurations), the executable immediately exits without error.
3. **Compilation:** The custom Artifact Kit is compiled and loaded into Cobalt Strike. The operator generates a Windows Executable (Stageless).
4. **Delivery:** The payload is delivered to the target via email.
5. **Static Analysis Phase:** The AV engine scans the file. The hashes do not match any known signatures. The IAT looks clean because critical APIs are resolved dynamically or replaced by syscalls. The shellcode is AES encrypted, appearing as high-entropy data indistinguishable from a compressed resource. The file is marked as "Unknown" and sent to the sandbox.
6. **Sandbox Phase:** The cloud sandbox executes the file. The artifact runs its hardware checks. Because the sandbox is configured with 2 virtual CPUs, the check fails, and the artifact exits. The sandbox records no malicious behavior and returns a "Clean" verdict.
7. **Execution Phase:** The user clicks the executable on their physical workstation (which has 8 cores and 16GB RAM). The hardware checks pass. The artifact uses direct syscalls to allocate memory, decrypts the AES payload, and executes the Beacon shellcode, bypassing local EDR hooks.

**Outcome:** The payload successfully bypasses both perimeter and endpoint defenses, establishing a C2 session.

## Detection Engineering Perspective
Detecting heavily obfuscated artifacts requires defense-in-depth, relying on behavioral analysis rather than static signatures.
- **Hunting for Direct Syscalls:** While direct syscalls bypass user-mode hooks, they do not bypass kernel-level telemetry (e.g., ETWti - Event Tracing for Windows Threat Intelligence). Defenders can utilize ETWti to monitor kernel-level API calls and correlate them with suspicious process behavior.
- **Mark-of-the-Web (MotW) Enforcement:** Ensure strict policies are in place to block or heavily restrict the execution of binaries that carry the MotW flag (indicating they were downloaded from the internet).
- **Entropy Analysis:** While attackers try to hide encrypted shellcode, large blocks of high-entropy data within a `.text` or `.data` section are inherently suspicious. EDRs should flag unknown binaries exhibiting this characteristic for deeper manual review.

## Chaining Opportunities
- The shellcode generated by the Artifact Kit is heavily influenced by the `stage` block. See [[06 - Malleable C2 PE and Memory Indicators]] to ensure the payload is stealthy once the artifact decrypts it into memory.
- The delivered artifact needs to establish a C2 connection safely. See [[08 - Crafting Advanced Malleable C2 Profiles for OPSEC]] for the network configuration.
- The delivery mechanism for this artifact is managed by the Resource Kit. See [[10 - Resource Kit and Web Delivery]].

## Related Notes
- [[13 - Introduction to Antivirus Evasion and Packing]]
- [[27 - Bypassing User-Mode API Hooks with Direct Syscalls]]
- [[48 - Advanced Sandbox Evasion Techniques]]
- [[96 - Cobalt Strike and Advanced Malleable C2/06 - Malleable C2 PE and Memory Indicators]]
- [[96 - Cobalt Strike and Advanced Malleable C2/10 - Resource Kit and Web Delivery]]

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
