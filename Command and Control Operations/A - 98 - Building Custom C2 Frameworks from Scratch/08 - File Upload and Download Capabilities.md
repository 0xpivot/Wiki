---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.08 File Upload and Download Capabilities"
---

# File Upload and Download Capabilities

## 1. Introduction to Data Exfiltration and I/O
A robust Command and Control (C2) framework requires reliable, stealthy mechanisms for moving files onto the compromised host (uploading/dropping secondary payloads) and retrieving files from the host (downloading/exfiltrating data). Implementing these capabilities from scratch requires careful management of File I/O operations, memory buffering, network transmission, and evasion tactics to bypass Data Loss Prevention (DLP) and network intrusion detection systems (IDS/IPS). 

From a defensive and threat-hunting perspective, file operations are noisy. Monitoring file creation in sensitive directories and baselining outbound network bandwidth are primary methods for detecting C2 activity.

## 2. Windows API for File Operations
At the lowest level, agents interact with the file system using native Windows APIs, avoiding higher-level wrappers that might introduce dependencies or unnecessary telemetry.

### The Core I/O APIs
*   **CreateFile:** Used to obtain a handle to a file. Despite its name, it is used for opening existing files as well as creating new ones. Threat hunters monitor the requested access rights (e.g., `GENERIC_READ` vs `GENERIC_WRITE`) and share modes.
*   **ReadFile:** Used during data exfiltration (download). The agent reads the file from the disk into a memory buffer.
*   **WriteFile:** Used during payload dropping (upload). The agent writes data received from the C2 server to the disk.
*   **SetFilePointerEx:** Used to navigate within a file, critical for chunked reading and resuming interrupted transfers.

## 3. Data Chunking and Serialization
Attempting to transmit a 500MB `NTDS.dit` file in a single HTTP POST request will immediately trigger network alarms and is highly prone to connection timeouts. Advanced agents implement "Chunking".

### The Chunking Mechanism
1.  **File Slicing:** The agent determines the file size and slices it into uniform chunks (e.g., 512KB to 1MB).
2.  **Structuring Data:** Each chunk is wrapped in a struct or JSON payload containing metadata:
    *   File ID / Session ID
    *   Chunk Index / Sequence Number
    *   Total Chunks
    *   Chunk Data (Base64 Encoded)
3.  **Transmission:** Chunks are sent sequentially or asynchronously. If a transmission fails, the agent only needs to re-transmit the failed chunk, not the entire file.

### Cryptography and Integrity
To prevent DLP solutions from recognizing sensitive file headers (like MZ headers of a PE file, or document signatures) during transit, each chunk is symmetrically encrypted (e.g., AES-256) before transmission. Furthermore, a SHA256 hash of the complete file is usually calculated and sent to the C2 server to ensure post-transfer integrity verification.

## 4. Network APIs for Data Transit
To send the chunks, the agent must interface with the network stack. 
*   **WinINet / WinHTTP:** The standard Windows APIs for web communication. They handle proxy resolution, TLS handshakes, and caching automatically, making the agent's traffic look like legitimate browser traffic.
*   **Sockets (Winsock):** Used for custom TCP/UDP protocols. While highly flexible, raw socket communication requires the agent to implement its own encryption (e.g., mTLS) and is more easily fingerprinted by network defenders.

## 5. ASCII Architecture Diagram

```ascii
+-------------------------------------------------------------+
| Exfiltration Flow (Agent Downloading to C2 Server)          |
+-------------------------------------------------------------+

[ Target File on Disk ] 
        |
        v
[ CreateFile(GENERIC_READ) ]
        |
        v
+-----------------------+      +---------------------------+
| Chunking Engine       |      | Network Transmitter       |
|                       |      |                           |
| Chunk 1 (0 - 512KB)   | ---> | AES Encrypt -> HTTP POST  | ---> C2 Server
| Chunk 2 (512 - 1024KB)| ---> | AES Encrypt -> HTTP POST  | ---> C2 Server
| Chunk 3 (1024 - EOF)  | ---> | AES Encrypt -> HTTP POST  | ---> C2 Server
+-----------------------+      +---------------------------+
        |
        v
[ SHA256 Hash Calculation ] ---> [ Integrity Check Request ] ---> C2 Server
```

## 6. Advanced Evasion Techniques
To hide file operations from EDR solutions, sophisticated agents employ several techniques:
*   **Transacted NTFS (TxF):** Using legacy APIs (like `CreateFileTransacted`) to perform file operations inside a transaction. If the payload is never committed, it never touches the disk permanently, but can still be executed. (Often tied to Process Doppelgänging).
*   **Direct Syscalls:** Bypassing `kernel32.dll` and `ntdll.dll` hooks by implementing direct syscalls for `NtCreateFile`, `NtReadFile`, and `NtWriteFile`.
*   **BITS (Background Intelligent Transfer Service):** Leveraging the legitimate Windows BITS service via COM objects to asynchronously download payloads. BITS traffic is notoriously difficult to distinguish from legitimate Windows Update traffic.

## 7. Telemetry and Threat Hunting Strategies

### Sysmon Event ID 11 (File Creation)
Defenders monitor file creation events, specifically looking for executable files (`.exe`, `.dll`, `.ps1`) dropped in uncommon directories like `C:\Users\Public`, `C:\ProgramData`, or `AppData\Local\Temp`. 

### Network Baselining and PCAP Analysis
Data exfiltration causes a spike in outbound bandwidth. Threat hunters utilize Zeek or Suricata to baseline normal host traffic. A sudden burst of consistent, encrypted HTTP POST requests of uniform size (indicative of chunking) to an uncategorized domain is a massive red flag. Analysts can reconstruct the network streams from PCAPs, and while they cannot read the encrypted payload, the metadata (headers, frequency, size) creates a distinct signature.

### Event ID 3 (Network Connection)
Correlating Sysmon Event 3 (Network Connection) with a process that rarely communicates externally (e.g., `notepad.exe` if it has been hollowed out) is a key hunting strategy. 

## Real-World Attack Scenario
During a ransomware engagement, an affiliate utilizes a custom C++ agent to exfiltrate a company's sensitive SQL databases prior to encryption (Double Extortion). To avoid triggering the SIEM's data-transfer volume alerts, the agent does not send the data directly over HTTP. Instead, the agent implements file chunking and embeds the encrypted chunks inside the `TXT` records of DNS queries. It slowly bleeds the data over several days to an attacker-controlled nameserver. The SOC fails to notice the exfiltration because DNS traffic volume is massive and rarely inspected deeply for payload characteristics. The activity is finally caught when a threat hunter notices anomalous, extremely long, high-entropy subdomains being requested continuously by a single host.

## Chaining Opportunities
*   Downloaded payloads can be immediately loaded into memory (Reflective Loading) to avoid touching the disk entirely, bypassing Event ID 11.
*   Background threads must be used for file transfers to prevent the main beacon loop from freezing.

## Related Notes
*   [[07 - Implementing Command Execution and Output Parsing]]
*   [[10 - Asynchronous Execution and Background Jobs]]
*   [[17 - DNS over HTTPS (DoH) and Alternative C2 Channels]]
*   [[18 - BITS Jobs and Living off the Land Data Transfers]]
