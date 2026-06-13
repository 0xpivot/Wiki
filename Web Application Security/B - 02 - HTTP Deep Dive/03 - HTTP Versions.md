---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.03 HTTP Versions (1.0, 1.1, 2, 3)"
---

# 02.03 — HTTP Versions (1.0, 1.1, 2, 3)

## What is it?

HTTP has evolved through several versions, each adding features to handle the modern web's demands. As a pentester, knowing the version matters because each has different behaviors, vulnerabilities, and security implications.

---

## HTTP/1.0 (1996)

```
CHARACTERISTICS:
- One request per TCP connection
- Connection closed after each response
- No Host header (one IP = one website)
- No persistent connections

PROBLEM:
  Browser loads page with 100 resources (images, CSS, JS):
  → 100 separate TCP connections needed!
  → 100 TCP handshakes → very slow

SECURITY RELEVANCE:
- HTTP/1.0 still accepted by many servers
- No Host header: useful in some virtual host attacks
- Manually specify with curl: curl --http1.0 http://target.com
```

---

## HTTP/1.1 (1997 — most common legacy)

```
KEY IMPROVEMENTS:
  Persistent connections (Keep-Alive): reuse TCP connection for multiple requests
  Host header REQUIRED: one IP can host many domains (virtual hosting)
  Chunked transfer encoding: stream response without knowing size upfront
  Pipelining: send multiple requests without waiting for each response
  More cache control headers (Cache-Control, ETag)

EXAMPLE REQUEST (HTTP/1.1):
GET /index.html HTTP/1.1
Host: example.com           ← REQUIRED in 1.1
Connection: keep-alive
User-Agent: curl/7.81

EXAMPLE RESPONSE:
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234
Connection: keep-alive      ← reuse this TCP connection!

[HTML body]

SECURITY ISSUES IN HTTP/1.1:
- Head-of-Line Blocking: requests processed in order → slow
- HTTP Request Smuggling: ambiguous parsing of Content-Length vs Transfer-Encoding
- Verbose headers reveal server information
```

---

## HTTP/2 (2015)

```
KEY IMPROVEMENTS OVER 1.1:
  Binary framing: not text-based like 1.0/1.1 → harder to read raw
  Multiplexing: multiple requests/responses interleaved on ONE TCP connection
  Header compression (HPACK): reduces overhead
  Server Push: server can preemptively send resources before client requests
  Stream prioritization: browser says which resources matter most

ARCHITECTURE:
HTTP/1.1:        HTTP/2:
                        Stream 1: ─── GET /style.css ───
TCP ─ [Req1] ─   TCP ─ Stream 2: ─── GET /script.js ──
      [Res1] ─         Stream 3: ─── GET /image.png ──
      [Req2] ─         ← ALL INTERLEAVED on one TCP connection
      [Res2] ─
      [Req3] ─
      [Res3] ─

SECURITY ISSUES IN HTTP/2:
- HTTP/2 to HTTP/1.1 downgrade proxy → request smuggling possible
- HTTP/2 rapid reset attack (CVE-2023-44487): send many RST_STREAM → DoS
- Server Push can be abused to cache poison
- HPACK compression side-channel (CRIME-like attacks, BREACH variant)
```

---

## HTTP/3 (2022)

```
KEY IMPROVEMENT:
  Runs over QUIC (not TCP!) — UDP-based transport protocol
  Built-in TLS 1.3
  No Head-of-Line blocking (packet loss on one stream doesn't block others)
  0-RTT connection establishment (faster reconnects)
  Connection migration (IP change doesn't break connection — mobile networks)

HTTP/2 HEAD-OF-LINE PROBLEM:
  Multiple streams on ONE TCP → single packet loss blocks ALL streams
  (TCP must deliver in order)

HTTP/3 QUIC SOLUTION:
  Each stream is independent at the QUIC layer
  Packet loss on Stream 1 only blocks Stream 1, not others

SECURITY IMPLICATIONS:
- Runs on UDP (port 443 for QUIC)
- Firewalls/WAFs must handle UDP port 443
- Some WAFs don't inspect HTTP/3 → potential bypass
- 0-RTT replays: requests in 0-RTT can be replayed → dangerous for non-idempotent actions
```

---

## Detecting HTTP Versions

