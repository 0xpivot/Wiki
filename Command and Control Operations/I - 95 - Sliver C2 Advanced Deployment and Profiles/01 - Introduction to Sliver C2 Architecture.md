---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.01 Introduction to Sliver C2 Architecture"
---

# 95.01 Introduction to Sliver C2 Architecture

## Overview of Sliver C2

Sliver is an advanced, open-source cross-platform adversary emulation and Command and Control (C2) framework developed by Bishop Fox. Written primarily in Golang, Sliver provides a robust suite of capabilities designed to simulate sophisticated threat actors and Advanced Persistent Threats (APTs). As threat hunting teams mature, understanding the architecture, deployment, and operational mechanisms of frameworks like Sliver becomes critical for developing effective detection engineering strategies.

Unlike older frameworks that rely heavily on single-platform payloads or unencrypted staging mechanisms, Sliver is designed with modern operational security (OPSEC) in mind. It embraces a "stageless by default" methodology, compiles cross-platform implants, and integrates seamlessly with modern evasive techniques like Object File (BOF) execution and memory-safe execution environments.

### Core Architectural Components

Sliver's architecture operates on a modern client-server model heavily utilizing gRPC and Protocol Buffers for internal communication, and a variety of encrypted protocols for implant-to-server communication.

#### 1. The Team Server (sliver-server)
The Team Server is the centralized brain of the operation. It manages all active listener services, maintains the backend database, handles the compilation of new implants, and coordinates multiple operators connected to the infrastructure. 
- **Backend Database**: Sliver uses a local embedded database (typically BoltDB or SQLite depending on the version and configuration) to track connected implants, operators, and captured data (loot).
- **Compilation Engine**: The server requires a full Golang toolchain and cross-compilers (like MinGW-w64 for Windows targets) to dynamically compile implants on the fly based on operator requests.

#### 2. The Client (sliver-client)
The client is a standalone binary used by operators to interact with the Team Server. It communicates securely with the server over mTLS on a dedicated administration port (default 31337). This separation allows the server to be hosted securely in the cloud behind redirectors, while operators connect from secure, local workstations.

#### 3. The Implants (Beacons and Sessions)
Implants are the payloads executed on the target systems. They are dynamically generated, statically linked binaries (or shellcode) that execute the adversary's instructions. Sliver supports two primary execution flows for its implants: Beacons (asynchronous) and Sessions (synchronous).

---

## Architectural Diagram

```text
+-----------------------------------------------------------------------------------+
|                                 ATTACKER INFRASTRUCTURE                           |
|                                                                                   |
|  +-----------------+        mTLS (Port 31337)        +-------------------------+  |
|  |                 | <=============================> |                         |  |
|  |  Operator 1     |                                 |    SLIVER TEAM SERVER   |  |
|  | (sliver-client) |        mTLS (Port 31337)        |    (sliver-server)      |  |
|  +-----------------+ <=============================> |                         |  |
|                                                      |  - DB (Bolt/SQLite)     |  |
|  +-----------------+                                 |  - gRPC Handlers        |  |
|  |                 |                                 |  - Compiler (Go/MinGW)  |  |
|  |  Operator 2     |                                 |  - Listeners (mTLS, WG, |  |
|  | (sliver-client) |                                 |    HTTP/S, DNS)         |  |
|  +-----------------+                                 +------------+------------+  |
|                                                                   |               |
+-------------------------------------------------------------------|---------------+
                                                                    |
                                        +---------------------------+---------------------------+
                                        |                           |                           |
                                  HTTPS (Port 443)            mTLS (Port 8888)            DNS (Port 53)
                                        |                           |                           |
+---------------------------------------|---------------------------|---------------------------|---------------+
|                                       v                           v                           v               |
|                               +---------------+           +---------------+           +---------------+       |
| TARGET ENVIRONMENT            |   Redirector  |           |   Redirector  |           |   DNS Server  |       |
|                               | (Nginx/Apache)|           |    (Socat)    |           |    (Bind9)    |       |
|                               +-------+-------+           +-------+-------+           +-------+-------+       |
|                                       |                           |                           |               |
|                                       | HTTP/S C2 Profile         | mTLS Connection           | DNS TXT/NULL  |
|                                       v                           v                           v               |
|                               +---------------+           +---------------+           +---------------+       |
|                               |               |           |               |           |               |       |
|                               | Target Host 1 |           | Target Host 2 |           | Target Host 3 |       |
|                               | (Windows -    |           | (Linux -      |           | (Windows -    |       |
|                               |  Session)     |           |  Beacon)      |           |  Beacon)      |       |
|                               |               |           |               |           |               |       |
|                               +---------------+           +---------------+           +---------------+       |
+---------------------------------------------------------------------------------------------------------------+
```

---

## Under the Hood: gRPC and Protocol Buffers

Sliver's internal communication between the client and server relies heavily on **gRPC (gRPC Remote Procedure Calls)** and **Protocol Buffers (protobuf)**. 
- **gRPC**: Provides a high-performance, open-source universal RPC framework. It allows the client to directly call methods on the server application as if it were a local object.
- **Protocol Buffers**: Used for serializing structured data. When an operator runs a command like `ls`, the client constructs a protobuf message, serializes it, and sends it via gRPC to the server. The server forwards this over the respective C2 channel to the implant, which decodes the protobuf, executes the OS command, and returns the serialized result.

