---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.04 HTTP Request Structure"
---

# 02.04 — HTTP Request Structure

## What is it?

An **HTTP request** is the message your browser (or any client) sends to a server to ask for something. Every request has a defined structure. Understanding every part is essential for pentesting — you inject into parts, modify them, and observe the effect.

---

## Request Anatomy

```
┌─────────────────────────────────────────────────────────────────┐
│                       REQUEST LINE                              │
│  METHOD   URL_PATH              HTTP_VERSION                    │
│  POST      /login               HTTP/1.1                        │
├─────────────────────────────────────────────────────────────────┤
│                        HEADERS                                  │
│  Host: target.com                                               │
│  Content-Type: application/x-www-form-urlencoded               │
│  Content-Length: 29                                             │
│  Cookie: session=abc123; theme=dark                             │
│  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)        │
│  Accept: text/html,application/xhtml+xml                        │
│  Accept-Language: en-US,en;q=0.9                                │
│  Referer: https://target.com/                                   │
│  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  │
│  Origin: https://target.com                                     │
│  Connection: keep-alive                                         │
├─────────────────────────────────────────────────────────────────┤
│                    BLANK LINE (mandatory)                        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     REQUEST BODY                                │
│  username=admin&password=secret                                 │
│  (only for POST/PUT/PATCH — empty for GET/HEAD/DELETE)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Request Line

```
METHOD  PATH                          VERSION
POST    /api/v2/users?sort=name       HTTP/1.1
│        │                │
│        │                └─ Query string: additional parameters
│        └──────────────── URL path: resource being requested
└───────────────────────── HTTP method: action to perform

FULL URL BREAKDOWN (not sent — Host header carries the domain):
https://target.com:443/api/v2/users?sort=name&page=1#section
│        │          │   │             │              │
│        │          │   │             │              └ Fragment (not sent to server)
│        │          │   │             └────────────── Query string
│        │          │   └──────────────────────────── Path
│        │          └──────────────────────────────── Port
│        └─────────────────────────────────────────── Host
└──────────────────────────────────────────────────── Scheme
```

---

## Part 2: Headers

Each header is: `Header-Name: value` followed by CRLF (`\r\n`)

```
ESSENTIAL HEADERS:
──────────────────
Host: target.com
  Required in HTTP/1.1. Tells server which virtual host you want.
  ATTACK: Host header injection → password reset poisoning, SSRF

Content-Type: application/json
  Tells server what format the body is in.
  ATTACK: Change to text/xml for XXE, change to JSON to bypass WAF

Content-Length: 29
  Exact byte count of the body.
  ATTACK: Content-Length/Transfer-Encoding desync → request smuggling

Cookie: session=abc123; csrf=xyz
  Sends stored cookies to server.
  ATTACK: Session hijacking, CSRF token bypass

Authorization: Bearer TOKEN
  Authentication credentials.
  ATTACK: JWT manipulation, weak token prediction

Referer: https://other-site.com/
  Where the request came from. (Note: intentional misspelling in RFC)
  ATTACK: Referer-based CSRF bypass, info disclosure

Origin: https://target.com
  CORS origin. Server decides if cross-origin request allowed.
  ATTACK: CORS misconfiguration

User-Agent: Mozilla/5.0 ...
  Identifies the client.
  ATTACK: Some apps behave differently based on User-Agent
  Try: User-Agent: sqlmap → might reveal debug mode
  Try: User-Agent: python-requests → might disable WAF rules

X-Forwarded-For: 1.2.3.4
  Client's real IP (set by proxies/load balancers).
  ATTACK: Spoof to bypass IP-based access controls

Accept: text/html
  What response formats the client accepts.
  ATTACK: Change to application/json to trigger JSON response (may bypass XSS filters)
```

---

## Part 3: Request Body

```
BODY FORMATS (determined by Content-Type):

1. URL-encoded form (HTML forms):
   Content-Type: application/x-www-form-urlencoded
   Body: username=admin&password=secret&token=abc123

