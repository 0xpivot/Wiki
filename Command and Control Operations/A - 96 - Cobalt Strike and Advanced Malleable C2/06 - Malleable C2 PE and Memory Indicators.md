---
tags: [cobalt-strike, malleable-c2, red-team, vapt]
difficulty: advanced
module: "96 - Cobalt Strike and Advanced Malleable C2"
topic: "96.06 Malleable C2 PE and Memory Indicators"
---

# Malleable C2 PE and Memory Indicators

## Introduction to Memory OPSEC
Memory OPSEC is one of the most critical aspects of modern Red Teaming. Endpoint Detection and Response (EDR) solutions and memory scanners have evolved significantly, moving away from simple disk-based static signatures to complex, heuristic, and behavioral memory analysis. When executing a Beacon payload in memory, defensive tooling such as PE-sieve, Moneta, and EDR agents are actively hunting for specific anomalies that indicate unauthorized or malicious code execution.

Advanced Malleable C2 profiles in Cobalt Strike provide the `stage` block, which directly influences how the beacon is loaded into memory, its Portable Executable (PE) characteristics, and its behavior over time. Malleable C2 allows operators to dictate the specific bytes that get loaded, the permissions of the memory regions allocated, the strings left in memory, and the PE header structures. Misconfiguring the `stage` block is the primary reason why Beacons get caught in memory by modern defensive solutions.

## The Anatomy of Memory Scanning
Before diving into the configuration, it is essential to understand how EDRs and memory scanners operate. EDRs utilize functions like `VirtualQueryEx` and `ReadProcessMemory` to inspect the memory space of running processes. They look for:
1. **Unbacked Executable Memory:** Memory regions with `EXECUTE` permissions that do not correspond to a legitimate file on disk. This is a classic indicator of reflective DLL injection or shellcode execution.
2. **RWX Memory:** Memory regions allocated with `PAGE_EXECUTE_READWRITE` permissions. Legitimate applications rarely need memory that is simultaneously writable and executable.
3. **PE Artifacts in Memory:** The presence of standard Windows executable structures (MZ headers, PE headers, DOS stubs) in unexpected locations, particularly within unbacked memory.
4. **Known Strings and Signatures:** Specific byte sequences or strings associated with known malware families or frameworks like Cobalt Strike (e.g., `%s as %s`, `ReflectiveLoader`).

## The `stage` Block Configuration Deep Dive

The `stage` block is where operators control the attributes of the Beacon payload itself. Cobalt Strike’s Beacon is fundamentally a Reflective DLL, meaning it loads itself into memory without relying on the Windows loader (`LoadLibrary`). However, the default Reflective DLL injection leaves several identifiable artifacts.

### Key Properties to Modify

1. **`userwx` (User RWX):**
   This setting dictates whether the memory allocated for the Beacon is `RWX` (Read-Write-Execute) or `RX` (Read-Execute). `RWX` is an immediate red flag for modern EDRs. Setting this to `false` forces the Beacon to allocate memory as `RW`, write the payload, and then change the permissions to `RX` using `VirtualProtect`.
   
2. **`cleanup`:**
   When set to `true`, the Reflective DLL loader will attempt to free the memory associated with the DLL when it exits. Furthermore, it clears the initial memory allocation for the Reflective DLL, ensuring that the initial PE stub does not linger in memory after the Beacon is fully loaded.
   
3. **`obfuscate`:**
   This flag instructs the Reflective DLL loader to copy the Beacon into memory without its PE header. This defeats simple memory scans that look for the `MZ` and `PE` magic bytes at the start of executable memory regions.
   
4. **`stomppe`:**
   An alternative or addition to `obfuscate`. This option stomps the PE header with null bytes or a predefined string after loading, making it difficult for memory scanners to parse the PE structure.
   
5. **`rich_header`:**
   Allows you to fake the Rich Header of the PE file. The Rich Header contains information about the build environment. Threat hunters use this to correlate malware. By forging it, you can blend in with legitimate binaries compiled by specific toolchains.

### Memory Scanning Evasion Techniques

Memory scanning tools look for disconnected executable memory (memory not backed by a file on disk). To evade this, operators can employ several strategies:

#### Module Stomping

