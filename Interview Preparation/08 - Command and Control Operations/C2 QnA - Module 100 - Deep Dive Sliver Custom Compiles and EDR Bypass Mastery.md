---
tags: [interview, c2, malware-dev, qna, scenario]
difficulty: expert
module: "Interview Prep - Command and Control Operations"
topic: "QnA - C2 Module 100"
---

# C2 QnA - Module 100 - Deep Dive Sliver Custom Compiles and EDR Bypass Mastery

```text
===================================================================================================
[ Sliver Custom Compilation Pipeline & Execution Architecture ]

 [ Developer Machine ]                          [ Target Machine Execution ]
 +-------------------+                          +--------------------------+
 | 1. Sliver Source  |                          | 1. Custom Initial Stager |
 |    Modification   |                          |    (Indirect Syscalls)   |
 +--------+----------+                          +------------+-------------+
          |                                                  |
          v                                                  v
 +-------------------+                          +--------------------------+
 | 2. Go Toolchain   |                          | 2. Reflective Loader     |
 |    (Garble CGO)   |  --- Encrypted Payload ->|    (Bypass PE Headers)   |
 | - trimpath        |                          +------------+-------------+
 | - buildid=        |                                       |
 +--------+----------+                                       v
          |                                     +--------------------------+
          v                                     | 3. Go Runtime Init       |
 +-------------------+                          |    (Obfuscated pclntab)  |
 | 3. Post-Compile   |                          +------------+-------------+
 |    Obfuscation    |                                       |
 |    (Packers/SGN)  |                                       v
 +-------------------+                          +--------------------------+
                                                | 4. Sliver Main Implant   |
                                                |    (Custom Named Pipes)  |
                                                +--------------------------+
===================================================================================================
```

## Formal Technical Questions

### Q1: How does Golang's runtime memory management and scheduling interact with Sliver's implant execution, and what specific modifications can be made to the Go compiler (e.g., using Garble) to drastically reduce the binary's static signature?
**Expert Answer:**
Golang uses a robust runtime containing a garbage collector (GC) and a custom scheduler (managing Goroutines via an M:N threading model). When a standard Sliver implant runs, the Go runtime spawns background threads for GC and system monitoring. EDRs easily profile these runtime characteristics and flag the massive statically-linked binary.
**Modifications & Garble Implementation:**
1. **The Signature Problem:** Go binaries contain a `pclntab` (Program Counter Line Number Table), which holds plaintext package paths, function names, and source file locations. A default Sliver compile leaves strings like `github.com/bishopfox/sliver/implant` completely visible.
2. **Garble Usage:** Using `garble` (a Go obfuscator), you compile the payload with command-line flags that randomize all package paths and function names dynamically.
   ```bash
   garble -tiny -literals -seed=random build -ldflags="-w -s -H=windowsgui -buildid=" main.go
   ```
3. **Deep Customization:**
   - `-tiny`: Strips the `pclntab` and optimization tables heavily, reducing file size and removing the structural signatures EDRs rely on.
   - `-literals`: Encrypts all static strings within the Go binary, decrypting them only at runtime.
   - `-buildid=`: Clears the build ID, a common static IOC used by YARA rules.
   - `-w -s`: Strips DWARF debugging information and the symbol table.

### Q2: Explain the process of creating and compiling custom Beacon Object Files (BOFs) for Sliver. How does Sliver handle the COFF loader mechanics under the hood?
**Expert Answer:**
Beacon Object Files (BOFs) are compiled, unlinked C code (Common Object File Format - COFF) that execute entirely in memory, avoiding the need to drop secondary tools to disk.
**Creation & Compilation:**
1. A developer writes a C program using the BOF API (e.g., declaring `DECLSPEC_IMPORT` for Windows APIs).
2. The code is compiled using `x86_64-w64-mingw32-gcc -c bof.c -o bof.o`. The `-c` flag ensures it is not linked into a full executable.
**Sliver COFF Loader Mechanics:**
Sliver (via its Armory extension) implements a custom COFF loader written in Go/CGO.
1. When a BOF is executed via Sliver (`bof_name`), the `.o` file is sent over the encrypted C2 channel.
2. The Sliver implant allocates memory for the BOF.
3. **Symbol Resolution:** The COFF file contains relocation tables. The Sliver loader parses these tables, locates the required Windows API functions via the PEB (Process Environment Block), and patches the addresses in the BOF memory space.
4. **Execution:** The loader sets up a custom stack, redirects execution to the BOF entry point (typically `go()`), captures standard output (`stdout`), and returns the results to the team server.

