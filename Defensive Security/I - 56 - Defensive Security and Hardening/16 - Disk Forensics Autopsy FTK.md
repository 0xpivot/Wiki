---
tags: [defense, hardening, security, vapt, forensics]
difficulty: advanced
module: "56 - Defensive Security and Hardening"
topic: "56.16 Disk Forensics Autopsy FTK"
---

# 16 - Disk Forensics, Autopsy, and FTK

Disk forensics is a highly specialized branch of digital forensics focused on the identification, extraction, preservation, and analysis of data stored on physical storage media. The goal is to reconstruct past events, recover deleted data, and build a timeline of malicious or unauthorized activities on a system. As attackers become more sophisticated using fileless malware, rootkits, and anti-forensic techniques, deep disk forensics remains a critical discipline for uncovering the ground truth of an incident.

In the realm of disk forensics, tools like Autopsy (open-source) and FTK (AccessData Forensic Toolkit) are industry standard. They allow investigators to parse complex filesystems, extract artifacts, and correlate data without modifying the underlying evidence.

## The Forensic Methodology

Before diving into the tools, a strict forensic methodology must be adhered to. Any deviation can render the evidence inadmissible in a court of law or lead to incorrect conclusions.

1. **Identification**: Recognizing the scope of the incident and identifying all potential sources of digital evidence (HDDs, SSDs, USBs, NVMe drives).
2. **Preservation**: Securing the evidence to prevent any alteration. This involves hardware write-blockers and maintaining a strict Chain of Custody.
3. **Acquisition**: Creating a bit-for-bit forensic image of the original media.
4. **Analysis**: Examining the forensic image using specialized tools to extract artifacts, timeline data, and indicators of compromise (IoCs).
5. **Reporting**: Documenting the findings, methodology, and conclusions in a comprehensive report.

### Forensic Image Formats

When acquiring evidence, analysts typically use one of three primary image formats:

*   **RAW (dd):** A bit-for-bit, uncompressed copy of the drive. It contains no metadata and takes up as much space as the original drive.
*   **EnCase (E01):** The Expert Witness Format. This is the industry standard. It compresses the data, splits it into chunks, and embeds metadata (investigator name, case number, hashes) directly into the file.
*   **AFF4 (Advanced Forensic Format):** An open-source format designed for speed and scalability, supporting compression and metadata, often used for large-scale acquisitions.

## Forensic Acquisition and Analysis Pipeline Diagram

```text
+-------------------+        +--------------------+        +---------------------+
| Physical Device   |        | Hardware/Software  |        | Forensic Workstation|
| (HDD, SSD, USB)   +------->+ Write-Blocker      +------->+ (FTK Imager / dd)   |
+-------------------+        +--------------------+        +----------+----------+
                                                                      |
                                                                      v
                                                           +----------+----------+
                                                           | Forensic Image      |
                                                           | (.E01, .RAW, .AFF4) |
                                                           +----------+----------+
                                                                      |
                   +--------------------------------------------------+--------------------------------------------------+
                   |                                                                                                     |
                   v                                                                                                     v
+------------------+------------------+                                                       +--------------------------+------------------+
|          Autopsy (Sleuth Kit)       |                                                       |    AccessData FTK (Forensic Toolkit)        |
|-------------------------------------|                                                       |---------------------------------------------|
| 1. Ingest Modules                   |                                                       | 1. Data Processing Engine (Oracle/Postgres) |
|    - Hash Lookup (NSRL)             |                                                       | 2. Known File Filter (KFF)                  |
|    - Exif Parser / Keyword Search   |                                                       | 3. Advanced Registry Parsing                |
|    - Email / Web Artifact Parser    |                                                       | 4. Decryption & Password Recovery (PRTK)    |
| 2. Timeline Analysis                |                                                       | 5. Live Search & Indexed Search             |
| 3. Deleted File Recovery            |                                                       | 6. Custom Carving (Data Carving)            |
+-------------------------------------+                                                       +---------------------------------------------+
                   |                                                                                                     |
                   +--------------------------------------------------+--------------------------------------------------+
                                                                      |
                                                                      v
                                                           +----------+----------+
                                                           | Extracted Artifacts |
                                                           | (MFT, Registry, Logs|
                                                           +----------+----------+
```

