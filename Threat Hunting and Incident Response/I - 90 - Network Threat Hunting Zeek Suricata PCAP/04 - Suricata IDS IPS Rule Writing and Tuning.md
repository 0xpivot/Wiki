---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.04 Suricata IDS IPS Rule Writing and Tuning"
---

# Suricata IDS/IPS Rule Writing and Tuning

## 1. Introduction to Suricata

Suricata is an open-source, high-performance Network Intrusion Detection System (IDS), Intrusion Prevention System (IPS), and Network Security Monitoring (NSM) engine. 

Developed by the Open Information Security Foundation (OISF), it distinguishes itself from legacy engines like Snort (pre-Snort 3) through its robust multithreaded architecture, native hardware acceleration (eBPF/XDP), extensive protocol parsing, and L7 metadata outputs (EVE JSON).

While Zeek is ideal for anomaly hunting and metadata generation, Suricata excels at real-time signature matching, stream reassembly, and active intrusion prevention (dropping packets).

## 2. Suricata Multithreaded Architecture

Suricata's strength lies in its pipeline and threading design. 

It utilizes a multi-threaded architecture allowing it to process massive volumes of traffic by assigning different "flows" (connections) to different CPU threads.

```text
+-------------------+      +-------------------+      +-------------------+
|  Packet Capture   | ---> |  Stream Assembly  | ---> | Protocol Parsers  |
| (AF_PACKET/PF_RING|      | (TCP Reassembly,  |      | (HTTP, TLS, SMB,  |
| /DPDK)            |      |  Defragmentation) |      |  DNS, SSH)        |
+-------------------+      +-------------------+      +-------------------+
                                                            |
                                                            v
+-------------------+      +-------------------+      +-------------------+
|  Alert Output     | <--- |   Detect Engine   | <--- | L7 Metadata &     |
| (EVE JSON,        |      | (Signature Match, |      | App-Layer Buffers |
| fast.log, sysog)  |      |  Rule Evaluation) |      |                   |
+-------------------+      +-------------------+      +-------------------+
```

### 2.1 Runmodes

- **Autofp:** Packets from the same flow are assigned to a specific thread. Excellent for maintaining state and flow consistency.
- **Workers:** Threads do everything from capture to detection. Best for pure performance and IPS setups where dropping a packet instantly is required.

## 3. Anatomy of a Suricata Rule

A Suricata rule consists of three main components: Action, Header, and Options.

`alert tcp $EXTERNAL_NET any -> $HOME_NET 80 (msg:"ET EXPLOIT Possible Apache Log4j JNDI Payload"; flow:established,to_server; content:"${jndi:"; fast_pattern; classtype:attempted-admin; sid:2034647; rev:1;)`

### 3.1 The Action

Defines what happens when the signature matches.

- `alert`: Generate an alert in the logs.
- `drop`: Drop the packet (IPS mode only, requires inline deployment).
- `pass`: Ignore the packet (useful for whitelisting specific traffic).
- `reject`: Drop the packet and send a TCP RST or ICMP unreachable to terminate the session.

### 3.2 The Header

Defines the network routing context.

- Protocol: `tcp`, `udp`, `icmp`, `ip`, or parsed L7 protocols like `http`, `tls`, `smb`.
- IPs/Ports: Source IP/Port (`$EXTERNAL_NET any`) -> Direction (`->` or `<>`) -> Destination IP/Port (`$HOME_NET 80`).

### 3.3 The Options (Rule Body)

This is the core detection logic. Enclosed in parentheses and separated by semicolons.

- **Meta Keywords:** `msg` (the alert name), `sid` (Signature ID), `rev` (Revision number), `classtype`.
- **Payload Keywords:** `content` (string to search for), `nocase` (case-insensitive), `depth`, `offset`, `pcre` (Perl Compatible Regular Expressions).
- **Flow Keywords:** `flow:established,to_server` ensures the engine only evaluates this rule if the TCP 3-way handshake has completed and the packet is heading towards the server.

## 4. Advanced Rule Writing: Sticky Buffers

Modern Suricata rules rely heavily on "Sticky Buffers." 

Instead of searching the raw packet payload, protocol parsers extract specific fields and place them in optimized memory buffers. This vastly improves performance and accuracy.

Instead of searching the entire payload:

`content:"User-Agent|3a| curl";` (Searching raw HTTP payload, slow and error-prone)

We use Sticky Buffers:

`http.user_agent; content:"curl";` (Searching only the parsed User-Agent buffer, extremely fast)

