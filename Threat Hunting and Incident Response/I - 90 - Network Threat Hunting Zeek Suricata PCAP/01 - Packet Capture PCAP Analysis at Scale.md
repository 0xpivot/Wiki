---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.01 Packet Capture PCAP Analysis at Scale"
---

# Packet Capture (PCAP) Analysis at Scale

## 1. Introduction to Scalable PCAP Analysis

Packet capture analysis is the fundamental bedrock of network threat hunting and incident response. 

While analyzing a 10MB PCAP file in Wireshark on a local machine is a straightforward task, performing PCAP analysis *at scale*—across gigabit or terabit links traversing enterprise perimeters—introduces immense logistical, storage, and processing challenges. 

Full packet capture (FPC) requires specialized hardware, kernel bypass mechanisms, optimized storage architectures, and distributed processing pipelines. 

Without these components, security teams will suffer from packet loss, rendering forensic investigations incomplete and inaccurate.

## 2. The Challenges of Line-Rate Capture

At 10 Gbps, a network link generates approximately 1.25 Gigabytes of data per second. Over 24 hours, this equates to roughly 108 Terabytes of data. Processing and storing this data implies massive hurdles.

### 2.1 Packet Loss and Ring Buffer Exhaustion

The operating system's kernel networking stack is historically not designed for lossless capture at line rates exceeding 1 Gbps. 

Context switching between kernel space and user space creates latency. 

When a packet arrives, an interrupt is triggered, an `sk_buff` (socket buffer) is allocated in the kernel, and the data is copied to user space. 

At 14.8 million packets per second (line rate for 10Gbps with 64-byte packets), the CPU cannot process these interrupts fast enough, leading to full ring buffers and dropped packets.

### 2.2 Storage IOPS Bottlenecks

Sustained write speeds of >1 GB/s require highly optimized NVMe RAID arrays or specialized Storage Area Networks (SANs). 

Standard magnetic disks or even single SSDs cannot keep up with the constant random/sequential write IOPS required to flush memory buffers to disk without dropping packets.

### 2.3 Retrieval Latency and Indexing

Searching through petabytes of raw PCAP data using traditional tools like `tcpdump` or `tshark` is computationally unfeasible. 

Reading a 50TB PCAP sequentially to find a single IP address would take days. 

Therefore, indexing the metadata (IPs, ports, protocols) into a highly searchable database is mandatory.

## 3. Deep Dive: Kernel Bypass Mechanisms

To capture at line rate, we must bypass the standard Linux kernel network stack and its inherent overhead.

### 3.1 PF_RING & PF_RING ZC (Zero Copy)

- Developed by ntop.
- It creates a direct path from the NIC driver to user-space memory.
- ZC bypasses the kernel entirely, allowing for 10Gbps+ capture on commodity hardware.
- It maps the NIC's memory directly into the application's memory space, achieving "zero-copy" architecture.

### 3.2 AF_PACKET with FANOUT

- A native Linux socket type that requires no third-party kernel modules.
- Combined with `PACKET_MMAP` (memory-mapped ring buffers) and `PACKET_FANOUT`.
- Distributes load across multiple CPU cores by hashing the 5-tuple (Src IP, Dst IP, Src Port, Dst Port, Protocol).
- Provides a highly performant, kernel-native capture mechanism.

### 3.3 DPDK (Data Plane Development Kit)

- A set of libraries and drivers for fast packet processing.
- Maintained by the Linux Foundation.
- Completely offloads packet processing from the OS kernel to processes running in user space.
- Requires dedicated CPU cores running in a constant polling loop (100% CPU utilization) rather than relying on interrupts.

### 3.4 eBPF and XDP (eXpress Data Path)

- Allows eBPF programs to process or drop packets directly at the NIC driver level.
- Happens before an `sk_buff` is even allocated, saving massive CPU cycles.
- Extremely powerful for dropping known-bad or irrelevant traffic (like streaming video) before it hits the capture engine.

## 4. Distributed Capture Architecture Diagram

```text
      +-------------------+       +-------------------+       +-------------------+
      |   Network TAP /   |       |   Network TAP /   |       |   Network TAP /   |
      |   SPAN Port (DC)  |       |   SPAN Port (HQ)  |       |   SPAN Port (AWS) |
      +---------+---------+       +---------+---------+       +---------+---------+
                |                           |                           |
                v                           v                           v
      +-------------------+       +-------------------+       +-------------------+
      |  Sensor Node 1    |       |  Sensor Node 2    |       |  Sensor Node 3    |
      | (AF_PACKET/DPDK)  |       | (AF_PACKET/DPDK)  |       |   (Cloud Mirror)  |
      +---------+---------+       +---------+---------+       +---------+---------+
                | (PCAP via Stenographer/Arkime)                       |
                +---------------------------+--------------------------+
                                            |
                                            v
                                  +-------------------+
                                  | Centralized Index |
                                  |  (Elasticsearch/  |
                                  |   OpenSearch)     |
                                  +---------+---------+
                                            |
                                            v
                                  +-------------------+
                                  |  Threat Hunter /  |
                                  |   SOC Analyst     |
                                  +-------------------+
```

## 5. Advanced BPF (Berkeley Packet Filter) Strategies

When capturing multi-gigabit traffic, you cannot—and should not—capture everything. BPF is vital for data reduction.

### 5.1 Syntax and Compilation

BPF filters are compiled into a highly optimized bytecode that runs inside an in-kernel virtual machine. 

