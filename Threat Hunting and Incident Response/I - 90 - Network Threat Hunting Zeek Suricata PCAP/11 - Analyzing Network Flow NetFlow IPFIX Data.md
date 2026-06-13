---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.11 Analyzing Network Flow NetFlow IPFIX Data"
---

# Analyzing Network Flow NetFlow IPFIX Data

## Introduction to Network Flow Analysis
Network flow analysis is an essential capability for network threat hunting and incident response. While full packet capture (PCAP) provides the absolute ground truth regarding network communications by recording every single bit transmitted across the wire, storing PCAP data for extended periods across a large enterprise network is prohibitively expensive due to the massive volumes of data generated. In high-throughput environments, a 10 Gbps link can generate petabytes of PCAP data in a very short timeframe. 

Network flow data (such as NetFlow, IPFIX, and sFlow) solves this storage and processing problem by providing metadata about network connections without capturing the actual application payload. Flow data acts as the "phone bill" or "itemized billing record" of the network, showing who talked to whom, when the conversation started, for how long it lasted, and exactly how much data was transferred in each direction. This metadata is incredibly powerful for identifying anomalous behavior, command and control (C2) communication, large-scale data exfiltration, horizontal and vertical port scanning, and unauthorized lateral movement within the environment.

### The Evolution of Flow Protocols
Understanding the differences between flow protocols is crucial for a threat hunter, as the type of data available will dictate the hunting techniques that can be employed.

1. **NetFlow v5:** The traditional standard introduced by Cisco. It is fixed-format and primarily captures the standard 5-tuple (Source IP, Destination IP, Source Port, Destination Port, Protocol) along with byte and packet counts, ToS (Type of Service), and TCP flags. Its rigid structure limits its utility in modern, complex threat hunting scenarios where application-layer context is often needed.
2. **NetFlow v9:** A template-based evolution of NetFlow that allows for flexible and extensible record formats. Exporters send templates that define the structure of the data, followed by the actual data records. This allows for the inclusion of non-standard fields, such as MAC addresses, VLAN IDs, and IPv6 data.
3. **IPFIX (IP Flow Information Export):** The IETF standard (RFC 7011) based heavily on NetFlow v9. IPFIX is highly extensible, allowing vendors to define Enterprise-Specific Information Elements (IEs). This means modern IPFIX exporters can include layer 7 application identification, HTTP host headers, TLS SNI (Server Name Indication) values, and even user identities directly within the flow record. For modern threat hunting, IPFIX is the gold standard.
4. **sFlow (Sampled Flow):** Unlike NetFlow and IPFIX, which track stateful flows, sFlow is a stateless packet sampling protocol (e.g., capturing 1 out of every 1000 packets). While highly scalable for massive core networks, sFlow is generally less useful for precise threat hunting because it can completely miss short-lived, low-volume connections (like a single malicious DNS request or a brief C2 beacon).

## The Architecture of Flow Analysis

A robust flow analysis architecture must be capable of ingesting tens of thousands of flows per second, parsing them in real-time, and storing them in a highly queryable format.

### Architectural Components
1. **Flow Exporter:** Network devices (routers, core switches, edge firewalls) or dedicated software sensors (like Zeek or fprobe) that observe network traffic, aggregate packets into flow states, and periodically export the flow records when the flow terminates or a timeout is reached.
2. **Flow Collector:** A dedicated server or cluster that listens on specific UDP ports (typically 2055, 4739, or 9995) to receive flow records from multiple exporters across the enterprise. The collector parses the proprietary or template-based binary formats into a structured format (like JSON).
3. **Data Lake / SIEM:** The parsed flows are shipped to a centralized repository, typically an Elasticsearch cluster, Splunk, or a cloud-native SIEM (like Microsoft Sentinel or Google Chronicle).
4. **Analytics Engine:** The interface where threat hunters craft queries, build dashboards, and run machine learning algorithms against the flow data.

