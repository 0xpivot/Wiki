---
tags: [interview, threat-hunting, ir, qna, scenario]
difficulty: expert
module: "Interview Prep - Threat Hunting and IR"
topic: "QnA - TH Module 90"
---

# Network Threat Hunting (Zeek, Suricata, PCAP) QnA

## Introduction
This document contains expert-level interview questions and deep-dive technical answers focused on Network Threat Hunting. It covers network telemetry generation using Zeek (formerly Bro), signature-based detection with Suricata, PCAP analysis, beaconing detection, and cryptographic fingerprinting (JA3/JARM).

## Custom ASCII Diagram: Zeek Log Correlation & C2 Beaconing Hunt

```text
 [ Compromised Endpoint ] ----(TLS Encrypted C2 Traffic)----> [ Malicious C2 Server ]
           |
           | (Network Tap / SPAN Port)
           v
  +-------------------------------------------------------------------------+
  |                             ZEEK ENGINE                                 |
  |  Analyzes raw packets and generates structured, protocol-specific logs  |
  +-------------------------------------------------------------------------+
           |                      |                     |
           v                      v                     v
    [ conn.log ]             [ dns.log ]            [ ssl.log ]
    - id.orig_h              - query                - server_name (SNI)
    - id.resp_h              - qtype                - ja3 / ja3s
    - duration               - rcode                - issuer
    - orig_bytes             - answers              - subject
           |                      |                     |
           +----------+-----------+----------+----------+
                      |                      |
                      v                      v
  +--------------------------------+ +--------------------------------------+
  | 1. BEACONING ANALYSIS (RITA)   | | 2. DGA & DNS TUNNELING HUNT          |
  | - High connection count        | | - High entropy in DNS queries        |
  | - Tight time dispersion        | | - Excessive TXT record queries       |
  | - Small data payload variance  | | - NXDOMAIN spikes                    |
  +--------------------------------+ +--------------------------------------+
                      |                      |
                      v                      v
            [ Confirmed C2 Infection & Lateral Movement Vector ]
```

---

## Formal Technical Questions

### Q1: Explain JA3, JA3S, and JARM fingerprinting. How do they work, and how can threat hunters use them when payload inspection is impossible due to TLS 1.3 encryption?
**Expert Answer:**
With modern encryption (TLS 1.3), traditional payload inspection (DPI) is often impossible without complex SSL decryption proxies. Threat hunters rely on metadata fingerprinting.
*   **JA3 (Client Fingerprint):** Hashes the TLS Client Hello packet. It looks at the SSL Version, Accepted Ciphers, List of Extensions, Elliptic Curves, and Elliptic Curve Formats. Since different applications (Chrome, Python `requests`, Cobalt Strike, Metasploit) use different underlying TLS libraries, their Client Hello structure differs.
*   **JA3S (Server Fingerprint):** Hashes the TLS Server Hello packet (Server SSL Version, Accepted Cipher, Extensions).
*   **JARM (Active Server Fingerprint):** An active scanning tool. It sends 10 customized TLS Client Hello packets to a target server and hashes the server's specific responses.
*   **Hunting Application:** 
    *   *Correlation:* A JA3 hash alone is prone to false positives (e.g., standard Windows Schannel might match a malware loader using Schannel). However, hunting for a specific JA3 *combined* with a specific JA3S creates an extremely high-fidelity indicator of a specific malware communicating with a specific C2 infrastructure.
    *   *JARM:* Hunters can scan the internet (via Shodan) for the JARM hash of a known Cobalt Strike team server profile to identify attacker infrastructure before an attack occurs.

### Q2: Compare and contrast the architectural philosophies and use-cases of Zeek and Suricata. Why would a mature SOC run both?
**Expert Answer:**
While both sit on a network tap/SPAN port, they serve entirely distinct primary purposes.
*   **Suricata (Signature/Rules-Based IDS/IPS):**
    *   *Philosophy:* "Is this packet bad based on what I already know?"
    *   *Architecture:* Uses multi-threaded signature matching against payloads and headers. Fast, heavily reliant on rulesets (e.g., Emerging Threats).
    *   *Output:* Alerts (e.g., `[1:2018358:2] ET TROJAN Possible Cobalt Strike Beacon...`).
*   **Zeek (Protocol Analyzer & Metadata Generator):**
    *   *Philosophy:* "I don't know if this is bad, but I will record exactly what happened in structured logs."
    *   *Architecture:* Reconstructs TCP sessions, parses protocols (HTTP, DNS, SMB, Kerberos) at the application layer, and generates highly structured TSV or JSON logs. It has a Turing-complete scripting language for complex logic.
    *   *Output:* Transaction logs (`conn.log`, `http.log`, `pe.log`).
*   **Why run both:** Suricata catches the *known* threats immediately (Intelligence-Driven). Zeek provides the rich historical metadata required to hunt for *unknown* threats (Data-Driven, like long-tail analysis or beaconing detection) and is essential for post-incident forensic investigation where Suricata alerts lack context.

