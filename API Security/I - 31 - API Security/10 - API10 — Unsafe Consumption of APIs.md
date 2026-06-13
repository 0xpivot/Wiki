---
tags: [API, VAPT, API10, Supply-Chain, Third-Party, Injection]
difficulty: intermediate
module: "31 - API Security"
topic: "31.10 API10 - Unsafe Consumption of APIs"
---

# API10:2023 — Unsafe Consumption of APIs

## 1. Executive Summary

Unsafe Consumption of APIs (API10:2023) is a new addition to the OWASP API Top 10, reflecting the reality that modern applications are highly distributed mosaics of third-party services. APIs do not just serve data to end-users; they continuously consume data from other APIs (e.g., payment gateways, weather APIs, social media integrations, CRM webhooks, mapping services). 

This vulnerability occurs when a developer intrinsically trusts the data returned by a third-party API and processes it without adequate validation, sanitization, or safety controls. If the third-party API is compromised, misconfigured, or maliciously manipulated, the consuming API becomes vulnerable to downstream attacks such as Server-Side Request Forgery (SSRF), SQL Injection (SQLi), Cross-Site Scripting (XSS), or Denial of Service (DoS). It is effectively an API-level supply chain attack.

## 2. Deep Dive: Implicit Trust and The API Supply Chain

The core fallacy driving API10 is the assumption: *"Because I am paying for this enterprise third-party API, or because they are a large reputable company, their data is safe."*

APIs consume external data via two primary methods:
1.  **Pull (Client Mode):** The backend server makes a request to a third-party API and parses the JSON/XML response.
2.  **Push (Webhook/Callback Mode):** The third-party API sends a POST request back to your server's endpoint asynchronously (e.g., Stripe payment confirmation).

If the data received from either method is directly inserted into a database, reflected in a web page, or used to build a local system command, any malicious payload embedded within that data will execute on the consuming system.

### Visualizing Unsafe API Consumption

```ascii
                                [ Threat Actor ]
                                       |
                   (1) Injects payload into vulnerable 3rd-Party system
                   (e.g., puts an XSS/SQLi payload in their user profile)
                                       |
                                       v
                     +-----------------------------------+
                     |      Third-Party API Service      |
                     |  (e.g., CRM, Payment Provider)    |
                     +-----------------------------------+
                                       |
                    (2) Consuming API fetches data, assuming
                        it is clean and safe to use.
                                       v
    +-----------------------------------------------------------------------+
    |                         Your Backend API                              |
    |                                                                       |
    |  [ Data Parser ] -> blindly extracts payload                          |
    |                                                                       |
    |  (3) Blindly executes payload during processing:                      |
    |   |                                                                   |
    |   +-> Executes SQL Injection against internal DB                      |
    |   +-> Stores XSS payload to be served to local admins                 |
    |   +-> Follows malicious redirect causing SSRF                         |
    +-----------------------------------------------------------------------+
```

## 3. Real-World Exploitation Scenarios

### Scenario A: Second-Order SQL Injection via CRM API
An organization's marketing API automatically pulls new lead information from an external CRM provider (e.g., HubSpot or Salesforce) every hour.
**The Flaw:** The marketing API extracts the `company_name` field from the CRM JSON response and concatenates it directly into an internal MySQL insert statement without parameterization.
**The Exploit:** An attacker signs up for the external CRM via a public form and sets their company name to:
`Acme Corp', (SELECT user()), '1`
When the marketing API consumes the CRM data, the payload executes on the internal database, allowing the attacker to perform a second-order SQL injection attack without ever directly interacting with the marketing API.

### Scenario B: SSRF via Unsafe Redirect Handling
An application uses a third-party URL shortening API to expand links submitted by users before checking them against a malware database.
**The Flaw:** The HTTP client used by the backend API to communicate with the URL shortener is configured to automatically follow all HTTP redirects.
**The Exploit:** The attacker registers a shortened URL that redirects to `http://169.254.169.254/latest/meta-data/` (AWS Metadata). They submit the short URL to the application. The backend API queries the shortener, receives an HTTP 302 redirect to the local AWS IP, and blindly follows it, resulting in an SSRF that leaks cloud credentials.

