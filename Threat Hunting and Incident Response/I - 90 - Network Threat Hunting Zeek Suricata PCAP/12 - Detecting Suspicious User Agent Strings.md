---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.12 Detecting Suspicious User Agent Strings"
---

# Detecting Suspicious User Agent Strings

## Introduction to User Agent Analysis
The HTTP `User-Agent` (UA) string is a header field transmitted by web browsers and other HTTP clients with every request. It serves to identify the client application, its operating system, and the underlying rendering engine to the web server. While originally designed for content negotiation (e.g., serving a mobile-friendly site to a smartphone), the User-Agent string has become a critical artifact for network threat hunting and incident response. 

Because attackers heavily rely on HTTP/HTTPS for command and control (C2) infrastructure, data exfiltration, and automated reconnaissance, their tools must generate HTTP requests. Many automated attack tools, vulnerability scanners, and malware frameworks either use hardcoded, highly distinctive User-Agent strings, or attempt to spoof legitimate browsers but fail to do so accurately. Identifying these anomalies within HTTP logs is a powerful method for detecting malicious activity that bypasses traditional signature-based network defenses.

### Anatomy of a Legitimate User-Agent String
A standard modern browser User-Agent string is complex and highly structured. According to RFC 7231, it contains multiple product tokens and comments.

Example of a standard Google Chrome UA:
`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36`

- **Mozilla/5.0:** Historical artifact included for compatibility reasons.
- **(Windows NT 10.0; Win64; x64):** System information detailing the OS and architecture.
- **AppleWebKit/537.36 (KHTML, like Gecko):** The rendering engine.
- **Chrome/114.0.0.0 Safari/537.36:** The browser version and compatibility markers.

Attackers often struggle to perfectly replicate this complexity, leading to subtle mismatches that hunters can exploit.

## Architecture of UA Logging and Inspection

To effectively hunt for suspicious User-Agents, an organization needs deep visibility into HTTP headers. 

```ascii
+-----------------------------------------------------------------------------------+
|                                 ENTERPRISE BOUNDARY                                 |
|                                                                                   |
|  +-------------------+      +-------------------+      +-------------------+      |
|  | Compromised Host  |      | Malicious Script  |      | External Attacker |      |
|  |  (Internal C2)    |      |  (Data Exfil)     |      |  (Vuln Scanner)   |      |
|  +--------+----------+      +---------+---------+      +----------+--------+      |
|           |                           |                           |               |
|      HTTP GET /config            HTTP POST /upload           HTTP GET /admin      |
|      UA: python-requests         UA: curl/7.68.0             UA: sqlmap/1.5       |
|           |                           |                           |               |
+-----------|---------------------------|---------------------------|---------------+
            v                           v                           v
+-----------------------------------------------------------------------------------+
|                             NETWORK SECURITY STACK                                  |
|                                                                                   |
|  +-------------------+      +-------------------+      +-------------------+      |
|  |    Web Proxy      |      |   Zeek Sensor     |      |    WAF / ADC      |      |
|  |  (Squid/BlueCoat) |      | (HTTP Analyzer)   |      |   (F5 / Imperva)  |      |
|  +--------+----------+      +---------+---------+      +----------+--------+      |
|           |                           |                           |               |
|     Proxy Access Logs          Zeek `http.log`                 WAF Logs           |
+-----------|---------------------------|---------------------------|---------------+
            v                           v                           v
+-----------------------------------------------------------------------------------+
|                                 SIEM / LOG LAKE                                     |
|  +-----------------------------------------------------------------------------+  |
|  |                Elasticsearch / Splunk / Microsoft Sentinel                  |  |
|  |    (Aggregates, normalizes, and indexes the `http.user_agent` field)        |  |
|  +------------------------------------+----------------------------------------+  |
+---------------------------------------|-------------------------------------------+
                                        | Queries & Dashboards
                                        v
+-----------------------------------------------------------------------------------+
|                                THREAT HUNTING                                       |
|  +-----------------------------------------------------------------------------+  |
|  | - Frequency Analysis (Rarest UAs)                                           |  |
|  | - Regex Matching (Known Bad, Default Tools)                                 |  |
|  | - Contextual Correlation (UA vs. JA3/TLS Fingerprint)                       |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## Threat Hunting Strategies for User Agents

### 1. Identifying Known Malicious and Tooling UAs
Many attackers fail to change the default User-Agent strings embedded within their tools. This provides a high-fidelity indicator of compromise.
- **Vulnerability Scanners:** Tools like Nmap, Nikto, Nessus, and SQLmap often announce themselves loudly.
  - Example: `sqlmap/1.5.8#stable (https://sqlmap.org)`
  - Example: `Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)`
- **Scripting Languages and Libraries:** Malware written in Python, PowerShell, or Go often uses the default library UA if the attacker neglects to spoof it.
  - Example: `python-requests/2.25.1`
  - Example: `Go-http-client/1.1`
  - Example: `Java/1.8.0_202`
  - Example: `WindowsPowerShell/v1.0` (Highly suspicious if seen making outbound internet requests to uncategorized domains).
- **Default C2 Frameworks:** If unmodified, frameworks like Metasploit, Empire, and Cobalt Strike have default UA profiles.