```ascii
+-----------------------------------------------------------------------------------+
|                                 ENTERPRISE NETWORK                                  |
|                                                                                   |
|  +-------------------+      +-------------------+      +-------------------+      |
|  |   Core Switch     |      |  Edge Firewall    |      |  Cloud VPC Router |      |
|  |  (Cisco Nexus)    |      |   (Palo Alto)     |      |    (AWS Transit)  |      |
|  |  [IPFIX Exporter] |      | [NetFlow v9 Exp]  |      |  [VPC Flow Logs]  |      |
|  +--------+----------+      +---------+---------+      +----------+--------+      |
|           |                           |                           |               |
+-----------|---------------------------|---------------------------|---------------+
            | UDP 4739                  | UDP 2055                  | API Export
            v                           v                           v
+-----------------------------------------------------------------------------------+
|                               FLOW INGESTION LAYER                                  |
|  +-----------------------------------------------------------------------------+  |
|  |                              Logstash / Fluentd                             |  |
|  |  (Receives UDP packets, applies IPFIX templates, enriches with GeoIP/ASN)   |  |
|  +------------------------------------+----------------------------------------+  |
+---------------------------------------|-------------------------------------------+
                                        | JSON Encoded Flow Records
                                        v
+-----------------------------------------------------------------------------------+
|                                 DATA STORAGE TIER                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                           Elasticsearch Cluster                             |  |
|  |                 (Hot/Warm/Cold architecture for long-term retention)        |  |
|  +------------------------------------+----------------------------------------+  |
+---------------------------------------|-------------------------------------------+
                                        | REST API Queries (KQL/Lucene)
                                        v
+-----------------------------------------------------------------------------------+
|                               ANALYTICS & HUNTING                                   |
|  +----------------------+  +-----------------------+  +------------------------+  |
|  |   Kibana Dashboard   |  |  Jupyter Notebooks    |  |     RITA / ML Engine   |  |
|  | (Visualizations)     |  | (Pandas DataFrames)   |  | (Beaconing Detection)  |  |
|  +----------------------+  +-----------------------+  +------------------------+  |
+-----------------------------------------------------------------------------------+
```

## Advanced Threat Hunting Methodologies with Flow Data

Threat hunting with flow data requires transitioning from searching for known indicators of compromise (IoCs) to searching for indicators of behavior (IoBs). Since flows lack payload data, hunters must focus on the metadata attributes that betray malicious intent.

### 1. Identifying Command and Control (C2) Beacons
Adversaries use beacons to maintain persistence and check for new tasks from their C2 infrastructure. Beacons are characterized by periodic, automated communication. Human-driven traffic is highly variable; machine-driven traffic is highly predictable.

**Hunting Strategies:**
- **Inter-Arrival Time (IAT) Analysis:** Calculate the time difference between consecutive flows from the same internal IP to the same external IP. If the standard deviation of the IAT over a 24-hour period is close to zero, it is highly likely to be an automated process.
- **Jitter Detection:** Modern malware introduces "jitter" (randomized delays) to evade basic IAT analysis. For example, a 60-second beacon with 20% jitter will trigger anywhere between 48 and 72 seconds. Advanced hunters use statistical variance or Fast Fourier Transforms (FFT) to detect the underlying frequency despite the jitter.
- **Byte Ratio Consistency:** C2 beacons often have extremely consistent payload sizes for their check-in requests and empty responses. Looking for a high number of connections where `bytes_in` and `bytes_out` remain constant is a strong indicator.

**Example Splunk SPL Query for Basic Beaconing Detection:**
```spl
index=network sourcetype=netflow
| stats count, earliest(_time) as first_seen, latest(_time) as last_seen, dc(dest_port) as unique_ports by src_ip, dest_ip
| eval duration = last_seen - first_seen
| eval connections_per_hour = count / (duration / 3600)
| where duration > 3600 AND connections_per_hour > 10 AND unique_ports = 1
| sort - connections_per_hour
```

### 2. Detecting Data Exfiltration
Data exfiltration is the ultimate goal of many targeted attacks. While DLP solutions look at the content, flow analysis looks at the volume and destination of the transfer.

**Hunting Strategies:**
- **Baseline Deviations:** Calculate the average daily outbound data volume for specific assets (e.g., a database server should have near zero outbound internet traffic). Flag any IP that exceeds its baseline by a specific multiplier (e.g., 3x standard deviation).
- **Long-Duration Connections:** Attackers may throttle exfiltration over a single long-lived connection to avoid traffic spikes. Hunt for flows that last longer than 12 hours.
- **Protocol Anomaly:** Look for large amounts of data leaving the network over protocols typically used for small transactions (e.g., DNS, ICMP). A single flow showing 50MB of DNS traffic is a massive red flag indicating DNS tunneling.

**Example KQL (Kibana) for identifying massive internal-to-external transfers:**
```kql
network.direction: "outbound" AND
source.ip: 10.0.0.0/8 AND
NOT destination.ip: (10.0.0.0/8 OR 172.16.0.0/12 OR 192.168.0.0/16) AND
network.bytes > 500000000 
```

### 3. Spotting Lateral Movement and Internal Reconnaissance
Once inside, adversaries must map the network and move to their objective. This activity generates highly anomalous internal flow patterns.

**Hunting Strategies:**
- **Horizontal Port Scanning:** Look for a single internal source IP connecting to a large number of unique internal destination IPs on a single specific port within a short timeframe. Common targets include TCP 445 (SMB), 3389 (RDP), 22 (SSH), and 5985/5986 (WinRM).
- **Vertical Port Scanning:** Look for a single source IP connecting to a large number of unique destination ports on a single target IP.
- **Workstation-to-Workstation Traffic:** In a standard enterprise, workstations communicate with servers (domain controllers, file servers, web proxies). Workstations rarely initiate connections directly to other workstations. Peer-to-peer flows between user subnets should be heavily scrutinized for lateral movement via tools like PsExec or WMI.

