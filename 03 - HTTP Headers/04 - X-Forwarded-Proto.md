---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.04 X-Forwarded-Proto — HTTP Downgrade"
---

# 03.04 — X-Forwarded-Proto

## What is it?

`X-Forwarded-Proto` indicates the original protocol (HTTP or HTTPS) used by the client before it hit a proxy. Load balancers and CDNs that terminate HTTPS add this header so the backend knows whether the original connection was secure.

---

## How It Works

```
HTTPS TERMINATION AT LOAD BALANCER:
  Client ──HTTPS──→ [Load Balancer] ──HTTP──→ Backend
  
  Load Balancer adds:
  X-Forwarded-Proto: https   ← tells backend original was HTTPS
  
  Backend can generate https:// URLs and set Secure cookies

WITHOUT THIS HEADER:
  Backend sees HTTP connection (to LB) → might think client is on HTTP
  → Generate http:// links → downgrade attack in email/responses!
```

---

## Attack: HTTP Downgrade via Spoofing

```
If app checks X-Forwarded-Proto to decide whether to redirect to HTTPS:

VULNERABLE CODE:
  if request.headers.get('X-Forwarded-Proto') != 'https':
      redirect_to_https()

BYPASS:
GET /secret HTTP/1.1
Host: target.com
X-Forwarded-Proto: https   ← claim we're already on HTTPS

→ App skips HTTPS redirect → serves response over HTTP!
→ If done via MITM, attacker can see the "HTTPS" page content!

ALSO USEFUL:
  App sets "Secure" flag on cookie ONLY if X-Forwarded-Proto: https
  Spoof it → app thinks you're HTTPS → sets Secure cookie → but sent over HTTP!
```

---

## Testing

```bash
# Check if app enforces HTTPS based on X-Forwarded-Proto
curl -k https://target.com/ -H "X-Forwarded-Proto: http"
# Does it redirect again? Or serve directly?

# Does changing to http bypass Secure cookie requirement?
curl -k https://target.com/login \
  -H "X-Forwarded-Proto: http" \
  -X POST -d "user=admin&pass=test" -v 2>&1 | grep -i set-cookie

# Missing Secure flag on cookie?
# Set-Cookie: session=abc (no Secure) → cookie sent over HTTP
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| HTTPS enforcement based on XFP | Trust XFP only from known proxies; use HSTS |
| Cookie Secure flag dependent on XFP | Always set Secure flag regardless |
| XFP spoofed to claim HTTPS | Strip XFP from client requests at load balancer |

---

## Related Notes
- [[01 - Host Header]] — Host header attacks
- [[02 - X-Forwarded-For]] — companion forwarding header
- [[Module 03 - HTTP Headers Security]] — HSTS and Secure headers
