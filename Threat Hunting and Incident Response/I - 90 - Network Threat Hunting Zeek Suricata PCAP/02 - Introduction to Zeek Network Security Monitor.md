---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.02 Introduction to Zeek Network Security Monitor"
---

# Introduction to Zeek Network Security Monitor

## 1. What is Zeek?

Zeek (formerly known as Bro) is an open-source network analysis framework and network security monitor (NSM). 

Unlike traditional Intrusion Detection Systems (IDS) like Snort or Suricata, which rely heavily on signature matching (looking for specific byte sequences that denote an attack), Zeek is fundamentally an anomaly detection, protocol parsing, and metadata generation engine.

Zeek transforms raw, unstructured network traffic (PCAP/wire data) into highly structured, high-fidelity, and easily searchable metadata logs. 

## 2. Core Philosophy: NSM vs IDS

To understand Zeek, one must understand the difference between NSM and IDS.

- **IDS (e.g., Suricata):** "I saw a packet matching the signature for the EternalBlue exploit. Alert!"
- **NSM (Zeek):** "I observed an SMB connection on port 445 from IP A to IP B. Here is the exact SMB tree connected to, the files transferred, the NTLM authentication details, and the duration of the connection."

Zeek acts as a "flight data recorder" for your network. 

When an alert fires from an IDS, the analyst relies on Zeek logs to reconstruct the context: what happened before the alert, during the alert, and after the alert?

## 3. Zeek Architecture Deep Dive

Zeek processes traffic in a highly efficient, layered pipeline designed to handle gigabit speeds.

### 3.1 Packet Capture Layer

Like any NSM, Zeek reads packets from the wire using `libpcap`, AF_PACKET, PF_RING, or DPDK. 

This layer is responsible for kernel bypass and getting packets into memory.

### 3.2 Event Engine (Core C++)

Written in highly optimized C++, this engine parses the raw packet stream into higher-level protocol events. 

It performs deep packet inspection and stateful tracking of connections.

When it identifies a protocol (e.g., HTTP), it fires an event (e.g., `http_request`).

### 3.3 Policy Script Interpreter

Zeek has its own Turing-complete scripting language. 

When the Event Engine generates an event, it triggers the corresponding Zeek scripts. 

The scripts define what to *do* with the event (e.g., write to a log file, generate an alert, extract a file).

## 4. Zeek Architecture Diagram

```text
   Raw Network Traffic (Packets via TAP/SPAN)
            |
            v
 +-------------------------+
 |   Packet Capture API    | (AF_PACKET, PF_RING, DPDK)
 +-------------------------+
            |
            v
 +-------------------------+
 |      Event Engine       |  <--- C++ Core
 |  (Protocol Analyzers &  |
 |   State Management)     |
 +-------------------------+
            |  Generates Events (e.g., http_request, file_extracted)
            v
 +-------------------------+
 |  Policy Script Engine   |  <--- Zeek Scripting Language
 |  (Base Scripts + Custom)|
 +-------------------------+
            |  Executes actions based on state & events
            v
 +-------------------------+
 |       Log Files         | (conn.log, http.log, dns.log, files.log)
 +-------------------------+
```

## 5. The Holy Grail: Core Zeek Logs

Zeek generates dozens of tab-separated value (TSV) or JSON logs. Understanding the schema of these logs is crucial for threat hunting.

### 5.1 `conn.log` (Connection Log)

The foundation of Zeek logging. It represents a single flow or connection (TCP, UDP, ICMP).

- `id.orig_h`, `id.orig_p`: Source IP and Port.
- `id.resp_h`, `id.resp_p`: Destination IP and Port.
- `uid`: A unique identifier for the connection (e.g., `C123abc456def`). This UID acts as a foreign key, allowing correlation across logs.
- `orig_bytes`, `resp_bytes`: Data payload sent and received.
- `conn_state`: State of the connection (`SF` for normal setup/teardown, `S0` for connection attempt seen, no reply).

### 5.2 `http.log`

Contains metadata parsed from HTTP traffic.

- `method`, `host`, `uri`, `user_agent`, `status_code`.
- Excellent for hunting SQL injection (anomalous `uri`), C2 beaconing (weird `user_agent`), or DGA domains (random `host`).

### 5.3 `dns.log`

Logs DNS queries and responses.

- `query`: The domain requested.
- `qtype_name`: Record type (A, AAAA, TXT).
- `answers`: The resolved IPs or text.
- Essential for hunting DNS tunneling, Fast Flux infrastructure, or malware resolution.

### 5.4 `files.log`

