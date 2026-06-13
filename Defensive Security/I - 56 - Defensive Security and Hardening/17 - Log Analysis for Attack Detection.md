---
tags: [defense, hardening, security, vapt, forensics]
difficulty: advanced
module: "56 - Defensive Security and Hardening"
topic: "56.17 Log Analysis for Attack Detection"
---

# 17 - Log Analysis for Attack Detection

Log analysis is the process of reviewing, interpreting, and correlating computer-generated event records (logs) to identify anomalous behavior, security breaches, operational issues, and policy violations. In the context of Defensive Security, logs are the breadcrumbs left behind by attackers. Proper log management and analysis form the backbone of modern Security Operations Centers (SOCs) and Threat Hunting teams.

Without comprehensive logging, an organization is effectively blind to ongoing attacks, and post-incident forensic investigations are severely hindered.

## The Logging Architecture and Pipeline

Modern environments generate massive volumes of log data. Simply writing logs to local files is insufficient for security monitoring. Organizations employ centralized logging architectures, typically culminating in a Security Information and Event Management (SIEM) system.

```text
+-------------------+       +-------------------+       +-------------------+
| Log Sources       |       | Log Forwarders    |       | Aggregation &     |
|                   |       | (Agents)          |       | Parsing           |
| - Windows Servers |       |                   |       |                   |
| - Linux Syslog    +------>+ - Winlogbeat      +------>+ - Logstash        |
| - Firewalls/IDS   |       | - Filebeat        |       | - Fluentd         |
| - Web Servers     |       | - Splunk Univ Fwd |       | - Syslog-ng       |
+-------------------+       +-------------------+       +---------+---------+
                                                                  |
                                                                  v
+-------------------+       +-------------------+       +---------+---------+
| Threat Intel      |       | SIEM / Log Data   |       | Storage / Indexing|
| - MISP            |       | Lake              |       |                   |
| - OTX             +------>+ - Splunk          +<------+ - Elasticsearch   |
| - ThreatFeeds     |       | - Microsoft Sentnl|       | - Splunk Indexer  |
+-------------------+       | - ELK Stack       |       | - AWS OpenSearch  |
                            +---------+---------+       +-------------------+
                                      |
                                      v
                            +---------+---------+
                            | Security Analyst  |
                            | - Dashboards      |
                            | - Alerts / Rules  |
                            | - Threat Hunting  |
                            +-------------------+
```

### Key Stages of the Pipeline:
1.  **Generation:** Devices and applications generate raw logs.
2.  **Collection/Forwarding:** Agents securely transmit logs to a central point (often over TLS to prevent tampering).
3.  **Parsing and Normalization:** Raw text is broken down into structured fields (e.g., `src_ip`, `username`, `action`). This is crucial because a firewall and a web server might log an IP address in completely different formats.
4.  **Enrichment:** Adding context to the logs. For example, mapping an IP address to a geographic location (GeoIP) or checking a hash against a Threat Intelligence feed.
5.  **Storage/Indexing:** Storing the normalized data in a highly searchable database.
6.  **Analysis/Correlation:** Applying rules, machine learning, and human analysis to detect attacks.

## Critical Log Sources and Event IDs

Effective detection relies on collecting the *right* logs, not just *all* logs.

### 1. Windows Event Logs (Security, System, Application)

Windows Event Logs are vital for detecting lateral movement, privilege escalation, and execution. Key Event IDs to monitor include:

*   **Logon/Logoff (Authentication):**
    *   `4624`: Successful Logon.
    *   `4625`: Failed Logon (Brute force detection).
    *   *Crucial Logon Types:* Type 3 (Network - e.g., SMB/PsExec), Type 10 (Remote Interactive - RDP).
*   **Process Execution:**
    *   `4688`: A new process has been created. Command-line logging *must* be enabled via GPO for this to be useful. This reveals exactly what commands an attacker ran.
*   **Account Management:**
    *   `4720`: A user account was created (Backdoor creation).
    *   `4728/4732`: A member was added to a security-enabled global/local group (e.g., Domain Admins).
*   **Object Access:**
    *   `5140`: A network share object was accessed (Detecting lateral movement or data exfiltration).
*   **System Integrity:**
    *   `7045`: A new service was installed in the system (Common persistence mechanism).
    *   `1102`: The audit log was cleared (Classic anti-forensic action).

### 2. Sysmon (System Monitor)

Sysmon is a Microsoft Sysinternals tool that massively enhances Windows logging. It provides high-fidelity telemetry that standard Windows logs often miss.

*   `Event ID 1`: Process creation (includes SHA256 hashes of the executable).
*   `Event ID 3`: Network connection (Tracks process to IP mappings).
*   `Event ID 8`: CreateRemoteThread (Detects process injection/hollowing techniques).
*   `Event ID 11`: FileCreate (Detects malware dropping payload files).
*   `Event ID 12, 13, 14`: Registry modifications (Detects persistence mechanisms like Run keys).

### 3. Web Server Logs (Apache / Nginx / IIS)

