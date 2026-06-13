---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.14 Creating FUD Fully Undetectable Payloads"
---

# 99.14 Creating FUD Fully Undetectable Payloads

## Overview
Creating Fully Undetectable (FUD) payloads is the intricate process of modifying and obfuscating malicious code so that it bypasses static, signature-based, and heuristic detection mechanisms before and during execution. While true FUD is often a temporary state due to the rapid evolution of security definitions, the goal is to ensure the initial access payload can reside on disk, pass initial endpoint scans, and execute its primary function without triggering alerts.

## In-Depth Technical Mechanics
Security products rely on known signatures (file hashes, specific byte sequences) and heuristics (Import Address Tables, high entropy) to identify malware statically. FUD techniques focus on obscuring these indicators.

The core methodology involves separating the malicious payload (shellcode) from the execution logic:
1. **Encryption and Encoding:** The raw shellcode is encrypted using algorithms like AES, RC4, or custom XOR routines. This removes any known signatures from the payload itself. The payload is only decrypted in memory at runtime.
2. **Obfuscation:** The loader's code is obfuscated to confuse static analysis tools. This includes adding junk code, renaming variables to random strings, and disrupting control flow with useless jumps or calculations.
3. **API Hashing:** Security tools analyze a binary's Import Address Table (IAT) to determine its capabilities. A binary importing `VirtualAllocEx` and `CreateRemoteThread` is highly suspicious. API hashing circumvents this. The payload does not declare these imports. Instead, it dynamically resolves the necessary APIs at runtime by hashing the names of exported functions in `ntdll.dll` and comparing them to pre-calculated hashes hardcoded in the payload. This results in a clean IAT.
4. **Environmental Keying (Guardrails):** A sophisticated technique where the payload uses specific properties of the target environment (e.g., the Active Directory domain name, a specific MAC address, or a file path) as the decryption key for the shellcode. If the payload is executed in a sandbox or on a researcher's machine, the key will be incorrect, and the payload will merely decrypt into inert garbage, preventing analysis and signature generation.

## Memory and Kernel Structures
FUD techniques manipulate how the binary is structured and how it interacts with the OS:
- **PE Sections:** The structure of a FUD binary typically consists of a loader (stub) in the `.text` section and the encrypted payload stored elsewhere, often in the `.data` or `.rsrc` (resource) section.
- **Entropy:** Defenders analyze the entropy (randomness) of these sections. High entropy in a specific section is a strong indicator of packed or encrypted data, which can trigger deeper heuristic scans or behavioral analysis.
- **Process Environment Block (PEB):** Payloads often read the PEB to find the base addresses of loaded modules like `kernel32.dll` and `ntdll.dll` to perform dynamic API resolution without relying on the IAT.

## Architectural Diagram
```text
+-------------------+       +-------------------+
|   Raw Payload     |       |   Obfuscator      |
+--------+----------+       +--------+----------+
         |                           |
         +---------------------------> 1. Encrypt/Pack
                                     | 2. API Hashing
                                     v
                            +--------+----------+
                            | FUD Executable    |
                            +--------+----------+
                                     |
                                     | 3. Execution on Target
                                     v
                            +--------+----------+
                            | EDR Scanner       | -> Static Analysis (Bypassed)
                            +-------------------+    (No known signatures)
```

## Real-World Attack Scenario
A red team is executing a spear-phishing campaign against a hardened target. They need their initial macro-enabled document and the subsequent executable payload to bypass the target's strict static antivirus engine. They take a standard Cobalt Strike beacon shellcode and wrap it in a custom AES encryption routine. To avoid suspicion, they use API hashing to dynamically resolve memory allocation APIs, ensuring the executable's IAT appears benign. Finally, they implement environmental keying: the payload will only decrypt if the system's DNS suffix matches the target company's domain. The resulting executable has zero detections on VirusTotal and bypasses the target's initial email gateway scans. When the victim executes the payload, the environmental check passes, the shellcode decrypts in memory, and the C2 connection is established.

