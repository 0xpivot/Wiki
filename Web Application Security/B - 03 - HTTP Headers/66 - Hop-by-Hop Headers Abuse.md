---
tags: [vapt, http-headers, hop-by-hop, proxy, access-control-bypass, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.66 Hop-by-Hop Headers Abuse"
---

# 03.66 — Hop-by-Hop Headers Abuse

## What is it?
HTTP headers come in two flavours:
- **End-to-end headers** — meant to travel all the way from the client to the final server (and back). Proxies must forward them untouched.
- **Hop-by-hop headers** — meant only for a *single* connection between two adjacent nodes (client→proxy, or proxy→proxy). Each proxy is supposed to **consume and strip** them before forwarding.

Think of hop-by-hop headers like a baton in a relay race: it's passed from one runner to the next, but it should **never** cross the finish line. If a sloppy proxy forwards the baton to the final server anyway — or lets *you* decide which headers become batons — you can make security-relevant headers vanish or get mishandled mid-journey.

The standard hop-by-hop headers (RFC 2616 §13.5.1) are:
```text
Keep-Alive, Transfer-Encoding, TE, Connection,
Trailer, Upgrade, Proxy-Authorization, Proxy-Authenticate
```

The key trick: the **`Connection`** header lets you *nominate additional headers as hop-by-hop*. A compliant proxy will strip any header you list in `Connection` before forwarding. That is the attack primitive.

```http
Connection: close, X-Forwarded-For
```
→ tells the next hop "treat `X-Forwarded-For` as hop-by-hop and remove it."

## Why it matters (the attack primitive)
If you can make a proxy strip a header that the **back-end relies on for a security decision**, you change the request the back-end sees. Two classic outcomes: access-control bypass and cache poisoning.

## Attack 1 — Bypassing IP-based access controls
Many apps trust `X-Forwarded-For` (XFF) to know the "real" client IP, and some make authz decisions on it (e.g. "admin panel only from 10.0.0.0/8").

1. Attacker sends a request through the proxy with a header the back-end uses for trust.
2. Attacker adds:
   ```http
   Connection: close, X-Forwarded-For
   ```
3. A misconfigured proxy strips `X-Forwarded-For` before forwarding.
4. The back-end no longer sees the forwarded chain — it may now treat the request as coming **directly from the trusted proxy IP**, granting access it should not.

The inverse is also useful: strip a header that *would* have revealed your spoofing, so your injected value (or absence of one) is what the app evaluates.

## Attack 2 — Cache poisoning via hop-by-hop injection
If a cache keys or stores responses without accounting for stripped headers:

1. Attacker sends a request marking a sensitive header hop-by-hop, e.g.:
   ```http
   Connection: close, Cookie
   ```
2. The cache fails to strip it correctly and caches a response that was tailored to the attacker's session (or to the absence of the cookie).
3. Later users requesting the same resource get the **poisoned cached response** — potentially leaking session-specific content or serving attacker-influenced output.

## ASCII Diagram
```text
================================================================================
                ABUSING THE Connection HEADER TO STRIP XFF
================================================================================

  ATTACKER                    PROXY                       BACK-END
  --------                    -----                       --------
  GET /admin HTTP/1.1
  X-Forwarded-For: 1.2.3.4
  Connection: close, X-Forwarded-For
        |
        |---- request -------->|
        |                      | proxy reads Connection header:
        |                      | "X-Forwarded-For is hop-by-hop"
        |                      | => STRIPS X-Forwarded-For
        |                      |
        |                      |----- forwarded (no XFF) ----->|
        |                      |                               | "No XFF? Must be
        |                      |                               |  a direct/trusted
        |                      |                               |  request" => ALLOW
        |                      |<------------ 200 OK ----------|
        |<------ 200 OK -------|
================================================================================
```

## Hands-on testing
General method: send the request twice — once normally, once with the header nominated as hop-by-hop — and **diff the responses**.

1. Baseline:
   ```http
   GET /resource HTTP/1.1
   Host: target
   X-Forwarded-For: 127.0.0.1
   ```
2. Hop-by-hop variant:
   ```http
   GET /resource HTTP/1.1
   Host: target
   X-Forwarded-For: 127.0.0.1
   Connection: close, X-Forwarded-For
   ```
3. Compare status code, body, and reflected values. A difference means the proxy honoured your `Connection` nomination and stripped the header.
4. Repeat for other trust headers: `Authorization`, `Cookie`, `X-Real-IP`, `X-Original-URL`, custom auth headers.

Automation: tooling can fuzz many candidate headers as hop-by-hop and flag behavioural changes (response diffing).

## Defense
- **Proxies/load balancers must strip all standard hop-by-hop headers** and should ignore client-supplied `Connection` directives for security-relevant headers — never let a client decide that `Authorization`/`Cookie`/`X-Forwarded-For` is hop-by-hop.
- **Don't trust forwarded headers for authz** unless they're set by *your* infrastructure and the client-supplied versions are overwritten at the edge.
- **Cache:** include relevant headers in the cache key and never cache responses keyed on stripped/auth headers.
- Pin a known, controlled `X-Forwarded-For` handling policy (overwrite, don't append blindly).

## Related
- [[64 - Subresource-Integrity]] — another header-trust topic
- See **HTTP Request Smuggling** module — `Transfer-Encoding`/`Connection` overlap with desync attacks
