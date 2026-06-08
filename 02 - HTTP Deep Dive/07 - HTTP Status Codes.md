---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.07 HTTP Status Codes — Full Reference"
---

# 02.07 — HTTP Status Codes — Full Reference

## What is it?

HTTP status codes tell you the result of a request. For pentesters, each status code carries security intelligence: 200 vs 302 vs 403 vs 500 are completely different signals during testing. Understanding them helps you interpret application behavior, detect hidden endpoints, and infer backend logic.

---

## Status Code Categories

```
1xx: Informational  — request received, continue
2xx: Success        — request was received and processed
3xx: Redirection    — further action needed
4xx: Client Error   — client made a bad request
5xx: Server Error   — server failed to process
```

---

## 1xx — Informational

```
100 Continue
  Server has received request headers, client should send the body.
  Used with Expect: 100-continue header.
  VAPT: Can bypass WAF that inspects first request but not continuation.

101 Switching Protocols
  Server is switching protocols as client requested.
  Most common: WebSocket upgrade.
  VAPT: Confirm WebSocket upgrade, then test WS-specific attacks.
  GET /chat HTTP/1.1
  Connection: Upgrade
  Upgrade: websocket
  → 101 Switching Protocols ← WebSocket established

102 Processing (WebDAV)
  Server processing but not done yet.
  VAPT: May indicate slow processing → DoS / resource exhaustion possible.
```

---

## 2xx — Success

```
200 OK
  Standard success. Most responses.
  VAPT: "200 on /admin" when you shouldn't have access = vulnerability!
        Always compare 200 on protected endpoint vs unprotected.

201 Created
  Resource was created (common for POST to APIs).
  VAPT: If 201 from PUT → file upload worked.
        If 201 without auth → unauthenticated creation!

204 No Content
  Success but no body returned.
  VAPT: Deletion successful. Blind SSRF - sometimes returns 204 on success.
        OPTIONS preflight returns 204 on CORS preflight.

206 Partial Content
  Range request fulfilled (resumable downloads).
  VAPT: Test range header injection: Range: bytes=0-9999999999 → DoS?
        Range override for zip slip in some frameworks.
```

---

## 3xx — Redirection

```
301 Moved Permanently
  Resource moved, browser caches this.
  VAPT: HTTP → HTTPS redirect should be 301 (permanent).
        If 301 without HSTS → SSL strip still works on first visit.

302 Found (Temporary Redirect)
  Temporary redirect.
  VAPT: After login → redirect to dashboard.
        Open redirect: /redirect?url=https://evil.com → 302 to evil.com
        Parameter-based redirect → test for open redirect!

303 See Other
  After POST, redirect to GET result (PRG pattern).

304 Not Modified
  Resource hasn't changed (ETag/If-Modified-Since matched).
  VAPT: Confirms cache behavior. Part of cache poisoning analysis.

307 Temporary Redirect
  Like 302 but preserves HTTP method (POST stays POST).
  VAPT: More dangerous than 302 for CSRF — preserves POST body.

308 Permanent Redirect
  Like 301 but preserves HTTP method.
```

---

## 4xx — Client Errors

```
400 Bad Request
  Server can't understand the request syntax.
  VAPT: Input validation exists. Check what payload triggers this.
        WAF may return 400 for blocked payloads (vs 403).
        Malformed headers → 400 (useful for request smuggling detection).

401 Unauthorized
  Authentication required (not provided or invalid).
  VAPT: ← Authentication required. Can you forge auth?
        Check: is the 401 actually enforced? Or just a hint?
        Try: empty credentials, null auth, JWT none algorithm.
        Compare: authenticated vs unauthenticated response.

403 Forbidden
  Authenticated but not authorized.
  VAPT: You're known but blocked. Try:
        - Different HTTP method (GET → POST)
        - Different Content-Type
        - Adding X-Forwarded-For: 127.0.0.1
        - Changing URL case: /Admin vs /admin
        - URL encoding: /a%64min
        - Adding path: /forbidden/../forbidden
        - Different User-Agent
        403 vs 404 reveals resource existence!

404 Not Found
  Resource doesn't exist (or server hiding it).
  VAPT: 404 = endpoint doesn't exist.
        Custom 404 pages may reveal server/framework.
        Some apps return 404 for auth-protected resources (security by obscurity).
        Gobuster/ffuf finds 200s hidden among 404s.

405 Method Not Allowed
  Method not supported for this resource.
  VAPT: Tells you which methods ARE allowed (from Allow header).
        If 200 on GET but 405 on DELETE → endpoint exists, only GET allowed.

408 Request Timeout
  Server timed out waiting for the request.
  VAPT: Slowloris/slow HTTP attacks → connection keep alive → 408.

429 Too Many Requests
  Rate limit hit.
  VAPT: Rate limiting exists. Try to bypass:
        - X-Forwarded-For header rotation
        - Different User-Agent
        - Distributed attack
        How long is the backoff? Is it IP-based? Token-based?

```

