---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.06 The Pyramid of Pain in Hunting"
---

# 88.06 The Pyramid of Pain in Hunting

## 1. Executive Summary

The Pyramid of Pain is a conceptual framework proposed by security professional David Bianco in 2013. It fundamentally changed how Security Operations Centers (SOCs), Threat Hunters, and Detection Engineers measure the effectiveness of their threat intelligence and detection engineering. At its core, the Pyramid represents the relationship between the types of Indicators of Compromise (IoCs) you might use to detect adversary activity and how much "pain" (in terms of time, effort, and money) it causes the adversary when you successfully deny those indicators to them.

Threat hunting is not merely about accumulating massive blocklists; it is about strategically deploying detection capabilities that force attackers to expend resources. If an organization only focuses on the bottom of the pyramid, an attacker can easily bypass defenses with minimal effort. Conversely, if an organization can detect and block behaviors at the top of the pyramid, they force the attacker to reinvent their entire methodology.

## 2. Deep Dive: The Six Tiers of the Pyramid

### 2.1 Hash Values (Trivial)
**Description:**
Hash values (MD5, SHA-1, SHA-256) are cryptographic representations of files. They are the most specific indicators possible, uniquely identifying a specific binary or script used by an attacker.

**Why it's Trivial for Attackers:**
Changing a single bit in a file, adding a space to the end of a script, or recompiling a binary completely alters its hash. For an adversary, the cost of generating a new hash is essentially zero. Modern malware often employs server-side polymorphism, where each victim receives a uniquely compiled payload, making hash-based detection nearly obsolete for targeted attacks.

**Hunting Approach:**
While trivial for the attacker, hashes are also trivial for defenders to implement in AV and EDR solutions. They are useful for establishing historical compromise (retro-hunting) to answer the question, "Did we ever see this specific file?". However, they should never be the primary focus of an active hunt.

### 2.2 IP Addresses (Easy)
**Description:**
IP addresses represent the network locations from which attackers launch their attacks, host their command and control (C2) servers, or exfiltrate data.

**Why it's Easy for Attackers:**
In the era of cloud computing, proxy networks, Tor, and fast-flux DNS, obtaining a new IP address takes seconds and costs pennies. Attackers regularly rotate through thousands of IPs using services like AWS, DigitalOcean, or compromised botnets. Blocking an IP might disrupt an active session, but the attacker will simply reconnect from a new one.

**Hunting Approach:**
Hunting by IP is often reactive. You take an IP from an intelligence report and search your firewall or proxy logs. It is a necessary baseline activity but provides little long-term strategic value.

### 2.3 Domain Names (Simple)
**Description:**
Domain names (e.g., `evil-c2-server.com`) are registered by attackers to provide resilient infrastructure. If an IP changes, the domain can simply be pointed to the new IP via DNS A-records.

**Why it's Simple for Attackers:**
While slightly more cumbersome than changing an IP—because domains must be registered, paid for, and propagated through DNS—it is still relatively easy. Domain Generation Algorithms (DGAs) allow malware to algorithmically generate thousands of domains a day, only one of which needs to be registered by the attacker to establish C2.

**Hunting Approach:**
Hunting domains involves analyzing DNS queries, proxy logs, and TLS SNI fields.
- **Example query:** Look for domains with high Shannon entropy, newly registered domains (NRDs), or unusual Top-Level Domains (TLDs) like `.xyz` or `.top`.

### 2.4 Network and Host Artifacts (Annoying)
**Description:**
At this level, we begin looking at the *byproducts* of the attacker's activity.
- **Host Artifacts:** Specific registry keys created by malware for persistence, predictable file paths, scheduled task names, or specific mutexes in memory.
- **Network Artifacts:** Distinctive HTTP User-Agent strings, specific URI patterns in C2 beacons, or unique TLS JA3 fingerprints.

**Why it's Annoying for Attackers:**
To evade detection at this level, the attacker must actually modify their tools or configurations. If you block a specific C2 URI pattern, the attacker must reconfigure their C2 framework, test it, and deploy the new profile. This takes development time and effort.

**Hunting Approach:**
This is where true, proactive threat hunting begins. Hunters look for anomalies in registry modifications, unusual persistence mechanisms, and deviations in network traffic patterns that correspond to known malware families.

### 2.5 Tools (Challenging)
**Description:**
Tools encompass the specific software the adversary uses to accomplish their goals. This includes C2 frameworks (Cobalt Strike, Sliver, Mythic), scanning tools (Nmap, BloodHound), or credential dumpers (Mimikatz, Procdump).

**Why it's Challenging for Attackers:**
Detecting the tool itself—regardless of how its configured or what infrastructure it uses—forces the attacker to either build a new tool from scratch or learn a completely different open-source framework. If your organization can reliably detect *any* execution of Mimikatz or *any* Cobalt Strike beacon (regardless of the specific payload hash or C2 domain), the attacker is in serious trouble.

**Hunting Approach:**
Hunt for the behavioral signatures of the tools. For example, Cobalt Strike's default named pipe patterns (`\pipe\msagent_*`), or Mimikatz's specific LSASS memory access patterns.

### 2.6 Tactics, Techniques, and Procedures - TTPs (Tough)
**Description:**
TTPs represent the attacker's fundamental methodology and behavior. It is *how* they accomplish their goals, independent of the tools they use. For example, "Credential Dumping via LSASS Memory Access" is a technique (T1003.001 in MITRE ATT&CK), while "Mimikatz" is just one tool that implements that technique.

**Why it's Tough for Attackers:**
To evade a TTP-based detection, the attacker must fundamentally change how they operate. If you detect *all* unauthorized access to LSASS, the attacker cannot use Mimikatz, they cannot use Procdump, they cannot use a custom API script. They must find an entirely different way to obtain credentials (e.g., kerberoasting instead of memory dumping). This requires massive retraining, research, and development on the attacker's part.

