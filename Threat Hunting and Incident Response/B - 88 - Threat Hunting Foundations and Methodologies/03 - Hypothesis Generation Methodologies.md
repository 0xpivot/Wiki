---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.03 Hypothesis Generation Methodologies"
---

# Hypothesis Generation Methodologies

## Overview
A hypothesis is the foundation of any proactive threat hunt. It dictates the scope, the data sources required, and the analytical techniques that will be employed. Without a well-crafted hypothesis, threat hunting devolves into aimless data browsing ("hunting for bad"), which is highly inefficient and rarely yields actionable results. 

Hypothesis generation is the process of formulating a structured, testable statement about suspected malicious activity within an environment. This document explores the primary methodologies used by elite threat hunters to generate robust and actionable hypotheses.

## Characteristics of a Strong Hypothesis
Before diving into the methodologies, it's critical to understand what makes a hypothesis "good."

1.  **Testable:** The hypothesis must be provable or disprovable using the data available to the organization. "Nation-state actors are targeting us" is not testable. "Actors are using WMI to execute base64 encoded commands on our Domain Controllers" is testable.
2.  **Specific but Flexible:** It should be narrow enough to guide a focused search but broad enough to catch slight variations in an attacker's TTPs.
3.  **Documented:** The reasoning behind the hypothesis (why it was chosen) must be recorded for future reference and continuous improvement.
4.  **Actionable:** If the hypothesis is proven true, there must be a clear path to triage and incident response.

## The Three Pillars of Hypothesis Generation
There are three primary methodologies for generating threat hunting hypotheses. Most mature security teams utilize a combination of all three to ensure comprehensive coverage.

```text
+---------------------------------------------------------------------------------+
|                    Hypothesis Generation Methodologies                          |
+----------------------+--------------------------+-------------------------------+
| Intelligence-Driven  | Situational-Awareness    | Domain-Driven (Analytics)     |
| (Threat Intel)       | (Environment Driven)     | (TTP/Behavior Driven)         |
+----------------------+--------------------------+-------------------------------+
| Focus: "Who is       | Focus: "What is          | Focus: "How would an          |
| attacking us?"       | changing here?"          | attacker operate?"            |
+----------------------+--------------------------+-------------------------------+
| Input: Reports, OSINT| Input: Crown Jewels,     | Input: MITRE ATT&CK, Red      |
| ISACs, Feeds         | Vuln Scans, Architecture | Team Reports, Pentests        |
+----------------------+--------------------------+-------------------------------+
| Example: "APT29 uses | Example: "The new DMZ    | Example: "Attackers use       |
| specific registry    | server might be          | PowerShell with encoded       |
| keys for persistence"| misconfigured for RDP"   | commands to evade AV"         |
+----------------------+--------------------------+-------------------------------+
```

### 1. Intelligence-Driven Hypothesis Generation
This methodology relies heavily on external Threat Intelligence (TI). Hunters consume reports from vendors, Information Sharing and Analysis Centers (ISACs), open-source intelligence (OSINT), and government alerts to understand current campaigns and adversary behavior.

**How it works:**
*   The hunter reads a report detailing a new malware variant or an active APT campaign targeting their specific industry.
*   The hunter extracts the Tactics, Techniques, and Procedures (TTPs) described in the report.
*   A hypothesis is formulated based on the premise that this specific adversary might be targeting the organization using those exact TTPs.

**Pros:** Highly relevant to current, real-world threats. Often provides clear indicators and behaviors to look for.
**Cons:** Inherently reactive to *known* threats. If the intelligence is poor or outdated, the hunt is wasted. It often struggles against zero-day exploits or highly bespoke attacks.

**Example Hypothesis:**
*   *Intelligence:* CISA releases an alert that ransomware operators are actively exploiting ProxyLogon (CVE-2021-26855) to drop web shells on Exchange servers.
*   *Hypothesis:* "Adversaries have successfully exploited CVE-2021-26855 on our external-facing Exchange infrastructure and have written `.aspx` web shells to the `C:\inetpub\wwwroot\aspnet_client\` directory."

### 2. Situational-Awareness (Environment) Driven
This methodology requires deep, intimate knowledge of the organization's own network, infrastructure, and business operations. It focuses on internal changes, vulnerabilities, and "Crown Jewel" assets.

**How it works:**
*   The hunter analyzes internal data: recent vulnerability scans, architectural changes, newly deployed applications, or upcoming corporate events (e.g., a major merger).
*   The hunter considers how these internal factors might create new attack vectors or increase risk.
*   A hypothesis is generated focusing on the intersection of internal vulnerabilities and critical assets.

**Pros:** Highly tailored to the specific organization. Excellent for finding insider threats, misconfigurations, or attacks targeting specific business processes.
**Cons:** Requires extensive cross-departmental communication and deep institutional knowledge. Can be difficult in massive, highly dynamic cloud environments.

