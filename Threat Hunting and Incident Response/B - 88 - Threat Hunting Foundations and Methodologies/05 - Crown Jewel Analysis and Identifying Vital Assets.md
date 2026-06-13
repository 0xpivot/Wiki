---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.05 Crown Jewel Analysis and Identifying Vital Assets"
---

# Crown Jewel Analysis and Identifying Vital Assets

## Overview
A fundamental reality of cybersecurity is that you cannot protect everything equally. Resources—budget, personnel, and time—are finite. In the context of proactive threat hunting, this reality is even more pronounced. Hunters cannot analyze every single log from every single endpoint. Therefore, they must prioritize their efforts based on risk.

Crown Jewel Analysis (CJA) is a systematic methodology for identifying, classifying, and prioritizing an organization's most critical assets. These are the assets that, if compromised, stolen, or destroyed, would cause catastrophic damage to the business's operations, reputation, or financial standing. For a threat hunter, knowing where the Crown Jewels are located is the map that guides the hunt.

## What Constitutes a Crown Jewel?
Crown Jewels are not merely "important servers." They are the core data and processes that define the organization's value. 

Examples vary drastically by industry:
*   **Financial Institution:** The SWIFT transaction database, customer PII/financial records, core banking applications.
*   **Healthcare Provider:** Electronic Health Records (EHR) systems, medical device control networks.
*   **Manufacturing/Tech:** Intellectual Property (IP), source code repositories, proprietary algorithms, industrial control systems (ICS/SCADA).
*   **E-commerce:** The customer credential database, payment processing gateways.
*   **Universally Critical:** Identity and Access Management (IAM) infrastructure. Active Directory (AD) or major Single Sign-On (SSO) providers are almost always Crown Jewels, as compromising them grants access to everything else.

## The Process of Crown Jewel Analysis

```text
+-----------------------------------------------------------------------------------+
|                        Crown Jewel Analysis Workflow                              |
+-----------------------------------------------------------------------------------+
| 1. Identify Business Mission & Processes                                          |
|    (What makes the company money? What are the legal obligations?)                |
|           |                                                                       |
|           v                                                                       |
| 2. Map Processes to Data                                                          |
|    (What data is required for these processes to function?)                       |
|           |                                                                       |
|           v                                                                       |
| 3. Map Data to Systems/Assets                                                     |
|    (Where does this data live? Servers, Cloud, Endpoints, Databases)              |
|           |                                                                       |
|           v                                                                       |
| 4. Identify Dependencies                                                          |
|    (What network segments, AD groups, or hypervisors support these systems?)      |
|           |                                                                       |
|           v                                                                       |
| 5. Prioritize and Apply Defensive/Hunting Focus                                   |
|    (Hunt in the pathways leading to these assets)                                 |
+-----------------------------------------------------------------------------------+
```

### 1. Business Impact Analysis (BIA) Integration
CJA cannot be performed in a vacuum by the IT or Security team. It requires deep engagement with business unit leaders. A system that IT considers low-priority might be the sole generator of revenue for a specific department. Security must understand the Business Impact Analysis (BIA) to know the true cost of downtime or data loss for specific assets.

### 2. Dependency Mapping (The Attack Path)
Identifying the database containing the Crown Jewels is only the first step. Threat hunters must understand the entire ecosystem supporting that database. Attackers rarely land directly on a Crown Jewel; they land on a vulnerable endpoint and traverse the network.

Hunters must map the dependencies:
*   **Network Paths:** Which subnets have routing access to the Crown Jewel segment? Are there overly permissive firewall rules?
*   **Identity Paths:** Which Active Directory groups have administrative access to the server? Who are the members of those groups? Are service accounts being used securely?
*   **Infrastructure Paths:** Which hypervisor hosts the VM? Which storage array holds the data? A compromise of the underlying ESXi host is a compromise of the Crown Jewel VM.

### 3. Attack Surface Reduction
Once Crown Jewels and their dependencies are identified, the immediate goal is to shrink the attack surface around them. This involves implementing strict network segmentation (Zero Trust architectures), enforcing Multi-Factor Authentication (MFA) for all administrative access, and ensuring these systems are patched with the highest priority.