## EDR Telemetry and Detection Engineering
Detecting FUD payloads requires moving away from static signatures toward behavioral and memory analysis:
- **Entropy Analysis:** High entropy in binary sections, especially `.data` or `.rsrc`, should be flagged for deeper dynamic analysis or manual review.
- **Antimalware Scan Interface (AMSI):** For script-based payloads (PowerShell, VBScript), AMSI is critical. It inspects the content *after* it has been decrypted or deobfuscated in memory, but *before* the script engine executes it, allowing detection of the raw malicious commands.
- **Behavioral Detections:** Regardless of how heavily obfuscated a binary is statically, it must eventually execute its malicious intent (e.g., modifying registry run keys, injecting memory into other processes, making unusual network connections). Behavioral rules focus on catching these actions rather than identifying the file itself.

## Mitigation Strategies
Mitigating FUD payloads relies on a layered defense architecture:
- **Behavioral Analytics:** Deploy Endpoint Detection and Response (EDR) solutions with strong behavioral analytics and machine learning models that monitor process behavior over time rather than relying solely on static file scans.
- **AMSI Integration:** Ensure AMSI is enabled, updated, and integrated with your endpoint security tools to catch fileless threats and script-based obfuscation.
- **Application Control (Allowlisting):** Implement strict Application Control policies (like WDAC or AppLocker) to block the execution of any unknown, unsigned, or untrusted binaries, effectively neutralizing FUD payloads by preventing their execution entirely.

## Chaining Opportunities
A FUD payload's success is heavily dependent on bypassing dynamic analysis during execution:
- To maintain its stealth, the loader often utilizes techniques detailed in [[13 - Living off the Land C2 using Native APIs]] to avoid triggering user-mode hooks during the injection process.
- Developing a FUD payload requires rigorous continuous testing against modern sandboxes, as outlined in [[15 - Continuous Testing against EDR Sandboxes]], to ensure it doesn't reveal its behavior prematurely.

## Related Notes
- [[11 - Evading Memory Scanners Sleeping and Encrypting Memory]]
- [[12 - Malicious Driver loading and Bring Your Own Vulnerable Driver BYOVD]]
- [[13 - Living off the Land C2 using Native APIs]]
- [[14 - Creating FUD Fully Undetectable Payloads]]
- [[15 - Continuous Testing against EDR Sandboxes]]

## Extended Technical Glossary and Context
- **FUD:** Fully Undetectable, bypassing static and heuristic signatures.
- **Obfuscation:** Deliberately making code difficult to analyze.
- **Encryption:** Securing data so it can only be read with a key.
- **API Hashing:** Resolving imports by hash to hide API usage.
- **IAT:** Import Address Table, lists functions a binary imports.
- **Environmental Keying:** Decrypting payload based on specific target details.
- **Entropy:** Measure of randomness in data.
- **PEB:** Process Environment Block.
- **AMSI:** Antimalware Scan Interface, inspects scripts before execution.
- **Heuristic Analysis:** Detecting threats based on behavior and characteristics.
- **Shellcode:** Small piece of code used as the payload.
- **AES:** Advanced Encryption Standard.
- **XOR:** Exclusive OR, a simple encryption algorithm.
- **WDAC:** Windows Defender Application Control.
- **AppLocker:** Windows feature to restrict application execution.
- **VAPT:** Vulnerability Assessment and Penetration Testing.
- **C2:** Command and Control.
- **EDR:** Endpoint Detection and Response.
- **OPSEC:** Operations Security.
- **Static Analysis:** Analyzing code without executing it.
- **Dynamic Analysis:** Analyzing code by executing it in a controlled environment.
- **Signature:** A unique pattern identifying a specific threat.
- **Dropper:** Malware designed to install a payload on the target system.
- **Loader:** Malware designed to load the payload into memory.
- **Sandbox:** Isolated environment for testing suspicious files.
