---
tags: [threat-hunting, forensics, memory, rootkits, vapt]
difficulty: advanced
module: "92 - Advanced Memory Forensics and Rootkit Detection"
topic: "92.01 Introduction to Volatility 3 and Memory Acquisition"
---

# Advanced Memory Forensics: Volatility 3 and Acquisition

## Core Concepts of Memory Forensics
Memory forensics is the analysis of a computer's volatile memory (RAM) dump to identify artifacts, malicious activities, and system state at the precise moment the snapshot was taken. Unlike disk forensics, which deals with data at rest, memory forensics focuses on data in execution. This is critical for uncovering advanced persistent threats (APTs), fileless malware, rootkits, and other sophisticated evasion techniques that exist solely in memory and never touch the physical disk.

The foundation of memory forensics lies in understanding the operating system's memory management mechanisms, specifically virtual memory translation, paging, and kernel structures. Every process running on a modern OS operates within its own virtual address space, which the OS and CPU collaboratively translate into physical addresses.

When analyzing memory, forensic investigators look for:
- Running and terminated processes.
- Active network connections and sockets.
- Loaded dynamic link libraries (DLLs) and kernel modules.
- Extracted cryptographic keys and passwords.
- Evidence of process injection, hooking, and Direct Kernel Object Manipulation (DKOM).

## Memory Acquisition Techniques
Before analysis can begin, volatile memory must be safely acquired. Memory acquisition is the process of extracting the contents of RAM to a file, typically referred to as a memory dump or image. The reliability and integrity of the dump heavily depend on the acquisition method.

### 1. Hardware-Based Acquisition
Hardware acquisition involves utilizing specialized PCI/PCIe cards (e.g., PCIe screamer devices, FireWire DMA attacks) or hardware features like System Management Mode (SMM) to directly access memory bypassing the operating system. 
- **Pros:** Least intrusive, invisible to OS-level rootkits, highly reliable.
- **Cons:** Requires physical access, difficult to implement, expensive hardware.

### 2. Software-Based Acquisition
This is the most common method, utilizing specialized drivers to read memory from the kernel mode and write it to disk. Because software acquisition relies on the target OS, it is susceptible to manipulation by kernel-mode rootkits.
- **Windows:** Tools like `DumpIt`, `FTK Imager`, `Magnet RAM Capture`, and `WinPmem`. These tools load a `.sys` driver (like `pmem.sys`) to read the `\Device\PhysicalMemory` object.
- **Linux:** `LiME` (Linux Memory Extractor) is the industry standard. It operates as a Loadable Kernel Module (LKM) to dump physical memory, supporting network transmission to avoid local disk writes.
- **macOS:** `OSXpmem` is widely used, though recent macOS security features (System Integrity Protection, Secure Enclave) make memory acquisition increasingly difficult.

### 3. Virtualization and Hypervisor Acquisition
For systems hosted in virtual environments (VMware, Hyper-V, KVM), memory can be acquired directly from the hypervisor. This is the cleanest and most reliable method as the guest OS is entirely unaware of the capture.
- **VMware:** Taking a VM snapshot generates a `.vmem` file containing the physical RAM. The accompanying `.vmsn` or `.vmss` file contains the device state.
- **Hyper-V:** Snapshotting produces `.bin` or `.vmrs` files.
- **KVM/QEMU:** The `virsh dump` command can be used to generate an ELF or raw memory dump.

## Volatility 3 Framework Architecture
Volatility 3 is the successor to the Volatility 2 framework, completely rewritten in Python 3. It introduces significant architectural shifts designed for speed, flexibility, and modernized memory analysis.

### Symbol Tables vs. Profiles
In Volatility 2, users had to supply an exact "Profile" (e.g., `Win7SP1x64`) to parse kernel structures. This was rigid and problematic as Windows 10 updates frequently changed kernel structs. 
Volatility 3 introduces **Intermediate Symbol Format (ISF)** files. Instead of monolithic profiles, Volatility 3 uses symbol tables containing JSON-formatted definitions of operating system structures, variables, and enumerations.
- Volatility 3 automatically determines the appropriate symbol table by scanning the memory image for known kernel markers (like the KDBG or kernel PDB GUIDs).
- It dynamically downloads ISF files from the internet if they are not cached locally, streamlining the analysis pipeline.

