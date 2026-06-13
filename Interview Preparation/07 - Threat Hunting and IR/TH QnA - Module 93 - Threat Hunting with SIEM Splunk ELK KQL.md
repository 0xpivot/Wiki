---
tags: [interview, threat-hunting, ir, qna, scenario]
difficulty: expert
module: "Interview Prep - Threat Hunting and IR"
topic: "QnA - TH Module 93"
---

# Threat Hunting QnA: Threat Hunting with SIEM (Splunk, ELK, KQL)

## Formal Technical Questions

### Q1: Explain the difference between search-time and index-time operations in Splunk. How do you optimize a Splunk SPL query for hunting across 30 days of high-volume endpoint telemetry (e.g., EDR logs)?
**Expert Answer:**
Understanding the Splunk data pipeline is critical for performance, especially when threat hunting across terabytes of data over extended periods.
*   **Index-Time:** Operations that occur when data is ingested. This includes line breaking, timestamp extraction, and default field extraction (host, source, sourcetype). Writing custom index-time field extractions reduces overhead during searching but increases storage and parsing costs.
*   **Search-Time:** Operations that occur when a query is executed. This includes schema-on-the-fly field extraction, alias creation, lookups, and aggregations.
*   **Optimization for 30-Day Hunting:**
    1.  **Use `tstats`:** For massive datasets, standard searches are too slow. `tstats` searches *only* the index metadata and TSIDX (Time Series Index) files, bypassing the raw data retrieval. 
        *   Example: `| tstats count from datamodel=Endpoint.Processes by Processes.process_name, Processes.dest`
    2.  **Filter Early and Often:** Apply the most restrictive filters (Index, Sourcetype, Time Range) at the very beginning of the pipeline before any pipes (`|`). Every pipe passes results to the next command, so filtering 90% of the data out in the base search is critical.
    3.  **Avoid Leading Wildcards:** `index=edr *malware*` is terrible for performance because it prevents the use of bloom filters. Use specific terms or trailing wildcards (`malware*`).
    4.  **Defer Resource-Intensive Commands:** Commands like `rex` (regex extraction), `transaction`, and `join` should be used as late in the SPL pipeline as possible, after the data set has been significantly reduced by `stats` or `search` filters.

### Q2: Compare and contrast Microsoft Sentinel KQL (Kusto Query Language) and Elastic EQL (Event Query Language) for detecting sequence-based attacks (e.g., Lateral Movement).
**Expert Answer:**
Both languages excel at structured data analysis but approach sequence detection differently.
*   **Elastic EQL:** Specifically designed for stateful, sequence-based threat hunting on endpoints. EQL excels at finding temporal relationships. For example, detecting a process creation followed by a file modification by that exact process within 5 minutes.
    *   *Syntax advantage:* The `sequence` operator is native and highly readable. 
    *   *Example:* 
        ```eql
        sequence by host.name with maxspan=5m
          [process where event.action == "exec" and process.name == "cmd.exe"]
          [network where event.action == "connection_attempted" and destination.port == 445]
        ```
*   **Sentinel KQL:** A data analytics language optimized for extremely fast aggregations, joins, and time-series analysis across diverse cloud and endpoint logs.
    *   *Sequence handling:* KQL requires more complex logic to track stateful sequences compared to EQL. Hunters often use `join`, `arg_max`, or windowing functions (e.g., `serialize` and `prev()`). 
    *   *Advanced capability:* KQL's strength lies in its ability to seamlessly join EDR logs (DeviceProcessEvents) with Azure AD logs (SigninLogs) and Office 365 logs in a single highly performant query. It also supports inline machine learning (e.g., `series_decompose_anomalies()`) for beaconing detection, which EQL does not natively do inline.

## Scenario-Based Questions

