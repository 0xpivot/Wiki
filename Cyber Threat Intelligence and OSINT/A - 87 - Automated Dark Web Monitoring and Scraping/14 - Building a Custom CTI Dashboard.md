---
tags: [darkweb, scraping, automation, vapt]
difficulty: advanced
module: "87 - Automated Dark Web Monitoring and Scraping"
topic: "87.14 Building a Custom CTI Dashboard"
---

# Building a Custom CTI Dashboard

## 1. Introduction to CTI Dashboards

Raw data from dark web scrapers and even structured data from platforms like MISP can overwhelm analysts. A Cyber Threat Intelligence (CTI) Dashboard acts as the "single pane of glass." It translates millions of scraped forum posts, market listings, and parsed metadata into visual intelligence—trends, heatmaps, alerts, and statistical anomalies.

A well-architected dashboard allows a security team to instantly grasp the current threat landscape, answer tactical questions ("Are our executives currently being discussed on hacking forums?"), and identify strategic shifts ("Is there a sudden spike in zero-day exploits being sold for our core tech stack?").

## 2. Technical Stack Selection

Building a high-performance CTI dashboard requires a robust data ingestion and visualization stack. The industry standard is the **ELK Stack (Elasticsearch, Logstash, Kibana)** or alternative combinations like **Prometheus + Grafana** or **Splunk**.

- **Elasticsearch:** A NoSQL, search-engine-based database optimized for full-text search and complex querying of massive datasets (ideal for storing scraped forum posts).
- **Logstash / Fluentd:** The data processing pipeline that ingests raw JSON from the scrapers, transforms it (e.g., GeoIP lookups, timestamp normalization), and ships it to Elasticsearch.
- **Kibana / Grafana:** The front-end visualization layer where dashboards, charts, and alerts are configured.

## 3. Architecture Diagram

```ascii
+-----------------------+      +-----------------------+      +-----------------------+
|                       |      |                       |      |                       |
|   Dark Web Scrapers   | ---> |      Message Bus      | ---> |       Logstash        |
|  (Python, Scrapy)     |      |   (Kafka / Redis)     |      |  (Data Normalization) |
|                       |      |                       |      |                       |
+-----------------------+      +-----------------------+      +-----------+-----------+
                                                                          |
                                                                          v
+-----------------------+      +-----------------------+      +-----------------------+
|                       |      |                       |      |                       |
|       Alerting        | <--- |        Kibana         | <--- |     Elasticsearch     |
| (Slack, PagerDuty,    |      | (Dashboard & Web UI)  |      |   (Search & Storage)  |
|  Email, Webhooks)     |      |                       |      |                       |
+-----------------------+      +-----------------------+      +-----------------------+
```

## 4. Designing the Dashboard Widgets

A CTI dashboard should be tailored to the organization's intelligence requirements. Key widgets typically include:

### 4.1 Brand & Executive Mentions (Keyword Tracking)
A simple but critical metric. A time-series bar chart tracking the frequency of specific keywords (Company Name, CEO Name, internal project codenames) across all scraped dark web forums. A sudden spike indicates a potential breach or targeted campaign.

### 4.2 Top Threat Actors by Activity
A data table aggregating the number of posts or listings by specific user aliases. Tracking the most active vendors helps prioritize investigations.

### 4.3 Extracted IOCs Geo-Map
If scrapers extract IP addresses from paste sites or forum dumps, running them through a GeoIP database and plotting them on a heat map can reveal the physical infrastructure distribution of threat actors or botnets.

### 4.4 Exploit & CVE Trend Analysis
A tag cloud or pie chart showing the most frequently mentioned CVEs in underground markets over the last 7 days. If a CVE relevant to your infrastructure starts trending heavily, patching priority must be elevated instantly.

## 5. Step-by-Step Implementation Guide

