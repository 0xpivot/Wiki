---
tags: [vapt, http, web, intermediate]
difficulty: intermediate
module: "02 - HTTP Deep Dive"
topic: "02.20 HTTP/2 — Multiplexing, HPACK, Server Push"
---

# 02.20 — HTTP/2 — Multiplexing, HPACK, Server Push

## What is it?

**HTTP/2** is the second major version of HTTP, introduced in 2015. It fundamentally changes how HTTP works under the hood while keeping the same HTTP semantics (methods, headers, status codes). Key features: binary framing, multiplexing, header compression (HPACK), and server push.

---

## HTTP/2 Binary Framing

```
HTTP/1.1: Text-based
  GET / HTTP/1.1\r\n
  Host: target.com\r\n
  \r\n

HTTP/2: Binary frames (not human-readable)
  ┌────────────────────────────────────┐
  │ Length (24 bits) | Type (8 bits)  │
  │ Flags (8 bits) | Reserved + Stream ID (31 bits) │
  ├────────────────────────────────────┤
  │             Payload                │
  └────────────────────────────────────┘

FRAME TYPES:
  DATA (0x0):        Request/response body data
  HEADERS (0x1):     Request/response headers
  PRIORITY (0x2):    Stream priority
  RST_STREAM (0x3):  Immediately terminate a stream
  SETTINGS (0x4):    Connection parameters
  PUSH_PROMISE (0x5): Server push notification
  PING (0x6):        Keepalive/RTT measurement
  GOAWAY (0x7):      Connection shutdown
  WINDOW_UPDATE (0x8): Flow control
  CONTINUATION (0x9): More headers
```

---

## Multiplexing — The Big Win

```
HTTP/1.1 HEAD-OF-LINE PROBLEM:
  Connection: [Req1][wait][Req2][wait][Req3]
  If Req1 is slow → Req2 and Req3 must wait!
  Workaround: browsers open 6 parallel TCP connections

HTTP/2 MULTIPLEXING:
  Single TCP connection, multiple streams:
  
  Stream 1: ──→ HEADERS (GET /)
               ←── DATA (response body chunk 1)
               ←── DATA (response body chunk 2)
  
  Stream 3: ──→ HEADERS (GET /style.css)
               ←── DATA (CSS content)           } All interleaved!
  
  Stream 5: ──→ HEADERS (GET /script.js)
               ←── DATA (JS content)
  
  All streams on ONE TCP connection.
  Streams don't block each other at HTTP/2 level.
```

---

## HPACK — Header Compression

```
PROBLEM: HTTP headers are repetitive across requests.
  Cookie: long_session_token_repeated_in_every_request

HPACK SOLUTION:
  Static table (61 predefined entries):
    :method: GET     → index 2
    :status: 200     → index 8
    content-type: application/json → index 31

  Dynamic table (built during session):
    New headers added → assigned index → referenced by index in future requests

  Huffman encoding:
    Common characters encoded as fewer bits

RESULT:
  First request: full headers sent
  Subsequent requests: only changed headers + indexes for unchanged ones
  85-95% header compression in practice!

SECURITY:
  CRIME attack targeted TLS compression of headers.
  HPACK is designed to be safe (different approach to CRIME).
```

---

## Server Push

```
TRADITIONAL (HTTP/1.1):
  Browser → GET index.html → receives HTML
  Browser parses HTML → GET style.css → GET script.js (two extra round trips)

HTTP/2 SERVER PUSH:
  Browser → GET index.html
  Server → PUSH style.css (even before browser asks!)
  Server → PUSH script.js (before browser asks!)
  Browser → receives all three simultaneously

HOW IT WORKS:
  Server sends PUSH_PROMISE frame first:
    "I'm about to send you style.css"
  Browser checks its cache:
    "I already have style.css" → CANCEL_PUSH
    "I don't have it" → accepts push
  Server sends DATA frames for pushed resource
```

---

## Security Context — HTTP/2 in VAPT

### 1. HTTP/2 Rapid Reset — CVE-2023-44487

```
October 2023 — largest DDoS attack in history (398 million req/sec)

HOW:
  HTTP/2 allows opening a stream (HEADERS) then immediately
  closing it (RST_STREAM) in a single round trip.
  
  Attacker sends:
  Stream 1: HEADERS → RST_STREAM (immediately!)
  Stream 3: HEADERS → RST_STREAM
  Stream 5: HEADERS → RST_STREAM
  ... millions per second ...
  
  Server must allocate resources for each stream open.
  RST_STREAM doesn't require waiting for server to respond.
  Server overwhelmed processing stream open+close cycles!

IMPACT: All HTTP/2 servers vulnerable (nginx, Apache, h2o, etc.)
FIX: Update server software; rate limit RST_STREAM per connection
```

