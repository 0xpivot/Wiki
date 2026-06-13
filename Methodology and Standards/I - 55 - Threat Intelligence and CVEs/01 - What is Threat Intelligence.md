---
tags: [threat-intel, cve, research, vapt]
difficulty: beginner
module: "55 - Threat Intelligence and CVEs"
topic: "55.01 What is Threat Intelligence"
---

# What is Cyber Threat Intelligence (CTI)?

## Introduction to Threat Intelligence
Cyber Threat Intelligence (CTI) is knowledge, skills, and experience-based information concerning the occurrence and assessment of both cyber and physical threats and threat actors that is intended to help mitigate potential attacks and harmful events occurring in cyberspace. In the context of Vulnerability Assessment and Penetration Testing (VAPT), Threat Intelligence serves as the foundation for simulating realistic, threat-actor-aligned attacks. While standard vulnerability scanning merely identifies missing patches and misconfigurations, threat-intelligence-led penetration testing (such as the TIBER-EU framework or CBEST) uses actionable intelligence to emulate the exact tactics, techniques, and procedures (TTPs) of adversaries likely to target the specific organisation.

The importance of CTI lies in moving an organisation's security posture from reactive to proactive. By understanding who the adversaries are, what their motivations are, and how they operate, defenders can anticipate attacks, prioritize patching based on actual exploitation trends rather than static CVSS scores, and tailor their security controls to defend against the most pertinent threats.

## Types of Threat Intelligence
Threat intelligence is generally categorized into four main types, each serving different audiences and purposes within an organisation:

### 1. Strategic Threat Intelligence
- **Audience**: C-Level Executives, Board of Directors, IT Management.
- **Focus**: High-level trends, long-term implications, financial impact, geopolitical drivers, and broader threat landscapes.
- **Content**: Reports on the rise of specific ransomware cartels, state-sponsored campaigns against particular sectors, and regulatory compliance changes.
- **VAPT Application**: Helps scope penetration tests by identifying which critical business assets are most likely to be targeted by advanced persistent threats (APTs).

### 2. Tactical Threat Intelligence
- **Audience**: Security Architects, SOC Managers, Penetration Testers.
- **Focus**: Adversary Tactics, Techniques, and Procedures (TTPs).
- **Content**: Detailed analysis of how a threat actor operates, such as their preferred initial access vectors (e.g., spear-phishing vs. exploiting public-facing applications), privilege escalation techniques, and lateral movement methods.
- **VAPT Application**: Directs the red team or penetration testers on *how* to attack the network, ensuring the engagement accurately mimics real-world adversaries.

### 3. Operational Threat Intelligence
- **Audience**: Threat Hunters, Incident Responders, Vulnerability Managers.
- **Focus**: Specific impending attacks against the organisation.
- **Content**: Intelligence gathered from dark web forums, botnet command and control (C2) monitoring, or insider threat monitoring. It answers questions like "Is our organisation currently being targeted?"
- **VAPT Application**: Validates whether the organisation's defenses can withstand the specific campaigns currently active in the wild.

### 4. Technical Threat Intelligence
- **Audience**: SOC Analysts, SIEM systems, Firewalls, Endpoint Detection and Response (EDR) tools.
- **Focus**: Indicators of Compromise (IoCs).
- **Content**: Malicious IP addresses, domain names, file hashes (MD5, SHA-256), and malicious URLs.
- **VAPT Application**: Used for bypass testing. Can the red team use known malicious infrastructure without being detected? Can the blue team identify these technical indicators during an active test?

## The Threat Intelligence Lifecycle
The generation of actionable threat intelligence is not a one-off event but a continuous cycle.

1. **Direction/Planning**: Defining the intelligence requirements (IRs). What does the organisation need to know? What assets are we protecting?
2. **Collection**: Gathering raw data from internal sources (logs, SIEM), technical sources (feeds, NVD), and human sources (dark web forums, OSINT).
3. **Processing**: Normalising, structuring, and filtering the raw data into a usable format. This involves deduplication and translation.
4. **Analysis**: Correlating the processed data to answer the intelligence requirements defined in the first step. This turns raw data into *information*, and then into *intelligence*.
5. **Dissemination**: Distributing the final intelligence product to the relevant stakeholders (e.g., sending an IoC feed to the firewall, or a strategic report to the CISO).
6. **Feedback**: Evaluating whether the intelligence provided was useful, timely, and actionable, which informs the next iteration of the cycle.

