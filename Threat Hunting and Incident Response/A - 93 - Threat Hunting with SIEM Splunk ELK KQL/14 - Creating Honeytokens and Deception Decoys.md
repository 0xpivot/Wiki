---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.14 Creating Honeytokens and Deception Decoys"
---

# 93.14 Creating Honeytokens and Deception Decoys

## Table of Contents
1. [Introduction to Deception Technology](#introduction-to-deception-technology)
2. [The "Zero False Positive" Paradigm](#the-zero-false-positive-paradigm)
3. [Deception Architecture and Data Flow](#deception-architecture-and-data-flow)
4. [Types of Honeytokens and Implementation](#types-of-honeytokens-and-implementation)
    - [Decoy Credentials (Honey Accounts)](#decoy-credentials-honey-accounts)
    - [Fake Service Principal Names (SPNs)](#fake-service-principal-names-spns)
    - [Honey Files and Directories](#honey-files-and-directories)
    - [AWS/Azure Canary Tokens](#awsazure-canary-tokens)
5. [SIEM Integration and High-Priority Alerting](#siem-integration-and-high-priority-alerting)
6. [Deployment Strategies and Pitfalls](#deployment-strategies-and-pitfalls)
7. [Real-World Attack Scenario](#real-world-attack-scenario)
8. [Chaining Opportunities](#chaining-opportunities)
9. [Related Notes](#related-notes)

## 1. Introduction to Deception Technology
Traditional security architecture (firewalls, EDR, IAM) operates on a "keep the bad guys out" methodology. Deception technology operates on the assumption that the perimeter will inevitably be breached. Instead of building taller walls, deception involves placing landmines and traps—honeytokens, decoy files, fake credentials, and phantom hosts—throughout the internal environment.

The goal is to trick the attacker into interacting with fake assets during their reconnaissance and lateral movement phases, thereby instantly revealing their presence.

## 2. The "Zero False Positive" Paradigm
The fundamental and most powerful advantage of deception technology is its **Zero False Positive** nature. 

If you write a SIEM rule to detect `cmd.exe` execution, you will inevitably catch legitimate system administrators troubleshooting servers. However, legitimate users have absolutely no business reason to access a hidden database credentials file explicitly named `backup_db_passwords.txt` located deep in a deprecated network share. Therefore, *any* interaction with a honeytoken—whether reading a file, querying a fake user, or attempting to use a decoy AWS key—is, by definition, unauthorized, highly anomalous, and actionable immediately.

## 3. Deception Architecture and Data Flow

```text
+-------------------+                                      +-------------------+
|  Internal Network |                                      |   SIEM / SOC      |
|                   |                                      |                   |
|  +-------------+  |  Interaction (Read/Login/Query)      |  +-------------+  |
|  |  Production |<-|------------------+                   |  | Alerting    |  |
|  |  Server     |  |                  |                   |  | Engine      |  |
|  +-------------+  |                  |                   |  +-------------+  |
|        |          |                  |                   |         ^         |
|   +----------+    |                  |                   |         |         |
|   | Decoy    |    |                  |                   |         |         |
|   | AWS Keys |    |                  |                   |         |         |
|   +----------+    |                  |                   |         |         |
|                   |                  |                   |         |         |
|  +-------------+  |                  |                   |         |         |
|  | Active      |  |   Logs Forwarded (Event 4625/4663)   |         |         |
|  | Directory   |--|--------------------------------------|---------+         |
|  +-------------+  |                                      |                   |
|        |          |                                      |                   |
|   +----------+    |                                      |                   |
|   | Fake SPN |    |                                      |                   |
|   | Account  |    |                                      |                   |
|   +----------+    |                                      |                   |
+-------------------+                                      +-------------------+
```

## 4. Types of Honeytokens and Implementation

### Decoy Credentials (Honey Accounts)
Creating entirely fake user accounts within Active Directory that appear highly privileged but have no actual rights.
- **Setup:** Create an AD account named `svc_sql_backup` or `admin_temp`. Set a complex password, but critically, set the "Logon Workstations" restriction to a null value or deny it interactive logon rights entirely via Group Policy.
- **Monitoring:** Monitor the SIEM for any Kerberos ticket requests (Event ID 4768, 4769) or failed logon attempts (Event ID 4625) targeting this specific account.
- **Value:** Instantly detects attackers attempting password spraying, Kerberoasting, or using credential dumping tools like Mimikatz (if the decoy credentials are artificially injected into LSASS memory on endpoints).

### Fake Service Principal Names (SPNs)
Attackers performing Kerberoasting query AD for accounts with associated SPNs, request service tickets, and attempt to crack the ticket hashes offline to obtain plaintext passwords.
- **Setup:** Assign a highly enticing SPN to a decoy account using the command line:
  `setspn -A MSSQLSvc/db-prod.domain.local:1433 svc_decoy_db`
- **Monitoring:** Alert in the SIEM on Event ID 4769 (Kerberos Service Ticket Requested) where the `Target UserName` is `svc_decoy_db`. 

### Honey Files and Directories
Placing enticing, booby-trapped files on public file shares, SharePoint sites, or user desktops.
- **Setup:** Create files named `passwords.xlsx`, `aws_root_keys.txt`, `Q3_Financials_Draft.pdf`, or `vpn_configs.zip`.
- **Implementation:** Enable Windows Object Access Auditing. Right-click the file -> Properties -> Security -> Advanced -> Auditing. Add the "Everyone" group and select "Read" auditing (SACLs).
- **Monitoring:** Alert on Event ID 4663 (An attempt was made to access an object) where the `Object Name` strictly matches the honey file path.

### AWS/Azure Canary Tokens
Fake cloud access keys strategically placed in `.aws/credentials` files, internal Git repositories, or Slack channels to detect developer environment compromise.
- **Setup:** Generate an AWS Access Key for an IAM user that has a restrictive policy attached denying *all* actions. Ensure AWS CloudTrail logging is enabled.
- **Monitoring:** Monitor AWS CloudTrail for *any* API calls attempting to authenticate using this specific Access Key ID.

## 5. SIEM Integration and High-Priority Alerting

To make honeytokens effective, the SIEM must be configured to bypass standard triage queues and generate critical alerts instantly upon interaction.

**Splunk SPL for Honey Account Logon Attempt:**
```spl
index=windows sourcetype=WinEventLog:Security (EventCode=4624 OR EventCode=4625) 
TargetUserName IN ("svc_decoy_admin", "temp_db_admin", "backup_svc_fake")
| stats count by _time, src_ip, TargetUserName, EventCode, WorkstationName
| eval Alert_Severity="CRITICAL", Description="Zero-False-Positive: Interaction with AD Honey Account Detected. Immediate Isolation Required."
| table _time, src_ip, TargetUserName, WorkstationName, Alert_Severity
```

**KQL (Azure Sentinel) for AWS Canary Token Interaction:**
```kql
AWSCloudTrail
| where UserIdentityAccessKeyId in ("AKIAIOSFODNN7EXAMPLE", "AKIAFAKEKEY123456789") // The Decoy Keys
| project TimeGenerated, SourceIpAddress, EventName, UserAgent, RecipientAccountId, ErrorMessage
| extend AlertName = "CRITICAL: AWS Canary Token Triggered - Potential Codebase or Endpoint Compromise"
```

## 6. Deployment Strategies and Pitfalls
- **Avoid Pattern Predictability:** Do not name all decoy accounts with a `decoy_` or `honey_` prefix. Sophisticated attackers review AD dumps and easily spot patterns. Blend them seamlessly into your organization's existing naming conventions.
- **Maintain Freshness:** A honey file modified 4 years ago looks highly suspicious to an attacker. Create an automated script to occasionally "touch" or update the metadata of honey files so they appear actively used.
- **Silence to Legitimate Scanners:** Ensure vulnerability scanners (Nessus/Qualys), SIEM log collectors, and backup agents are strictly allowlisted. If your enterprise backup software reads `passwords.xlsx` every night at 2 AM, it will trigger the honeytoken, causing severe alert fatigue and destroying the "Zero False Positive" advantage.

## 7. Real-World Attack Scenario

### Scenario: Catching a Ransomware Operator Pre-Encryption
**Context:** An affiliate for a major Ransomware-as-a-Service (RaaS) group gains access to an internal enterprise network via a phished VPN credential. Their standard playbook involves network discovery, lateral movement to a Domain Controller, and broad file exfiltration prior to deploying the encryptor payload.

**The Setup:**
Months prior, the SOC seeded a hidden but accessible network file share named `\\fileserver\finance_archive$` and placed a file named `Crypto_Wallet_Seeds_2024.txt` inside it. A Windows SACL was applied to log read access to the SIEM.

**The Attack Execution:**
1. The attacker authenticates via the VPN and immediately runs `BloodHound` and `Advanced IP Scanner` to map the network.
2. They discover the `\\fileserver\finance_archive$` share.
3. Searching for high-value data to extort the company (double extortion), they navigate to the share and open `Crypto_Wallet_Seeds_2024.txt` to copy the contents.
4. The file read triggers a Windows Security Event ID 4663, which is instantly ingested by Splunk.

**The Detection and Response:**
The SIEM instantly flags this event. Because it is a honeytoken, it bypasses normal queue triage and pages the on-call responder with a `P1 - CRITICAL` alert. Within 5 minutes, the SOC utilizes EDR integration to isolate the attacker's endpoint from the network, revokes the compromised VPN session, and successfully prevents the deployment of the ransomware payload. The deception mechanism caught the attacker during the reconnaissance/exfiltration phase, averting a multi-million dollar incident.

## 8. Chaining Opportunities
- Interactions logged by honeytokens should be the foundation of the high-priority alerts designed in `[[13 - Designing High-Fidelity Alerting Rules]]`.
- When a honeytoken fires, it provides the exact pivot point (Source IP, User Account) to launch a deep-dive threat hunt using `[[11 - Using Jupyter Notebooks for Threat Hunting]]`.

## 9. Advanced Honeytoken Concepts

### Network-Level Decoys (Tarpits)
Beyond just fake files and accounts, advanced deception involves network-level tarpits. A tarpit is a phantom host designed to deliberately slow down an attacker's automated scanning tools (like Nmap or Masscan).
- **How it works:** When the attacker scans a subnet containing a tarpit, the tarpit responds to SYN packets but artificially delays the TCP handshake or holds the HTTP connection open indefinitely without sending data.
- **Value:** This drastically inflates the time required for network reconnaissance, buying the Blue Team precious hours to react to the initial alert while the attacker's tools hang, awaiting a response.

### Honey-Databases
Deploying a fake SQL server filled with synthetic data (e.g., `customers_cc_data`).
- **Setup:** Stand up a lightweight Docker container running MySQL or PostgreSQL. Populate it with thousands of rows of randomly generated PII (fake names, invalid credit card numbers).
- **Monitoring:** Monitor for any inbound network connections on port 3306 or 5432. Alert immediately on successful authentications or `SELECT *` queries.
- **Attribution & Intelligence:** If the synthetic "credit card numbers" are later found dumped on a dark web forum, the organization has instant, undeniable proof of exactly what data was exfiltrated and from which decoy database.

### Deception in the CI/CD Pipeline
Modern attackers increasingly target the software supply chain. Placing honeytokens in DevOps environments is critical.
- **Honey-Tokens in Git:** Commit fake API keys to a private, deprecated repository. If an attacker compromises a developer's endpoint and scrapes their local Git history, they will find the key.
- **Honey-Pipelines:** Create a Jenkins or GitLab CI job named `Deploy_Prod_Secrets`. Monitor the job's execution logs. Any manual trigger of this job is an immediate red flag indicating unauthorized access to the DevOps infrastructure.

## 10. Glossary of Deception Terminology
- **Breadcrumb:** A clue left on a real endpoint designed to subtly lead the attacker toward a honeytoken or decoy system (e.g., a mapped network drive pointing to a fake file server, or a saved RDP connection file).
- **Decoy System:** A full operating system running inside a VM or container, existing solely to be attacked. Unlike a honeypot (which is often internet-facing to catch automated scanners), decoys are usually placed on the internal network to catch lateral movement.
- **Lure:** An enticing piece of information (like a file named `passwords.txt`) that actively tricks the attacker into interacting with it.
- **High-Interaction Honeypot:** A system that provides a real OS and real services for the attacker to interact with, allowing defenders to capture their exact TTPs, uploaded malware, and post-exploitation frameworks.
- **Low-Interaction Honeypot:** A system that simply emulates a service (e.g., a python script listening on port 22 that logs connection attempts but doesn't provide an actual SSH shell). They are less risky but provide less intelligence.

## 11. Related Notes
- `[[11 - Using Jupyter Notebooks for Threat Hunting]]`
- `[[12 - Machine Learning for Log Anomaly Detection]]`
- `[[13 - Designing High-Fidelity Alerting Rules]]`
- `[[15 - Case Study Tracking APT29 across a SIEM]]`