This structured approach makes Sliver highly reliable and easily extensible. Developers can define new capabilities by updating the protobuf definitions (`.proto` files) without needing to rewrite complex parsing logic.

### Threat Hunting Context: gRPC Artifacts
From a defensive perspective, identifying gRPC traffic in unexpected places can be a strong indicator of compromise. While the operator-to-server communication is typically encrypted via mTLS, analyzing the binaries themselves (if recovered) often reveals standard Golang gRPC libraries and protobuf structures.
- **Strings Analysis**: Look for imports like `google.golang.org/grpc` or `github.com/golang/protobuf` in suspicious binaries.
- **Network Telemetry**: While encrypted, the timing and flow of gRPC over mTLS often exhibit specific application-layer behavioral patterns distinct from standard web browsing, potentially identifiable via behavioral network traffic analysis (NTA).

---

## The Compilation Engine and Garble

A unique feature of Sliver is its built-in capability to dynamically compile implants using the Go toolchain. When an operator generates an implant, they pass parameters (e.g., OS, architecture, protocol, obfuscation flags).

If the `--obfuscate` flag is utilized, Sliver incorporates **Garble**, a popular Golang obfuscation tool. Garble replaces standard symbol names, package paths, and function names with randomized or hashed strings. It also strips debugging information and attempts to defeat basic static analysis signatures.

### Threat Hunting Context: Deobfuscating Golang
Hunting for Sliver implants requires understanding how Golang binaries are structured. 
- **Go Build ID**: Even obfuscated Go binaries retain a Build ID (unless explicitly stripped via advanced manipulation).
- **Section Headers**: Tools like `go-re` or analyzing `.gopclntab` (Go Program Counter Line Table) can sometimes recover execution structures even if strings are obfuscated.
- **YARA**: YARA rules targeting the runtime initialization routines of Go 1.18+ rather than specific strings provide higher fidelity detections against Sliver implants.

---

## Dynamic Implants vs Shellcode

Sliver supports generating multiple formats:
1. **Executable (.exe / .elf / .mach-o)**: Standard compiled binaries. Easy to execute but highly visible to Endpoint Detection and Response (EDR) solutions if dropped to disk.
2. **Dynamic Link Library (.dll)**: Often used for DLL search order hijacking or side-loading attacks.
3. **Shellcode**: By integrating with projects like **Donut** (for Windows), Sliver can convert its compiled Go binaries into position-independent shellcode. This is crucial for advanced operators who wish to inject the implant directly into the memory of a legitimate process (e.g., `explorer.exe` or `notepad.exe`) without the payload ever touching the disk.

---

## Real-World Attack Scenario

### Initial Access and Execution
An adversary targets a mid-sized financial institution. After conducting OSINT, they launch a targeted spear-phishing campaign against the HR department, attaching a weaponized ISO file containing a legitimate signed executable and a hidden, malicious DLL.

### Persistence and Execution
When the victim mounts the ISO and runs the legitimate executable, it vulnerable to DLL side-loading. It loads the malicious DLL, which contains an encrypted Sliver shellcode payload. The shellcode is decrypted in memory and executed, spawning a Sliver Beacon.

### C2 Communication
The Beacon is configured to communicate via HTTPS (Port 443) to a redirector domain (`cdn-update-services[.]com`) categorized as "Technology". The redirector forwards the traffic to the actual Sliver Team Server hosted on a bulletproof VPS.

### Lateral Movement
The attacker, interacting with the Sliver Team Server via the `sliver-client` from their own infrastructure, issues commands through the gRPC interface. They convert the Beacon into an interactive Session to run a BOF (Beacon Object File) that executes `Seatbelt` to enumerate local host configurations, followed by a pass-the-hash attack to move laterally to a high-value database server.

---

## Chaining Opportunities

Sliver's architecture does not exist in a vacuum. It is explicitly designed to integrate with other advanced red team capabilities.
1. **BOF Integration**: Sliver can load and execute Cobalt Strike Beacon Object Files (BOFs) via its `execute-bof` extension, allowing operators to leverage existing C-based post-exploitation tooling without needing to compile new Golang features.
2. **Donut / SRDI**: Integrating with tools that convert PE files to shellcode allows Sliver payloads to be loaded by customized loaders (e.g., Nim, Rust, or C# based droppers) tailored to bypass specific EDR hooks.
3. **Armory**: The Sliver Armory is an integrated package manager that allows operators to seamlessly install third-party aliases and extensions directly into the framework.

---

## Related Notes

- [[95.02 Deploying Sliver Team Server and Multiplayer Mode]]
- [[95.03 Generating Sliver Implants Beacons vs Sessions]]
- [[95.04 Sliver Listeners mTLS WireGuard HTTP DNS]]
- [[95.05 Customizing Sliver Profiles for OPSEC]]
- [[80.12 Introduction to gRPC and Protocol Buffers]]
- [[72.05 Advanced DLL Side-Loading Techniques]]
- [[65.09 Golang Binary Analysis and Deobfuscation]]

---
*Note: This material is intended for Threat Hunting, Detection Engineering, and authorized Red Team emulation purposes only. Analyzing adversary frameworks is critical for developing resilient defensive postures.*