## Indicators of Compromise (IoCs) vs Indicators of Attack (IoAs)
Understanding the difference between IoCs and IoAs is crucial for both offensive and defensive security.

- **Indicators of Compromise (IoCs)**: These are forensic artefacts left behind after a breach has occurred. They are inherently reactive. Examples include a known malware hash, an IP address associated with a known C2 server, or a specific registry key modification. IoCs are useful for sweeping a network to see if it *has been* compromised.
- **Indicators of Attack (IoAs)**: These focus on the *intent* and the *actions* of an attacker, regardless of the specific tools used. They are proactive. An example would be "A user opening a Word document which spawns a PowerShell process that connects to an external IP". The exact hash of the Word doc or the IP address doesn't matter; the *behaviour* is the indicator.

In VAPT, focusing on IoAs is far more effective. A red team can easily recompile malware to change its hash (evading IoC detection), but it is much harder for them to change their fundamental operational behaviour (IoA detection).

## Threat Modeling and Attack Frameworks
To effectively structure and communicate tactical threat intelligence, the industry relies on standard frameworks.

### MITRE ATT&CK Framework
The Adversarial Tactics, Techniques, and Common Knowledge (ATT&CK) framework is a globally accessible knowledge base of adversary tactics and techniques based on real-world observations. It categorizes adversary behavior into distinct Tactics (the *why*, e.g., Initial Access) and Techniques (the *how*, e.g., Phishing).

### The Cyber Kill Chain
Developed by Lockheed Martin, this framework models the stages of a cyberattack:
1. Reconnaissance
2. Weaponization
3. Delivery
4. Exploitation
5. Installation
6. Command and Control (C2)
7. Actions on Objectives

### The Diamond Model of Intrusion Analysis
This model emphasizes the relationships between four core features of any intrusion event: Adversary, Capability, Infrastructure, and Victim. It is heavily used in threat attribution and tracking threat actors over time.

## Visualizing the Threat Intelligence Lifecycle

```text
+---------------------------------------------------------+
|              Threat Intelligence Lifecycle              |
+---------------------------------------------------------+
       ^                                         |
       |                                         |
       | 1. Direction & Planning                 |
       |    (Defining Requirements)              |
       |                                         v
       |                               +-------------------+
+------+------+                        | 2. Collection     |
| 6. Feedback |                        |    (Raw Data)     |
| & Review    |                        +--------+----------+
+------+------+                                 |
       ^                                        |
       |                                        v
+------+----------+                    +-------------------+
| 5. Dissemination|                    | 3. Processing     |
|    (To Stake-   |                    |    (Normalisation)|
|     holders)    |                    +--------+----------+
+------+----------+                             |
       ^                                        |
       |                                        v
       |          +-------------------+         |
       +----------+ 4. Analysis &     |<--------+
                  |    Production     |
                  +-------------------+
```

## Incorporating CTI into VAPT
To maximize the value of Penetration Testing and Red Teaming, VAPT engagements should be threat-led. This involves:
1. **Threat Profiling**: Before the test begins, the CTI team identifies the most likely threat actors targeting the client's industry and geographic location.
2. **TTP Extraction**: The CTI team extracts the known Tactics, Techniques, and Procedures used by these actors using frameworks like MITRE ATT&CK.
3. **Scenario Development**: The Red Team develops attack scenarios that mimic these specific TTPs.
4. **Execution and Emulation**: The Red Team executes the attack, using similar tools, infrastructure, and pacing as the real adversary.
5. **Defensive Review**: The Blue Team evaluates whether their detection engineering and incident response processes effectively identified and mitigated the simulated threat.

## Chaining Opportunities
- Threat Intelligence gathered during the reconnaissance phase can directly feed into prioritizing which vulnerabilities to test first.
- Identifying leaked credentials via Operational CTI can be chained with external access testing.
- Understanding threat actor preferred exploits helps in searching Exploit-DB effectively.

## Related Notes
- [[02 - CVE CVSS CWE Terminology]]
- [[03 - NVD National Vulnerability Database]]
- [[04 - Exploit-DB and Packet Storm]]
- [[05 - SearchSploit Offline Exploit-DB Search]]
