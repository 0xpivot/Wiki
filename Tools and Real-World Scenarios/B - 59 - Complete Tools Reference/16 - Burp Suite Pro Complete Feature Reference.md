---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.16 Burp Suite Pro Complete Feature Reference"
---

# Burp Suite Pro Complete Feature Reference

## 1. Introduction and Architectural Overview
Burp Suite Professional, developed by PortSwigger, is the paramount toolkit for web application penetration testing. Functioning primarily as an interception proxy, it positions itself strategically between the client (typically a web browser or API client like Postman) and the target server. This man-in-the-middle (MitM) positioning allows security professionals to intercept, inspect, modify, and replay HTTP/HTTPS requests and responses in real-time.

Beyond simple proxying, Burp Suite Pro integrates a cohesive suite of tools designed to automate repetitive tasks, discover complex vulnerabilities, and facilitate deep manual exploitation. Its modular architecture ensures that data flows seamlessly between tools—for instance, a request intercepted in the Proxy can be sent to the Scanner for automated analysis, to the Intruder for fuzzing, and to the Repeater for manual tweaking, all with single clicks.

## 2. Core Proxy and Interception Mechanics
The Proxy is the foundational component of Burp Suite. All traffic routing through Burp is logged here, providing a historical record of the application's attack surface.

### 2.1 Proxy Listeners
By default, Burp listens on `127.0.0.1:8080`. However, listeners can be configured to bind to specific interfaces or all interfaces, which is crucial when proxying traffic from mobile devices (iOS/Android) or thick clients on the same network.
*   **Invisible Proxying:** Used for thick clients that do not support proxy configuration. Burp intercepts traffic destined for port 80/443 and seamlessly routes it to the target.
*   **Certificate Management:** To intercept HTTPS, Burp dynamically generates a per-host certificate signed by its own Certificate Authority (CA). The tester must install Burp's CA certificate in their browser's or device's trust store.

### 2.2 Intercept Rules and Scope
Interception can be noisy. Burp allows granular control:
*   **Scope Definition:** The Target Scope is arguably the most important configuration. It defines exactly what domains, subdomains, and directories are "in bounds."
*   **Interception Rules:** Rules can be configured to drop requests based on file extensions (e.g., `^.*\.js$`), HTTP methods, or specific headers, ensuring the tester only sees relevant traffic.

### 2.3 Match and Replace
A powerful feature that automatically alters requests or responses on the fly.
*   **Request Manipulation:** Automatically changing `User-Agent` headers, stripping `Authorization` headers to test for unauthenticated access, or forcing HTTP/1.1 downgrade.
*   **Response Manipulation:** Bypassing client-side controls by changing `disabled="true"` to `disabled="false"` in HTML, or modifying JavaScript validation logic before it reaches the browser.

## 3. Burp Scanner: Automated Vulnerability Auditing
Burp Scanner is an enterprise-grade automated security testing engine. It employs a two-phased approach: Crawling and Auditing.

### 3.1 Crawling (Spidering)
The crawler's goal is to map the application's attack surface, including discovering hidden endpoints, mapping API routes, and identifying state-changing actions.
*   **Navigation:** It parses HTML, JavaScript, and JSON to extract links.
*   **State Management:** Modern applications require state tracking. The crawler can handle logins, maintain session tokens, and understand when it has been logged out, attempting to re-authenticate if a macro is configured.

### 3.2 Auditing (Active & Passive Scanning)
*   **Passive Scanning:** Analyzes the traffic flowing through the proxy without sending any additional requests. It identifies missing security headers, cleartext transmission of sensitive data, insecure cookie flags (`HttpOnly`, `Secure`), and information disclosure (e.g., stack traces, internal IPs).
*   **Active Scanning:** Sends crafted, malicious payloads to the target. It analyzes the responses to identify vulnerabilities such as SQL Injection (SQLi), Cross-Site Scripting (XSS), Command Injection (CMDi), Path Traversal, and XML External Entity (XXE) injection.
*   **BChecks:** Custom, scriptable scan checks written in a domain-specific language. Testers can write BChecks to look for specific, bespoke vulnerabilities unique to their target organization.

## 4. Burp Intruder: Advanced Fuzzing and Brute-Forcing
Intruder is the engine for automated, customized attacks. It takes a base request, defines payload markers (`§`), and iterates through payload lists.

### 4.1 Attack Types
*   **Sniper:** Uses a single payload set. It places payloads sequentially into each defined position, one at a time. If there are two positions and 100 payloads, it makes 200 requests. Ideal for targeted fuzzing of individual parameters.
*   **Battering Ram:** Uses a single payload set. It places the *same* payload into *all* defined positions simultaneously. If there are two positions and 100 payloads, it makes 100 requests. Useful when the same input must be supplied in multiple places.
*   **Pitchfork:** Uses multiple payload sets (one for each position). It iterates through the lists simultaneously. Request 1 uses Payload 1 from Set A and Payload 1 from Set B. Request 2 uses Payload 2 from Set A and Payload 2 from Set B. Ideal for testing authorization matrices or credential stuffing with known username/password pairs.
*   **Cluster Bomb:** Uses multiple payload sets. It tries every possible permutation. If Set A has 10 payloads and Set B has 10 payloads, it makes 100 requests. Extremely powerful but computationally expensive; used for complex brute-forcing.

