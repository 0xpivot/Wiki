---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.11 Creating a Threat Hunting Runbook"
---

# 11 - Creating a Threat Hunting Runbook

## Introduction to Threat Hunting Runbooks

A Threat Hunting Runbook is a meticulously designed, formalized document or living repository that guides a threat hunter through a specific hypothesis-driven hunt. Unlike detection engineering, which relies on automated alerts, threat hunting is proactive and human-driven. However, human-driven does not mean unstructured. Without a runbook, a hunt can quickly devolve into aimless log scrolling, leading to missed artifacts, wasted resources, and non-repeatable processes.

A high-quality runbook standardizes the methodology, ensures that all necessary data sources are checked, defines the analytical techniques to be employed, and dictates the post-hunt procedures (such as transitioning successful findings into automated detections). By institutionalizing the hunt process, teams can scale their operations, onboard new analysts efficiently, and measure the effectiveness of their hunting program over time.

## The Threat Hunting Lifecycle

Before diving into the runbook itself, it is crucial to understand the lifecycle of a threat hunt, as the runbook is designed to facilitate this exact process.

```text
+-------------------------------------------------------------------------+
|                    The Threat Hunting Lifecycle                         |
+-------------------------------------------------------------------------+
|                                                                         |
|  +------------------+       +------------------+       +-------------+  |
|  | 1. Hypothesis    | ----> | 2. Data          | ----> | 3. Analysis |  |
|  |    Generation    |       |    Collection    |       |    & Pivot  |  |
|  +------------------+       +------------------+       +-------------+  |
|           ^                                                   |         |
|           |                                                   v         |
|  +------------------+       +------------------+       +-------------+  |
|  | 6. Detection     | <---- | 5. Documentation | <---- | 4. Response |  |
|  |    Engineering   |       |    & Reporting   |       |    (If Hit) |  |
|  +------------------+       +------------------+       +-------------+  |
|                                                                         |
+-------------------------------------------------------------------------+
```

A runbook structures steps 1 through 3, provides guidelines for step 4, and mandates the outputs for steps 5 and 6.

## Core Components of a Comprehensive Runbook

An elite runbook is structured to leave no ambiguity. It should contain the following critical sections:

### 1. Metadata and Tracking
Every runbook must have a unique identifier, author attribution, target environment scope, and a version history. This ensures the hunt is tracking against the current state of the organization's infrastructure.
- **Runbook ID:** HUNT-WIN-004
- **Target OS:** Windows Server 2019/2022
- **MITRE ATT&CK Mapping:** T1047 (Windows Management Instrumentation)

### 2. The Hypothesis
The hypothesis is the foundation of the hunt. It must be testable, specific, and grounded in intelligence or environmental awareness.
* **Poor Hypothesis:** "Adversaries might be in our network."
* **Elite Hypothesis:** "Adversaries are utilizing WMI (`wmic.exe` or `Get-WmiObject`) for lateral movement and remote execution, bypassing traditional EDR monitoring by living off the land, which will manifest as anomalous child processes spawning from `WmiPrvSE.exe`."

### 3. Data Requirements
A hunt cannot execute without data. The runbook must explicitly state what data is needed, where it lives, and the required retention period.
- **Log Source:** Windows Event Logs (Security)
- **Event IDs:** 4688 (Process Creation with Command Line), 4104 (PowerShell Script Block Logging)
- **Telemetry Type:** EDR Process Trees
- **Index/Platform:** Splunk index=`wineventlog`

### 4. Query Design and Analytical Techniques
This section provides the exact queries, logic, and techniques to pull the data. It should include base queries and filtering techniques to remove known noise (False Positives).

**Example KQL (Kusto Query Language) for Microsoft Sentinel:**
```kusto
// Base query looking for WMI Provider Host spawning suspicious child processes
let SuspiciousBinaries = dynamic(["cmd.exe", "powershell.exe", "certutil.exe", "rundll32.exe", "regsvr32.exe"]);
DeviceProcessEvents
| where InitiatingProcessFileName =~ "WmiPrvSE.exe"
| where FileName in~ (SuspiciousBinaries)
| project TimeGenerated, DeviceName, InitiatingProcessCommandLine, FileName, ProcessCommandLine, AccountName
| order by TimeGenerated desc
```

