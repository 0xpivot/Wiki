---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.02 Advanced Splunk Processing Language SPL for Hunts"
---

# Advanced Splunk Processing Language (SPL) for Hunts

## 1. The Anatomy of Advanced SPL

Threat hunting relies on the ability to manipulate data in ways that automated, signature-based SIEM rules do not. 
Standard searches using `index=` and `search` are sufficient for basic lookups, but advanced hunting requires complex aggregation, regular expression parsing, and statistical correlation.
Advanced Splunk Processing Language (SPL) allows the hunter to shape raw telemetry into actionable intelligence.

Mastering advanced SPL means understanding how Splunk pipelines data.
Each command passes its results to the next command via the pipe (`|`) character.
Optimizing this pipeline is the difference between a search that finishes in seconds and one that crashes the indexer.

## 2. Fast Aggregation: `tstats` vs `stats`

### 2.1 The `stats` Command
The `stats` command calculates aggregate statistics over a dataset (e.g., `count`, `sum`, `avg`, `dc`).
While powerful, `stats` requires Splunk to read the raw events off the disk, which is computationally expensive for millions of logs.

### 2.2 The `tstats` Command
`tstats` operates on indexed metadata (TSIDX files) and accelerated Data Models.
Because it does not read raw events, it is exponentially faster. 
Use `tstats` whenever you need simple counts or statistics over massive time ranges.

**Example: Finding high-volume authentication failures**
```splunk
| tstats count from datamodel=Authentication 
  where Authentication.action=failure 
  by Authentication.user 
| sort - count 
| head 10
```

## 3. The Trifecta of Statistics: `stats`, `eventstats`, and `streamstats`

Understanding the difference between these three commands is crucial for advanced correlation.

### 3.1 `stats` (Aggregating and Condensing)
Condenses the dataset. Only the fields explicitly mentioned in the `by` clause and the calculated statistics are passed to the next pipeline stage. All other fields are dropped.

### 3.2 `eventstats` (Inline Aggregation)
Calculates the exact same statistics as `stats`, but **appends** the result as a new field to every original event. No events are dropped, and all original fields are preserved.
*Use case:* Comparing an individual event's value to the global average.

### 3.3 `streamstats` (Rolling Aggregation)
Calculates statistics sequentially as events stream through the pipeline. It calculates a rolling total or difference.
*Use case:* Calculating the time difference between consecutive events (e.g., for beaconing detection).

## 4. ASCII Data Flow: The Stats Commands

```text
+-----------------------------------------------------------------------+
|                 SPL STATS PIPELINE DATA FLOW                          |
|                                                                       |
|  [RAW EVENTS: User A, IP 1; User A, IP 2; User B, IP 3]               |
|                                                                       |
|  | stats count by user                                                |
|  +--> Returns:                                                        |
|       user: A, count: 2                                               |
|       user: B, count: 1                                               |
|       (Original IP field is lost!)                                    |
|                                                                       |
|  | eventstats count by user                                           |
|  +--> Returns:                                                        |
|       user: A, IP: 1, count: 2                                        |
|       user: A, IP: 2, count: 2                                        |
|       user: B, IP: 3, count: 1                                        |
|       (Original fields kept, global aggregate added)                  |
|                                                                       |
|  | streamstats count by user                                          |
|  +--> Returns:                                                        |
|       user: A, IP: 1, count: 1                                        |
|       user: A, IP: 2, count: 2                                        |
|       user: B, IP: 3, count: 1                                        |
|       (Original fields kept, rolling aggregate added sequentially)    |
+-----------------------------------------------------------------------+
```

## 5. Advanced Parsing and Logic

### 5.1 `rex` (Regular Expression Extraction)
When fields are not automatically parsed, `rex` allows hunters to extract them on the fly.
Named capture groups `(?<field_name>...)` are used extensively.

**Example: Extracting a domain from an email address**
```splunk
index=email
| rex field=sender ".*@(?<sender_domain>.*)"
| stats count by sender_domain
```

### 5.2 `eval` (Conditional Logic)
`eval` is used to create or overwrite fields dynamically. 
It supports complex logic using `if()`, `case()`, and mathematical functions.

