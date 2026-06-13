---
tags: [API_Security, Information_Disclosure, Logging, Tokens, OWASP_API8]
difficulty: beginner
module: "31 - API Security"
topic: "31.20 API Token Leakage in Logs"
---

# 20 - API Token Leakage in Logs

## Introduction

In the complex architecture of modern APIs, observability is critical. To maintain uptime, debug errors, and monitor performance, development and DevOps teams deploy extensive logging mechanisms. These include Web Server logs (Nginx/Apache), API Gateway logs, Application Performance Monitoring (APM) tools (Datadog, New Relic), and centralized SIEM/Log Management stacks (ELK - Elasticsearch, Logstash, Kibana, Splunk).

However, excessive or misconfigured logging frequently leads to **Sensitive Data Exposure**, specifically the leakage of API Tokens, JWTs (JSON Web Tokens), OAuth access tokens, API keys, and user credentials. 

In the OWASP API Security Top 10, this falls under **API8:2023 - Security Misconfiguration** (improperly configured logging) and relates heavily to **Broken Authentication** when these tokens are weaponized. Once an attacker gains access to these logs, they can extract active, long-lived tokens to bypass authentication entirely, impersonate high-privilege users, or pivot deep into the internal network.

---

## ASCII Diagram: API Token Lifecycle and Log Leakage Points

```text
  [Client] Sends Request with Token (Bearer: eyJhbG...)
      |
      |  (1) URL Params Leakage (?token=123)
      v
  +-------------------+      (2) Writes to access.log
  |  Reverse Proxy /  | ================> [ Nginx / Apache Logs ]
  |   API Gateway     |                   (Often written to disk unencrypted)
  +-------------------+
      |
      |  (3) WAF / Request Body Logging
      v
  +-------------------+      (4) Forwards HTTP Headers
  |  Web Application  | ================> [ APM / Datadog / Splunk ]
  |  Firewall (WAF)   |                   (Logs Authorization Headers)
  +-------------------+
      |
      |  (5) Application Crash / Unhandled Exception
      v
  +-------------------+      (6) Dumps Stack Trace & Env Vars
  |  Backend API App  | ================> [ Sentry / Error Logs / Kibana ]
  | (Node, Spring, Go)|                   (Leaks DB Credentials & API Keys)
  +-------------------+
      |
      v
  [Database]
```

---

## How API Tokens Leak

Token leakage is rarely intentional; it is the byproduct of developers favoring debugging visibility over security constraints.

### 1. Tokens in URLs (GET Parameters)
Passing API tokens or session IDs in the URL query string is one of the most critical design flaws in API development.
```http
GET /api/v1/user/profile?access_token=abcdef123456 HTTP/1.1
Host: api.target.com
```
**Why it's disastrous:**
- **Web Server Logs**: Nginx, Apache, and IIS log the full Request URI by default. The token is written in plaintext to `access.log` for every request.
- **Referer Headers**: If the API response contains links to third-party sites, the browser will send the full URL (including the token) in the `Referer` header to the third party.
- **Browser History**: The token is saved in the user's browser history and local proxy logs.

### 2. Verbose Debug Logging and APM Tools
During development, engineers often turn the logging level to `DEBUG` or `TRACE` to see incoming requests and responses. This setting is sometimes accidentally pushed to production.
In this state, the application might log the entirety of the HTTP request, including all headers.
```json
{
  "timestamp": "2026-06-09T08:00:00Z",
  "level": "DEBUG",
  "message": "Incoming Request Received",
  "headers": {
    "Host": "api.target.com",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```
These logs are ingested into centralized systems like Kibana or Splunk, exposing active session tokens to anyone within the organization who has dashboard access.

### 3. Crash Reports and Stack Traces
When an API encounters an unhandled exception, it often generates a stack trace. Modern error tracking tools (like Sentry or Rollbar) capture this trace along with the *environment context*—which includes local variables, HTTP request data, and server environment variables (`.env`).
If an API key is stored in memory or passed as a variable when the crash occurs, it is shipped off to the error-tracking platform.
Furthermore, if error messages are returned in the HTTP response to the client (`500 Internal Server Error`), the stack trace might leak the API tokens directly to the attacker.

