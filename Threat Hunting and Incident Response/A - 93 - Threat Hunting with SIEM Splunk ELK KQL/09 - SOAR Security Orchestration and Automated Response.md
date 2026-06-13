---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.09 SOAR Security Orchestration and Automated Response"
---
# 93.09 SOAR: Security Orchestration, Automation, and Response

## Overview
Security Orchestration, Automation, and Response (SOAR) platforms represent the nervous system of a mature Security Operations Center (SOC). While SIEMs (Splunk, ELK, Sentinel) act as the brain—collecting data, detecting anomalies, and generating alerts—they do not, by themselves, take action. SOAR platforms bridge the gap between detection and remediation. They connect disparate security tools, automate highly repetitive triage workflows, and execute rapid, standardized incident response procedures at machine speed. 

By implementing SOAR, organizations drastically reduce their Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR), alleviate alert fatigue, and free up Tier 3 analysts to focus on advanced threat hunting rather than mundane data gathering.

## The Three Pillars of SOAR
1. **Orchestration:** The ability to integrate and coordinate disparate security tools (firewalls, EDR, IAM, email gateways, sandboxes) via APIs. Orchestration ensures that a single platform can pull a file from an endpoint, submit it to VirusTotal, check the sender IP against MISP, and push a block rule to a Palo Alto firewall.
2. **Automation:** The execution of predefined workflows (Playbooks/Runbooks) without human intervention. This codifies the standard operating procedures (SOPs) of the SOC into software logic.
3. **Response:** Case management, ticketing, and reporting. SOAR platforms act as the centralized workbench where analysts review the output of automation, collaborate on incidents, and document the investigation lifecycle.

## ASCII Architecture: The SOAR Ecosystem Workflow

```text
+-------------------+      +-------------------+      +-------------------+
|    SIEM / XDR     |      |  Threat Intel     |      |   User Reports    |
| (Splunk/Sentinel) |      |   (MISP/Otx)      |      | (Phish Mailbox)   |
+-------------------+      +-------------------+      +-------------------+
          |                          |                          |
          v                          v                          v
+-------------------------------------------------------------------------+
|                        SOAR Platform (e.g. Cortex XSOAR)                |
|                                                                         |
|  [ Event Ingestion Engine ] --> Normalizes incoming alerts to a Case    |
|                                                                         |
|  [ Playbook Execution Engine ]                                          |
|     |                                                                   |
|     +--> Context Enrichment: Query AD for User Info, VT for Hashes      |
|     +--> Triage Logic: If VT Score > 10, escalate to High Severity      |
|     +--> Automated Action: Isolate Host via CrowdStrike API             |
|                                                                         |
|  [ Case Management UI ] --> Analyst workbench for final decision making |
+-------------------------------------------------------------------------+
          |                          |                          |
          v                          v                          v
+-------------------+      +-------------------+      +-------------------+
|     Network       |      |     Endpoint      |      |     Identity      |
| (Firewall Block)  |      |   (EDR Isolate)   |      | (Disable AD Acct) |
+-------------------+      +-------------------+      +-------------------+
```

## Anatomy of a Playbook
A playbook is a directed graph of automated tasks mapped to a specific incident type (e.g., Phishing, Malware, Failed Logins).

1. **Trigger:** The event that initiates the playbook (e.g., an alert from Splunk ES).
2. **Data Extraction (Parsing):** Using regex or JSON parsing to extract indicators (IPs, URLs, Hashes, Users) from the raw alert payload.
3. **Enrichment:** Querying integrated systems to add context to the indicators.
   - *Is the IP known to MISP?*
   - *What is the user's role in Active Directory?*
   - *Has this file hash been seen globally in VirusTotal?*
4. **Decision Blocks:** Conditional logic (If/Else) based on the enriched data.
5. **Remediation Actions:** Active steps taken to contain the threat.
6. **Notification/Ticketing:** Updating ServiceNow/Jira and notifying the SOC via Slack/Teams.

## Industry-Leading SOAR Platforms
- **Splunk SOAR (formerly Phantom):** Deeply integrated with Splunk Enterprise Security. Utilizes a Python-based execution engine. Excellent for complex, highly customized automation scripts.
- **Palo Alto Cortex XSOAR (formerly Demisto):** Known for its massive library of pre-built integrations, collaborative "War Room" interface, and highly visual playbook editor.
- **Microsoft Sentinel (Logic Apps):** Native SOAR capabilities built directly into the Sentinel SIEM via Azure Logic Apps. Exceptional for orchestrating across the Microsoft 365 and Azure ecosystem (Entra ID, Defender for Endpoint).