### 2. HTTP/2-to-HTTP/1.1 Downgrade — Request Smuggling

```
Most web architectures:
  Client ──HTTP/2──→ Front-end proxy ──HTTP/1.1──→ Back-end

Front-end speaks HTTP/2, translates to HTTP/1.1 for back-end.

If translation is imperfect → REQUEST SMUGGLING:

H2.TE attack:
  Client sends HTTP/2 header:
    :method: POST
    :path: /
    transfer-encoding: chunked   ← HTTP/2 shouldn't have TE!
  
  Front-end strips Transfer-Encoding (it's HTTP/2 forbidden header)
  OR front-end doesn't strip it → back-end sees TE: chunked

  If F/E adds Content-Length AND B/E uses Transfer-Encoding:
  → Desync → smuggling!

H2.CL attack:
  HTTP/2 has no Content-Length (length is in frame)
  But attacker injects :method: POST with custom Content-Length value
  F/E adds Content-Length: X to HTTP/1.1 request
  B/E uses Content-Length: X but actual body length differs
  → Smuggling!

TOOL: HTTP Request Smuggler (Burp Extension by albinowax)
```

### 3. HTTP/2 Header Injection

```
HTTP/2 headers don't use CRLF (\r\n) as separator.
But when translated to HTTP/1.1, header values are inserted into text.

If attacker can inject CRLF into an HTTP/2 header value:
  :authority: target.com\r\nX-Injected-Header: evil

Front-end HTTP/2 accepts it (CRLF is just bytes in HTTP/2 headers)
Front-end translates to HTTP/1.1:
  Host: target.com
  X-Injected-Header: evil    ← injected! Host header is also split!

This can inject arbitrary HTTP/1.1 headers into back-end request!
```

### 4. HTTP/2 Cleartext (h2c) — Bypassing TLS Restrictions

```
h2c = HTTP/2 without TLS (cleartext, non-standard)

Some internal services accept h2c on port 80 or custom ports.
Proxies may be configured to forward h2c even when TLS is required for clients.

ATTACK (h2c smuggling):
1. Send HTTP/1.1 request with Upgrade: h2c to proxy
2. Proxy doesn't support h2c → ignores upgrade → proxies to backend
3. If backend supports h2c → negotiates HTTP/2 directly
4. Now you have a multiplexed connection to backend bypassing proxy!
5. Send arbitrary requests to backend on this direct channel!

TOOL:
h2csmuggler.py --target http://target.com/
```

---

## Hands-On: HTTP/2 Testing

```bash
# Test HTTP/2 support
curl -sv --http2 https://target.com/ 2>&1 | head -5
# * Using HTTP2, server supports multiplexing ← HTTP/2 works

# Test h2c (cleartext HTTP/2)
curl -sv --http2 http://target.com/ 2>&1 | head -5
curl --http2-prior-knowledge http://target.com:8080/

# Detect HTTP/2 via ALPN
echo | openssl s_client -connect target.com:443 -alpn h2 2>/dev/null | grep -i ALPN
# ALPN protocol: h2 → HTTP/2 supported

# HTTP/2 header injection test (Burp Suite with HTTP/2 support):
# In Burp Repeater, enable HTTP/2
# Add a header with CRLF in value: custom-header: value\r\nX-Injected: evil
# Send → check response

# Rapid reset PoC (educational):
python3 -c "
import h2.connection, h2.config, socket, ssl
# Not shown for brevity — use existing PoC tools for authorized testing
"

# h2c smuggling
# git clone https://github.com/BishopFox/h2csmuggler
python3 h2csmuggler.py -x https://target.com/ http://target.com/internal
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| HTTP/2 rapid reset DoS | Upgrade server software, rate limit RST_STREAM |
| H2-to-H1 request smuggling | Use HTTP/2 end-to-end, or strict H1 parsing on backend |
| HPACK header injection | Strip CRLF from HTTP/2 header values before HTTP/1.1 translation |
| h2c smuggling | Disable h2c support if not needed, validate Upgrade header |

---

## Related Notes
- [[03 - HTTP Versions]] — HTTP/2 in context of all versions
- [[21 - HTTP3 and QUIC]] — next version after HTTP/2
- [[Module 09 - HTTP Request Smuggling]] — H2 desync attacks
- [[18 - HTTP Pipelining]] — HTTP/1.1 pipelining comparison