## Deep Dive: Autopsy and The Sleuth Kit (TSK)

Autopsy is the premier open-source digital forensics platform, serving as a graphical interface to The Sleuth Kit (TSK). It allows investigators to analyze disk images, local drives, and logical files efficiently.

### Key Features of Autopsy

1. **Ingest Modules:** Autopsy runs a series of background tasks called ingest modules when an image is loaded.
    *   **Recent Activity:** Extracts web browser history, bookmarks, cookies, and recent documents.
    *   **Hash Lookup:** Calculates MD5/SHA-256 hashes of all files and compares them against known databases like the NIST National Software Reference Library (NSRL) to filter out known good files, or against custom databases of known malware.
    *   **File Type Identification:** Analyzes file signatures (magic bytes) to identify files even if their extensions have been altered (e.g., a `.exe` renamed to `.txt`).
    *   **Extension Mismatch Detector:** Flags files where the extension does not match the actual file signature.
    *   **Keyword Search:** Performs indexed searches across the entire drive for specific strings, IPs, email addresses, or custom regular expressions.

2. **Timeline Analysis:** One of Autopsy's most powerful features. It creates a visual timeline of all file system events (MACB - Modified, Accessed, Changed, Birth), web activity, and system events. This is crucial for answering the "when" of an attack.

3. **Data Carving (PhotoRec integration):** Recovers deleted files by scanning the unallocated space for file signatures and extracting the contiguous data blocks. This works even if the file system metadata (like the MFT) has been overwritten.

### Analyzing a Case in Autopsy

When analyzing a compromised Windows system, a forensic investigator will typically focus on the following artifacts within Autopsy:

*   **The Master File Table (MFT):** The core of the NTFS file system. The MFT tracks all files on the volume. Analyzing the `$MFT` can reveal deleted files, file creation times (timestomping detection), and Resident Data (small files stored entirely within the MFT record).
*   **Windows Registry:** Autopsy can parse NTUSER.DAT, SAM, SYSTEM, SOFTWARE, and SECURITY hives. Investigators look for persistence mechanisms (Run keys), executed programs (UserAssist, BAM/DAM), and connected USB devices (USBSTOR).
*   **Prefetch and Amcache:** These artifacts prove that a specific executable was run on the system, even if the executable itself has been deleted. They contain execution counts, last run times, and loaded modules.
*   **LNK Files and Shellbags:** Provide evidence of user interaction. Shellbags prove that a user opened a specific folder, even if that folder was on a removable drive or a network share. LNK files (shortcuts) contain metadata about the target file, including its original path and MAC times.

## Deep Dive: FTK (Forensic Toolkit)

AccessData's FTK is a commercial enterprise-grade forensic suite. It is known for its robust processing power, database-driven backend, and advanced analytical capabilities.

### Key Advantages of FTK

1. **Database-Driven Architecture:** Unlike Autopsy, which uses SQLite and local indexing, FTK relies on a robust database (historically Oracle, now often PostgreSQL). This allows FTK to handle massive datasets (terabytes of data) without crashing and enables distributed processing across multiple worker nodes.
2. **Known File Filter (KFF):** FTK's version of hash filtering, highly optimized and integrated with vast databases of known good and bad hashes.
3. **Advanced Decryption:** FTK integrates seamlessly with PRTK (Password Recovery Toolkit) and DNA (Distributed Network Attack). It can automatically detect encrypted files (BitLocker, TrueCrypt, encrypted ZIPs, Office docs) and attempt to decrypt them using dictionaries, brute-force, or extracted memory artifacts.
4. **Data Carving:** FTK offers highly customizable data carving options, allowing investigators to define custom file headers, footers, and maximum file sizes to recover proprietary or obscure file formats from unallocated space.
5. **Volume Shadow Copy (VSS) Analysis:** FTK excels at automatically parsing and presenting Volume Shadow Copies, allowing investigators to compare the current state of a file system with historical snapshots to identify deleted files or reverted changes.

