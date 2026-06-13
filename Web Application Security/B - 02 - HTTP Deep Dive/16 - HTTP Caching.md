---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.16 HTTP Caching (Cache-Control, ETag, If-Modified-Since)"
---

# 02.16 — HTTP Caching (Cache-Control, ETag, If-Modified-Since)

## What is it?

**HTTP caching** allows responses to be stored and reused without making a new request to the origin server. Caches exist in browsers, CDNs, and proxy servers. For pentesters, caching creates opportunities for **cache poisoning** and **sensitive data exposure** — getting a malicious response cached and served to many victims.

---

## How Caching Works

```
FIRST REQUEST (cache miss):
  Browser → [CDN Cache] → Origin Server
  Origin responds with content + caching headers
  CDN stores the response

SECOND REQUEST (cache hit):
  Browser → [CDN Cache]
  CDN returns cached response (no origin server involved!)
  Fast, no origin server load

CACHE KEY:
  What makes a cache entry unique?
  Default: URL (scheme + host + path + query string)
  Cache key: https://target.com/page?id=1
  Different key: https://target.com/page?id=2 (separate cache entry)
```

---

## Caching Headers

### Cache-Control (request and response)

```
RESPONSE HEADERS (server tells cache how to store):

Cache-Control: no-store
  → Never store this response. Not even the browser should cache.
  → Use for: auth pages, personal data, session-specific content

Cache-Control: no-cache
  → Store but ALWAYS validate with origin before using.
  → NOT "no cache" — it DOES cache, but validates first.
  → Server responds with 304 Not Modified if unchanged.

Cache-Control: public
  → Any cache (CDN, proxy, browser) can store this.
  → Use for: public static assets.

Cache-Control: private
  → Only browser can cache. Not CDNs/proxies.
  → Use for: user-specific responses (dashboard, profile).

Cache-Control: max-age=3600
  → Cache valid for 3600 seconds (1 hour) from response time.

Cache-Control: s-maxage=86400
  → Shared cache (CDN) TTL. Overrides max-age for CDNs.

Cache-Control: must-revalidate
  → Once expired, must get fresh copy before serving.

COMBINED EXAMPLES:
Cache-Control: public, max-age=86400        ← CDN cache for 1 day
Cache-Control: private, no-cache            ← browser only, always revalidate
Cache-Control: no-store                     ← never cache (sensitive!)
Cache-Control: public, max-age=31536000, immutable  ← 1 year (static assets with hash in URL)
```

### ETag (Entity Tag)

```
Response: ETag: "abc123def456"
  → Unique identifier for current version of resource.
  → Changes when resource changes.

Next request: If-None-Match: "abc123def456"
  → Server checks if resource matches this ETag
  → If unchanged: 304 Not Modified (no body, just headers)
  → If changed: 200 OK with new ETag + new content

VAPT: ETags can fingerprint server software:
  Apache: ETag based on inode, file size, mtime → leaks filesystem info!
  Fix: FileETag MTime Size (disable inode component)
```

### Last-Modified / If-Modified-Since

```
Response: Last-Modified: Wed, 21 Oct 2024 07:28:00 GMT

Next request: If-Modified-Since: Wed, 21 Oct 2024 07:28:00 GMT
  → Server checks if modified since then
  → Not modified: 304 Not Modified
  → Modified: 200 OK with new content + new Last-Modified

VAPT: Last-Modified reveals when files were last changed.
  Information disclosure about file timestamps.
```

---

## Security Context — Caching in VAPT

### 1. Web Cache Poisoning

Attack cached responses to serve malicious content to all users who hit the cached version. Full details: [[Module 10 - Web Cache Poisoning]].

```
CONCEPT:
1. Find a cache key (URL that gets cached)
2. Find an unkeyed input (header not in cache key but reflected in response)
3. Inject malicious payload into unkeyed input
4. Get the response cached with malicious content
5. All users requesting that URL get the poisoned response!

SIMPLE EXAMPLE:
GET /page HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com        ← unkeyed (not in cache key)

Response:
<script src="https://evil.com/evil.js"></script>  ← host reflected in response!

If this response gets cached → all users get evil.js!
```

