---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.07 Advanced KQL Joins and Time-Series Analysis"
---
# 93.07 Advanced KQL Joins and Time-Series Analysis

## Overview
While fundamental Kusto Query Language (KQL) operators allow analysts to filter and summarize discrete datasets, advanced threat hunting requires cross-correlating telemetry from disparate sources and identifying mathematical deviations over time. This document explores advanced relational operations (joins) and time-series anomaly detection within KQL. Mastering these techniques transforms a SOC analyst from a reactive alert-chaser into a proactive threat hunter capable of unearthing stealthy, low-and-slow adversaries and sophisticated beaconing behaviors.

## ASCII Architecture: Relational Correlation & Time-Series Engine

```text
+-------------------------------------------------------------------------------+
|                      Advanced KQL Analytical Engine                           |
|                                                                               |
|  [ Table A: Identity ]        [ Table B: Network ]      [ Table C: Endpoint]  |
|          |                            |                          |            |
|          v                            v                          v            |
|    +-------------+              +-------------+            +-------------+    |
|    |    Join     |==============|    Join     |============|    Join     |    |
|    | (leftouter) |  Cross-Correlate Indicators of Attack   | (inner/anti)|    |
|    +-------------+              +-------------+            +-------------+    |
|                                        ||                                     |
|                                        \/                                     |
|                        +-----------------------------------+                  |
|                        |   Time-Series Transformation      |                  |
|                        |     (make-series operator)        |                  |
|                        +-----------------------------------+                  |
|                                        ||                                     |
|                                        \/                                     |
|                        +-----------------------------------+                  |
|                        | Machine Learning Anomaly Detection|                  |
|                        | (series_decompose_anomalies)      |                  |
|                        +-----------------------------------+                  |
|                                        ||                                     |
|                                        \/                                     |
|                        +-----------------------------------+                  |
|                        |   High-Fidelity Hunting Alerts    |                  |
|                        +-----------------------------------+                  |
+-------------------------------------------------------------------------------+
```

## Advanced Relational Operations: Joins
KQL provides robust relational capabilities. However, because KQL operates over massive datasets, understanding the mechanics of different `join` flavors is critical for performance and accuracy. Kusto executes joins by broadcasting the smaller (left) table to the nodes hosting the larger (right) table.

### Join Flavors
- **`inner` (default):** Returns only rows where there is a match in both tables.
- **`innerunique`:** Deduplicates the left side before performing an inner join. Useful for reducing explosive cardinalities but can silently drop relevant data if not careful.
- **`leftouter`:** Returns all records from the left table, and matching records from the right table. Non-matching right table columns will be null.
- **`rightouter` / `fullouter`:** Standard SQL equivalents. Rarely used in security telemetry due to massive output sizes.
- **`leftanti` / `rightanti`:** The most powerful join for security. Returns records from the left table that DO NOT have matches in the right table. Perfect for finding "new" or "unseen" behavior.
- **`leftsemi`:** Returns records from the left table that HAVE a match in the right table, without actually appending the columns from the right table.

### Relational Hunting Example: The `leftanti` Join
Finding anomalous administrative behavior by comparing the last 24 hours to a 30-day baseline.
```kusto
let baseline = SecurityEvent
    | where TimeGenerated between(ago(30d) .. ago(1d))
    | where EventID == 4720 // User account created
    | distinct Account;
let recent = SecurityEvent
    | where TimeGenerated >= ago(1d)
    | where EventID == 4720
    | distinct Account, TargetAccount, TimeGenerated;
recent
| join kind=leftanti baseline on Account
// The result is any Account that has created a user in the last 24h, 
// but HAS NEVER created a user in the preceding 30 days.
```

## Time-Series Analysis and Anomaly Detection
Traditional threshold-based alerts (e.g., "Alert if failed logins > 50") are brittle. They generate false positives during high legitimate traffic and false negatives during low-and-slow attacks. Time-series analysis solves this by establishing a mathematical baseline of "normal" and alerting on statistically significant deviations.

### The `make-series` Operator
The `make-series` operator creates specified default values for missing time intervals, generating a continuous array of values. This is fundamentally different from `summarize`, which simply omits intervals with no data. Continuous arrays are required for mathematical decomposition.

```kusto
DeviceNetworkEvents
| where TimeGenerated > ago(7d)
| where ActionType == "NetworkCommunicationEvents"
| make-series BytesSent = sum(InitiatingProcessBytesSent) default=0 
              on TimeGenerated from ago(7d) to now() step 1h 
              by DeviceName
```
*Output:* This generates a table where each `DeviceName` has a single row containing arrays of `TimeGenerated` and `BytesSent` representing hourly buckets over 7 days.

### Machine Learning Algorithms: `series_decompose_anomalies`
Once data is formulated into a series, KQL provides native machine learning functions to detect anomalies. The `series_decompose_anomalies` function uses the Seasonal-Trend decomposition using Loess (STL) algorithm.

