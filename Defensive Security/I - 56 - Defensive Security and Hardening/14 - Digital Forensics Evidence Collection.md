---
tags: [defense, hardening, security, vapt, incident-response]
difficulty: advanced
module: "56 - Defensive Security and Hardening"
topic: "56.14 Digital Forensics Evidence Collection"
---

# Digital Forensics: Evidence Collection

## Overview
Digital Forensics is the rigorous scientific process of identifying, preserving, extracting, analyzing, and presenting digital evidence in a manner that is legally acceptable in a court of law. Within this discipline, evidence collection is the most critical and fragile phase. If digital evidence is mishandled, altered, or collected without adhering to strict, documented procedures, it becomes legally inadmissible ("fruit of the poisonous tree") and potentially useless for root-cause analysis during an incident response engagement.

The core guiding principle of forensic collection is the **Order of Volatility**, as formally defined by RFC 3227. This principle dictates that investigators must capture evidence starting with the most ephemeral data (which disappears rapidly over time or upon a system reboot) and progressing sequentially to the most persistent data.

## Architecture and ASCII Diagram

Below is a visualization of the Order of Volatility, illustrating the fragility of data at each level and the specialized tools typically used for acquisition.

```text
+-----------------------------------------------------------------------------------+
|                        THE ORDER OF VOLATILITY (RFC 3227)                         |
|                                                                                   |
|    MOST VOLATILE (Acquire First)                                                  |
|    ^  +-----------------------------------------------------------------+         |
|    |  | 1. CPU Registers, L1/L2 Cache                                   |         |
|    |  |    (Rarely collected by standard IR due to extreme volatility)  |         |
|    |  +-----------------------------------------------------------------+         |
|    |  | 2. Routing Tables, ARP Cache, Process Tables, Kernel Stats      |         |
|    |  |    (Tools: netstat, arp, ps, EDR telemetry scripts)             |         |
|    |  +-----------------------------------------------------------------+         |
|    |  | 3. System Memory (RAM)                                          |         |
|    |  |    (Tools: DumpIt, FTK Imager, WinPmem, LiME for Linux)         |         |
|    |  +-----------------------------------------------------------------+         |
|    |  | 4. Temporary File Systems / Swap Space                          |         |
|    |  |    (pagefile.sys, hiberfil.sys, /tmp, Linux swap partitions)    |         |
|    |  +-----------------------------------------------------------------+         |
|    |  | 5. Disk Drives (Persistent Storage / Artifacts)                 |         |
|    |  |    (Tools: dd, dc3dd, FTK Imager, KAPE, EnCase, Guymager)       |         |
|    |  +-----------------------------------------------------------------+         |
|    |  | 6. Remote Logging and Monitoring Data                           |         |
|    |  |    (SIEM logs, Firewall logs, NetFlow/Zeek PCAPs)               |         |
|    |  +-----------------------------------------------------------------+         |
|    |  | 7. Physical Configuration / Network Topology                    |         |
|    |  |    (Architecture diagrams, rack layouts, system time offsets)   |         |
|    |  +-----------------------------------------------------------------+         |
|    v  | 8. Archival Media                                               |         |
|  LEAST|    (Tape backups, cold cloud storage, CD-ROMs)                  |         |
|  VOL. +-----------------------------------------------------------------+         |
+-----------------------------------------------------------------------------------+
```

## Core Principles of Evidence Handling

Before detailing specific collection methodologies, it is crucial to understand the foundational rules of forensic handling. Deviating from these principles compromises the investigation.

### 1. Minimal Alteration (Locard's Exchange Principle)
The golden rule of forensics is: **Do not alter the original evidence.** Locard's principle states that every contact leaves a trace. Every action taken on a live system alters its state (even running a `dir` command changes memory, timestamps, and the prefetch cache). Investigators must minimize their footprint.
-   **Never** install new software (like an antivirus scanner or a forensic tool suite) directly onto a compromised machine. 
-   Always run statically compiled collection tools from a sanitized, read-only USB drive or execute them remotely via a specialized, trusted network agent (like an EDR sensor).
-   When imaging physical disks, always use a **hardware write-blocker** (e.g., Tableau, WiebeTech) to physically, at the hardware level, prevent any data bits from being written back to the source drive by the forensic workstation.

### 2. Chain of Custody
The Chain of Custody is a chronological, legally binding document that records the unbroken sequence of custody, control, transfer, analysis, and disposition of physical or electronic evidence.
-   It must definitively answer: Who collected the evidence? When and where was it collected? How was it transported? Where was it stored? Who had access to it during analysis?
-   A broken chain of custody can render evidence completely inadmissible in criminal or civil court, as defense attorneys can successfully argue the data might have been tampered with.

### 3. Cryptographic Hashing and Integrity Verification
To conclusively prove that digital evidence has not been altered since the moment of collection, cryptographic hashes (typically SHA-256 or SHA-512) are generated at the time of acquisition.
-   The hash of the original drive must exactly match the hash of the resulting forensic image file.
-   Analysis is *never* performed on the original evidence. It is performed on a working copy of the forensic image. The hash of the copy is verified against the original hash before analysis begins to ensure data integrity.

## Live Response vs. Dead Box Forensics

Evidence collection generally falls into two distinct methodologies: Live Response and Dead Box. Modern incident response heavily favors Live Response due to the prevalence of memory-resident malware and encrypted disks.

