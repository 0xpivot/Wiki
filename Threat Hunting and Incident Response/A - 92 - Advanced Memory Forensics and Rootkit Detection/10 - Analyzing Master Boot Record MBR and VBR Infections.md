---
tags: [threat-hunting, forensics, memory, rootkits, vapt]
difficulty: advanced
module: "92 - Advanced Memory Forensics and Rootkit Detection"
topic: "92.10 Analyzing Master Boot Record MBR and VBR Infections"
---

# 92.10 Analyzing Master Boot Record MBR and VBR Infections

## Introduction

While the cybersecurity industry heavily focuses on application-layer exploits and OS-level malware, some of the most destructive and persistent threats operate beneath the operating system itself. Bootkits—malware that infects the Master Boot Record (MBR), Volume Boot Record (VBR), or the Unified Extensible Firmware Interface (UEFI)—are designed to execute before the OS kernel even loads. 

By executing in the pre-boot environment, a bootkit can subvert early security checks (like Kernel Patch Protection/PatchGuard and Driver Signature Enforcement), hook the transition from real mode to protected mode, and silently inject its payload into the kernel memory space as the OS initializes. Analyzing MBR and VBR infections is a highly specialized skill in digital forensics and incident response (DFIR), requiring knowledge of low-level assembly, disk structures, and the Windows boot process.

## The Boot Process: BIOS, MBR, and VBR

To understand how a bootkit operates, one must understand the traditional BIOS boot sequence (which is still emulated in many modern systems via Compatibility Support Module or CSM, though native UEFI is the modern standard).

1. **Power-On Self Test (POST):** The hardware initializes, and the BIOS executes.
2. **MBR Execution:** The BIOS reads the first sector (Sector 0) of the bootable drive, known as the Master Boot Record (MBR), into memory at physical address `0x7C00` and executes it. 
3. **Partition Table Lookup:** The MBR code parses the embedded Partition Table to find the active (bootable) partition.
4. **VBR Execution:** The MBR loads the first sector of the active partition, known as the Volume Boot Record (VBR), into memory and executes it.
5. **Bootmgr/NTLDR:** The VBR code parses the file system (e.g., NTFS) just enough to locate and execute the Windows Boot Manager (`bootmgr`).
6. **OS Loading:** `bootmgr` loads `winload.exe`, which transitions the CPU to protected mode and loads the Windows kernel (`ntoskrnl.exe`).

### How MBR/VBR Bootkits Work

A bootkit interrupts this chain of trust by overwriting the legitimate MBR or VBR code with its own malicious instructions. 

**MBR Infection:**
The malware replaces the original MBR code. When the BIOS hands over control, the malicious MBR executes first. It typically hooks interrupts (like `INT 13h` for disk access) to intercept subsequent reads. It then loads the original, legitimate MBR (which it saved elsewhere on the disk) and allows the boot process to continue, maintaining stealth while ensuring its code remains resident in memory.

**VBR Infection:**
Some malware targets the VBR instead of the MBR to bypass simple MBR integrity checks. The logic is similar: the malicious VBR executes, hooks necessary interrupts, and then passes control back to the legitimate VBR or `bootmgr`.

```text
+-----------------------------------------------------------------------------------+
|                            Bootkit Infection Architecture                         |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  Legitimate Boot Flow:                                                            |
|  [BIOS] ---> [Original MBR] ---> [Original VBR] ---> [Bootmgr] ---> [Windows OS]  |
|                                                                                   |
|                                                                                   |
|  Infected Boot Flow (MBR Bootkit):                                                |
|                                                                                   |
|  [BIOS]                                                                           |
|    |                                                                              |
|    v                                                                              |
|  +--------------------+                                                           |
|  | Malicious MBR      | 1. BIOS executes Bootkit at Sector 0                      |
|  | (Sector 0)         | 2. Bootkit hooks INT 13h (Disk I/O)                       |
|  +---------+----------+ 3. Bootkit loads its payload into high memory             |
|            |                                                                      |
|            v                                                                      |
|  +--------------------+                                                           |
|  | Original MBR       | 4. Bootkit jumps to the backed-up Original MBR            |
|  | (Moved to Sec 7)   |                                                           |
|  +---------+----------+                                                           |
|            |                                                                      |
|            v                                                                      |
|  +--------------------+                                                           |
|  | Original VBR       |                                                           |
|  +---------+----------+                                                           |
|            |                                                                      |
|            v                                                                      |
|  [ Windows Bootmgr ]    <-- Bootkit (via hooked INT 13h) watches as Windows loads.|
|                             When ntoskrnl.exe is loaded, the Bootkit patches it   |
|                             in memory to disable PatchGuard and inject its Ring 0 |
|                             rootkit payload.                                      |
+-----------------------------------------------------------------------------------+
```

## Forensic Analysis and Detection Techniques

Analyzing bootkits is challenging because if the OS is booted from an infected drive, the bootkit intercepts the forensic tool's disk read requests and returns the *clean*, original MBR, hiding its presence. Therefore, analysis must be performed offline (e.g., via a write-blocker on the physical drive) or through memory forensics.

### 1. Static Disk Analysis (Offline)
When analyzing the physical disk image (E01 or DD file) using a hex editor or a tool like The Sleuth Kit (TSK):
- **Inspect Sector 0:** Extract the first 512 bytes. The last two bytes must be the boot signature `0x55AA`. Disassemble the executable code portion (the first 446 bytes). Legitimate Windows MBR code is well-documented and static across OS versions. Any deviation, obfuscation, or unrecognized strings (like error messages not found in standard Windows MBRs) indicates infection.
- **Search for the Original MBR:** Bootkits must store the original MBR somewhere to continue the boot process. Scan the unallocated space or the sectors immediately following the MBR (Sectors 1-62, the "MBR gap") for the `0x55AA` signature and standard MBR code.
- **VBR Analysis:** Extract the first sector of the active partition. Similar to the MBR, the VBR has a known structure depending on the file system (NTFS, FAT32). Use tools to compare the extracted VBR against known good hashes.