### Q3: How do you identify Domain Generation Algorithms (DGA) strictly using Network Telemetry (e.g., Zeek `dns.log`)?
**Expert Answer:**
DGAs are used by malware to dynamically generate thousands of pseudo-random domain names for C2 rendezvous, evading static blocklists.
1.  **Lexical Analysis (Entropy):** Calculate the Shannon entropy of the `query` field in `dns.log`. Legitimate domains (e.g., `google.com`) have low entropy. DGA domains (e.g., `xkqzjywvntm.info`) have high entropy due to random character distribution.
2.  **Length and Consonant Ratio:** DGA domains often have unusual lengths and a high ratio of consonants to vowels.
3.  **NXDOMAIN Spikes:** A DGA malware will query hundreds of domains, but the attacker only registers one or two. Therefore, the vast majority of queries will return an `NXDOMAIN` (RCODE 3). A hunt query would look for a single internal IP generating a massive spike in NXDOMAIN responses over a short window.
4.  **Zeek-Cut Example:**
    ```bash
    cat dns.log | zeek-cut id.orig_h query rcode | awk '$3 == "3"' | sort | uniq -c | sort -nr | head -n 10
    ```
    This identifies the top hosts generating NXDOMAINs, a strong DGA indicator.

---

## Scenario-Based Questions

### Q4: You notice a sudden, sustained spike in DNS TXT record queries originating from a critical database server to an external, unknown DNS server. What is happening, and how do you investigate this using PCAP and Zeek?
**Expert Answer:**
This scenario is highly indicative of **DNS Tunneling** for either Command and Control (C2) or Data Exfiltration. DNS is often poorly monitored and allowed outbound from internal segments. TXT records are abused because they can hold large amounts of base64/hex encoded data (up to 255 characters per string).
1.  **Hypothesis Formulation:** The DB server has been compromised and is exfiltrating database dumps via DNS queries to attacker-controlled authoritative name servers.
2.  **Zeek Investigation (`dns.log`):**
    *   Filter `dns.log` for `qtype_name == "TXT"`.
    *   Analyze the `query` field. In a tunnel, the subdomain portion contains the encoded payload (e.g., `<base64_data>.attacker-domain.com`).
    *   Look at the total `Z` (length) of the queries. Tunneling produces exceptionally long DNS query names.
3.  **PCAP Investigation (Wireshark/tshark):**
    *   Filter: `dns.qry.type == 16` (TXT).
    *   Extract the payloads from the subdomains and the TXT responses.
    *   Attempt to decode the subdomains (Base64, Base32, Hex). If the decoded data contains database headers or recognized text, exfiltration is confirmed.
4.  **Remediation:** Block outbound DNS traffic (Port 53) from the DB server. Force all internal assets to resolve through internal DNS resolvers, which can be strictly monitored and sinkholed.

### Q5: Your SOC relies heavily on a Threat Intel Feed for malicious IPs. During a hunt, you use RITA (Real Intelligence Threat Analytics) against Zeek `conn.log` and identify a host with a perfect beaconing score (1.0) to a Microsoft Azure IP address. There are no IDS alerts. Walk me through your analysis.
**Expert Answer:**
This describes **Domain Fronting** or **Cloud Provider abuse** (Living off the Cloud). The attacker is hosting their C2 redirector on Azure, hiding behind a legitimate, highly trusted IP address that bypasses IP-based threat intel and Suricata signature blocks.
1.  **Analyze Beaconing Metrics:** A perfect beacon score indicates exact timing (e.g., exactly 60.0 seconds between connections) with low jitter, and consistent payload sizes. This is programmatic behavior, not human web browsing.
2.  **Pivot to `ssl.log` and `http.log`:**
    *   Since it's Azure, I need to know *which* service is being accessed. I check the `ssl.log` for the `server_name` (Server Name Indication - SNI).
    *   If the SNI is a generic endpoint (e.g., `ajax.microsoft.com`) but the Host header in the encrypted payload routes to an attacker's tenant, we have Domain Fronting.
    *   Look at the TLS certificate `subject` and `issuer`. Does it match the expected Microsoft certs, or is it a Let's Encrypt cert hosted on an Azure VM?
3.  **Endpoint Pivot:** The network confirms the beacon, but I must identify the process. I take the connection timestamps and destination IP, and pivot to the EDR (Sysmon Event ID 3) for that specific host to find the originating Process ID and binary (e.g., `svchost.exe` running a malicious thread).

---

## Deep-Dive Defensive Questions

### Q6: Lateral movement via SMB (Port 445) and RPC (Port 135) is notoriously difficult to hunt because it blends in with normal Windows domain traffic. How can you leverage Zeek to reliably hunt for malicious lateral movement like PsExec or WMI abuse?
**Expert Answer:**
Hunting lateral movement requires shifting from volume-based metrics to behavioral sequence metrics.
*   **Hunting PsExec (SMB):**
    *   Zeek's `smb_files.log` and `smb_mapping.log` are critical.
    *   Legitimate admin usage of PsExec is rare on standard user workstations. Hunt for SMB connections targeting the `IPC$` and `ADMIN$` hidden shares.
    *   Specifically, look for the transfer of a binary file (often pseudo-randomly named like `PSEXESVC.exe`) to the `ADMIN$` share, followed immediately by RPC endpoint mapper traffic (Port 135) to start the service.