### Q3: You are hunting for C2 (Command and Control) beaconing behavior using network proxies and firewall logs in an ELK stack. Walk me through the mathematical/statistical approach you would take using Elastic tools and query logic.
**Expert Answer:**
Beaconing is characterized by repetitive, systematic outbound connections, often with consistent timing (jitter applied) and payload sizes.
*   **Phase 1: Feature Extraction:** I need to calculate the time differences (deltas) between sequential connections from the same source IP to the same destination IP/Domain. In Kibana, I would leverage Elasticsearch aggregations or transform jobs.
*   **Phase 2: Mathematical Analysis (The Query Logic):**
    *   Group data by `source.ip`, `destination.ip`, and `destination.domain`.
    *   Calculate the time interval between each request.
    *   Compute the **Variance** and **Standard Deviation** of these intervals. A low standard deviation means the timing is highly rigid (machine-generated, no human randomness).
    *   Calculate the average byte sizes (`network.bytes_out`, `network.bytes_in`). Highly consistent byte sizes (low variance) across thousands of requests indicate automated heartbeats.
*   **Phase 3: Anomaly Detection (Machine Learning):** Instead of manually building massive Lucene or KQL queries, I would deploy an Elastic Machine Learning job using the `High_Variance` or `Rare` functions. Specifically, a time-series model looking for anomalous patterns in `event.duration` combined with `count` to isolate low-frequency, high-consistency C2 communications that evade static threshold alerts.

### Q4: An attacker is using BloodHound to map the Active Directory environment. You have Windows Event Forwarding (WEF) sending logs to Microsoft Sentinel. Write a conceptual KQL query or explain the logic to detect this.
**Expert Answer:**
BloodHound relies heavily on SharpHound for ingestion, which generates massive amounts of LDAP queries, SAMR requests, and SMB sessions to enumerate group memberships, sessions, and ACLs across the domain.
*   **Hunting Logic:** We are looking for a single user/host generating anomalous enumeration activity across the entire domain in a short burst.
*   **Key Event IDs:** 4624 (Logon), 5145 (Detailed File Share - looking for IPC$ and SAMR/LSARPC named pipes), 4662 (Directory Service Access - SAM-Domain enumeration).
*   **Conceptual KQL Query:**
    ```kusto
    let timeframe = 1h;
    let threshold = 100; // Threshold of unique hosts accessed
    SecurityEvent
    | where TimeGenerated > ago(timeframe)
    | where EventID == 5145
    | where ShareName endswith "IPC$"
    | where RelativeTargetName in~ ("samr", "lsarpc")
    | summarize UniqueTargets = dcount(TargetServerName), TargetList = make_set(TargetServerName) 
      by Account, SourceComputerId, bin(TimeGenerated, 5m)
    | where UniqueTargets >= threshold
    | project TimeGenerated, Account, SourceComputerId, UniqueTargets, TargetList
    | sort by UniqueTargets desc
    ```
*   **Explanation:** This query looks for IPC$ connections targeting the `samr` or `lsarpc` named pipes. It aggregates (`summarize`) the distinct count (`dcount`) of target servers by the source account and computer within 5-minute windows (`bin`). If a single machine queries over 100 distinct servers' SAMR interfaces in 5 minutes, it is a glaring indicator of SharpHound enumeration.

## Deep-Dive Defensive Questions

### Q5: In Splunk, how can you identify "Living off the Land" (LotL) execution, specifically when utilities like PowerShell or Certutil are renamed by the attacker to evade basic static detections?
**Expert Answer:**
Relying purely on `process_name == "powershell.exe"` is a rudimentary and easily bypassed detection.
*   **OriginalFileName / PeVersionInfo:** EDR tools (and Sysmon Event ID 1) extract the metadata embedded in the PE header. In Splunk, I will query against the `OriginalFileName` field rather than the executed `Image` name.
    `index=sysmon EventCode=1 OriginalFileName="PowerShell.EXE" NOT Image="*\\powershell.exe"`
