---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.12 False Positives vs False Negatives in Hunting"
---

# 12 - False Positives vs False Negatives in Hunting

## Introduction: The Hunter's Dilemma

In the realm of Threat Hunting and Detection Engineering, the ultimate objective is to achieve perfect visibility: catching every adversary while never alerting on legitimate user behavior. In reality, this is mathematically and practically impossible. The discipline of threat hunting is an ongoing war of attrition against two primary adversaries: the actual threat actor, and the statistical noise of the environment.

Understanding the balance between False Positives (FP) and False Negatives (FN) is the core of effective hunting. A program heavily skewed toward eliminating FNs will drown its analysts in alert fatigue (too many FPs). Conversely, a program obsessed with eliminating FPs will create massive blind spots, allowing sophisticated actors to operate undetected (too many FNs).

## Defining the Confusion Matrix

To mathematically and logically quantify our hunting queries, we rely on the Confusion Matrix, a concept borrowed from machine learning and statistics.

```text
+-------------------------------------------------------------------------+
|                  Threat Detection Confusion Matrix                      |
+-------------------------------------------------------------------------+
|                        |                                                |
|                        |             ACTUAL STATE                       |
|                        |   Malicious (True)  |   Benign (False)         |
|------------------------+---------------------+--------------------------|
| P   Alert Triggered    |    TRUE POSITIVE    |    FALSE POSITIVE        |
| R       (Positive)     |        (Hit)        |     (False Alarm)        |
| E                      |                     |                          |
| D ---------------------+---------------------+--------------------------|
| I  No Alert/Ignored    |   FALSE NEGATIVE    |    TRUE NEGATIVE         |
| C       (Negative)     |       (Miss)        |    (Correct Rejection)   |
| T                      |                     |                          |
+-------------------------------------------------------------------------+
```

* **True Positive (TP):** A malicious action occurred, and the hunt query successfully identified it. (The Goal)
* **True Negative (TN):** A benign action occurred, and the hunt query correctly ignored it. (The Normal State)
* **False Positive (FP):** A benign action occurred, but the hunt query flagged it as malicious. (Alert Fatigue / Noise)
* **False Negative (FN):** A malicious action occurred, but the hunt query completely missed it. (The Nightmare Scenario)

## The Base Rate Fallacy in Cybersecurity

The Base Rate Fallacy is a cognitive bias that drastically affects threat hunters. It occurs when people ignore the underlying probability (the base rate) of an event in favor of specific information. 

In a massive enterprise network, billions of events are generated daily. The base rate of actual malicious activity is incredibly small—perhaps 0.00001%. Even if a threat hunting query is 99% accurate (meaning it only has a 1% false positive rate), running it against 1,000,000 events will generate 10,000 False Positives. The sheer volume of benign activity completely overwhelms the actual malicious signals.

This is why "hunting for anomalies" without context is a failed strategy. Hunters must narrow the denominator (the base rate) by focusing on specific choke points, high-value assets, or well-defined adversarial behaviors rather than sweeping the entire haystack.

## The Cost of False Positives (Alert Fatigue)

False positives are not merely an annoyance; they are a severe security risk. 
1. **Analyst Burnout:** Investigating benign behavior drains mental energy and resources.
2. **The "Boy Who Cried Wolf" Effect:** When a rule triggers falsely 99 times, the analyst will likely dismiss the 100th alert, which might be the actual True Positive. This converts a False Positive problem into a catastrophic False Negative.
3. **Resource Exhaustion:** SOAR tools and SIEM licenses can be exhausted processing junk alerts.

**Tuning FPs in a Hunt:**
To reduce FPs during a hunt without creating FNs, hunters utilize:
* **Behavioral Baselining:** Establishing what "normal" looks like for a specific user, host, or application, and filtering out those exact patterns.
* **Contextual Enrichment:** Before returning a result, script the query to cross-reference threat intelligence or asset inventory (e.g., automatically ignore SSH connections originating from the authorized vulnerability scanner IP).

## The Cost of False Negatives (Silent Failure)

False Negatives represent a complete failure of the detection mechanism. The adversary successfully bypassed the logic, and the organization is operating under a false sense of security. 

False Negatives occur for several reasons:
1. **Over-Tuning:** The analyst was tired of FPs, so they added too many exceptions to the query (e.g., `where ProcessName != 'powershell.exe'`). The adversary then uses `powershell.exe`.
2. **Evasion Techniques:** The adversary alters their behavior to evade the signature (e.g., renaming the binary, using API unhooking, encrypting payloads).
3. **Log Gaps:** The required telemetry was simply not collected or aged out of the SIEM.

