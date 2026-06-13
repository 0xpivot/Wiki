---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.10 Data Sources Endpoint Network and Cloud"
---

# 88.10 Data Sources: Endpoint, Network, and Cloud

## 1. Introduction: The Visibility Triad
Threat hunting relies entirely on the quality, depth, and retention of the data available to the hunter. Without comprehensive visibility, a hunter is effectively blind. The modern enterprise environment requires a **"Visibility Triad"** approach, meaning logs must be collected from three distinct domains: the Endpoint, the Network, and the Cloud. 

Relying on only one source leaves massive operational blind spots. For instance, if an attacker uses heavily encrypted command and control (C2) traffic, network sensors will be blind to the payload, necessitating endpoint visibility. Conversely, if an attacker obtains SYSTEM privileges and disables the endpoint logging agent (EDR/Sysmon), the network sensor becomes the sole source of truth to detect the exfiltration.

## 2. Endpoint Data Sources (The Micro View)
Endpoint data provides the most granular view of what is happening on a specific host (workstation or server). It tells you exactly what processes executed, what files were touched, and what memory spaces were manipulated.

### 2.1 Sysmon (System Monitor)
A free Windows Sysinternals tool that provides highly detailed logging of system activity to the Windows Event Log. It is the gold standard for free endpoint visibility and is heavily utilized in mature hunting environments.
- **Key Event IDs for Hunters:**
  - `Event ID 1`: Process Creation. Includes command-line arguments, hashes, and parent process GUIDs. Critical for detecting LOLBins.
  - `Event ID 3`: Network Connection. Links a specific executing process to an outbound IP/Port.
  - `Event ID 8`: CreateRemoteThread. Crucial for detecting advanced process injection techniques.
  - `Event ID 11`: FileCreate. Useful for tracking dropped malware or webshells.
  - `Event ID 22`: DNSEvent. Maps DNS queries back to the specific process making them.

### 2.2 Endpoint Detection and Response (EDR)
Commercial EDRs (CrowdStrike Falcon, SentinelOne, Microsoft Defender for Endpoint) provide similar data to Sysmon but include kernel-level telemetry, automated block capabilities, and memory introspection APIs. They often stream this telemetry directly to a vendor-managed data lake.

### 2.3 Linux Auditd / eBPF
For Linux environments, `auditd` has historically been used to track system calls and file access. However, modern cloud-native environments are shifting toward **eBPF (Extended Berkeley Packet Filter)** based sensors (like Cilium, Falco, or Tracee), which provide high-performance, low-overhead observation of kernel and network events directly from the Linux kernel.

## 3. Network Data Sources (The Macro View)
Network data provides the ground truth of communications. An attacker can lie to an Operating System, employ rootkits to hide processes, or tamper with event logs, but they cannot hide their packets if they want to communicate over the network.

### 3.1 Zeek (Formerly Bro)
Zeek is an open-source network analysis framework. Unlike an IDS (like Snort) which alerts on known-bad signatures, Zeek records *everything* in highly structured, tab-separated transaction logs. It is a hunter's best friend.
- **conn.log:** Records every TCP/UDP connection, duration, and byte counts. Excellent for finding C2 beacons.
- **http.log:** Records URIs, User-Agents, and HTTP methods. Great for finding anomalous download requests.
- **dns.log:** Records all DNS queries and responses. Crucial for finding DGAs or DNS tunneling.
- **ssl.log / x509.log:** Extracts certificate details, TLS versions, and JA3/JA3S fingerprints without needing to decrypt the traffic.

### 3.2 Full Packet Capture (PCAP)
PCAP records the entire network packet, including the payload. It is incredibly expensive to store and usually only kept for a few days due to storage constraints. However, it is invaluable during Incident Response to see exactly what data was exfiltrated, what exploit payload was delivered, or what credentials were stolen over cleartext protocols.

### 3.3 NetFlow / IPFIX
Provides metadata about network traffic (Source IP, Dest IP, Ports, Bytes) without the payload or application-layer context. It is lightweight, cheap to store for months, and excellent for long-term baseline analysis and detecting volumetric anomalies (e.g., massive data transfers).

## 4. Cloud Data Sources (The Distributed View)
The shift to Infrastructure as a Service (IaaS) and Software as a Service (SaaS) means traditional endpoint and network tools are often blind. Cloud logging relies on API telemetry and control plane activity.