### Live Response (Triage Collection)
Live response involves gathering volatile and targeted non-volatile data from a machine while it is powered on and running. This is critical for capturing active network connections, running processes, injected fileless malware, and decrypted files or keys currently residing in RAM.

**Live Collection Steps:**
1.  **Memory Acquisition:** This must be the very first step. Tools like FTK Imager, DumpIt, or WinPmem are executed from a USB to create a bit-for-bit copy of the RAM. See [[15 - Memory Forensics Volatility]] for detailed analysis techniques of this dump.
2.  **Volatile State Collection:** Running specialized scripts to quickly grab the state of the OS before it changes. This includes running processes (`tasklist`), network connections (`netstat -anob`), routing tables, and DNS caches.
3.  **Targeted Artifact Collection (Triage):** Instead of waiting hours to acquire a multi-terabyte full disk image, investigators collect a targeted subset of high-value forensic artifacts. Tools like Kroll Artifact Parser and Extractor (KAPE) can rapidly gather Registry hives, Event Logs, Prefetch files, Amcache, and the MFT within minutes, providing enough actionable intelligence to triage the incident immediately.

### Dead Box Forensics (Post-Mortem)
Dead box forensics involves analyzing a system that is powered off. This is the traditional approach, focusing on acquiring persistent storage.

**Disk Imaging Techniques:**
1.  **Physical Extraction:** The hard drive is physically removed from the suspect machine.
2.  **Write-Blocking:** The drive is connected to a hardware write-blocker, which is then connected to the forensic analyst's workstation.
3.  **Bit-Stream Imaging:** A forensic imaging tool creates a sector-by-sector, bit-level exact replica of the drive. This includes all active files, hidden files, unallocated space (where deleted files reside), and file slack space.
    -   **Tools:** `dd` (Linux), `dc3dd` (enhanced dd with hashing), FTK Imager, Guymager.
    -   **Formats:** The image is saved in raw (`.dd`, `.img`) or specialized forensic formats like EnCase (`.E01`) or Advanced Forensic Format (`.AFF`). These specialized formats are preferred as they compress the data and embed metadata and cryptographic hashes directly within the file structure.

## Cloud and Virtual Environments

Modern IT infrastructure relies heavily on virtualization and cloud services, fundamentally shifting collection paradigms away from physical write-blockers.

-   **Virtual Machines (VMs):** Extracting evidence is often cleaner. Hypervisors (ESXi, Hyper-V) allow taking immediate snapshots. The VM's memory can be captured simply by pausing the VM and copying the hypervisor's memory file (e.g., the `.vmem` or `.vmss` files in VMware). The virtual disks (`.vmdk`, `.vhd`) can be copied directly, functioning identically to full physical disk images.
-   **Cloud Native (AWS, Azure, GCP):** Physical access to the underlying hardware is impossible. Evidence collection relies heavily on cloud provider APIs. Disks are captured by taking EBS/Managed Disk snapshots, which are then attached to an isolated forensic EC2/VM instance in a dedicated security VPC for analysis. Acquiring RAM from cloud instances is more complex but can be achieved via specific hypervisor introspection tools or memory acquisition agents deployed via SSM/Run Command.

## Summary of Critical Artifacts (Windows Deep Dive)

When performing targeted triage collection, investigators prioritize the following specific artifacts to reconstruct the attacker's timeline and actions:

-   **Registry Hives (`SAM`, `SYSTEM`, `SOFTWARE`, `NTUSER.DAT`):** 
    -   Reveals system configuration changes, installed software, persistent autorun keys (Run/RunOnce), and deep user activity (UserAssist, ShellBags, AppCompatCache/ShimCache which prove a program was executed).
-   **Windows Event Logs (`.evtx`):** 
    -   Security, System, and Application logs track logins (Event ID 4624/4625), service creation (Event ID 7045 - a common persistence mechanism), and process execution (Event ID 4688).
-   **Prefetch (`.pf`) & Amcache:** 
    -   These system optimization files provide undeniable evidence of program execution, execution times, and the path from which the executable ran, *even if the attacker has subsequently deleted the executable file itself*.
-   **Master File Table (`$MFT`):** 
    -   The core relational database of the NTFS file system. It contains metadata for every single file and directory on the volume. Parsing the MFT is crucial for generating a master timeline of file creation, modification, and access times (MACB timestamps) and for locating the remnants of deleted files.
-   **Browser Artifacts:** History databases (SQLite), cookies, and download logs can reveal the initial phishing vector, drive-by download sites, or the web-based email used for data exfiltration.

## Chaining Opportunities
-   The alerts and initial scoping performed during [[12 - SOC Operations Tier 1 2 3 Overview]] dictate exactly which assets require forensic evidence collection.
-   Evidence collection is a mandatory, heavily regulated step within the Containment and Eradication phases of the [[13 - Incident Response PICERL]] lifecycle.
-   The memory dumps (`.raw`, `.dmp`, `.vmem`) acquired during the Live Response phase detailed here are directly parsed and analyzed using the techniques described in [[15 - Memory Forensics Volatility]].

## Related Notes
-   [[13 - Incident Response PICERL]]
-   [[15 - Memory Forensics Volatility]]
-   [[12 - SOC Operations Tier 1 2 3 Overview]]
-   [[04 - Endpoint Security and EDR]]