```bash
# Check what version server supports
curl --http1.0 -I http://target.com   # force HTTP/1.0
curl --http1.1 -I http://target.com   # force HTTP/1.1
curl --http2 -I https://target.com    # force HTTP/2
curl --http3 -I https://target.com    # force HTTP/3

# See protocol in response (verbose):
curl -v --http2 https://target.com 2>&1 | head -5
# * Using HTTP2, server supports multiplexing

# Nmap HTTP version detection
nmap -sV -p 80,443 target

# h2c (HTTP/2 over cleartext — no TLS):
# Some internal services use http2 without TLS!
curl --http2 http://internal-target:8080/
curl --http2-prior-knowledge http://internal-target:8080/  # skip upgrade negotiation
```

---

## Security Context — HTTP Versions in VAPT

### 1. HTTP Request Smuggling — HTTP/1.1 vs HTTP/2

The most critical version-related vulnerability. When a front-end uses HTTP/2 and back-end uses HTTP/1.1 (or different HTTP/1.1 parsing), you can smuggle requests.

```
ATTACK FLOW:
Browser → [HTTP/2 Frontend] → [HTTP/1.1 Backend]
                ↑
         Frontend translates HTTP/2 to HTTP/1.1
         If translation is ambiguous → request smuggling!

Detailed coverage: [[Module 09 - HTTP Request Smuggling]]
```

### 2. HTTP/2 Rapid Reset — CVE-2023-44487

```
October 2023 — largest DDoS in history (398 million rps)

ATTACK:
Client opens HTTP/2 connection
Client sends HEADERS frame (opens new stream)
Client IMMEDIATELY sends RST_STREAM (cancels it)
Repeat millions of times per second
Server must process each stream open+close → CPU exhausted

DETECTION:
  Sudden traffic spike to 443/UDP (if HTTP/3) or 443/TCP
  High RST_STREAM rate in HTTP/2 metrics

FIX:
  Update nginx/apache/haproxy/load balancer to patched version
  Rate limit new streams per connection
```

### 3. HTTP/1.0 Bypass for Access Controls

```bash
# Some servers/WAFs behave differently for HTTP/1.0 vs 1.1
# Try HTTP/1.0 to bypass IP-based or host-based restrictions:
curl --http1.0 -H "Host: admin.internal" http://target.com/admin
# No Host header validation in old HTTP/1.0 — sometimes bypasses ACLs

# HTTP/1.0 doesn't require Host header:
printf "GET /admin HTTP/1.0\r\n\r\n" | nc target.com 80
```

### 4. CRIME/BREACH — HTTP Compression Attacks

```
If HTTPS + HTTP body/header compression enabled:
  Attacker can infer secrets by observing response length differences
  Works when: attacker can inject chosen text into request
              AND observe the encrypted response length

  CRIME: TLS compression → disabled in modern TLS
  BREACH: HTTP body compression (gzip) → still exists!

  BREACH requires: secret in response body + reflection of user input

DETECTION:
  curl -I https://target.com | grep -i "Content-Encoding"
  If "gzip" and app reflects user input with secrets → test for BREACH
```

---

## Hands-On: HTTP Version Testing

```bash
# Detect HTTP/2 support
curl -sI --http2 https://target.com | head -3
# HTTP/2 200  ← server speaks HTTP/2

# List protocols advertised via ALPN (in TLS handshake)
echo | openssl s_client -connect target.com:443 -alpn h2 2>/dev/null | grep -i ALPN
# ALPN protocol: h2  ← HTTP/2 supported

# Detect HTTP/3 (QUIC)
# Check Alt-Svc header for h3:
curl -sI https://target.com | grep -i alt-svc
# Alt-Svc: h3=":443"; ma=86400  ← HTTP/3 available on port 443

# Test h2c (HTTP/2 cleartext — internal apps):
curl --http2-prior-knowledge http://internal-app:8080/
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| HTTP/2 rapid reset attack | Upgrade to patched server version, rate limit RST_STREAM |
| HTTP/2-to-HTTP/1.1 downgrade smuggling | Use consistent protocol end-to-end, or HTTP/2 throughout |
| BREACH attack | Disable HTTP compression for sensitive pages, or use CSRF tokens that rotate |
| HTTP/1.0 access control bypass | Require Host header, update to HTTP/1.1+ only |

---

## Related Notes
- [[01 - What is HTTP]] — HTTP fundamentals
- [[04 - HTTP Request Structure]] — request anatomy
- [[Module 09 - HTTP Request Smuggling]] — HTTP version desync attacks
- [[Module 10 - Web Cache Poisoning]] — caching in different HTTP versions
