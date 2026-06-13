---
tags: [cti, intelligence, threat-hunting, vapt]
difficulty: beginner
module: "82 - CTI Foundations and Intelligence Lifecycle"
topic: "82.05 Mitre ATT&CK Framework Deep Dive"
---

# MITRE ATT&CK Framework: A Deep Dive

## 1. Executive Summary

The MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge) framework is arguably the most important development in the history of cybersecurity threat intelligence. It serves as the globally recognized *lingua franca* for offensive and defensive security professionals. 

Before ATT&CK, the cybersecurity industry lacked a common, standardized taxonomy. Defenders would talk about "advanced persistence," while intelligence feeds discussed "registry key modifications," and vendors sold vaguely defined "next-gen protection." ATT&CK unified this disjointed language by categorizing *why* an adversary acts (Tactics), *how* they achieve it (Techniques), and the specific implementations (Procedures). For Vulnerability Assessment and Penetration Testing (VAPT), SOC Operations, and Cyber Threat Intelligence, ATT&CK is the definitive blueprint for adversary emulation and detection engineering.

## 2. Core Structure of the Framework

The framework is structured as a series of matrices tailored to specific domains (Enterprise, Mobile, ICS). The most commonly used is the Enterprise matrix, which covers Windows, macOS, Linux, Cloud (AWS, Azure, GCP), and Network environments.

### 2.1. Tactics (The "Why")
Tactics represent the adversary's technical goals or objectives. They are the columns of the matrix. There are currently 14 tactics in the Enterprise matrix, representing a roughly linear progression of an attack (though adversaries often bounce non-linearly between them):
1. **Reconnaissance**: Gathering information for future operations.
2. **Resource Development**: Establishing resources to support operations (e.g., buying domains).
3. **Initial Access**: Breaking into the network (e.g., phishing).
4. **Execution**: Running malicious code.
5. **Persistence**: Maintaining access across restarts.
6. **Privilege Escalation**: Gaining higher-level permissions.
7. **Defense Evasion**: Avoiding detection.
8. **Credential Access**: Stealing account names and passwords.
9. **Discovery**: Understanding the environment.
10. **Lateral Movement**: Moving through the environment to other systems.
11. **Collection**: Gathering data of interest.
12. **Command and Control (C2)**: Communicating with compromised systems.
13. **Exfiltration**: Stealing the data.
14. **Impact**: Manipulating, interrupting, or destroying systems/data.

### 2.2. Techniques (The "How")
Techniques are the specific methods an adversary uses to achieve a tactical objective. Each tactic contains multiple techniques.
- *Example*: To achieve the Tactic of **Initial Access** (TA0001), an adversary might use the Technique of **Phishing** (T1566) or **Exploit Public-Facing Application** (T1190).

### 2.3. Sub-Techniques (The Specific "How")
Sub-techniques provide a more granular, detailed description of a technique. They were introduced to prevent the framework from becoming too bloated at the technique level.
- *Example*: Under the Technique of **Phishing** (T1566), sub-techniques include:
  - T1566.001: Spearphishing Attachment
  - T1566.002: Spearphishing Link
  - T1566.003: Spearphishing via Service

### 2.4. Procedures (The "Exact Implementation")
Procedures are the highly specific actions, command-line arguments, or tools used by a specific threat actor to execute a technique. 
- *Example*: "APT29 used a heavily obfuscated PowerShell script to execute Cobalt Strike beacon within memory, leveraging the Spearphishing Attachment sub-technique."

### ASCII Diagram: The ATT&CK Structure

```text
+-------------------------------------------------------------+
|                     MITRE ATT&CK MATRIX                     |
+-------------------------------------------------------------+
| TACTIC: Initial Access  | TACTIC: Execution                 |
| (Objective: Get In)     | (Objective: Run Code)             |
+-------------------------+-----------------------------------+
| TECHNIQUE: Phishing     | TECHNIQUE: Command/Script Interp. |
| (ID: T1566)             | (ID: T1059)                       |
|                         |                                   |
|   +-> SUB-TECHNIQUE:    |   +-> SUB-TECHNIQUE:              |
|       Attachment        |       PowerShell                  |
|       (ID: T1566.001)   |       (ID: T1059.001)             |
|                         |                                   |
|       * PROCEDURE:      |       * PROCEDURE:                |
|         APT29 sends     |         FIN7 runs base64          |
|         macro-enabled   |         encoded script via        |
|         Word doc.       |         powershell.exe -enc       |
+-------------------------+-----------------------------------+
```

## 3. Beyond TTPs: Mitigations and Data Sources

ATT&CK is not merely a catalog of bad things; it provides actionable defensive guidance for every single technique.

