---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.49 Pragma: no-cache — Legacy Cache Control"
---

# 03.49 — Pragma

## What is it?

`Pragma: no-cache` is the HTTP/1.0 equivalent of `Cache-Control: no-cache`. It was the original way to request that caches not serve stale content. In modern HTTP, `Cache-Control` supersedes `Pragma`, but `Pragma` still appears in many apps for backward compatibility.

---

## Modern Relevance

```
HTTP/1.0 (legacy):
  Pragma: no-cache   → don't serve cached version

HTTP/1.1+ (modern):
  Cache-Control: no-cache   → same meaning, takes precedence

WHEN TO SET BOTH:
  For maximum compatibility with old proxies and CDNs:
  Cache-Control: no-store, no-cache
  Pragma: no-cache
```

---

## VAPT Relevance: Missing Pragma on Sensitive Pages

```
Some apps only set Pragma: no-cache but forget Cache-Control.
Old proxies honor Pragma, modern ones honor Cache-Control.

RESULT: Content may be cached in modern CDN even with Pragma: no-cache!

SCENARIO:
  Legacy banking app:
    Pragma: no-cache     ← old way
    (no Cache-Control)
  
  Modern CDN in front: ignores Pragma, caches response!
  → Account pages cached!
  → Cache deception possible!
```

---

## Testing

```bash
# Check if Pragma is set alongside Cache-Control:
curl -sI https://target.com/account | grep -iE "pragma|cache-control"

# If only Pragma → check if CDN honors it or ignores it:
curl -sI https://target.com/account | grep -i "age\|x-cache"
# If Age header present → CDN is caching despite Pragma!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Only Pragma, no Cache-Control | Add `Cache-Control: no-store, private` for sensitive pages |
| Relying on Pragma for security | Use Cache-Control instead (Pragma is deprecated for responses) |

---

## Related Notes
- [[48 - Cache-Control]] — modern cache control header
- [[50 - Expires]] — another legacy cache header