### Q3: Sliver utilizes a specific custom reflective DLL injection technique for its stagers. How can you modify the core loader stubs in Sliver's source code to evade memory-based detections like PE headers in memory?
**Expert Answer:**
Sliver's default shellcode stagers often use variations of Stephen Fewer’s Reflective DLL Injection. Memory scanners easily detect this by looking for the `MZ` and `PE` magic bytes in RWX memory regions.
**Source Code Modifications for Evasion:**
1. **Erasing the MZ/PE Headers:** Locate the C/C++ loader stub within Sliver’s source (often in the `sliver/implant/sliver` stager generation logic). Modify the reflective loader so that immediately after the DLL is mapped and relocated into memory, the loader calls `RtlSecureZeroMemory` on the first `0x1000` bytes (the DOS and NT headers).
2. **Custom Magic Bytes:** Modify the stager generation to replace the `MZ` (0x4D 0x5A) header with random bytes before transmission. The custom reflective loader in the implant is then modified to look for these custom bytes (e.g., `0xDE 0xAD`) instead of `MZ` to find the start of the payload.
3. **Stomping DOS Stub:** Overwrite the DOS stub (the "This program cannot be run in DOS mode" string) with shellcode NOP sleds or random garbage data.
4. **RWX to RX Transition:** Modify the loader so it maps the memory as RW (Read/Write), copies the payload, resolves imports, and then utilizes `VirtualProtect` to change the final permissions to RX (Read/Execute), avoiding the massive red flag of RWX memory.

---

## Scenario-Based Questions

### SQ1: You are leading a Red Team operation and your standard Sliver HTTP beacon is immediately flagged by Microsoft Defender for Endpoint (MDE) upon execution. You suspect behavioral detection rather than static signatures. How do you re-engineer the Sliver profile and execution chain to bypass this?
**Expert Answer:**
If MDE flags the beacon behaviorally, it is likely detecting the process tree, API call sequence, or network beaconing rhythm.
1. **Process Injection Profile:** Default Sliver profiles might spawn suspicious child processes (like `cmd.exe` or `powershell.exe`) when running commands. I would modify the Sliver profile to use **Spawnto** targeting legitimate, signed Windows binaries (e.g., `svchost.exe` or `RuntimeBroker.exe`).
2. **API Unhooking & Syscalls:** The behavioral detection is likely stemming from userland hooks in `ntdll.dll`. I would wrap the Sliver stager in a custom C/C++ loader (like a Nim/C++ dropper). This dropper would use **Indirect Syscalls** to allocate memory and use **Module Stomping** to inject the heavily obfuscated Garble-compiled Sliver payload.
3. **C2 Profile Evasion:** I would heavily modify the `http-c2.json` configuration. MDE inspects packet headers and frequency. I would implement extensive Jitter (e.g., 40%), manipulate the HTTP headers to spoof legitimate Microsoft telemetry traffic, and ensure the domain is properly categorized.

### SQ2: You are leading a Red Team operation and need to maintain long-term persistence using a customized Sliver implant. You want to leverage a custom C2 extension (Armory) but need to ensure it executes completely in memory without touching disk. Walk through your strategy.
**Expert Answer:**
Long-term persistence requires blending into the OS seamlessly.
1. **The Persistence Mechanism:** I would establish persistence via a WMI Event Subscription or a hidden Scheduled Task that executes a benign-looking application.
2. **The Loader:** The task executes a legitimate application subject to DLL Search Order Hijacking. Our custom proxy DLL is loaded by the benign app.
3. **Memory Execution:** The proxy DLL reaches out to a secure endpoint (e.g., an AWS S3 bucket), pulls down our customized, Garble-obfuscated Sliver stager (encrypted via XOR/AES), decrypts it entirely in memory, and executes it via thread hijacking.
4. **Armory Extension Usage:** To use extensions like `Seatbelt` or `Rubeus` from the Armory without disk artifacts, I utilize Sliver's `.net` in-memory execution capabilities (e.g., `execute-assembly`). Sliver utilizes the CLR (Common Language Runtime) hosting interfaces (`ICLRMetaHost`) to load the .NET assembly directly into the process memory, execute it, capture the output, and flush the AppDomain, leaving zero artifacts on disk.