## Hunting Around the Crown Jewels
Threat hunters use the output of CJA to focus their Situational-Awareness methodologies (see [[03 - Hypothesis Generation Methodologies]]). 

**The Strategy:** Hunters do not just hunt *on* the Crown Jewel; they hunt on the *pathways* leading to it.

1.  **Chokepoint Hunting:** If all administrative access to a critical database must pass through a specific Jump Server (Bastion Host), the hunter focuses intensely on the logs of that Jump Server. Any anomaly there is an immediate red flag.
2.  **Privilege Escalation Focus:** Knowing that attackers need high-level credentials to access the Crown Jewels, hunters aggressively monitor for identity-based attacks (e.g., Kerberoasting, DCSync, unauthorized modifications to high-privilege AD groups).
3.  **Data Exfiltration Monitoring:** For assets where data theft is the primary risk (e.g., IP repositories), hunters baseline the normal outbound data transfer rates and hunt for anomalous spikes, unusual staging directories, or unauthorized use of cloud storage tools.

## Real-World Attack Scenario
**Scenario:** A pharmaceutical company is in the final stages of developing a highly lucrative new drug. The proprietary chemical formulas (the Crown Jewels) are stored in a restricted document management system on a segmented internal network.

1.  **The Attack:** An advanced persistent threat (APT) group, seeking to steal the IP, breaches a low-level marketing employee's laptop via a phishing email.
2.  **The Navigation:** The marketing laptop has no direct network access to the restricted R&D segment. The attacker begins mapping the network. They discover that IT administrators frequently use Remote Desktop Protocol (RDP) from a specific IT subnet to manage the R&D servers.
3.  **The Pivot:** The attacker moves laterally from the marketing laptop to a weakly secured print server, and from there to an IT administrator's workstation. They steal the administrator's session tokens, granting them access to the Jump Server that bridges the IT subnet and the R&D segment.
4.  **The Goal:** They cross the Jump Server, access the document management system, compress the formulas, and exfiltrate them.

**How Crown Jewel-Focused Hunting Prevents This:**
*   A threat hunter, knowing the document management system is a Crown Jewel, has explicitly mapped its dependencies, including the Jump Server and the specific IT administrator accounts.
*   The hunter regularly executes hypotheses based on these pathways: *"Are unauthorized processes executing on the R&D Jump Server?"* or *"Are IT Admin accounts exhibiting anomalous login behaviors from non-standard endpoints?"*
*   When the attacker pivots to the IT admin's workstation and initiates the RDP session to the Jump Server, the hunter identifies this as an outlier (a deviation from the Known Good baseline of how that specific admin usually operates), triggering an immediate investigation before the data is exfiltrated.

## Challenges in Crown Jewel Analysis
*   **Dynamic Environments:** In cloud and containerized environments, assets are ephemeral. A server might exist for only a few hours. CJA must shift from focusing on physical servers to focusing on data flows, IAM roles, and microservices.
*   **Shadow IT:** Departments often procure cloud services (SaaS) and store critical data without the knowledge of the central IT or Security teams. You cannot hunt around a Crown Jewel you do not know exists.
*   **Over-Classification:** If a business unit claims *all* their data is a Crown Jewel, the categorization loses its value. Strict criteria must be enforced to maintain focus.

## Chaining Opportunities
*   Crown Jewel Analysis directly informs the prioritization matrix for incident response and disaster recovery plans.
*   The dependency maps created during CJA are invaluable for Red Teams conducting objective-based penetration tests (e.g., "See if you can access the SWIFT database").
*   Gaps in visibility discovered around Crown Jewels must be escalated to engineering for immediate remediation.

## Related Notes
*   [[01 - Introduction to Proactive Threat Hunting]]
*   [[02 - The Threat Hunting Loop Hypothesis to Triage]]
*   [[03 - Hypothesis Generation Methodologies]]
*   [[04 - Known Bad vs Known Good vs Outliers]]
