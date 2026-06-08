---
tags: [vapt, csrf, beginner]
difficulty: beginner
module: "11 - CSRF"
topic: "11.02 Same-Origin Policy and CSRF"
---

# 11.02 — Same-Origin Policy and CSRF

## What is the Same-Origin Policy?

The Same-Origin Policy (SOP) is a browser security mechanism that restricts how documents/scripts from one origin can interact with resources from another origin.

```
ORIGIN = protocol + hostname + port
  https://target.com:443 → origin: {https, target.com, 443}
  http://target.com:80   → DIFFERENT origin (different protocol!)
  https://sub.target.com → DIFFERENT origin (different subdomain!)
  https://target.com:8080 → DIFFERENT origin (different port!)
  https://target.com/other/page → SAME origin!

SOP RULE:
  A page from origin A can READ data from origin B
  ONLY IF they have the same origin.
  
  A page from origin A CAN SEND REQUESTS to origin B
  (but can't read the response!)
```

---

## Why SOP Doesn't Prevent CSRF

```
SOP RESTRICTS READING RESPONSES
SOP DOES NOT RESTRICT SENDING REQUESTS!

WHAT SOP PREVENTS:
  evil.com → fetch('https://bank.com/account') → CAN'T read response
  → evil.com can't steal your account balance

WHAT SOP DOES NOT PREVENT:
  evil.com → form.submit() to bank.com → REQUEST IS SENT!
  Browser includes bank.com cookies automatically
  bank.com processes the request!
  evil.com just can't read the response (bank.com's confirmation page)
  
  But for CSRF, we don't NEED to read the response!
  We just need the action to execute!
```

---

## "Simple" vs "Complex" Requests

```
CORS DISTINGUISHES TWO TYPES:

SIMPLE REQUESTS (no preflight):
  Methods: GET, POST, HEAD
  Content-Types: text/plain, multipart/form-data, application/x-www-form-urlencoded
  No custom headers
  
  → These go straight through! No preflight CORS check!
  → HTML forms are "simple requests"
  → CSRF uses simple requests!

COMPLEX REQUESTS (require preflight):
  Methods: PUT, DELETE, PATCH
  Content-Type: application/json  ← NOT simple!
  Custom headers (like X-CSRF-Token)
  
  → Browser sends OPTIONS preflight first
  → Server must respond with CORS headers allowing it
  → CSRF can't bypass this... mostly (but see note 08!)
```

---

## Why HTML Forms Are Dangerous for CSRF

```
HTML FORM SUBMIT = SIMPLE REQUEST:
  <form action="https://bank.com/transfer" method="POST">
    <input name="amount" value="1000">
    <input name="to" value="ATTACKER">
  </form>
  
  This form submit:
  ✓ POST method → simple
  ✓ Content-Type: application/x-www-form-urlencoded → simple
  ✓ No custom headers → simple
  ✓ NO PREFLIGHT CORS CHECK!
  
  The bank.com server receives this and processes it.
  
WHAT STOPS IT?
  CSRF token: the form should include a secret token
  that evil.com can't know (SOP prevents reading the token page)
  
  SameSite cookie: modern browsers can restrict when cookies
  are sent cross-site
```

---

## Cross-Origin vs Cross-Site

```
SAME ORIGIN:  same protocol + host + port
SAME SITE:    same eTLD+1 (effective top-level domain + 1 label)

EXAMPLES:
  https://sub1.target.com and https://sub2.target.com
  → Different origin (different subdomain)
  → BUT: Same site (target.com is the eTLD+1)
  → SameSite=Strict/Lax cookies apply to BOTH!
  
  This matters for CSRF via subdomains:
  If evil.sub.target.com can be controlled by attacker
  → They're "same site" as target.com
  → SameSite cookies ARE sent in this case!
  → Subdomain takeover + CSRF = bypass!
```

---

## Cookie Behavior in Cross-Origin Requests

```
COOKIE BEHAVIOR:

Standard cookies (no SameSite):
  Sent in ALL cross-origin requests
  → Easy CSRF!

SameSite=None:
  Sent in all cross-origin requests (same as no SameSite)
  Must be: SameSite=None; Secure
  
SameSite=Lax:
  Sent for cross-site GET requests only (top-level navigation)
  NOT sent for POST, PUT, etc. forms from cross-site!
  → Protects against form-based CSRF!
  
SameSite=Strict:
  NEVER sent for cross-site requests
  → Maximum CSRF protection
  → But: even top-level GET navigation won't include cookie
     (e.g., clicking a link to bank.com from Google won't include cookie)
  → Less user-friendly
```

---

## The Evolution of CSRF Defense

```
2005-2015: CSRF tokens were the primary defense
2016: SameSite cookie attribute introduced
2021: Chrome made SameSite=Lax the DEFAULT (no SameSite = Lax)
2023+: Most modern apps are protected by default via SameSite=Lax

BUT STILL TESTABLE:
  ✓ Old cookies with SameSite=None
  ✓ GET-based CSRF (SameSite=Lax doesn't block top-level GET!)
  ✓ CSRF via SameSite bypass (subdomains, CORS misconfiguration)
  ✓ Broken CSRF token implementations
```

---

## Related Notes
- [[01 - What is CSRF]] — CSRF fundamentals
- [[06 - SameSite Cookie Bypass]] — bypassing SameSite protection
- [[07 - CSRF via CORS Misconfiguration]] — CORS + CSRF
- [[10 - Defense CSRF Tokens SameSite]] — defenses
