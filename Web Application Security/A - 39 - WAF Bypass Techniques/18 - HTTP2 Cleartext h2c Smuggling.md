---
tags: [waf, evasion, bypass, vapt]
difficulty: advanced
module: "39 - WAF Bypass Techniques"
topic: "39.18 HTTP2 Cleartext h2c Smuggling"
---

# HTTP/2 Cleartext (h2c) Smuggling

HTTP/2 Cleartext (h2c) Smuggling is a highly advanced and devastating technique used to bypass Web Application Firewalls (WAFs), API Gateways, and reverse proxies to access internal, highly restricted endpoints. It exploits the HTTP/1.1 to HTTP/2 upgrade mechanism, taking advantage of critical discrepancies in how front-end proxies and back-end servers handle the transition between communication protocols.

## The HTTP Upgrade Mechanism Explained

To fully understand h2c smuggling, we must first examine the standard HTTP `Upgrade` mechanism defined in RFC 7230. When a client wants to communicate using a different protocol (such as WebSockets or HTTP/2 Cleartext, known as `h2c`), it initiates an HTTP/1.1 request but includes specific headers requesting a protocol shift:

```http
GET / HTTP/1.1
Host: target.com
Connection: Upgrade, HTTP2-Settings
Upgrade: h2c
HTTP2-Settings: AAMAAABkAAQAAP__
```

If the backend server supports the requested upgraded protocol, it acknowledges the shift by returning a specific status code:

```http
HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: h2c

[... subsequent traffic on this TCP socket is now raw binary HTTP/2 frames ...]
```

## The Core Vulnerability: Reverse Proxy Blindness

The vulnerability arises when a WAF or reverse proxy acts as an intermediary but fails to properly manage, understand, or terminate the `Upgrade` connection.

Many WAFs are fundamentally configured to deeply inspect standard HTTP/1.1 plain-text traffic. When they encounter an `Upgrade` request, they evaluate the initial HTTP/1.1 headers. If the headers and the target path (e.g., `/`) appear benign, the WAF forwards the request to the backend server. 

Once the backend server responds with `101 Switching Protocols`, a persistent TCP tunnel is established directly between the client and the backend server, simply passing through the WAF. **Crucially, because the subsequent traffic is now binary HTTP/2 multiplexed frames, the HTTP/1.1-focused WAF is entirely blind to it.** It lacks the protocol awareness to parse the binary frames, so it defaults to acting as a dumb TCP pipe, forwarding bytes without inspection.

### ASCII Architecture of h2c Smuggling

```text
[ Attacker ]                                 [ WAF / Front-End Proxy ]                           [ Backend Server ]
     |                                              |                                               |
     |--- 1. HTTP/1.1 Upgrade: h2c Request -------->| (WAF inspects HTTP/1.1)                       |
     |       (Targeting benign /index.html)         | (Path allowed, forwarding)                    |
     |                                              |--- 2. Forwards Upgrade Request -------------->|
     |                                              |                                               |
     |                                              |<-- 3. 101 Switching Protocols ----------------|
     |<-- 4. 101 Switching Protocols ---------------|                                               |
     |                                              |                                               |
     |==============================================|===============================================|
     |           TCP Tunnel Established. WAF is now transparent and protocol-blind.                 |
     |==============================================|===============================================|
     |                                              |                                               |
     |--- 5. Binary HTTP/2 GET /admin/delete_db --->| ---> (WAF blind, passes frames) ------------->|
     |       (Malicious smuggled payload)           |                                               |
     |<-- 6. HTTP/2 200 OK (Action Executed) -------|<---- (WAF blind, passes frames) --------------|
```

## Step-by-Step Exploitation

The execution of an h2c smuggling attack requires precise manipulation of the connection state.

