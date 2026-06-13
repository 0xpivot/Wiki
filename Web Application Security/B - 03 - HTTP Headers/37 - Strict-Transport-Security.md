---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.37 Strict-Transport-Security (HSTS) — HTTPS Enforcement"
---

# 03.37 — Strict-Transport-Security (HSTS)

## What is it?

HSTS tells the browser to ONLY communicate with the server over HTTPS — never HTTP. Once a browser receives HSTS, it refuses to connect via HTTP even if the user types `http://` in the URL bar. This prevents SSL stripping attacks and cookie interception on unencrypted connections.

---

## Header Format

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload

max-age=31536000     → 1 year; remember HTTPS-only for this long
includeSubDomains    → apply to ALL subdomains too (*.target.com)
preload              → include in browser's HSTS preload list (hardcoded!)

MINIMAL (weak):
  Strict-Transport-Security: max-age=300   → 5 minutes (testing only!)

RECOMMENDED:
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

---

## What HSTS Protects Against

```
WITHOUT HSTS (SSL Stripping Attack):
  User types: target.com (or clicks http:// link)
  MITM attacker intercepts:
    MITM ← HTTP → User
    MITM ← HTTPS → Server
  
  User thinks: site is HTTP (no lock icon)
  Attacker: sees ALL traffic in plaintext!
  
  Even if site redirects: http:// → https://
  MITM intercepts BEFORE redirect!

WITH HSTS:
  Browser has remembered: target.com = HTTPS only
  User types: target.com
  Browser: automatically upgrades to https://target.com
  No HTTP request ever made → MITM can't intercept!
```

---

## Attack: HSTS Bypass via New Subdomain

```
HSTS without includeSubDomains:
  Strict-Transport-Security: max-age=31536000
  (no includeSubDomains)

ATTACK:
  Target subdomain: api.target.com
  No HSTS for api.target.com → SSL stripping still possible there!
  
  Then use api.target.com to set cookies for .target.com:
  → Cookie on main domain over HTTP → intercepted!
```

---

## Attack: HSTS Bypass via First Visit (No Preload)

```
HSTS only kicks in AFTER first HTTPS visit.
First-time users with no HSTS cache are vulnerable!

SCENARIO:
  Victim never visited target.com before.
  MITM attacker intercepts their first HTTP request.
  → Full SSL strip of first visit!
  → HSTS header never received by victim!

MITIGATION: HSTS Preload list
  → Browser vendors hardcode domains as HTTPS-only
  → Even first visit is forced to HTTPS
  → Submit at hstspreload.org
```

---

## Attack: HSTS Deletion via Shared Computer

```
SCENARIO: Attacker has brief physical access to victim's computer.
  
  Delete HSTS cache:
  Chrome: chrome://net-internals/#hsts → Delete domain → type target.com
  Firefox: Browser cache clear
  
  → Next visit vulnerable to SSL stripping!
  
  (Impractical but worth knowing)
```

---

## Testing HSTS

```bash
# Check if HSTS is set
curl -sI https://target.com | grep -i "strict-transport-security"

# Check max-age (is it long enough? min 1 year = 31536000)
curl -sI https://target.com | grep -i sts | grep "max-age"

# Check if preloaded:
# https://hstspreload.org/?domain=target.com

# Test HTTP to HTTPS redirect (without HSTS, this is the only protection):
curl -sI http://target.com | grep -i location
# Location: https://target.com → redirect exists but HSTS is better!

# Check includeSubDomains:
curl -sI https://sub.target.com | grep -i sts
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No HSTS | Add HSTS with max-age ≥ 31536000 |
| No includeSubDomains | Add includeSubDomains |
| Not on preload list | Submit to hstspreload.org |
| HSTS on HTTP response | HSTS MUST only be on HTTPS responses (browsers ignore it on HTTP) |

**Quick fix (Nginx):**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

---

## Related Notes
- [[02.02 - HTTP vs HTTPS]] — SSL stripping attack detail
- [[47 - Set-Cookie flags]] — Secure flag pairs with HSTS
- [[Module 16 - TLS Attacks]] — TLS/SSL vulnerabilities
