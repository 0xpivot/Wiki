---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.05 Hunting for C2 Beacons and Jitter"
---

# Hunting for Command and Control (C2) Beacons and Jitter

## 1. Introduction to C2 Infrastructure

Command and Control (C2) infrastructure is the lifeline of any advanced persistent threat (APT) operation or ransomware deployment. 

To remain undetected, modern malware does not maintain a constant, noisy TCP connection to the attacker's server. 

Instead, it "beacons"—calling home at regular intervals over standard protocols like HTTP/HTTPS or DNS to ask for new instructions and upload results. 

Hunting for these beacons is a critical component of network threat hunting, requiring statistical analysis of network metadata rather than simple signature matching.

## 2. The Anatomy of a Beacon

A beacon is a periodic network connection initiated by the compromised host.

### 2.1 Key Metrics of a Beacon

1. **Sleep Time (Interval):** The base duration the malware waits between check-ins. If the sleep time is 60 seconds, the malware reaches out at T+0, T+60, T+120.
2. **Jitter:** A randomization factor applied to the sleep time to evade simple periodic detection algorithms. If the sleep time is 60 seconds with a 10% jitter, the actual interval will randomly fluctuate between 54 and 66 seconds.
3. **Payload Size:** Beacons often have very small, consistent payload sizes (e.g., an HTTP GET request with a small encrypted cookie, followed by a 200 OK response with a small encrypted instruction).

## 3. Threat Hunting Methodology: Long-Tail and Statistical Analysis

Hunting for beacons involves analyzing massive volumes of connection metadata (typically Zeek `conn.log` or NetFlow) and looking for the "long tail" of the distribution and statistical anomalies.

### 3.1 Connection Frequency & Dispersion

We group network connections by Source IP and Destination IP. We then analyze the time delta (inter-arrival time) between successive connections.

If an internal IP talks to an external IP 1,440 times a day, and the time delta between *every single connection* is exactly 60 seconds, this is a deterministic, 100% periodic beacon. The standard deviation of the time deltas approaches zero.

Even with jitter applied, statistical models can identify the clustering of intervals. 

If a malware uses a 60s sleep with 20% jitter, the histogram of inter-arrival times will show a clear normal distribution centered tightly around 60 seconds, unlike organic human web browsing which is highly erratic.

### 3.2 C2 Beaconing Architecture Diagram

```text
       Internal Network                      Internet
+---------------------------+       +-------------------------+
|                           |       |                         |
|   +---------------+       |       |     +--------------+    |
|   | Compromised   |       |       |     |  Attacker C2 |    |
|   | Workstation   |       |       |     |  Server      |    |
|   | (10.0.5.10)   |       |       |     | (198.51.100.2|    |
|   +-------+-------+       |       |     +------+-------+    |
|           |               |       |            ^            |
|           |               |       |            |            |
+-----------|---------------+       +------------|------------+
            |                                    |
            |                                    |
            |   T=0:   HTTPS GET /api/v1     --->|
            |   T=60:  HTTPS GET /api/v1     --->| (No Jitter, Highly Detectable)
            |   T=120: HTTPS GET /api/v1     --->|
            |                                    |
            |   T=180: HTTPS GET /api/v1     --->|
            |   T=243: HTTPS GET /api/v1     --->| (With 10% Jitter)
            |   T=296: HTTPS GET /api/v1     --->|
```

## 4. Tools for Beacon Hunting

### 4.1 RITA (Real Intelligence Threat Analytics)

Developed by Active Countermeasures, RITA is an open-source framework specifically designed to ingest Zeek logs and calculate statistical beaconing scores based on mathematical models.

RITA analyzes:

- **Connection Dispersion:** How evenly spaced are the connections?
- **Data Size Dispersion:** Is the amount of data transferred in each session nearly identical?
- **Duration Dispersion:** Do the connections last the exact same amount of time?

It outputs a normalized "Score" (0.0 to 1.0). A score of 0.99 strongly implies an automated, non-human beaconing process.

```bash
# Ingesting Zeek logs into RITA's MongoDB backend
rita import /opt/zeek/logs/2023-10-25/ dataset_name

# Viewing the highest scored beacons
rita show-beacons dataset_name | head -n 20
```

### 4.2 Analyzing Encrypted Channels (JA3/JA3S)

Modern C2 beacons utilize HTTPS (TLS). Since the URI, Host headers, and payloads are encrypted, we cannot easily inspect the traffic content.

- **JA3** fingerprints the client's SSL/TLS `Client Hello` packet (SSL version, cipher suites, elliptic curve extensions).
- **JA3S** fingerprints the server's `Server Hello` packet.

Many C2 frameworks (e.g., Cobalt Strike, Metasploit, Covenant, Sliver) use custom TLS implementations or specific networking libraries (like older versions of Python `requests` or Golang crypto libraries) that produce unique JA3 hashes, distinct from a standard Google Chrome browser.

By combining periodic beacon detection with rare or known-malicious JA3 hashes, the fidelity of the hunt increases drastically.

### 4.3 Data Stacking (Frequency Analysis via CLI)

Using standard Linux CLI tools on Zeek `http.log` to find rare user agents, or `conn.log` to find consistent byte counts.

```bash
# Find the least common HTTP User-Agents (Long-Tail Analysis)
cat http.log | zeek-cut user_agent | sort | uniq -c | sort -n | head -n 20

# Find destination IPs that have exact byte counts across multiple connections
cat conn.log | zeek-cut id.orig_h id.resp_h orig_bytes resp_bytes | sort | uniq -c | awk '$1 > 100 {print $0}'
```

## 5. Legitimate Beacons (False Positives)

The biggest challenge in beacon hunting is filtering out legitimate telemetry and background processes.

- **NTP (Network Time Protocol):** Highly periodic by design.
- **Windows Updates / WSUS:** Software update checkers reach out at set intervals.
- **Antivirus / EDR Telemetry:** Security agents beacon to their cloud consoles constantly.
- **Web Analytics:** Pages left open in a browser running background AJAX refreshes.

A mature hunting program maintains extensive whitelists for known legitimate internal and external services.

## 6. Real-World Attack Scenario

**Scenario:** A threat hunting team is performing proactive analysis using RITA against 7 days of Zeek logs.

1. The analyst runs `rita show-beacons` and notices an internal HR workstation (10.1.20.50) communicating with an external IP in DigitalOcean (167.71.x.x).
2. RITA reports a beacon score of `0.96`, indicating highly periodic traffic.
3. The analyst pivots to the raw Zeek `conn.log` and observes connections occurring approximately every 300 seconds (5 minutes) with a variation of +/- 15 seconds (jitter).
4. Checking `ssl.log`, the analyst extracts the JA3 hash of the connection.
5. They cross-reference the JA3 hash with Threat Intelligence platforms, discovering it matches a known fingerprint for the `Sliver` C2 framework's HTTP beacon.
6. The analyst initiates Incident Response procedures, isolating the HR workstation and identifying a malicious Excel macro execution as the root cause.

## 7. Chaining Opportunities

- **Zeek Automation:** Automate the ingestion of Zeek logs into RITA or Elasticsearch for daily automated beacon scoring and dashboarding.
- **Suricata Alerting:** Once a C2 JA3 hash or periodic IP is discovered via hunting, write a Suricata rule to instantly block or alert on future occurrences, closing the loop between hunting and detection.

## 8. Related Notes

- [[01 - Packet Capture PCAP Analysis at Scale]]
- [[02 - Introduction to Zeek Network Security Monitor]]
- [[03 - Writing Custom Zeek Scripts for Detection]]
- [[04 - Suricata IDS IPS Rule Writing and Tuning]]
