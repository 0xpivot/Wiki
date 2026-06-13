---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.29 Connection — Hop-by-Hop Abuse"
---

# 03.29 — Connection

## What is it?

The `Connection` header controls whether the connection stays open (Keep-Alive) or closes after the response. It also lists hop-by-hop headers — headers that should be consumed by the next hop (proxy) and NOT forwarded to the origin server. Attackers can abuse hop-by-hop header behavior to strip security headers.

---

## Connection Values

```
Connection: keep-alive   → keep connection open for multiple requests
Connection: close        → close connection after this response
Connection: Upgrade      → protocol upgrade (WebSocket)
Connection: TE           → hop-by-hop: TE header
```

---

## Hop-by-Hop Header Abuse

```
RFC 2616 defines hop-by-hop headers that proxies must NOT forward:
  Connection, Keep-Alive, Proxy-Authorization, TE, Trailers,
  Transfer-Encoding, Upgrade

BUT: Connection header can list additional hop-by-hop headers:
  Connection: X-Custom-Security-Token, Authorization
  
  → Proxy strips X-Custom-Security-Token before forwarding!
  → Backend never sees the security token!

ATTACK:
  Request:
    Connection: X-Real-IP, Authorization
    X-Real-IP: 127.0.0.1
    Authorization: Bearer legit-token
  
  Proxy: "Connection says X-Real-IP and Authorization are hop-by-hop"
         → Strips them!
  
  Backend sees:
    (no X-Real-IP or Authorization)
    → Might default to anonymous access or localhost trust!
```

---

## Attack: Stripping Security Headers via Connection

```
PRACTICAL ATTACKS:
  
  1. Strip Authorization header:
     Connection: Authorization
     → Backend receives no auth header → might allow anonymous access!

  2. Strip custom API key header:
     Connection: X-API-Key
     → Backend gets no key → might have different behavior!
  
  3. Strip security context headers:
     Connection: X-User-ID, X-Role
     → Backend uses defaults → privilege escalation!
  
  NOTE: This depends on proxy actually processing Connection correctly.
  Not all proxies implement this spec behavior.
```

---

## Connection and Slowloris DoS

```
Slowloris keeps many connections open by sending partial HTTP requests:

  GET / HTTP/1.1
  Host: target.com
  Connection: keep-alive
  [send headers very slowly, never completing the request]
  
  Server holds connection open for each of hundreds of parallel sockets.
  → Exhausts server's max connection limit!
  → Legitimate users can't connect → DoS!
```

---

## Testing Hop-by-Hop Abuse

```bash
# Test if proxy strips headers listed in Connection
curl -H "Connection: X-Custom-Header" \
     -H "X-Custom-Header: value" \
     https://target.com/ -v
# Check if X-Custom-Header appears in backend (via error messages, reflection, etc.)

# Test stripping Authorization
curl -H "Connection: Authorization" \
     -H "Authorization: Bearer invalid" \
     https://target.com/protected
# 200 = proxy stripped auth, backend allowed!

# Test stripping security context
curl -H "Connection: X-User-Role" \
     -H "X-User-Role: user" \
     https://target.com/admin
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Hop-by-hop abuse strips auth | Proxies should not blindly strip headers listed in Connection |
| Slowloris DoS | Set timeout for incomplete requests; limit per-IP connections |
| Keep-alive pool exhaustion | Set max keep-alive requests and timeout |

---

## Related Notes
- [[28 - Upgrade]] — Connection: Upgrade for WebSocket
- [[20 - Transfer-Encoding]] — TE as hop-by-hop header
- [[Module 10 - HTTP Request Smuggling]] — hop-by-hop and smuggling interaction
