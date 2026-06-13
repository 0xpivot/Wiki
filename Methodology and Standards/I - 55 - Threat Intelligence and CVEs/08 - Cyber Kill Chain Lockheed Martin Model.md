---
tags: [threat-intel, cve, research, vapt]
difficulty: intermediate
module: "55 - Threat Intelligence and CVEs"
topic: "55.08 Cyber Kill Chain Lockheed Martin Model"
---

# The Cyber Kill Chain: Lockheed Martin Intelligence-Driven Defense

## 1. Introduction to the Cyber Kill Chain

Developed by Lockheed Martin in 2011, the Cyber Kill Chain framework is part of the Intelligence-Driven Defense model for identification and prevention of cyber intrusions activity. The model identifies what the adversaries must complete in order to achieve their objective. 

The core philosophy behind the Kill Chain is that cyber attacks are not magic; they are methodical, step-by-step processes. If a defender can break the adversary's chain at *any* point, the entire attack fails. This shifts the defender's mindset from "I must block everything perfectly" to "I only need to stop them once before they reach their final objective."

While newer frameworks like MITRE ATT&CK provide a more granular, tactical matrix of behaviors, the Lockheed Martin Cyber Kill Chain remains the foundational strategic model for understanding the lifecycle of a targeted cyber attack, particularly Advanced Persistent Threats (APTs).

## 2. The Seven Phases of the Cyber Kill Chain

The framework is divided into seven sequential phases. 

### 2.1 Phase 1: Reconnaissance
The adversary researches, identifies, and selects targets. This phase can be passive or active.
- **Passive:** Open Source Intelligence (OSINT) gathering, analyzing LinkedIn for employee names, parsing WHOIS records, or reviewing Shodan data.
- **Active:** Port scanning, web application vulnerability scanning, or interacting with company DNS servers.
- **Objective:** Build a target profile, identify the external attack surface, and select the optimal entry point.

### 2.2 Phase 2: Weaponization
The adversary couples a remote access trojan (RAT) or backdoor with an exploitable vulnerability into a deliverable payload.
- **Action:** This typically happens within the adversary's own infrastructure. They might create a malicious PDF (the weapon) containing an exploit for Adobe Reader (the vulnerability) that drops a reverse shell (the payload).
- **Objective:** Prepare the cyber weapon for delivery.

### 2.3 Phase 3: Delivery
Transmission of the weapon to the targeted environment.
- **Methods:** Spearphishing emails, watering hole attacks (compromising a website the target frequents), USB drops, or direct exploitation of an internet-facing web server.
- **Objective:** Cross the perimeter of the target's network.

### 2.4 Phase 4: Exploitation
After delivery, the weapon's code is triggered.
- **Action:** Exploiting an application or operating system vulnerability, or leveraging a user to execute malicious code (e.g., enabling macros).
- **Objective:** Achieve initial code execution on a target system.

### 2.5 Phase 5: Installation
The weapon installs a backdoor or persistence mechanism on the victim's system.
- **Action:** Installing a web shell, creating a scheduled task, modifying registry run keys, or injecting code into a legitimate process (`explorer.exe`).
- **Objective:** Maintain access to the environment even if the system is rebooted or the initial vulnerability is patched.

### 2.6 Phase 6: Command and Control (C2)
The compromised system establishes communication with the adversary's infrastructure.
- **Action:** The installed backdoor reaches out via HTTP, DNS, or custom protocols to a C2 server for instructions.
- **Objective:** Establish a two-way communication channel ("hands-on keyboard" access).

### 2.7 Phase 7: Actions on Objectives
The adversary accomplishes their original goals.
- **Action:** Data exfiltration, data destruction (ransomware), lateral movement to other systems, or disruption of services.
- **Objective:** The culmination of the attack.

## 3. Visualizing the Kill Chain and Defensive Actions (ASCII Diagram)

Lockheed Martin pairs the Kill Chain with a "Courses of Action" matrix. For each phase, defenders can employ six distinct actions: Detect, Deny, Disrupt, Degrade, Deceive, and Destroy.

