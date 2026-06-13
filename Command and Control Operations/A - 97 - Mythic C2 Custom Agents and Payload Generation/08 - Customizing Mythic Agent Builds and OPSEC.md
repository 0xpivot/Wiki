---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.08 Customizing Mythic Agent Builds and OPSEC"
---

# Customizing Mythic Agent Builds and OPSEC

## Introduction
While the default agents provided by the Mythic C2 framework (Apollo, Poseidon, Athena) are incredibly powerful, using out-of-the-box payloads on advanced red team engagements is a guaranteed way to get caught. Endpoint Detection and Response (EDR) solutions signature the default build artifacts, default sleep mechanisms, and default network indicators of these agents.

Customizing Mythic agent builds is a critical skill. It involves modifying the builder source code, altering cryptographic implementations, integrating custom evasion loaders (e.g., D/Invoke, direct syscalls), and heavily obfuscating the final binary output before it ever reaches the target.

## Core Capabilities of Customization
- **Builder Overrides**: Modifying the Python `builder.py` scripts inside the Mythic agent Docker containers to inject custom compilation flags.
- **Sleep and Jitter Customization**: Replacing standard `Sleep()` calls with advanced thread obfuscation techniques (e.g., Ekko, Foliage).
- **IOC Eradication**: Stripping known strings, renaming namespaces, and randomizing struct names in the agent source.
- **Custom Cryptography**: Replacing the standard AES-256 implementation with custom cryptographic routines.
- **Loader Integration**: Outputting raw shellcode (Position Independent Code) instead of standard PE/ELF files for integration into custom droppers.

## Architecture and Build Flow

Mythic abstracts the build process using Docker containers and RabbitMQ. To customize a build, you must understand this pipeline.

```text
+----------------+      JSON Config       +-----------------------+
|  Mythic Web UI | ---------------------> |   RabbitMQ Message    |
|  (User Input)  |                        |   Queue (Internal)    |
+----------------+                        +-----------------------+
                                                     |
                                                     v
+-----------------------------------------------------------------+
|                    Agent Docker Container                       |
|                                                                 |
|  +-----------------+    +----------------+    +--------------+  |
|  | builder.py      | -> | Source Code    | -> | Compiler     |  |
|  | (Parses Config) |    | Modification   |    | (Go/C#/GCC)  |  |
|  +-----------------+    +----------------+    +--------------+  |
|                                                     |           |
+-----------------------------------------------------+-----------+
                                                      |
                                                      v
                                            +-------------------+
                                            | Final Payload     |
                                            | (EXE/BIN/Shellcode|
                                            +-------------------+
```

## Agent Execution & Loader Strategies

Instead of compiling an agent to an `.exe`, advanced operators modify the Mythic builder to generate raw shellcode. 

### Generating Position Independent Code (PIC)
For agents like Apollo (C#) or Athena (.NET), operators often use tools like `Donut` to convert the compiled assembly into shellcode.
By modifying `builder.py`, you can automate this:
```python
# Snippet inside a custom builder.py
def build(self):
    # ... compile C# to EXE ...
    os.system(f"donut.exe -i {output_exe} -o {output_bin} -a 2 -b 1")
    with open(output_bin, "rb") as f:
        payload = f.read()
    return BuildResponse(status=BuildStatus.Success, payload=payload)
```
The resulting shellcode is then embedded into a custom C/C++ loader that utilizes direct system calls (e.g., SysWhispers) to bypass API hooking.

## Configuration & Profiles

Modifying the C2 Profile is another layer of customization. EDRs inspect HTTP headers and URI parameters.

**Default HTTP Profile (Easily Caught):**
```json
{
  "USER_AGENT": "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
  "URI": "/api/v1/update"
}
```

**Highly Customized Profile (Blends in):**
```json
{
  "USER_AGENT": "Microsoft-Delivery-Optimization/10.0",
  "URI": "/msdownload/update/v3/static/trustedr/en/authrootstl.cab",
  "HEADERS": {
    "Accept-Language": "en-US",
    "Host": "update.microsoft.com"
  }
}
```
*Note: Ensure your redirector infrastructure properly handles these custom URIs and Host headers via Nginx or Apache.*

## Detailed OPSEC Modifications

| OPSEC Technique | Implementation in Mythic | Target EDR Bypass |
| :--- | :--- | :--- |
| **String Encryption** | Modify the agent source to encrypt static strings and decrypt them at runtime using XOR/RC4. | Static Analysis / YARA rules. |
| **Sleep Obfuscation** | Replace `Thread.Sleep` with ROP chains that alter memory protections during sleep (e.g., `Foliage`). | Memory Scanners (BeaconHunter, Moneta). |
| **Import Hiding** | Use D/Invoke in C# agents to dynamically resolve APIs instead of P/Invoke. | IAT (Import Address Table) Hooking. |
| **Syscall Integration** | Implement direct or indirect syscalls for critical functions (`NtAllocateVirtualMemory`). | User-land API Hooking (ntdll.dll hooks). |
| **Code Signing** | Post-process the generated binary with stolen/purchased valid code signing certificates. | SmartScreen & Basic AV trust models. |

## Real-World Attack Scenario

### Objective
A Red Team needs to bypass CrowdStrike Falcon on fully updated Windows 11 endpoints. 

### The Build
1. The operator clones the `Apollo` agent repository locally.
2. They modify the C# source code, replacing all P/Invoke API calls with D/Invoke to dynamically resolve unhooked NTDLL functions from disk.
3. They integrate a custom "Sleep Obfuscation" technique that encrypts the agent's heap and stack while it sleeps, making the process memory look benign to CrowdStrike's memory scanner.
4. The modified Apollo source is loaded into the Mythic Docker container.
5. The operator requests a shellcode build via the Mythic UI.
6. The resulting shellcode is encrypted with AES-256 and embedded into a custom C++ loader that uses Indirect Syscalls to allocate memory and execute.

### Execution
The C++ loader is executed via a DLL side-loading vulnerability in a legitimate Microsoft binary. CrowdStrike fails to detect the memory allocation due to indirect syscalls, and the sleep obfuscation prevents memory scanning detections during the C2 callback intervals.

## Detection Evasion / Blue Team Notes

Blue Teams must pivot from static signatures to behavioral heuristics:
- **Thread Call Stack Analysis**: Even with direct syscalls, the call stack often reveals anomalous origins (e.g., memory mapped as `RWX` or floating threads).
- **ETW-TI (Event Tracing for Windows - Threat Intelligence)**: EDRs utilizing ETW-TI can see memory protection changes (`VirtualProtect`) even if syscalls are used.
- Look for mismatched DLL loads or unknown binaries loading network-centric libraries (`wininet.dll`, `ws2_32.dll`).

## Chaining Opportunities
- Connect this to custom dropper creation: [[18 - Advanced C++ Malware Loaders and Syscalls]]
- Understand the infrastructure behind the profiles: [[05 - Nginx and C2 Redirector Setup]]

## Related Notes
- [[06 - Poseidon Agent macOS and Linux C2]]
- [[09 - Mythic Browser Scripts and UI Customization]]