**Reducing FNs in a Hunt:**
* **Hunt by Behavior, Not Indicator:** Searching for `hash=12345` will yield an FN the second the malware is recompiled. Searching for "Process X injecting into Process Y via CreateRemoteThread" will catch the behavior regardless of the hash.
* **Assume Compromise:** The foundational mindset of threat hunting. Assume the automated defenses have already failed, and build queries to look for the post-exploitation artifacts.

## ROC Curves and the Detection Sweet Spot

In advanced threat hunting programs, Detection Engineers evaluate queries using a Receiver Operating Characteristic (ROC) curve. The curve plots the True Positive Rate against the False Positive Rate at various threshold settings. 

The goal is not to find a query with zero FPs and zero FNs—that doesn't exist. The goal is to find the optimal threshold where the operational cost of investigating the FPs is less than the risk of the FNs. 

If you are hunting for highly critical activity (e.g., Domain Controller replication anomalies like DCSync), you must accept a higher FP rate because the cost of an FN is a total domain compromise. If you are hunting for adware, you demand a near-zero FP rate, as the risk of an FN is extremely low.

## Real-World Attack Scenario

**Scenario: Living off the Land with `certutil.exe`**

**The Concept:** Threat hunters deployed a query to identify the use of `certutil.exe` downloading files from the internet, a known Living-off-the-Land (LotL) technique used by adversaries to bypass application whitelisting and fetch payloads.

**The Initial Query (High FN Risk):**
```kusto
DeviceProcessEvents
| where ProcessCommandLine contains "certutil" 
| where ProcessCommandLine contains "urlcache" and ProcessCommandLine contains "split"
| where ProcessCommandLine contains ".exe"
```
*Why it failed (FN):* The adversary knew about this rule. They downloaded a `.txt` file containing base64 encoded malware, and they renamed `certutil.exe` to `updater.exe` before executing it. The query completely missed it.

**The Revised Query (High FP Risk):**
```kusto
DeviceProcessEvents
| where OriginalFileName == "certutil.exe" // Catches renaming
| where ProcessCommandLine contains "urlcache"
```
*The Result:* The hunter was flooded with thousands of alerts. IT deployment scripts, antivirus updates, and configuration managers were constantly using `certutil` to verify certificates and download legitimate CRL (Certificate Revocation List) files. (Massive FP).

**The Tuned Hunt Query (The Sweet Spot):**
```kusto
DeviceProcessEvents
| where OriginalFileName == "certutil.exe"
| where ProcessCommandLine contains "urlcache"
// Filter out known good domains
| where not(ProcessCommandLine has_any ("microsoft.com", "verisign.com", "digicert.com"))
// Filter out known admin subnets
| where not(IPAddress startswith "10.0.50.")
// Look for anomalous execution contexts
| where InitiatingProcessFileName in ("cmd.exe", "powershell.exe", "wscript.exe")
```
*The Result:* The query returned 3 results. Two were IT admins manually testing connectivity (minor FPs). One was `certutil.exe` downloading `payload.bin` from a Pastebin URL, initiated by a malicious Word macro (True Positive). The hunter successfully navigated the FP/FN tradeoff.

## Continuous Tuning

Hunting is not a static endeavor. As the environment changes, a query that was perfectly tuned yesterday will generate massive FPs tomorrow (e.g., when IT deploys a new software management tool). Hunters must continuously feed metrics back into the detection engineering pipeline to adjust thresholds, update whitelists, and refine behavioral logic.

## Chaining Opportunities
* Before you can tune FPs/FNs, you need a structured approach. Review `[[11 - Creating a Threat Hunting Runbook]]` for foundational structures.
* When a True Positive is finally validated after wading through FPs, the hunt instantly escalates. See `[[13 - Transitioning from Hunt to Incident Response]]`.
* Managing this lifecycle at scale requires automation. See `[[14 - Automating Hunts vs Manual Investigations]]`.

## Related Notes
* `[[11 - Creating a Threat Hunting Runbook]]`
* `[[13 - Transitioning from Hunt to Incident Response]]`
* `[[14 - Automating Hunts vs Manual Investigations]]`
* `[[15 - Measuring the ROI of a Threat Hunting Program]]`