### FTK Imager

While FTK is the analysis suite, **FTK Imager** is a free, standalone tool used primarily for acquisition and triage.
*   **Live Acquisition:** It can capture physical memory (RAM) and acquire a live image of the system drive while the OS is running (though this breaks the strict "turn it off and image it" rule, it's often necessary for encrypted systems where pulling the plug would lose the decryption keys in RAM).
*   **Triage:** Investigators can use FTK Imager to mount a forensic image or a physical drive as a read-only device and quickly browse the file system, export specific artifacts (like Registry hives), or extract memory dumps without loading the entire multi-terabyte image into the full FTK suite.

## The Challenge of Solid State Drives (SSDs)

Modern disk forensics faces a massive challenge: SSDs. Unlike HDDs, where deleted data remains until overwritten, SSDs utilize a function called **TRIM** and a process called **Active Garbage Collection**.

When a file is deleted on an SSD, the OS sends a TRIM command to the drive controller. The controller then actively erases the underlying NAND flash memory cells in the background.
*   **Result:** Data carving on an SSD is often futile. A deleted file might be permanently unrecoverable within minutes or even seconds.
*   **Forensic Implications:** Investigators must prioritize live acquisition and memory forensics if they suspect an SSD is actively destroying evidence. Pulling the plug on an SSD might actually allow the drive's internal controller to continue garbage collection using residual capacitor power.

## Anti-Forensics and Evasion

Attackers actively attempt to thwart disk forensics using various techniques:

*   **Timestomping:** Modifying the MAC (Modified, Accessed, Created) times of a malicious executable to blend in with legitimate system files (e.g., setting the creation date of a backdoor to match `cmd.exe`).
    *   *Detection:* Compare the standard information attribute times with the file name attribute times in the NTFS MFT. Timestomping tools often only change one set of timestamps.
*   **Fileless Malware:** Executing entirely in memory or hiding within the registry (e.g., Poweliks).
    *   *Detection:* Analyzing memory dumps (RAM forensics) and scrutinizing the registry for large, obfuscated binary blobs.
*   **Rootkits:** Modifying the OS kernel to hide files, processes, and network connections from standard APIs.
    *   *Detection:* Booting the drive from a clean, forensic OS. The forensic OS bypasses the compromised APIs and reads the raw disk sectors directly, revealing the hidden files.
*   **Wiping/Shredding:** Overwriting files with random data before deletion.
    *   *Detection:* Identifying the presence of wiping tools (e.g., SDelete, DBAN) and finding partially overwritten files or anomalous blocks of high-entropy data.

## Chaining Opportunities

*   **Memory Forensics:** Disk forensics must almost always be paired with RAM analysis (Volatility) to capture encryption keys, active network connections, and fileless malware. Connects to `[[15 - Memory Forensics Volatility]]`.
*   **Malware Analysis:** Binaries extracted from the disk using Autopsy or FTK are typically passed to a reverse engineering team for static and dynamic analysis. Connects to `[[22 - Malware Analysis Reverse Engineering]]`.
*   **Incident Response:** The findings from disk forensics directly inform the Incident Response containment and eradication strategy. Connects to `[[12 - Incident Response Frameworks]]`.

## Related Notes
*   `[[14 - Digital Forensics Fundamentals]]`
*   `[[17 - Log Analysis for Attack Detection]]`
*   `[[15 - Memory Forensics Volatility]]`
*   `[[05 - Windows Privilege Escalation]]` (Understanding Windows artifacts helps track privilege escalation attempts)