## Real-World Attack Scenario

### Scenario: The Phishing Campaign and Automated Containment
A targeted spear-phishing campaign hits an organization. An employee receives an email containing a malicious Word document with an embedded macro, opens it, and the macro attempts to download a second-stage payload. The EDR detects suspicious PowerShell execution originating from `WINWORD.exe` and fires a High Severity alert into the SIEM. The SIEM forwards this alert to the SOAR platform.

### The Automated Playbook Workflow (Time Elapsed: 45 Seconds)

**Step 1: Alert Ingestion & Artifact Extraction**
The SOAR platform receives the JSON payload from the SIEM. It parses out the `EndpointName`, `UserName`, `FileHash` (of the Word doc), and the `DestinationIP` (the C2 server the PowerShell attempted to reach).

**Step 2: Automated Enrichment**
- The SOAR queries Active Directory: Discovers `UserName` belongs to the CFO (High Value Target).
- The SOAR queries VirusTotal with the `FileHash`: Returns a score of 45/70 indicating known malware (Emotet variant).
- The SOAR queries MISP with the `DestinationIP`: Matches an active IOC for an Emotet C2 node.

**Step 3: Decision Engine & Severity Escalation**
The playbook evaluates the data: Target is an Executive AND File is known malware AND IP is a known C2. The playbook automatically escalates the incident severity from High to Critical.

**Step 4: Automated Remediation (Containment)**
- **API Call to EDR (CrowdStrike/Defender):** Issues a "Network Containment" command to isolate the CFO's laptop, breaking the connection to the C2 server while keeping access open for SOC forensics.
- **API Call to IAM (Azure AD/Entra ID):** Forces a password reset and revokes all active session tokens for the CFO's account to prevent lateral movement.
- **API Call to Email Security (Proofpoint/Mimecast):** Searches the mail gateways for any other delivered emails containing the same `FileHash` and automatically purges them from all user inboxes (Auto-Purge/Search and Destroy).
- **API Call to Firewall (Palo Alto):** Adds the `DestinationIP` to a dynamic blocklist.

**Step 5: Human-in-the-Loop & Case Management**
By the time the Tier 1 analyst clicks on the alert in the SOAR dashboard, the host is contained, the lateral spread is halted, other users are protected, and all contextual data is summarized in the Case notes. The analyst is presented with a prompt: *"Containment executed successfully. Proceed to Forensic Analysis and Re-imaging?"*

## Challenges and Pitfalls of SOAR Implementation
1. **Garbage In, Garbage Out:** SOAR platforms amplify the quality of your SIEM alerts. If your SIEM is generating thousands of false positives, hooking a SOAR platform to them will result in automated, chaotic disruptions across the network. High-fidelity detections are a prerequisite for SOAR.
2. **API Rate Limiting and Maintenance:** SOAR relies entirely on third-party APIs. When a vendor updates their API, playbooks break. Relying heavily on public APIs (like the free tier of VirusTotal) will quickly hit rate limits during a major incident.
3. **The "Automate Everything" Fallacy:** Not every alert requires an automated response. Irreversible actions (wiping a hard drive, shutting down a core switch) should always require a "Human-in-the-Loop" approval step within the playbook.

## Chaining Opportunities
- SOAR platforms rely heavily on high-fidelity, context-rich alerts generated by SIEM correlation searches. See [[07 - Advanced KQL Joins and Time-Series Analysis]].
- The indicators used by SOAR for enrichment and blocking are often maintained within MISP. See [[08 - Integrating MISP with Splunk ELK]].
- To parse incoming SIEM data effectively, the SOAR platform expects logs to be structured consistently. See [[10 - Normalizing Data Sources Common Information Model CIM]].

## Related Notes
- [[04 - Threat Hunting Methodologies]]
- [[07 - Advanced KQL Joins and Time-Series Analysis]]
- [[08 - Integrating MISP with Splunk ELK]]
- [[10 - Normalizing Data Sources Common Information Model CIM]]
- [[12 - Incident Response Frameworks PICERL]]
