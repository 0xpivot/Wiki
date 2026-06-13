---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.04 Introduction to Elastic Stack ELK for Threat Hunting"
---

# Introduction to Elastic Stack (ELK) for Threat Hunting

## 1. The Elastic Ecosystem
While Splunk has historically dominated the enterprise SIEM market, the Elastic Stack (formerly ELK: Elasticsearch, Logstash, Kibana) has rapidly become a premier platform for Threat Hunting and Security Analytics.
Its open-source roots, massive scalability, and lightning-fast search capabilities make it an incredibly potent weapon for security teams.

Unlike traditional RDBMS systems, Elastic is built on Apache Lucene, a full-text search engine library.
This architecture means that searching billions of log lines for a specific IP address or process hash is nearly instantaneous.

## 2. Architecture of the Elastic Stack

A successful threat hunter must understand how data traverses the Elastic architecture. If a log is missing, the hunter must know where the pipeline broke.

### 2.1 The Components
-   **Beats / Elastic Agent (The Shippers):** Lightweight data shippers installed on endpoint systems.
    -   *Winlogbeat:* Ships Windows Event Logs (Sysmon, Security).
    -   *Packetbeat:* Sniffs network traffic and extracts metadata (DNS, HTTP).
    -   *Filebeat:* Reads text-based log files (Nginx, Syslog).
-   **Logstash (The Processor):** The data ingestion and processing pipeline. It ingests logs from Beats, parses them (using Grok filters), enriches them (e.g., GeoIP lookups, Threat Intel tagging), and outputs them to Elasticsearch.
-   **Elasticsearch (The Brain):** The distributed JSON-based search and analytics engine. It indexes the data and handles complex queries.
-   **Kibana (The UI):** The visualization layer. It provides Dashboards, Discover (for raw searching), and the Elastic Security app.

### 2.2 Elastic Common Schema (ECS)
Similar to Splunk's CIM, the Elastic Common Schema (ECS) is an open-source specification that defines a common set of fields for data ingestion.
Instead of querying `src_ip` for firewalls and `source.ip` for web logs, ECS mandates `source.ip` across all logs.
Adhering to ECS is mandatory for building effective, platform-agnostic threat hunting queries.

## 3. ASCII Architecture: ELK Data Flow

```text
+-------------------+       +---------------+      +----------------+
|  DATA SOURCES     |       |   INGESTION   |      |    STORAGE     |
|                   |       |               |      |                |
|  [Winlogbeat] ----+-----> |  [Logstash]   | ---> | [Elasticsearch]|
|  [Filebeat]   ----+       | (Parse/Enrich)|      | (Data Nodes)   |
|  [Packetbeat] ----+       +---------------+      +----------------+
|  (Endpoints)      |       (Grok/Filters)                 |
+-------------------+                                      |
                                                           v
                                                  +----------------+
                                                  |  VISUALIZATION |
                                                  |                |
                                                  |    [Kibana]    |
                                                  | (Dashboards &  |
                                                  |  Discover UI)  |
                                                  +----------------+
```

## 4. Understanding Indices, Shards, and Replicas

To hunt efficiently, one must understand how Elasticsearch stores data.
-   **Index:** A collection of documents that share similar characteristics (e.g., `winlogbeat-2026.06.09`).
-   **Sharding:** Elasticsearch divides an index into multiple shards. This allows the index to scale horizontally across multiple servers (nodes). When you query an index, the query runs in parallel across all shards, providing immense speed.
-   **Replica:** A copy of a primary shard for high availability and load balancing.

*Hunting Implication:* When running complex queries (like aggregations) over 90 days of data, you are querying hundreds of shards. Optimizing the time filter is crucial to prevent Kibana timeouts.

## 5. Splunk vs. Elastic: The Paradigm Shift

Transitioning from Splunk to Elastic requires a fundamental mindset shift.

