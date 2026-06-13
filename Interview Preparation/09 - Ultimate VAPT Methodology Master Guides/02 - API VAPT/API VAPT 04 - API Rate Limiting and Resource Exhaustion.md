---
tags: [vapt, methodology, api-security, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - API"
topic: "Master Guide - API VAPT 04"
---

# Ultimate VAPT Methodology: API Rate Limiting and Resource Exhaustion

## 1. Introduction to Resource Exhaustion in APIs

APIs are processing engines. Because they handle machine-to-machine traffic and parse complex data structures (JSON, XML, GraphQL), they are highly susceptible to resource exhaustion. OWASP API4:2019 (Lack of Resources & Rate Limiting) and API4:2023 (Unrestricted Resource Consumption) highlight this danger.

In a VAPT interview, simply saying "I use Burp Intruder to check for rate limits" is insufficient. An expert candidate demonstrates how to *bypass* WAFs, how to exhaust memory vs. CPU, and how modern APIs (like GraphQL) introduce entirely new DoS paradigms.

## 2. Bypassing Rate Limits and WAFs

When testing brute-force (OTP, passwords) or enumeration, rate limits will block you. You must know how to circumvent them.

### 2.1 Header Spoofing (IP Rotation)
Many rate limiters track attempts based on the IP address. If the API sits behind a reverse proxy or load balancer, you can spoof the source IP using HTTP headers.
*   **Target Headers:**
    *   `X-Forwarded-For: 127.0.0.1` (Rotate this value per request)
    *   `X-Real-IP: 192.168.1.5`
    *   `Client-IP: 10.0.0.1`
    *   `True-Client-IP: 172.16.0.1`
*   **Automation:** Use Burp Suite Intruder with the "Pitchfork" attack type to rotate passwords and IPs simultaneously, or use the `IP Rotate` Burp Extension.

### 2.2 Path Variations
WAFs often apply rate limits based on strictly defined URL paths. Modifying the path slightly can bypass the regex while the backend still resolves it.
*   **Original:** `/api/v1/login` (Rate limited)
*   **Bypasses:**
    *   `/api/v1//login`
    *   `/api/v1/login/`
    *   `/api/v1/./login`
    *   `/api/v1/users/../login`
    *   `/api/v1/login%00` (Null byte injection)

### 2.3 Parameter/Payload Variation
If the rate limit is tied to the username/email being attacked:
*   Add spaces: `"email": " admin@test.com"`
*   Change casing: `"email": "AdMiN@test.com"`
*   Append dummy parameters: `&nonce=1`, `&nonce=2`

## 3. Advanced Resource Exhaustion Attacks

Resource exhaustion is not just sending 10,000 requests per second (Volumetric DoS). It is sending one carefully crafted request that consumes 100% of the server's CPU or RAM (Application DoS).

### 3.1 Pagination Anomalies
APIs often use pagination (`limit`, `offset`, `page`, `per_page`).
*   **Exploitation:** Change `limit=50` to `limit=99999999`. If the backend database attempts to query and allocate memory for a million records in a single request, the API will crash (Out of Memory - OOM).

### 3.2 GraphQL Batching Attacks
GraphQL allows multiple queries to be sent in a single HTTP request (Query Batching).
*   **Vulnerability:** A rate limiter might see exactly 1 HTTP request per second, but that single request contains 10,000 password guesses.
*   **Exploitation Payload:**
    ```json
    [
      {"query": "mutation { login(username:\"admin\", password:\"pass1\") { token } }"},
      {"query": "mutation { login(username:\"admin\", password:\"pass2\") { token } }"},
      {"query": "mutation { login(username:\"admin\", password:\"pass3\") { token } }"}
    ]
    ```

### 3.3 Regular Expression Denial of Service (ReDoS)
If the API uses poorly constructed regular expressions to validate input (e.g., email format, passwords), an attacker can send a string that causes catastrophic backtracking.
*   **Example Regex:** `^(([a-z])+.)+[A-Z]([a-z])+$`
*   **Payload:** `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!`
*   **Result:** The CPU spikes to 100% trying to evaluate the string. 10 concurrent requests can take down the entire server cluster.

### 3.4 Deep Object Nesting (JSON / XML)
Parsing deeply nested JSON structures consumes significant memory.
*   **Payload:** `{"a":{"a":{"a":{"a":{"a": ... }}}}}` (Nest 10,000 times).

## 4. Interview Preparation: How to Explain

### 4.1 Question: "How would you bypass a rate limiter when testing an OTP endpoint?"
**Expert Answer Script:**
> "First, I analyze how the rate limiter identifies me. If it's IP-based, I will use header spoofing techniques by injecting dynamically changing `X-Forwarded-For`, `X-Real-IP`, or `True-Client-IP` headers to simulate a distributed attack. If that fails, I use AWS API Gateway to rotate my actual source IP dynamically.
>
> If the limit is path-based, I apply path normalizations like adding trailing slashes, double slashes, or path traversal sequences (`/./`) to bypass WAF regex rules. Furthermore, if the application supports JSON parsing, I will try array-based parameter injection, sending an array of 100 OTPs in a single request to see if the backend iterates through them, bypassing the HTTP request rate limit entirely."

### 4.2 Question: "Explain how GraphQL introduces new challenges for Rate Limiting."
**Expert Answer Script:**
> "Traditional rate limiting operates at the HTTP layer, counting the number of URI requests per second. GraphQL breaks this paradigm because it operates on a single endpoint (usually `/graphql`). An attacker can utilize GraphQL Query Batching or construct a massive, deeply nested query (Alias overloading) within a *single* HTTP request. The WAF sees one request and allows it, but the backend server must resolve thousands of nested resolvers or authentication attempts, leading to CPU exhaustion or brute-force success. Securing GraphQL requires query cost analysis and depth limiting, not just HTTP rate limiting."

## 5. Real-World Attack Scenario

### Scenario: Bypassing 2FA via GraphQL Batching

```ascii
+-------------------+       1. Attacker notices GraphQL     +-------------------+
|                   | ------------------------------------> |   WAF / Gateway   |
|   Attacker        |       POST /graphql                   | (Limit: 5 req/sec)|
|                   |                                       +-------------------+
+-------------------+                                                 |
          |                                                           |
          | 2. Craft Array of 10,000 Mutations                        |
          v                                                           |
+---------------------------------------------------+                 |
| [                                                 |                 |
|   { "query": "mutation { verifyOTP(code:0000) }" },                 |
|   { "query": "mutation { verifyOTP(code:0001) }" },                 |
|   ... 9,998 more ...                              |                 |
|   { "query": "mutation { verifyOTP(code:9999) }" }                  |
| ]                                                 |                 |
+---------------------------------------------------+                 |
          |                                                           |
          | 3. Send Single HTTP Request                               |
          v                                                           v
+-------------------+                                       +-------------------+
|   Attacker        | ---- 1 HTTP Req (10k payload) ------> |   WAF (ALLOWS)    |
|                   | <--- Returns {"data": {"token":X}}--- |   GraphQL Server  |
+-------------------+                                       +-------------------+
```
**Breakdown:**
The application has a strict WAF rate limit of 5 requests per second to prevent OTP brute-forcing. The attacker discovers the API is GraphQL. Instead of sending 10,000 individual HTTP requests, the attacker creates a JSON array containing 10,000 GraphQL mutations, covering every possible 4-digit OTP. The WAF inspects the traffic, sees exactly 1 HTTP POST request, and permits it. The GraphQL engine processes the array sequentially, hits the correct OTP, and returns the authentication token.

## 6. Tools & Command Cheat Sheet

### Turbo Intruder (Burp Suite Extension)
Turbo Intruder is vastly superior to Burp Intruder for rate limit testing because it utilizes a custom HTTP stack, capable of sending thousands of requests per second.
*   **Python Script for Header Spoofing:**
    ```python
    def queueRequests(target, wordlists):
        engine = RequestEngine(endpoint=target.endpoint, concurrentConnections=50)
        for i in range(1000, 9999):
            # Rotate IP
            ip = "10.0.0.%d" % (i % 255)
            engine.queue(target.req, [str(i), ip])

    def handleResponse(req, interesting):
        if req.status != 429: # Ignore Rate Limit responses
            table.add(req)
    ```

### ffuf - Rate Limit Bypass Fuzzing
```bash
ffuf -w otps.txt -u https://api.target.com/v1/verify -X POST -d '{"otp":"FUZZ"}' -H "X-Forwarded-For: 127.0.0.1" -H "Content-Type: application/json" -p 0.1
```
*(Note: `-p 0.1` adds a delay if you need to stay strictly under a specific threshold).*

## 7. Chaining Opportunities

*   **Rate Limit Bypass -> Account Takeover:** Bypassing rate limits on the `/forgot_password` or `/verify_otp` endpoint directly leads to complete account compromise.
*   **Resource Exhaustion -> Security Control Bypass:** Crashing a specific security microservice (e.g., an audit logging or WAF analysis engine) via resource exhaustion may allow subsequent malicious requests to pass undetected (Fail-Open vulnerability).

## 8. Related Notes
*   [[Master Guide - API VAPT 03]] - Bypassing auth is often the precursor to brute-force attacks.
*   [[GraphQL Security Testing]] - Deep dive into query depth analysis.
*   [[Web Application Firewall Evasion]] - Further WAF bypass methodologies.

---
**End of Master Guide 04**
