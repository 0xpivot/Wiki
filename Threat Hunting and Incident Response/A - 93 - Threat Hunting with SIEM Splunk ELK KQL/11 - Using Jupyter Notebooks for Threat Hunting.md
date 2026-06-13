---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.11 Using Jupyter Notebooks for Threat Hunting"
---

# 93.11 Using Jupyter Notebooks for Threat Hunting

## Table of Contents
1. [Introduction to Data-Driven Threat Hunting](#introduction-to-data-driven-threat-hunting)
2. [Why Use Jupyter for Threat Hunting?](#why-use-jupyter-for-threat-hunting)
3. [Architecture and Data Flow](#architecture-and-data-flow)
4. [Essential Tools and Libraries Ecosystem](#essential-tools-and-libraries-ecosystem)
5. [Setting Up the Hunting Environment](#setting-up-the-hunting-environment)
6. [Connecting to SIEM Data Sources](#connecting-to-siem-data-sources)
7. [Advanced Hunting Techniques Using Pandas](#advanced-hunting-techniques-using-pandas)
8. [Threat Intelligence Enrichment](#threat-intelligence-enrichment)
9. [Visualizing the Attack](#visualizing-the-attack)
10. [Real-World Attack Scenario](#real-world-attack-scenario)
11. [Troubleshooting and Pitfalls](#troubleshooting-and-pitfalls)
12. [Chaining Opportunities](#chaining-opportunities)
13. [Related Notes](#related-notes)

## 1. Introduction to Data-Driven Threat Hunting
Traditional Security Information and Event Management (SIEM) systems provide powerful query languages (like SPL, KQL, and EQL) and built-in dashboards. However, as threat hunting evolves, analysts often encounter limitations when dealing with highly complex statistical analysis, advanced multi-dimensional visualizations, or iterative ad-hoc data manipulation across disjointed datasets. Jupyter Notebooks bridge this critical gap by bringing the full power of the Python data science ecosystem directly into the threat hunter's workflow.

By leveraging Jupyter Notebooks, threat hunters transform from simple log reviewers into security data scientists, applying rigorous analytical methods to uncover stealthy adversaries.

## 2. Why Use Jupyter for Threat Hunting?
- **Data Source Agnosticism:** You can query multiple, completely disparate data sources simultaneously (e.g., merging Splunk SIEM logs with CrowdStrike EDR telemetry and an internal SQLite asset database) and join them in a single Pandas DataFrame.
- **Advanced Data Transformations:** Using Pandas and Dask, you can pivot, melt, group, and resample data in ways that are computationally prohibitive or syntactically impossible in native SIEM interfaces.
- **Machine Learning Integration:** Utilize Scikit-Learn, PyTorch, or TensorFlow for bespoke anomaly detection without relying on the SIEM’s built-in (and often inflexible) ML toolkits.
- **Reproducibility and Documentation:** A Jupyter Notebook acts as a living document. Code, markdown text, and output graphs are saved together, creating a perfectly reproducible hunt playbook that can be shared, peer-reviewed, and version-controlled.

## 3. Architecture and Data Flow

The following ASCII diagram illustrates the overarching data flow when integrating Jupyter Notebooks into a mature Threat Hunting pipeline:

```text
+---------------------+        +-----------------------+        +---------------------+
|   Data Sources      |        |   Jupyter Notebook    |        |   External Context  |
|                     |        |  (Hunter's Workspace) |        |                     |
|  +---------------+  | API/   |  +-----------------+  |  API   |  +---------------+  |
|  | Splunk SIEM   |--|--------|->| Data Retrieval  |--|--------|->| Threat Intel  |  |
|  +---------------+  | Query  |  | (MSTICPy/REST)  |  |        |  | (VirusTotal,  |  |
|                     |        |  +-----------------+  |        |  | OTX, X-Force) |  |
|  +---------------+  |        |           |           |        |  +---------------+  |
|  | ELK Stack     |--|--------|-----------+           |        |                     |
|  +---------------+  |        |           v           |        +---------------------+
|                     |        |  +-----------------+  |
|  +---------------+  |        |  | Data Processing |  |
|  | MS Sentinel   |--|--------|->| (Pandas/NumPy)  |  |
|  +---------------+  |        |  +-----------------+  |
+---------------------+        |           |           |
                               |           v           |
                               |  +-----------------+  |
                               |  | Analysis &      |  |
                               |  | Visualization   |  |
                               |  +-----------------+  |
                               +-----------------------+
```

## 4. Essential Tools and Libraries Ecosystem

### MSTICPy (Microsoft Threat Intelligence Center Python Security Tools)
MSTICPy is a library designed specifically for threat hunting and incident response in Jupyter Notebooks. It drastically reduces the boilerplate code required to execute complex hunts.
Key capabilities include:
- **Query Providers:** Native connectors for Azure Sentinel, Splunk, Microsoft Defender, and local files (CSV, JSON, XML).
- **Threat Intel Lookups:** Built-in integrations with major TI providers.
- **Time Series Analysis:** Anomaly detection on time-series log data.
- **Event Timeline Visualization:** Interactive Bokeh plots tailored for security events.

### Data Manipulation and Visualization
- **Pandas:** The backbone of data manipulation in Python. Essential for filtering, grouping, and transforming log data.
- **NumPy:** For high-performance mathematical operations on numerical log data (e.g., bytes transferred).
- **Bokeh & Plotly:** Used for creating rich, interactive visualizations, such as timelines of attacker activity or heatmaps of authentication failures.
- **NetworkX:** Useful for graphing active directory relationships (like BloodHound data) or network traffic patterns.

## 5. Setting Up the Hunting Environment
To ensure a clean, reproducible environment, it is highly recommended to use Python virtual environments or Docker containers for hunting notebooks.

```bash
# Create a virtual environment
python3 -m venv threat_hunt_env
source threat_hunt_env/bin/activate

# Install core libraries
pip install jupyterlab pandas numpy msticpy bokeh plotly elasticsearch splunk-sdk
```

## 6. Connecting to SIEM Data Sources

### Connecting to Splunk
To query Splunk from Jupyter, you can use the official Splunk Python SDK or MSTICPy. MSTICPy handles the parsing and conversion to Pandas DataFrames automatically.

```python
# Using MSTICPy to connect to Splunk
from msticpy.data import QueryProvider
import pandas as pd

# Initialize the Splunk provider
splunk_prov = QueryProvider("Splunk")

# Connect using configuration in msticpyconfig.yaml
# Ensure your Splunk REST API port (default 8089) is accessible
splunk_prov.connect()

# Execute a query targeting successful logons
query = '''
search index=windows sourcetype=WinEventLog:Security EventCode=4624
| stats count by TargetUserName, IpAddress, WorkstationName
| sort - count
'''
df_logins = splunk_prov.exec_query(query)
display(df_logins.head())
```

### Connecting to ElasticSearch (ELK)
When hunting in an ELK environment, you can use the native Python `elasticsearch` client.

```python
from elasticsearch import Elasticsearch
import pandas as pd

# Connect to ES cluster securely
es = Elasticsearch(
    ["https://siem.corp.local:9200"], 
    basic_auth=("soc_hunter", "SecureHunterPass!"),
    verify_certs=True
)

# Define an Elasticsearch DSL query for process creation
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"event.code": "4688"}},
                {"range": {"@timestamp": {"gte": "now-7d", "lte": "now"}}}
            ]
        }
    }
}

# Fetch results
res = es.search(index="winlogbeat-*", body=query, size=10000)

# Convert nested JSON to a flat Pandas DataFrame
logs = [hit['_source'] for hit in res['hits']['hits']]
df_processes = pd.json_normalize(logs)
display(df_processes.head())
```

## 7. Advanced Hunting Techniques Using Pandas

Once data is residing in a Pandas DataFrame, threat hunters can perform complex mathematical and statistical analyses that are incredibly difficult in standard SIEM query languages.

### Identifying Rare Processes and Outliers
Adversaries often use rare or uniquely named binaries. We can find processes that occur very infrequently across the environment.

```python
# Assuming df contains process execution logs with 'process.name' and 'host.name'
process_counts = df_processes['process.name'].value_counts()

# Identify processes that executed less than 3 times globally in 7 days
rare_processes = process_counts[process_counts < 3].index.tolist()

# Filter original dataframe for these rare processes
df_rare = df_processes[df_processes['process.name'].isin(rare_processes)]

# Display the hosts running these rare processes
print("Rare processes identified on hosts:")
display(df_rare[['@timestamp', 'host.name', 'process.name', 'process.command_line']])
```

### Time-Series Anomaly Detection (Moving Averages)
Detecting stealthy spikes in failed logins or unusual data transfer volumes over time.

```python
# Ensure timestamp is a datetime object
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Resample data by hour and count events
df_hourly = df.set_index('timestamp').resample('1H').size().reset_index(name='event_count')

# Calculate 24-hour moving average and standard deviation
df_hourly['rolling_mean'] = df_hourly['event_count'].rolling(window=24).mean()
df_hourly['rolling_std'] = df_hourly['event_count'].rolling(window=24).std()

# Define anomaly threshold (e.g., counts greater than 3 standard deviations above the mean)
df_hourly['is_anomaly'] = df_hourly['event_count'] > (df_hourly['rolling_mean'] + 3 * df_hourly['rolling_std'])

anomalies = df_hourly[df_hourly['is_anomaly'] == True]
display(anomalies)
```

## 8. Threat Intelligence Enrichment
A major benefit of Jupyter is seamlessly enriching Indicators of Compromise (IOCs) found during the hunt without switching tabs or manually pasting into web portals.

```python
from msticpy.sectools import TILookup

# Initialize Threat Intel Lookup provider
ti_lookup = TILookup()

# Extract a list of unique external IP addresses from our log data
suspicious_ips = df_network['destination_ip'].unique().tolist()

# Perform bulk lookup against configured providers (e.g., VirusTotal, AlienVault OTX)
ti_results = ti_lookup.lookup_iocs(data=suspicious_ips, providers=["VirusTotal", "OTX"])

# Filter for IPs with a high severity score
malicious_ips = ti_results[ti_results['Severity'].isin(['High', 'Severe'])]
display(malicious_ips[['Ioc', 'Provider', 'Result', 'Severity']])
```

## 9. Visualizing the Attack
Visualization is key to understanding the timeline and scope of a breach.

```python
from msticpy.nbtools import nbdisplay

# Create an interactive timeline of process executions
nbdisplay.display_timeline(
    data=df_rare,
    time_column='@timestamp',
    source_columns=['host.name', 'process.name', 'process.command_line'],
    title='Timeline of Rare Process Executions'
)
```

## 10. Real-World Attack Scenario

### Scenario: Hunting for Living off the Land (LotL) Techniques
**Context:** The SOC received a vague tip from a government intelligence agency about a potential compromise. No specific IOCs (domains, IPs, or hashes) were provided, but the adversary is suspected to heavily utilize native Windows binaries (obfuscated PowerShell and WMI) to remain undetected.

**The Hunt Execution via Jupyter:**
1. **Data Ingestion:** The threat hunter extracts all process creation events (Event ID 4688 / Sysmon 1) involving `powershell.exe`, `cmd.exe`, `wmic.exe`, and `certutil.exe` over the last 30 days into a Jupyter Notebook Pandas DataFrame.
2. **Feature Extraction (The "Math" Phase):** The hunter writes custom Python functions to calculate the Shannon entropy of the command lines and the total length of the arguments. High entropy often indicates Base64 encoding or heavy obfuscation.
   ```python
   import math
   from collections import Counter

   def calculate_entropy(text):
       if not text: return 0
       p, lns = Counter(text), float(len(text))
       return -sum( count/lns * math.log(count/lns, 2) for count in p.values())

   # Apply function to the entire dataset rapidly
   df['cmd_entropy'] = df['command_line'].apply(calculate_entropy)
   df['cmd_length'] = df['command_line'].apply(len)
   ```
3. **Filtering and Discovery:** The hunter filters the DataFrame for command lines with entropy > 5.8 and length > 300 characters. 
4. **Analysis:** The output surfaces several highly anomalous, Base64-encoded PowerShell commands running under the context of a public-facing IIS Web Server's service account.
5. **Deobfuscation:** Right within the notebook, the hunter writes a script to decode the Base64 payload, revealing an attempt to download and execute a Cobalt Strike beacon from an external IP address.
6. **Enrichment:** Running the extracted IP address through the MSTICPy `TILookup` module confirms it is a known Cobalt Strike Team Server.
7. **Reporting:** The hunter exports the notebook to HTML, creating an instant, mathematically backed incident report for the SOC managers and Incident Response teams.

## 11. Troubleshooting and Pitfalls
- **Memory Management:** Attempting to pull 30 days of raw network flow logs directly into Pandas will likely cause an Out-Of-Memory (OOM) error. Use the SIEM's query language to aggregate and pre-filter data *before* pulling it into Jupyter.
- **Authentication Timeouts:** Long-running hunts may suffer from SIEM API token expiration. Implement try-catch blocks to refresh tokens dynamically.
- **Data Privacy:** DataFrames often cache sensitive data (PII, passwords in cleartext logs). Use tools like `nbstripout` to strip output cells before committing notebooks to shared Git repositories.

## 12. Chaining Opportunities
- Insights and anomalies identified through exploratory data analysis in Jupyter Notebooks should be operationalized into permanent SIEM correlation rules, as detailed in `[[13 - Designing High-Fidelity Alerting Rules]]`.
- Features engineered in Python (like command-line entropy) can be used as inputs for training the machine learning models discussed in `[[12 - Machine Learning for Log Anomaly Detection]]`.

## 13. Related Notes
- `[[12 - Machine Learning for Log Anomaly Detection]]`
- `[[13 - Designing High-Fidelity Alerting Rules]]`
- `[[14 - Creating Honeytokens and Deception Decoys]]`
- `[[15 - Case Study Tracking APT29 across a SIEM]]`