2. Multipart form data (file uploads):
   Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryXXXX
   Body:
     ------WebKitFormBoundaryXXXX
     Content-Disposition: form-data; name="file"; filename="shell.php"
     Content-Type: image/jpeg
     ←blank line→
     <?php system($_GET['cmd']); ?>
     ------WebKitFormBoundaryXXXX--

3. JSON:
   Content-Type: application/json
   Body: {"username":"admin","password":"secret"}

4. XML:
   Content-Type: application/xml
   Body: <?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>

5. Raw binary (file upload, protobuf, etc.)
```

---

## Security Context — Request Parts in VAPT

### Every Field is an Attack Vector

```
REQUEST LINE:
  Method:   PUT/DELETE/TRACE → dangerous if no auth
  Path:     /admin/../../etc/passwd → path traversal
  Version:  HTTP/1.0 → may bypass some WAF rules

HEADERS (most interesting for attacks):
  Host:           password reset poisoning, cache poisoning, SSRF
  Cookie:         session hijacking, CSRF token bypass
  Content-Type:   XXE (switch to XML), content sniffing attacks
  Content-Length: request smuggling
  Transfer-Encoding: request smuggling
  X-Forwarded-For: IP bypass for admin access
  Referer:        CSRF protection bypass (if referer-based)
  Authorization:  JWT attacks, basic auth brute force
  Origin:         CORS bypass
  User-Agent:     fingerprinting, WAF bypass, bot detection bypass

BODY:
  Parameters:  SQLi, XSS, command injection, SSRF, template injection
  JSON keys:   mass assignment, prototype pollution
  XML content: XXE
  File name:   path traversal in uploads (../../etc/passwd.jpg)
  File content: webshell upload, polyglot files
```

### Burp Suite — Reading Every Part

```
In Burp Suite, every part of the request is visible and modifiable:

RAW view:
POST /api/login HTTP/1.1
Host: target.com
Content-Type: application/json
Content-Length: 42
Cookie: session=abc; PHPSESSID=xyz

{"username":"admin","password":"password"}

INSPECTOR panel (right side) decodes:
  Query Parameters: (none for this POST)
  Body Parameters: username=admin, password=password
  Request Cookies: session=abc, PHPSESSID=xyz
  Request Headers: all headers listed

Right-click any value → Send to Intruder → fuzz it!
```

---

## Hands-On: Crafting Requests

```bash
# Full GET request with curl
curl -v \
  -H "Host: target.com" \
  -H "Cookie: session=abc123" \
  -H "X-Forwarded-For: 127.0.0.1" \
  -H "User-Agent: Mozilla/5.0" \
  "https://target.com/api/users"

# POST with JSON body
curl -v -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"username":"admin","password":"test"}' \
  "https://target.com/api/login"

# POST form-encoded
curl -v -X POST \
  -d "username=admin&password=test&token=csrf_token" \
  "https://target.com/login"

# Multipart file upload
curl -v -X POST \
  -F "file=@shell.php;type=image/jpeg" \
  -F "submit=Upload" \
  -H "Cookie: session=abc" \
  "https://target.com/upload"

# Custom raw HTTP (netcat — full control)
printf "POST /login HTTP/1.1\r\nHost: target.com\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 29\r\n\r\nusername=admin&password=test" | nc target.com 80
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Trusting X-Forwarded-For without validation | Only trust from known proxy IPs |
| Verbose User-Agent triggering different behavior | Treat all clients equally in security logic |
| Content-Type not validated | Reject requests with unexpected Content-Type |
| Request body size unlimited | Limit max body size to prevent memory exhaustion |
| Headers reflected back in response | Sanitize before reflecting (XSS via headers) |

---

## Related Notes
- [[05 - HTTP Response Structure]] — the other side of the conversation
- [[06 - HTTP Methods]] — all HTTP methods and their attacks
- [[08 - URLs Anatomy]] — URL breakdown
- [[11 - Cookies Structure Flags Lifecycle]] — cookie details
- [[Module 09 - HTTP Request Smuggling]] — abusing Content-Length and Transfer-Encoding
