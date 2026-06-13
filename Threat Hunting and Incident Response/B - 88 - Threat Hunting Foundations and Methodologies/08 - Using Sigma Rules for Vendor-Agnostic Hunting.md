---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.08 Using Sigma Rules for Vendor-Agnostic Hunting"
---

# 88.08 Using Sigma Rules for Vendor-Agnostic Hunting

## 1. Introduction to Sigma
In the world of Threat Hunting and Detection Engineering, Security Operations Centers (SOCs) face a massive problem: **vendor lock-in and language fragmentation**. If a threat researcher discovers a new technique used by a threat actor, they might write a detection query using Splunk's SPL (Search Processing Language). If your organization uses ElasticSearch (KQL), Microsoft Sentinel (KQL), or CrowdStrike (FQL), that Splunk query is useless to you without manual translation.

Enter **Sigma**. Sigma is an open-source, generic, and standardized signature format for log events. Just as Snort is the standard for network packets and YARA is the standard for file analysis, Sigma is the standard for log-based behavioral detection. It provides a vendor-agnostic way to describe relevant log events in a structured YAML format.

## 2. Why Sigma is Revolutionary for Threat Hunters
- **Portability:** A single Sigma rule can be translated into Splunk, ElasticSearch, QRadar, ArcSight, Microsoft Sentinel, CrowdStrike, and dozens of other SIEM/EDR platforms automatically.
- **Collaboration:** Because it is vendor-neutral, the global security community can share Sigma rules seamlessly. Repositories like the official SigmaHQ GitHub contain thousands of community-vetted detection rules.
- **Detection as Code (DaC):** Sigma allows detection logic to be stored in version control systems (like Git), reviewed via Pull Requests, and automatically deployed to SIEMs via CI/CD pipelines. This brings software engineering rigor to security operations.
- **Longevity:** If an organization decides to migrate from Splunk to ElasticSearch, they do not need to rewrite years of custom detection engineering. They simply run their existing Sigma rules through the compiler with a new target backend.

## 3. The Anatomy of a Sigma Rule
A Sigma rule is a YAML document divided into several key sections.

### 3.1 Meta Information
Contains tracking and contextual data for analysts and documentation.
- `title`: A short, descriptive name for the rule (e.g., `Suspicious Process Spawned by Word`).
- `id`: A unique UUID for tracking the rule across its lifecycle.
- `status`: Indicates maturity (`experimental`, `test`, `stable`).
- `description`: Detailed explanation of what the rule detects and why it matters.
- `author`, `date`, `references`.
- `tags`: Critical for mapping to frameworks (e.g., mapping to MITRE ATT&CK like `attack.t1059` or `attack.execution`).

### 3.2 Log Source Definition
Defines *where* the rule should look for data. The compiler uses this to determine which indexes to query in the SIEM.
- `category`: Broad classification (e.g., `process_creation`, `network_connection`, `file_event`).
- `product`: The OS or application (e.g., `windows`, `linux`, `aws`).
- `service`: Specific log providers (e.g., `sysmon`, `security`, `cloudtrail`).

### 3.3 Detection Logic (The Core)
This section contains the actual matching criteria, defined as a set of key-value maps or lists, followed by a `condition` that applies Boolean logic.
- **Search Identifiers:** Named blocks of logic (e.g., `selection`, `filter`, `known_good`).
- **Modifiers:** Sigma allows modifiers on fields, such as `|contains`, `|startswith`, `|endswith`, `|re` (regex), or `|base64`.
- **Condition:** The logical combination (e.g., `selection and not filter`, `1 of them`, `all of them`).

## 4. A Concrete Sigma Rule Example
Let's look at a rule designed to detect the execution of reconnaissance tools (`whoami`, `systeminfo`) out of a web server process—a classic indicator of a webshell execution.

```yaml
title: Suspicious Execution from Web Server Process
id: 12345678-abcd-1234-abcd-1234567890ab
status: stable
description: Detects command line tools commonly executed by webshells spawned by web server processes.
author: Threat Hunter
date: 2023-10-25
tags:
    - attack.execution
    - attack.t1059.003
logsource:
    category: process_creation
    product: windows
detection:
    web_servers:
        ParentImage|endswith:
            - '\w3wp.exe'          # Microsoft IIS
            - '\httpd.exe'         # Apache
            - '\nginx.exe'         # Nginx
            - '\tomcat*.exe'       # Apache Tomcat
    suspicious_commands:
        Image|endswith:
            - '\whoami.exe'
            - '\systeminfo.exe'
            - '\cmd.exe'
            - '\powershell.exe'
    filter_legit:
        CommandLine|contains:
            - 'iisreset'           # Known legitimate admin task
    condition: web_servers and suspicious_commands and not filter_legit
falsepositives:
    - Highly customized web applications that legitimately call system tools (rare).
level: high
```

## 5. The Sigma Compiler (pySigma / Sigmac)
To use a Sigma rule, you must compile it. The compiler takes the generic YAML and a **backend target**, and outputs the specific query language for your tool. It also relies on a **mapping configuration** to map generic Sigma fields (like `Image`) to your SIEM's specific schema (like `Process.Name` or `winlog.event_data.Image`).