1. **The Setup Request:** The attacker crafts an HTTP/1.1 request targeting a public, harmless endpoint (e.g., `/public/style.css`) that the WAF is guaranteed to allow. They include the `Upgrade: h2c` headers.
2. **WAF Inspection & Bypass:** The WAF inspects the request. Because the path is benign and the headers do not trigger SQLi/XSS signatures, the WAF forwards the request.
3. **The Tunnel Establishment:** The backend server accepts the upgrade, returning `101 Switching Protocols`. The connection is now upgraded. The WAF stops applying HTTP/1.1 rules to the socket.
4. **The Smuggled HTTP/2 Frames:** The attacker immediately sends an HTTP/2 `MAGIC` connection preface (`PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n`), followed by HTTP/2 `HEADERS` and `DATA` frames. This new HTTP/2 request completely ignores the original path and instead targets a restricted, internal endpoint (e.g., `/api/internal/debug`).
5. **Execution:** Because the WAF is no longer parsing the stream, it blindly forwards the HTTP/2 frames. The backend server parses the HTTP/2 request and executes the privileged action, completely bypassing the WAF's access controls.

## Weaponization and Variations

### Connection Header Manipulation (RFC Violation Exploitation)

A key aspect of this attack relies on abusing the `Connection` header. RFC 7230 strictly states that hop-by-hop headers must be removed by proxies before forwarding a request.

If an attacker sends:
```http
Connection: Upgrade, HTTP2-Settings, X-Forwarded-For
```
A fully compliant proxy *should* strip `Upgrade` and `HTTP2-Settings` before passing the request to the backend. If it does, the backend never sees the upgrade request, and the attack fails. However, poorly configured proxies (or custom routing scripts) often blindly forward the `Upgrade` header, initiating the vulnerability.

### WebSocket Smuggling

The exact same architectural flaw applies to WebSockets. If a WAF allows upgrading to WebSockets but does not deeply inspect the subsequent WebSocket data frames, an attacker can establish a WebSocket connection to a backend component (like a custom WebSocket API, a Docker daemon, or a smuggled SSH session over WS). Once the `101` upgrade happens, the WAF is bypassed, and the attacker has a bidirectional, uninspected tunnel to the internal network.

## Detecting and Mitigating h2c Smuggling

Mitigating upgrade-based smuggling requires strict, uncompromising control over protocol transitions at the network edge.

1. **Disable h2c at the Edge and Proxy:** Unless explicitly and specifically required by a legacy internal application, do not allow HTTP/2 Cleartext (`h2c`) upgrades anywhere in the stack. If HTTP/2 is needed for performance, it must be implemented via ALPN (Application-Layer Protocol Negotiation) over TLS (`h2`), which is negotiated securely during the TLS handshake, entirely bypassing the vulnerable HTTP `Upgrade` header mechanism.
2. **Strict Header Stripping:** Ensure the reverse proxy (Nginx, HAProxy, Envoy) is configured to rigorously strip all hop-by-hop headers defined in the `Connection` header before forwarding the request to the backend. 
3. **Deep Packet Inspection (DPI) for Upgrades:** Modern WAFs must be capable of inspecting HTTP/2 and WebSocket traffic natively. If an upgrade occurs, the WAF must dynamically shift its parsing engine to the new protocol rather than dropping into a blind TCP pass-through mode. If it cannot inspect the upgraded protocol, it must drop the connection.
4. **Backend Hardening (Zero Trust):** Backend servers should be configured to reject `Upgrade: h2c` requests entirely if they are situated behind a reverse proxy that handles client communication. Internal service-to-service communication can use h2c, but it should not accept h2c upgrades originating from external ingress paths.

## Summary

HTTP/2 Cleartext Smuggling highlights the severe dangers of protocol complexity and intermediary desynchronization. By abusing the upgrade mechanism, attackers can create massive blind spots in WAF coverage, transforming a secure proxy into a dumb pipe, and gaining direct, unfiltered access to backend infrastructure.

### Chaining Opportunities
- Highly effective when chained with [[03 - HTTP Request Smuggling (CL.TE & TE.CL)]] to create complex, multi-layered desynchronization attacks across different proxies in the chain.
- Once the h2c tunnel is established, attackers can freely execute payload-heavy attacks like [[09 - SQL Injection WAF Bypass]] or [[11 - Command Injection Obfuscation]] without any interference or filtering from the WAF.

### Related Notes
- [[07 - Protocol Downgrade Attacks]]
- [[22 - WebSocket Security and WAF Blindspots]]
- [[25 - Backend Desynchronization Attacks]]
- [[27 - Advanced Proxy Evasion]]
