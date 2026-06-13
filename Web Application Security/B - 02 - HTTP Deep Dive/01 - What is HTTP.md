---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.01 What is HTTP?"
---

# 02.01 — What is HTTP?

## What is it?

**HTTP (HyperText Transfer Protocol)** is the foundation of the World Wide Web — the protocol that browsers and servers use to communicate. Every time you visit a website, your browser sends HTTP requests and receives HTTP responses.

HTTP is a **text-based, stateless, request-response protocol** running over TCP (port 80) or TLS/TCP (port 443 for HTTPS).

**Stateless** means each request is completely independent — the server treats every request as if it's the first time it's seeing you, unless you provide a cookie or token to identify yourself.

---

## HTTP in One Picture

```
BROWSER (CLIENT)                        WEB SERVER
     │                                      │
     │  ──── HTTP REQUEST ─────────────→   │
     │  GET /index.html HTTP/1.1            │
     │  Host: example.com                   │
     │  User-Agent: Mozilla/5.0             │
     │  Accept: text/html                   │
     │                                      │
     │  ←─── HTTP RESPONSE ─────────────   │
     │  HTTP/1.1 200 OK                     │
     │  Content-Type: text/html             │
     │  Content-Length: 1234                │
     │                                      │
     │  <html>...</html>                    │
     │                                      │
```

---

## The Request-Response Cycle

```
Step 1: User types https://example.com/page in browser

Step 2: DNS lookup → IP address of example.com

Step 3: TCP connection to IP:443

Step 4: TLS handshake (for HTTPS)

Step 5: Browser sends HTTP REQUEST:
        GET /page HTTP/1.1
        Host: example.com
        [other headers]

Step 6: Server processes request

Step 7: Server sends HTTP RESPONSE:
        HTTP/1.1 200 OK
        Content-Type: text/html
        [other headers]
        [blank line]
        <html>page content</html>

Step 8: Browser renders the HTML

Step 9: For each resource in the HTML (CSS, JS, images):
        Repeat steps 5-7 for each one
```

---

## HTTP is Text-Based

Unlike binary protocols, HTTP messages are human-readable text. You can type HTTP by hand with netcat:

```bash
# Connect to a web server
nc -v example.com 80

# Type this exactly (two newlines at end):
GET / HTTP/1.1
Host: example.com

# Server responds with full HTTP response
```

---

## HTTP is Stateless — Why it Matters

```
REQUEST 1:  POST /login (username=alice, password=secret)
RESPONSE 1: 200 OK (authenticated!)

REQUEST 2:  GET /dashboard
RESPONSE 2: 401 Unauthorized! ← Server forgot about REQUEST 1!

WHY? HTTP has no memory between requests.

SOLUTION: Cookies and sessions
Server issues a "remember you" token in REQUEST 1's response:
  Set-Cookie: session=abc123

Browser sends it in every future request:
  Cookie: session=abc123

Now server recognizes you!
```

---

## Security Context — HTTP Fundamentals in VAPT

### Why Pentesters Need to Master HTTP

```
Every web vulnerability lives inside HTTP:
  SQLi:       Malicious parameter in URL or POST body
  XSS:        Injected script in response body
  CSRF:       Forged request using victim's cookies
  SSRF:       Server-side request via URL parameter
  XXE:        Malicious XML in request body
  JWT attack: Manipulated token in Authorization header
  Command inj: OS commands in HTTP parameters
  IDOR:       Change an ID in URL to access other users' data

You cannot find or exploit web vulnerabilities without
understanding what every part of an HTTP request/response means.
```

### What Burp Suite Intercepts

```
When Burp Suite sits between your browser and the target:

  Your Browser ──→ Burp Proxy ──→ Target Server
                       ↑
                   You see and modify every byte
                   of every HTTP request/response

This is how web pentesting works:
1. Browse normally
2. Burp captures all requests
3. Send to Repeater → modify → send → analyze response
4. Find vulnerabilities in parameters, headers, cookies
```

### Common HTTP Weak Points

```
1. Parameters (GET and POST):
   /search?q=shoes       → inject here for SQLi, XSS, SSRF
   username=admin        → inject here for auth bypass

2. HTTP Headers:
   Host: target.com      → Host header injection
   Cookie: session=abc   → session hijacking
   X-Forwarded-For: ip   → IP bypass
   Referer: url          → open redirect, info disclosure
   User-Agent: browser   → sometimes triggers different behavior

3. URL itself:
   /admin/../../etc/passwd  → path traversal
   /api/v1/users/123        → IDOR (change 123 to 124)

4. HTTP Method:
   GET /api/data           → try PUT, DELETE, PATCH
   OPTIONS shows allowed methods → attack surface mapping
```

---

## Hands-On: Sending Raw HTTP

```bash
# HTTP/1.1 request with curl (verbose — shows all headers)
curl -v http://target.com/

# Custom headers
curl -H "X-Forwarded-For: 127.0.0.1" http://target.com/

# POST request
curl -X POST -d "username=admin&password=test" http://target.com/login

# Follow redirects
curl -L http://target.com/

# HTTP with netcat (manual)
printf "GET / HTTP/1.0\r\nHost: target.com\r\n\r\n" | nc target.com 80

# Save full response (headers + body)
curl -D headers.txt -o body.html http://target.com/

# Proxy through Burp Suite
curl -x http://127.0.0.1:8080 http://target.com/
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| HTTP (no encryption) in use | Enforce HTTPS, add HSTS |
| Sensitive data in URL parameters | Use POST body, not GET params |
| Missing security headers | Add Content-Security-Policy, X-Frame-Options, etc. |
| Verbose error messages | Generic error pages, no stack traces |

---

## Related Notes
- [[02 - HTTP vs HTTPS]] — encryption differences
- [[03 - HTTP Versions]] — HTTP/1.1, HTTP/2, HTTP/3
- [[04 - HTTP Request Structure]] — every part of a request
- [[05 - HTTP Response Structure]] — every part of a response
- [[17 - TLS SSL How HTTPS Works]] — how HTTPS encrypts HTTP
