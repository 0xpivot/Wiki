---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.10 Normalizing Data Sources Common Information Model CIM"
---
# 93.10 Normalizing Data Sources: Common Information Model (CIM)

## Overview
A Security Operations Center (SOC) ingests telemetry from a vast array of heterogeneous sources: Windows Event Logs, Linux Syslog, Cisco Firewalls, Palo Alto proxies, AWS CloudTrail, and diverse EDR platforms. Without normalization, every device calls the same concept by a different name. Windows calls an IP address `IpAddress`, a Cisco ASA calls it `IP_Address`, and an Apache web server calls it `clientip`. 

If a threat hunter wants to find a specific IP address across all network segments, they would have to write an exponentially complex query using endless `OR` statements for every specific vendor field name. Data normalization solves this problem by enforcing a standardized schema. Frameworks like the Splunk Common Information Model (CIM), the Elastic Common Schema (ECS), and Microsoft Sentinel's Advanced Security Information Model (ASIM) are critical architectural requirements for scalable threat hunting and correlation.

## The Normalization Problem

Imagine writing a detection for a simple brute-force attack across multiple authentication systems.

**Without Normalization (The Nightmare):**
```spl
(index=windows EventCode=4625 user=jdoe) OR 
(index=linux process=sshd status=failed username=jdoe) OR 
(index=okta event_type=user.session.start outcome.result=FAILURE actor.alternateId=jdoe)
```
This is unmaintainable. Every time a new technology is added, every single correlation search in the SIEM must be rewritten.

**With Normalization (The Solution):**
```spl
| tstats count from datamodel=Authentication where Authentication.action=failure Authentication.user=jdoe by Authentication.src
```
With a normalized schema, the search queries the *concept* of authentication, entirely agnostic to the underlying vendor technology.

## ASCII Architecture: The Normalization Pipeline

```text
+----------------+       +----------------+       +----------------+
|  Vendor A Log  |       |  Vendor B Log  |       |  Vendor C Log  |
| (user=admin)   |       | (username=adm) |       | (usr=admin)    |
+----------------+       +----------------+       +----------------+
        |                        |                        |
        +------------------------+------------------------+
                                 |
                                 v
                 +-------------------------------+
                 |       Parsing & Extraction    | (e.g. Splunk props.conf / transforms.conf)
                 |       (Regex, JSON Parse)     | (e.g. Logstash grok patterns)
                 +-------------------------------+
                                 |
                                 v
                 +-------------------------------+
                 |       Field Aliasing & Eval   | (Mapping specific fields to CIM/ECS fields)
                 | user -> src_user              |
                 | username -> src_user          |
                 | usr -> src_user               |
                 +-------------------------------+
                                 |
                                 v
                 +-------------------------------+
                 |       Tagging / Categorization| (e.g. tag=authentication)
                 +-------------------------------+
                                 |
                                 v
                 +-------------------------------+
                 |    Data Model / Schema Layer  | (Splunk Datamodels, Sentinel ASIM Parsers)
                 |  [ Normalized Search Plane ]  |
                 +-------------------------------+
```

## Major Normalization Frameworks

### 1. Splunk Common Information Model (CIM)
The Splunk CIM relies heavily on search-time (schema-on-read) normalization using configuration files (`props.conf`, `tags.conf`, `eventtypes.conf`).
- **Eventtypes and Tags:** Splunk uses eventtypes to group similar logs, and tags to map them to specific data models. For example, a Windows Logon event gets tagged with `authentication`.
- **Field Aliases:** `FIELDALIAS` configurations map vendor-specific fields to CIM-compliant fields (e.g., `FIELDALIAS-dest = DestinationIp AS dest`).
- **Datamodels & `tstats`:** Datamodels are hierarchical structures that map the CIM. Splunk accelerates these datamodels, storing highly optimized summaries. Using the `tstats` command against accelerated datamodels is exponentially faster than standard raw searches.

### 2. Elastic Common Schema (ECS)
Unlike Splunk, Elastic primarily enforces schema-on-write. Data must be transformed *before* or *during* indexing (via Logstash or Ingest Node Pipelines) into the ECS format.
- ECS is highly structured and nested (e.g., `source.ip`, `user.name`, `process.command_line`).
- This approach requires more upfront engineering but results in incredibly fast query performance because the data is perfectly structured on disk.

