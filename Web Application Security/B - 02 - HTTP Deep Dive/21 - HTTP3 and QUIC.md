---
tags: [vapt, http, web, intermediate]
difficulty: intermediate
module: "02 - HTTP Deep Dive"
topic: "02.21 HTTP/3 and QUIC"
---

# 02.21 — HTTP/3 and QUIC

## What is it?

**HTTP/3** is the third major HTTP version, built on **QUIC** (Quick UDP Internet Connections) instead of TCP. QUIC is a transport protocol developed by Google and standardized by IETF that runs over UDP, providing built-in TLS 1.3, no head-of-line blocking, and faster connection establishment.

---

## Why QUIC? The TCP Problem

```
HTTP/2 SOLVED: Application-layer head-of-line blocking (multiplexing)
HTTP/2 DIDN'T SOLVE: Transport-layer head-of-line blocking

In HTTP/2 over TCP:
  Stream 1 | Stream 2 | Stream 3 — all share ONE TCP connection
  If ONE TCP packet is lost → TCP must retransmit → ALL streams stall!
  Because TCP delivers data IN ORDER — no stream can proceed until gap is filled.

QUIC SOLUTION:
  QUIC streams are independent at transport layer.
  Packet loss on Stream 1 → only Stream 1 stalls.
  Streams 2 and 3 continue!
```

---

## QUIC Architecture

```
TRADITIONAL TLS over TCP:        QUIC over UDP:
┌────────────────────┐          ┌────────────────────┐
│     HTTP/2         │          │     HTTP/3          │
├────────────────────┤          ├────────────────────┤
│     TLS 1.2/1.3    │          │     QUIC (includes │
├────────────────────┤          │     TLS 1.3)       │
│       TCP          │          ├────────────────────┤
├────────────────────┤          │       UDP          │
│       IP           │          ├────────────────────┤
└────────────────────┘          │       IP           │
                                └────────────────────┘

QUIC combines transport + crypto in one layer.
TLS 1.3 is MANDATORY — no unencrypted QUIC.
```

---

## Key QUIC Features

```
1. 0-RTT Connection Establishment:
   First connection: 1-RTT (vs 2-RTT for TCP + TLS)
   Resuming connection: 0-RTT (vs 1-RTT for TCP + TLS resume)
   
   BROWSER → SERVER:
   0-RTT: "I've connected before, here's my cached key + request" → data immediately
   No handshake needed for repeat connections!

2. Connection Migration:
   Client gets a Connection ID (not IP:port)
   If you move from WiFi to 4G (IP changes) → connection continues!
   Server uses Connection ID → still knows it's you
   
   Great for mobile apps — no reconnection needed on network switch.

3. Multiplexing at QUIC level:
   Like HTTP/2, but packet loss only affects ONE stream.

4. Built-in TLS 1.3:
   All QUIC traffic is encrypted.
   No unencrypted QUIC mode.
```

---

## Security Context — HTTP/3 in VAPT

### 1. Detecting HTTP/3 Support

```bash
# HTTP/3 uses UDP port 443
# Server advertises HTTP/3 via Alt-Svc header:
curl -sI https://target.com | grep -i alt-svc
# Alt-Svc: h3=":443"; ma=86400  ← HTTP/3 on UDP 443!
# Alt-Svc: h3-29=":443"         ← HTTP/3 draft version

# Test HTTP/3 connection
curl --http3 https://target.com/
# If curl is built with HTTP/3 support

# nmap UDP scan for QUIC:
nmap -sU -p 443 target.com
# 443/udp open → QUIC/HTTP3 potentially running
```

### 2. WAF Bypass via HTTP/3

```
Many WAFs only inspect TCP port 443 traffic.
HTTP/3 runs on UDP port 443 — different traffic path.

If WAF doesn't inspect UDP 443:
  Connect via HTTP/3 → bypass WAF!
  
  curl --http3 "https://target.com/?id=1' OR '1'='1"
  
  If WAF was blocking SQLi on HTTP/1.1/2 → HTTP/3 might bypass!

STATUS: Most modern WAFs now support QUIC inspection.
        But check for gaps, especially in older deployments.
```

### 3. 0-RTT Replay Attacks

```
0-RTT REPLAY VULNERABILITY:

In 0-RTT mode, client sends request BEFORE server acknowledges connection.
These "early data" packets can be captured and replayed by an attacker
who is positioned on the network (or captures packets).

RISK:
  Replaying a 0-RTT POST request → action executed TWICE
  GET requests in 0-RTT: generally safe (idempotent)
  POST/PUT/DELETE in 0-RTT: potential replay → double charge, double action

EXAMPLE:
  0-RTT request: POST /transfer?amount=100&to=bob
  Attacker captures this 0-RTT packet
  Attacker replays it → Bob gets $200!

DEFENSE:
  Server MUST NOT process non-idempotent actions from 0-RTT
  RFC 9001: "Applications MUST NOT use 0-RTT for non-idempotent requests"
  Google: 0-RTT limited to safe requests (GET only)
```

### 4. QUIC Connection ID Tracking

```
QUIC uses Connection IDs for connection tracking.
These are visible to network observers (unlike TCP where port changes break tracking).

PRIVACY IMPLICATION:
  Your QUIC Connection ID is visible even though data is encrypted.
  ISPs/adversaries can use Connection ID to track connections.
  
  QUIC spec requires rotating Connection IDs regularly to mitigate.
  
PENTEST NOTE:
  During traffic analysis, QUIC Connection IDs appear in UDP payloads.
  Helps identify QUIC connections in pcap analysis.
  QUIC header is partially visible (Initial packets, Connection ID).
```

### 5. HTTP/3 Header Injection

```
Same concerns as HTTP/2 header injection apply:
If QUIC/HTTP3 terminates at a proxy that translates to HTTP/1.1:
  CRLF injection in HTTP/3 header values → header injection in HTTP/1.1 backend

Also: HTTP/3 uses QPACK header compression (similar to HPACK).
QPACK side-channel attacks theoretically possible (similar to BREACH for HTTP/2).
```

---

## Hands-On: HTTP/3 Testing

```bash
# Install curl with HTTP/3 support (may need to build from source or use Docker):
docker run --rm -it ymuski/curl-http3 curl --http3 https://cloudflare.com/

# Check HTTP/3 support
curl -sI https://target.com | grep -i alt-svc

# Test HTTP/3 if curl supports it
curl -v --http3 https://target.com/ 2>&1 | head -10

# nmap for QUIC (UDP 443)
sudo nmap -sU -p 443 target.com

# Wireshark — capture QUIC traffic
sudo tshark -i eth0 -f "udp port 443" -Y quic

# QUIC connection analysis tools:
# quiche (cloudflare): https://github.com/cloudflare/quiche
# qvis: https://qvis.quictools.info/ (visualize QUIC connections)
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| 0-RTT replay attacks | Don't process non-idempotent requests from 0-RTT data |
| WAF bypass via HTTP/3 | Ensure WAF covers UDP 443 / QUIC traffic |
| QUIC header injection | Same fixes as HTTP/2 → validate and sanitize all headers |
| Unrotated Connection IDs | Implement Connection ID rotation per QUIC spec |

---

## Related Notes
- [[20 - HTTP2 Multiplexing HPACK Server Push]] — HTTP/2 predecessor
- [[17 - TLS SSL How HTTPS Works]] — TLS 1.3 integrated into QUIC
- [[Module 09 - HTTP Request Smuggling]] — H3 downgrade issues
- [[Module 36 - WAF Bypass]] — HTTP/3 WAF bypass