Web logs are the primary source for detecting attacks against public-facing infrastructure.

*   **SQL Injection (SQLi):** Look for SQL keywords (`UNION`, `SELECT`, `OR 1=1`, `--`) in URI parameters.
    *   *Example Log snippet:* `"GET /product.php?id=1%27%20OR%20%271%27=%271 HTTP/1.1" 200*
*   **Cross-Site Scripting (XSS):** Look for HTML/JS tags (`<script>`, `alert()`, `onerror=`) in URIs or User-Agent strings.
*   **Directory/Path Traversal:** Look for `../`, `..%2f`, `%2e%2e%2f` attempting to access files outside the web root (e.g., `/etc/passwd`).
    *   *Example Log snippet:* `"GET /images/../../../../etc/passwd HTTP/1.1" 200*
*   **Command Injection:** Look for shell metacharacters (`;`, `|`, `&&`, `$()`) followed by system commands (`whoami`, `id`, `wget`).
*   **Web Shell Interactions:** Detect access to anomalous script files (`cmd.php`, `shell.jsp`) or high-frequency POST requests to a single unusual endpoint.

### 4. Network Logs (Firewalls, IDS/IPS, Proxies)

*   **Firewall Denies:** High volume of denied inbound connections from a single IP indicates a port scan. High volume of denied outbound connections from an internal host indicates compromised host beaconing.
*   **DNS Logs:** Essential for detecting C2 (Command and Control) traffic. Look for DGA (Domain Generation Algorithm) queries (e.g., `xfqkzplx.com`), excessively long subdomains (DNS tunneling), or queries to known malicious domains.
*   **Proxy Logs:** Track user web browsing, useful for spotting initial infection vectors (drive-by downloads) or data exfiltration to cloud storage.

## Attack Detection Strategies

### 1. Signature-Based Detection (Rules)

This relies on matching specific patterns or indicators known to be associated with threats.

*   **Sigma Rules:** Sigma is a generic and open signature format that allows you to describe relevant log events in a straightforward manner. It is highly flexible and can be converted into queries for Splunk, Elastic, QRadar, etc.
    *   *Example Concept:* Write a Sigma rule to trigger if `Event ID 4688` occurs where `Image` ends in `powershell.exe` AND `CommandLine` contains `-enc` or `-EncodedCommand`.

### 2. Behavioral/Anomaly-Based Detection

This involves establishing a baseline of "normal" behavior and alerting on deviations. This is harder to implement but necessary for catching novel (zero-day) attacks.

*   **Time-based Anomalies:** A user who usually logs in between 9 AM and 5 PM suddenly logs in at 3 AM.
*   **Volume Anomalies:** A database server suddenly transfers 50GB of data to an unknown external IP address (Data Exfiltration).
*   **First-Seen Analysis:** Alerting when a specific process (e.g., `psexec.exe`) executes on a host where it has never been seen before.
*   **Beaconing Detection:** Analyzing proxy or firewall logs for connections to an external IP occurring at highly regular intervals (e.g., exactly every 60 seconds with a tiny bit of jitter), indicative of C2 communication.

## Evasion and Challenges

Attackers are acutely aware of log analysis and employ techniques to evade detection:

*   **Living off the Land (LotL):** Using built-in, legitimate administrative tools (PowerShell, WMI, Certutil, Bitsadmin) to conduct attacks. Because these tools are normally used by admins, their activity blends in, making behavioral detection difficult.
*   **Log Tampering/Clearing:** The attacker clears the Event Logs or modifies log files (e.g., removing specific lines from `/var/log/auth.log` in Linux).
    *   *Countermeasure:* Forward logs to a central server immediately. Even if the local logs are cleared, the central SIEM retains the records, and the "Audit Log Cleared" event itself becomes a high-fidelity alert.
*   **Command Line Obfuscation:** Using heavy obfuscation, caret `^` insertion, or environmental variables to hide the true payload from command line logging.
    *   *Countermeasure:* Use Advanced Script Block Logging (Event ID 4104) for PowerShell, which logs the de-obfuscated script content just before execution.

## Chaining Opportunities

*   **Threat Hunting:** Log analysis is the foundation of Threat Hunting. Hunters formulate hypotheses and query log data to prove or disprove them. Connects to `[[19 - Threat Hunting Hypothesis-Driven Approach]]`.
*   **EDR Solutions:** EDR platforms heavily rely on endpoint telemetry (process execution, network connections), which is essentially advanced log analysis at the agent level. Connects to `[[20 - EDR Solutions]]`.
*   **Incident Response:** When an alert fires, log analysis is the primary tool used by IR teams to trace the attacker's steps. Connects to `[[12 - Incident Response Frameworks]]`.

## Related Notes
*   `[[14 - Digital Forensics Fundamentals]]`
*   `[[18 - Honeypots and Honeytokens]]`
*   `[[08 - Network Traffic Analysis]]` (Correlating packet captures with network logs)
*   `[[04 - Linux Privilege Escalation]]` (Understanding what actions to look for in Linux audit logs)
