---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.14 Evading Signatures with Unique Mythic Payloads"
---

# 97.14 Evading Signatures with Unique Mythic Payloads

## 1. Introduction to Payload Signaturing

In modern defensive environments, Endpoint Detection and Response (EDR) solutions and Antivirus (AV) engines rely heavily on static signatures to detect malicious payloads before execution. Static signatures evaluate file hashes, strings, Import Address Tables (IAT), and specific byte sequences (YARA rules).

When using open-source or commercial C2 frameworks, default payloads are inevitably signatured rapidly by security vendors. Mythic combats this through its modular, containerized architecture, allowing Red Teams to seamlessly integrate heavy obfuscation, encryption, and custom compilation pipelines directly into the payload generation process.

## 2. Mythic Payload Generation Pipelines

Mythic agents are not pre-compiled binaries sitting on the server. Every time an operator requests a payload, Mythic spins up the corresponding Docker container for that agent (e.g., the Apollo container or Poseidon container) and dynamically compiles the agent from source code.

This dynamic compilation step is the perfect choke point to introduce evasion techniques.

### 2.1 The Builder Script (`builder.py`)
In every Mythic agent container, a Python script (`builder.py`) dictates how the payload is compiled. Operators can modify this script to implement custom logic before the final artifact is delivered.

### 2.2 ASCII Diagram: Mythic Payload Generation Pipeline

```text
+--------------------------------------------------------------------------------+
|                             Mythic Operator UI                                 |
|  Configures Payload:                                                           |
|  - OS: Windows x64                                                             |
|  - C2 Profile: HTTP (http://c2.evil.com)                                       |
|  - Obfuscation: True (Custom Checkbox)                                         |
+--------------------------------------------------------------------------------+
                                     |
                                     v (JSON Tasking)
+--------------------------------------------------------------------------------+
|                      Mythic Core Server (RabbitMQ)                             |
+--------------------------------------------------------------------------------+
                                     |
                                     v (Triggers Build)
+--------------------------------------------------------------------------------+
|                     Agent Docker Container (e.g., Apollo)                      |
|                                                                                |
|  +--------------------------------------------------------------------------+  |
|  |  builder.py execution                                                    |  |
|  |                                                                          |  |
|  |  1. Generate C2 profile headers dynamically (inject UUIDs, URLs)         |  |
|  |  2. Source Code Modification: String Encryption / API Hashing            |  |
|  |  3. Compilation: cl.exe or MSBuild                                       |  |
|  |  4. Post-Compilation Processing (The Evasion Magic):                     |  |
|  |     - Obfuscator-LLVM (Control Flow Flattening, Bogus Flow)              |  |
|  |     - sRDI (Convert EXE/DLL to position-independent shellcode)           |  |
|  |     - Donut wrapper                                                      |  |
|  +--------------------------------------------------------------------------+  |
|                                                                                |
+--------------------------------------------------------------------------------+
                                     |
                                     v (Return Final Payload via API)
+--------------------------------------------------------------------------------+
|  Highly Obfuscated, Signature-Free Artifact Delivered to Operator              |
+--------------------------------------------------------------------------------+
```

## 3. Customizing the Agent Build Step for Evasion

To evade static signatures, operators must intercept the build process and alter the output. Here are the primary techniques integrated into Mythic builders.

### 3.1 String Encryption and API Hashing
Instead of relying on the agent developer to implement string encryption, the `builder.py` can be written to parse the source code, extract all strings, encrypt them using AES or XOR, and inject a decryption stub before compilation. 
Similarly, Win32 API calls (`VirtualAlloc`, `CreateThread`) can be dynamically replaced with hashed equivalents, forcing the agent to resolve APIs at runtime using the PEB, stripping the IAT of malicious indicators.

