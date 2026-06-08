---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.48 Cache-Control — Sensitive Data Caching"
portswigger_labs: ["Web cache poisoning — 13 labs", "Web cache deception — 4 labs"]
---

# 03.48 — Cache-Control

## What is it?

`Cache-Control` is the primary mechanism for controlling how responses are cached by browsers and intermediary caches (CDN, proxy, reverse proxy). Misconfigured caching can store sensitive authenticated data in shared caches, expose private content, or enable cache poisoning attacks.

---

## Key Directives

```
no-store:         → NEVER cache (not in browser, not in proxy)
                    Required for truly sensitive responses!
no-cache:         → Can cache but MUST revalidate with server before use
                    (Misleading name — it DOES cache, just validates first!)
public:           → Can be cached by any cache (CDN, proxy, browser)
private:          → Only browser cache, not shared/proxy caches
max-age=N:        → Cache for N seconds
s-maxage=N:       → Cache for N seconds in shared caches (CDN) only
must-revalidate:  → Must revalidate with server when stale
proxy-revalidate: → Shared caches must revalidate when stale
immutable:        → Never revalidate (for versioned static assets)
```

---

## Attack 1: Sensitive Data Cached in Shared Cache

```
VULNERABLE RESPONSE:
  HTTP/1.1 200 OK
  Cache-Control: max-age=3600    ← cached for 1 hour!
  Content-Type: application/json
  
  {"username":"admin","ssn":"123-45-6789","balance":$5000}

IF CDN caches this → ALL users who request same URL get admin's data!
(CDNs don't differentiate users for same URL without proper cache keys)

FIX:
  Cache-Control: no-store, private    ← never cache sensitive data
  OR:
  Cache-Control: no-cache, private    ← revalidate per-user
```

**PortSwigger Labs:** Web cache deception (4 labs)

---

## Attack 2: Web Cache Deception

```
ATTACK:
  1. Target: https://target.com/profile  (authenticated, sensitive data)
  2. Attacker tricks victim to visit: https://target.com/profile/nonexistent.css
  3. App ignores the .css part → serves profile page for victim!
  4. Cache: "Oh, *.css → cache it!" → caches victim's profile!
  5. Attacker visits: https://target.com/profile/nonexistent.css
  → Gets cached victim profile!

REQUIRES:
  - App returns same content for /profile and /profile/*.css
  - Cache stores based on URL (sees .css → cacheable)
  - No proper Cache-Control headers on profile page
```

---

## Attack 3: Web Cache Poisoning

```
CACHE POISONING ATTACK:
  1. Find an unkeyed input (header that affects response but not cache key)
     e.g., X-Forwarded-Host: evil.com
  2. Inject payload:
     GET / HTTP/1.1
     Host: target.com
     X-Forwarded-Host: evil.com"><script>alert(1)</script>
  3. If server reflects X-Forwarded-Host in response AND caches it:
     → Cached XSS served to all users!

COMMON UNKEYED INPUTS:
  X-Forwarded-Host
  X-Forwarded-For
  X-Original-URL
  User-Agent (sometimes)
  Accept-Language
```

**PortSwigger Labs:** Web cache poisoning (13 labs)

---

## Checking Caching Behavior

```bash
# Check Cache-Control on sensitive responses
curl -sI https://target.com/account -b "session=token" | grep -i "cache"

# Check what CDN caches (look for age header):
curl -sI https://target.com/ | grep -iE "age|x-cache|cf-cache-status|x-varnish"
# Age: 300 → response is 300 seconds old in cache
# X-Cache: HIT → served from cache

# Test cache poisoning: send with unkeyed header, then without:
curl -sI https://target.com/ -H "X-Forwarded-Host: evil.com"
curl -sI https://target.com/  # does response differ?

# Check if authenticated response is cached:
curl https://target.com/profile -H "Cookie: session=legit" -sI | grep cache-control
# If "public" or no "no-store" → potentially cacheable!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Sensitive data cached | `Cache-Control: no-store, private` |
| Authentication bypassed via cache | Use `Vary: Cookie` so cache keys include cookie |
| Cache poisoning via unkeyed inputs | Remove unkeyed inputs from response; use proper cache keys |
| Web cache deception | Return 404 for non-existent paths; apply strict Cache-Control |

---

## Related Notes
- [[27 - If-Modified-Since and If-None-Match]] — conditional caching
- [[49 - Pragma]] — legacy cache control
- [[50 - Expires]] — legacy expiry
- [[Module 11 - Web Cache Poisoning]] — full cache poisoning module
- [[02.16 - HTTP Caching]] — caching deep dive
