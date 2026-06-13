---
tags: [threat-hunting, siem, splunk, elk, vapt]
difficulty: advanced
module: "93 - Threat Hunting with SIEM: Splunk, ELK, KQL"
topic: "93.08 Integrating MISP with Splunk ELK"
---
# 93.08 Integrating MISP with Splunk & ELK

## Overview
The Malware Information Sharing Platform (MISP) is an open-source threat intelligence platform (TIP) widely used by SOCs, CERTs, and intelligence communities globally. It facilitates the collection, storage, distribution, and sharing of cyber security indicators and threats (IOCs). However, threat intelligence isolated within a TIP is practically useless for real-time defense. To operationalize MISP, it must be deeply integrated into the Security Information and Event Management (SIEM) systems, such as Splunk and the Elastic Stack (ELK). 

This document explores the advanced architectural integration, API interaction, data normalization, and hunting strategies required to effectively fuse MISP threat intelligence with real-time log ingestion in Splunk and ELK.

## The Operational Threat Intelligence Lifecycle
Operationalizing MISP involves three core phases:
1. **Aggregation & Normalization:** Ingesting STIX/TAXII feeds, OSINT, and proprietary intelligence into MISP, where it is mapped to the MISP core format.
2. **Distribution (SIEM Integration):** Pushing or pulling these structured indicators (IPs, hashes, domains, URLs) from MISP into the SIEM's high-speed lookup tables or specialized indices.
3. **Actionable Correlation:** Continuously matching incoming live telemetry (firewall logs, EDR telemetry, proxy logs) against the imported threat intelligence to generate high-fidelity alerts.

## ASCII Architecture: MISP to SIEM Integration Pipeline

```text
+---------------------+      +-----------------------------------------+
| OSINT / ISAC Feeds  |      |             MISP Instance               |
| (STIX, TAXII, CSV)  | ===> | [Event DB] <--> [Attribute DB] <--> API |
+---------------------+      +-----------------------------------------+
                                         ||                    ||
                   +---------------------+                     +---------------------+
                   |                                                                 |
                   V                                                                 V
+-----------------------------------+               +-----------------------------------+
|         Splunk Enterprise         |               |           Elastic Stack           |
|-----------------------------------|               |-----------------------------------|
| 1. MISP Modular Input App         |               | 1. Logstash HTTP Poller           |
| 2. Threat Intel Framework (ES)    |               | 2. Elastic Filebeat Threat Intel  |
| 3. KV Store / CSV Lookups         |               | 3. Elasticsearch Indexing         |
| 4. SPL Correlation Searches       |               | 4. Kibana Alerting (EQL/KQL)      |
+-----------------------------------+               +-----------------------------------+
                   ||                                                 ||
                   ====================================================
                                         ||
                                         V
                        +-----------------------------------+
                        |   SOC Automation & Triage (SOAR)  |
                        +-----------------------------------+
```

## Integrating MISP with Splunk

### Method 1: The Splunk App for MISP (Modular Input)
The most direct way to integrate MISP into a standard Splunk deployment is via the Splunk App for MISP. This application uses custom Python modular inputs to query the MISP REST API and index the results into a dedicated Splunk index (e.g., `index=misp`).

**Configuration Steps:**
1. Install the TA-MISP add-on on the Splunk Heavy Forwarder or Search Head.
2. Configure the connection using the MISP Base URL and the MISP Automation Key.
3. Define the data inputs. You can filter the data pulled from MISP based on Tags (e.g., `tlp:green`, `type:osint`), Published status, and Date ranges.

### Method 2: Splunk Enterprise Security (ES) Threat Intelligence Framework
For mature SOCs utilizing Splunk Enterprise Security, the optimal approach is integrating MISP directly into the ES Threat Intelligence Framework. This allows MISP indicators to automatically populate ES threat intel KV Store collections, enabling native Threat Match correlation searches.

1. In Splunk ES, navigate to `Configure -> Data Enrichment -> Threat Intelligence Downloads`.
2. Configure a new download using the MISP API endpoint for CSV/STIX export.
   - Example MISP URL: `https://<misp-ip>/events/csv/download/<api-key>/attributes/domain/false/false`
3. Map the columns from the MISP output to the Splunk Common Information Model (CIM) threat intelligence fields (e.g., mapping MISP `value` to Splunk `domain`).
4. ES handles the periodic polling, deduplication, and integration into the `threat_intel_by_domain` lookups.

### SPL Hunting Example: Correlating Proxy Logs with MISP Domains
```spl
index=proxy sourcetype=squid:access
| rename url as requested_url
| lookup misp_domain_lookup domain as requested_url OUTPUT event_id, threat_actor, tag
| search event_id=* // Filters for only logs that had a MISP match
| stats count, values(threat_actor) as Actor, values(tag) as Context by src_ip, requested_url
| where count > 5
```

## Integrating MISP with Elastic Stack (ELK)

### Method 1: Elastic Agent & Filebeat Threat Intel Module
Elastic provides native support for MISP via the Threat Intel module in Filebeat and the modern Elastic Agent. This is the recommended approach for modern Elastic deployments.

**Filebeat Configuration (`filebeat.yml`):**
```yaml
filebeat.modules:
- module: threatintel
  misp:
    enabled: true
    var.input: httpjson
    var.url: "https://misp.internal.corp/events/restSearch"
    var.api_token: "YOUR_MISP_AUTOMATION_KEY"
    var.ssl.verification_mode: none
    var.first_interval: 24h
    var.interval: 60m
    var.tags: ["tlp:amber", "tlp:green"]
```
This configuration polls MISP hourly, pulling recent indicators and natively mapping them to the Elastic Common Schema (ECS), specifically under the `threat.*` fields.

