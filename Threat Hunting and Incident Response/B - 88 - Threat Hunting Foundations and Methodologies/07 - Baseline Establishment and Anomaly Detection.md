---
tags: [threat-hunting, ir, methodologies, vapt]
difficulty: beginner
module: "88 - Threat Hunting Foundations and Methodologies"
topic: "88.07 Baseline Establishment and Anomaly Detection"
---

# 88.07 Baseline Establishment and Anomaly Detection

## 1. Introduction to Baselines
In the context of Threat Hunting, a "baseline" is an established standard of normal behavior within an IT environment over a specific period. It is the mathematical, behavioral, and statistical representation of what the network, endpoints, and users look like when they are *not* under attack.

Without a baseline, anomaly detection is impossible. You cannot find the needle if you do not know what the haystack looks like. Many novice threat hunters make the mistake of hunting for "bad" (searching for known Indicators of Compromise). Advanced hunters hunt for "abnormal" by thoroughly understanding "normal." This shift in perspective is what enables defenders to catch zero-day exploits, novel malware, and sophisticated insider threats that lack known signatures.

## 2. The Core Philosophy of Anomaly Detection
Anomaly detection assumes that malicious activity will inevitably cause a deviation from normal operations. When an adversary compromises a host, deploys a C2 beacon, or exfiltrates data, they generate network traffic, execute processes, or access files in ways that differ from standard business operations.

However, the major challenge in anomaly detection is the "Normal-Bad" phenomenon. Not all anomalies are malicious. A sysadmin running a rare diagnostic script, a sudden spike in traffic due to a new software rollout, or a user logging in while traveling abroad all create anomalies. Tuning anomalies to reduce False Positives (FPs) is the hardest part of the job.

## 3. Types of Baselines in an Enterprise

### 3.1 Endpoint Baselines
Endpoint baselines focus on the behavior of individual hosts (workstations and servers).
- **Process Execution & Lineage:** What processes normally run on this machine? What are their parent-child relationships?
  - *Normal:* `winword.exe` spawning `splwow64.exe` (print spooler).
  - *Anomaly:* `winword.exe` spawning `cmd.exe` or `powershell.exe`.
- **Network Connections by Process:** Which processes normally communicate over the network?
  - *Normal:* `chrome.exe` connecting to port 443.
  - *Anomaly:* `notepad.exe` or `svchost.exe` (without specific flags) connecting to an external IP on port 443.
- **Registry Modifications:** What keys are normally altered during boot or login?
- **File System Monitoring:** Which directories typically see high write volumes?

### 3.2 Network Baselines
Network baselines look at the aggregate traffic flowing through switches, routers, and firewalls.
- **Volume Metrics:** What is the normal ratio of inbound to outbound traffic? A sudden spike in outbound traffic (e.g., 50GB leaving a database server that normally sends 1GB a day) might indicate data exfiltration.
- **Protocol Usage:** What protocols are standard in the environment? Is someone suddenly using RDP over a non-standard port, or tunneling SSH over DNS?
- **Beaconing Behavior:** C2 frameworks often communicate at regular intervals. Analyzing the standard deviation of inter-arrival times for network packets between a host and an external IP can reveal automated beaconing.

### 3.3 User and Entity Behavior Analytics (UEBA)
UEBA focuses on human behavior and identity.
- **File Access:** Does a user in Marketing suddenly start accessing thousands of files in the Engineering department's SharePoint?
- **Geographic Location:** Impossible travel scenarios (e.g., a login from New York and a login from Tokyo 10 minutes later).
- **Time of Day:** Does a user who historically works 9-to-5 suddenly log in at 3:00 AM on a Sunday to run administrative commands?

### 3.4 Cloud Environment Baselines
- **API Call Rates:** What is the normal volume of AWS `Describe*` or `List*` API calls?
- **Resource Spawning:** How often are new EC2 instances or Lambda functions created?
- **IAM Modifications:** How frequently are new administrative roles created or assigned?

## 4. Methodologies for Establishing Baselines

### Step 1: Data Collection and Aggregation
You must gather high-fidelity data over a sufficient time window. A baseline established over 24 hours is useless due to weekend/weekday variations. A standard baseline requires at least 14 to 30 days of data collection. Tools used include Sysmon, EDR sensors, Zeek (for network data), and Active Directory logs.

### Step 2: Feature Engineering
Raw logs are rarely useful for mathematical modeling. You must extract "features" (data points).
For example, if analyzing network traffic for C2 beacons, the features might be:
- Average bytes sent per session.
- Standard deviation of time between connections.
- Distinct number of User-Agents used by the source IP.
- The ratio of HTTP GET vs POST requests.

### Step 3: Statistical and Machine Learning Models
Hunters use various techniques to model the data:
- **Statistical Profiling:** Using simple metrics like Mean, Median, Mode, and Standard Deviation (e.g., Median Absolute Deviation - MAD). Alerts trigger when a value exceeds 3 standard deviations from the mean (the 68-95-99.7 rule).
- **Time-Series Analysis:** Algorithms like ARIMA (AutoRegressive Integrated Moving Average) to account for seasonality (e.g., traffic naturally drops at night and on weekends).
- **Clustering (e.g., K-Means, DBSCAN):** Grouping similar behaviors together. Outliers that do not fit into any cluster are flagged for investigation.
- **Long Tail Analysis:** Stacking data by frequency. The "long tail" consists of events that occur very rarely. Threat hunters love the long tail because malware execution is often a rare event compared to normal OS processes.

