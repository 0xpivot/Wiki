---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.04 Known Bad vs Known Good vs Outliers"
---

# Known Bad vs Known Good vs Outliers

## Overview
In the realm of proactive threat hunting, the ability to rapidly sift through mountains of data is paramount. A typical enterprise generates terabytes of log data daily. To find the proverbial needle in the haystack, hunters employ a critical analytical framework: the categorization of data into "Known Bad," "Known Good," and "Outliers." 

This methodology is not merely about finding malware; it is a systematic approach to data reduction. By identifying and filtering out the expected, hunters isolate the unexpected, which is where advanced threats operate.

## The Data Categorization Triad

```text
+-----------------------------------------------------------------------+
|                    The Data Categorization Triad                      |
+-----------------------------------------------------------------------+
|                                                                       |
|   [Known Bad] <--------------------------------------> [Known Good]   |
|        |                                                    |         |
|        |                  [OUTLIERS]                        |         |
|        |                 (The Hunt Zone)                    |         |
|        v                                                    v         |
|   - Threat Intel Feeds                             - Golden Images    |
|   - AV Signatures                                  - Approved Apps    |
|   - Blocklists (IP/Domain)                         - Baselined Tfc    |
|   - Historical Incidents                           - Standard Configs |
|                                                                       |
+-----------------------------------------------------------------------+
```

### 1. Known Bad (The Reactive Domain)
"Known Bad" refers to artifacts, behaviors, or indicators that have been definitively identified as malicious. This is the domain of traditional, reactive security controls.

*   **Examples:** A file hash associated with WannaCry ransomware, an IP address belonging to a known Cobalt Strike team server, or an executable signed by a revoked, stolen certificate.
*   **The Hunter's Interaction:** While threat hunters *do* look for known bad, it is usually the starting point, not the end goal. Searching for known bad is typically automated via SIEM rules, EDR alerts, and firewall blocklists. If a hunter spends all their time searching for known IoCs, they are performing "Indicator Search," not true threat hunting.
*   **Value in Hunting:** Known bad is used to quickly triage alerts and to provide context. For example, if an outlier behavior connects to a Known Bad IP, the confidence of a true positive incident skyrockets.

### 2. Known Good (The Baseline)
"Known Good" (or the baseline) is the cornerstone of effective threat hunting. You cannot find the anomalous if you do not understand the normal. Known Good represents the legitimate, authorized, and expected activity within an environment.

*   **Examples:** `svchost.exe` running from `C:\Windows\System32\`, standard weekday VPN login times for employees, authorized administrative scripts executed by the IT team, or the expected volume of DNS traffic to the corporate DNS servers.
*   **The Hunter's Interaction:** Defining Known Good is arguably the most difficult and time-consuming part of threat hunting. It requires deep environmental awareness. Hunters use Known Good primarily for **data reduction**. By filtering out all definitively benign activity, the dataset is drastically reduced, making the analysis of what remains manageable.
*   **The Challenge:** Environments are dynamic. "Good" changes as new software is deployed, employees change roles, or infrastructure is upgraded. Baselines must be continuously updated to prevent alert fatigue from false positives.

### 3. Outliers (The Hunt Zone)
Outliers (or anomalies) are events, behaviors, or artifacts that do not fit into the "Known Bad" category (because no signature exists yet) but also deviate significantly from the "Known Good" baseline. **This is where threat hunting lives.**

*   **Examples:** `svchost.exe` running from `C:\Users\Public\`, a massive spike in outbound HTTPS traffic at 3:00 AM on a Sunday, a user logging in from two different countries within an hour (Impossible Travel), or an unusually long encoded command executed via PowerShell.
*   **The Hunter's Interaction:** Outliers are not inherently malicious. They are simply unusual. A hunter's primary job is to investigate outliers and determine their nature. They must answer the question: *Is this outlier a new, undocumented business process (a new Known Good), or is it a stealthy adversary (a new Known Bad)?*
*   **Analytical Techniques:** Hunters find outliers using statistical analysis (e.g., standard deviation), stack counting (frequency analysis), data clustering, and machine learning models.

## The Process of Data Reduction
The core technique utilizing this triad is Data Reduction (or filtering).

1.  **Collect Data:** Gather massive datasets based on the hunt hypothesis (e.g., all process execution logs for a week).
2.  **Filter Known Good:** Remove all standard OS processes, authorized third-party applications, and verified administrative scripts. (e.g., `WHERE process_name != 'chrome.exe' AND path != 'C:\Program Files\'`).
3.  **Filter Known Bad:** Ensure no automated alerts have already fired for the remaining data.
4.  **Analyze the Outliers:** The remaining dataset (the outliers) should be small enough for human analysis. The hunter investigates these remaining events, grouping similar anomalies and investigating the most suspicious ones.
5.  **Re-Categorize:** After investigating an outlier, the hunter must classify it. If it was an IT admin running a new script, it is added to the "Known Good" baseline. If it was an attacker, it is classified as "Known Bad," an incident is declared, and detection rules are written.