Module stomping involves loading a legitimate DLL into the target process (e.g., `amsi.dll` or `xpsprint.dll`), which creates a file-backed executable memory region. The Reflective Loader then overwrites the code section of this legitimate DLL with the Beacon payload. EDRs scanning memory will see the executable region is backed by a legitimate file on disk, heavily reducing the suspicion score.

In Malleable C2, this is achieved using the `module_x64` and `module_x86` options within the `stage` block.

#### Sleep Obfuscation (Ekko, Gargoyle, etc.)

When a Beacon is sleeping, its memory remains in an executable state, making it vulnerable to YARA scans. Sleep obfuscation techniques (like Ekko) encrypt the Beacon's memory region while it sleeps and decrypts it just before it wakes up. Cobalt Strike introduced native support for memory encryption via the `sleep_mask` option.

When `sleep_mask` is enabled, Cobalt Strike XORs the Beacon's `.text` section and other data sections with a random key during the sleep cycle. Modern extensions also allow hooking into User-Defined Reflective Loaders (UDRL) for even more advanced sleep obfuscation routines.

### Customizing the PE Header

Beyond just hiding the PE header, you can forge it to mimic legitimate applications. EDRs often look at the compile time, checksums, and image sizes to identify anomalous PE files loaded in memory.

By heavily modifying these attributes, we decouple the signature of the payload from standard Cobalt Strike defaults. The `transform-x64` block allows us to prepend NOP sleds or replace strings directly within the PE, stripping out predictable strings like "ReflectiveLoader".

## Advanced Evasion Concepts

### User-Defined Reflective Loader (UDRL)
Cobalt Strike supports User-Defined Reflective Loaders, which allow operators to completely replace the built-in loader with a custom implementation. This is the ultimate form of memory evasion, as the operator can implement custom memory allocation (e.g., direct syscalls for memory allocation), custom execution logic, and advanced sleep obfuscation techniques that are completely unknown to the EDR.

### Thread Stack Spoofing
When a Beacon executes, it requires a thread. Threat hunters analyze thread call stacks for anomalies. If a thread points to an unbacked memory region, it is suspicious. Malleable C2, combined with advanced UDRLs, can implement thread stack spoofing, where the call stack is manipulated to point to legitimate, backed functions while the thread is sleeping, making it appear benign.

## Detailed Table: Memory Properties and OPSEC Impact

| Property | Default Behavior | Malleable C2 Override | OPSEC Impact | Blue Team Telemetry |
| :--- | :--- | :--- | :--- | :--- |
| **`userwx`** | Allocates `RWX` memory using `VirtualAlloc`. | `set userwx "false";` | Forces `RW` allocation, writes payload, changes to `RX`. Eliminates RWX IoC. | `NtAllocateVirtualMemory`, `NtProtectVirtualMemory` |
| **`cleanup`** | Reflective loader stub remains in memory. | `set cleanup "true";` | Frees the memory associated with the initial DLL loader stub after Beacon is loaded. | `NtFreeVirtualMemory` |
| **`obfuscate`** | Leaves the MZ and PE headers intact. | `set obfuscate "true";` | Loads Beacon without its PE header, defeating basic `MZ`/`PE` magic byte scanning. | Memory dumps lacking PE signatures |
| **`sleep_mask`** | Beacon remains executable and decryted while sleeping. | `set sleep_mask "true";` | XOR encrypts the Beacon `.text` section during the sleep cycle, evading static YARA scans. | Suspicious thread states, high entropy memory blocks |
| **`module_x64`** | Uses `VirtualAlloc` for unbacked memory. | `set module_x64 "xpsprint.dll";` | Module Stomping: Hijacks a legitimate DLL, backing the memory with a file on disk. | File mappings, `NtMapViewOfSection`, code section modifications |

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
|                           Advanced Memory Evasion Strategy                        |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  1. Injection & Allocation                                                        |
|     VirtualAlloc (PAGE_READWRITE) -> NO RWX!                                      |
|            |                                                                      |
|            v                                                                      |
|  2. Payload Loading                                                               |
|     Write Beacon payload to allocated memory region                               |
|            |                                                                      |
|            v                                                                      |
|  3. PE Modification (stomppe / obfuscate)                                         |
|     [ MZ Header ] -> Overwritten with 0x00 or custom bytes                        |
|     [ PE Header ] -> Destroyed, Manipulated, or Faked                             |
|            |                                                                      |
|            v                                                                      |
|  4. Permission Change & Execution                                                 |
|     VirtualProtect (PAGE_EXECUTE_READ)                                            |
|     Execute payload via Thread Creation                                           |
|            |                                                                      |
|            v                                                                      |
|  5. Sleep Cycle (sleep_mask & Thread Stack Spoofing)                              |
|     Encrypt RX region -> Manipulate Stack -> Wait -> Restore Stack -> Decrypt     |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

