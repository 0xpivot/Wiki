---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.06 Kusto Query Language KQL Basics in Microsoft Sentinel"
---
# 93.06 Kusto Query Language (KQL) Basics in Microsoft Sentinel

## Overview
Kusto Query Language (KQL) is a powerful, highly optimized language designed to explore and analyze vast amounts of data. Originally developed for Azure Data Explorer (ADX), KQL is now the foundational querying engine powering Microsoft Sentinel, Azure Monitor, Microsoft Defender for Endpoint, and advanced hunting across the Microsoft 365 Defender ecosystem. This document provides an exhaustive, advanced deep-dive into KQL basics, tailored specifically for threat hunting, SOC investigations, and incident response within Microsoft Sentinel.

Unlike SQL, which is structured relationally, KQL is a read-only request mechanism designed for petabyte-scale datasets and high-performance, real-time querying. The syntax employs a highly readable, composable pipeline approach, where the output of one operator becomes the input of the next. Understanding KQL is no longer optional for modern SOC analysts—it is the prerequisite for effective threat hunting in cloud-native environments.

## The Paradigm Shift: From SQL and SPL to KQL
For analysts transitioning from Splunk's SPL (Search Processing Language) or relational SQL, adapting to KQL requires understanding the pipeline operator (`|`). 

In SQL, queries are structured rigidly: `SELECT -> FROM -> WHERE`. This structure forces the database engine to parse the entire query to understand execution order. In KQL, the data flow is sequential and logical, reading top-to-bottom, left-to-right: `Table -> Filter -> Aggregate/Project -> Sort -> Limit`.

This pipeline structure ensures that datasets are conceptually and practically reduced as early as possible in the execution path, drastically optimizing performance against massive telemetry datasets.

## ASCII Architecture: KQL Execution Pipeline in Sentinel

```text
+--------------------------------------------------------------------------+
|                       Microsoft Azure Ecosystem                          |
|                                                                          |
|  +---------------------+     +--------------------------+     +-------+  |
|  |  Raw Telemetry Data |     |  Log Analytics Workspace |     | TI &  |  |
|  | (Endpoints, Cloud,  | ===>|  (Kusto Engine Cluster)  | <===| Rules |  |
|  |  Network, Identity) |     |  Data Sharding & Indexing|     +-------+  |
|  +---------------------+     +--------------------------+                |
|                                         ||                               |
|                                         \/                               |
|                        +-----------------------------------+             |
|                        |  KQL Pipeline Execution Flow      |             |
|                        | --------------------------------- |             |
|                        | 1. Table Selection (e.g. Syslog)  |             |
|                        | 2. Time Filter (TimeGenerated)    |             |
|                        | 3. Logical Filter (where EventID) |             |
|                        | 4. Projection/Extension (extend)  |             |
|                        | 5. Aggregation (summarize)        |             |
|                        +-----------------------------------+             |
|                                         ||                               |
|                                         \/                               |
|                        +-----------------------------------+             |
|                        | Output Rendering / Investigation  |             |
|                        | (Hunting Dashboards, Alerts,      |             |
|                        |  Sentinel Workbooks)              |             |
|                        +-----------------------------------+             |
+--------------------------------------------------------------------------+
```

## Core Foundational Mechanics

### 1. The `search` Operator
The `search` operator is often the entry point for novice analysts who know what they are looking for but not where to find it. It performs a multi-table, full-text search. While highly convenient, it is extremely resource-intensive and should generally be avoided in production hunting rules.
```kusto
// Searching across all tables for an IP address
search "198.51.100.45"
| summarize count() by $table
```
*Best Practice:* Transition from `search` to specific table queries as quickly as possible.

### 2. Table Selection and Time Filtering
Every efficient KQL query begins by defining the target table and immediately applying a time bound. Kusto partitions data on the backend using the `TimeGenerated` column. Filtering by time *first* prevents full table scans.
```kusto
SecurityEvent
| where TimeGenerated >= ago(7d)
| where EventID == 4624 // Successful Logon
| where LogonType in (2, 10) // Interactive and Remote Interactive
```

### 3. The `let` Statement
The `let` statement is arguably one of the most powerful features in KQL. It allows analysts to define variables, constants, and even entire sub-queries that can be reused throughout the main query pipeline. This promotes highly readable, modular code.