### Step 1: Logstash Pipeline Configuration
Logstash acts as the ETL (Extract, Transform, Load) tool. Here is a sample `logstash.conf` designed to ingest JSON data from a dark web scraper via a file or Kafka, parse it, and send it to Elasticsearch.

```ruby
input {
  # Assuming scrapers dump structured JSON to a log file
  file {
    path => "/var/log/darkweb_scrapes/*.json"
    start_position => "beginning"
    codec => json
  }
}

filter {
  # Ensure timestamps are based on the forum post time, not ingestion time
  date {
    match => [ "post_timestamp", "ISO8601" ]
    target => "@timestamp"
  }
  
  # Add a tag if the company name is mentioned in the content
  if [content] =~ /(?i)AcmeCorp/ {
    mutate {
      add_tag => [ "Brand_Mention", "CRITICAL_ALERT" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "cti-darkweb-%{+YYYY.MM.dd}"
    # Optional authentication
    # user => "elastic"
    # password => "changeme"
  }
  
  # Trigger an alert if the tag was added
  if "CRITICAL_ALERT" in [tags] {
    http {
      url => "https://hooks.slack.com/services/T0000/B000/XXXX"
      http_method => "post"
      format => "json"
      mapping => {
        "text" => "🚨 DARK WEB ALERT: Brand mention found in post by %{author}. URL: %{onion_url}"
      }
    }
  }
}
```

### Step 2: Creating Kibana Visualizations
Once data is in Elasticsearch, open Kibana:
1. Create an Index Pattern (`cti-darkweb-*`).
2. Navigate to **Visualize Library** -> Create new visualization.
3. Choose **Line Chart**. Set the Y-axis to `Count` and the X-axis to `Date Histogram` (using `@timestamp`). 
4. Add a split series filter for specific `keywords` to track brand mentions over time.
5. Combine visualizations into a unified **Dashboard**.

## 6. Real-World Attack Scenario

### Scenario: Spotting a Zero-Day Exploitation Campaign
An organization utilizes a specific proprietary CRM software.
The CTI team has configured their Kibana dashboard to track the name of this CRM alongside terms like "exploit", "0day", and "RCE".

On a Tuesday at 3:00 AM, the alerting pipeline triggers a Slack notification. The dashboard shows a 500% spike in mentions of the CRM software on the Exploit[.]in forum. An analyst clicks the spike on the Kibana graph, filtering down to the exact posts. They discover a Russian-speaking threat actor selling a weaponized, unpatched Remote Code Execution (RCE) exploit for their CRM.

Because of the real-time visual alerting provided by the dashboard, the security team implements emergency WAF rules and isolates the CRM servers hours before the exploit is widely distributed or utilized against their network.

## 7. Operational Challenges

- **Data Retention & Storage Costs:** Storing full text of millions of forum posts requires massive Elasticsearch clusters. Implement aggressive Index Lifecycle Management (ILM) policies to delete or archive indices older than 90 days.
- **False Positives:** Keyword alerting is prone to false positives (e.g., searching for "Apple" will trigger on the fruit, not just the company). Regular tuning and complex boolean queries in Elasticsearch are required.

## 8. Chaining Opportunities
- **[[11 - Network Graphing of Criminal Relationships]]:** Kibana can embed visualizations from Neo4j, allowing analysts to view statistical trends and relationship graphs side-by-side.
- **[[13 - Dark Web Data Enrichment using MISP]]:** Instead of feeding raw scrapes directly to Elastic, route them through MISP first, and have MISP forward the enriched JSON to Logstash.
- **[[15 - Legal and Storage Considerations for Malicious Data]]:** Ensure the Elasticsearch cluster is highly secured, as it will inevitably house stolen PII, credentials, and potentially illegal data scraped from the dark web.

## 9. Related Notes
- [[SIEM Architecture and Deployment]]
- [[Log Aggregation and Parsing Techniques]]
- [[Developing Actionable Intelligence]]
- [[Threat Hunting with Elastic Security]]