## Stack Counting (Frequency Analysis)
The most common technique for identifying outliers is stack counting.

*   **The Concept:** Attackers want to blend in, but their tools often leave unique, low-frequency footprints. By counting the occurrences of specific events and sorting them, hunters can easily spot outliers at the extremes.
*   **Execution:** A hunter aggregates a dataset (e.g., User-Agents in proxy logs) and counts how many times each unique User-Agent appears.
*   **Analysis:**
    *   *The Top (High Frequency):* Usually represents the "Known Good" (e.g., the standard corporate build of Chrome).
    *   *The Bottom (Low Frequency/Long Tail):* This is the Hunt Zone. A User-Agent that appears only 3 times across a network of 10,000 machines is highly anomalous. It could be a custom Python script used by an attacker, or it could be an obscure, legitimate application used by a single researcher. The hunter must investigate.

## Real-World Attack Scenario
**Scenario:** An advanced attacker has gained initial access and is attempting to establish persistence and move laterally without deploying custom malware. They rely entirely on "Living off the Land" binaries (LOLBins).

1.  **The Attack:** The attacker uses Windows Management Instrumentation (WMI) to spawn `cmd.exe` on remote systems. They execute commands that are base64 encoded to evade simple keyword string matching.
2.  **The Failure of Known Bad:** Traditional AV and basic SIEM rules fail. `WmiPrvSE.exe` and `cmd.exe` are legitimate Microsoft binaries. The encoded commands do not match any known malicious signatures.
3.  **The Application of the Triad:**
    *   The hunter gathers all logs showing `WmiPrvSE.exe` spawning child processes.
    *   **Filtering Known Good:** The hunter filters out instances where WMI spawns known management agents (e.g., SCCM, monitoring tools) based on established baselines.
    *   **Identifying Outliers:** The hunter performs stack counting on the command-line arguments of the remaining child processes. They notice a single instance where `cmd.exe` was spawned with an extremely long string of characters ending in `==` (a strong indicator of base64 encoding).
    *   **Investigation:** The encoded string is an outlier. The hunter decodes it and discovers a command designed to download a secondary payload via a hidden PowerShell window.
    *   **Re-categorization:** The outlier is confirmed as a true threat. The specific decoded behavior is now categorized as "Known Bad," and the incident response process begins.

## The Danger of "Assuming Good"
A critical pitfall in this methodology is the false assumption of "Known Good." Attackers are fully aware that hunters filter out known good processes.

*   **Process Masquerading:** Attackers frequently name their malware `svchost.exe` or `lsass.exe` to bypass superficial filters. Hunters must verify "Good" not just by name, but by path, cryptographic signature, and parent-child process relationships.
*   **Compromised Valid Accounts:** An attacker logging in with stolen credentials looks exactly like "Known Good" authentication. Detecting this requires analyzing behavioral outliers (e.g., logging in at 3 AM, accessing databases they never usually touch) rather than just looking at the successful login event.

## Chaining Opportunities
*   The continuous refinement of "Known Good" significantly reduces false positives in the SIEM, improving the efficiency of the entire SOC.
*   Outliers identified during stack counting can be fed into machine learning models to improve automated anomaly detection over time.
*   Discovered "Known Bad" TTPs must be immediately shared with Threat Intelligence platforms and automated blocking mechanisms (e.g., firewalls, EDR blocklists).

## Related Notes
*   [[01 - Introduction to Proactive Threat Hunting]]
*   [[02 - The Threat Hunting Loop Hypothesis to Triage]]
*   [[03 - Hypothesis Generation Methodologies]]
*   [[05 - Crown Jewel Analysis and Identifying Vital Assets]]