### 3. Microsoft Sentinel Advanced Security Information Model (ASIM)
Sentinel uses Kusto (KQL) parsing functions to achieve normalization at search-time, bridging the gap between raw tables and normalized views.
- ASIM provides standardized views (e.g., `_Im_Dns`, `_Im_NetworkSession`, `_Im_ProcessEvent`).
- When a user queries `_Im_NetworkSession`, Sentinel dynamically executes KQL functions under the hood to pull and unify data from Azure Firewalls, Palo Alto, AWS VPC Flow Logs, etc., presenting them in a unified schema (e.g., `SrcIpAddr`, `DstIpAddr`).

## Deep Dive: Normalization Mechanics in Splunk

To normalize a custom firewall log into the Splunk Network Traffic CIM datamodel:

**1. Create Eventtype (`eventtypes.conf`):**
```ini
[custom_fw_traffic]
search = sourcetype=custom_firewall action=*
```

**2. Assign Tags (`tags.conf`):**
```ini
[eventtype=custom_fw_traffic]
network = enabled
communicate = enabled
```
*(These specific tags tell Splunk this log belongs to the Network Traffic datamodel).*

**3. Map Fields (`props.conf`):**
```ini
[custom_firewall]
FIELDALIAS-src = Source_IP_Address AS src
FIELDALIAS-dest = Destination_IP_Address AS dest
FIELDALIAS-action = FW_Action AS action
EVAL-transport = lower(Protocol_Type)
EVAL-app = "CustomAppliance"
```

## Real-World Attack Scenario

### Scenario: Tracking Lateral Movement Across Diverse Environments
A threat actor compromises a low-privileged Linux web server in AWS. They steal an API key, move to an Azure environment, compromise a Windows Virtual Desktop, and finally access an on-premise proprietary database. 

### Hunting Without Normalization
The hunter would have to write multiple complex, distinct queries for AWS CloudTrail, Azure Activity, Windows Event Logs, and Cisco core switch logs, manually trying to correlate timestamps and user identities.

### Hunting With Normalization (Splunk CIM Example)
Because the SOC engineering team successfully mapped AWS, Azure, Windows, and Linux authentication logs to the `Authentication` datamodel, and all endpoint process execution to the `Endpoint` datamodel, the hunter can execute a unified, cross-platform trace.

```spl
| tstats `summariesonly` count min(_time) as first_seen max(_time) as last_seen 
  from datamodel=Authentication 
  where Authentication.action=success 
  by Authentication.user, Authentication.src, Authentication.dest, Authentication.app
| sort first_seen
```
*Result:* The analyst immediately sees a timeline of the exact same user identity authenticating successfully from AWS -> Azure -> On-Premise. 

Pivoting to track execution across platforms:
```spl
| tstats `summariesonly` count 
  from datamodel=Endpoint.Processes 
  where Processes.user="jdoe" 
  by Processes.dest, Processes.process_name, Processes.process
```
*Result:* This single query returns the bash commands executed on the Linux web server AND the PowerShell commands executed on the Azure Windows VM, unified under the `Processes.process` field.

## Challenges and Pitfalls
1. **Performance Overhead (Schema-on-Read):** In Splunk, relying on heavy `eval` statements at search-time for normalization can severely degrade search performance. Data model acceleration is mandatory for performance, but it consumes significant storage space.
2. **Incomplete Mapping:** If an engineer maps the IP address but forgets to map the `action` field (e.g., blocked vs allowed) to the firewall datamodel, correlation searches relying on `action=allowed` will blindly ignore those logs, creating massive visibility gaps.
3. **Over-Normalization:** Forcing highly unique, complex log sources (like deep application debug logs) into a generic CIM model often results in losing critical context. Normalization is for common security concepts (Auth, Network, Process, DNS); keep specialized logs raw or create custom, documented schemas.

## Chaining Opportunities
- Normalized data is a prerequisite for feeding threat intelligence effectively into a SIEM. See [[08 - Integrating MISP with Splunk ELK]].
- SOAR platforms rely entirely on normalized field names to execute playbooks reliably regardless of the alerting technology. See [[09 - SOAR Security Orchestration and Automated Response]].
- For Microsoft Sentinel, ASIM normalization allows for advanced KQL correlations across diverse tables. See [[07 - Advanced KQL Joins and Time-Series Analysis]].

## Related Notes
- [[01 - SIEM Architecture and Deployment Strategies]]
- [[04 - Threat Hunting Methodologies]]
- [[07 - Advanced KQL Joins and Time-Series Analysis]]
- [[08 - Integrating MISP with Splunk ELK]]
- [[09 - SOAR Security Orchestration and Automated Response]]
