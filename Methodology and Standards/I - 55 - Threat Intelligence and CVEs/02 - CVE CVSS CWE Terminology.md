---
tags: [threat-intel, cve, research, vapt]
difficulty: beginner
module: "55 - Threat Intelligence and CVEs"
topic: "55.02 CVE CVSS CWE Terminology"
---

# CVE, CVSS, and CWE Terminology

## Introduction to the Vulnerability Ecosystem
In the realm of Vulnerability Assessment and Penetration Testing (VAPT), standardisation is paramount. Without a common language, security researchers, software vendors, and system administrators would struggle to communicate the severity, nature, and identity of software flaws. The modern vulnerability ecosystem is built upon several foundational standards managed primarily by MITRE and the National Institute of Standards and Technology (NIST). The core triad of this ecosystem consists of CVE (the *identity* of the vulnerability), CWE (the *nature* or type of the weakness), and CVSS (the *severity* or risk score).

Understanding these terms in extreme detail is essential for any cybersecurity professional, as they form the basis of vulnerability scanners, bug bounty programs, and threat intelligence reports.

## Common Vulnerabilities and Exposures (CVE)
CVE is a dictionary, not a database. It provides a standardized identifier for publicly known cybersecurity vulnerabilities. 

### Structure of a CVE Identifier
The format is `CVE-YYYY-NNNNN`. 
- `YYYY` represents the year the vulnerability was reported or assigned.
- `NNNNN` is an arbitrary sequence number assigned by a CVE Numbering Authority (CNA). While originally limited to four digits (e.g., CVE-2014-0160 for Heartbleed), the explosion of vulnerabilities necessitated expansion to five or more digits.

### The Role of CNAs
CVE Numbering Authorities (CNAs) are organizations authorized by the CVE Program (managed by MITRE) to assign CVE IDs to vulnerabilities discovered within their specific scope. Major software vendors (like Microsoft, Apple, and Oracle) are CNAs for their own products. There are also Root CNAs and Top-Level Roots that manage hierarchies of CNAs.

### The CVE Lifecycle
1. **Discovery**: A researcher discovers a vulnerability.
2. **Assignment**: A CNA assigns a CVE ID to the vulnerability (often in a "Reserved" state initially).
3. **Disclosure**: The vulnerability is publicly disclosed, usually accompanied by a patch from the vendor.
4. **Publication**: The CVE entry is populated with details (description, affected versions, references) and published to the global CVE list.

## Common Weakness Enumeration (CWE)
While a CVE identifies a *specific* instance of a vulnerability in a *specific* product, CWE identifies the *underlying software error or architectural flaw* that caused the vulnerability. It is a formal taxonomy of software weaknesses.

### CWE Hierarchy and Abstraction
CWEs are organized hierarchically, ranging from high-level classes to extremely specific coding errors.
- **Class Level**: Broad categories (e.g., CWE-119: Improper Restriction of Operations within the Bounds of a Memory Buffer).
- **Base Level**: More specific (e.g., CWE-120: Buffer Copy without Checking Size of Input).
- **Variant Level**: Highly specific (e.g., CWE-121: Stack-based Buffer Overflow).

### Importance of CWE in VAPT
By mapping a discovered CVE to its CWE, penetration testers can understand the root cause of the flaw. If a web application is vulnerable to CVE-2021-44228 (Log4Shell), knowing it maps to CWE-502 (Deserialization of Untrusted Data) or CWE-20 (Improper Input Validation) allows the tester to look for *similar* unseen vulnerabilities in custom code. The "CWE Top 25 Most Dangerous Software Weaknesses" is a critical list updated annually, guiding secure coding practices.

## Common Vulnerability Scoring System (CVSS)
CVSS provides a standardized framework for rating the severity of a vulnerability. It translates the technical characteristics of a vulnerability into a numerical score from 0.0 to 10.0.

### CVSS Metrics Breakdown
CVSS v3.1 (and the emerging v4.0) consists of three metric groups:

#### 1. Base Metrics (Always Required)
These represent the intrinsic qualities of a vulnerability that are constant over time and across user environments.
- **Attack Vector (AV)**: Network, Adjacent, Local, or Physical. (Network is worst).
- **Attack Complexity (AC)**: Low or High.
- **Privileges Required (PR)**: None, Low, or High.
- **User Interaction (UI)**: None or Required.
- **Scope (S)**: Unchanged or Changed. (A changed scope means a vulnerability in one component can compromise a different component, e.g., a VM escape).
- **Impact Metrics (CIA Triad)**: Confidentiality (None, Low, High), Integrity (None, Low, High), Availability (None, Low, High).

