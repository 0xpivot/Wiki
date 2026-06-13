---
tags: [prometheus, grafana, metrics, credential-disclosure, lfi, monitoring]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.28 Prometheus / Grafana"
---

# Prometheus Grafana — Metrics Exposure, Credential Disclosure

## 1. Introduction

Prometheus and Grafana are the de-facto standard stack for monitoring and observability in modern cloud-native and Kubernetes environments.
- **Prometheus** is a time-series database that pulls (scrapes) metrics from configured endpoints across the network.
- **Grafana** is a highly customizable visualization platform that queries data sources like Prometheus (and many others, such as Elasticsearch or SQL databases) to display dashboards.

Because these tools are designed to have deep visibility into every application and server in the infrastructure, securing them is paramount. Misconfigurations or vulnerabilities in this stack can lead to massive information disclosure, leakage of sensitive credentials, and occasionally Remote Code Execution.

## 2. Architecture & Vulnerability Context

- **Targets (Exporters):** Applications expose a `/metrics` HTTP endpoint. Prometheus regularly connects to these endpoints to scrape plaintext metrics.
- **Prometheus Server:** Stores the scraped data. It exposes an API and a basic web UI, typically on port `9090`.
- **Grafana Server:** Connects to Prometheus (and other databases) using configured credentials. It serves the primary visualization UI, typically on port `3000`.

**The Security Challenge:** Monitoring data is often incorrectly assumed to be "non-sensitive." Consequently, `/metrics` endpoints and the Prometheus server itself are frequently deployed without authentication. Furthermore, Grafana must store the credentials needed to access various backend databases, making it a lucrative target for attackers seeking lateral movement.

## 3. ASCII Diagram: Grafana LFI to Credential Theft (CVE-2021-43798)

```text
      [ Attacker ]
           |
           | (1) Crafts malformed URL requesting plugin assets
           |     with directory traversal characters
           v
  +---------------------------------------+
  |    Target Grafana Server              |
  |    Port: 3000                         |
  |                                       |
  |  GET /public/plugins/alertlist/       |
  |  ../../../../../../../../etc/grafana/ |
  |  grafana.ini HTTP/1.1                 |
  +---------------------------------------+
           |
           | (2) Path traversal bypasses plugin sandboxing
           v
  +---------------------------------------+
  |    Local File System                  |
  |                                       |
  |  Reads /etc/grafana/grafana.ini       | <-- (3) Extracts Database Passwords
  |  Reads /var/lib/grafana/grafana.db    | <--     and Secret Keys
  +---------------------------------------+
           |
           | (4) Sensitive files returned in HTTP response
           v
      [ Attacker ] --> Pivots to backend databases
```

## 4. Prometheus Metrics Exposure

By default, Prometheus does not enable authentication or TLS on its web UI and API (port 9090).

### Scraping the Scraper
If you can reach a Prometheus server, you can query all the time-series data it has collected using PromQL (Prometheus Query Language) via its HTTP API.

```bash
# Get all targets Prometheus is monitoring (Great for internal network mapping!)
curl -s http://<prometheus-ip>:9090/api/v1/targets | jq

# Query a specific metric (e.g., finding the version of a specific service)
curl -g 'http://<prometheus-ip>:9090/api/v1/query?query=up' | jq
```

### Direct `/metrics` Endpoint Exposure
Applications expose metrics on paths like `/metrics` or `/actuator/prometheus`. Developers sometimes mistakenly include sensitive data in these labels.

```bash
curl http://<app-ip>:8080/metrics
```
**What to look for in `/metrics` output:**
While metrics are meant to be numerical, they include key-value labels. Attackers search these endpoints for accidental disclosures:
- Usernames or IDs in URL paths.
- Database connection strings or tokens erroneously logged as metric labels.
- Extensive internal IP addressing and port maps.

## 5. Grafana Credential Disclosure & CVEs

Grafana is a far more complex application than Prometheus and has suffered from several severe vulnerabilities.

### CVE-2021-43798 (Grafana Unauthenticated LFI)
A critical, mass-exploited vulnerability in Grafana 8.x. Grafana allows plugins to serve static assets. A flaw in how the path to these assets was constructed allowed an unauthenticated attacker to perform directory traversal.

**Exploitation:**
```http
GET /public/plugins/alertlist/../../../../../../../../etc/passwd HTTP/1.1
Host: grafana.example.com
```
*Note: `alertlist` is a default plugin, guaranteeing the path exists.*

**Post-Exploitation (What to steal):**
1. `/etc/grafana/grafana.ini`: Contains configuration, sometimes including admin passwords, LDAP bind credentials, or SMTP passwords.
2. `/var/lib/grafana/grafana.db`: The SQLite database Grafana uses to store its state.

**Extracting Data Source Credentials:**
Grafana connects to backend databases (MySQL, Postgres, AWS CloudWatch). The credentials for these databases are stored in `grafana.db`. They are encrypted using the `secret_key` located in `grafana.ini`.
By exploiting the LFI to download both the `.ini` file and the `.db` file, an attacker can locally decrypt all the database credentials Grafana uses, leading to massive internal compromise.

### Default Credentials
Grafana installs with default credentials `admin / admin`. While it prompts to change this on first login, many automated deployments (e.g., via Helm charts) bypass this prompt or leave the default intact if unconfigured.

## 6. Manipulating Dashboards & SSRF

If an attacker gains authenticated access to Grafana (e.g., via weak credentials or an exploit), they can leverage Grafana's features for further attacks.

### Server-Side Request Forgery (SSRF)
Grafana allows users to add new "Data Sources". To support various backends, Grafana acts as a proxy. If a user can configure a new data source, they can point the URL to an internal network address (e.g., `http://169.254.169.254/latest/meta-data/` in AWS).
When Grafana tests the data source connection, it fetches the URL, returning the response (or a partial response/error) to the user, effectively turning Grafana into an SSRF proxy.

## 7. Defense & Hardening

1. **Require Authentication:** Ensure Prometheus is deployed behind a reverse proxy (like Nginx) that enforces Basic Auth or OIDC. Do not expose port 9090 directly.
2. **Network Segmentation:** `/metrics` endpoints on applications should only be accessible by the IP address of the Prometheus server. Use firewall rules or Kubernetes Network Policies to block direct access from user subnets.
3. **Patch Grafana:** Keep Grafana up to date to protect against LFI and auth bypass CVEs.
4. **Use Strong Data Source Permissions:** When providing Grafana with database credentials, use the Principle of Least Privilege. Grafana only needs `SELECT` (read-only) permissions. Never provide Grafana with a database `admin` or `root` account.
5. **Rotate Keys:** If Grafana is compromised, you must rotate the credentials for *every single data source* configured in Grafana, as well as the LDAP/SMTP credentials in the configuration file.

## 8. Chaining Opportunities

- **Grafana LFI to Database Compromise:** Exploit CVE-2021-43798 to download `grafana.db` and `grafana.ini`, decrypt the MySQL data source credentials, and connect directly to the internal customer database to exfiltrate data. Link to `[[03 - Local File Inclusion (LFI)]]`.
- **Prometheus Mapping to Lateral Movement:** Use exposed Prometheus targets to map the exact IPs, ports, and versions of internal microservices, prioritizing vulnerable services for exploitation. Link to `[[01 - Network Reconnaissance & Port Scanning]]` (hypothetical).

## 9. Related Notes

- `[[03 - Local File Inclusion (LFI)]]`
- `[[05 - Server-Side Request Forgery (SSRF)]]`
- `[[22 - etcd — Exposed Key-Value Store]]` (Often monitored by Prometheus)