### 2. Frequency Analysis (Long Tail Hunting)
Instead of looking for specific strings, hunters should look for the rarest strings in the environment. In an enterprise of 10,000 employees, you will see millions of Chrome and Edge User-Agents. If you group by the `user_agent` field and sort ascending, the UAs seen only 1 to 5 times are highly suspicious.

**Splunk SPL Example for Long Tail Analysis:**
```spl
index=proxy OR index=zeek sourcetype=zeek_http
| stats count by http_user_agent, src_ip
| sort count asc
| head 50
```

### 3. Mismatch and Anomaly Analysis
Sophisticated attackers will spoof their User-Agent to look like legitimate traffic, often copying a standard Chrome or Firefox UA. However, they frequently make mistakes.
- **Typographical Errors:** Attackers typing out strings might misspell words (e.g., `Mozila/5.0` instead of `Mozilla/5.0`).
- **Outdated Versions:** A beacon configured three years ago might spoof `Chrome/70.0`, while the entire enterprise has been updated to `Chrome/114.0`. Finding radically outdated browser versions in the logs can highlight legacy C2 channels.
- **OS/Environment Mismatches:** If an endpoint is known to be a Linux server, but the proxy logs show it communicating externally with a User-Agent claiming to be `Windows NT 10.0`, this is a massive anomaly indicating potential spoofing by a backdoor.

### 4. Advanced Correlation: UA vs. TLS Fingerprinting (JA3)
When traffic is encrypted, hunters can correlate the HTTP User-Agent (if decrypted via TLS inspection) with the TLS JA3 fingerprint (collected passively by Zeek/Suricata). 
A legitimate Chrome browser will have a specific JA3 hash based on its TLS cipher suites. If an attacker uses a Python script that spoofs the Chrome User-Agent, the JA3 hash generated by the Python OpenSSL library will not match the known JA3 hash of Chrome. This mismatch is a highly reliable indicator of malicious spoofing.

## Real-World Attack Scenario

### The Scenario: Customized Python Backdoor
An organization's security team noticed unusual outbound traffic from a segmented internal application server (`10.20.30.40`). The server was only supposed to communicate with internal database clusters.

### The Attack Flow
1. **Exploitation:** The attacker exploited an unpatched remote code execution (RCE) vulnerability in a web application hosted on the server.
2. **Persistence:** The attacker deployed a custom, memory-resident Python script designed to act as a reverse shell and C2 beacon.
3. **C2 Communication:** To evade network detection, the attacker configured the Python script to reach out to an external IP (`203.0.113.88`) over HTTP port 80.
4. **Evasion Attempt:** The attacker attempted to blend in by hardcoding a User-Agent string into the Python script. They used: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.212 Safari/537.36`.

### How UA Analysis Detected the Activity
1. **Contextual Anomaly Detection:** The threat hunter was reviewing proxy logs for the server segment. They noticed outbound HTTP traffic, which was immediately suspicious given the server's role.
2. **User-Agent Mismatch:** The hunter examined the `http_user_agent` field. At first glance, it looked like a legitimate Chrome browser. However, two critical anomalies stood out:
   - **OS Mismatch:** The source IP `10.20.30.40` belonged to a Linux CentOS server, but the User-Agent claimed to be a Windows 10 machine (`Windows NT 10.0`).
   - **Structural Missing Elements:** The attacker failed to include the `AppleWebKit` string, which is standard in Chromium-based browsers. The crafted UA was `... Chrome/90.0... Safari/537.36`. A real Chrome UA contains `AppleWebKit/537.36 (KHTML, like Gecko)`.
3. **Investigation & Remediation:** The hunter pivoted on the destination IP (`203.0.113.88`) and found continuous, 10-minute interval beaconing activity. Correlation with endpoint EDR logs revealed the hidden Python process running the backdoor. The server was isolated, and the C2 IP was blocked at the perimeter.

## Zeek `http.log` for User Agent Hunting
Zeek is an incredibly powerful tool for this type of analysis. In the `http.log`, Zeek automatically extracts the `user_agent` field.
A hunter can use simple `zcat` and `awk` commands to find the rarest User-Agents directly from the sensor:

```bash
# Extract the top 20 rarest User Agents from a Zeek http.log
zcat http.log.gz | awk -F'\t' '{print $12}' | sort | uniq -c | sort -n | head -n 20
```

## Chaining Opportunities
- **[[15 - Dealing with Encrypted Network Traffic in Hunts]]**: User-Agent analysis requires plaintext HTTP or TLS inspection. Correlating UA strings with JA3 hashes discussed in this module is the ultimate technique for detecting spoofing.
- **[[08 - Understanding Zeek Architecture and Logs]]**: Zeek's `http.log` is the primary source for network-based User-Agent analysis. Understanding how Zeek parses this data is crucial.
- **[[13 - RITA Real Intelligence Threat Analytics for C2]]**: RITA can be configured to enrich its beaconing analysis by factoring in the HTTP User-Agent strings associated with the identified beacons.

## Related Notes
- [[11 - Analyzing Network Flow NetFlow IPFIX Data]]
- [[14 - Correlating Network and Endpoint Events]]
- [[20 - Web Application Threat Hunting]]
- [[04 - Threat Hunting Methodologies]]
