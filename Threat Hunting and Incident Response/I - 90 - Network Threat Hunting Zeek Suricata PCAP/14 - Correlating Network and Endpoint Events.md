---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.14 Correlating Network and Endpoint Events"
---

# Correlating Network and Endpoint Events

## Introduction to Correlation
In modern threat hunting and incident response, isolated visibility is a critical weakness. Network telemetry (Zeek, Suricata, PCAP, NetFlow) provides the "What" and "Where" – what data was transferred and where it went. Endpoint telemetry (Sysmon, EDR, Windows Event Logs) provides the "Who" and "How" – which user, which process, and how it was executed. 

Correlating network and endpoint events bridges the gap between these two domains. It allows a threat hunter to observe a suspicious network connection (e.g., a highly jittered beacon to a Russian IP) and immediately map it back to the exact process executable on the endpoint (e.g., a hidden PowerShell script spawned by Microsoft Word). Without correlation, a network alert is merely an IP address requiring tedious manual investigation; with correlation, it becomes an actionable, context-rich narrative of an attack.

### The Key Link: The 5-Tuple
The fundamental anchor point for correlating network and endpoint data is the network 5-tuple, combined with a precise timestamp:
1. **Source IP Address**
2. **Destination IP Address**
3. **Source Port** (Crucial, as it is dynamically assigned and highly unique)
4. **Destination Port**
5. **Protocol** (TCP/UDP)

If a network sensor records a connection matching a specific 5-tuple at `14:05:01Z`, and an endpoint agent records a process initiating a connection with the exact same 5-tuple at `14:05:01Z`, the hunter can confidently link the network behavior to the host process.

## Architecture of a Correlation Engine

A robust correlation architecture requires high-fidelity sensors on both the network and the endpoints, streaming data into a centralized SIEM capable of complex table joins.

