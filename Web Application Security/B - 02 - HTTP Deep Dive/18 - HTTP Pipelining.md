---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.18 HTTP Pipelining"
---

# 02.18 — HTTP Pipelining

## What is it?

**HTTP pipelining** allows a client to send multiple HTTP requests over the same TCP connection without waiting for each response. Responses are returned in the same order as requests. It was introduced in HTTP/1.1 to improve performance but is largely superseded by HTTP/2 multiplexing.

---

## Pipelining vs Sequential vs Multiplexed

```
SEQUENTIAL (HTTP/1.0 style):
  [Req1] → [Res1] → [Req2] → [Res2] → [Req3] → [Res3]
  Each request waits for previous response
  Slow: 3 round trips

PIPELINING (HTTP/1.1):
  [Req1][Req2][Req3] → [Res1][Res2][Res3]
  Send all requests immediately without waiting
  Server MUST respond in order (Head-of-Line blocking remains)
  If Res1 is slow → Res2 and Res3 must wait even if ready

MULTIPLEXING (HTTP/2):
  [Req1 Stream 1] [Req2 Stream 2] [Req3 Stream 3]
  [Res3 S3] [Res1 S1] [Res2 S2]    ← any order!
  True parallelism, no head-of-line blocking at HTTP level
```

---

## How Pipelining Works

```
TCP CONNECTION (single):
  Client → Server:
    GET /page1 HTTP/1.1\r\n
    Host: target.com\r\n
    \r\n
    GET /page2 HTTP/1.1\r\n
    Host: target.com\r\n
    \r\n
    GET /page3 HTTP/1.1\r\n
    Host: target.com\r\n
    \r\n

  Server → Client (in order):
    HTTP/1.1 200 OK [body1]
    HTTP/1.1 200 OK [body2]
    HTTP/1.1 200 OK [body3]
```

---

## Security Context — Pipelining in VAPT

### 1. Pipelining and Request Smuggling

HTTP pipelining creates a shared connection where multiple requests flow. This is one of the conditions that makes **request smuggling** possible — if a middle proxy interprets request boundaries differently from the back-end server.

```
PIPELINE:
  Frontend proxy receives:
    [Request A - length 100 bytes]
    [Request B - smuggled extra data]

  If front-end parses differently from back-end:
  Back-end sees:
    [Request A]
    [Smuggled prefix][Request B]

  The "smuggled prefix" gets prepended to the next victim's request!
  See: [[Module 09 - HTTP Request Smuggling]]
```

### 2. Timing Attacks via Pipelining

```
TECHNIQUE: Send multiple requests in a burst to reduce timing noise

NORMAL TIMING ATTACK:
  Send request → wait for response → measure time
  Network jitter adds noise to timing

PIPELINED TIMING:
  Send N identical requests in pipeline burst → N responses arrive
  Average timing across N responses → reduces jitter
  More accurate for time-based blind SQLi

Used in tools:
  sqlmap --technique=T (time-based)
  racetool for race conditions
```

### 3. Race Condition Exploitation via Pipelining

```
ATTACK SCENARIO: Exploit race condition in:
  - Coupon redemption (use once)
  - Like button (count once)
  - Inventory check before purchase
  - Rate limiting bypass

RACE CONDITION REQUIRES:
  Send N requests simultaneously to hit the window before state update

BURP SUITE - "LAST-BYTE SYNCHRONIZATION":
  1. Queue all N requests in Burp Repeater (group them)
  2. Send group "in parallel" 
  3. All requests hit server within microseconds of each other
  4. Server processes all before any completes

  Burp Suite Pro → "Send Group in Parallel (last-byte sync)" button
  This holds TCP connection until all requests are queued, then flushes all at once

MANUAL WITH CURL:
  Synchronized with shell pipeline (less precise):
  for i in {1..10}; do
    curl -s -X POST https://target.com/redeem -d "code=DISCOUNT10" &
  done; wait
```

### 4. HTTP Pipelining Enabled Detection

```bash
# Test if server supports pipelining (use netcat for raw pipelining):
(printf "GET / HTTP/1.1\r\nHost: target.com\r\n\r\nGET /about HTTP/1.1\r\nHost: target.com\r\n\r\n") | \
  nc target.com 80

# If server responds to both → pipelining supported

# Check if connection stays alive (required for pipelining):
curl -v https://target.com/ 2>&1 | grep -i "connection:"
# Connection: keep-alive → pipelining possible
# Connection: close → server closes after each request
```

---

## Hands-On: Race Condition with Pipelining

```bash
# Burp Suite method (most reliable for race conditions):
# 1. Intercept target request
# 2. Right-click → "Send to Repeater"
# 3. Right-click → "Send to Repeater" (9 more times = 10 total)
# 4. Select all tabs → right-click → "Send group in parallel (last-byte sync)"
# 5. All 10 requests sent simultaneously

# Python with threading (rough race):
import threading, requests

def redeem():
    r = requests.post('https://target.com/redeem', 
                      data={'code':'DISCOUNT'},
                      cookies={'session':'abc123'})
    print(r.status_code, r.text[:50])

threads = [threading.Thread(target=redeem) for _ in range(10)]
[t.start() for t in threads]
[t.join() for t in threads]

# turbo-intruder (Burp extension) — best for precise race conditions
# See PortSwigger Race Conditions labs
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Race conditions in business logic | Implement database-level locking (SELECT FOR UPDATE, unique constraints) |
| Request smuggling via pipelined connections | Use HTTP/2 end-to-end, strict Content-Length parsing |
| Pipelining amplifies timing attacks | Use constant-time comparison for secrets |

---

## Related Notes
- [[03 - HTTP Versions]] — pipelining in HTTP/1.1, multiplexing in HTTP/2
- [[19 - HTTP Keep-Alive and Connection Reuse]] — connection reuse enables pipelining
- [[Module 09 - HTTP Request Smuggling]] — pipelining vulnerability
- [[Module 19 - Race Conditions]] — race condition attacks
