---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.03 Statistical Outlier Detection in Splunk"
---

# Statistical Outlier Detection in Splunk

## 1. Introduction to Mathematical Hunting

Traditional threat hunting heavily relies on Indicators of Compromise (IoCs)—known bad IP addresses, file hashes, and domains. 
However, Advanced Persistent Threats (APTs) change their infrastructure rapidly, rendering static IoCs obsolete within hours.
To catch modern adversaries, hunters must pivot to **Indicator of Attack (IoA)** hunting, focusing on behavioral anomalies rather than static artifacts.

This is where statistical outlier detection comes into play. 
By applying mathematical models to standard network and endpoint telemetry, hunters can identify behavior that deviates significantly from the established baseline.
If an attacker exfiltrates 50GB of data via DNS over two weeks, no single packet is inherently malicious, but the overall statistical volume is an extreme outlier.

## 2. Core Statistical Concepts for Hunting

Before diving into SPL implementations, hunters must understand the underlying math.

### 2.1 The Normal Distribution and Standard Deviation (Z-Score)
In a normal distribution (the "Bell Curve"), data is clustered around the mean (average).
Standard Deviation ($\sigma$) measures the amount of variation or dispersion of a set of values.
- 68% of data falls within 1 standard deviation of the mean.
- 95% falls within 2 standard deviations.
- 99.7% falls within 3 standard deviations.

A **Z-Score** represents how many standard deviations a data point is from the mean. 
A Z-score $> 3$ or $< -3$ is typically considered a highly suspicious outlier.

### 2.2 Median Absolute Deviation (MAD)
The weakness of standard deviation is that it is heavily skewed by massive outliers.
If one user downloads 1TB of data, the mean shifts so drastically that other exfiltration events might be hidden.
**MAD (Median Absolute Deviation)** is robust against outliers because it uses the median instead of the mean. It calculates the median of the absolute deviations from the dataset's median.

### 2.3 Interquartile Range (IQR)
IQR is another robust statistical measure. It divides data into quartiles.
The IQR is the range between the 75th percentile (Q3) and the 25th percentile (Q1).
Any value that lies $1.5 \times IQR$ above Q3 is considered a statistical outlier.

## 3. ASCII Visualization: The Bell Curve

```text
+-------------------------------------------------------------------+
|                NORMAL DISTRIBUTION (BELL CURVE)                   |
|                                                                   |
|                              |                                    |
|                            . | .                                  |
|                          .   |   .                                |
|                        .     |     .          (Outliers)          |
|                      .       |       .             *              |
|        *           .         |         .                          |
|  (Outliers)      .           |           .                        |
| _________________............|............_____________________   |
|                 -3σ  -2σ  -1σ  μ   +1σ  +2σ  +3σ                  |
|                                                                   |
|  μ = Mean | σ = Standard Deviation                                |
|  Hunting Rule: Alert if Event > μ + (3 * σ)                       |
+-------------------------------------------------------------------+
```

## 4. Implementing Statistical Hunting in Splunk

Splunk provides built-in functions via `stats` and `eventstats` to perform these mathematical calculations efficiently.

### 4.1 Hunting for Exfiltration via Z-Score
This query identifies users who are transferring significantly more outbound data than their historical average.

**SPL Example:**
```splunk
index=network sourcetype=firewall dest_zone=external
| bucket _time span=1d
| stats sum(bytes_out) as daily_bytes by user, _time
| eventstats avg(daily_bytes) as mean_bytes stdev(daily_bytes) as stdev_bytes by user
| eval z_score = (daily_bytes - mean_bytes) / stdev_bytes
| where z_score > 3
| sort - z_score
```
*Insight:* This query calculates daily outbound bytes per user. It then uses `eventstats` to calculate the long-term mean and standard deviation for each user, allowing us to find days where a specific user exceeded their personal baseline by 3 standard deviations.