**Example Hypothesis:**
*   *Situation:* The organization recently acquired a smaller company and established a VPN trust between the two domains. The acquired company has a lower security maturity.
*   *Hypothesis:* "Adversaries have compromised an endpoint in the acquired company's network and are attempting lateral movement across the newly established VPN trust using stolen credentials via SMB (Port 445)."

### 3. Domain-Driven (Analytics/TTP) Generation
This is the most advanced and proactive methodology. It relies on a deep understanding of attacker behavior, operating system internals, and frameworks like MITRE ATT&CK. It does not rely on specific threat intelligence or internal events, but rather on the fundamental ways attackers *must* operate to succeed.

**How it works:**
*   The hunter studies an overarching tactic (e.g., Persistence, Credential Access).
*   They analyze the various techniques used to achieve that tactic (e.g., Registry Run Keys, LSASS dumping).
*   A hypothesis is generated to detect the *behavior* of the technique, regardless of the specific tool or actor used.

**Pros:** Excellent for detecting zero-day attacks, "Living off the Land" (LotL) techniques, and unknown adversaries. Highly proactive.
**Cons:** Requires advanced technical skills (data science, OS internals) and generates the highest volume of data to analyze. High potential for false positives if not carefully tuned.

**Example Hypothesis:**
*   *Domain Knowledge:* Attackers frequently use WMI (Windows Management Instrumentation) for stealthy lateral movement and execution, as it blends in with administrative traffic.
*   *Hypothesis:* "Adversaries are utilizing `WmiPrvSE.exe` to spawn abnormal child processes (such as `cmd.exe` or `powershell.exe`) to execute commands remotely across the network."

## The Role of MITRE ATT&CK
The MITRE ATT&CK framework is an indispensable tool for Domain-Driven hypothesis generation. It provides a standardized taxonomy of adversary behavior.

Hunters use ATT&CK to:
*   **Identify Gaps:** Map existing SIEM/EDR rules against the matrix to find areas with zero coverage, then generate hypotheses to hunt in those specific areas.
*   **Structure Hunts:** Use specific Technique IDs (e.g., T1059.001 - PowerShell) to standardize documentation and communication.
*   **Emulate Adversaries:** Work with Red Teams to execute specific techniques, capture the resulting logs, and use that data to build robust hunting hypotheses.

## Real-World Attack Scenario
**Scenario:** A large enterprise heavily utilizes Microsoft 365. They have strong endpoint controls but have recently experienced a high volume of phishing attempts.

**Applying the Methodologies:**

1.  **Intelligence-Driven:**
    *   *Intel:* A new report details a campaign where attackers bypass MFA by utilizing legacy authentication protocols (e.g., IMAP/POP3) against Azure AD.
    *   *Hypothesis:* "Attackers are attempting to authenticate to our M365 tenant using legacy protocols from foreign IP addresses to bypass conditional access policies."

2.  **Situational-Awareness Driven:**
    *   *Situation:* The HR department is currently undertaking a massive hiring drive, receiving thousands of resumes (PDFs/DOCXs) daily via a specific external portal.
    *   *Hypothesis:* "Adversaries are submitting malicious macro-enabled documents through the HR portal, resulting in abnormal process spawning (e.g., `winword.exe` spawning `powershell.exe`) on HR endpoints."

3.  **Domain-Driven:**
    *   *Domain Knowledge:* To maintain persistent access in cloud environments, attackers often create rogue Inbox rules to forward emails or hide evidence of compromise.
    *   *Hypothesis:* "Unauthorized users are utilizing PowerShell (e.g., `New-InboxRule`) to create hidden email forwarding rules within VIP Exchange Online mailboxes."

## Refining and Prioritizing Hypotheses
A mature hunting team will generate more hypotheses than they have time to execute. Prioritization is essential.

*   **Risk vs. Effort:** Evaluate hypotheses based on the potential impact if true (Risk) versus the difficulty of gathering the data and proving it (Effort). High Risk / Low Effort hunts should be executed first.
*   **Crown Jewel Proximity:** Prioritize hunts that focus on the infrastructure immediately surrounding the organization's most critical assets.
*   **Data Availability:** A brilliant hypothesis is useless if the required logs are not being collected. Discard or table hypotheses that cannot be tested, but use them to justify requests for better logging.

## Chaining Opportunities
*   A validated Domain-Driven hypothesis often leads to the discovery of new Indicators of Compromise (IoCs), which can then be fed back into Intelligence-Driven hunts.
*   Hypotheses generated during a hunt should be documented in a central repository to avoid duplication of effort and build a knowledge base.
*   Collaborate with Red Teams to validate hypotheses through Purple Teaming exercises before executing them in production.

## Related Notes
*   [[01 - Introduction to Proactive Threat Hunting]]
*   [[02 - The Threat Hunting Loop Hypothesis to Triage]]
*   [[04 - Known Bad vs Known Good vs Outliers]]
*   [[05 - Crown Jewel Analysis and Identifying Vital Assets]]