---

## Deep-Dive Defensive Questions

### DQ1: How do malware analysts reverse engineer obfuscated Go binaries (like those produced by garble)? What specific structures (e.g., pclntab) do they look for to reconstruct function names?
**Expert Answer:**
Reversing Go binaries is notoriously difficult due to the large statically linked runtime, but analysts have specialized tools.
1. **Pclntab Extraction:** The `pclntab` is the holy grail for Go reversing. Analysts use tools like `GoReSym` or IDA Pro scripts (e.g., `go_parser`) to locate the magic bytes for the `pclntab`. Even if stripped, partial remnants often remain. By parsing this table, they map PC (Program Counter) offsets back to function names, recovering the entire structure of the Sliver implant.
2. **Type Information:** Go embeds rich type information (`moduledata`) for interfaces and reflection. Analysts parse this data to recover the exact structures of custom C2 packets or configuration blocks.
3. **Defeating Garble:** While Garble randomizes names (e.g., `pkg_a.Func_b`), the fundamental structure of the Go runtime remains. Analysts will use bindiffing against known Sliver builds. They identify core Go libraries (like `net/http` or `crypto/tls`) and map the randomized names back to their original functions based on basic block structure and system call patterns.

### DQ2: What are the hallmark network signatures of default Sliver TLS and WireGuard profiles, and how can threat hunters write Suricata rules to catch unmodified Sliver traffic?
**Expert Answer:**
Out-of-the-box C2 frameworks are highly signatureable.
1. **TLS Profiles:** Default Sliver generates self-signed certificates with predictable subjects (e.g., random capitalization, specific locality structures) or utilizes Let's Encrypt without proper domain aging. A Suricata rule can target the specific JA3 hash of the Go TLS client implementation used by Sliver.
   ```suricata
   alert tls $HOME_NET any -> $EXTERNAL_NET any (msg:"Suspicious Go TLS Client Hello (Sliver Default)"; ja3.hash; content:"e7d705a3286e19ea42f587b344ee6865"; sid:1000001; rev:1;)
   ```
2. **HTTP Profiles:** Default Sliver HTTP profiles often use a predictable set of URIs (e.g., `/login`, `/api/v1/update`) and predictable cookie structures (like a base64 encoded JWT token of a specific length). Suricata can flag HTTP requests lacking common browser headers (like `Accept-Language`) combined with these URIs.
3. **WireGuard (mTLS):** Sliver's WireGuard implementation has specific packet size characteristics during handshakes. Hunters look for UDP traffic on non-standard ports exhibiting the exact packet size cadence of a WireGuard initiation followed by sustained, uniform heartbeats.

---

## Real-World Attack Scenario

A ransomware affiliate attempting to deploy a payload in a mature healthcare environment opted for Sliver due to Cobalt Strike’s intense scrutiny. The actor pulled the Sliver source code and modified the core compilation pipeline. 
They stripped the `pclntab`, integrated **Garble**, and completely rewrote the internal Reflective DLL injection logic to erase PE headers dynamically. Furthermore, they modified the `named_pipes` configuration in the source. Instead of default Sliver pipes, they hardcoded the implant to utilize `\\.\pipe\sql\query`, mimicking Microsoft SQL Server. 
The MDE sensor, configured to trust internal SQL named pipes, completely ignored the lateral movement traffic. The actor successfully used the `execute-assembly` module in memory to run SharpHound and subsequently BloodHound, eventually escalating privileges to Domain Admin without triggering a single disk-based YARA signature.

---

## Chaining Opportunities

- **Combine with Module 98 (Custom Frameworks):** Understand the architectural differences between Sliver's Go implementation and a custom C++ framework to decide when to use off-the-shelf modified tools versus entirely bespoke malware.
- **Advanced Loaders (Module 99):** Do not rely on Sliver's built-in stagers. Chain a custom C++ loader utilizing Indirect Syscalls (from Module 99) to inject the heavily obfuscated Garble-compiled Sliver payload into a legitimate process.

---

## Related Notes
- [[Golang Malware Reverse Engineering]]
- [[Beacon Object Files (BOF) Development]]
- [[Defeating EDR Userland Hooks]]
- [[Sliver C2 Framework Advanced Customization]]