### 4.2 Detecting C2 Beaconing via Variance
Command and Control (C2) frameworks use automated beacons to "check-in."
These beacons happen at highly regular intervals (e.g., exactly every 60 seconds) with minimal variance.
Human-driven web traffic is highly variable (high variance). Malware is automated (low variance).

**SPL Example:**
```splunk
index=proxy sourcetype=squid action=allowed
| sort 0 _time
| streamstats current=f last(_time) as prev_time by src_ip, dest_domain
| eval time_diff = prev_time - _time
| stats count avg(time_diff) as avg_interval stdev(time_diff) as stdev_interval by src_ip, dest_domain
| eval variance = stdev_interval / avg_interval
| where count > 50 AND variance < 0.1
```
*Insight:* We calculate the time difference between consecutive requests to the same domain. If the variance is incredibly low (`< 0.1`) and the request count is high, it strongly indicates a programmatic, automated C2 beacon.

## 5. Built-in Machine Learning Commands

Splunk offers native commands to simplify outlier detection without requiring manual Z-score calculations.

### 5.1 The `predict` Command
`predict` uses forecasting algorithms (like the Kalman filter) to model historical data and predict future values.
It automatically calculates upper and lower confidence intervals.

```splunk
index=auth action=failure
| timechart count span=1h
| predict count as predicted algorithm=LLP future_timespan=0
| where count > upper95(predicted)
```
*Insight:* This will alert only when the current hour's failed logins exceed the mathematically predicted upper bound for that specific hour, adjusting for time-of-day and day-of-week seasonality.

### 5.2 The `anomalies` Command
The `anomalies` command scores events based on how unexpected they are compared to previous events.
It works exceptionally well on strings and categorical data (like URLs or process parameters) rather than just integers.

## 6. Real-World Attack Scenario

### Scenario: Low-and-Slow Insider Threat Exfiltration
An insider threat at a financial institution decides to steal proprietary source code.
Knowing that the DLP system triggers an alert if more than 1GB is transferred via HTTP in a single day, the insider writes a script to upload exactly 900MB of encrypted archives to a personal cloud storage provider every day over 6 months.

### Detection via Interquartile Range (IQR)
Standard deviation failed to catch this because the data transfer became the "new normal," slowly shifting the mean over 6 months.
The threat hunter deployed an IQR-based detection query looking back 90 days across all peer groups in the engineering department.

1.  **Peer Group Baseline:** The query calculated the daily upload volume for the entire engineering department.
2.  **Quartile Calculation:** It established Q1 (200MB) and Q3 (300MB) for the department.
3.  **IQR Threshold:** The IQR was $300 - 200 = 100MB$. The upper bound limit ($Q3 + 1.5 * IQR$) was set at $300 + 150 = 450MB$.
4.  **Detection:** The insider's consistent 900MB daily transfer violently violated the 450MB mathematical upper bound of the peer group.

Because IQR is resistant to outlier skew, the insider's long-term slow exfiltration could not manipulate the median of the entire department, resulting in a high-fidelity alert.

## 7. Chaining Opportunities

- The robust mathematical baselines generated here should be exported and visualized continuously on the dashboards created in [[01 - Building a Hunting Dashboard in Splunk]].
- Understanding how to chain `streamstats` into `eventstats` for variance calculation is fundamentally reliant on advanced skills covered in [[02 - Advanced Splunk Processing Language SPL for Hunts]].
- Elastic Stack offers similar capabilities via Machine Learning jobs and Pipeline Aggregations, as discussed in [[04 - Introduction to Elastic Stack ELK for Threat Hunting]] and [[05 - Writing Elastic Query DSL and EQL for Detection]].

## 8. Related Notes

- [[01 - Building a Hunting Dashboard in Splunk]]
- [[02 - Advanced Splunk Processing Language SPL for Hunts]]
- [[04 - Introduction to Elastic Stack ELK for Threat Hunting]]
- [[05 - Writing Elastic Query DSL and EQL for Detection]]
- [[Threat Hunting Hypothesis Generation]]
- [[Machine Learning Toolkit (MLTK) Basics]]
