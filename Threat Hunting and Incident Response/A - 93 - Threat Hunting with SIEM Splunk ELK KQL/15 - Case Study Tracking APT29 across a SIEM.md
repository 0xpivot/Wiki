---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.15 Case Study Tracking APT29 across a SIEM"
---

# 93.15 Case Study Tracking APT29 across a SIEM

## Table of Contents
1. [Introduction to APT29 (Cozy Bear)](#introduction-to-apt29-cozy-bear)
2. [APT29 Key Tactics, Techniques, and Procedures (TTPs)](#apt29-key-tactics-techniques-and-procedures-ttps)
3. [Threat Hunting Architecture](#threat-hunting-architecture)
4. [Hunting APT29 TTPs in the SIEM](#hunting-apt29-ttps-in-the-siem)
    - [Hunting Defense Evasion: Process Renaming](#hunting-defense-evasion-process-renaming)
    - [Hunting Credential Access: Golden SAML](#hunting-credential-access-golden-saml)
    - [Hunting Lateral Movement: Malicious WMI](#hunting-lateral-movement-malicious-wmi)
5. [Detecting Stealth C2 via Legitimate Cloud Services](#detecting-stealth-c2-via-legitimate-cloud-services)
6. [Real-World Attack Scenario: The SolarWinds Supply Chain Attack](#real-world-attack-scenario-the-solarwinds-supply-chain-attack)
7. [Lessons Learned for Blue Teams](#lessons-learned-for-blue-teams)
8. [Chaining Opportunities](#chaining-opportunities)
9. [Related Notes](#related-notes)

## 1. Introduction to APT29 (Cozy Bear)
APT29 (also known widely as Cozy Bear, NOBELIUM, or Midnight Blizzard) is a highly sophisticated, state-sponsored cyber espionage group attributed to the Russian Foreign Intelligence Service (SVR). They are infamous for perpetrating the 2020 SolarWinds supply chain attack and executing highly stealthy operations targeting government agencies, diplomatic entities, think tanks, and technology organizations worldwide.

Tracking APT29 is considered the pinnacle of threat hunting. It requires moving far beyond basic IOC (Indicator of Compromise) hunting—searching for known bad IPs or file hashes—because APT29 utilizes bespoke malware and rapidly rotates infrastructure. Instead, analysts must hunt based on IOAs (Indicators of Attack) and behavioral TTPs (Tactics, Techniques, and Procedures).

## 2. APT29 Key Tactics, Techniques, and Procedures (TTPs)
Based on MITRE ATT&CK framework mapping, APT29 frequently employs the following advanced methodologies:
- **Initial Access:** Supply chain compromise (injecting backdoors into legitimate software updates), highly sophisticated spear-phishing, and password spraying against cloud identities (Azure AD).
- **Execution:** Malicious MSBuild tasks, Windows Management Instrumentation (WMI), and executing PowerShell directly in memory without invoking `powershell.exe` (using unmanaged runspaces via custom .NET assemblies).
- **Defense Evasion:** Renaming native system utilities (e.g., `adfind.exe` renamed to `update.exe`), timestomping payloads to match OS file creation dates, disabling EDR sensors, and programmatically clearing Windows Event Logs (Event ID 104).
- **Credential Access:** Extracting AD FS token signing certificates to forge cloud authentication (Golden SAML), and deeply hooking or dumping LSASS memory.
- **Command & Control (C2):** Abusing legitimate cloud services (Dropbox, Google Drive, Notion, Microsoft Graph API) to hide C2 traffic within normal enterprise TLS noise.

## 3. Threat Hunting Architecture

To catch an actor like APT29, a multi-layered telemetry architecture must be ingested into the SIEM.

```text
+-------------------+      +-------------------+      +-------------------+
|  Identity Layer   |      |  Endpoint Layer   |      |   Network Layer   |
|  (Azure AD, AD FS)|      |  (Sysmon, EDR,    |      |  (Proxy Logs,     |
|  Cloud App Sec.   |      |   PowerShell Logs)|      |   Zeek/Suricata)  |
+-------------------+      +-------------------+      +-------------------+
          |                          |                          |
          v                          v                          v
+-------------------------------------------------------------------------+
|                              SIEM (Splunk / ELK)                        |
|                                                                         |
|  +--------------------+  +--------------------+  +-------------------+  |
|  | Behavioral Rules   |  | Temporal Sequence  |  | Rare/Anomaly ML   |  |
|  | (Sigma/SPL)        |  | Analysis (EQL)     |  | (MLTK/ELK Nodes)  |  |
|  +--------------------+  +--------------------+  +-------------------+  |
+-------------------------------------------------------------------------+
                                     |
                                     v
                           +-------------------+
                           | High Confidence   |
                           | Threat Detections |
                           +-------------------+
```

## 4. Hunting APT29 TTPs in the SIEM

### Hunting Defense Evasion: Process Renaming
APT29 often renames legitimate enumeration and execution tools to evade basic detections. We hunt for this by comparing the `OriginalFileName` (extracted by Sysmon from the PE header metadata) to the actual executing process name.

**Splunk (Sysmon Event ID 1 - Process Creation):**
```spl
index=windows sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational EventCode=1
// Ensure OriginalFileName exists in the log
| where isnotnull(OriginalFileName)
// Extract just the filename from the execution path
| eval image_filename=mvindex(split(Image,"\\"),-1)
// Compare the execution name to the PE header name
| where lower(OriginalFileName) != lower(image_filename)
// Filter out legitimate variations (e.g., software installers)
| search NOT image_filename IN ("setup.exe", "install.exe")
| table _time, Computer, User, Image, OriginalFileName, CommandLine
| eval Alert_Context="Suspicious Process Renaming Detected - Potential Defense Evasion"
```
*Goal: Look for tools like `adfind.exe` renamed to `update.exe` or `svchost.exe`.*

### Hunting Credential Access: Golden SAML
During the SolarWinds campaign, APT29 stole AD FS token-signing certificates to forge SAML tokens. This allowed them to completely bypass MFA and access highly sensitive cloud resources at will.

**Hunting in Azure Sentinel (KQL):**
Look for anomalous additions of new credentials or certificates to service principals or applications, executed by unauthorized accounts.

```kql
AuditLogs
| where OperationName has "Update application – Certificates and secrets management"
   or OperationName has "Update service principal – Certificates and secrets management"
// Extract the actor performing the action
| extend Actor = tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)
// Extract the application being modified
| extend Target = tostring(TargetResources[0].displayName)
// Filter out the highly restricted service accounts that legitimately do this
| where Actor != "Azure_Automation_ServiceAccount" and Actor != "GlobalAdmin_Service"
| project TimeGenerated, OperationName, Actor, Target, ResultDescription
```

### Hunting Lateral Movement: Malicious WMI
APT29 uses WMI for stealthy remote execution without dropping standard files on disk. We hunt for `WmiPrvSE.exe` (the WMI Provider Host) spawning highly suspicious child processes.

**ELK (Elasticsearch Query Language - EQL):**
```eql
sequence by host.name with maxspan=1m
  // Match the WMI host process
  [process where event.code == "1" and process.name == "WmiPrvSE.exe"]
  // Match suspicious children spawned by WMI
  [process where event.code == "1" and process.parent.name == "WmiPrvSE.exe" 
   and process.name in ("cmd.exe", "powershell.exe", "rundll32.exe", "certutil.exe")]
```

## 5. Detecting Stealth C2 via Legitimate Cloud Services
Because APT29 routinely uses services like Microsoft Graph API, Notion, or Dropbox for Command and Control, network hunting cannot rely on domain reputation (Graph API will always have a good reputation). Instead, hunters must look for anomalous data volumes or rhythmic timing.

**Advanced Hunt Strategy:**
1. Baseline outbound traffic to `graph.microsoft.com` or `api.dropbox.com` originating from specific server subnets (servers shouldn't generally be browsing Dropbox).
2. Look for rigid, mechanical beaconing patterns (e.g., exactly every 300 seconds, 24/7, with zero variance).
3. Utilize Jupyter Notebooks to apply Machine Learning (Fast Fourier Transforms) on network flow data to detect low-and-slow periodic beaconing hidden beneath the noise of legitimate traffic.

## 6. Real-World Attack Scenario: The SolarWinds Supply Chain Attack

### Context:
In late 2020, an organization learns via a CISA alert that their SolarWinds Orion server may be compromised via a maliciously altered software update containing the Sunburst backdoor.

### The Hunt Sequence:
1. **Initial Vector Verification:** Analysts query the SIEM for Sysmon Event ID 1 where `SolarWinds.BusinessLayerHost.exe` is the parent process.
   *Finding:* The SIEM reveals `SolarWinds.BusinessLayerHost.exe` spawning `cmd.exe` and `powershell.exe` to execute heavily obfuscated scripts. This confirms the supply chain compromise.
2. **Network C2 Investigation:** Analysts pivot to enterprise proxy and DNS logs, filtering for traffic originating specifically from the Orion server over the past 6 months.
   *Finding:* The logs show anomalous DNS queries to `avsvmcloud[.]com`, the known Sunburst DGA (Domain Generation Algorithm) domain.
3. **Lateral Movement Tracking:** The attacker used the Orion server as a beachhead. Analysts search the SIEM for SMB connections and logon events originating from the Orion server's IP to critical tier-0 infrastructure.
   *Finding:* Event ID 4624 (Logon Type 3 - Network Logon) shows the Orion server accessing the primary AD FS server.
4. **Impact Assessment (The Golden SAML):** Checking AD FS event logs reveals an anomalous export of the Directory Services Restore Mode (DSRM) password and the token signing certificates.
5. **Eradication & Recovery:** The hunt proves the network is catastrophically compromised at the identity layer. Incident Response teams must take the entire environment offline for a massive, coordinated credential reset and an Active Directory rebuild from the ground up.

## 7. Lessons Learned for Blue Teams
- **Defense-in-Depth Logging is Mandatory:** Without Sysmon (specifically tracking parent-child process relationships and OriginalFileName extraction) and deep Azure AD audit logging, this entire attack chain would be completely invisible to the SOC.
- **Behavior over Signatures:** APT29 recompiles and customizes malware for every single target. Hash-based signatures fail instantly. Hunting must focus exclusively on behavioral anomalies like unusual parent processes, irregular identity management actions, and mathematically anomalous network traffic.

## 8. Chaining Opportunities
- The EQL and SPL detection queries developed during this specific hunt should be converted into permanent, high-fidelity Sigma rules as discussed in `[[13 - Designing High-Fidelity Alerting Rules]]`.
- High-value targets like AD FS servers, which are heavily targeted by APT29, should be protected with advanced deception techniques and fake SPNs detailed in `[[14 - Creating Honeytokens and Deception Decoys]]`.

## 9. Deep Dive: The Mechanics of Golden SAML
Understanding the Golden SAML attack is crucial for modern threat hunters, as it represents a massive paradigm shift from on-premise Active Directory dominance to Cloud Identity dominance.

### What is SAML?
Security Assertion Markup Language (SAML) is an open XML-based standard for exchanging authentication and authorization data between an identity provider (IdP, like AD FS, Okta, or PingIdentity) and a service provider (SP, like Microsoft 365, AWS, or Salesforce).

### The Attack Flow
1. **Compromise the IdP:** The attacker gains administrative access to the on-premise AD FS server, often via lateral movement from a compromised endpoint.
2. **Steal the Certificate:** The attacker exports the private key of the Token-Signing Certificate from the AD FS server's local certificate store.
3. **Forge the Assertion:** Using offensive tools like ADFSpoof or custom Python scripts, the attacker crafts a perfectly valid, cryptographically signed SAML response asserting they are a highly privileged cloud user (e.g., a Global Administrator or Exchange Admin).
4. **Bypass Defenses:** Because the assertion is cryptographically signed by the trusted on-premise IdP, the cloud service accepts it unconditionally. MFA is entirely bypassed because the IdP asserts that MFA was already successfully performed on-premise.

### Detection Strategies
- **Certificate Mismatches:** Monitor for SAML assertions signed with a certificate that is technically valid but differs from the primary certificate actively configured and expected by Azure AD.
- **Unusual Claim Values:** Look for forged tokens that lack standard claims usually injected by the legitimate IdP, or contain hardcoded, non-dynamic timestamps that don't align with standard token lifetimes.
- **Impossible Travel combined with IdP Auth:** Detect an authentication from a highly anomalous location (e.g., a Tor exit node or foreign IP space) that claims to have just passed on-premise AD FS authentication.

## 10. APT29 Incident Response Playbook Overview
If an APT29 compromise is suspected, standard Incident Response playbooks fail because the actor is highly patient and maintains deep persistence across multiple disjointed layers.

1. **Do NOT Evict Immediately:** If you block their initial C2 IP, they will instantly realize they are discovered, switch to a fallback stealth method (like Microsoft Graph API or steganography), and dig deeper. Monitor them silently in the SIEM to uncover the full scope of their access.
2. **Identity First Recovery:** The remediation effort must focus entirely on identity. Rebuilding endpoints and installing new EDR agents is completely useless if the adversary holds a Golden SAML certificate or a Golden Ticket, as they can simply mint new access at will.
3. **The "Big Bang" Eviction:** Remediation must happen simultaneously across the entire enterprise to prevent reinfection. Rotate the `krbtgt` password twice, revoke all active cloud refresh sessions, roll all AD FS signing certificates, and block known C2 infrastructure at the exact same moment.

## 11. Related Notes
- `[[11 - Using Jupyter Notebooks for Threat Hunting]]`
- `[[12 - Machine Learning for Log Anomaly Detection]]`
- `[[13 - Designing High-Fidelity Alerting Rules]]`
- `[[14 - Creating Honeytokens and Deception Decoys]]`