### 2. Memory Forensics Detection
Because the bootkit must hook BIOS interrupts (like INT 13h) to monitor the OS loading phase, traces of these hooks and the bootkit's 16-bit real-mode code can sometimes be found in physical memory dumps, particularly in the lower memory regions (below 1MB).
- **Volatility `mbrparser` / `bioskbd`:** Some Volatility plugins are designed to parse the MBR structures if they were loaded into memory or to check for anomalous interrupt vector tables (IVT) in lower memory.
- **Kernel Patching Detection:** If the bootkit successfully patched the kernel during boot, plugins like `windows.ssdt` (checking for disabled PatchGuard) or `windows.malfind` might detect the resulting Ring 0 payload, providing the initial clue that a boot-level compromise occurred.

### 3. Emulation and Dynamic Analysis
Extracted MBR or VBR code can be analyzed dynamically using tools like Bochs, QEMU, or IDA Pro with real-mode emulation. By stepping through the 16-bit assembly, an analyst can see exactly where the bootkit reads its payload from the disk, how it hooks interrupts, and how it patches the Windows kernel in memory.

## Real-World Attack Scenario

### Initial Infection
A sophisticated cyber-espionage group targets an NGO. They deliver a malicious payload via a zero-day browser exploit. The payload achieves local privilege escalation and writes a custom bootkit (similar to the historic FinSpy or modern equivalents) directly to Sector 0 of the hard drive, moving the original MBR to Sector 10.

### Persistence and Evasion
The machine is rebooted. The BIOS loads the malicious MBR. The bootkit hooks `INT 13h` and monitors the disk reads as the Windows OS loads. When it detects `winload.exe` reading `ntoskrnl.exe` into memory, the bootkit patches the kernel image on the fly. This patch disables Driver Signature Enforcement (DSE). 
With DSE disabled, the bootkit injects an unsigned, highly stealthy network filtering driver into the kernel space. The OS finishes booting, entirely unaware of the compromise. Live EDR tools see nothing wrong because the kernel itself is lying to them.

### Detection and Forensic Response
The organization notices unusual DNS requests originating from the machine. The IR team acquires both a physical memory dump and a raw physical disk image of the machine.

**Memory Analysis:** The analyst runs `volatility -f memdump.raw windows.modules` and notices an unsigned driver loaded in kernel space. They then run `windows.ssdt`, which reveals multiple hooks. Since this is a Windows 10 64-bit system, the presence of SSDT hooks indicates that PatchGuard was bypassed, strongly suggesting a pre-boot compromise.

**Disk Analysis:** The analyst mounts the disk image in a forensic workstation and uses `dd` to extract the MBR:
```bash
dd if=disk.dd of=suspect_mbr.bin bs=512 count=1
```
Opening `suspect_mbr.bin` in IDA Pro (configured for 16-bit x86 architecture), the analyst immediately sees that the code does not match the standard Windows MBR template. Instead, it contains a heavily obfuscated routine that hooks `INT 13h` and reads a large payload from Sector 15 of the disk.

The IR team extracts the payload from Sector 15, reverse-engineers the kernel patching logic, and develops a precise IOC to scan the rest of the network for the specific modified MBR signature, successfully eradicating the threat.

## The Shift to UEFI
It is important to note that modern systems use UEFI (Unified Extensible Firmware Interface) instead of legacy BIOS, and GPT (GUID Partition Table) instead of MBR. UEFI enforces Secure Boot, which cryptographically verifies each stage of the bootloader. 
While this mitigates classic MBR/VBR bootkits, adversaries have evolved. Modern bootkits (like BlackLotus) exploit vulnerabilities in signed UEFI bootloaders (e.g., the Baton Drop vulnerability) to bypass Secure Boot, implanting themselves in the EFI System Partition (ESP) and achieving the exact same pre-OS execution as their MBR predecessors. The forensic principles remain similar: extract the boot components offline and perform static reverse engineering.

## Conclusion

MBR and VBR infections represent the deepest level of OS compromise, granting attackers ultimate control over the system before security software can even initialize. While legacy BIOS systems are becoming less common, understanding the mechanics of these bootkits is fundamental for DFIR professionals. It bridges the gap between disk forensics, memory forensics, and reverse engineering, teaching analysts how trust is established during the boot process and how to identify when that trust is broken.

## Chaining Opportunities
- If a bootkit is suspected due to disabled OS protections, pivot to `[[08 - Kernel Level Rootkits SSDT Hooking Detection]]` to find the resulting kernel hooks in memory.
- Use `[[09 - Direct Kernel Object Manipulation DKOM Detection]]` to see if the bootkit's kernel payload is actively hiding processes or drivers.
- Correlate the unsigned drivers found in memory back to the payload sections hidden in the unallocated space or MBR gaps on the physical disk.
- If investigating a modern system, transition to `[[13 - Advanced UEFI and Firmware Forensics]]` to adapt these concepts to Secure Boot and the EFI System Partition.

## Related Notes
- `[[08 - Kernel Level Rootkits SSDT Hooking Detection]]`
- `[[09 - Direct Kernel Object Manipulation DKOM Detection]]`
- `[[03 - Memory Acquisition and Preservation Techniques]]`
- `[[13 - Advanced UEFI and Firmware Forensics]]`