For example, compiling the rule above for Splunk:
`sigma convert -t splunk -p sysmon_windows rule.yml`
**Output (Splunk SPL):**
```spl
sourcetype="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventCode=1 
(ParentImage="*\\w3wp.exe" OR ParentImage="*\\httpd.exe" OR ParentImage="*\\nginx.exe" OR ParentImage="*\\tomcat*.exe") 
AND (Image="*\\whoami.exe" OR Image="*\\systeminfo.exe" OR Image="*\\cmd.exe" OR Image="*\\powershell.exe") 
NOT (CommandLine="*iisreset*")
```

Compiling the exact same rule for ElasticSearch:
`sigma convert -t elasticsearch -p ecs rule.yml`
**Output (Elastic KQL):**
```kql
event.category:"process" AND process.parent.executable:(*\\w3wp.exe OR *\\httpd.exe OR *\\nginx.exe OR *\\tomcat*.exe) 
AND process.executable:(*\\whoami.exe OR *\\systeminfo.exe OR *\\cmd.exe OR *\\powershell.exe) 
AND NOT process.command_line:*iisreset*
```

## 6. Real-World Attack Scenario

### The Scenario: Rapid Response to a Zero-Day Vulnerability
A critical zero-day vulnerability (e.g., Log4Shell, ProxyLogon, or a new Atlassian Confluence RCE) drops on Twitter on a Friday night. Proof-of-concept (PoC) code is published simultaneously.

**Without Sigma (The Legacy Way):**
The SOC team scrambles. The threat intelligence analyst reads the PoC, understands the behavior, and tries to write an ArcSight rule. They struggle with ArcSight syntax. Meanwhile, the EDR team tries to write a custom CrowdStrike IOA. The team operating Microsoft Sentinel tries to write KQL. They are operating in silos, wasting crucial hours figuring out query syntax, debugging parentheses, and testing field names rather than hunting.

**With Sigma (The Modern Way):**
1. A threat researcher on GitHub analyzes the PoC and writes a generic Sigma rule detecting the specific process ancestry anomaly caused by the exploit (e.g., `java.exe` spawning `bash`).
2. They push the rule to the global SigmaHQ repository.
3. Your organization's CI/CD pipeline automatically pulls the latest SigmaHQ updates.
4. The Python-based Sigma compiler (`pySigma`) automatically translates the rule into Splunk SPL for the primary SIEM, KQL for the Azure Sentinel instance, and a custom format for the EDR.
5. The rules are deployed via API within 15 minutes of the rule being published globally.
6. The Threat Hunt team immediately runs the compiled queries across the last 30 days of historical data to verify if the organization was compromised before the zero-day was public, while the SOC monitors the live alerts.

## 7. ASCII Diagram: Sigma Pipeline Architecture

```text
[ Threat Intelligence / Researchers ] ---> Write YAML ---> [ Sigma Rule (.yml) ]
                                                                |
                                                                v
                                                       [ Version Control (Git) ]
                                                                |
                                                                | (CI/CD Pipeline triggers)
                                                                v
   [ Configuration / Field Mapping ] ---------------> [ Sigma Compiler (pySigma) ]
   (Maps generic "Image" to specific                      |          |          |
    SIEM schema fields like ECS)                          |          |          |
                                                          |          |          |
                      /-----------------------------------/          |          \-----------\
                     v                                               v                      v
             Target: Splunk                                  Target: Elastic              Target: CrowdStrike
             Query: SPL                                      Query: KQL                   Query: FQL
                     |                                               |                      |
                     v                                               v                      v
             [ Splunk SIEM ]                                 [ ELK Stack ]            [ Falcon EDR ]
             (Live Alerting &                                (Log Archiving)          (Endpoint Blocking)
              Retro-Hunting)
```

## 8. Chaining Opportunities
- **[[06 - The Pyramid of Pain in Hunting]]**: Sigma rules naturally live at the top of the pyramid. They are designed to describe TTPs and tool behaviors, rarely relying on hardcoded IPs or hashes.
- **[[07 - Baseline Establishment and Anomaly Detection]]**: While Sigma is primarily for signature-based behavioral detection, the `filter` blocks in Sigma rules rely heavily on knowing your baseline to filter out known-good behavior (tuning).
- **[[09 - Threat Hunting Maturity Model THMM]]**: Adopting Sigma and Detection-as-Code is a hallmark of transitioning from Level 2 (Procedural) to Level 3 (Innovative) and Level 4 (Leading) in the Threat Hunting Maturity Model.

## 9. Related Notes
- [[18 - Detection as Code (DaC) Principles]]
- [[21 - YARA Rule Development for Malware Analysis]]
- [[28 - Automating Hunt Operations with CI/CD]]
- [[33 - Translating MITRE ATT&CK to Detection Logic]]
- [[45 - Writing Custom Sysmon Configurations]]