**Example: Categorizing Ports**
```splunk
| eval port_type=case(
    dest_port==80 OR dest_port==443, "Web",
    dest_port==22, "SSH",
    dest_port==3389, "RDP",
    true(), "Other"
  )
| stats count by port_type
```

## 6. Joins, Appends, and Why You Should Avoid Them

Traditional SQL users often reach for `join` and `append` in Splunk. 
**Avoid this.**
Splunk's `join` command is heavily memory-constrained (by default, it truncates at 50,000 subsearch results) and breaks MapReduce functionality.

### 6.1 The "OR" Paradigm (Alternative to Join)
Instead of joining two searches, combine them with an `OR` and use `stats` to collapse the data based on a common key.

**Bad (Join approach):**
```splunk
index=network src_ip=10.0.0.5 
| join dest_ip [search index=threat_intel | fields dest_ip, threat_actor]
```

**Good (Stats approach):**
```splunk
(index=network src_ip=10.0.0.5) OR (index=threat_intel)
| stats values(action) as action, values(threat_actor) as threat_actor by dest_ip
| where isnotnull(action) AND isnotnull(threat_actor)
```
This method utilizes Splunk's parallel processing capabilities and scales indefinitely.

## 7. Real-World Attack Scenario

### Scenario: Advanced Persistent Threat utilizing DGA (Domain Generation Algorithm)
An APT group is communicating with their C2 infrastructure using randomly generated domains (DGA).
These domains bypass static threat intel feeds because they change every hour.
The hunter needs to identify internal hosts querying high-entropy, anomalous domains.

### Detection via Advanced SPL
The hunter writes an SPL query that calculates the length and entropy of requested domains, filtering out known good domains.

```splunk
index=dns sourcetype=stream:dns record_type=A
| eval domain_len = len(query)
| where domain_len > 15
| rex field=query "(?<tld>\.[a-z]{2,4})$"
| eval query_no_tld = replace(query, tld, "")
| eval consonant_count = corex(query_no_tld, "(?i)[bcdfghjklmnpqrstvwxyz]")
| eval vowel_count = corex(query_no_tld, "(?i)[aeiou]")
| eval ratio = consonant_count / vowel_count
| where ratio > 3.0 OR ratio < 0.3
| stats count dc(query) as unique_domains list(query) as sample_queries by src_ip
| where unique_domains > 5
```

**Breakdown of the Hunt:**
1. Filter for A records.
2. Filter for unusually long domains (`len > 15`).
3. Extract the TLD and strip it.
4. Calculate the ratio of consonants to vowels. High-entropy DGA domains often look like `xjfkdlzqwnp.com`, resulting in a highly skewed consonant ratio.
5. Aggregate by `src_ip`. If an IP requests many unique domains matching this profile, it triggers the alert.
This hunt successfully uncovers the DGA beaconing without relying on any external threat intel.

## 8. Macros and Subsearches for Modularity

For repeated logic, encapsulate the SPL within a **Macro**. 
Macros act like functions. If you frequently define local IP space, create a macro `` `local_ips` `` instead of typing `(src_ip=10.0.0.0/8 OR src_ip=192.168.0.0/16)` every time.

**Subsearches** `[]` run first and pass their output to the outer search. 
They are useful for dynamic filtering but are limited by memory/time constraints.
Example: `index=firewall [search index=threat_intel | return 100 dest_ip]`

## 9. Chaining Opportunities

- The efficient use of `tstats` and avoiding `join` is critical for populating the panels in [[01 - Building a Hunting Dashboard in Splunk]].
- Combining `streamstats` and `eval` mathematical functions lays the groundwork for the mathematical modeling discussed in [[03 - Statistical Outlier Detection in Splunk]].
- The concept of pipeline filtering (`|`) maps directly to Kibana's Query DSL filtering phases in [[05 - Writing Elastic Query DSL and EQL for Detection]].

## 10. Related Notes

- [[01 - Building a Hunting Dashboard in Splunk]]
- [[03 - Statistical Outlier Detection in Splunk]]
- [[04 - Introduction to Elastic Stack ELK for Threat Hunting]]
- [[05 - Writing Elastic Query DSL and EQL for Detection]]
- [[Splunk Regular Expressions Cheat Sheet]]
- [[Threat Hunting with DNS Anomalies]]
