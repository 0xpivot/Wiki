---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.05 HTTP Response Structure"
---

# 02.05 — HTTP Response Structure

## What is it?

An **HTTP response** is the server's answer to a client's request. Every response tells you the status (success/error), metadata about the content (headers), and the actual content (body). For pentesters, responses reveal server internals, vulnerabilities, and confirm successful exploits.

---

## Response Anatomy

```
┌─────────────────────────────────────────────────────────────────┐
│                       STATUS LINE                               │
│  HTTP/1.1   200   OK                                            │
│  │           │    │                                             │
│  version     │    └── status text (human readable)              │
│              └──────── status code (machine readable)           │
├─────────────────────────────────────────────────────────────────┤
│                     RESPONSE HEADERS                            │
│  Date: Mon, 01 Jan 2024 12:00:00 GMT                           │
│  Server: nginx/1.18.0 (Ubuntu)          ← reveals server!      │
│  Content-Type: text/html; charset=UTF-8                         │
│  Content-Length: 4523                                           │
│  Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax    │
│  X-Frame-Options: SAMEORIGIN                                    │
│  X-Content-Type-Options: nosniff                                │
│  Content-Security-Policy: default-src 'self'                    │
│  Strict-Transport-Security: max-age=31536000                    │
│  Cache-Control: no-store, private                               │
│  X-Request-ID: 7f4a9b12-abc3-def4                              │
│  X-Powered-By: PHP/7.4.3                ← reveals tech stack!  │
├─────────────────────────────────────────────────────────────────┤
│                     BLANK LINE                                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     RESPONSE BODY                               │
│  <!DOCTYPE html>                                                │
│  <html>                                                         │
│    <head><title>Dashboard</title></head>                        │
│    <body>Welcome admin!</body>                                   │
│  </html>                                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Context — Responses in VAPT

### 1. What Responses Leak (Recon Phase)

```
HEADERS THAT REVEAL TECHNOLOGY STACK:
──────────────────────────────────────────────────
Server: nginx/1.18.0 (Ubuntu)      → OS + web server version
Server: Apache/2.4.41 (Debian)     → Apache version + OS
X-Powered-By: PHP/7.4.3            → PHP version (find CVEs!)
X-Powered-By: ASP.NET              → .NET application
X-AspNet-Version: 4.0.30319        → exact .NET version
X-AspNetMvc-Version: 5.2           → MVC framework version

COMMANDS TO EXTRACT FINGERPRINTING INFO:
curl -sI https://target.com | grep -iE "server|x-powered|x-generator|x-framework"

whatweb target.com         ← fingerprint web tech
nikto -host target.com     ← finds misconfigs and version disclosure
```

### 2. Security Headers — What's Missing

```
GOOD RESPONSE HAS ALL THESE SECURITY HEADERS:
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY (or SAMEORIGIN)
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=()

CHECK:
curl -sI https://target.com | grep -iE "strict-transport|x-frame|x-content|content-security|referrer-policy"

TOOL: securityheaders.com (enter URL → grade A-F based on headers)

MISSING HEADERS → VULNERABILITIES:
Missing X-Frame-Options → Clickjacking possible
Missing CSP → XSS easier to exploit
Missing X-Content-Type-Options → MIME sniffing attacks
Missing HSTS → SSL stripping possible
```

### 3. Set-Cookie — Cookie Security Analysis

```
GOOD: Set-Cookie: session=abc; HttpOnly; Secure; SameSite=Strict; Path=/

BAD:  Set-Cookie: session=abc
      → No HttpOnly: JS can steal with document.cookie
      → No Secure: cookie sent over HTTP too
      → No SameSite: CSRF possible

CHECK FOR EACH COOKIE:
curl -sI https://target.com | grep -i set-cookie

ANALYZE:
  HttpOnly missing?  → XSS can steal session
  Secure missing?    → Cookie sent over HTTP (capture in transit)
  SameSite=None?     → CSRF risk if no CSRF token
  Domain=.target.com? → Cookie shared with all subdomains