### 4.1 Example: Writing a Rule for C2 Infrastructure

Suppose we have threat intel indicating a new C2 framework always communicates over TLS, uses a specific Subject Name in its certificate, and has a specific JA3 hash.

```snort
alert tls $EXTERNAL_NET 443 -> $HOME_NET any ( \
    msg:"THREAT-HUNT Custom C2 Framework TLS Characteristics observed"; \
    flow:established,from_server; \
    tls.cert_subject; content:"CN=malicious-c2.internal"; \
    ja3.hash; content:"e7d705a3286e19ea42f587b344ee6865"; \
    classtype:command-and-control; \
    sid:9000100; rev:1; \
)
```

## 5. Suricata Tuning and Alert Fatigue

A poorly tuned IDS is worse than no IDS. Alert fatigue destroys SOC morale. Tuning is a continuous process.

### 5.1 Thresholding and Suppression

Located in `threshold.config`.

- **Suppression (Whitelisting):** "Do not alert on SID 10001 if the source IP is our authorized vulnerability scanner."
  `suppress gen_id 1, sig_id 10001, track by_src, ip 10.0.0.50`

- **Thresholding (Rate Limiting):** "Only alert once every 60 seconds per destination IP for this noisy ping sweep rule."
  `threshold gen_id 1, sig_id 20005, type limit, track by_dst, count 1, seconds 60`

### 5.2 Flowbit Management

`flowbits` allow rules to track state across multiple packets and rules.

- Rule 1 checks for an exploit request: `flowbits:set,exploit_sent;`
- Rule 2 checks the server response, but *only* alerts if the first rule fired: `flowbits:isset,exploit_sent; content:"root::0:0:";`

## 6. The EVE JSON Output format

Suricata's greatest modernization is the `eve.json` log. 

It combines alerts, L7 metadata (similar to Zeek), flow records, and extracted file metadata into a single, structured JSON log easily ingestible by Elasticsearch, Splunk, or parsed with `jq`.

```json
{
  "timestamp": "2023-10-25T10:00:00",
  "event_type": "alert",
  "src_ip": "192.168.1.5",
  "dest_ip": "8.8.8.8",
  "alert": {
    "action": "allowed",
    "signature_id": 2027865,
    "signature": "ET INFO Suspicious DNS TXT Record",
    "category": "Misc activity"
  },
  "dns": {
    "type": "query",
    "rrname": "malicious-c2.com",
    "rrtype": "TXT"
  }
}
```

## 7. Variables and Configuration (`suricata.yaml`)

Tuning your environment variables is critical for minimizing false positives.

```yaml
vars:
  address-groups:
    HOME_NET: "[10.0.0.0/8,192.168.0.0/16]"
    EXTERNAL_NET: "!$HOME_NET"
    HTTP_SERVERS: "[10.0.5.0/24]"
```
Defining these accurately ensures rules looking for attacks *against* servers don't trigger when a client machine is browsing the web.

## 8. Real-World Attack Scenario

**Scenario:** A threat actor drops a webshell (`cmd.jsp`) on a vulnerable internet-facing Tomcat server.

1. The attacker accesses `http://victim.com/cmd.jsp?c=whoami`.
2. Suricata intercepts the packet. The HTTP protocol parser reads the request and buffers the URI into `http.uri`.
3. A rule fires: `alert http any any -> $HOME_NET any (msg:"Webshell Command Execution Attempt"; http.uri; content:".jsp?"; pcre:"/[?&]c=(whoami|id|ifconfig)/U"; sid:9000101;)`
4. The alert is written to `eve.json` containing the full HTTP metadata.
5. The SOC analyst views the alert in their SIEM and can immediately see the exact payload (`c=whoami`) and the server's HTTP response code (e.g., 200 OK, indicating successful execution) without needing a full PCAP.

## 9. Chaining Opportunities

- **Integration with PCAP:** Suricata alerts are the primary pivot points for requesting Full Packet Captures (FPC) from systems like Arkime.
- **Zeek Correlation:** Alert SIDs and timestamps can be correlated with Zeek's `conn.log` using standard 5-tuple matching to gain surrounding contextual network data.

## 10. Related Notes

- [[01 - Packet Capture PCAP Analysis at Scale]]
- [[02 - Introduction to Zeek Network Security Monitor]]
- [[03 - Writing Custom Zeek Scripts for Detection]]
- [[05 - Hunting for C2 Beacons and Jitter]]
