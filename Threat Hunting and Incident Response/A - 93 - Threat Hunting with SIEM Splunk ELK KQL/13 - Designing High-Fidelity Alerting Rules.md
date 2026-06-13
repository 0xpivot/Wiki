---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.13 Designing High-Fidelity Alerting Rules"
---

# 93.13 Designing High-Fidelity Alerting Rules

## Table of Contents
1. [Introduction to High-Fidelity Alerting](#introduction-to-high-fidelity-alerting)
2. [The Danger of Alert Fatigue](#the-danger-of-alert-fatigue)
3. [Anatomy of a High-Fidelity Rule](#anatomy-of-a-high-fidelity-rule)
4. [Alerting Architecture and Data Flow](#alerting-architecture-and-data-flow)
5. [Sigma Rules: The Universal SIEM Standard](#sigma-rules-the-universal-siem-standard)
6. [Implementing High-Fidelity Logic in SIEMs](#implementing-high-fidelity-logic-in-siems)
    - [Splunk (SPL) - Correlation and Thresholds](#splunk-spl---correlation-and-thresholds)
    - [Elastic (EQL) - Temporal Sequence Detection](#elastic-eql---temporal-sequence-detection)
    - [Azure Sentinel (KQL) - Behavior Baseline Deviation](#azure-sentinel-kql---behavior-baseline-deviation)
7. [Strategies to Reduce False Positives](#strategies-to-reduce-false-positives)
8. [Real-World Attack Scenario](#real-world-attack-scenario)
9. [Chaining Opportunities](#chaining-opportunities)
10. [Related Notes](#related-notes)

## 1. Introduction to High-Fidelity Alerting
Security Operations Centers (SOCs) are constantly bombarded with telemetry. Designing alerting rules is easy; designing *good* alerting rules is exceptionally difficult. High-fidelity alerting focuses on precision (accuracy) over recall (catching absolutely everything). 

The core philosophy is: **An alert should only trigger if there is a high probability of malicious activity or a severe misconfiguration requiring immediate human intervention.**

## 2. The Danger of Alert Fatigue
A common failure mode in enterprise security is "Alert Fatigue"—where analysts are overwhelmed by thousands of low-context, false-positive alerts. 
Consequences include:
- **Burnout:** Analysts spending hours clearing benign alerts (e.g., "Failed login attempt" for a service account typing the wrong password).
- **The "Boy Who Cried Wolf" Syndrome:** Analysts begin auto-closing alerts without investigation, eventually ignoring a critical alert that represents a true breach.
- **Wasted Compute:** Inefficient rules running every 5 minutes consume massive SIEM CPU resources.

## 3. Anatomy of a High-Fidelity Rule
A high-fidelity rule is rarely based on a single, isolated event (e.g., "Alert on `cmd.exe` execution"). Instead, it relies on complex combinations of state tracking, thresholds, and environmental context.

Key components of a robust rule:
1. **Primary Indicator:** The core suspicious event (e.g., a process execution, an unusual network connection).
2. **Contextual Enrichment:** Adding secondary data (e.g., Is the executing user a Domain Admin? Is the destination IP a known Tor exit node?).
3. **Correlation (Temporal Sequence):** Linking multiple disparate events over time (e.g., 50 failed logins from IP 'X', followed immediately by 1 successful login from IP 'X').
4. **Exclusions / Allowlisting:** Rigorously filtering out known, documented benign activity (e.g., SCCM executing scripts, nightly backup jobs).

## 4. Alerting Architecture and Data Flow

```text
+-------------------+      +-------------------+      +-------------------+
|  Raw Event Stream |      |  Enrichment Data  |      | Historical State  |
| (Sysmon, Windows, |      | (AD, Threat Intel,|      | (Previous Alerts, |
|  Network Flows)   |      |  Asset Inventory) |      |  Known Baselines) |
+-------------------+      +-------------------+      +-------------------+
          \                          |                          /
           \                         v                         /
            \              +-------------------+              /
             +------------>| Correlation Engine|             /
                           | (Rule Logic)      |<-----------+
                           +-------------------+
                                     |
                                     v
                           +-------------------+
                           | Alert Filtering & |
                           | Allowlisting      |
                           +-------------------+
                                     |
                                     v
                           +-------------------+
                           | High-Fidelity     |
                           | Alert Generation  |
                           | & SOAR Dispatch   |
                           +-------------------+
```

## 5. Sigma Rules: The Universal SIEM Standard
Sigma is an open, generic signature format that allows analysts to describe relevant log events in a straightforward manner. It is the "YARA for log data." The massive advantage of Sigma is its portability; a single YAML rule can be compiled into Splunk SPL, Elastic KQL, Azure Sentinel, and QRadar formats.

**Example Sigma Rule: High-Fidelity Web Shell Detection via Whoami**
```yaml
title: Suspicious Execution of Whoami by Web Server Process
id: 12345678-1234-1234-1234-123456789012
status: stable
description: Detects the execution of whoami.exe spawned directly by IIS, Apache, or Nginx. This is a massive indicator of a web shell or Remote Code Execution (RCE) vulnerability being exploited.
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        ParentImage|endswith:
            - '\w3wp.exe'
            - '\httpd.exe'
            - '\nginx.exe'
            - '\tomcat.exe'
        Image|endswith:
            - '\whoami.exe'
            - '\net.exe'
            - '\cmd.exe'
    condition: selection
falsepositives:
    - Highly unlikely. Legitimate web applications do not spawn system enumeration binaries.
level: critical
tags:
    - attack.execution
    - attack.t1059
```

## 6. Implementing High-Fidelity Logic in SIEMs

### Splunk (SPL) - Correlation and Thresholds
Detecting a brute force attack is a low-fidelity alert (it happens thousands of times a day on the internet). Detecting a *successful* login after a brute force attack is a critical, high-fidelity alert.

```spl
// SPL logic to detect a successful breach following a brute force attempt within a 1-hour window
index=windows sourcetype=WinEventLog:Security (EventCode=4625 OR EventCode=4624)
| transaction TargetUserName maxspan=1h
| search EventCode=4625 EventCode=4624
| stats count(eval(EventCode=4625)) as failed_count, count(eval(EventCode=4624)) as success_count by TargetUserName, src_ip
| where failed_count > 20 AND success_count > 0
| eval Alert_Description="Successful authentication post-brute-force. Immediate account lock required."
```

### Elastic (EQL) - Temporal Sequence Detection
Elasticsearch Query Language (EQL) is brilliantly designed for event-based time series correlation, making it perfect for tracking attacker sequences.

```eql
// EQL logic to detect an attacker dropping a file and immediately executing it
sequence by host.name, user.name with maxspan=1m
  [file where event.action == "creation" and file.extension in ("exe", "dll", "ps1", "bat")]
  [process where event.action == "start" and process.executable == file.path]
```

### Azure Sentinel (KQL) - Behavior Baseline Deviation
Sometimes high-fidelity means alerting when someone does something they have *never* done before, especially involving high-privilege actions.

```kql
// Detect a user granting mailbox permissions, but ONLY if they haven't done it in the last 30 days
let historic_grants = CloudAppEvents
| where ActionType == "Add-MailboxPermission"
| where TimeGenerated between (ago(30d) .. ago(1d))
| summarize count() by AccountObjectId;

CloudAppEvents
| where TimeGenerated > ago(1d)
| where ActionType == "Add-MailboxPermission"
// Filter out anyone who regularly does this (e.g., IT Support)
| where AccountObjectId !in (historic_grants)
| project TimeGenerated, AccountObjectId, TargetMailbox, ActionType
```

## 7. Strategies to Reduce False Positives
1. **Precise Command Line Filtering:** Instead of ignoring all `powershell.exe` activity from a specific parent process, filter based on exact command-line arguments (e.g., block `powershell -enc` but allow `powershell -file C:\scripts\backup.ps1`).
2. **Contextual Thresholds:** A threshold of 50 failed logins might be entirely normal for a public-facing API service account, but 5 failed logins is highly anomalous for the CFO's personal account. Thresholds should be dynamic based on entity risk.
3. **Risk Scoring (The "Tripwire" Method):** Instead of alerting on single events, assign a risk score to entities (users/hosts). For example: Running `whoami` = 10 points. Running `ping` = 5 points. Accessing a rare share = 20 points. Only generate an alert when the host's cumulative score exceeds 50 within a 2-hour window.

## 8. Real-World Attack Scenario

### Scenario: Detecting Golden Ticket Usage
**Context:** Attackers using a forged Kerberos Ticket Granting Ticket (Golden Ticket) often bypass standard authentication mechanisms, allowing them persistent, undetectable domain admin access. Detecting this requires highly nuanced rules.

**The Flawed Approach:**
An analyst creates a rule to alert on any Event ID 4624 (Logon) with Logon Type 3 (Network Logon).
*Result:* Millions of false positives. It alerts every time a user maps a network drive or accesses a printer.

**The High-Fidelity Approach:**
A Golden Ticket often has a lifetime of 10 years, whereas the default Active Directory domain policy issues tickets valid for 10 hours. Furthermore, attackers often use legacy RC4 encryption to forge the ticket if they don't know the AES keys, whereas modern AD defaults to AES.

**Rule Logic:**
1. Monitor Windows Event ID 4769 (Kerberos Service Ticket Requested).
2. Filter for Authentication Package = "Kerberos".
3. Check the Ticket Encryption Type. (Is it RC4 `0x17` in an environment that should be strictly AES?).
4. **The Correlation Kicker:** Correlate with Event ID 4768 (TGT Requested). If there is a Service Ticket requested, but absolutely no preceding TGT request from that user/IP in the last 10 hours, it means the ticket was forged offline and injected into memory.

**Splunk SPL Example:**
```spl
index=windows sourcetype=WinEventLog:Security EventCode=4769
// Look for weak RC4 encryption
| search Ticket_Encryption_Type="0x17" OR Ticket_Encryption_Type="RC4-HMAC"
// Left join to see if a TGT was actually requested recently
| join type=left Account_Name [ search index=windows sourcetype=WinEventLog:Security EventCode=4768 earliest=-10h ]
// If EventCode_4768 is null, the TGT was never requested from the DC!
| where isnull(EventCode_4768)
| table _time, Account_Name, Client_Address, Service_Name, Ticket_Encryption_Type
| eval Alert_Description="CRITICAL: Golden Ticket Usage Detected. Forged Service Ticket without TGT request."
```
This rule targets the specific cryptographic and temporal anomaly of Golden Tickets, drastically reducing noise while effectively catching advanced persistent threats.

## 9. Chaining Opportunities
- Alerts generated by these high-fidelity rules can trigger automated SOAR playbooks, or prompt a deep dive using the techniques detailed in `[[11 - Using Jupyter Notebooks for Threat Hunting]]`.
- To achieve absolute maximum fidelity (Zero False Positives), integrate these rules with the traps discussed in `[[14 - Creating Honeytokens and Deception Decoys]]`.

## 10. Advanced Sigma Rule Considerations
When deploying Sigma rules at scale, consider the following robust pipeline:
1. **Sigma Rule Creation:** Analysts write the rule in standard YAML based on Threat Intel or an active incident investigation.
2. **CI/CD Integration:** The YAML file is committed to a centralized Git repository (e.g., GitLab or GitHub).
3. **Automated Testing:** A CI pipeline automatically runs `sigmac` (the Sigma compiler) to ensure the rule is syntactically valid and does not contain gross logic errors.
4. **Backend Compilation:** The rule is dynamically translated into the specific backend language of your environment (e.g., Splunk SPL, Elastic EQL, Log Analytics KQL).
5. **Continuous Deployment:** The rule is pushed via API directly to the SIEM production environment.
By treating rules as Detection-as-Code (DaC), the SOC ensures high-fidelity rules are strictly version-controlled, meticulously peer-reviewed, and easily rolled back if they unexpectedly generate false positives in production.

## 11. Performance Tuning High-Fidelity Rules
Even a high-fidelity rule can be computationally expensive if poorly written.
- **Filter Early:** Always apply the most restrictive filters first (e.g., filter by `EventCode=4688` before doing a wildcard search on `CommandLine`).
- **Avoid Leading Wildcards:** Searching for `*password*` forces the SIEM to scan every character of every string. Use precise matching whenever possible.
- **Leverage Summary Indexes:** For long-term correlation (e.g., looking at 30 days of data), pre-calculate the data into a summary index rather than running a raw search across billions of events.

## 12. Related Notes
- `[[11 - Using Jupyter Notebooks for Threat Hunting]]`
- `[[12 - Machine Learning for Log Anomaly Detection]]`
- `[[14 - Creating Honeytokens and Deception Decoys]]`
- `[[15 - Case Study Tracking APT29 across a SIEM]]`