**Hunting Approach:**
TTP hunting relies on deep behavioral analysis using EDR logs, Sysmon, and advanced SIEM correlations. It involves establishing baselines of normal behavior and identifying the precise API calls or process trees associated with malicious techniques.

## 3. Real-World Attack Scenario

### The Scenario: A Ransomware Deployment (Black Basta)
Let's analyze how a defender interacts with the Pyramid of Pain during a targeted ransomware incident.

**Phase 1: Initial Access via Phishing (The Bottom Tiers)**
The attacker sends an email with a malicious payload.
- **Hash:** The defender's AV blocks `invoice-v1.docx` (Hash). The attacker trivially recompiles to `invoice-v2.docx`. The defender loses.
- **IP/Domain:** The macro beacons to `192.168.1.5` and `evil-macro.xyz`. The defender blocks them. The attacker updates the macro to beacon to a new cloud-hosted IP. The defender loses again.

**Phase 2: Persistence and Discovery (The Middle Tiers)**
The attacker drops a custom backdoor.
- **Artifacts:** The backdoor always creates a scheduled task named `WindowsUpdateTask_Critical`. The hunter finds this and removes it. The attacker is annoyed, has to re-code the persistence mechanism to use Run registry keys instead.
- **Tools:** The attacker uses BloodHound to map the Active Directory. The hunter has a rule that detects the specific LDAP queries generated by SharpHound. The attacker is challenged; they can't use their favorite tool and must manually query AD using built-in Windows commands (`net group "Domain Admins" /domain`).

**Phase 3: Execution and Impact (The Top Tier)**
The attacker attempts to dump credentials.
- **TTPs:** Regardless of whether the attacker uses Mimikatz, an unknown custom tool, or a living-off-the-land binary (Task Manager), the Threat Hunter has deployed a rule detecting *any process that requests `PROCESS_ALL_ACCESS` or specific access flags against `lsass.exe` originating from a non-system process*.
- **The Result:** The attack is completely stopped. The attacker cannot dump credentials without re-engineering their entire methodology for privilege escalation. The pain inflicted is absolute.

## 4. Visualizing the Pyramid

### ASCII Diagram: The Pyramid of Pain

```text
                               /\
                              /  \
                             /    \
                            / TTPs \
                           /        \
                          /----------\     <-- TOUGH: Forces attacker to change behavior
                         /            \
                        /    Tools     \
                       /                \
                      /------------------\ <-- CHALLENGING: Forces attacker to change tools
                     /                    \
                    /       Network/       \
                   /     Host Artifacts     \
                  /                          \
                 /----------------------------\ <-- ANNOYING: Forces attacker to modify configs
                /                              \
               /          Domain Names          \
              /                                  \
             /------------------------------------\ <-- SIMPLE: Attackers change domains easily
            /                                      \
           /             IP Addresses               \
          /                                          \
         /--------------------------------------------\ <-- EASY: Attackers rotate IPs instantly
        /                                              \
       /                  Hash Values                   \
      /                                                  \
     /----------------------------------------------------\ <-- TRIVIAL: Hashes change automatically
```

## 5. Integrating the Pyramid into Hunt Operations

### 5.1 Evaluating Threat Intelligence
If your CTI (Cyber Threat Intelligence) vendor only provides hashes and IPs, they are providing low-value data. While useful for automated blocking at the perimeter, it is not "Threat Intelligence"—it is data. Demand TTP-level intelligence (e.g., MITRE ATT&CK mapping, behavioral reports, YARA/Sigma rules) from your vendors.

### 5.2 Prioritizing Detection Engineering
SOCs have limited time. Spend 80% of your detection engineering time building alerts for Tools and TTPs. Spend 20% automating the ingestion of lower-level indicators via SOAR platforms. If a human has to manually block an IP address, the process is inefficient.

### 5.3 Metric Tracking
Track the number of detections your team creates at each level of the pyramid. A mature hunting team will heavily skew toward the top three tiers. Measure the "shelf-life" of your detections: a hash-based detection is useful for hours; a TTP-based detection is useful for years.

## 6. Common Pitfalls
1. **Ignoring the Bottom:** Do not completely ignore hashes and IPs. They are trivial for attackers to change, but if an attacker *is* reusing infrastructure, you want to catch them easily. The goal is to automate the bottom tiers, not abandon them.
2. **False Positives at the Top:** TTP hunting inherently generates more false positives than hash matching. Robust baselining is required to tune TTP alerts effectively.
3. **Overcomplicating the Middle:** Do not write a custom regular expression for every User-Agent string you see. Focus on the behavior that generated the traffic instead.

## 7. Chaining Opportunities
- **[[07 - Baseline Establishment and Anomaly Detection]]**: In order to hunt for TTPs effectively (the top of the pyramid), you must first establish baselines of normal behavior to filter out legitimate administrative activity.
- **[[08 - Using Sigma Rules for Vendor-Agnostic Hunting]]**: Sigma is the primary language used to write behavioral (TTP-level) detections that can be shared across different SIEMs and EDRs.
- **[[09 - Threat Hunting Maturity Model THMM]]**: Reaching the top of the Pyramid of Pain correlates directly with reaching Level 3 or Level 4 of the SANS THMM.

## 8. Related Notes
- [[01 - Introduction to Threat Hunting]]
- [[03 - The MITRE ATT&CK Framework]]
- [[11 - Identifying Living off the Land Binaries (LOLBins)]]
- [[15 - Memory Analysis and LSASS Abuse]]
- [[26 - Cyber Threat Intelligence CTI Integration]]