### 3.2 Obfuscator-LLVM Integration
For C/C++ agents, integrating Obfuscator-LLVM into the Docker build chain is highly effective. 
By adding compiler flags in the builder script:
```python
build_command = [
    "clang", "-mllvm", "-bcf", "-mllvm", "-bcf_loop=3", # Bogus Control Flow
    "-mllvm", "-fla",                                   # Control Flow Flattening
    "-mllvm", "-sub",                                   # Instruction Substitution
    "-o", "agent.exe", "main.c"
]
```
The resulting binary's control flow graph (CFG) is entirely mangled, rendering traditional YARA rules and reverse engineering efforts significantly more difficult.

### 3.3 Shellcode Wrapping via Donut and sRDI
Often, Red Teams do not want an EXE or DLL; they want raw shellcode to inject into a legitimate process.
The builder script can seamlessly invoke Donut or sRDI (Shellcode Reflective DLL Injection) post-compilation:

```python
import donut

# Post-compilation step in builder.py
def post_process_payload(self, executable_path):
    shellcode = donut.create(file=executable_path, arch=2) # 2 = x64
    with open("payload.bin", "wb") as f:
        f.write(shellcode)
    return "payload.bin"
```
Mythic will then return `payload.bin` directly to the operator, ready for advanced loader techniques.

## 4. Evading YARA and Default Indicators

Security vendors often signature the default configurations of C2 profiles. 
1. **HTTP Headers:** Default Mythic profiles might use specific User-Agents or HTTP headers (e.g., hardcoded `User-Agent: Mythic/1.0`). Changing these dynamically in the UI and ensuring the builder embeds randomized headers destroys these trivial signatures.
2. **Sleep Times and Jitter:** Hardcoded sleep intervals create predictable network beaconing patterns. Using the builder to randomize the default sleep and jitter per-payload prevents network intrusion detection systems (NIDS) from clustering agent beacons.
3. **Rich Headers:** The Microsoft linker includes "Rich Headers" in PE files. Stripping these or copying them from a legitimate binary (like `explorer.exe`) during the build process can bypass machine-learning models analyzing PE anomalies.

## 5. Real-World Attack Scenario

**The Environment:** A targeted attack against an organization running SentinelOne. Previous attempts to drop default Cobalt Strike or standard Mythic Apollo executables resulted in immediate quarantine and SOC alerts.

**The Execution:**
1. The Red Team modifies the Apollo `builder.py` within their Mythic instance.
2. They integrate the `Donut` python module to generate shellcode, and then wrap that shellcode using a custom AES encryption script directly within the builder.
3. The operator generates a payload via the Mythic UI, checking a custom "Generate Encrypted Shellcode" parameter.
4. Mythic dynamically compiles the agent, passes it to Donut, encrypts the shellcode, and returns a binary blob.
5. The operator utilizes a custom D/Invoke loader written in C# that decrypts the blob in memory and executes it via a thread hijacking technique.
6. SentinelOne analyzes the loader on disk but finds no malicious strings, IAT hooks, or known agent byte sequences.
7. Execution succeeds, and the agent calls back successfully.

## 6. Chaining Opportunities

- **[[11 - Integrating BOFs in Mythic]]**: Once the highly evasive payload executes and establishes a session, operators should exclusively use BOFs for post-exploitation to maintain the memory-evasion footprint.
- **[[15 - Mythic Scripting API Automating Operations]]**: Use the Scripting API to automatically generate dozens of uniquely obfuscated payloads on a schedule, rotating them on the Red Team's staging servers to defeat rapid signaturing.
- **[[12 - Developing Custom Mythic Agents from Scratch]]**: Developing a custom agent inherently bypasses many signatures; combining it with the advanced build pipelines described here creates an incredibly resilient tool.

## 7. Related Notes
- [[11 - Integrating BOFs in Mythic]]
- [[12 - Developing Custom Mythic Agents from Scratch]]
- [[15 - Mythic Scripting API Automating Operations]]
- [[55 - Advanced Loader Techniques and Memory Injection]]
- [[77 - YARA Rule Creation and Evasion]]
