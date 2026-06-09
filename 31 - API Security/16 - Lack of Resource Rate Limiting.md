---
tags: [API_Security, Rate_Limiting, DoS, Brute_Force, OWASP_API4]
difficulty: beginner
module: "31 - API Security"
topic: "31.16 Lack of Resource Rate Limiting"
---

# 16 - Lack of Resource Rate Limiting

## Introduction

In the modern API-driven ecosystem, APIs serve as the central nervous system connecting diverse clients, applications, and microservices. However, when an API lacks proper resource rate limiting, it becomes highly susceptible to an array of attacks ranging from credential stuffing and brute-forcing to application-layer Denial of Service (DoS) and costly resource exhaustion.

In the OWASP API Security Top 10 (2023), this vulnerability is formally categorized under **API4:2023 - Unrestricted Resource Consumption**. It encompasses not only the absence of rate limits (number of requests per time window) but also the lack of constraints on payload size, execution time, memory allocation, and database query complexity.

A lack of rate limiting allows an attacker to interact with the API at superhuman speeds, testing thousands of inputs per second, scraping proprietary data, or deliberately maxing out CPU and memory resources on the backend servers.

---

## Core Concepts of Rate Limiting and Resource Limiting

While often used interchangeably, rate limiting and resource limiting refer to slightly different protective mechanisms:

1. **Rate Limiting**: Restricts the *number* of API requests a client can make within a specified timeframe.
2. **Resource Limiting**: Restricts the *size* or *complexity* of the request itself (e.g., maximum payload size, maximum number of items returned in pagination, maximum depth of a GraphQL query).

### Common Rate Limiting Algorithms

Understanding how rate limiters work is crucial for identifying weaknesses and developing bypass strategies.

- **Token Bucket**: Tokens are added to a bucket at a fixed rate. Each API request consumes a token. If the bucket is empty, the request is dropped. This allows for brief bursts of traffic.
- **Leaky Bucket**: Requests enter a queue (bucket) and are processed at a constant rate (leaking out). If the queue is full, new requests are discarded. This smooths out traffic bursts.
- **Fixed Window**: The timeline is divided into fixed intervals (e.g., 00:00 to 00:01). A counter tracks requests in the current window. Once the limit is reached, all subsequent requests in that window are blocked. Susceptible to spikes at the edges of the window.
- **Sliding Window Log**: Logs the timestamp of each request. To check if a limit is exceeded, it counts timestamps within the previous $N$ seconds. Highly accurate but memory-intensive.
- **Sliding Window Counter**: A hybrid approach using fixed windows and a weighted count from the previous window to estimate the current rate smoothly.

---

## ASCII Architecture Diagram: Rate Limiting Flow and Bypass

```text
                                        Rate Limiting Evasion Vectors
                                        +---------------------------+
                                        | 1. IP Rotation (Proxies)  |
                                        | 2. Header Spoofing        |
                                        | 3. Unauthenticated Routes |
                                        | 4. Endpoint Variations    |
                                        +-------------+-------------+
                                                      |
                                                      v
  +-----------+     [Request] X-Forwarded-For: 1.2.3.4  +-------------+       +---------------+
  | Attacker  | --------------------------------------> | WAF / Proxy | ----> |  API Gateway  |
  +-----------+                                         +-------------+       +---------------+
        ^                                                     |                       |
        |                                                (Checks IP)             (Checks Token/
        |                                                     |                   User ID)
        |                                                     v                       |
        |                                              +---------------+              |
        +--------------------------------------------- | Block / Allow | <------------+
            429 Too Many Requests (If Blocked)         +---------------+              |
                                                                                      v
                                                                             +-----------------+
                                                                             | Backend Server  |
                                                                             | (Database/App)  |
                                                                             +-----------------+
                                                                             [Resource Exhaustion]
                                                                             - Heavy DB Queries
                                                                             - Memory Leaks
                                                                             - Pagination Abuse
```

---

## Exploitation Scenarios

When an API lacks resource and rate limiting, several critical attack vectors open up.

### 1. Brute-Force and Credential Stuffing

Without rate limits on authentication endpoints (`/api/v1/login`), attackers can perform rapid credential stuffing using lists of breached usernames and passwords. They can also brute-force OTPs (One-Time Passwords) sent to SMS or email if the verification endpoint (`/api/v1/verify-otp`) is not throttled.

### 2. Application-Layer DoS (Layer 7 DoS)

Attackers can exhaust server resources by sending requests that are computationally expensive for the backend but cheap for the attacker.

- **Pagination Abuse**: If an API endpoint like `/api/v1/users?limit=10&offset=0` allows the attacker to specify `limit=1000000`, the database may attempt to load millions of records into memory, causing an Out-Of-Memory (OOM) crash.
- **Large Payload Attacks**: Sending massive JSON arrays or deeply nested XML structures to endpoints that parse them entirely in memory before validation.
- **GraphQL Introspection and Nested Queries**: If complexity limits are absent, an attacker can craft a deeply nested GraphQL query that exponentially increases the database load:
  ```graphql
  query {
    author(id: 1) {
      posts {
        comments {
          author {
            posts {
              comments { ... }
            }
          }
        }
      }
    }
  }
  ```

### 3. Business Logic Abuse