### The Layered Architecture
Volatility 3 treats memory images as a stack of translation layers. 
- **File Layer:** Reads raw bytes from the `.raw` or `.vmem` file.
- **Physical Layer:** Represents physical memory, handling fragmentation.
- **Virtual Layer:** Understands CPU page tables and translates virtual addresses to physical ones.

When you run a plugin like `windows.pslist`, Volatility operates on the virtual layer, intelligently navigating the OS-specific memory mappings.

## Deep Dive into Page Tables and Virtual Memory Translation
Understanding how Volatility (and the CPU) translates a virtual address to a physical address is paramount. Modern 64-bit architectures (x86_64) use a 4-level paging structure (often expanding to 5-level).

```text
=============================================================================
                  ASCII Diagram: 4-Level Paging Translation (x86_64)
=============================================================================

+-------+      +--------+      +--------+      +--------+      +--------+
|  CR3  | ---> |  PML4  | ---> |  PDPT  | ---> |   PD   | ---> |   PT   |
+-------+      +--------+      +--------+      +--------+      +--------+
Register        Page Map        Page Dir        Page           Page
(Physical)      Level 4         Pointer         Directory      Table
                Table           Table

Virtual Address Breakdown (64-bit):
[63      48][47      39][38      30][29      21][20      12][11       0]
 Sign Extend   PML4 idx     PDPT idx     PD idx       PT idx     Offset

1. CR3 points to the physical address of the PML4 base.
2. The top 9 bits of the VA index into the PML4 to find the PDPT.
3. The next 9 bits index the PDPT to find the PD.
4. The next 9 bits index the PD to find the PT.
5. The next 9 bits index the PT to find the Physical Page Frame.
6. The lowest 12 bits define the byte offset within that physical page.
=============================================================================
```

Volatility replicates this exact CPU behavior in software via its Translation Layer, allowing it to accurately reconstruct the virtual memory space of any specific process simply by locating the process's specific CR3 (Directory Table Base - DTB) value.

## Essential Volatility 3 Commands for Initialization
To begin analyzing a memory dump, the first step is typically gathering system information.
```bash
vol -f memory.dmp windows.info.Info
```
This plugin parses the kernel's `KUSER_SHARED_DATA` structure and kernel global variables to extract:
- OS Version and Build Number.
- Major and Minor versions.
- The `KdCopyDataBlock` which helps locate the KDBG structure.
- The precise kernel base address.

Another critical command is `windows.pslist.PsList`, which walks the active process list.
```bash
vol -f memory.dmp windows.pslist
```

## Real-World Attack Scenario
**Scenario:** An organization suspects a compromised workstation after unusual outbound network traffic to a known malicious IP. The EDR (Endpoint Detection and Response) agent on the endpoint shows zero alerts. 

**Incident Response Steps:**
1. The IR team remotely connects to the hypervisor (ESXi) hosting the compromised virtual desktop and takes a VM snapshot, yielding a `.vmem` file without triggering any alerts within the guest OS.
2. The team processes the `.vmem` file with Volatility 3:
   `vol -f snapshot.vmem windows.netstat.NetStat`
3. The output reveals an active TCP connection to the malicious IP originating from `notepad.exe`.
4. However, running `vol -f snapshot.vmem windows.pslist` shows that `notepad.exe` is running with `SYSTEM` privileges and its parent process is `cmd.exe`—highly anomalous behavior.
5. The memory dump confirms an in-memory execution attack (process injection) where the attacker bypassed the EDR by running purely out of memory, leaving no artifacts on disk. The stealthy memory acquisition allowed investigators to capture the malware before the attacker could clear their tracks.

## Chaining Opportunities
- Understanding memory acquisition is useless without knowing how processes operate. Proceed to [[02 - Analyzing Windows Process Structures EPROCESS]] to map process structures.
- To find injected payloads like the one in the scenario, see [[04 - Hunting for Injected Threads and Hollowed Processes]].
- For extraction of the anomalous executable, utilize [[05 - Extracting Malware Payloads from Memory Dumps]].

## Related Notes
- [[Windows OS Architecture and Internals]]
- [[Virtualization and Hypervisor Forensics]]
- [[Incident Response Methodology]]
- [[Endpoint Detection and Response (EDR) Evasion Techniques]]
