---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.14 Load Balancers"
---

# 01.14 — Load Balancers

## What is it?

A **load balancer** distributes incoming network traffic across multiple backend servers to ensure no single server is overwhelmed. It improves availability, reliability, and scalability.

**Analogy:** A load balancer is like a restaurant host who assigns arriving customers to available tables — spreading the load evenly so no single waiter is overwhelmed.

---

## How a Load Balancer Works

```
                   ┌─── Backend Server 1 (192.168.1.10)
Client ──→ [LB] ───┼─── Backend Server 2 (192.168.1.11)
                   └─── Backend Server 3 (192.168.1.12)

Client only sees the load balancer's IP/hostname.
Backend servers are hidden behind the LB.

LOAD BALANCING ALGORITHMS:
─────────────────────────────────────────────────────
Round Robin    : Request 1 → Server 1, 2 → Server 2, 3 → Server 3, 4 → Server 1...
Least Connections: Send to server with fewest active connections
IP Hash        : Same client IP always goes to same server (session persistence)
Weighted       : Server 1 gets 50% traffic, Server 2/3 get 25% each
Random         : Random server each request
```

---

## Layer 4 vs Layer 7 Load Balancers

```
LAYER 4 (Transport Layer) — TCP/UDP Level
─────────────────────────────────────────
Routes based on IP + port only.
Cannot inspect HTTP content.
Very fast, low latency.
Examples: AWS NLB, HAProxy (TCP mode)

LAYER 7 (Application Layer) — HTTP Level
─────────────────────────────────────────
Routes based on HTTP headers, path, cookies, host.
Can do:
  - Path-based routing: /api/ → API servers, /static/ → CDN
  - Host-based routing: api.target.com → API cluster
  - Cookie-based sticky sessions
  - SSL termination
Examples: AWS ALB, Nginx, HAProxy (HTTP mode), Cloudflare
```

---

## Session Persistence (Sticky Sessions)

```
Problem: User logs in on Server 1. Next request goes to Server 2.
         Server 2 has no session — user is logged out!

Solution: Sticky Sessions — always send same user to same server.

HOW:
1. Cookie-based: LB sets a cookie (e.g., AWSALB=abc123)
   → Client sends cookie → LB routes to same backend

2. IP Hash: Client IP always maps to same server

3. JWT/Stateless sessions: No stickiness needed — session
   is in the token, not on the server

Sticky sessions for VAPT: if you find the LB cookie, you can
manually set it to force routing to a specific backend.
```

---

## Security Context — Load Balancers in VAPT

### 1. Detecting Load Balancers

```bash
# lbd — Load Balancing Detector
lbd target.com

# Send repeated requests and watch for:
# - Different response headers
# - Different Server: values
# - Different cookies (AWSALB, PHPSESSID format changes)

curl -s -D - https://target.com | grep -i server
# Server: nginx/1.18.0     ← one backend
# Make request again:
# Server: nginx/1.14.0     ← different backend version!

# ELB (AWS) header tells you it's behind ALB:
# Server: awselb/2.0
# X-Amzn-Trace-Id: Root=1-abc-xyz

# Shodan can reveal load balancer type from historical data
```

### 2. Load Balancer Bypass — Reach Backend Directly

If you can find the IP of a backend server directly, you might bypass the LB (and its WAF/security rules):

```bash
# Enumerate backend IPs:
# - Historical DNS records (SecurityTrails, PassiveDNS)
# - SSL certificate SANs: openssl s_client -connect target:443
# - Shodan: find the backend IPs that respond to the same content
# - Error messages that leak internal IPs

# Access backend directly by IP:
curl -H "Host: target.com" http://192.168.1.10/
# ↑ Set Host header so backend knows which site you want

# If backend accepts requests without valid SNI (no LB):
curl --insecure https://192.168.1.10/admin
```

### 3. Session Persistence Abuse

```bash
# If sticky sessions use a cookie:
# AWSALB=xxx tells you which backend you're on
# Modify AWSALB to test routing to different backends

# Some backends may have different vulnerabilities:
# - Backend 1: patched
# - Backend 2: not patched (stale deployment)
# → Force routing to Backend 2 for exploit

# PHP session ID may encode backend ID:
# PHPSESSID=backend2_abc123 → try PHPSESSID=backend1_abc123
```

### 4. Race Conditions via Load Balancer

```
If app stores state on backend server (not shared DB):

Request 1 → Backend 1 (updates balance to $0 after withdrawal)
Request 2 → Backend 2 (still has old balance $100 → allows withdrawal again!)

This is a race condition amplified by load balancing.
Send simultaneous requests and hope they hit different backends.
```

### 5. HTTP Request Smuggling Through Load Balancer

Load balancers that rewrite headers or handle connection pooling can be vulnerable to request smuggling.

```
Load Balancer → Backend has different HTTP parsing behavior
→ Poison shared connection pool
→ Requests meant for other users get misdirected

See [[Module 09 - HTTP Request Smuggling]] for full details.
```

### 6. Health Check Endpoints — Information Disclosure

Load balancers probe backend health endpoints:

```bash
# Common health check paths (often unprotected):
curl https://target.com/health
curl https://target.com/healthz
curl https://target.com/ping
curl https://target.com/status
curl https://target.com/actuator/health   ← Spring Boot!
curl https://target.com/actuator/env      ← Spring Boot env vars!
curl https://target.com/metrics
curl https://target.com/api/health

# Spring Boot Actuator at /actuator/env can expose:
# - Database credentials
# - API keys
# - Internal URLs
# - Environment variables
```

---

## Hands-On: Load Balancer Commands

```bash
# lbd (Load Balancing Detector)
lbd target.com

# Repeated requests to detect LB
for i in {1..10}; do curl -s -I https://target.com | grep -i server; done

# Check for AWS ALB cookies
curl -c cookies.txt https://target.com
cat cookies.txt | grep -i awsalb

# ffuf to discover health endpoints
ffuf -u https://target.com/FUZZ \
     -w /usr/share/seclists/Discovery/Web-Content/common.txt \
     -mc 200 -fc 404
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Backend servers accessible directly | Firewall backends — only allow traffic from LB |
| Health endpoints leaking info | Protect health endpoints with auth or IP restriction |
| Sticky sessions expose backend routing | Use shared session store (Redis), not server-local |
| Different backend versions (patch lag) | Ensure all backends are on same version at all times |
| LB headers reveal internal info | Strip internal headers before response |

---

## Related Notes
- [[13 - Proxies Forward and Reverse]] — proxies and LBs overlap
- [[15 - CDNs Content Delivery Networks]] — CDN is a distributed LB
- [[Module 09 - HTTP Request Smuggling]] — LB introduces desync
- [[Module 10 - Web Cache Poisoning]] — LB + cache interactions