### 4.1 AWS CloudTrail / Azure Activity Logs / GCP Audit Logs
These services log every API call made within the cloud environment. They are the absolute source of truth for cloud management.
- **Hunt Use Case:** Detecting an attacker who compromised IAM credentials and is attempting to enumerate S3 buckets, snapshot EBS volumes for data theft, or spin up unauthorized GPU instances for cryptomining.

### 4.2 VPC Flow Logs
The cloud equivalent of NetFlow. It records IP traffic going to and from network interfaces in a Virtual Private Cloud (AWS VPC, Azure VNet).
- **Hunt Use Case:** Detecting a compromised EC2 instance attempting to map the internal cloud subnet (port scanning) or communicating with known malicious external IPs.

### 4.3 Identity Provider (IdP) Logs
Logs from authentication systems like Azure Active Directory (Entra ID), Okta, or Duo.
- **Hunt Use Case:** Detecting MFA fatigue attacks (spamming a user with push notifications), impossible travel, or lateral movement via compromised session cookies and identity tokens.

## 5. Real-World Attack Scenario

### The Scenario: The "Blind Spot" Pivot
An attacker compromises an employee's home laptop (BYOD) via a phishing email. The laptop is not managed by IT and has no EDR installed. The employee then connects to the corporate network via VPN.

**The Hunt using the Visibility Triad:**
1. **Endpoint Failure:** The hunter cannot see the initial malware execution because the BYOD laptop lacks EDR/Sysmon.
2. **Network Success:** The hunter analyzes the Zeek `conn.log` and notices the VPN IP address acting anomalously. It is initiating port 445 (SMB) connections to every server in the data center, followed by a massive spike in data transfer over MSRPC (Zeek `dce_rpc.log`). This indicates lateral movement and staging.
3. **Cloud Success:** The attacker extracts a hardcoded AWS access key from a compromised internal server. The attacker attempts to use the key from an external VPS to steal data. The hunter monitors AWS CloudTrail and detects a `sts:GetCallerIdentity` call followed by `s3:ListBuckets` originating from an unapproved Tor exit node IP.
4. **Resolution:** By correlating the network flow data with the cloud control plane data, the hunter pieces together the entire attack path, despite having zero visibility into the originating compromised endpoint.

## 6. ASCII Diagram: The Visibility Architecture

```text
                      [ THE VISIBILITY TRIAD ]

   [ 1. ENDPOINT ]           [ 2. NETWORK ]             [ 3. CLOUD ]
   (The "What & Who")        (The "How & Where")        (The "Control Plane")
         |                         |                          |
   - Sysmon (Process)        - Zeek (App Layer)         - CloudTrail (AWS API)
   - EDR (Memory/Files)      - PCAP (Full Payload)      - VPC Flow Logs
   - Windows Event Logs      - NetFlow (Volume)         - Okta/Entra ID (Auth)
   - Auditd/eBPF (Linux)     - Suricata/Snort (IDS)     - O365 / Workspace
         |                         |                          |
         \-------------------------+--------------------------/
                                   |
                                   v
                      [ DATA NORMALIZATION (Logstash/Vector) ]
                                   |
                                   v
                         [ DATA LAKE / SIEM ]
                        (Splunk, Elastic, Sentinel)
                                   |
                                   v
                       [ THREAT HUNTING ENGINE ]
                       (Sigma Rules, Baselines, ML)
```

## 7. Importance of Parsing and Normalization
Having the data is only half the battle. If Windows logs a process name as `Image` and Sysmon logs it as `ProcessName` and Linux logs it as `exe`, hunters cannot write efficient queries. Implementing a standardized schema, such as the Elastic Common Schema (ECS) or Splunk Common Information Model (CIM), is mandatory for mature hunting.

## 8. Chaining Opportunities
- **[[07 - Baseline Establishment and Anomaly Detection]]**: You cannot establish network or endpoint baselines without first operationalizing high-fidelity data sources like Sysmon, Zeek, and CloudTrail.
- **[[09 - Threat Hunting Maturity Model THMM]]**: A Level 0 or Level 1 organization might only have perimeter firewall logs. Advancing to Level 2 or 3 requires deploying the full visibility triad described here.
- **[[08 - Using Sigma Rules for Vendor-Agnostic Hunting]]**: Sigma rules require standardized field names. Understanding the underlying data structures of EDR vs CloudTrail is crucial for writing effective, cross-platform Sigma detections.

## 9. Related Notes
- [[14 - Advanced Zeek Log Analysis]]
- [[17 - Sysmon Configuration and Tuning]]
- [[24 - Cloud Incident Response and API Auditing]]
- [[36 - eBPF for Cloud Native Security]]
- [[42 - Normalization with Elastic Common Schema ECS]]