## 5. Real-World Attack Scenario

### The Scenario: Detecting an APT's Custom Command and Control

**The Attack:**
An Advanced Persistent Threat (APT) group compromises a Linux server via an unpatched web application vulnerability. They drop a custom, never-before-seen C2 implant. Because it's a zero-day implant, no threat intelligence feeds have the hash, IP, or domain. EDR signature engines see nothing wrong because the binary does not match any known signatures.

**The Hunt (Baseline & Anomaly Detection):**
1. **Network Baseline Deviation:** The threat hunter runs a weekly script that analyzes the byte ratio (Bytes Out / Bytes In) for all DMZ servers. Historically, the compromised web server receives large requests (uploads) and sends small responses, or serves standard HTML (ratio of 1:10). Over the last 48 hours, the ratio flipped. The server is consistently sending out steady 50KB chunks every hour over port 443 to a previously unseen external IP address.
2. **Process Baseline Deviation:** The hunter pivots to the endpoint logs (Auditd/Sysmon for Linux). They look at the "Long Tail" of network-connected processes. The web server normally only uses `nginx` and `php-fpm` for outbound connections. However, a process named `kworker/u4:2` (a common masquerade name used by malware to look like a legitimate kernel thread) is initiating the outbound TLS connections.
3. **Resolution:** The hunter isolates the process, extracts the binary from memory, and identifies the custom C2 implant. The attack was caught entirely through anomaly detection, completely bypassing the need for prior knowledge of the threat.

## 6. ASCII Diagram: Baseline and Anomaly Architecture

```text
[ Raw Data Sources ]
  |-- EDR/Sysmon Logs
  |-- Zeek/Firewall Traffic
  |-- AD/IdP Authentication Logs
         |
         v
[ Data Aggregation & Normalization ] ---> (SIEM / Data Lake)
         |
         | (Collect data over a 14-30 Day Window)
         v
[ Feature Extraction Pipeline ]
  |-- Extract: Time of Day
  |-- Extract: Connection Frequency
  |-- Extract: Process Lineage (Parent -> Child)
         |
         v
[ Baseline Modeling Engine ]
  |-- Statistical Averages (Mean, MAD)
  |-- K-Means Clustering for Peer Groups
  |-- Time-Series Forecasting for Traffic Volume
         |
         |----------------------------------\
         v                                  v
[ Real-Time Stream Processing ]     [ Historical Hunt Queries ]
  | (Compares live streaming data)    | (Long-tail analysis)
  | (to the established baseline)     | (Frequency stacking)
         |                                  |
         v                                  v
    [ Anomaly Detected: Deviation > Set Threshold ]
                     |
                     v
             [ Triage & Investigation ]
                     |
            [ True Positive? ]
               /          \
            YES            NO
            /                \
   [ Incident Response ]   [ Tune Baseline / Add Exceptions ]
```

## 7. Tuning and Managing Baseline Drift

IT environments are organic; they change constantly. Software is updated, new employees are hired, network architectures shift to the cloud, and business practices evolve. This causes **Baseline Drift**, where what was once considered anomalous slowly becomes the new normal.

- **Continuous Learning:** Baselines must be rolling. A 30-day baseline should drop the oldest day and add the newest day continuously. Static baselines become obsolete in weeks.
- **Contextual Tuning:** When a false positive occurs, hunters must add highly specific exclusions rather than broad whitelists.
  - *Bad Practice:* Whitelisting `powershell.exe` because it causes too many alerts.
  - *Good Practice:* Whitelisting `powershell.exe` *only* when the `ParentImage` is `sccm.exe`, the `CommandLine` contains `-ExecutionPolicy Bypass`, and it is running from the `C:\AdminScripts\` directory.
- **Peer Grouping:** Compare entities to their peers rather than the global average. A developer compiling code looks anomalous compared to the company average, but normal when compared to the baseline of other developers.

## 8. Chaining Opportunities
- **[[06 - The Pyramid of Pain in Hunting]]**: Anomaly detection enables hunters to target the very top of the pyramid (TTPs), as behavioral anomalies are much harder for attackers to hide than simple static indicators like IPs and Hashes.
- **[[10 - Data Sources Endpoint Network and Cloud]]**: You cannot establish a baseline without deep, parsed, and reliable data sources. Zeek and Sysmon are the lifeblood of anomaly detection.
- **[[12 - Long Tail Analysis and Stacking]]**: Stacking is the primary manual technique used by threat hunters to identify deviations from normal baselines.

## 9. Related Notes
- [[22 - Beaconing Analysis and Network Threat Hunting]]
- [[25 - Utilizing Machine Learning in SOC Environments]]
- [[31 - User and Entity Behavior Analytics UEBA Frameworks]]
- [[40 - Detecting Living off the Land LOLBins]]