### Scenario C: Denial of Service (Memory Exhaustion)
An application integrates with a weather API, expecting a small JSON payload containing the 5-day forecast.
**The Flaw:** The application allocates memory dynamically based on the size of the incoming response and does not enforce a maximum timeout for the connection.
**The Exploit:** The weather API is compromised or experiences a severe glitch. It begins streaming an infinitely large string of garbage data. The consuming API continues to buffer this response into memory until the server runs out of RAM and crashes, causing a system-wide Denial of Service.

## 4. Detection and Identification

Finding API10 vulnerabilities requires mapping out all external dependencies.
*   **Architecture Review:** Identify every external API, SDK, and webhook endpoint your application interacts with.
*   **Dependency Fuzzing:** If you control test accounts on the third-party platforms, insert standard attack payloads (SQLi, XSS, command injection) into the third-party system and observe how *your* application behaves when it ingests them.
*   **Log Review:** Analyze application logs for crashes, timeouts, or unexpected database errors occurring immediately after an external API sync job runs.
*   **Code Review (SAST):** Look for HTTP client configurations (like `allow_redirects=True`), lack of input validation on variables populated from external JSON schemas, and missing connection timeout parameters.

## 5. Defense in Depth and Mitigation

To defend against Unsafe Consumption of APIs, developers must adopt a **Zero Trust** mindset regarding external data.

### 1. Strict Input Validation (The "Trust Nothing" Approach)
Treat data received from third-party APIs exactly as you would treat data submitted by an anonymous user on the internet.
*   Validate the schema: Ensure the incoming JSON strictly matches the expected types (e.g., `age` must be an integer, not a string or array).
*   Sanitize inputs before storing them in a database or reflecting them in a browser. Use parameterized queries/ORMs universally.

### 2. Secure HTTP Client Configuration
When making requests to third-party APIs:
*   **Enforce Timeouts:** Never make an open-ended HTTP request. Always set strict connect and read timeouts (e.g., `timeout=5.0` seconds).
*   **Disable Automatic Redirects:** Handle HTTP 301/302 redirects manually, ensuring the new target URL is validated against a safe list and does not point to internal IP space (Preventing SSRF).
*   **Size Limits:** Restrict the maximum size of the response body you are willing to parse. If the payload exceeds 2MB (or whatever is reasonable), drop the connection.

### 3. Circuit Breakers and Fallbacks
Implement the "Circuit Breaker" design pattern. If the third-party API starts returning 500 errors, taking too long to respond, or sending malformed data, the circuit breaker should "trip," temporarily halting requests to the external service. Your API should then serve cached data or graceful degradation errors rather than allowing the third-party failure to cascade and crash your systems.

### 4. Transport Security
*   Verify the TLS certificate of the third-party API (prevent Man-in-the-Middle attacks where an attacker spoofs the API provider).
*   If using webhooks, validate the cryptographic signature provided by the sender (e.g., verifying a GitHub or Stripe webhook HMAC signature) to ensure the payload actually came from the trusted provider and not a forged request.

## 6. Chaining Opportunities

Unsafe consumption acts as a delivery mechanism for traditional web vulnerabilities into the internal network:
*   **[[07 - API7 — Server Side Request Forgery (SSRF)]]:** Often achieved when consuming an API that returns malicious redirects or URIs to fetch.
*   **[[Cross-Site Scripting (XSS)]]:** Stored XSS is frequently achieved by injecting payloads into third-party profiles that are later ingested and rendered by your API.
*   **[[Injection Vulnerabilities (SQLi, Command Injection)]]:** Passing unvalidated 3rd-party data into internal sinks.

## 7. Related Notes
- [[Zero Trust Architecture Principles]]
- [[Securing Webhook Integrations]]
- [[Implementing the Circuit Breaker Pattern]]
- [[Defense against Second-Order SQL Injection]]

---
*End of Note*
