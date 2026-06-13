---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.14 Automating Hunts vs Manual Investigations"
---

# 14 - Automating Hunts vs Manual Investigations

## Introduction: The Automation Paradox

In modern cybersecurity operations, automation is often touted as the panacea for all operational woes. SOAR (Security Orchestration, Automation, and Response) platforms, AI-driven analytics, and machine learning models promise to replace the tedious manual labor of analysts. However, in the specific context of Threat Hunting, there exists a fundamental paradox:

*If a threat hunt can be fully 100% automated, it is no longer a "hunt." It is a Detection Rule.*

Threat hunting is, by definition, the proactive search for unknown or heavily obfuscated threats that have successfully bypassed automated security controls. Therefore, the core analytical process of hunting requires human intuition, creativity, and contextual understanding of the business environment. Yet, expecting highly skilled analysts to manually pull logs, format CSVs, and cross-reference IPs against VirusTotal manually is a massive waste of resources. 

The elite hunting program does not automate the *analysis*; it automates the *data pipeline* and the *enrichment*.

## The Automation Continuum

Understanding where hunting sits on the automation continuum is vital for building a mature security posture.

```text
+-------------------------------------------------------------------------+
|                    The Threat Detection Automation Continuum            |
+-------------------------------------------------------------------------+
|                                                                         |
|  [ Pure Manual ] -----> [ Scripted Prep ] -----> [ Automated Pipeline]  |
|   Ad-hoc queries        Jupyter Notebooks         SOAR enrichment       |
|   High time cost        API integrations          Continuous baselining |
|   High flexibility      Medium flexibility        Low flexibility       |
|                                                                         |
|                               |                                         |
|                               V                                         |
|                       [ Fully Automated ]                               |
|                         (Detection Engineering)                         |
|                         Real-time SIEM alerts                           |
|                         Automated blocking                              |
|                                                                         |
+-------------------------------------------------------------------------+
```

## What Should Be Automated?

To maximize the efficiency of a threat hunter, all rote, repetitive tasks must be automated. The goal is to present the hunter with a rich, contextualized dataset so they can begin their analysis immediately.

### 1. Data Aggregation and Normalization
Instead of writing ten different queries for ten different log sources (Firewall, Proxy, EDR, Windows Event Logs), automated data pipelines should normalize these logs into a common schema (like OSSEM - Open Source Security Events Metadata) and aggregate them into a single data lake.

### 2. Contextual Enrichment via APIs
When a hunter pulls a list of suspicious external IP addresses, they shouldn't have to manually check them. Automation (via SOAR or Python scripts) should intercept this list, query Threat Intelligence APIs (e.g., GreyNoise, VirusTotal, CrowdStrike Falcon), gather WHOIS data, check ASN reputation, and append this metadata to the hunter's dataset.

### 3. Statistical Baselining
Machine learning excels at identifying deviations from the norm. Automating the calculation of baselines (e.g., "What is the standard volume of outbound SSH traffic for this specific server over a 30-day period?") allows the hunter to instantly query the outliers, rather than calculating the baseline manually.

### Code Example: Automating Enrichment with Python (MSTICPy)
Microsoft Threat Intelligence Python (MSTICPy) is a powerful library used in Jupyter Notebooks to automate the enrichment phase of a hunt.

```python
import msticpy as mp
from msticpy.sectools import TILookup

# Initialize Threat Intel Lookup
ti = TILookup()

# The hunter manually identifies suspicious IPs
suspicious_ips = ["198.51.100.23", "203.0.113.45", "185.15.59.224"]

# Automating the enrichment process
ti_results = ti.lookup_iocs(data=suspicious_ips, providers=["AlienVault", "VirusTotal"])

# The hunter is presented with a pre-analyzed DataFrame, ready for human intuition
display(ti_results[['Ioc', 'Provider', 'Result', 'Severity']])
```

## What MUST Remain Manual?

Despite the power of automation, critical phases of the hunt must remain manual.

### 1. Hypothesis Generation
Automation cannot generate a novel hypothesis based on reading a newly published CISA alert or understanding the geopolitical landscape. Formulating the initial question requires human intelligence.

### 2. Contextual Validation (The "Why")
An automated script might flag a sudden spike in database queries as an anomaly. Only a human analyst can contextualize that this spike aligns perfectly with the end-of-quarter financial reporting run by the CFO's office.

### 3. Pivoting and Lateral Exploration
When an anomaly is discovered, the adversary's next steps are rarely predictable. They might deploy a custom webshell, execute an obfuscated PowerShell script, or simply use valid RDP credentials. A human hunter dynamically adapts their search strategy (pivoting) based on the evidence presented at each step. An automated script follows a rigid path and will miss lateral movement if the adversary deviates from the playbook.

## Real-World Attack Scenario

**Scenario: Automated Detection of Beaconing vs. Manual Payload Analysis**

**The Automation Phase:** An organization deployed an automated Zeek and RITA (Real Intelligence Threat Analytics) pipeline. Every night, a script analyzed the previous 24 hours of proxy logs, mathematically scoring all outbound connections for beaconing behavior based on timing interval, data payload size, and dispersion.

**The Alert:** The automated pipeline generated a daily report highlighting one internal host with a high beacon score communicating to `update.legit-software-cdn.com` (a seemingly benign domain).

**The Manual Phase:** The threat hunter took over.
1. **Analysis:** The hunter manually queried the EDR logs for the internal host to see what process was making the network connection. It was `svchost.exe`.
2. **Pivoting:** Knowing `svchost.exe` should not be communicating with random CDNs without a specific service attached, the hunter manually investigated the process arguments and thread execution.
3. **Discovery:** The hunter found an injected thread running heavily obfuscated shellcode. They manually extracted the memory segment, reverse-engineered the shellcode, and discovered a heavily modified variant of the Sliver C2 framework.

**Conclusion:** The automation did the heavy lifting of finding the needle in the haystack (the mathematically anomalous network connection). The human did the critical work of contextualizing the artifact, reverse engineering the payload, and confirming the breach.

## The Lifecycle: From Manual Hunt to Automated Detection

The relationship between manual hunting and automation is circular. 
1. The human conducts a **manual hunt** based on a novel hypothesis.
2. The hunt successfully identifies a new TTP (Tactics, Techniques, and Procedures).
3. The hunter works with Detection Engineers to codify the logic.
4. The manual hunt becomes a **fully automated detection rule**.
5. The hunter is freed up to manually hunt for the next unknown threat.

## Chaining Opportunities
* Understanding what to automate requires a solid foundation. The queries defined in `[[11 - Creating a Threat Hunting Runbook]]` are prime candidates for automation.
* Automating the baseline calculation is the most effective way to address the False Positive issues discussed in `[[12 - False Positives vs False Negatives in Hunting]]`.
* When measuring success, tracking the number of manual hunts converted into automated detections is a key metric. See `[[15 - Measuring the ROI of a Threat Hunting Program]]`.

## Related Notes
* `[[11 - Creating a Threat Hunting Runbook]]`
* `[[12 - False Positives vs False Negatives in Hunting]]`
* `[[13 - Transitioning from Hunt to Incident Response]]`
* `[[15 - Measuring the ROI of a Threat Hunting Program]]`