### 4.2 Payload Processing and Grep
Payloads can be processed before transmission (e.g., URL encoding, Base64 encoding, hashing). The `Grep - Match` and `Grep - Extract` features allow testers to flag responses containing specific strings or extract data (like CSRF tokens) from a response to use in the next request.

## 5. Burp Collaborator: Out-of-Band (OAST) Testing
Many vulnerabilities are "blind," meaning the application executes the payload but returns no direct output to the attacker. Collaborator detects these out-of-band interactions.

### 5.1 Architecture and Mechanics
Collaborator is a custom DNS, HTTP, and SMTP server.
1.  **Payload Generation:** Burp generates a unique payload (e.g., `http://xxyyzz.oastify.com`).
2.  **Injection:** The tester injects this payload into a target parameter (e.g., testing for SSRF).
3.  **Interaction:** If the target server is vulnerable, it will make a DNS lookup or an HTTP request to `xxyyzz.oastify.com`.
4.  **Detection:** The Collaborator server logs the interaction. Burp Suite polls the Collaborator server, retrieves the interaction details, and alerts the tester to the vulnerability.

### 5.2 Private Collaborator
For highly sensitive engagements or isolated networks, PortSwigger allows organizations to deploy their own Private Collaborator server, ensuring that no vulnerability metadata leaves the corporate network.

## 6. Architecture Diagram: Collaborator Flow

```ascii
+-------------------+       +-----------------------+       +-------------------+
|                   |       |      Burp Suite       |       |                   |
|   Attacker PC     +------>| +-------------------+ |<------+   Target Web      |
|   (Browser)       | HTTPS | |  Proxy / Intruder | | HTTPS |   Server          |
+-------------------+       | +---------+---------+ |       +---------+---------+
                            |           |           |                 |
                            | +---------v---------+ |                 |
                            | | Collaborator      | |                 |
                            | | Polling Engine    | |                 |
                            | +---------+---------+ |                 |
                            +-----------|-----------+                 |
                                        |                             |
                                        | (3) Polling for Hits        | (1) Payload Injection
                                        |                             | (Blind SSRF)
                            +-----------v-----------+                 |
                            |                       |<----------------+
                            |  Burp Collaborator    | (2) Out-of-Band Request
                            |  Server (DNS/HTTP)    |     (DNS lookup for payload)
                            |                       |
                            +-----------------------+
```

## 7. Auxiliary Tools: Repeater, Sequencer, Decoder, Comparer
*   **Repeater:** The essential tool for manual testing. It allows for the rapid modification and resubmission of individual HTTP requests. It supports HTTP/2 and WebSockets, and features a robust history log to track changes and responses over time.
*   **Sequencer:** Analyzes the entropy (randomness) of tokens (e.g., Session IDs, CSRF tokens, Password Reset links). It captures thousands of samples and applies statistical tests (like FIPS-140) to determine if the tokens can be predicted or forged.
*   **Decoder:** A utility for quickly encoding and decoding data across various formats (URL, HTML, Base64, Hex, Octal, Binary, GZIP). Its "Smart Decode" feature attempts to automatically identify the encoding scheme recursively.
*   **Comparer:** A visual diffing tool. Testers can send two requests or two responses to Comparer to identify subtle byte-level or word-level differences. This is vital when analyzing authorization bypasses or complex logic flaws where the response structural changes are minimal.

## 8. Macros and Session Handling Rules
Modern web applications utilize complex state mechanisms, anti-CSRF tokens, and short-lived JWTs. Burp handles this via Macros.

### 8.1 Configuring Macros
A macro is a recorded sequence of HTTP requests. For instance, a macro might execute:
1.  GET `/login` (to retrieve a new CSRF token).
2.  POST `/login` (to submit credentials and authenticate).

### 8.2 Session Handling Rules
These rules dictate when a macro should run. A rule can be configured to monitor the Scanner or Intruder. If a request returns a `401 Unauthorized` or a specific string like "Session Expired", the Session Handling Rule will pause the attack, execute the Login Macro, extract the new session cookie, update the original request with the new cookie, and resume the attack seamlessly.

## 9. Chaining Opportunities
*   **[[17 - Burp Extensions Active Scan Autorize JWT]]:** Burp's native capabilities are exponentially increased by utilizing the BApp store. Extensions like Autorize automate the detection of IDORs, which the native scanner struggles with.
*   **[[19 - ffuf Advanced Usage]]:** While Burp Intruder is powerful, `ffuf` is significantly faster for initial directory brute-forcing. A common chain is to use `ffuf` to discover hidden paths and then proxy only the successful requests into Burp for deep manual inspection using Repeater and Active Scanner.
*   **[[02 - API2 — Broken User Authentication]]:** Burp Intruder's Pitchfork attack type is specifically designed for complex credential stuffing and brute-forcing authentication endpoints, testing for rate limiting and account lockout mechanisms.

## 10. Related Notes
*   [[01 - API1 — Broken Object Level Authorization (BOLA)]] - Use Burp Repeater to manually swap object IDs (e.g., `user_id=1` to `user_id=2`) to test for authorization bypasses.
*   [[05 - API5 — Broken Function Level Authorization]] - Map the application surface using Burp's Target Site Map, identify administrative endpoints, and use Repeater to attempt access as a low-privileged user.
*   [[18 - OWASP ZAP Full Scan Modes and API]] - Compare Burp's manual testing focus with ZAP's heavy emphasis on CI/CD pipeline automation and open-source accessibility.