Full analysis: [[11 - Cookies Structure Flags Lifecycle]]
```

### 4. Response Body — Finding Leaked Information

```
IN THE HTML BODY, LOOK FOR:
- HTML comments: <!-- TODO: remove admin backdoor at /secret-admin-123 -->
- Hardcoded paths: src="/var/www/html/js/app.js" (server file path!)
- Internal IPs: "apiUrl": "http://10.0.0.50/api"
- API keys: "apiKey": "AIzaSyAbc..." 
- Version strings: "version": "1.2.3-INTERNAL"
- Database errors: "MySQL Error 1064 in query: SELECT * FROM users WHERE..."
- Stack traces: at com.target.AuthService.login(AuthService.java:123)

SEARCH FOR:
curl -s https://target.com | grep -iE "<!--.*-->|TODO|FIXME|password|secret|apikey|api_key|token"
```

### 5. Response Differences — Blind Vulnerabilities

```
Many vulnerabilities are detected by DIFFERENCE in responses,
not by seeing the exploit's result directly.

BLIND SQLi:
  Normal:   /products?id=1    → 200 OK, product page
  True cond: /products?id=1 AND 1=1-- → 200 OK, same page
  False cond: /products?id=1 AND 1=2-- → 200 OK, EMPTY page
  → Page empty on false condition → SQLi confirmed (boolean-based)!

BLIND XSS:
  Payload fires in admin panel (you don't see it directly)
  XSS beacon hits your server → you know it fired

  Track: response time, response length, response content differences

TOOLS:
  Burp Intruder: compare response lengths, status codes across payloads
  Burp Comparer: diff two responses
  diff <(curl response1) <(curl response2)
```

### 6. Response Headers for Attack Planning

```
RESPONSE HEADER:                    ATTACKER INFERS:
────────────────────────────────────────────────────────────────
Server: Apache/2.4.29               Search CVEs for this version
X-Powered-By: PHP/5.6.40           PHP 5.6 = end-of-life! Lots of CVEs
Via: 1.1 squid/3.5.27              Squid proxy present, specific version
X-Cache: HIT from cache01          CDN/proxy in use, cache poisoning?
Set-Cookie: PHPSESSID=abc          PHP-based app
Set-Cookie: JSESSIONID=abc         Java/Tomcat-based app
Set-Cookie: ASP.NET_SessionId=abc  .NET/IIS-based app
Set-Cookie: laravel_session=abc    Laravel PHP framework
X-Drupal-Cache: HIT                Drupal CMS (check for Drupalgeddon)
X-Generator: Drupal 8              Drupal version (find CVEs)
```

---

## Hands-On: Response Analysis

```bash
# Get only response headers
curl -sI https://target.com

# Get headers + first 100 bytes of body
curl -sv https://target.com 2>&1 | head -50

# Save response headers to file
curl -D response_headers.txt https://target.com -o /dev/null

# Check all security headers at once
curl -sI https://target.com | grep -iE \
  "strict-transport|x-frame|x-content-type|content-security|referrer-policy|permissions-policy|x-xss|set-cookie"

# Compare two responses (blind testing)
diff <(curl -s https://target.com/?id=1) <(curl -s https://target.com/?id=2)

# Extract all cookies
curl -c cookies.txt -s https://target.com -o /dev/null
cat cookies.txt

# Check response size (useful for blind testing)
curl -sI https://target.com | grep -i content-length

# Full verbose HTTP/2 exchange
curl -v --http2 https://target.com 2>&1
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Server version in headers | Remove Server header or set to generic value |
| X-Powered-By leaking tech | Remove this header entirely |
| Stack traces in error responses | Generic error pages in production |
| Missing security headers | Implement full security header set |
| Sensitive data in HTML comments | Audit templates, enforce code review |
| Set-Cookie without security flags | Add HttpOnly, Secure, SameSite=Lax/Strict |

---

## Related Notes
- [[04 - HTTP Request Structure]] — the request that triggers this response
- [[07 - HTTP Status Codes]] — what each status code means
- [[11 - Cookies Structure Flags Lifecycle]] — Set-Cookie deep dive
- [[Module 03 - HTTP Headers Security]] — all security headers