```kusto
let timeframe = 14d;
let suspicious_domains = dynamic(["malicious.com", "evildomain.net", "c2-server.org"]);
let TargetHosts = DeviceNetworkEvents
    | where TimeGenerated > ago(timeframe)
    | where RemoteUrl in (suspicious_domains)
    | distinct DeviceId;
DeviceProcessEvents
| where TimeGenerated > ago(timeframe)
| where DeviceId in (TargetHosts)
| where FileName =~ "cmd.exe" or FileName =~ "powershell.exe"
```
In this example, the `let` statement creates an array of domains, calculates a dynamic list of compromised hosts, and passes that sub-query output into a process execution search.

## Data Manipulation and Shaping

### Projection (`project`, `project-away`, `project-reorder`)
The `project` operator selects the columns to include, rename, or drop, and can create new computed columns inline. `project-away` removes columns, which is useful when dealing with massively wide tables where you want to keep everything *except* a few noisy fields.
```kusto
SigninLogs
| where TimeGenerated >= ago(1d)
| project-rename LoginTime = TimeGenerated, TargetUser = UserPrincipalName
| project LoginTime, TargetUser, IPAddress, LocationDetails
| project-away LocationDetails // Demonstrative removal
```

### Extension (`extend`)
The `extend` operator is used to create calculated columns and append them to the result set. It evaluates expressions for each row. It is heavily utilized to unpack JSON structures dynamically or perform mathematical/string operations.
```kusto
DeviceProcessEvents
| extend CommandLength = strlen(ProcessCommandLine)
| extend IsObfuscated = iff(CommandLength > 1000, true, false)
| where IsObfuscated == true
```

## Aggregation and Statistical Summarization

### The `summarize` Operator
The `summarize` operator produces a table that aggregates the content of the input table. This is the equivalent of `GROUP BY` in SQL or `stats` in Splunk.

```kusto
SecurityEvent
| where TimeGenerated >= ago(30d)
| where EventID == 4625 // Failed Logon
| summarize FailedCount = count(), 
            FirstAttempt = min(TimeGenerated), 
            LastAttempt = max(TimeGenerated) 
            by Account, IpAddress
| where FailedCount > 50
| sort by FailedCount desc
```
Advanced aggregation functions include:
- `count()`: Standard row count.
- `dcount()`: Distinct count (uses HyperLogLog algorithm for speed, approximate by default).
- `make_set()`: Creates a JSON array of unique values encountered in a column.
- `make_list()`: Creates a JSON array of all values (including duplicates).
- `arg_max()` / `arg_min()`: Returns the row that maximizes or minimizes an expression.

## Advanced String Operators and Searching
KQL offers highly granular string matching operators, which are vital for hunting specific Indicators of Compromise (IOCs). Understanding the performance implications of these operators is critical for advanced analysts.

- `==`: Strict, exact string equality. (Fastest)
- `=~`: Case-insensitive exact string equality.
- `contains`: Substring match. Case-insensitive. (Slow, bypasses index)
- `has`: Whole word token match. Case-insensitive. **Crucially, `has` is exponentially faster than `contains` because it leverages Kusto's term index.**
- `matches regex`: Regular expression matching. Powerful, but highly resource-intensive.

```kusto
// BAD: Slow substring search
DeviceNetworkEvents | where RemoteUrl contains "pastebin"

// GOOD: Fast token index search
DeviceNetworkEvents | where RemoteUrl has "pastebin.com"
```

## Parsing Dynamic Data Types (JSON/XML)
Modern logging, especially in Azure and AWS integrations within Sentinel, often dumps highly structured JSON data into a single, massive string column (e.g., `AdditionalFields` or `Properties`). The `parse_json()` function and `parse` operator are essential for extracting this telemetry.

```kusto
AzureActivity
| where TimeGenerated > ago(1d)
| where OperationName == "Create or Update Virtual Machine"
| extend PropertiesJson = parse_json(Properties)
| extend VmName = tostring(PropertiesJson.vmName)
| extend OSDisk = tostring(PropertiesJson.storageProfile.osDisk.name)
| project TimeGenerated, Caller, VmName, OSDisk
```
Alternatively, the `parse` operator allows for regex-like extraction without the computational overhead of regex:
```kusto
Syslog
| where ProcessName == "sshd"
| parse SyslogMessage with * "Failed password for " user " from " ip " port " port " ssh2" *
| summarize count() by user, ip
```

