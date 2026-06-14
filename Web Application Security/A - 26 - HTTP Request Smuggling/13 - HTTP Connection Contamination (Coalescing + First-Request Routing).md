---
tags: [vapt, request-smuggling, http2, http3, connection-coalescing, first-request-routing, advanced]
difficulty: advanced
module: "26 - HTTP Request Smuggling"
topic: "26.13 HTTP Connection Contamination"
---

# 26.13 — HTTP Connection Contamination (Coalescing + First-Request Routing)

## What is it?
A connection-level cousin of request smuggling. It exploits the collision between two browser/proxy behaviours:

- **HTTP connection coalescing** — to save handshakes, browsers **reuse one HTTP/2+ connection for different hostnames** when they share an **IP address** and a **common TLS certificate** (e.g. a wildcard `*.example.com`).
- **First-request routing** — some reverse proxies decide which back-end to route a connection to **based only on the first request**, then send everything else on that connection to the **same** back-end.

Put them together and requests for one host get **misrouted to another host's back-end** — no attacker-in-the-middle needed. If the wrong back-end is more vulnerable (e.g. an old WordPress), you've effectively dragged a secure host's request into an insecure processor.

Think of a shared shuttle bus (the connection) that picks its destination from whoever boards first. If `wordpress.example.com` boards first, every later passenger — including `secure.example.com` — gets dropped at the WordPress office, even though they wanted the secure building.

## Example
`wordpress.example.com` and `secure.example.com`:
- same reverse proxy, same IP, shared wildcard cert.
- browser coalesces them onto one connection.
- proxy routed that connection to the **WordPress** back-end on the first request.
- a request meant for `secure.example.com` is now processed by WordPress → its **XSS / vulns** apply to content served under the secure origin.

## Detecting coalescing
Use Chrome DevTools **Network** tab (watch connection reuse) or **Wireshark**. Trigger coalescing in JS:
```javascript
fetch("//sub1.hackxor.net/", { mode: "no-cors", credentials: "include" }).then(() => {
  fetch("//sub2.hackxor.net/", { mode: "no-cors", credentials: "include" })
})
```
If the second request reuses the first connection (no new TLS handshake), the hosts coalesced.

## ASCII Diagram
```text
================================================================================
              CONNECTION COALESCING + FIRST-REQUEST ROUTING
================================================================================

  Browser (shared IP + wildcard cert *.example.com)
        |  ONE coalesced HTTP/2 connection
        v
  [Reverse proxy] -- routes by FIRST request -->
        | first request was for wordpress.example.com
        v
  [WordPress back-end]  <-- now ALSO receives:
        ^                     request for secure.example.com
        |                     (misrouted!)
        +-- vulnerable processor applied to the "secure" origin => XSS etc.
================================================================================
```

## Why HTTP/3 widens it
Today the threat is limited — first-request routing is uncommon and HTTP/2 still requires an **IP match** to coalesce. **HTTP/3 relaxes the IP-address match requirement**, so any servers sharing a wildcard certificate could coalesce more freely — broadening the attack surface **without** needing MITM.

## Hands-on workflow
1. Find sibling subdomains behind one proxy sharing an IP + wildcard cert.
2. Confirm coalescing (DevTools/Wireshark + the fetch snippet).
3. Test whether the proxy uses first-request routing: prime the connection with host A, then send a host-B request on it and see which back-end answers (differential response/headers).
4. If misrouted, port the weaker back-end's bugs (XSS, etc.) onto the stronger origin.

## Defense
- **Avoid first-request routing** in reverse proxies — route every request by its own `:authority`/`Host`, not the connection's first request.
- Be **cautious with wildcard TLS certificates**; scope certs per host where feasible, especially with HTTP/3.
- Test sibling hosts for coalescing behaviour regularly.

## Related
- [[01 - What is HTTP Request Smuggling?]] — the broader desync family
- [[05 - HTTP_2 Request Smuggling (H2.CL, H2.TE)]] — HTTP/2 downgrade smuggling
- [[07 - Smuggling to Bypass Front-End Controls]] — same goal (reach a back-end out of context)