```text
+-----------------------------------------------------------------------------------+
|                        THE CYBER KILL CHAIN VS. DEFENSES                          |
+-----------------------------------------------------------------------------------+
|     PHASE        |   ATTACKER ACTION        |        DEFENSIVE COUNTERMEASURE     |
+------------------+--------------------------+-------------------------------------+
| 1. RECON         | OSINT, Shodan, Scans     | Web Analytics, Threat Intel,        |
|                  |                          | Firewall Blacklists (Deny)          |
+------------------+--------------------------+-------------------------------------+
|                  |                          |                                     |
|        ||        |                          |                                     |
|        \/        |                          |                                     |
+------------------+--------------------------+-------------------------------------+
| 2. WEAPONIZATION | Build maldoc with RAT    | YARA signatures, Threat Hunting     |
|                  |                          | (Detect in the wild)                |
+------------------+--------------------------+-------------------------------------+
|                  |                          |                                     |
|        ||        |                          |                                     |
|        \/        |                          |                                     |
+------------------+--------------------------+-------------------------------------+
| 3. DELIVERY      | Spearphishing Email      | Email Gateway, Proxy Filters,       |
|                  |                          | DNS Sinkholing (Deny/Disrupt)       |
+------------------+--------------------------+-------------------------------------+
|                  |                          |                                     |
|        ||        |                          |                                     |
|        \/        |                          |                                     |
+------------------+--------------------------+-------------------------------------+
| 4. EXPLOITATION  | Trigger buffer overflow  | Patch Management, ASLR, DEP,        |
|                  |                          | EDR/AV heuristics (Deny)            |
+------------------+--------------------------+-------------------------------------+
|                  |                          |                                     |
|        ||        |                          |                                     |
|        \/        |                          |                                     |
+------------------+--------------------------+-------------------------------------+
| 5. INSTALLATION  | Registry Run Key added   | EDR Behavioral Analysis, HIPS,      |
|                  |                          | AppLocker (Detect/Deny)             |
+------------------+--------------------------+-------------------------------------+
|                  |                          |                                     |
|        ||        |                          |                                     |
|        \/        |                          |                                     |
+------------------+--------------------------+-------------------------------------+
| 6. COMMAND &     | Beacon to C2 server      | NIDS, Outbound Proxy rules,         |
|    CONTROL (C2)  | over HTTPS               | Threat Intel IP blocks (Disrupt)    |
+------------------+--------------------------+-------------------------------------+
|                  |                          |                                     |
|        ||        |                          |                                     |
|        \/        |                          |                                     |
+------------------+--------------------------+-------------------------------------+
| 7. ACTIONS ON    | Exfiltrate DB to Mega    | DLP, Network Segmentation,          |
|    OBJECTIVES    | or deploy Ransomware     | Honeypots, Zero Trust (Deceive/Deny)|
+------------------+--------------------------+-------------------------------------+
```

## 4. Strengths and Weaknesses of the Kill Chain

### 4.1 Strengths
- **Simplicity:** It is highly intuitive. Executives and non-technical stakeholders easily grasp the concept of "breaking the chain."
- **Strategic Focus:** It forces organizations to look beyond the perimeter. If Delivery fails, how do we catch them at C2?
- **Metric Generation:** Security teams can measure their effectiveness by tracking *where* in the chain they most frequently stop attacks.

### 4.2 Weaknesses and Criticisms
- **Perimeter Focus (Traditional):** The original model implies a hard perimeter. In modern cloud and zero-trust environments, "Delivery" and "Exploitation" blur significantly.
- **Insider Threats:** The model struggles to map malicious insiders, who bypass the first five phases entirely and begin at "Actions on Objectives."
- **Not Agile Enough:** Modern attacks, like living-off-the-land (LotL) or compromised supply chains, do not always fit neatly into this linear sequence.
- **Lack of Granularity:** "Actions on Objectives" is a massive bucket. The MITRE ATT&CK framework was largely created to expand upon what happens during and after phases 5, 6, and 7.

## 5. Integrating the Kill Chain into Incident Response

When an incident occurs, the SOC should attempt to reconstruct the Kill Chain.

1. **The Alert:** An EDR tool alerts on suspicious `powershell.exe` execution (Installation).
2. **Going Backwards:** The analyst investigates what spawned PowerShell. They find an instance of `winword.exe` (Exploitation). 
3. **Further Back:** They trace the Word document back to an email gateway log (Delivery). 
4. **Going Forwards:** They check network logs to see if the PowerShell script initiated any outbound connections (C2).

