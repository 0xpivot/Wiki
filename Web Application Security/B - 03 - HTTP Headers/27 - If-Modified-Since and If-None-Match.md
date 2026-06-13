---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.27 If-Modified-Since / If-None-Match — Cache Bypass"
---

# 03.27 — If-Modified-Since / If-None-Match

## What is it?

These conditional request headers help browsers avoid re-downloading unchanged resources. The server responds with `304 Not Modified` if the resource hasn't changed, saving bandwidth. From a VAPT perspective, they can be abused to bypass caching, force fresh responses, or fingerprint server behavior.

---

## How Conditional Requests Work

```
FIRST REQUEST:
  GET /page.js HTTP/1.1
  
  RESPONSE:
  HTTP/1.1 200 OK
  Last-Modified: Wed, 01 Jan 2025 12:00:00 GMT    ← timestamp
  ETag: "abc123def456"                              ← content hash

SUBSEQUENT REQUEST (browser uses cached value):
  GET /page.js HTTP/1.1
  If-Modified-Since: Wed, 01 Jan 2025 12:00:00 GMT
  If-None-Match: "abc123def456"
  
  RESPONSE (if unchanged):
  HTTP/1.1 304 Not Modified    ← no body, use cached version
  
  RESPONSE (if changed):
  HTTP/1.1 200 OK              ← fresh content
```

---

## Attack 1: Cache Bypass for Fresh Response

```
PROBLEM: WAF or proxy caches a "clean" response.
         Your attack payload gets cached 404.

BYPASS: Force fresh response with fake ETag:
  GET /target HTTP/1.1
  If-None-Match: "fake-etag-that-wont-match"
  Cache-Control: no-cache
  
  → Server must return fresh 200 response (not cached 304)!
  → WAF re-evaluates fresh request!

CACHE POISONING SETUP:
  1. Poison cache with malicious response
  2. Other users get 304 (server says "use cached" = your poisoned version)
```

---

## Attack 2: ETag as Filesystem Information Leakage

```
Apache httpd ETag for static files:
  ETag: "inode-size-timestamp"
  
  EXAMPLE:
  ETag: "1234f-5678-5abcdef0"
        ^^^^^^ ^^^^
        inode   size
  
  REVEALS: filesystem inode numbers!
  → Partial filesystem info leakage
  
  This was a known Apache vulnerability — most modern configs use
  "FileETag MTime Size" to avoid leaking inode.
  
  Check if server leaks inodes:
  curl -sI https://target.com/index.html | grep -i etag
```

---

## Attack 3: Version/Timestamp Fingerprinting

```
Last-Modified: Fri, 30 May 2025 14:23:01 GMT

REVEALS:
  - Last time file was modified → deployment timestamp!
  - Server timezone
  - Software update schedule

Combined with file path → can infer:
  → "config.js was last updated 3 days ago → recent deployment?"
  → "backup.tar.gz has Last-Modified → it exists and was created when"
```

---

## Attack 4: Bypassing Authentication Checks

```
RARELY: Some apps don't check auth on 304 responses.
  
  1. Log in, request /admin → get 200 + ETag
  2. Log out
  3. Request /admin with If-None-Match → get 304 (cached)!
  
  → Sensitive data served from cache without auth check!
  
  (This is a caching misconfiguration — covered more in Cache-Control note)
```

---

## Testing

```bash
# Get ETag from response
curl -sI https://target.com/file.js | grep -i etag

# Check if ETag leaks inode
curl -sI https://target.com/file.js | grep -i "etag\|last-modified"
# ETag: "4f2c-5678-1234567890abc" → could contain inode

# Force fresh response (bypass cache)
curl -H 'If-None-Match: "nonexistent"' \
     -H "Cache-Control: no-cache" \
     https://target.com/endpoint

# Check 304 without auth (after getting ETag authenticated)
curl -H 'If-None-Match: "<real-etag>"' https://target.com/admin
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| ETag leaks inode numbers | Use `FileETag MTime Size` in Apache config |
| Auth bypass via 304 | Re-validate authentication before all responses |
| Sensitive files with Last-Modified | Avoid caching sensitive/authenticated resources |

---

## Related Notes
- [[48 - Cache-Control]] — controlling caching behavior
- [[02.16 - HTTP Caching]] — full caching security guide
- [[Module 11 - Web Cache Poisoning]] — cache poisoning attacks