### 5. Baselining and Tuning
This section instructs the hunter on how to differentiate between normal administrative behavior and anomalous activity. For example, SCCM (System Center Configuration Manager) heavily utilizes WMI. The runbook must specify how to filter out known SCCM service accounts without creating blind spots.

### 6. Investigation and Pivoting Steps
If the query returns suspicious results, what does the hunter do next? The runbook should define pivot points:
- Check network connections originating from the suspicious child process.
- Review file modifications (Event ID 11) by the child process.
- Identify the source IP that initiated the WMI connection by correlating with Event ID 4624 (Logon Type 3).

### 7. Handover and Escalation
Defines the threshold at which a "hunt" becomes an "incident." If malicious activity is confirmed, the runbook must detail how to transition to the Incident Response team (e.g., locking the compromised asset, creating a high-severity ticket, preserving memory).

## Real-World Attack Scenario

**Scenario: The "Phantom" WMI Lateral Movement**

**Background:** A financial institution received Threat Intel indicating that a new ransomware affiliate was bypassing standard EDR detections by utilizing purely fileless WMI lateral movement. The threat hunting team activated `HUNT-WIN-004: WMI Process Anomalies`.

**The Hunt Execution:**
1. The hunter deployed the runbook's KQL queries across the last 30 days of telemetry.
2. The initial query returned 45,000 hits, mostly `cmd.exe` executing configuration scripts from a known IT management subnet.
3. The hunter applied the runbook's tuning parameters, excluding the specific IT subnet and the `svc_sccm` account. The results dropped to 14 hits.
4. Analyzing the 14 hits, the hunter noticed `WmiPrvSE.exe` spawning `powershell.exe -nop -exec bypass -EncodedCommand ...` on three critical database servers.
5. **Pivoting:** Following the runbook's pivot instructions, the hunter decoded the Base64 command, revealing a Cobalt Strike SMB beacon payload.
6. **Escalation:** The hunter immediately halted the hunt, captured the exact timestamp and affected hostnames, and initiated the IR escalation protocol as defined in the runbook. The DB servers were isolated, preventing the ransomware encryption phase.

## Documenting and Maturing the Process

A successful hunt doesn't end with escalation; it ends with systemic improvement.

1. **Detection Engineering:** If the hunt found an adversary, the query used should be hardened, tuned for low false-positive rates, and deployed as a real-time SIEM/EDR alert.
2. **Runbook Updates:** If the hunter found that certain data sources were missing or if a new legitimate administrative tool was causing noise, the runbook must be updated. This ensures the next hunter doesn't waste time on the same false positives.

## Key Considerations for Runbook Creation

* **Avoid Over-Prescribing:** While a runbook should be detailed, it must allow room for the analyst's intuition. Adversaries adapt; if the runbook is a rigid script, it will fail. Treat it as a framework, not a straitjacket.
* **Regular Review Cycles:** Technology changes. A runbook for hunting Exchange vulnerabilities is useless after a migration to Microsoft 365. Implement a quarterly review cycle for all active runbooks to ensure relevance and effectiveness.
* **Integration with Automation:** The ultimate goal of a runbook is to eventually automate the initial data gathering phase. By clearly defining the queries and data sources, security engineering teams can build Jupyter Notebooks or SOAR playbooks to pre-fetch the data, allowing the hunter to start immediately at the analysis phase.

## Chaining Opportunities
* A well-documented runbook directly addresses the challenge of managing false positives. Proceed to `[[12 - False Positives vs False Negatives in Hunting]]` to understand how to tune queries mathematically.
* When a runbook uncovers an active breach, the procedure must abruptly change. See `[[13 - Transitioning from Hunt to Incident Response]]` for the next steps in the escalation chain.
* For scaling these runbooks across massive datasets, refer to `[[14 - Automating Hunts vs Manual Investigations]]`.

## Related Notes
* `[[12 - False Positives vs False Negatives in Hunting]]`
* `[[13 - Transitioning from Hunt to Incident Response]]`
* `[[14 - Automating Hunts vs Manual Investigations]]`
* `[[15 - Measuring the ROI of a Threat Hunting Program]]`
