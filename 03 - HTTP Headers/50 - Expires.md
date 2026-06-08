---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.50 Expires — Caching Behavior"
---

# 03.50 — Expires

## What is it?

`Expires` is an HTTP/1.0 response header that sets an absolute date/time after which the cached response is considered stale. It was the original way to control cache duration before `Cache-Control: max-age` was introduced in HTTP/1.1. If both are present, `Cache-Control: max-age` takes precedence.

---

## Format

```
Expires: Thu, 01 Jan 2030 00:00:00 GMT    → cache until this date
Expires: 0                                 → already expired (don't cache)
Expires: Thu, 01 Jan 1970 00:00:00 GMT    → past date = expired = don't cache
```

---

## VAPT Relevance

```
SCENARIO 1: Far-future Expires on sensitive content
  Expires: Thu, 01 Jan 2030 00:00:00 GMT
  
  Sensitive data will be served from cache for years!
  → If shared CDN → all users get cached sensitive response!

SCENARIO 2: Conflicting headers
  Cache-Control: no-cache
  Expires: Thu, 01 Jan 2030 00:00:00 GMT
  
  Cache-Control wins in HTTP/1.1 → response won't be cached.
  But old HTTP/1.0 proxies only see Expires → cache for years!

SCENARIO 3: Session token in cached response
  Expires: [far future]
  Body: {"sessionToken": "abc123"}
  
  Other users on shared connection get cached token!
```

---

## Server Time Disclosure

```
Expires header reveals server's clock:
  Date: Thu, 01 Jun 2024 12:00:00 GMT    ← current server time
  Expires: Thu, 01 Jun 2024 12:00:30 GMT ← expires in 30 seconds
  
  → Exact server time known!
  → Can affect time-based security tokens that use server time!
  → Predictable "random" seeds if app uses time as seed!
```

---

## Testing

```bash
# Check Expires header:
curl -sI https://target.com | grep -iE "expires|date|cache-control"

# Check for far-future Expires on authenticated endpoints:
curl -sI https://target.com/account -H "Cookie: session=test" | grep expires

# Detect time-based info: compare Date and Expires to find max-age:
curl -sI https://target.com/ | grep -iE "^date|^expires"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Far-future Expires on sensitive pages | Use `Cache-Control: no-store` instead |
| Expires without Cache-Control | Add modern Cache-Control directives |
| Server time disclosure | Acceptable trade-off; don't use time as security seed |

---

## Related Notes
- [[48 - Cache-Control]] — modern cache control
- [[49 - Pragma]] — other legacy header
- [[Module 11 - Web Cache Poisoning]] — caching attacks
