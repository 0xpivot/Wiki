---
tags: [vapt, http-headers, web, advanced]
difficulty: advanced
module: "03 - HTTP Headers"
topic: "03.30 TE (chunked) — HTTP/2 Downgrade Smuggling"
portswigger_labs: ["HTTP request smuggling — 22 labs"]
---

# 03.30 — TE (Trailers / HTTP/2 Chunked)

## What is it?

The `TE` (Transfer Encodings) request header advertises which transfer encodings the client accepts. Combined with HTTP/2 to HTTP/1.1 downgrade scenarios, it enables advanced request smuggling variants. `TE: trailers` is most common.

---

## TE Header Values

```
TE: trailers           → client accepts trailer headers
TE: deflate            → client accepts deflate encoding
TE: chunked            → client accepts chunked (always supported in HTTP/1.1)
TE: gzip, trailers     → multiple values

HTTP/2 NOTE:
  HTTP/2 doesn't use Transfer-Encoding (built into protocol).
  But if a request is downgraded H2→H1, TE headers become relevant.
```

---

## TE as Hop-by-Hop Header

```
Connection: TE      ← marks TE as hop-by-hop
TE: trailers

MEANING: Proxy should strip TE header before forwarding.
ATTACK: If proxy doesn't strip → backend sees TE → may process chunks differently!
```

---

## HTTP/2 TE Smuggling (H2.TE)

```
SCENARIO:
  Frontend: HTTP/2 (TLS)
  Backend: HTTP/1.1
  
  Frontend strips Transfer-Encoding from H2 requests (correct behavior).
  But attacker injects TE header in H2 request headers:
  
  H2 request (attacker sends):
    :method = POST
    :path = /
    :scheme = https
    :authority = target.com
    transfer-encoding: chunked   ← injected into H2 headers
    content-length: 0
  
  Proxy converts H2 to H1:
    POST / HTTP/1.1
    Transfer-Encoding: chunked   ← carried over!
    Content-Length: 0
  
  Backend sees both → CL.TE desync → smuggling!
```

---

## H2.CL Smuggling Variant

```
H2 request:
  :method = POST
  content-length: 200    ← injected CL
  [actual body is 5 bytes]

H2 protocol uses frame length (5 bytes), not Content-Length.
But when downgraded to H1:
  POST / HTTP/1.1
  Content-Length: 200    ← backend reads 200 bytes!
  
  [5 bytes of body + 195 bytes from next request in pipeline!]
  → Next request polluted with our 195 arbitrary bytes → smuggling!
```

---

## Testing H2 Smuggling

```bash
# Use Burp Suite for H2 smuggling (Repeater with HTTP/2 selected):
# 1. Select HTTP/2 in Repeater
# 2. Click Inspector → add request attribute: transfer-encoding: chunked
# 3. Send and observe backend behavior

# Burp HTTP Request Smuggler extension auto-detects H2 variants

# Manual detection (timing-based):
# Send with injected TE: chunked in H2
# If response is delayed → server is waiting for chunk completion → vulnerable!

# h2csmuggler tool:
pip3 install h2csmuggler
h2csmuggler --smuggle -x "https://target.com/"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| H2.TE downgrade smuggling | Strip/reject Transfer-Encoding in H2→H1 downgrade |
| H2.CL smuggling | Use HTTP/2 end-to-end (no H1 backend); validate Content-Length |
| TE hop-by-hop not stripped | Proxies must strip TE when forwarding |

---

## Related Notes
- [[20 - Transfer-Encoding]] — TE chunked in HTTP/1.1
- [[21 - Content-Length]] — CL.TE and TE.CL smuggling
- [[29 - Connection]] — TE as hop-by-hop header
- [[02.20 - HTTP2 Multiplexing HPACK]] — HTTP/2 internals
- [[Module 10 - HTTP Request Smuggling]] — full smuggling module