### Scenario: Evading Next-Gen EDR with File-Backed Memory and Sleep Obfuscation

**Context:** The Red Team has established initial access on a tier-1 endpoint. The endpoint is protected by a modern Next-Gen EDR that aggressively scans for anomalous `RWX` memory regions, unbacked executable memory, and performs periodic YARA scans of all process memory spaces.

**Execution:**
1. **Profile Generation:** The operator creates a custom Malleable C2 profile with the following `stage` block configuration:
   - `userwx "false"` (Prevents RWX flags)
   - `module_x64 "c:\\windows\\system32\\xpsprint.dll"` (Module Stomping)
   - `sleep_mask "true"` (In-memory encryption during sleep)
   - `obfuscate "true"` (Removes PE headers)
   - `cleanup "true"` (Frees initial reflective loader stub)
2. **Payload Staging:** The initial stager executes and begins the staging process.
3. **Module Loading:** Instead of allocating arbitrary, unbacked memory, the Reflective Loader forces the OS to load `xpsprint.dll` (a rarely used legitimate Microsoft DLL) into the target process space.
4. **Memory Stomping:** The loader then overwrites the `.text` (executable) section of `xpsprint.dll` with the Beacon payload.
5. **EDR Scanning:** The EDR performs a routine memory scan. It identifies the executable memory, but checks its provenance. Because the memory is backed by `c:\windows\system32\xpsprint.dll` on disk, the EDR classifies it as benign and moves on.
6. **Sleep Obfuscation:** When the Beacon enters its 60-second sleep cycle, the `sleep_mask` function engages. It encrypts the `.text` section of the hijacked DLL, ensuring that no known Cobalt Strike strings or patterns are visible to YARA scans running during the sleep period.
7. **Resumption:** Upon waking, the memory is decrypted, Beacon checks in with the C2 server, receives new tasks, and immediately encrypts itself again before going back to sleep.

**Outcome:** The Beacon achieves complete evasion of memory-based detection, allowing prolonged presence on the high-value endpoint without triggering any heuristic or signature-based alerts.

## Detection Engineering Perspective
From a Blue Team perspective, detecting heavily customized Malleable C2 profiles requires moving beyond simple string matching and RWX hunting. 
- **Hunting for Module Stomping:** Look for loaded modules that are rarely used by the host process, or compare the memory contents of loaded modules against their on-disk counterparts. If the `.text` section in memory differs significantly from the file on disk, module stomping may be occurring.
- **Hunting for Sleep Obfuscation:** Analyze thread behavior. Threads that spend the vast majority of their time in a suspended or sleeping state, particularly those with anomalous call stacks, should be investigated.
- **Hunting for UDRLs:** Focus on telemetry related to thread creation (`CreateRemoteThread`, `NtCreateThreadEx`) and analyze the entry point of these threads. If the entry point lies within an unbacked region or a stomped module, it warrants further analysis.

## Chaining Opportunities
- Using custom PE indicators pairs perfectly with advanced process injection. See [[07 - Malleable C2 Process Injection and Evasion]] for injecting this hardened payload into remote processes.
- Memory evasions must be coupled with network traffic masking. See [[08 - Crafting Advanced Malleable C2 Profiles for OPSEC]] to ensure the network traffic doesn't give away the payload that memory scanning missed.
- Further customization of the initial PE loader and the generation of the stagers can be achieved using the Artifact Kit. See [[09 - Artifact Kit and Payload Obfuscation]].

## Related Notes
- [[11 - Introduction to Reflective DLL Injection]]
- [[24 - EDR Evasion Techniques and Memory Scanning]]
- [[45 - Advanced YARA Rule Creation for Threat Hunting]]
- [[96 - Cobalt Strike and Advanced Malleable C2/07 - Malleable C2 Process Injection and Evasion]]
- [[96 - Cobalt Strike and Advanced Malleable C2/08 - Crafting Advanced Malleable C2 Profiles for OPSEC]]

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