It breaks the time-series array down into four components:
1. **Baseline:** The expected value.
2. **Seasonal:** Periodic patterns (e.g., high traffic on weekdays, low on weekends).
3. **Trend:** Gradual directional changes over time.
4. **Residual (Noise):** What is left after subtracting the above. Anomalies are detected on the residual.

```kusto
let min_t = ago(30d);
let max_t = now();
let dt = 1h;
Syslog
| where TimeGenerated between(min_t .. max_t)
| where ProcessName == "sshd"
| make-series SshLogins = count() default=0 on TimeGenerated from min_t to max_t step dt by HostIP
| extend (Anomalies, Score, Baseline) = series_decompose_anomalies(SshLogins, 1.5, -1, 'linefit')
// 1.5 is the anomaly threshold. -1 means detect both positive and negative spikes.
| mv-expand SshLogins, TimeGenerated, Anomalies, Score, Baseline
| where Anomalies == 1 // 1 indicates a positive anomaly
| project TimeGenerated, HostIP, SshLogins, Baseline, Score
```

## Integrating External Threat Intel (`externaldata`)
Advanced hunting often requires correlating internal telemetry with external, dynamically updating indicators of compromise (IOCs). The `externaldata` operator allows KQL to pull data directly from external APIs or storage blobs at query execution time.

```kusto
let TorNodes = externaldata(IPAddress: string)
    [@"https://check.torproject.org/exit-addresses"]
    with (format="txt")
    | where IPAddress matches regex @"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    | project IPAddress;
SigninLogs
| where TimeGenerated > ago(24h)
| join kind=inner TorNodes on $left.IPAddress == $right.IPAddress
| project TimeGenerated, UserPrincipalName, IPAddress, Location
```

## Real-World Attack Scenario

### Scenario: Stealthy C2 Beaconing Detection
A compromised endpoint establishes a covert Command and Control (C2) channel via HTTPS. To avoid detection, the malware beacons out exactly every 60 minutes with a small variance (jitter), sending out small heartbeat packets. Standard threshold alerts ignore this because the volume is extremely low. 

### Hunting with KQL: Detecting Periodicity
To hunt for C2 beaconing, we look for highly regular, periodic network connections that lack typical human variation.

**Phase 1: Calculating Connection Intervals**
We analyze network events, sorting connections by time, and calculating the time delta between each connection for a specific Source to Destination pair.

```kusto
let time_window = 7d;
DeviceNetworkEvents
| where TimeGenerated > ago(time_window)
| where ActionType == "ConnectionSuccess"
| project TimeGenerated, DeviceName, RemoteIP, RemotePort
| sort by DeviceName, RemoteIP, TimeGenerated asc
// Calculate the time difference between the current connection and the previous one
| serialize 
| extend TimeDelta = datetime_diff('minute', TimeGenerated, prev(TimeGenerated))
| extend PrevDevice = prev(DeviceName), PrevIP = prev(RemoteIP)
// Ensure we are only comparing deltas within the same device to the same destination
| where DeviceName == PrevDevice and RemoteIP == PrevIP
| summarize 
    TotalConnections = count(),
    AverageDelta = avg(TimeDelta),
    DeltaVariance = variance(TimeDelta)
    by DeviceName, RemoteIP
// A low variance indicates highly mechanical, periodic behavior (beaconing)
| where TotalConnections > 50 
| where DeltaVariance < 5 // Very little jitter
| sort by DeltaVariance asc
```
*Result:* This query identifies endpoints making highly regular connections to specific external IP addresses. A `DeltaVariance` approaching 0 indicates machine-driven periodicity, a strong indicator of an automated C2 beacon. By chaining relational logic (`serialize`, `prev()`) with statistical variance, the analyst uncovers an attack entirely invisible to standard rules.

## Performance Considerations for Advanced Queries
1. **Serialization Overhead:** Operators like `serialize`, `prev()`, and `next()` force the engine to process data in a strict serial order, disabling parallel processing. Use these only after aggressively filtering down the dataset.
2. **`mv-expand` Cost:** Expanding dynamic arrays (from `make-series` or `parse_json`) creates a new row for every element in the array. This can lead to rapid dataset explosion. Always filter your expanded results immediately.
3. **External Data Throttling:** `externaldata` queries a remote URI. Excessive use in automated, high-frequency rules can lead to IP blocking from the remote source. Consider caching the data in a custom table if queried frequently.

## Chaining Opportunities
- The anomaly detection concepts here are foundational for configuring highly accurate SOAR playbooks to avoid false-positive alert fatigue. See [[09 - SOAR Security Orchestration and Automated Response]].
- `externaldata` integrations are a manual approach to what MISP and Threat Intelligence Platforms do systematically. See [[08 - Integrating MISP with Splunk ELK]].
- For foundational understanding of KQL syntax, review [[06 - Kusto Query Language KQL Basics in Microsoft Sentinel]].

## Related Notes
- [[02 - Endpoint Detection and Response EDR Telemetry]]
- [[04 - Threat Hunting Methodologies]]
- [[05 - MITRE ATT&CK Framework Mapping]]
- [[06 - Kusto Query Language KQL Basics in Microsoft Sentinel]]