Logs metadata about files transferred over supported protocols (HTTP, FTP, SMTP, SMB).

- `mime_type`: Derived from magic bytes (file carving), not the extension. (An `.exe` renamed to `.txt` will accurately be logged as `application/x-dosexec`).
- `md5`, `sha1`, `sha256`: Hash of the transferred file (if enabled in scripts).
- `extracted`: Path to the file if Zeek was configured to automatically dump it to disk.

### 5.5 `ssl.log`

Tracks TLS/SSL negotiations.

- `server_name`: The SNI (Server Name Indication) requested.
- `ja3`, `ja3s`: Client and server TLS fingerprints, heavily used in modern encrypted C2 hunting.

## 6. Analyzing Zeek Logs at the CLI

Because Zeek's default output is TSV, standard Linux utilities (`awk`, `grep`, `sort`, `uniq`) are incredibly powerful. 

Zeek includes a specialized tool called `zeek-cut` to parse column names.

### 6.1 Basic Examples

```bash
# Find the top 10 destination IPs by bytes sent in conn.log
cat conn.log | zeek-cut id.resp_h orig_bytes | sort | awk '{arr[$1]+=$2} END {for (i in arr) print arr[i], i}' | sort -nr | head -n 10

# Find unique HTTP User-Agents across all HTTP logs
cat http.log | zeek-cut user_agent | sort | uniq -c | sort -nr

# Correlate a UID from an IDS alert to all related Zeek L7 logs
grep "CHereIsAUniqueUID123" *.log
```

### 6.2 Advanced Time Manipulation

Zeek stores time in Epoch format. `zeek-cut` can natively convert this for human readability.

```bash
# Convert Epoch time to human-readable format while parsing DNS queries
cat dns.log | zeek-cut -d ts query | head -n 5
```

## 7. Advanced Zeek Frameworks

### 7.1 The Intelligence Framework

Zeek allows you to ingest Threat Intelligence (TI) feeds (IPs, domains, hashes, URLs) directly via CSV files. 

When an indicator is observed anywhere in the network traffic stream, Zeek automatically generates an alert in `intel.log`.

### 7.2 The Notice Framework

While Zeek is not primarily an IDS, the Notice Framework allows it to act like one. 

Scripts can raise "Notices" (alerts) for specific behaviors, such as seeing cleartext passwords over HTTP, detecting an SSH brute-force attack based on connection timing, or identifying self-signed SSL certificates.

### 7.3 Dynamic Protocol Detection (DPD)

Unlike traditional tools that assume port 80 is HTTP, Zeek uses DPD. It analyzes the byte stream. 

If a user runs an SSH server on port 80, Zeek's DPD identifies the SSH protocol signature, generates an `ssh.log` entry, and logs the anomaly.

## 8. Real-World Attack Scenario

**Scenario:** A threat hunter is looking for signs of data exfiltration over encrypted channels.

1. The hunter examines `conn.log` for connections to anomalous geographic regions or newly observed ASNs with high data transfer.
2. They identify a long-standing TCP connection on port 443 with a massive `orig_bytes` value (e.g., 50GB sent) and a low `resp_bytes` value.
3. Using the `uid` from `conn.log`, the hunter pivots to `ssl.log` to investigate the TLS negotiation.
4. They observe the `server_name` (SNI) is a dynamic DNS provider (`suspicious-upload.ddns.net`).
5. Further, the `ja3` hash matches a known custom exfiltration tool (e.g., a custom compiled Rclone binary).
6. The exfiltration attempt is confirmed and characterized despite the payload being fully encrypted.

## 9. Zeek Cluster Deployment

For high-speed environments, Zeek must be clustered.
- **Manager:** Receives logs and notices from workers, handles state that needs to be global.
- **Logger:** Offloads disk I/O from the manager.
- **Workers:** The nodes actually doing the packet processing and event generation. Load is balanced via PF_RING or AF_PACKET.
- **Proxy:** Intermediary state storage for workers.

## 10. Chaining Opportunities

- **Custom Scripts:** To further extend Zeek's capabilities, analysts write custom scripts to parse proprietary protocols.
- **C2 Hunting:** Zeek logs (specifically `conn.log` and `dns.log`) are perfectly suited for long-tail analysis to find periodic beacons.

## 11. Related Notes

- [[01 - Packet Capture PCAP Analysis at Scale]]
- [[03 - Writing Custom Zeek Scripts for Detection]]
- [[04 - Suricata IDS IPS Rule Writing and Tuning]]
- [[05 - Hunting for C2 Beacons and Jitter]]