By tracing the chain both forwards and backwards, the incident responder ensures they have completely eradicated the threat, rather than just playing whack-a-mole with isolated alerts.

## 6. The "Unified Kill Chain"

To address the shortcomings of the Lockheed Martin model, Paul Pols created the Unified Kill Chain in 2017. It integrates the Lockheed Martin model, MITRE ATT&CK, and other models into an 18-phase process encompassing:
1. **Initial Foothold:** Gaining the first entry.
2. **Network Propagation:** Moving laterally.
3. **Action on Objectives:** Achieving the final goal.
This expanded model is increasingly used by Red Teams to structure their engagements in complex, multi-domain environments.

## 7. Expanding the Concept: The Internal Kill Chain

The traditional Lockheed Martin model assumes an external attacker targeting an enterprise perimeter. However, inside a modern Active Directory network, the Kill Chain essentially restarts once the perimeter is breached. This is often referred to as the **Internal Kill Chain**.

1. **Internal Reconnaissance:** Using `nltest`, PowerView, or BloodHound to map out domain trusts, user privileges, and local administrative groups.
2. **Internal Weaponization:** Compiling a custom version of Mimikatz or obfuscating a PowerShell script specifically designed for the internal target's EDR solution.
3. **Internal Delivery:** Moving the payload to the target system via SMB file shares, Windows Remote Management (WinRM), or WMI.
4. **Internal Exploitation:** Leveraging a misconfigured service, exploiting an internal unpatched server (e.g., PrintNightmare), or exploiting a Kerberos flaw (Roasting).
5. **Internal Installation:** Establishing lateral persistence. Creating Scheduled Tasks on internal application servers, or modifying Active Directory ACLs to ensure a backdoor exists even if passwords are reset.
6. **Internal C2:** Internal systems often cannot connect directly to the internet. Therefore, the adversary establishes an internal C2 mechanism. They might use a compromised internal server as a jump box, routing SMB named pipes internally before funneling the traffic out via a single edge node.
7. **Actions on Objectives:** Reaching the Domain Controller, extracting the `NTDS.dit` file, and completely owning the identity provider of the organization.

## 8. The Cloud Kill Chain

Cloud environments (AWS, Azure, GCP) require a massive paradigm shift in how the Kill Chain is interpreted. In the cloud, there is no "perimeter" in the traditional sense, and exploitation often focuses on misconfigurations rather than memory corruption.

### The Cloud-Adapted Phases
- **Reconnaissance:** Enumerating public S3 buckets, analyzing GitHub repositories for hardcoded AWS access keys, or querying public Route53 DNS zones.
- **Weaponization:** Crafting specialized API requests using tools like Pacu or CloudFox.
- **Delivery:** Sending the crafted API request directly to the Cloud Service Provider's endpoint. There is no email or payload to drop; the delivery is the HTTP request itself.
- **Exploitation:** Exploiting an overly permissive IAM role or an SSRF vulnerability in a hosted application to steal temporary EC2 instance metadata credentials.
- **Installation:** Creating a new hidden IAM user, generating new access keys, or modifying security group rules to allow inbound SSH from the adversary's IP.
- **Command and Control:** Accessing the AWS Management Console directly via stolen credentials, or interacting with the cloud environment via the AWS CLI. The "C2 channel" is simply normal, encrypted API traffic.
- **Actions on Objectives:** Data exfiltration from S3 buckets, destroying infrastructure (deleting EC2 instances), or deploying cryptominers via AWS Lambda functions.

By understanding how the Kill Chain adapts to different environments (Internal AD, Cloud, ICS/SCADA), VAPT professionals can tailor their assessments and their defensive recommendations to the specific architecture of their client.

---
## Chaining Opportunities
- **[[06 - MITRE ATT&CK Framework]]:** MITRE ATT&CK acts as the tactical execution manual for the strategic phases outlined in the Kill Chain, particularly from phase 4 onwards.
- **[[01 - OSINT Overview and Methodology]]:** Directly maps to the "Reconnaissance" phase of the Kill Chain.
- **[[23 - Phishing and Social Engineering]]:** The primary mechanism utilized during the "Delivery" phase.

## Related Notes
- [[11 - Red Teaming vs Penetration Testing]]
- [[15 - SIEM and SOC Operations]]
- [[50 - Malware Analysis Basics]]
