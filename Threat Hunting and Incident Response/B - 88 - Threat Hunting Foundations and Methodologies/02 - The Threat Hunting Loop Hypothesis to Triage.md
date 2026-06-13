---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.02 The Threat Hunting Loop Hypothesis to Triage"
---

# The Threat Hunting Loop: Hypothesis to Triage

## Overview
Threat hunting is not a random search for bad things in the network; it is a highly structured, repeatable, and iterative process. Attempting to hunt without a formal methodology leads to inefficiency, burnout, and an inability to track success or improve detection capabilities. The most widely adopted framework for this structured approach is the Threat Hunting Loop, often attributed to the SANS Institute and various leading cybersecurity practitioners.

The Threat Hunting Loop consists of four primary phases:
1.  **Hypothesis Generation:** Formulating an educated guess about attacker behavior.
2.  **Investigation (Data Collection & Analysis):** Gathering relevant data and applying analytical techniques to test the hypothesis.
3.  **Pattern Discovery (TTP Discovery):** Identifying new malicious patterns and behaviors based on the analysis.
4.  **Automated Analytics & Triage (Operationalization):** Turning the findings into automated detections and responding to validated threats.

## The Anatomy of the Threat Hunting Loop

```text
+---------------------------------------------------------------------------------------+
|                               The Threat Hunting Loop                                 |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   +-----------------------+                         +---------------------------+     |
|   | 1. Create Hypothesis  |                         | 2. Investigate via Data   |     |
|   |                       |                         |    Collection & Analysis  |     |
|   | - Based on Intel      | ----------------------> | - Query SIEM/EDR          |     |
|   | - Based on Environment|                         | - Apply Analytics         |     |
|   | - Based on TTPs       |                         | - Identify Anomalies      |     |
|   +-----------------------+                         +---------------------------+     |
|             ^                                                     |                   |
|             |                                                     |                   |
|             |                                                     v                   |
|   +-----------------------+                         +---------------------------+     |
|   | 4. Automate & Triage  |                         | 3. Uncover Patterns &     |     |
|   |                       |                         |    TTP Discovery          |     |
|   | - Create SIEM Rules   | <---------------------- | - Correlate Events        |     |
|   | - Update Playbooks    |                         | - Document Behaviors      |     |
|   | - Initiate IR if Bad  |                         | - Refine Search Criteria  |     |
|   +-----------------------+                         +---------------------------+     |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

### Phase 1: Create Hypothesis
Every successful hunt begins with a well-defined hypothesis. A hypothesis is a testable statement predicting that a specific type of malicious activity is occurring within the environment. It must be specific enough to be actionable but broad enough to account for variations in attacker behavior.

**A good hypothesis considers:**
*   **The Actor:** Who might be attacking us? (e.g., Ransomware affiliate, Nation-State APT).
*   **The TTP:** How are they operating? (e.g., Using WMI for lateral movement, DNS for C2).
*   **The Environment:** Where are they operating? (e.g., High-value database servers, user endpoints).

**Examples of Strong vs. Weak Hypotheses:**
*   *Weak:* "Attackers are running malware on our endpoints." (Too broad, untestable, relies on automated AV).
*   *Strong:* "Adversaries are establishing persistence on domain controllers by modifying scheduled tasks or registry run keys, mimicking legitimate administrative scripts." (Specific, testable, focuses on behavior).

### Phase 2: Investigate via Data Collection and Analysis
Once the hypothesis is defined, the hunter must gather the necessary data to prove or disprove it. This requires a deep understanding of the organization's data sources (SIEM, EDR, network logs) and the technical skills to query them effectively.

**Data Collection Strategies:**
*   **Targeted Queries:** Writing specific queries (e.g., Splunk SPL, Elastic KQL) to extract exactly the data needed.
*   **Data Aggregation:** Pulling data from multiple disparate sources to build a complete picture of an event sequence.

**Analytical Techniques:**
*   **Stack Counting (Frequency Analysis):** Identifying the least common (or most common) occurrences of an event. Attackers often try to hide in the noise, but their unique tools or methods might stand out as statistical outliers.
*   **Clustering:** Grouping similar data points together to identify broader trends or anomalous clusters.
*   **Volume Analysis:** Looking for sudden spikes or drops in data volume (e.g., a massive spike in DNS traffic could indicate exfiltration).
*   **Timeline Analysis:** Reconstructing the chronological order of events to understand the narrative of an attack.

### Phase 3: Uncover Patterns and TTP Discovery
In this phase, the hunter analyzes the collected data, looking for the patterns and behaviors predicted by the hypothesis. This is where human intuition and analytical skill are paramount. The hunter must distinguish between legitimate administrative activity and malicious "living off the land" techniques.

**The Output of Phase 3:**
*   **Validation:** Proving that the hypothesis is true (malicious activity is found).
*   **Refutation:** Proving that the hypothesis is false (no malicious activity is found).
*   **Refinement:** Realizing the hypothesis needs adjustment based on the data discovered, leading to a new iteration of the loop.

*Crucially, finding nothing is not a failure.* A hunt that finds no malicious activity provides assurance that the specific TTP being investigated is not currently active. It also often highlights gaps in visibility or logging, which is a highly valuable outcome.

### Phase 4: Automate Analytics and Triage (Operationalization)
The final phase is about turning the knowledge gained during the hunt into persistent value. If a hunt is successful, the organization should not have to manually run that exact hunt again.

**Operationalization Steps:**
1.  **Automated Detection:** Translate the successful hunt query into a permanent rule or alert in the SIEM or EDR platform. This shifts the detection from a proactive hunt to a reactive automated control.
2.  **Playbook Updates:** Document the findings and update Incident Response (IR) playbooks to ensure rapid and consistent response when the new automated alert triggers.
3.  **Initiate Incident Response:** If an active, ongoing breach is discovered during the hunt, the hunt is immediately paused, and the findings are handed over to the Incident Response team for containment and eradication.
4.  **Visibility Improvements:** If the hypothesis could not be adequately tested due to missing data, recommendations are made to the engineering team to improve logging and telemetry.

## The Iterative Nature of the Loop
The Threat Hunting Loop is not a linear process that ends at Phase 4. It is designed to be continuous. The operationalization phase (automating a detection) frees up the hunter's time, allowing them to formulate new, more complex hypotheses, feeding directly back into Phase 1. This continuous cycle drives constant improvement in the organization's security posture and moves the SOC up the Hunting Maturity Model.

## Real-World Attack Scenario
**Scenario:** A threat intelligence report indicates that a new APT group is using maliciously crafted `.LNK` (shortcut) files distributed via spear-phishing. When executed, these `.LNK` files use `cmd.exe` to download and execute a payload via PowerShell, bypassing Mark-of-the-Web (MotW) protections.

**Executing the Threat Hunting Loop:**

1.  **Phase 1 - Hypothesis:** Based on the intel, the hunter formulates: *"Adversaries are attempting initial access and execution by utilizing `.LNK` files that spawn suspicious child processes, specifically `cmd.exe` executing PowerShell commands."*
2.  **Phase 2 - Investigation:** The hunter uses EDR telemetry to query process creation events. They search for instances where `explorer.exe` (the process that handles user interaction with the desktop/folders) spawns `cmd.exe`, which subsequently spawns `powershell.exe`. They filter out known good administrative scripts.
3.  **Phase 3 - Pattern Discovery:** The hunter performs stack counting on the command-line arguments of the discovered `powershell.exe` executions. They find a highly anomalous, heavily obfuscated PowerShell command executing from a temporary directory, originating from a user's Downloads folder. The hypothesis is validated.
4.  **Phase 4 - Automate & Triage:**
    *   **Triage:** The hunter immediately escalates the finding to the IR team, providing the compromised hostname, user account, and the malicious script.
    *   **Automate:** The hunter works with the SIEM engineering team to create a new behavioral detection rule: Alert when `explorer.exe` -> `cmd.exe` -> `powershell.exe` occurs, specifically if the command line contains `-enc` (encoded command) or references paths like `\Downloads\` or `\AppData\Local\Temp\`.

## Integrating Triage with Incident Response
Triage is the critical bridge between Threat Hunting and Incident Response. When a hunter discovers a true positive, they must act rapidly but methodically.

*   **Contextualization:** The hunter must gather enough context to confirm the finding is malicious and not a benign anomaly. This includes verifying timelines, involved assets, and the scope of the suspected compromise.
*   **Handoff:** The handoff to the IR team must be seamless. The hunter provides a detailed report of their findings, including the initial hypothesis, the queries used, the extracted data, and a summary of the attacker's observed TTPs.
*   **Collaboration:** Often, the threat hunter remains involved during the IR process, utilizing their deep knowledge of the environment and hunting skills to help scope the extent of the breach while the IR team focuses on containment.

## Common Pitfalls in the Loop
*   **Vague Hypotheses:** Starting with a hypothesis that is too broad makes Phase 2 nearly impossible to execute effectively.
*   **Data Overload:** Attempting to analyze too much data without proper filtering or analytical techniques leads to alert fatigue and missed anomalies.
*   **Failing to Automate:** If successful hunts are not operationalized into automated detections, the organization fails to improve its reactive capabilities and hunters are forced to repeat work.

## Chaining Opportunities
*   The output of Phase 4 (Automate) directly feeds into the tuning and optimization of SIEM and EDR rulesets.
*   Findings from the hunting loop are critical inputs for tabletop exercises and red team engagements.
*   Discovered TTPs should be mapped to the MITRE ATT&CK framework to visualize defensive coverage.

## Related Notes
*   [[01 - Introduction to Proactive Threat Hunting]]
*   [[03 - Hypothesis Generation Methodologies]]
*   [[04 - Known Bad vs Known Good vs Outliers]]
*   [[05 - Crown Jewel Analysis and Identifying Vital Assets]]