## Advanced Analytics: Long Tail and Graph Theory
Beyond simple statistical thresholds, mature threat hunting teams employ advanced data science techniques on flow data.
- **Long Tail Analysis:** Instead of looking for high-volume activity, hunters look for the absolute rarest events. Grouping all external destinations by the number of connections and investigating the IPs that were contacted exactly once or twice across the entire enterprise can reveal highly targeted, low-and-slow C2 channels.
- **Graph Theory / Network Mapping:** By representing IP addresses as nodes and flows as edges, hunters can use graph algorithms (like PageRank or Centrality) to identify critical choke points or spot compromised hosts that are suddenly acting as internal hubs for communication.

## Real-World Attack Scenario

### The Scenario: APT29 (Cozy Bear) Style Stealthy Breach
A defense contractor was compromised by an advanced persistent threat (APT) group. The adversary successfully bypassed EDR solutions on the initial endpoint and maintained a stealthy presence for several months before being detected.

### The Attack Flow
1. **Initial Compromise:** A developer downloaded a trojanized software package. The execution established a highly stealthy C2 channel using domain fronting over HTTPS to an adversary-controlled server (`198.51.100.77`).
2. **Stealthy Beaconing:** To avoid detection, the beacon was configured with an extremely long sleep interval of 12 hours, with a massive jitter of 50%. This meant connections could happen anywhere from 6 to 18 hours apart.
3. **Internal Recon:** The attacker did not use noisy network scanners like Nmap. Instead, they used native Windows tools (`net.exe`, `nltest.exe`) and single-packet SYN probes to slowly map out domain controllers.
4. **Data Staging and Exfiltration:** The attacker staged sensitive intellectual property into a compressed, encrypted archive on an internal staging server (`10.50.20.15`). The exfiltration was performed via an encrypted reverse proxy tunnel established over an obscure high port (TCP 44443).

### How Flow Analysis Detected the Activity
The hunt team uncovered the breach entirely through NetFlow analysis, as the endpoint logs had been tampered with by the adversary.
1. **Uncovering the C2:** Standard beacon detection queries missed the 12-hour jittered C2. However, a long-tail analysis of outbound TLS traffic revealed that the developer's workstation was making highly infrequent, small byte-count connections to a specific CDN edge node that no other system in the enterprise was talking to.
2. **Tracing the Internal Recon:** By reviewing the flow logs for the developer's workstation, the team noticed a slow, methodical horizontal scan on TCP 445 (SMB) across the server subnet. Instead of thousands of connections per minute, the flow logs showed one connection every few minutes over the course of several days—a pattern clearly designed to evade IDS rate-limiting.
3. **Discovering the Exfiltration:** The most glaring anomaly was found when querying for long-duration outbound flows on non-standard ports. A query isolating flows lasting longer than 4 hours on ports other than 80 or 443 immediately highlighted a 9-hour connection from the internal staging server (`10.50.20.15`) to an external IP on TCP 44443, transferring exactly 45 GB of data. The NetFlow record provided the exact timestamp, duration, source, destination, and byte count, providing the IR team with everything they needed to isolate the staging server and begin remediation.

## Best Practices for Flow Collection
- **Ensure Accurate Time Synchronization:** Flow data is heavily reliant on precise timestamps. Ensure all exporters, collectors, and analytics engines are strictly synchronized using a reliable NTP source. Minor time drifts can ruin inter-arrival time calculations.
- **Strategic Placement of Sensors:** Collecting flows from every edge firewall is crucial for North-South visibility (C2 and exfiltration). Collecting flows from core switches is essential for East-West visibility (lateral movement).
- **Use Enriched Flows (Zeek/IPFIX):** Whenever possible, upgrade from standard NetFlow v5 to Zeek connection logs (`conn.log`) or highly customized IPFIX templates. The addition of application-layer protocol identification and TLS metadata exponentially increases the value of flow data for threat hunting.

## Chaining Opportunities
- **[[08 - Understanding Zeek Architecture and Logs]]**: Zeek takes the concept of network flow analysis to the next level by providing application-aware metadata. Understanding Zeek's `conn.log` is a direct continuation of this topic.
- **[[13 - RITA Real Intelligence Threat Analytics for C2]]**: RITA is a purpose-built tool designed specifically to automate the statistical analysis of flow data (specifically Zeek logs) to find the beaconing and long-connections discussed in this note.
- **[[14 - Correlating Network and Endpoint Events]]**: Once a suspicious flow is identified, the next logical step is to correlate the 5-tuple information with endpoint telemetry (like Sysmon Event ID 3) to identify the specific process executable that generated the traffic.

## Related Notes
- [[12 - Detecting Suspicious User Agent Strings]]
- [[15 - Dealing with Encrypted Network Traffic in Hunts]]
- [[04 - Threat Hunting Methodologies]]
- [[22 - Advanced Persistent Threats (APTs) Tactics]]
