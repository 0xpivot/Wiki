---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.59 Cross-Origin-Resource-Policy (CORP)"
---

# 03.59 — Cross-Origin-Resource-Policy (CORP)

## What is it?

`Cross-Origin-Resource-Policy` (CORP) is a response header that controls which origins can load the resource. Unlike CORS (which controls what JavaScript can read), CORP controls whether the browser can even load the resource at all (images, scripts, fonts, etc.) from cross-origin pages.

---

## Values

```
Cross-Origin-Resource-Policy: same-site      → only same-site can load this resource
Cross-Origin-Resource-Policy: same-origin    → only exact same origin
Cross-Origin-Resource-Policy: cross-origin   → any origin can load (public resource)
```

---

## Why It Matters

```
WITHOUT CORP:
  A malicious page can load your private API responses as images:
  <img src="https://target.com/api/user/secret-avatar">
  
  Browser loads it → might leak info via timing (if image loads = secret exists)
  
  WITH COEP: require-corp on main page:
  → Resources WITHOUT CORP header are BLOCKED from loading!
  → All resources must opt in to cross-origin loading!

SPECTRE ATTACK:
  Even without reading response → speculative execution + timing
  → Can read memory contents of loaded resource!
  → CORP + COEP together prevent this!
```

---

## Attack: Pixelated Side-Channel (CORP missing)

```
SCENARIO: Private user avatar at https://target.com/avatar/user_1234.png
          No CORP header.

ATTACK:
  <img src="https://target.com/avatar/user_1234.png"
       onload="exists()"
       onerror="notexists()">
  
  → Attacker can tell if user 1234's avatar exists → user exists!
  → Scale this to enumerate all user IDs!
  
  WITH timing attacks (Spectre):
  → Even the image CONTENT might be readable!
```

---

## CORP Required by COEP

```
IF main page sets COEP: require-corp:
  → Every cross-origin sub-resource MUST have CORP: cross-origin!
  → Or it's blocked!

ATTACK SCENARIO (app breaks when fixing COEP):
  COEP blocks CDN resources that don't set CORP!
  → Developer disables COEP to "fix" the issue
  → Security regression!
  → Educate: all third-party resources need CORP: cross-origin!
```

---

## Testing

```bash
# Check if resources have CORP:
curl -sI https://target.com/static/image.png | grep -i "cross-origin-resource-policy"

# Check if API responses have CORP:
curl -sI https://target.com/api/user/1 | grep -i "corp"

# Missing on sensitive resources → privacy leak potential
# Missing on API → COEP incompatible (can't enable cross-origin isolation)
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Private resources lack CORP | Add `CORP: same-origin` to private resources |
| Public CDN resources lack CORP | Add `CORP: cross-origin` to public resources |
| COEP requires all resources to have CORP | Audit all third-party resources |

---

## Related Notes
- [[57 - Cross-Origin-Embedder-Policy]] — COEP requires resources to have CORP
- [[58 - Cross-Origin-Opener-Policy]] — COOP (cross-origin isolation partner)
- [[41 - Access-Control-Allow-Origin]] — CORS (different: controls JS reads, not loads)