## Real-World Attack Scenario

### Scenario: Initial Access via Password Spraying leading to PowerShell Obfuscation
A threat actor conducts a low-and-slow password spraying attack against an organization's Azure Active Directory. Once a weak password is successfully guessed, the actor logs into an Azure Virtual Machine via RDP and executes a base64 encoded PowerShell payload to establish persistence and download a Command and Control (C2) beacon.

### Hunting with KQL

**Phase 1: Detecting the Password Spray**
The analyst begins by querying `SigninLogs` to identify any external IP addresses exhibiting a high ratio of failed logins across multiple unique internal accounts, followed by a successful login.

```kusto
let time_window = 24h;
let FailedLogins = SigninLogs
    | where TimeGenerated >= ago(time_window)
    | where ResultType != "0" // 0 indicates success in Azure AD logs
    | summarize FailedAccounts = dcount(UserPrincipalName), TotalFailures = count() by IPAddress
    | where FailedAccounts > 5; // The IP attempted to login to more than 5 distinct accounts
FailedLogins
| join kind=inner (
    SigninLogs
    | where TimeGenerated >= ago(time_window)
    | where ResultType == "0" // Successful login
    | summarize CompromisedAccounts = make_set(UserPrincipalName), SuccessfulLogonTime = min(TimeGenerated) by IPAddress
) on IPAddress
| project IPAddress, FailedAccounts, TotalFailures, CompromisedAccounts, SuccessfulLogonTime
| sort by TotalFailures desc
```
*Result:* This query identifies the attacker's IP, quantifies the scope of the spray (`FailedAccounts`), and precisely isolates the breached identity (`CompromisedAccounts`).

**Phase 2: Tracing Post-Compromise Activity on the Endpoint**
Assuming the query above identified `jdoe@victim.com` as compromised, the analyst now pivots to endpoint telemetry (`DeviceProcessEvents`) to monitor what `jdoe` did immediately following the login.

```kusto
let breached_user = "jdoe";
DeviceProcessEvents
| where TimeGenerated > ago(24h)
| where AccountName contains breached_user
| where FileName in~ ("powershell.exe", "pwsh.exe", "cmd.exe")
// Looking for common obfuscation flags
| extend IsBase64 = iff(ProcessCommandLine matches regex @"(?i)(-[eE][nNcCoOdDeE]*\s+[a-zA-Z0-9+/=]{20,})", true, false)
| extend IsHidden = iff(ProcessCommandLine has_any ("-w hidden", "-windowstyle hidden"), true, false)
| where IsBase64 or IsHidden
| project TimeGenerated, DeviceName, AccountName, ActionType, FileName, ProcessCommandLine
```
*Result:* This seamlessly transitions the hunt from cloud identity infrastructure to host-based execution tracking, uncovering the specific encoded payload the attacker attempted to run.

## Performance Tuning Tips
1. **Time Filters First:** As reiterated, Kusto heavily optimizes by time. Apply `TimeGenerated` filters immediately after the table declaration.
2. **Filter Before `join`:** Drastically reduce the dataset size of both tables before applying heavy relational operators like `join` or `summarize`.
3. **Use `has` Over `contains`:** Whenever possible, rely on Kusto's term indexing rather than brute-force substring matching.
4. **Avoid `search *`:** Never use open-ended searches in production analytics rules.
5. **Pre-Calculate with `let`:** If you are filtering by a complex list of IOCs, calculate that list once in a `let` statement rather than repeatedly computing it within the main query body.

## Chaining Opportunities
- KQL basics seamlessly transition into advanced relational analysis and statistical anomaly detection. See [[07 - Advanced KQL Joins and Time-Series Analysis]].
- Understanding parsing (`parse_json`, `parse`) in KQL maps directly to data normalization strategies discussed in [[10 - Normalizing Data Sources Common Information Model CIM]].
- Hunting workflows and logic developed in KQL can be directly integrated into automated playbooks via [[09 - SOAR Security Orchestration and Automated Response]].

## Related Notes
- [[02 - Endpoint Detection and Response EDR Telemetry]]
- [[04 - Threat Hunting Methodologies]]
- [[05 - MITRE ATT&CK Framework Mapping]]
- [[07 - Advanced KQL Joins and Time-Series Analysis]]
- [[08 - Integrating MISP with Splunk ELK]]