- **Mitigations**: Security concepts, configurations, and technologies that can prevent a technique from being successfully executed in the first place. For example, the mitigation for *Spearphishing Attachment* includes Antivirus/Antimalware (M1049), User Training (M1017), and Restricting Web-Based Content (M1021).
- **Data Sources**: The specific system telemetry required to detect a technique. If you are not collecting the right data, you cannot write a detection rule. For *PowerShell Execution*, the required data sources include `Command: Command Execution` and `Process: Process Creation`. This tells data engineers exactly what logs to send to the SIEM.

## 4. Operationalizing MITRE ATT&CK in VAPT and SOC

MITRE ATT&CK has revolutionized offensive security testing and defensive operations.

### 4.1. Adversary Emulation (Red Teaming)
Instead of throwing generic exploits at a network (traditional pentesting), Red Teams use CTI to profile a specific threat actor, map their known behaviors to the ATT&CK matrix, and execute a customized emulation plan. This tests whether the Blue Team can detect the specific TTPs of a relevant adversary, providing a realistic assessment of defensive posture.

### 4.2. ATT&CK Navigator and Heatmapping
Defenders use the open-source ATT&CK Navigator tool to create visual heatmaps of their defensive posture and coverage.
- **Red Cells**: Techniques the organization has zero visibility or protection against.
- **Yellow Cells**: Techniques where some telemetry exists, but detections are brittle or prone to false positives.
- **Green Cells**: Techniques with high-confidence SIEM alerts, automated SOAR playbooks, and strong preventative controls.

### 4.3. Threat Hunting Hypothesis Generation
Threat hunters use the matrix to proactively search for undetected intrusions. A hunter might say: "Looking at our Navigator heatmap, we have excellent coverage of Initial Access, but poor coverage of Defense Evasion. I will formulate a hypothesis to hunt for signs of Process Injection (T1055) and Token Manipulation (T1134) in our environment this week."

## 5. Real-World Attack Scenario: Mapping an Incident

### The Scenario: The NotPetya Attack

Let's map the infamous NotPetya wiper attack to the ATT&CK framework to understand how an attack is deconstructed:

1. **Initial Access**: The adversary compromised the update mechanism of M.E.Doc, a Ukrainian accounting software. 
   - *Mapping*: **Supply Chain Compromise (T1195)**.
2. **Execution & Privilege Escalation**: The malicious payload executed as a privileged process because the M.E.Doc software inherently required local admin rights.
   - *Mapping*: **Valid Accounts (T1078)** and **Execution through API (T1106)**.
3. **Credential Access**: The malware used a customized version of Mimikatz to dump credentials from memory to facilitate rapid spread.
   - *Mapping*: **OS Credential Dumping: LSASS Memory (T1003.001)**.
4. **Lateral Movement**: NotPetya aggressively spread across the network using the stolen credentials and the EternalBlue exploit (CVE-2017-0144).
   - *Mapping*: **Remote Services: SMB/Windows Admin Shares (T1021.002)** and **Exploitation of Remote Services (T1210)**.
5. **Impact**: The malware encrypted the Master File Table (MFT) and modified the Master Boot Record (MBR), rendering the systems unbootable and permanently destroying data.
   - *Mapping*: **Data Destruction (T1485)** and **Disk Wipe (T1561)**.

By mapping an incident in this manner, organizations can quickly identify where in the attack chain their defenses failed and prioritize engineering efforts to disrupt similar attacks in the future.

## 6. Limitations of ATT&CK

While exceptionally powerful, ATT&CK is not a silver bullet and has known limitations:
- **Complexity**: The sheer volume of techniques (hundreds of sub-techniques) can overwhelm immature security teams.
- **Abstraction**: It is a framework, not a step-by-step tutorial. Knowing that an adversary uses "Process Injection" does not give a defender the exact YARA or Sigma rule needed to detect it.
- **Lag**: ATT&CK is based entirely on *observed* in-the-wild behavior. It inherently lags behind bleeding-edge zero-day techniques that have not yet been publicly reported or discovered.

## 7. Chaining Opportunities

- The intelligence gathered and structured using the [[04 - Threat Modeling Frameworks Diamond Model]] (specifically the Capability node) is directly translated into MITRE ATT&CK techniques.
- [[01 - Introduction to Cyber Threat Intelligence CTI]] explains the foundation of why standardizing on a taxonomy like ATT&CK is crucial for escaping the "Pyramid of Pain."
- Developing MITRE ATT&CK mappings and detection rules falls firmly into the Tactical layer described in [[03 - Tactical vs Operational vs Strategic Intelligence]].

## 8. Related Notes

- [[01 - Introduction to Cyber Threat Intelligence CTI]]
- [[02 - The Intelligence Cycle Direction Collection Processing]]
- [[03 - Tactical vs Operational vs Strategic Intelligence]]
- [[04 - Threat Modeling Frameworks Diamond Model]]