---

## 5xx — Server Errors

```
500 Internal Server Error
  Something broke on the server.
  VAPT: VERY interesting!
        500 = application crashed = you hit something unexpected!
        This is the signal: injection worked, just need to refine
        Check response body for stack trace (reveals code + line numbers)
        SQLi: 500 on 'single-quote input = syntax error in SQL query
        Try to get useful info from the error message

501 Not Implemented
  Method not implemented.
  Rarely seen legitimately.

502 Bad Gateway
  Proxy/LB can't reach backend.
  VAPT: Backend is down or unreachable.
        During request smuggling → target victim gets 502 while your request runs.

503 Service Unavailable
  Server temporarily unable to handle requests.
  VAPT: DoS successful? Rate limiting kicking in? Maintenance mode?
        Slow down your attack and retry.

504 Gateway Timeout
  Backend didn't respond to proxy in time.
  VAPT: Time-based SQLi working?
        Server is slow to process your input (hints at blind injection).
```

---

## Status Code Reference Table

```
CODE   MEANING             PENTESTING SIGNIFICANCE
────────────────────────────────────────────────────────────────────
200    OK                  Endpoint exists, check auth bypass
201    Created             Resource created — did you need auth?
204    No Content          Action succeeded — deletion? blind SSRF?
301    Permanent Redirect  HTTP→HTTPS (good); open redirect (bad)?
302    Found               Open redirect? Post-login redirect?
304    Not Modified        Caching behavior confirmed
400    Bad Request         Input validation; WAF blocking
401    Unauthorized        Need auth; can you forge it?
403    Forbidden           Need auth; 403 bypass techniques
404    Not Found           Hidden resources? 404 vs 403?
405    Method Not Allowed  Map allowed methods (check Allow header)
429    Too Many Requests   Rate limiting; try to bypass
500    Internal Server Error  INJECTION POINT? Check error detail
502    Bad Gateway         Backend unreachable
503    Service Unavailable DoS working? Rate limit?
504    Gateway Timeout     Time-based attacks working?
```

---

## Security Context — Status Codes in VAPT

### Finding Hidden Endpoints (Gobuster/ffuf)

```bash
# ffuf — fuzz for directories, filter by status code
ffuf -u https://target.com/FUZZ \
     -w /usr/share/seclists/Discovery/Web-Content/common.txt \
     -mc 200,201,204,301,302,401,403    # interesting codes
     -fc 404                            # exclude 404s

# gobuster
gobuster dir -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/big.txt \
  -s "200,201,204,301,302,307,401,403"

# INTERESTING FINDINGS:
# 403 on /admin → endpoint EXISTS, just forbidden → try bypass!
# 401 on /api/users → needs auth → what auth?
# 200 on /backup.zip → direct file download!
```

### 403 Bypass Techniques

```bash
# Try different methods
curl -X POST https://target.com/admin
curl -X PUT https://target.com/admin
curl -X HEAD https://target.com/admin

# Add IP bypass headers
curl -H "X-Forwarded-For: 127.0.0.1" https://target.com/admin
curl -H "X-Real-IP: 127.0.0.1" https://target.com/admin
curl -H "True-Client-IP: 127.0.0.1" https://target.com/admin

# URL encoding
curl "https://target.com/%61dmin"    # /admin
curl "https://target.com/ADMIN"
curl "https://target.com/admin/"    # trailing slash
curl "https://target.com/./admin"
curl "https://target.com//admin"
curl "https://target.com/admin..;/"  # Spring boot bypass

# Different Accept header (API may return differently)
curl -H "Accept: application/json" https://target.com/admin
```

### 500 = Injection Confirmation

```bash
# Single quote test → 500 may indicate SQLi
curl "https://target.com/product?id=1'"
# If 500 → SQL syntax error → injection point!

# Double quote
curl "https://target.com/product?id=1\""

# Check the response body:
curl "https://target.com/product?id=1'" -s | grep -i "sql\|mysql\|syntax\|error"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Stack traces in 500 responses | Use generic error pages in production |
| 403 bypassable via URL encoding | Normalize URLs before access control check |
| 200 on admin endpoints for all users | Implement proper authorization, not just authentication |
| Open redirect via 302 | Whitelist redirect destinations |
| Rate limit 429 bypassable | Implement server-side rate limiting per user token |

---

## Related Notes
- [[04 - HTTP Request Structure]] — requests that generate these responses
- [[05 - HTTP Response Structure]] — full response anatomy
- [[Module 03 - Access Control]] — 401 and 403 bypass
- [[Module 01 - SQL Injection]] — 500 as injection signal