*   **Hunting WMI Abuse:**
    *   WMI uses DCOM (RPC). Zeek's `dce_rpc.log` tracks this.
    *   Hunt for the specific UUID of the WMI interface (`IWbemServices`: `9556dc99-828c-11cf-a37e-00aa003240c7`) originating from non-administrative subnets targeting other workstations (peer-to-peer lateral movement), which is highly anomalous in a standard hub-and-spoke IT architecture.
*   **The "One-to-Many" Ratio:** Map out the ratio of source IP to unique destination IPs over port 445. A standard workstation connects to a few domain controllers and file servers. An infected host scanning or moving laterally will have an inverted ratio, connecting to hundreds of peer workstations on port 445.

### Q7: If you only had a raw PCAP of an incident and no endpoint logs, what is your methodology for triaging a suspected malware infection, step-by-step?
**Expert Answer:**
Analyzing raw PCAP without endpoint context requires a top-down protocol approach, moving from the network edge inward.
1.  **Protocol Hierarchy & Endpoints:** Use Wireshark's `Statistics -> Protocol Hierarchy` and `Endpoints` tools. I look for unusual protocols or a massive volume of traffic to a single external IP.
2.  **DNS Analysis:** Filter `dns`. Extract all resolved domains. I look for DGAs, misspelled known domains (Typosquatting), or dynamic DNS providers (DuckDNS, No-IP) commonly used by attackers.
3.  **HTTP/Cleartext Extraction:** Filter `http.request`. Extract HTTP objects (`File -> Export Objects -> HTTP`). I look for dropped executables, PowerShell scripts, or malicious macro documents. I analyze User-Agents for anomalies (e.g., `User-Agent: curl/7.68.0` or standard Python agents coming from a Windows user subnet).
4.  **TLS/SSL Analysis:** Filter `tls.handshake.type == 1` (Client Hello). I extract the SNIs and check them against Threat Intel. I extract JA3 hashes and compare them against malware databases.
5.  **Follow TCP Streams:** For suspicious cleartext traffic (like FTP, Telnet, or unencrypted C2), I use `Follow TCP Stream` to read the exact commands executed by the attacker and the server's responses.

---

## Real-World Attack Scenario

### SolarWinds SUNBURST DGA and C2 Traffic
**Background:** The SolarWinds supply chain attack deployed the SUNBURST backdoor. The backdoor was incredibly stealthy, remaining dormant for weeks, checking domain states, and using a complex DGA for its initial C2 resolution.
**The Attack (Network Perspective):**
1.  **Initial Beacon (DGA):** SUNBURST generated a subdomain containing the victim's encoded active directory domain name. It queried this against `avsvmcloud.com` (e.g., `0123456789.appsync-api.us-west-2.avsvmcloud.com`).
2.  **CNAME Response:** The attacker's authoritative DNS server received the query, decoded the victim's name, and if it was a high-value target, responded with a CNAME record pointing to a secondary C2 server.
3.  **C2 Traffic:** The backdoor then initiated HTTPS traffic to the secondary C2 server using an API-like URI structure mimicking legitimate SolarWinds Orion Improvement Program (OIP) traffic, blending perfectly into the noise.

**The Hunt:**
*   **Retrospective Hunt:** Once the `avsvmcloud.com` IoC was released, hunters pivoted to Zeek `dns.log`.
*   **Execution:**
    *   Query: `cat dns.log | grep avsvmcloud.com`.
    *   Hunters identified the specific affected SolarWinds servers. More importantly, by analyzing the `answers` field in the Zeek logs, they could see *which* infected servers received the malicious CNAME response (indicating the attacker actively escalated privileges on that specific host) versus those that received an A record or NXDOMAIN (indicating they were infected but ignored by the attacker).
*   **Pivot to HTTPS:** Hunters then took the IPs from the CNAME resolution and queried `conn.log` and `ssl.log` to determine the volume of bytes transferred (`orig_bytes` vs `resp_bytes`), identifying if major data exfiltration occurred over the secondary C2 channel.

---

## Chaining Opportunities
*   To correlate network beaconing with the specific process spawning the connections (e.g., Sysmon Event ID 3), refer to [[TH QnA - Module 89 - Endpoint Threat Hunting Windows Sysmon EDR]].
*   For the core hypothesis generation concepts that drive network hunts (like assuming breach and building data-driven DGA hypotheses), return to [[TH QnA - Module 88 - Threat Hunting Foundations and Methodologies]].
*   For deeper analysis of network exfiltration protocols, proceed to [[Data Exfiltration and Insider Threat Detection]].

## Related Notes
*   [[Zeek Scripting and Log Parsing]]
*   [[Suricata Signature Development]]
*   [[RITA and Active Beacon Detection]]
*   [[TLS Fingerprinting with JA3 and JARM]]
