---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.15 Transfer-Encoding"
---

# 02.15 — Transfer-Encoding (chunked, gzip, deflate, br)

## What is it?

**Transfer-Encoding** is an HTTP header that tells the receiver how the message body is encoded for transfer. The most important for pentesters is **chunked** encoding — it's the mechanism behind HTTP Request Smuggling. Other values (gzip, br) handle compression.

---

## Transfer-Encoding vs Content-Encoding

```
TRANSFER-ENCODING: How the data is transferred over the wire (hop-by-hop)
  Chunked: body split into sized chunks
  Applied during transmission → stripped before reaching application

CONTENT-ENCODING: How the content is encoded (end-to-end)
  gzip, br, deflate: compressed content
  Stays encoded until client decodes it
  Content-Encoding: gzip → browser decompresses, shows HTML
```

---

## Chunked Transfer-Encoding

```
USED WHEN: Server doesn't know response length upfront (streaming)

FORMAT:
HTTP/1.1 200 OK
Transfer-Encoding: chunked
Content-Type: text/html

7\r\n           ← chunk size in hexadecimal (7 = 7 bytes)
Hello, \r\n     ← chunk data
6\r\n           ← next chunk size (6 bytes)
World!\r\n      ← chunk data
0\r\n           ← terminal chunk (size 0 = end of body)
\r\n            ← end of chunked body

DECODED BODY: "Hello, World!"

CHUNKED IN REQUESTS:
POST /api/data HTTP/1.1
Transfer-Encoding: chunked

4\r\n
data\r\n
0\r\n
\r\n
```

---

## Content-Encoding Compression Types

```
gzip:    GNU zip compression (most widely supported)
deflate: zlib compression (without gzip header)
br:      Brotli compression (modern, better ratio than gzip)
zstd:    Zstandard (Meta's compression algorithm)
identity: No encoding (passthrough)

CLIENT NEGOTIATION:
  Request: Accept-Encoding: gzip, deflate, br
  Response: Content-Encoding: br  ← server chose Brotli

CURL WITH DECOMPRESSION:
  curl --compressed https://target.com/
```

---

## Security Context — Transfer-Encoding in VAPT

### 1. HTTP Request Smuggling — TE.CL and CL.TE

This is the most critical Transfer-Encoding security issue. Full details in [[Module 09 - HTTP Request Smuggling]]. Summary:

```
THE PROBLEM:
  Front-end (F/E): uses Content-Length to find end of request
  Back-end (B/E): uses Transfer-Encoding: chunked

  OR VICE VERSA

  Both parse the same request DIFFERENTLY → one server's "second request" is the
  other server's "beginning of next request" → REQUEST SMUGGLING!

CL.TE ATTACK:
POST / HTTP/1.1
Content-Length: 6         ← F/E uses this: reads 6 bytes ("0\r\n\r\n")
Transfer-Encoding: chunked ← B/E uses this: reads chunked body

0                         ← F/E stops here (Content-Length: 6 consumed)
                           ← B/E reads: chunk size 0 = end, then POISON below
GPOST HTTP/1.1            ← POISONED: prepended to NEXT request in B/E pipeline!
...

NEXT VICTIM'S REQUEST:
GPOST HTTP/1.1            ← Victim's request prefixed with attacker data!
...actual victim request...
→ Victim gets error for GPOST method → weird behavior
```

### 2. Chunked Encoding Obfuscation

```
WAF may not handle chunked encoding variations:

Standard:
Transfer-Encoding: chunked

Obfuscated variants (to bypass WAF):
Transfer-Encoding: chunked, identity
Transfer-Encoding: chunked\t       ← tab character
Transfer-Encoding: xchunked
Transfer-Encoding:chunked           ← no space after colon
X-Transfer-Encoding: chunked        ← custom header some servers honor
```

### 3. Compression-Based Info Leakage (BREACH)

```
If response contains:
1. Sensitive data (CSRF token, session info)
2. User-controlled input reflected
3. HTTP compression enabled

Then attacker can extract secrets by measuring compressed response size!

When attacker adds known prefix to reflected data:
If prefix matches secret → compression is very efficient → smaller response
If prefix doesn't match → less compression → larger response
Binary search → recover full secret byte by byte

TEST FOR BREACH CONDITIONS:
curl -sI https://target.com | grep -i "content-encoding"
curl -s https://target.com | grep -i "csrf\|token" (does token appear in body?)
# If BOTH → potential BREACH risk
```

### 4. GZIP Bomb (Decompression DoS)

```
ATTACK: Upload/send tiny compressed file that decompresses to huge size
  1KB compressed → 1GB uncompressed

  Content-Encoding: gzip
  [42 bytes of gzip data that decompresses to 1TB]

TEST:
python3 -c "
import gzip, io
buf = io.BytesIO()
with gzip.GzipFile(fileobj=buf, mode='wb') as f:
    f.write(b'A' * 100_000_000)  # 100MB
print(f'Compressed size: {len(buf.getvalue())} bytes')
"

UPLOAD: as profile picture, attachment, etc.
If server decompresses before size-checking → DoS
```

---

## Hands-On: Transfer-Encoding Commands

```bash
# See if chunked encoding is used in response
curl -v https://target.com 2>&1 | grep -i "transfer-encoding\|chunked"

# Send chunked request manually
curl -X POST https://target.com/api/data \
  -H "Transfer-Encoding: chunked" \
  --data-binary $'4\r\ntest\r\n0\r\n\r\n'

# Test request smuggling detection (Burp Suite)
# Extensions: HTTP Request Smuggler (James Kettle / albinowax)
# Burp → Target → right-click → Extensions → HTTP Request Smuggler → Launch

# Measure response size with/without compression:
curl -s -o /dev/null -w "%{size_download}\n" https://target.com/
curl -s -o /dev/null -w "%{size_download}\n" --compressed https://target.com/
# Difference = how much data compression saves (if any)

# Detect BREACH conditions:
curl -s https://target.com | grep -c "csrf_token\|__token\|_token"
curl -sI https://target.com | grep -i content-encoding
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| TE/CL desync → request smuggling | Use HTTP/2 end-to-end, or same parser on F/E and B/E |
| BREACH | Disable compression for sensitive pages, or use random padding |
| Gzip bomb | Set max decompressed size limit before decompression |
| Chunked encoding WAF bypass | WAF must properly parse chunked encoding |

---

## Related Notes
- [[Module 09 - HTTP Request Smuggling]] — full smuggling attack guide
- [[03 - HTTP Versions]] — HTTP/2 avoids chunked issues
- [[04 - HTTP Request Structure]] — where headers appear