### Method 2: Logstash HTTP Poller
For highly customized pipelines where data needs to be manipulated, enriched, or transformed before indexing, Logstash is utilized.

**Logstash Configuration (`misp-pipeline.conf`):**
```logstash
input {
  http_poller {
    urls => {
      misp_feed => {
        method => get
        url => "https://misp.internal.corp/events/restSearch/returnFormat:json/published:true"
        headers => {
          "Authorization" => "YOUR_MISP_AUTOMATION_KEY"
          "Accept" => "application/json"
        }
      }
    }
    request_timeout => 60
    schedule => { cron => "0 * * * *"} # Run hourly
    codec => "json"
  }
}
filter {
  # Extensive Ruby and Mutate blocks to map MISP JSON to ECS
  mutate {
    add_field => { "[threat][indicator][type]" => "%{[Attribute][type]}" }
    add_field => { "[threat][indicator][value]" => "%{[Attribute][value]}" }
  }
}
output {
  elasticsearch {
    hosts => ["https://es-cluster:9200"]
    index => "misp-threat-intel-%{+YYYY.MM}"
    user => "logstash_internal"
    password => "secure_password"
  }
}
```

## Real-World Attack Scenario

### Scenario: Zero-Day Campaign and Rapid Intelligence Sharing
A new zero-day vulnerability in a widely used VPN appliance is actively being exploited. A partner organization within your ISAC (Information Sharing and Analysis Center) is breached and immediately publishes an incident report containing IP addresses of the attacker's infrastructure, specific user-agent strings used by the exploit toolkit, and MD5 hashes of dropped webshells to a shared MISP instance.

### The Automated Defense Pipeline
1. **Intelligence Ingestion:** The SOC's internal MISP instance is configured to sync with the ISAC's MISP server. Within seconds of the partner organization publishing the event, the IOCs are replicated to the internal MISP instance.
2. **SIEM Synchronization:** The Splunk ES Threat Intelligence framework, configured to poll MISP every 5 minutes via the REST API, pulls the new IP addresses and hashes into the `threat_intel_by_ip` and `threat_intel_by_file_hash` KV stores.
3. **Correlation & Detection:** 
   - A live Splunk correlation search continuously monitoring firewall `Network Traffic` logs immediately triggers when an inbound connection from one of the malicious IPs attempts to connect to the organization's perimeter VPN appliance.
   - An EDR telemetry correlation search triggers when `sysmon` logs report the creation of a file matching the specific MD5 hash of the webshell on an internal server.
4. **Hunting (Retroactive):** The SOC analyst uses SPL to search backward in time (last 30 days) against the newly ingested MISP IOCs to ensure the network wasn't silently breached prior to the intelligence being published.

```spl
// Retroactive Hunt in Splunk
index=firewall OR index=edr
| eval normalized_ip = coalesce(src_ip, dest_ip, endpoint_ip)
| eval normalized_hash = coalesce(md5, file_hash)
| lookup misp_intel_lookup ioc_value as normalized_ip OUTPUT ioc_type, misp_event_id, misp_tags
| lookup misp_intel_lookup ioc_value as normalized_hash OUTPUT ioc_type, misp_event_id, misp_tags
| search misp_event_id=*
| stats earliest(_time) as first_seen, latest(_time) as last_seen, count by normalized_ip, normalized_hash, misp_event_id, misp_tags
```

## Best Practices and Pitfalls
1. **Indicator Decay and Aging:** Threat intelligence is inherently ephemeral. IP addresses change hands, and domains are sinkholed. Integrating MISP without a mechanism to expire or remove old indicators will result in an exponential increase in false positives. Utilize MISP's `Sightings` and `Decay Models` to automatically lower the confidence score of aging IOCs, and filter SIEM pulls based on these scores.
2. **Context is King:** Importing raw IPs without context (tags, event descriptions, threat actor attribution) turns your SIEM into a noisy IDS. Always import and map contextual fields so analysts understand *why* an IP is malicious.
3. **The "Too Much Data" Problem:** Pulling the entire MISP database into a SIEM lookup will crash the lookup tables. Filter API calls aggressively based on `published: true`, relevant tags (e.g., dropping generic spam lists if focusing on APTs), and a specific time horizon (e.g., IOCs generated in the last 90 days).

## Chaining Opportunities
- The actionable alerts generated from MISP/SIEM integration should be automatically routed to SOAR platforms for containment. See [[09 - SOAR Security Orchestration and Automated Response]].
- To effectively match MISP indicators across diverse log types, a normalized data model is required. See [[10 - Normalizing Data Sources Common Information Model CIM]].
- Hunting for these indicators within Microsoft Sentinel utilizes different syntactical approaches. See [[07 - Advanced KQL Joins and Time-Series Analysis]].

## Related Notes
- [[04 - Threat Hunting Methodologies]]
- [[06 - Kusto Query Language KQL Basics in Microsoft Sentinel]]
- [[07 - Advanced KQL Joins and Time-Series Analysis]]
- [[09 - SOAR Security Orchestration and Automated Response]]
- [[10 - Normalizing Data Sources Common Information Model CIM]]
