---
tags: [vapt, csrf, intermediate]
difficulty: intermediate
module: "11 - CSRF"
topic: "11.06 SameSite Cookie Bypass"
portswigger_labs: ["SameSite Lax bypass via method override", "SameSite Strict bypass via client-side redirect", "SameSite Strict bypass via sibling domain", "SameSite Lax bypass via cookie refresh"]
---

# 11.06 — SameSite Cookie Bypass

## SameSite Cookie Quick Reference

```
SameSite attribute controls WHEN cookies are sent in cross-site requests:

SameSite=Strict:
  Cookie NEVER sent for cross-site requests
  Even clicking a link to the site from Google → no cookie!
  Strongest protection, but breaks some UX

SameSite=Lax:
  Cookie sent for TOP-LEVEL NAVIGATION only (clicking links)
  NOT sent for: cross-site form POSTs, iframes, images, fetch
  Default in Chrome since 2021 if no SameSite attribute set
  
SameSite=None:
  Cookie always sent cross-site
  Must also have Secure flag
  Same as old behavior before 2021

KEY INSIGHT FOR BYPASS:
  Even SameSite=Lax can be bypassed in several ways!
  And SameSite=Strict can be bypassed via client-side redirects!
```

---

## Bypass 1 — SameSite=Lax via GET Request

```
SameSite=Lax protects POST requests.
But if endpoint accepts GET → bypass!

SCENARIO:
  Set-Cookie: session=abc; SameSite=Lax
  
  Attacker page with link:
  <a href="https://target.com/delete-account?confirm=yes">Click me!</a>
  
  OR with auto-redirect:
  window.location = 'https://target.com/change-email?email=evil@evil.com';
  
  → This is "top-level navigation" → SameSite=Lax sends the cookie!
  → Request succeeds!
  
COMBINED WITH METHOD OVERRIDE:
  Some frameworks accept: POST /action?_method=GET
  Or: X-HTTP-Method-Override: GET header
  → If app treats it as GET → SameSite=Lax bypass!
```

---

## Bypass 2 — SameSite=Lax via Method Override (_method)

```
MANY FRAMEWORKS SUPPORT METHOD OVERRIDE:
  Ruby on Rails: ?_method=DELETE
  Laravel: ?_method=PUT
  
  The request is technically a POST (browser sends POST)
  but the framework treats it as DELETE/PUT
  
  SameSite=Lax: POST is blocked cross-site... 
  BUT: if you wait 120 seconds (Chrome's 2-minute rule)!

CHROME'S 2-MINUTE EXCEPTION:
  Chrome allows SameSite=Lax cookies on cross-site POST
  ONLY within 2 minutes of setting the cookie!
  (Designed for OAuth/SSO compatibility)
  
  This means: right after login (within 2 min) → Lax=POST allowed!
  
  PRACTICAL: Hard to exploit reliably, but important to know for edge cases.
```

---

## Bypass 3 — SameSite=Strict via Client-Side Redirect

```
SameSite=Strict: cookie is NOT sent even for top-level GET navigation
from external origin.

BUT: if you can reach the action via a SAME-SITE redirect!

SCENARIO:
  Target has open redirect on same site:
  https://target.com/redirect?url=/change-email?email=evil@evil.com
  
  Attack flow:
  1. Victim visits: https://evil.com/csrf.html
  2. evil.com does: window.location = 'https://target.com/redirect?url=...'
  3. Browser navigates to target.com (top-level navigation)
  4. SameSite=Strict: this came from evil.com → cookie NOT sent!
  5. BUT: target.com redirects to /change-email (SAME-SITE redirect!)
  6. Now the browser is on target.com → follows the redirect same-site!
  7. SameSite=Strict cookie IS sent for the same-site redirect!
  8. Action executes!

KEY INSIGHT:
  SameSite checks the ORIGINAL initiating origin, NOT the redirect chain!
  Once on target.com, internal redirects are same-site!
  
  Wait: some implementations DO check origin at each redirect hop.
  Test in practice!
```

---

## Bypass 4 — SameSite via Sibling Subdomain (Same-Site Attack)

```
REMEMBER: same-site = same eTLD+1

  sub1.target.com and sub2.target.com → SAME SITE!
  
  If attacker controls any subdomain of target.com:
    → They are "same site" as target.com
    → Requests from sub.attacker_controlled.target.com 
      include SameSite=Strict/Lax cookies!

HOW TO FIND:
  1. Look for subdomain takeover opportunities
     (dangling CNAMEs to cloud services, GitHub Pages, etc.)
  2. Find subdomains with XSS vulnerabilities
  3. Find subdomains with CORS misconfigurations

SCENARIO:
  uploads.target.com allows user-uploaded HTML files (XSS stored)
  → XSS on uploads.target.com = same site as target.com
  → From uploads.target.com, JS can make requests to target.com
  → SameSite cookies are sent!

COMBO ATTACK:
  uploads.target.com → XSS → fetch to target.com/admin/delete-user
  → SameSite=Strict/Lax cookies sent → action executes!
```

---

## Bypass 5 — SameSite None with Secure (Old Cookies)

```
IF: Cookie set with SameSite=None; Secure (or no SameSite)
THEN: No bypass needed! Just use regular CSRF attack!

Look for:
  Set-Cookie: session=abc; HttpOnly; Secure; SameSite=None
  
  → Cookie sent cross-site for ALL requests!
  → Classic CSRF attack works!

WHY THIS STILL EXISTS:
  ✓ Old sessions set before Chrome's 2021 default change
  ✓ APIs that explicitly set SameSite=None for cross-site auth
  ✓ Older browsers still in use
  ✓ Developer explicitly set SameSite=None
```

---

## Detecting SameSite Setting

```bash
# CHECK COOKIE SAMESITE IN BURP:
# Response → Set-Cookie header → look for SameSite=

# CHECK WITH CURL:
curl -I https://target.com/login

# EXAMPLE OUTPUT:
Set-Cookie: session=abc123; Path=/; HttpOnly; SameSite=Lax
                                               ↑ Note this!

# CHECK IN BROWSER DEV TOOLS:
# Application tab → Cookies → look at SameSite column

# IF NO SAMESITE:
# Chrome defaults to SameSite=Lax (since 2021)
# Firefox and Safari may differ

# TEST BYPASS:
# 1. Log in → get session cookie
# 2. In new tab: open attack page
# 3. Check: did action execute?
```

---

## Complete Bypass Decision Tree

```
START: Is CSRF protected by SameSite?
  
  NO SameSite (or None) → Use standard CSRF attack!
  
  SameSite=Lax?
    ├── Does endpoint accept GET? → GET-based CSRF works!
    ├── Can you do method override (_method)? → Try it!
    └── Can you exploit within 2 minutes of login? → POST CSRF!
  
  SameSite=Strict?
    ├── Is there an open redirect on target.com? → Client-side redirect bypass!
    ├── Is there XSS on any subdomain of target.com? → Same-site attack!
    ├── Is there a subdomain takeover? → Same-site attack!
    └── Nothing? → CSRF likely not exploitable via cookies alone
                   Consider CORS misconfig or token bypass instead
```

---

## Related Notes
- [[02 - Same-Origin Policy and CSRF]] — SOP and SameSite basics
- [[04 - CSRF via POST Request]] — form-based CSRF
- [[05 - CSRF Token Bypass Techniques]] — token bypass
- [[07 - CSRF via CORS Misconfiguration]] — CORS + CSRF
- [[10 - Defense CSRF Tokens SameSite]] — how SameSite protects