### 4. Client-Side Logging (`console.log`)
Frontend applications (React, Angular) interacting with APIs might leave `console.log(response)` statements in the production build. While this technically leaks the token to the user's own browser, it increases the risk of exfiltration via XSS (Cross-Site Scripting) or malicious browser extensions.

### 5. Unsanitized Request/Response Bodies
If authentication endpoints (`/api/login`) require credentials in the JSON body, and the API Gateway or WAF is configured to log full request payloads to analyze malicious traffic, plaintext passwords and resulting JWTs will be stored permanently in the security logs.

---

## Exploitation and Reconnaissance

How do attackers find and exploit these leaked logs?

### A. Accessing Publicly Exposed Logs
The most direct route is finding log interfaces that have been left exposed to the internet without authentication.
- **Exposed ELK Stacks**: Using Shodan or Google Dorks, attackers look for exposed Kibana dashboards (`port:5601`). If unauthenticated, they simply query the index for `"Authorization: Bearer"` to extract thousands of active JWTs.
- **Open S3 Buckets**: Organizations often backup their access logs to AWS S3. Misconfigured buckets allow attackers to download gigabytes of historical HTTP logs containing tokens in URLs.
- **Exposed `/logs` Directories**: Directory brute-forcing (`ffuf`) might reveal endpoints like `/api/logs`, `/debug/vars`, or standard web directories containing `error.log`.

### B. Exploiting Local File Inclusion (LFI)
If the API has an LFI vulnerability, the attacker can use it to read the server's local log files directly.
Payload example: `GET /api/v1/download?file=../../../../var/log/nginx/access.log`
Once the log is downloaded, the attacker parses it for leaked tokens.

### C. Server-Side Request Forgery (SSRF)
If the API suffers from SSRF, the attacker can force the server to query its internal observability tools. They might send a request to the internal Datadog agent or Prometheus endpoint (`http://localhost:9090/metrics`) to scrape memory dumps or log streams containing sensitive tokens.

---

## Defensive Strategies and Mitigation

Preventing log leakage requires strict engineering discipline and proactive data masking.

### 1. Never Pass Tokens in URLs
API tokens, Session IDs, and API Keys must **never** be transmitted via the query string or URL path. They must exclusively be sent in HTTP Headers (e.g., `Authorization: Bearer <token>`) or secure, HTTPOnly cookies. This completely eliminates leakage in standard web server `access.log` files.

### 2. Implement Log Scrubbing and Data Masking
Before logs are written to disk or shipped to an APM/SIEM, they must pass through a filtering layer.
- Configure loggers to automatically redact, mask, or drop sensitive headers (`Authorization`, `Cookie`) and sensitive JSON keys (`password`, `credit_card`, `ssn`).
- Example output: `"Authorization": "Bearer [REDACTED]"`

### 3. Restrict Log Access (Principle of Least Privilege)
Logs should be treated with the same security classification as the data they process. Access to Splunk, Datadog, or Kibana must be restricted using RBAC (Role-Based Access Control) and require Multi-Factor Authentication (MFA).

### 4. Suppress Stack Traces in Production
Ensure that the API framework is configured to return generic error messages (e.g., `{"error": "An internal server error occurred"}`) to the client. Stack traces must only be logged internally, and even then, they must be scrubbed of local variable values.

### 5. Short-Lived Tokens
If a token *is* leaked in a log, its window of utility should be minimal. Implement short-lived access tokens (e.g., 15 minutes) combined with strictly controlled refresh tokens. By the time an attacker finds the token in a log and attempts to use it, it should have already expired.

---

## Chaining Opportunities

- **[[02 - JWT Security and Vulnerabilities]]**: Leaked JWTs from logs can be analyzed offline for weak signing keys or manipulated if signature verification is flawed.
- **[[22 - Server-Side Request Forgery (SSRF) in APIs]]**: SSRF is heavily utilized to access internal logging dashboards (like Kibana or Prometheus) that contain leaked tokens.
- **[[08 - Broken Authentication]]**: Token leakage provides the credentials necessary to bypass all authentication mechanisms and execute account takeover.

## Related Notes

- [[16 - Lack of Resource Rate Limiting]]
- [[17 - API Fuzzing with ffuf and Burp]]
- [[18 - API Documentation Discovery]]

---
