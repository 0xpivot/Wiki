---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.26 Range — Partial Content, DoS"
---

# 03.26 — Range

## What is it?

The `Range` request header asks the server to send only a portion (byte range) of a resource. Useful for resumable downloads and video streaming. From a VAPT perspective, it can be abused for DoS, WAF bypass, and information extraction.

---

## Format

```
Range: bytes=0-499         → first 500 bytes
Range: bytes=500-999       → bytes 500 to 999
Range: bytes=-500          → last 500 bytes
Range: bytes=0-            → from byte 0 to end (entire file!)
Range: bytes=0-0,-1        → first and last byte (multipart range)

Server responds with:
  206 Partial Content       → range honored
  200 OK                    → range ignored (full content)
  416 Range Not Satisfiable → invalid range
```

---

## Attack 1: Range DoS (Amplification)

```
RANGE REQUEST BOMB:
  Range: bytes=0-0,1-1,2-2,3-3,...,9999-9999
  
  Server must create a multipart response for each range!
  → Single request causes massive server CPU/memory usage!
  → DoS via range amplification

MEMORY EXHAUSTION:
  Range: bytes=0-999999999999  ← request "to infinity"
  → Server may try to allocate huge buffer!
```

---

## Attack 2: WAF Bypass via Partial Request

```
WAFs scan complete request bodies for attack payloads.

BYPASS:
  Fragment malicious payload across range requests:
  
  Request 1: Range: bytes=0-100   (sends innocent part)
  Request 2: Range: bytes=101-200 (sends attack payload)
  
  WAF may not reassemble → misses detection!
  
  This is harder to exploit since Range is for responses from server,
  not request bodies. But works in responses that contain reflected input.
```

---

## Attack 3: Sensitive File Partial Download

```
If a sensitive file is accessible but access is monitored:
  - Normal download might trigger DLP alerts
  - Range requests download in pieces
  - Might avoid size-based monitoring triggers

Range: bytes=0-1023     → first 1KB of /etc/passwd equivalent
Range: bytes=1024-2047  → next 1KB
...
```

---

## Attack 4: Information Disclosure via Range Headers

```
SERVER RESPONSE REVEALS:
  Content-Range: bytes 0-499/5242880
                              ^^^^^^^
                              Total file size! (5MB)
  
  → Know exact size of internal files!
  → Can infer content based on size vs. expected content

Accept-Ranges: bytes    → server supports range requests
Accept-Ranges: none     → range requests not supported
```

---

## Testing

```bash
# Test if ranges are supported
curl -H "Range: bytes=0-10" https://target.com/file.pdf -v 2>&1 | grep "HTTP\|Content-Range"

# Get file size via Range:
curl -H "Range: bytes=0-0" https://target.com/file.pdf -v 2>&1 | grep "Content-Range"
# Content-Range: bytes 0-0/5242880  → file is exactly 5242880 bytes!

# DoS test (careful - only on authorized targets):
# Range: bytes=0-0,1-1,2-2  (create many small ranges)
curl -H "Range: bytes=0-0,1-1,2-2,3-3" https://target.com/largefile.pdf -v

# Negative range (last N bytes)
curl -H "Range: bytes=-100" https://target.com/logfile.txt
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Range DoS via many ranges | Limit number of ranges per request (e.g., max 5) |
| Size disclosure via Content-Range | Don't expose total size for sensitive files |
| Unbounded range requests | Limit max range size |

---

## Related Notes
- [[26 - Content-Disposition]] — download vs inline behavior
- [[02.16 - HTTP Caching]] — caching and partial content
- [[Module 12 - DoS Techniques]] — denial of service methods