APIs that trigger actions costing the company money can be abused.
- **SMS Bombing**: Continuously calling `/api/v1/send-sms?phone=+1234567890`. The company incurs charges from their SMS gateway provider (e.g., Twilio) for every message sent.
- **Email Flooding**: Continuously calling password reset endpoints to flood a victim's inbox, hiding actual critical alerts.
- **Inventory Depletion (Scalping)**: Bots rapidly adding high-value items to their carts and holding them, preventing legitimate users from purchasing.

---

## Advanced Rate Limit Bypass Techniques

When a basic rate limiter *is* present, it is often implemented improperly. Attackers can bypass these rudimentary protections using various techniques.

### A. IP Rotation and Proxies

If the rate limit is enforced strictly by IP address, an attacker can route their traffic through proxy networks, botnets, or Tor. By rotating the source IP on every few requests, the rate limit threshold per IP is never reached. Tools like Burp Suite's "IP Rotate" extension (which leverages AWS API Gateway) are heavily used for this.

### B. HTTP Header Manipulation

Many internal APIs or load balancers determine the client's IP address by reading specific HTTP headers. If the application blindly trusts these headers without validating that the request came from a trusted internal proxy, an attacker can spoof them.

Injecting random IPs or rotating IPs in these headers can reset the rate limit counter:
- `X-Forwarded-For: <random-ip>`
- `X-Real-IP: <random-ip>`
- `Client-IP: <random-ip>`
- `X-Originating-IP: <random-ip>`
- `X-Remote-IP: <random-ip>`
- `True-Client-IP: <random-ip>`

**Example:**
```http
POST /api/v1/login HTTP/1.1
Host: api.target.com
X-Forwarded-For: 192.168.1.55
Content-Type: application/json

{"username": "admin", "password": "password123"}
```
By incrementing the IP in `X-Forwarded-For` with each request, the attacker circumvents IP-based restrictions.

### C. Null Byte and Path Manipulation

Sometimes, rate limiting is tied to the exact string of the URI path. If the API framework normalizes paths differently than the rate-limiting proxy (like Nginx), bypasses are possible.

- Original: `/api/v1/login` (Rate limited)
- Bypass 1: `/api/v1/login%00`
- Bypass 2: `/api/v1/login/`
- Bypass 3: `/api/v1/./login`
- Bypass 4: `/api/v1//login`
- Bypass 5: `/api/V1/LOGIN` (If the API is case-insensitive but the WAF is case-sensitive).

### D. Parameter Pollution and JSON Arrays

If an API accepts an array of values instead of a single value, an attacker can submit multiple guesses in a single HTTP request, completely bypassing per-request rate limits.

**Example 1: Login Array**
```json
{
  "username": "admin",
  "password": ["pass1", "pass2", "pass3", ..., "pass1000"]
}
```

**Example 2: GraphQL Batching**
Sending an array of GraphQL queries in a single POST request to execute them simultaneously, circumventing request-per-second limits.

---

## Defensive Strategies and Remediation

Securing an API against resource exhaustion requires a multi-layered defense-in-depth approach.

### 1. Robust Rate Limiting Implementation

- **Identify the Client Accurately**: Do not rely solely on the IP address. Use a combination of IP, API Key, Session Token, and Device Fingerprint (e.g., JA3 TLS fingerprinting) to identify clients.
- **Implement Tiered Limits**:
  - Global limits (e.g., 1000 req/min per IP).
  - Endpoint-specific limits (e.g., 5 req/min on `/login`, 1 req/min on `/reset-password`).
  - User-specific limits (e.g., 100 req/min per authenticated User ID).
- **Return Meaningful Responses**: When limits are exceeded, return a `429 Too Many Requests` status code along with `Retry-After` and `X-RateLimit-Remaining` headers to allow legitimate clients to gracefully back off.

### 2. Resource Constraints

- **Strict Pagination Limits**: Enforce hard limits on `limit` or `per_page` parameters (e.g., maximum 100 items per request). Ignore or reject requests exceeding the limit.
- **Payload Size Limits**: Enforce maximum payload sizes at the API Gateway or WAF level (e.g., maximum 1MB per JSON payload).
- **Timeouts**: Enforce strict execution timeouts for API processing and database queries to prevent long-running requests from tying up server threads.

### 3. Mitigating Logic Abuse

- **CAPTCHA / Challenge-Response**: Require reCAPTCHA, hCaptcha, or Proof of Work (PoW) challenges on highly sensitive endpoints like login, registration, and password resets.
- **Lockouts and Delays**: Implement account lockouts or exponential backoff delays after multiple failed authentication attempts.

### 4. GraphQL Specific Defenses

- **Query Depth Limiting**: Reject queries that exceed a certain nesting depth.
- **Query Complexity Analysis**: Assign a "cost" to each field in the GraphQL schema. Calculate the total cost of a query before execution and reject it if it exceeds a predefined maximum cost.

---

## Chaining Opportunities

- **[[08 - Broken Authentication]]**: Lack of rate limiting on login endpoints directly facilitates broken authentication via credential stuffing.
- **[[15 - Insecure Direct Object References (IDOR)]]**: Without rate limiting, an attacker can rapidly iterate through object IDs (e.g., `/api/user/1`, `/api/user/2`) to scrape the entire database efficiently.
- **[[24 - API Injection Attacks]]**: Fuzzing for SQLi or Command Injection is much faster and stealthier when there is no rate limiting or WAF intervention.

## Related Notes

- [[02 - JWT Security and Vulnerabilities]]
- [[17 - API Fuzzing with ffuf and Burp]]
- [[22 - Server-Side Request Forgery (SSRF) in APIs]]

---