### 2. Cache Deception

```
ATTACK: Trick cache into storing user-specific sensitive data,
        then retrieve it.

HOW:
1. Victim visits: https://target.com/profile/evil-name.css
   (attacker tricks victim via social engineering or XSS)

2. App ignores the .css extension → serves /profile page (user's data!)
3. CDN sees .css extension → thinks "static file" → CACHES the profile page!
   Cache key: /profile/evil-name.css
   
4. Attacker visits: https://target.com/profile/evil-name.css
   CDN serves VICTIM'S CACHED PROFILE → attacker gets victim's data!

REQUIREMENTS:
  - App serves content regardless of URL extension
  - Cache caches based on extension/path rules
  
TEST:
  Visit: https://target.com/profile/evil.css
  If you still see your profile → vulnerable!
```

### 3. Sensitive Data in Cache

```
COMMON MISTAKES:
  Personal pages cached with Cache-Control: public
  Authentication responses cached
  CSRF tokens in cached responses → reuse old CSRF token

CHECK CACHE HEADERS ON SENSITIVE PAGES:
curl -sI https://target.com/dashboard | grep -i "cache-control\|pragma\|expires"

SHOULD BE:
  Cache-Control: no-store (or private + no-cache)
  Pragma: no-cache (legacy HTTP/1.0)

IF PUBLIC or MISSING → sensitive data potentially cached in CDN/proxy
```

### 4. Finding Cache Hits

```bash
# Check if response is cached:
curl -sI https://target.com/static/logo.png | grep -i "x-cache\|age\|cf-cache"

X-Cache: HIT from cloudfront       ← cached by CloudFront
Age: 3600                           ← cached 1 hour ago
CF-Cache-Status: HIT                ← Cloudflare cache hit

# Cache miss (first request) vs hit (subsequent):
curl -sI https://target.com/page
# X-Cache: MISS (first request, not cached)
curl -sI https://target.com/page
# X-Cache: HIT (second request, served from cache)

# Test if your injected header gets cached:
curl -sI https://target.com/page -H "X-Forwarded-Host: evil.com"
# If X-Cache: MISS → try GET instead of HEAD to populate cache
curl -s https://target.com/page -H "X-Forwarded-Host: evil.com" > /dev/null
curl -s https://target.com/page  # no X-Forwarded-Host
# Does evil.com appear in response? → cache poisoned!
```

---

## Hands-On: Cache Analysis

```bash
# Analyze caching headers on all resources
curl -sI https://target.com/
curl -sI https://target.com/app.js
curl -sI https://target.com/dashboard
curl -sI https://target.com/api/user/me

# For each: check Cache-Control, X-Cache, Age, ETag

# Test cache poisoning manually:
# 1. Find an unkeyed header that's reflected in response:
curl -s https://target.com/ -H "X-Forwarded-Host: reflected.test" | grep "reflected.test"

# 2. If reflected, send as GET to populate cache:
curl -s https://target.com/ -H "X-Forwarded-Host: evil.com" > /dev/null

# 3. Request without the header — did evil.com get cached?
curl -s https://target.com/ | grep "evil.com"

# param-miner (Burp Extension): automates finding unkeyed inputs
# Install from BApp Store → right-click request → Extensions → Param Miner → Guess everything
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Sensitive pages cached publicly | Set Cache-Control: no-store on all auth/personal pages |
| Cache poisoning via unkeyed headers | Include all headers that affect response in cache key |
| Cache deception | Validate URL path before serving content, ignore unrecognized extensions |
| ETag leaking filesystem info | Configure ETag to use content hash only (not inode) |
| Missing Vary header | Add Vary: Accept-Encoding (or other relevant headers) |

---

## Related Notes
- [[Module 10 - Web Cache Poisoning]] — full cache poisoning attack guide
- [[15 - CDNs Content Delivery Networks]] — CDN as cache layer
- [[14 - Load Balancers]] — LB cache interactions
- [[Module 03 - HTTP Headers Security]] — security headers for caching