```ascii
+-----------------------------------------------------------------------------------+
|                                 ENTERPRISE ENVIRONMENT                              |
|                                                                                   |
|  +-----------------------------------+   +------------------------------------+   |
|  |           THE ENDPOINT            |   |            THE NETWORK             |   |
|  |                                   |   |                                    |   |
|  |  [Malicious Macro Executes]       |   |                                    |   |
|  |        `powershell.exe`           |   |                                    |   |
|  |               |                   |   |                                    |   |
|  |        (Initiates TCP SYN)        |   |                                    |   |
|  |               |                   |   |                                    |   |
|  |    +-------------------------+    |   |     +-------------------------+    |   |
|  |    | Sysmon (Event ID 3)     |    |   |     |      Zeek Sensor        |    |   |
|  |    | Network Connection Logs |    |   |     |    `conn.log` events    |    |   |
|  |    +-------------------------+    |   |     +-------------------------+    |   |
|  |               |                   |   |                  |                 |   |
|  |      EventID: 3                   |   |       id.orig_h: 10.0.0.50         |   |
|  |      Image: powershell.exe        |   |       id.resp_h: 198.51.100.5      |   |
|  |      SrcIP: 10.0.0.50             |   |       id.orig_p: 49152             |   |
|  |      DstIP: 198.51.100.5          |   |       id.resp_p: 443               |   |
|  |      SrcPort: 49152               |   |       proto: tcp                   |   |
|  |      DstPort: 443                 |   |                                    |   |
|  +-----------------------------------+   +------------------------------------+   |
|                  |                                          |                     |
+------------------|------------------------------------------|---------------------+
                   v                                          v
+-----------------------------------------------------------------------------------+
|                                  SIEM / DATA LAKE                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                        Correlation Engine (Splunk / KQL)                    |  |
|  |   (Matches Sysmon SrcIP+SrcPort+DstIP+DstPort with Zeek id fields on Time)  |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## Threat Hunting Strategies via Correlation

### 1. Identifying Fileless Malware and Living off the Land (LotL)
Attackers frequently use native, legitimate binaries (like `powershell.exe`, `certutil.exe`, `mshta.exe`, `rundll32.exe`) to execute malicious code purely in memory. 
- **The Network View:** The network sensor might just see an HTTPS connection to a generic cloud provider (AWS/Azure). 
- **The Endpoint View:** The endpoint sees `powershell.exe` making a network connection, which is common.
- **The Correlation:** By correlating the two, a hunter can find that an unusually large outbound data transfer (from Zeek) was initiated by `certutil.exe` (from Sysmon), which is highly anomalous since `certutil` should only download small certificate files, not upload 50MB of data.

### 2. Hunting for Unmapped Network Flows
One of the most advanced hunting techniques is searching for network connections observed on the wire that *do not* have a corresponding endpoint event.
If Zeek records a connection from `10.0.0.50` to `8.8.8.8` on port `53`, but Sysmon on `10.0.0.50` has no record of any process making that connection, it indicates severe compromise. The attacker has likely loaded a rootkit, bypassed the Windows filtering platform, or disabled the endpoint logging agent entirely. This discrepancy is a massive red flag.

### 3. DNS Resolution to Process Execution
Adversaries often use Fast Flux DNS or domain generation algorithms (DGA). 
- **Hunting Strategy:** Correlate the `dns.log` from Zeek with Sysmon Event ID 22 (DNSEvent). If Zeek shows a resolution for a known bad DGA domain, correlating the exact timestamp and host with Sysmon Event 22 will instantly reveal the specific executable that requested the malicious resolution.

## Real-World Attack Scenario

### The Scenario: Emotet Delivery via Malicious Document
An accountant opened a malicious Excel file containing an obfuscated macro.

### The Attack Flow
1. **Execution:** The macro executes `cmd.exe`, which spawns an encoded `powershell.exe` command.
2. **Download:** The PowerShell script connects to a compromised WordPress site over HTTP to download the Emotet payload.
3. **Execution 2:** The payload executes and injects itself into `svchost.exe`.
4. **C2:** The injected `svchost.exe` begins beaconing to the Emotet C2 infrastructure over an encrypted custom protocol on port 8080.

### How Correlation Uncovered the Attack Timeline
1. **Network Alert:** A Suricata IDS signature triggered on the initial HTTP download of an executable file claiming to be a PNG image. 
2. **First Correlation:** The threat hunter took the 5-tuple from the Suricata alert (Source Port: 55432, Dest IP: `203.0.113.10`) and queried Sysmon Event ID 3. 
   - *Result:* Sysmon confirmed `powershell.exe` (ProcessID 4502) initiated that exact connection.
3. **Endpoint Pivot:** The hunter pivoted on ProcessID 4502 in Sysmon Event ID 1 (Process Creation). 
   - *Result:* They saw `powershell.exe` was spawned by `EXCEL.EXE`, proving the phishing vector.
4. **Network Pivot:** The hunter then looked at Zeek `conn.log` for any other traffic from that host. They found a persistent, long-duration connection on port 8080.
5. **Second Correlation:** Taking the new 5-tuple (Port 8080), they queried Sysmon Event ID 3 again.
   - *Result:* The connection was initiated by `svchost.exe`. Because `svchost.exe` usually communicates on standard ports for Windows services, its communication over port 8080 to an untrusted IP confirmed process injection.

## Advanced SIEM Queries for Correlation

### Splunk SPL: Joining Zeek and Sysmon
This query joins Zeek connection data with Sysmon network events to identify the process responsible for high-volume outbound traffic.

```spl
index=zeek sourcetype=zeek_conn network.direction=outbound
| stats sum(bytes_out) as total_out by id.orig_h, id.orig_p, id.resp_h, id.resp_p
| rename id.orig_h as src_ip, id.orig_p as src_port, id.resp_h as dest_ip, id.resp_p as dest_port
| join type=inner src_ip, src_port, dest_ip, dest_port [
    search index=windows sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational EventCode=3
    | rename SourceIp as src_ip, SourcePort as src_port, DestinationIp as dest_ip, DestinationPort as dest_port
    | fields src_ip, src_port, dest_ip, dest_port, Image, ProcessId
]
| sort - total_out
| table src_ip, Image, ProcessId, dest_ip, dest_port, total_out
```

### Challenges in Correlation
- **Time Drift:** If the endpoint clock is 5 minutes out of sync with the network sensor, joining on `_time` will fail. Using NTP strictly across the enterprise is mandatory.
- **NAT (Network Address Translation):** If there are firewalls or proxies performing NAT between the endpoint and the network sensor, the source IP and source port will change, breaking the 5-tuple. Sensors must be placed internally, before NAT occurs.
- **Data Volume:** Sysmon Event ID 3 can generate massive amounts of data. Organizations often have to filter out noisy, legitimate processes (like browsers) to manage SIEM costs, which creates blind spots.

## Chaining Opportunities
- **[[08 - Understanding Zeek Architecture and Logs]]**: Zeek provides the network half of the correlation equation.
- **[[11 - Analyzing Network Flow NetFlow IPFIX Data]]**: Flow data provides the timestamps and 5-tuples required to pivot to the endpoint.
- **[[13 - RITA Real Intelligence Threat Analytics for C2]]**: When RITA identifies a mathematical beacon on the network, correlation is the next step to find the malware binary.

## Related Notes
- [[12 - Detecting Suspicious User Agent Strings]]
- [[15 - Dealing with Encrypted Network Traffic in Hunts]]
- [[04 - Threat Hunting Methodologies]]
- [[22 - Advanced Persistent Threats (APTs) Tactics]]
