---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.46 Access-Control-Max-Age — Preflight Caching"
---

# 03.46 — Access-Control-Max-Age

## What is it?

`Access-Control-Max-Age` specifies how long (in seconds) the browser should cache the preflight CORS response. A cached preflight means subsequent cross-origin requests of the same type don't need to send a preflight OPTIONS request again — speeding up requests.

From a security perspective, an excessively long max-age means that even if you fix a CORS misconfiguration, attackers' browsers may still use the cached (vulnerable) policy for hours.

---

## Format

```
Access-Control-Max-Age: 3600     → cache preflight for 1 hour
Access-Control-Max-Age: 86400    → cache for 24 hours (too long!)
Access-Control-Max-Age: -1       → don't cache (always preflight)
Access-Control-Max-Age: 0        → don't cache

Browser limits:
  Chrome: max 7200 seconds (2 hours)
  Firefox: max 86400 seconds (24 hours)
```

---

## Security Implication: Stale CORS Policy Cache

```
SCENARIO:
  Day 1: CORS misconfiguration exists. Attacker sends preflight.
         Access-Control-Max-Age: 86400 → cached for 24 hours!
  
  Day 1 (1 hour later): Admin discovers and fixes CORS policy.
  
  Day 2: Attacker's browser still has old (vulnerable) preflight cached.
         For 23 more hours → can send cross-origin requests without new preflight!
         
  IMPACT: Fixing a CORS issue doesn't immediately protect all users!
  
  MITIGATION: Set short max-age for CORS policies
              Clear affected browsers (inform users to clear cache if needed)
```

---

## Attack: Timing the Preflight Window

```
If max-age is very short (or 0):
  → Every cross-origin request requires a preflight
  → Double the requests → potential performance DoS
  
  (Flood server with OPTIONS requests)
  → Each requires processing → server load!
  
  This is a minor DoS vector, not critical.
```

---

## Checking Cache Duration

```bash
# Check preflight max-age:
curl -X OPTIONS https://target.com/api \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -sI | grep -i "max-age"

# If max-age is very high → long window for stale policy exploitation
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Very long max-age | Keep max-age reasonable (600-3600 seconds) |
| CORS fix not taking immediate effect | Inform users or use short max-age during policy transitions |
| DoS via preflight flood | Rate limit OPTIONS requests |

---

## Related Notes
- [[41 - Access-Control-Allow-Origin]] — ACAO header
- [[43 - Access-Control-Allow-Methods]] — methods in preflight
- [[Module 08 - CORS]] — full CORS exploitation