#### 2. Temporal / Threat Metrics
These reflect characteristics that change over time.
- **Exploit Code Maturity (E)**: Is there a functional exploit available? (Unproven, Proof of Concept, Functional, High).
- **Remediation Level (RL)**: Is there a patch or workaround? (Official Fix, Temporary Fix, Workaround, Unavailable).
- **Report Confidence (RC)**: How confirmed is the vulnerability? (Unknown, Reasonable, Confirmed).

#### 3. Environmental Metrics
These are customized by the end-user organization to reflect the vulnerability's impact on their specific IT environment.
- **Modified Base Metrics**: Adjusting the base metrics based on mitigating controls (e.g., an internal firewall).
- **Confidentiality/Integrity/Availability Requirements (CR/IR/AR)**: How critical is the affected asset to the business?

### CVSS v3.1 vs CVSS v4.0
CVSS v4.0 introduces finer granularity, particularly concerning the interaction between vulnerable systems and subsequent systems (replacing the confusing "Scope" metric with explicit Vulnerable System and Subsequent System impact metrics). It also adds metrics for Automatable (can the exploit be wormable?) and Recovery (how easily can the system recover?).

## Common Platform Enumeration (CPE)
CPE is a structured naming scheme for IT systems, software, and packages. When a CVE is published, it must identify *what* software is vulnerable. CPE provides the syntax for this.
Format: `cpe:2.3:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>`
Example: `cpe:2.3:a:apache:http_server:2.4.49:*:*:*:*:*:*:*`
This string allows automated vulnerability scanners to match installed software against the National Vulnerability Database.

## Exploit Prediction Scoring System (EPSS)
While CVSS measures *severity* (impact if exploited), EPSS estimates the *probability* that a vulnerability will actually be exploited in the wild. It uses machine learning models trained on real-world threat intelligence. A vulnerability might have a CVSS of 9.8 but an EPSS of 0.01% if no one is actually exploiting it. Conversely, a CVSS 7.5 might have an EPSS of 95% if it's currently being actively used by ransomware gangs.

## The Interplay: Putting it all together
When a penetration tester encounters a system:
1. They identify running services and extract their **CPE** strings.
2. They query a database to find **CVE**s associated with those CPEs.
3. They look at the **CVSS** score to prioritize which CVEs to investigate first.
4. They analyze the **CWE** to understand the nature of the flaw and formulate an attack strategy.
5. They check **EPSS** to gauge the likelihood of finding a public exploit.

## Visualizing the Vulnerability Ecosystem

```text
+-------------------------------------------------------------------------+
|                      The Vulnerability Data Triad                       |
+-------------------------------------------------------------------------+

  [CPE] Common Platform Enumeration           [CWE] Common Weakness Enum.
  Identifies the AFFECTED ASSET               Identifies the ROOT CAUSE
  (e.g., cpe:2.3:a:vendor:product:1.0)        (e.g., CWE-89: SQL Injection)
             \                                       /
              \                                     /
               v                                   v
             +---------------------------------------+
             |    [CVE] Common Vuln. & Exposures     |
             |    The unique IDENTIFIER              |
             |    (e.g., CVE-2023-12345)             |
             +---------------------------------------+
                               |
                               |  Determines
                               v
             +---------------------------------------+
             |    [CVSS] Common Vuln. Scoring Sys.   |
             |    The SEVERITY SCORE (0.0 to 10.0)   |
             |    (e.g., Base Score: 9.8 CRITICAL)   |
             +---------------------------------------+
                               |
                               |  Complemented by
                               v
             +---------------------------------------+
             |    [EPSS] Exploit Prediction Score    |
             |    The PROBABILITY of exploitation    |
             |    (e.g., 85% probability in 30 days) |
             +---------------------------------------+
```

## How Vulnerability Scanners Use This Data
Tools like Nessus, OpenVAS, and Qualys rely entirely on this standardisation. They use plugins that:
1. Extract the CPE of the target service.
2. Query local databases synchronised with the NVD for CVEs linked to that CPE.
3. Report the findings, categorising them by CVSS scores, and often mapping them to CWEs to help developers understand how to patch the underlying code rather than just applying a quick fix.

## Chaining Opportunities
- A low CVSS score vulnerability (e.g., Information Disclosure) can be chained with another low score vulnerability (e.g., CSRF) to achieve a high-impact compromise.
- Understanding the CWE of a discovered CVE can guide a tester to find zero-day vulnerabilities in the same application by looking for similar coding patterns.

## Related Notes
- [[01 - What is Threat Intelligence]]
- [[03 - NVD National Vulnerability Database]]
- [[04 - Exploit-DB and Packet Storm]]
- [[05 - SearchSploit Offline Exploit-DB Search]]
