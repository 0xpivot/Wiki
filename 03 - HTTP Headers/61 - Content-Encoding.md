---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.61 Content-Encoding — Compression Disclosure"
---

# 03.61 — Content-Encoding

## What is it?

`Content-Encoding` specifies how the response body is compressed. Unlike `Transfer-Encoding` (which is about transport), `Content-Encoding` is applied by the origin server and kept through caches. It enables the BREACH compression attack and can occasionally cause request smuggling in combined headers.

---

## Values

```
Content-Encoding: gzip         → gzip compressed (most common)
Content-Encoding: deflate      → deflate compressed
Content-Encoding: br           → Brotli compressed (best ratio)
Content-Encoding: identity     → no encoding (uncompressed)
Content-Encoding: gzip, deflate → multiple encodings (nested, rare)
```

---

## vs Transfer-Encoding

```
Content-Encoding:
  → Applied by ORIGIN server
  → Survives caches (CDN stores compressed version)
  → Client decompresses final response
  → Listed in Accept-Encoding request header
  
Transfer-Encoding:
  → Applied hop-by-hop (proxy to proxy)
  → NOT stored in caches
  → Used for chunked transfer
  → Related to HTTP request smuggling!
```

---

## Attack 1: BREACH via Content-Encoding: gzip

```
BREACH attack exploits HTTP compression + reflected secret + user input:

Content-Encoding: gzip
  → Body is compressed!
  → Compression ratio reveals repeated content!
  → Attack: measure size to guess secret (see note 32 - Accept-Encoding)

IF RESPONSE IS GZIP COMPRESSED AND CONTAINS:
  1. A secret (CSRF token, API key)
  2. Attacker-controlled reflected input
  → BREACH attack possible!
```

---

## Attack 2: Gzip Bomb (DoS)

```
If server decompresses before processing:
  Upload a file or send a body that is:
    - 1KB compressed (gzip)
    - 1GB uncompressed!
  
  Server decompresses → runs out of memory!
  
GZIP BOMB CREATION:
  dd if=/dev/zero bs=1M count=1024 | gzip > bomb.gz
  ls -la bomb.gz  → might be only 1MB compressed but 1GB when expanded!

TEST:
  curl -X POST https://target.com/api/upload \
    -H "Content-Encoding: gzip" \
    --data-binary @bomb.gz
    
  (Only test on authorized targets!)
```

---

## Attack 3: Content-Encoding Confusion

```
CLIENT SENDS COMPRESSED REQUEST (unusual):
  POST /api HTTP/1.1
  Content-Encoding: gzip
  Content-Type: application/json
  
  [gzip compressed JSON]

If server decompresses automatically:
  → WAF might inspect BEFORE decompression → misses payloads!
  → WAF bypass using compressed request body!

ATTACK:
  Compress SQLi payload → server decompresses → SQLi executes!
  WAF: sees compressed gibberish → can't detect → allows!
```

---

## Testing

```bash
# Check if response is compressed:
curl -sI https://target.com | grep -i "content-encoding"
curl -H "Accept-Encoding: gzip" https://target.com -o /dev/null \
  --write-out "%{size_download} bytes compressed vs %{size_download} uncompressed\n"

# Actually decompress response:
curl -H "Accept-Encoding: gzip" https://target.com | gunzip | head -20

# Test gzip request (if server accepts):
echo '{"test":"value"}' | gzip | curl -X POST https://target.com/api \
  -H "Content-Encoding: gzip" \
  -H "Content-Type: application/json" \
  --data-binary @-
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| BREACH via gzip compression | Add CSP, randomize CSRF tokens (BREACH mitigation) |
| Gzip bomb DoS | Limit decompressed body size; reject if ratio too high |
| WAF bypass via compressed request | WAF should decompress before inspection |

---

## Related Notes
- [[32 - Accept-Encoding]] — BREACH attack via compression
- [[20 - Transfer-Encoding]] — different from Content-Encoding
- [[Module 12 - DoS Techniques]] — gzip bomb DoS