*   **Hash Banning/Hunting:** Querying by SHA256 or IMPHASH. Standard Windows binaries have known hashes. We can build a lookup table of common administrative tool hashes and hunt for executions where the hash matches, but the name does not.
*   **Command-Line Entropy and Arguments:** We look at the `CommandLine` field. Even if `powershell.exe` is renamed to `update.exe`, the arguments often remain characteristic: `-nop -w hidden -c "IEX(New-Object Net.WebClient)..."`.
    We can write SPL to look for heavy use of Base64 encoding or anomalous entropy in the command line string using custom Python scripts integrated via the Splunk Machine Learning Toolkit (MLTK), or using complex `rex` commands to find anomalous character repetition.

## Custom ASCII Diagram: SIEM Threat Hunting Data Pipeline

```text
[ Endpoint Telemetry ]   [ Network Sensors ]   [ Cloud Control Plane ]
     (Sysmon/EDR)            (Zeek/Suricata)       (AWS CloudTrail)
          |                         |                     |
          v                         v                     v
+-------------------------------------------------------------------+
|                     DATA INGESTION & PARSING                      |
| (Logstash / Splunk Heavy Forwarder / Azure Monitor Agent)         |
|  1. Line Breaking   2. Timestamp Ext   3. Metadata Tagging        |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               NORMALIZATION & ENRICHMENT (OCSF/ECS)               |
| -> Maps 'sourceIpAddress', 'src_ip', 'Source_IP' to `src.ip`      |
| -> Enriches IPs with Threat Intel (MISP, VirusTotal Lookups)      |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                    HOT / WARM STORAGE (TSIDX)                     |
|            (Indexed for blazingly fast `tstats` / KQL)            |
+-------------------------------------------------------------------+
                                  |
       +--------------------------+--------------------------+
       |                          |                          |
+-------------+            +-------------+            +-------------+
| STATISTICAL |            | BEHAVIORAL  |            | INDICATOR   |
|   HUNTING   |            |  SEQUENCES  |            |  MATCHING   |
| (Time Series|            | (EQL / Joins|            | (IOC Sweeps |
|  Anomalies) |            | Lateral Mov)|            |  Dashboards)|
+-------------+            +-------------+            +-------------+
```

## Real-World Attack Scenario
**Ransomware Precursor: The WMI Pivot**
During a routine proactive threat hunt, an analyst utilizing Microsoft Sentinel was investigating a baseline anomaly. A KQL Time Series forecast flagged a 400% spike in Windows Event ID 4688 (Process Creation) across 50 workstations simultaneously.
Instead of looking at the alert generically, the hunter used a `join` query to correlate the 4688 events with Network flow logs. The hunt revealed that a compromised tier-2 admin credential was systematically executing WMI commands (`WmiPrvSE.exe`) remotely via DCOM (TCP 135) to spawn hidden `cmd.exe` processes. The `cmd.exe` processes were dropping a batch script that disabled Windows Defender and prepared the host for encryption. The ability to use KQL's `summarize dcount(TargetComputer)` combined with `arg_max` for the exact command-line parameters allowed the team to sever the DCOM connections globally and isolate the compromised admin account before the ransomware payload could be executed.

## Chaining Opportunities
*   SIEM hunts often pivot directly into **Endpoint Forensics (Module 92)**; once an anomalous process identifier (PID) is found via KQL/SPL, the responder will pull a memory dump for deep Volatility analysis to find the injected code.
*   Correlating **Cloud Logs (Module 91)** with Endpoint logs in the SIEM is the only way to track a complete Kill Chain (e.g., Attacker phishes a user on-prem, moves to Entra ID, and accesses AWS via federated SAML).
*   Integrating SOAR logic: Automatically triggering an isolation playbook when the SIEM identifies high-confidence lateral movement chains.

## Related Notes
*   [[22 - Splunk tstats and Data Model Optimization]]
*   [[48 - Kusto Query Language Advanced Analytics]]
*   [[71 - Network Beaconing Mathematical Detection]]
*   [[84 - EQL Sequence Building for Lateral Movement]]
*   [[95 - Threat Intelligence MISP Integration with SIEM]]
