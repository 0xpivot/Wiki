---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.19 HTTP Keep-Alive and Connection Reuse"
---

# 02.19 — HTTP Keep-Alive and Connection Reuse

## What is it?

**HTTP Keep-Alive** (persistent connections) allows a single TCP connection to be reused for multiple HTTP requests instead of opening a new TCP connection for each request. This dramatically improves performance and reduces latency.

---

## Without vs With Keep-Alive

```
WITHOUT KEEP-ALIVE (HTTP/1.0):
  [TCP Connect] → [HTTP Req 1] → [HTTP Res 1] → [TCP Close]
  [TCP Connect] → [HTTP Req 2] → [HTTP Res 2] → [TCP Close]
  [TCP Connect] → [HTTP Req 3] → [HTTP Res 3] → [TCP Close]
  3 TCP handshakes for 3 requests = slow!

WITH KEEP-ALIVE (HTTP/1.1 default):
  [TCP Connect] → [HTTP Req 1] → [HTTP Res 1]
                → [HTTP Req 2] → [HTTP Res 2]
                → [HTTP Req 3] → [HTTP Res 3] → [TCP Close]
  1 TCP handshake for 3 requests = fast!
```

---

## Keep-Alive Headers

```
REQUEST:
  Connection: keep-alive    ← client requests persistent connection

RESPONSE:
  Connection: keep-alive    ← server agrees
  Keep-Alive: timeout=5, max=100
             ↑ seconds until connection closes
                     ↑ max requests on this connection

CLOSE CONNECTION:
  Connection: close         ← either side can request closure after this response

HTTP/1.1 DEFAULT: Keep-alive unless Connection: close specified
HTTP/1.0 DEFAULT: Close unless Connection: keep-alive specified
HTTP/2: Always multiplexed — "keep-alive" concept built-in
```

---

## Security Context — Keep-Alive in VAPT

### 1. Request Smuggling via Persistent Connections

```
Keep-alive connections create a "pipeline" where multiple requests share
a single TCP connection. This is the foundation of HTTP Request Smuggling.

When a front-end proxy and back-end server share a persistent connection:
  All traffic from multiple users may share ONE backend connection
  Poisoning the connection → affects other users' requests!

For full details → [[Module 09 - HTTP Request Smuggling]]
```

### 2. Session Reuse in Keep-Alive Connections

```
Some middleware or CGI implementations incorrectly reuse state
across requests on the same keep-alive connection.

Bug example (old Apache mod_php):
  Request 1: GET /app?user=alice (authenticated)
  Response 1: alice's data
  
  [SAME TCP CONNECTION]
  
  Request 2: GET /app?user=bob (unauthenticated)
  Response 2: BOB sees ALICE'S data! (session leaked across keep-alive!)
  
This is rare in modern apps but documented in legacy CGI.
```

### 3. Slowloris — DoS via Keep-Alive Exhaustion

```
ATTACK:
1. Open many partial HTTP connections
2. Each connection sends keep-alive headers slowly
3. Server keeps connections open (waiting for rest of request)
4. Server connection pool exhausted → legitimate users can't connect

HOW IT WORKS:
  GET / HTTP/1.1\r\n
  Host: target.com\r\n
  X-a: b\r\n                ← sending headers very slowly (1 per 15 sec)
  X-b: c\r\n
  [never send the final \r\n to complete request]
  
  Server waits... and waits... and waits...

TOOL:
  slowloris.py target.com -p 80 -s 500  ← open 500 slow connections

DETECTION:
  Many connections in PARTIAL state (SYN-ACK but no data)
  netstat -an | grep :80 | grep ESTABLISHED | wc -l  ← unusually high

DEFENSE:
  - Set low keep-alive timeout
  - Limit connections per IP
  - nginx handles this well by design (event-driven, not thread-per-connection)
  - Load balancer timeout settings
```

### 4. Connection Pool Poisoning

```
When back-end connection pools are shared (as in Node.js, Python, etc.):
  Multiple requests reuse back-end TCP connections from a pool

If Request Smuggling is possible:
  Attacker's smuggled payload sits in back-end pipeline
  Next user's request is "combined" with attacker's payload
  User gets wrong response / attacker gets user's data
  
Connection pool = multiplies the damage of smuggling
See [[Module 09 - HTTP Request Smuggling]] for exploitation
```

---

## Hands-On: Keep-Alive Testing

```bash
# Check if server uses keep-alive
curl -v https://target.com/ 2>&1 | grep -i "connection\|keep-alive"
# Connection: keep-alive → persistent
# Connection: close → not persistent

# Test multiple requests on same connection (curl does this automatically):
curl -v --keepalive-time 5 \
  https://target.com/page1 \
  https://target.com/page2 \
  https://target.com/page3 2>&1 | grep "Reusing connection"
# "Reusing existing connection" → keep-alive working

# See active connections
ss -tn state ESTABLISHED dport = :443
# Many connections to same server = connection pooling

# Slowloris test (authorized only):
pip install slowloris
slowloris target.com -p 80 --sleeptime 10 -s 50
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Slowloris DoS | Set low keep-alive timeout, limit connections per IP |
| Connection pool poisoning | Fix request smuggling vulnerability (see Module 09) |
| State leakage across connections | Use stateless design, reset state after each request |

---

## Related Notes
- [[18 - HTTP Pipelining]] — pipelining on persistent connections
- [[Module 09 - HTTP Request Smuggling]] — exploiting shared connections
- [[Module 19 - Race Conditions]] — timing attacks on pooled connections
