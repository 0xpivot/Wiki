---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.12 Machine Learning for Log Anomaly Detection"
---

# 93.12 Machine Learning for Log Anomaly Detection

## Table of Contents
1. [Introduction to ML in Threat Hunting](#introduction-to-ml-in-threat-hunting)
2. [Why Traditional Signatures Fail](#why-traditional-signatures-fail)
3. [Core Concepts of ML in Log Analysis](#core-concepts-of-ml-in-log-analysis)
4. [Architecture of SIEM ML Integration](#architecture-of-siem-ml-integration)
5. [Feature Engineering for Semi-Structured Logs](#feature-engineering-for-semi-structured-logs)
6. [Implementing ML in Popular SIEMs](#implementing-ml-in-popular-siems)
    - [Splunk Machine Learning Toolkit (MLTK)](#splunk-machine-learning-toolkit-mltk)
    - [ELK Machine Learning Nodes](#elk-machine-learning-nodes)
    - [Azure Sentinel Time Series Analysis](#azure-sentinel-time-series-analysis)
7. [Real-World Attack Scenario](#real-world-attack-scenario)
8. [Challenges, Tuning, and Pitfalls](#challenges-tuning-and-pitfalls)
9. [Chaining Opportunities](#chaining-opportunities)
10. [Related Notes](#related-notes)

## 1. Introduction to ML in Threat Hunting
As threat actors evolve, relying solely on static rules and known Indicators of Compromise (IOCs) is insufficient. Machine Learning (ML) fundamentally shifts the defensive paradigm from a reactive posture ("alert when we see something known to be bad") to a proactive, probabilistic posture ("alert when we see something statistically unusual").

In the context of modern SIEM solutions (like Splunk, Elastic Stack, and Azure Sentinel), ML models ingest massive volumes of continuous log data, autonomously establish baselines of normal operational behavior, and flag deviations that warrant human investigation.

## 2. Why Traditional Signatures Fail
- **Zero-Day Exploits:** Signatures cannot exist for vulnerabilities that are not yet publicly known or analyzed.
- **Polymorphism:** Malware authors frequently alter the hashes, strings, and IPs associated with their payloads, immediately rendering static IOC lists obsolete.
- **Living off the Land (LotL):** Attackers increasingly use native administrative tools (e.g., PowerShell, WMI, PsExec). A rule that blocks `powershell.exe` will break the IT environment; ML can differentiate between an IT admin's standard script execution and an attacker's anomalous obfuscated execution.

## 3. Core Concepts of ML in Log Analysis

### Unsupervised Learning (Anomaly Detection)
This is the most common and effective approach for log anomaly detection because Security Operations Centers (SOCs) rarely possess perfectly labeled datasets detailing every possible attack vector. Unsupervised models mathematically look for outliers.
- **Clustering (e.g., DBSCAN, K-Means):** Groups similar log events together based on multidimensional features. Logs that do not map cleanly to any established cluster are flagged as anomalies.
- **Isolation Forests:** An algorithm explicitly designed to isolate anomalies rather than profile normal data. It builds random decision trees; because anomalies are few and different, they require fewer splits to be isolated compared to dense, normal data points.
- **Autoencoders (Neural Networks):** A type of deep learning model that learns to compress and perfectly reconstruct normal data. When fed malicious/anomalous data, the model struggles, resulting in a high "reconstruction error," which serves as the anomaly score.

### Supervised Learning (Classification)
Requires highly curated, labeled data (e.g., logs tagged "Benign" vs. "Malicious"). Common SOC use cases include:
- **DGA (Domain Generation Algorithm) Detection:** Classifying domain names as human-readable vs. algorithmically generated.
- **Phishing Triage:** Classifying inbound email text and metadata as malicious or benign.

## 4. Architecture of SIEM ML Integration

```text
+-------------------+        +----------------------+        +-----------------------+
|  Raw Log Data     |        | Feature Engineering  |        | Machine Learning Node |
|  (Windows Event,  |=======>| - Parsing/Grok       |=======>| - Baseline Creation   |
|   Firewall, Prox) |        | - Tokenization       |        | - Model Training      |
+-------------------+        | - Aggregation        |        | - Anomaly Scoring     |
                             +----------------------+        +-----------------------+
                                                                         |
                                                                         v
+-------------------+        +----------------------+        +-----------------------+
| Incident Response |        |  SIEM Alert Engine   |        |  Anomaly Results      |
| & Threat Hunt     |<=======|  (Thresholding &     |<=======|  (Score > Threshold)  |
| Dashboard         |        |   Correlation)       |        |                       |
+-------------------+        +----------------------+        +-----------------------+
```

## 5. Feature Engineering for Semi-Structured Logs
Machine learning algorithms only understand numbers, not text. Logs are inherently semi-structured text. Therefore, **Feature Engineering** is the most critical and difficult step in log anomaly detection. Transforming raw logs into numerical vectors determines the success or failure of the model.

Common features extracted from security logs include:
- **Temporal Features:** Hour of day, day of the week, time elapsed since the user's last login. (Useful for detecting "impossible travel" or off-hours access).
- **Volumetric/Frequency Features:** Number of events per minute, total bytes transferred outbound, ratio of inbound to outbound traffic.
- **Categorical Encoding:** Converting fields like `TargetUserName`, `EventID`, or `SourceIP` into usable formats using techniques like One-Hot Encoding or Target Encoding.
- **Lexical/Text-based Features:** Length of a command line, Shannon entropy of a script, or TF-IDF (Term Frequency-Inverse Document Frequency) vectors of PowerShell arguments.

## 6. Implementing ML in Popular SIEMs

### Splunk Machine Learning Toolkit (MLTK)
Splunk's MLTK provides a guided interface and custom SPL commands to seamlessly apply Scikit-Learn algorithms directly within the search bar.

**Example: Detecting Unusual Network Traffic using DensityFunction**
The `DensityFunction` fits a probability density distribution to the data. It calculates the probability of an event occurring; if the probability is extremely low, it is flagged.

```spl
// Training the model on historical firewall logs
index=firewall sourcetype=pan:traffic
| timechart span=1h sum(bytes_out) as total_bytes_out by src_ip
| fit DensityFunction total_bytes_out by src_ip threshold=0.01 into network_baseline_model
```
Later, apply the model to real-time incoming streams:
```spl
// Applying the model to real-time data
index=firewall sourcetype=pan:traffic earliest=-1h
| timechart span=1h sum(bytes_out) as total_bytes_out by src_ip
| apply network_baseline_model
| search "IsOutlier(total_bytes_out)"=1
| table _time, src_ip, total_bytes_out
```

### ELK Machine Learning Nodes
The Elastic Stack provides purpose-built, unsupervised ML capabilities designed specifically for high-volume time-series log data.

**Setting up an Anomaly Detection Job in Kibana:**
1. Navigate to **Machine Learning -> Anomaly Detection**.
2. Select your target index (e.g., `winlogbeat-*`).
3. Choose Job Type: "Multi-metric" or "Population".
4. Define the detector logic:
   - **Function:** `rare`
   - **Field:** `process.name`
   - **By Field:** `host.name`
   - **Over Field:** `user.name`
   This specific configuration detects processes that are highly rare for a specific host, compared to the historical baseline of what users typically run on that host.

### Azure Sentinel Time Series Analysis
Sentinel utilizes Kusto Query Language (KQL), which includes built-in functions for time-series decomposition and anomaly detection without needing external compute nodes.

```kql
// Detect anomalous spikes in failed logins using built-in decomposition
let start_time = ago(30d);
let end_time = now();
SigninLogs
| where TimeGenerated between (start_time .. end_time)
| where ResultType != "0" // Filter for Failed logins only
// Create a time series array
| make-series FailedLogins=count() on TimeGenerated from start_time to end_time step 1h
// Apply the anomaly detection algorithm (expecting max 3 anomalies)
| extend (anomalies, score, baseline) = series_decompose_anomalies(FailedLogins, 3)
// Expand arrays back into tabular format for alerting
| mv-expand TimeGenerated, FailedLogins, anomalies, score, baseline
| where anomalies == 1
| project TimeGenerated, FailedLogins, baseline, score
```

## 7. Real-World Attack Scenario

### Scenario: Detecting Data Exfiltration via DNS Tunneling
**Context:** An Advanced Persistent Threat (APT) has established a foothold inside an air-gapped segment of the network. To exfiltrate a sensitive SQL database, they are tunneling the data out over DNS queries (TXT records), bypassing the strict outbound proxy rules.

**The ML Approach to Detection:**
1. **Data Ingestion & Feature Engineering:** The SOC ingests all raw DNS query logs. They utilize Python preprocessing to extract key numerical features:
   - Length of the sub-domain query.
   - Shannon entropy of the sub-domain string.
   - Number of unique sub-domains queried per root domain per 10-minute window.
   - Volume ratio of A records to TXT records.
2. **Model Training:** An Isolation Forest model is trained on 60 days of historical DNS logs. The model organically learns that typical DNS behavior consists of short, low-entropy queries that repeat frequently due to caching (e.g., `www.google.com`).
3. **The Attack Begins:** The attacker's script begins querying dynamically generated domains: `[high-entropy-base64-chunk].evil-c2-domain.com`.
4. **Detection & Alerting:** The ML model evaluates these live log entries. It flags them as massive mathematical outliers due to the extreme entropy (Base64 data) and the unprecedented volume of completely unique subdomains for a single root domain within a short timeframe. A high-priority alert is dispatched to the SIEM dashboard.
5. **Incident Response:** Analysts review the anomaly cluster, verify the malicious payload in the subdomains, block the root domain at the enterprise DNS filter, and isolate the compromised internal host, successfully stopping the exfiltration.

## 8. Challenges, Tuning, and Pitfalls
- **Concept Drift:** Environments are not static. A massive rollout of new SCCM deployment software will mathematically appear as an anomaly. Models must be continuously retrained to incorporate new "normal" behaviors, lest they generate infinite false positives.
- **Alert Fatigue from Benign Anomalies:** Just because something is mathematically anomalous does not mean it is malicious. An admin logging in at 3 AM on a Sunday is anomalous, but often benign. ML alerts must be correlated with other threat intelligence or rules before waking up an analyst.
- **Data Quality:** "Garbage in, garbage out." Unparsed logs, inconsistent timestamp formats, or missing critical fields will completely cripple ML performance.

## 9. Chaining Opportunities
- High-fidelity anomalies identified by ML models serve as the perfect starting point for deep-dive investigations using techniques outlined in `[[11 - Using Jupyter Notebooks for Threat Hunting]]`.
- Insights gained from ML baselining can be hardcoded into static, threshold-based rules to reduce computational overhead, as discussed in `[[13 - Designing High-Fidelity Alerting Rules]]`.

## 10. Glossary of Machine Learning Terms in SOC
- **True Positive:** The model successfully identified a mathematically anomalous event that is actually a malicious attack.
- **False Positive:** The model flagged an event as anomalous, but it was benign administrative activity. This causes alert fatigue.
- **False Negative:** The model completely missed a malicious event because it blended in too closely with normal baseline traffic.
- **Dimensionality Reduction:** Techniques like PCA (Principal Component Analysis) used to reduce the number of features in log data, making models train faster and removing noise.
- **Overfitting:** When a model memorizes the exact historical logs instead of learning the underlying patterns. An overfitted model will flag *everything* new as an anomaly.
- **Underfitting:** When a model is too simple to capture the complexity of the enterprise network, resulting in it missing critical anomalies.
- **Hyperparameter Tuning:** The manual process of adjusting the underlying settings of the ML algorithm (e.g., the number of trees in an Isolation Forest or the threshold limit) to reduce false positives.

## 11. Extended Troubleshooting Guide
1. **Model taking too long to train:** You are likely feeding it too much raw text. Ensure you extract specific features (e.g., string length, distinct count) rather than feeding it raw command lines.
2. **"No baselines generated" error:** Your chosen time window is too small. A population model needs at least 30-60 days of historical data to accurately profile "normal" behavior.
3. **Spike in anomalies after Patch Tuesday:** This is expected concept drift. System updates change binary hashes and execution patterns. Consider temporarily pausing model alerting during massive enterprise rollouts to prevent SOC flooding.
4. **Data Sparsity Issues:** Some event types occur so rarely that ML models cannot form a baseline. These should be monitored using traditional static rules rather than ML.
5. **Feature Importance Mismatch:** The model might be keying in on irrelevant features (like a random transaction ID) instead of the actual malicious indicator. Use feature importance plotting in Jupyter to debug.

## 12. Related Notes
- `[[11 - Using Jupyter Notebooks for Threat Hunting]]`
- `[[13 - Designing High-Fidelity Alerting Rules]]`
- `[[14 - Creating Honeytokens and Deception Decoys]]`
- `[[15 - Case Study Tracking APT29 across a SIEM]]`