### 5.1 Schema-on-Read vs. Schema-on-Write
-   **Splunk (Schema-on-Read):** Ingests raw data as-is. Parsing and field extraction (using regex) happen dynamically at search time. This is flexible but computationally heavy during a hunt.
-   **Elastic (Schema-on-Write):** Data must be parsed, structured into JSON, and mapped to specific data types (text, keyword, IP) *before* indexing. Searching is incredibly fast because the data is already perfectly structured, but changing field types later requires reindexing.

### 5.2 The `text` vs `keyword` Mapping Trap
This is the most common pitfall for new Elastic hunters.
-   **`text` fields:** Analyzed and broken down into individual words. If a field contains `C:\Windows\System32\cmd.exe`, a `text` search for `cmd` will find it. You cannot perform exact aggregations (like `stats count by process`) on a `text` field.
-   **`keyword` fields:** Stored exactly as-is. Used for exact matching and aggregations. To group by process name, you must use the `process.name.keyword` field.

## 6. Kibana Discover: The Hunter's Workbench

The "Discover" tab in Kibana is where ad-hoc hunting occurs. 
It utilizes the **Kibana Query Language (KQL)**, which provides auto-complete for ECS fields.

**Basic KQL Syntax:**
-   *Free text search:* `mimikatz`
-   *Field specific:* `process.name: "powershell.exe"`
-   *Boolean logic:* `process.name: "cmd.exe" AND user.name: "SYSTEM"`
-   *Wildcards:* `file.path: *\\Temp\\*.exe`
-   *Existence:* `dns.question.name: *` (Finds logs where this field exists)

While KQL is excellent for rapid filtering, it lacks the advanced aggregation pipelines of Splunk SPL. 
For deep statistical correlation, hunters must pivot to Elastic Query DSL or EQL.

## 7. Real-World Attack Scenario

### Scenario: Ransomware Deployment via RDP
An attacker brute-forces an external RDP port, logs in as a local administrator, disables Windows Defender via PowerShell, drops a ransomware payload named `encrypt.exe` into the `AppData` folder, and executes it. 

### Detection via Kibana Discover correlation
The hunter receives an alert for a potential Defender bypass and opens Kibana Discover to investigate.

1.  **Filter by time and host:** The hunter sets the time window to the last 2 hours and adds a filter: `host.name: "WEB-DMZ-01"`.
2.  **Identify Initial Access:** The hunter searches for `event.code: 4624 AND logon.type: 10` (RDP Logon). They find a successful logon from a Russian IP address for the `Administrator` account immediately preceding the alert.
3.  **Trace Execution:** The hunter adds a filter for Sysmon process creation: `event.code: 1` and searches `process.command_line: *DisableRealtimeMonitoring*`. They see `powershell.exe` executing the Defender bypass.
4.  **Identify the Payload:** The hunter queries Filebeat data: `event.category: file AND file.extension: exe AND file.path: *AppData*`. They instantly locate the creation of `encrypt.exe`.
5.  **Network Correlation:** Switching to Packetbeat data, they search `source.ip: 10.0.5.25 AND destination.port: 443`. They observe a massive spike in outbound HTTPS traffic just before encryption began, identifying the C2 data exfiltration channel.

Because Elastic structured all logs into ECS, the hunter was able to filter by `host.name` and seamlessly pivot across Authentication logs, Sysmon process logs, file system logs, and network traffic within seconds in a single Discover view.

## 8. Chaining Opportunities

- The foundational architectural knowledge here is a prerequisite for writing advanced JSON queries and sequences in [[05 - Writing Elastic Query DSL and EQL for Detection]].
- The concepts of baseline normalization (ECS) directly mirror the Splunk CIM requirements discussed in [[01 - Building a Hunting Dashboard in Splunk]].
- Understanding Kibana Discover is the first step before applying statistical anomalies, similar to those built in [[03 - Statistical Outlier Detection in Splunk]].

## 9. Related Notes

- [[01 - Building a Hunting Dashboard in Splunk]]
- [[02 - Advanced Splunk Processing Language SPL for Hunts]]
- [[03 - Statistical Outlier Detection in Splunk]]
- [[05 - Writing Elastic Query DSL and EQL for Detection]]
- [[Elastic Common Schema (ECS) Reference]]
- [[Deploying Winlogbeat for Sysmon]]