This ensures the filtering logic executes as close to the hardware as possible.

### 5.2 Common Exclusion Filters

You often want to exclude high-volume, low-value traffic such as:

- Streaming services (Netflix, YouTube, Spotify).
- Backup replication (Storage area networks, Veeam backups).
- Encrypted payloads where metadata is sufficient, but payload is opaque.

```bash
# Example BPF filter excluding known noisy ports but keeping TCP handshakes
not port 443 and not port 22 and not port 9000

# Keep only SYN and FIN packets for HTTPS to log connections without payloads
(tcp[tcpflags] & (tcp-syn|tcp-fin) != 0) and port 443
```

## 6. Large-Scale PCAP Platforms

### 6.1 Arkime (formerly Moloch)

Arkime is an open-source, large-scale, full packet capturing, indexing, and database system.

- **Capture Component:** Uses AF_PACKET, PF_RING, or DPDK to pull packets. It parses the L7 headers.
- **Viewer Component:** Node.js app providing an intuitive web interface for querying.
- **Elasticsearch Component:** Stores SPI (Session Profile Information) like IPs, domains, and extracted files.
- **On-Demand Retrieval:** The actual PCAP payload remains on the disk of the distributed capture nodes. Arkime dynamically fetches and merges the PCAP when an analyst clicks "Download PCAP".

### 6.2 Stenographer

Developed by Google, Stenographer is designed for highly reliable capture to disk.

- Intended to replace rolling `tcpdump` files which are prone to data loss under load.
- Analysts query Stenographer using standard BPF filters.
- It rapidly reads the specific requested packets from its optimized on-disk index.
- Serves them over a UNIX socket or stdout.

### 6.3 TShark at Scale (Parallelization)

For ad-hoc processing of massive PCAP files natively, standard `tshark` fails because it is single-threaded.

```bash
# 1. Splitting a massive PCAP into 1GB chunks using editcap
editcap -c 1000000 massive.pcap chunked_pcap_

# 2. Parallel TShark execution extracting HTTP Host headers
# Using GNU parallel distributes the load across all CPU cores
ls chunked_pcap_* | parallel -j 8 'tshark -r {} -Y "http.request" -T fields -e http.host' > all_hosts.txt

# 3. Sort and unique the results
cat all_hosts.txt | sort | uniq -c | sort -nr > top_hosts.txt
```

## 7. Threat Hunting Methodologies at Scale

### 7.1 Session Profiling

At scale, you rarely look at raw packets first. You convert PCAPs into metadata and hunt through those logs. 

Full packet capture is the *evidence*, while metadata is the *index*.

### 7.2 Volume and Timing Analysis

- Look for abnormal data transfer sizes (e.g., thousands of small connections vs one massive outbound connection) to identify data exfiltration.
- Identify periodic beaconing by analyzing the inter-arrival times of connections.

### 7.3 Protocol Mismatch Identification

- Identify anomalous traffic on standard ports (e.g., SSH running over port 80).
- Identify Command and Control (C2) frameworks hiding inside DNS TXT records or ICMP payloads.

## 8. Real-World Attack Scenario

**Scenario:** A large enterprise financial institution detects an anomaly: a spike in DNS traffic to a newly registered domain.

1. The SOC receives an alert from their Suricata IDS indicating high-volume DNS requests querying TXT records (`ET INFO Suspicious DNS TXT Record`).
2. The Threat Hunter pivots to the centralized **Arkime** instance.
3. They query the Elasticsearch index for the malicious domain (`host.dns: "malicious-c2.com"`).
4. Arkime retrieves the indexed session metadata within milliseconds, showing hundreds of thousands of requests originating from an internal, critical web server over the past 4 hours.
5. The Hunter uses Arkime's web interface to request the raw PCAP for only these specific sessions.
6. Arkime transparently reaches out to the specific sensor node storing the raw packets, extracts the relevant packets from disk, and presents a `.pcap` download.
7. The Hunter opens the precise, filtered PCAP in Wireshark.
8. By analyzing the payloads, they identify base64-encoded command-and-control instructions embedded within the DNS TXT responses.
9. The compromise and exact attacker commands are confirmed without the hunter ever having to manually sift through the 50 Terabytes of network traffic generated that day.

## 9. Glossary of Terms

- **AF_PACKET:** A Linux socket type used to capture packets at the data link layer.
- **DPDK:** Data Plane Development Kit; bypasses kernel networking to provide extreme packet processing speeds.
- **eBPF:** Extended Berkeley Packet Filter; safely runs sandboxed programs in the Linux kernel without changing kernel source code.
- **Zero-Copy:** A mechanism where CPU does not perform the task of copying data from one memory area to another, drastically saving overhead.
- **SPAN Port:** Switched Port Analyzer; mirrors traffic from one switch port to another for monitoring.

## 10. Chaining Opportunities

- **Zeek Integration:** PCAP analysis is vastly augmented when run through Zeek, creating structured metadata logs that are easier to parse than raw PCAP.
- **Suricata Detection:** Alerting off PCAP streams using Suricata provides the initial tipping mechanism, directing hunters to the specific timeframes for FPC retrieval.

## 11. Related Notes

- [[02 - Introduction to Zeek Network Security Monitor]]
- [[03 - Writing Custom Zeek Scripts for Detection]]
- [[04 - Suricata IDS IPS Rule Writing and Tuning]]
- [[05 - Hunting for C2 Beacons and Jitter]]
