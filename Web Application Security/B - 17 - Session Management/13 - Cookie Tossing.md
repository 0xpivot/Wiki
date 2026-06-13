---
tags: [vapt, session-management, cookies, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.13 Cookie Tossing"
---

# 17.13 — Cookie Tossing

## What Is Cookie Tossing?

```
COOKIE TOSSING:
  Attack where a subdomain "tosses" (injects) a cookie
  into the parent domain's cookie jar, interfering with the main app
  
PREREQUISITE:
  Attacker must be able to set cookies for a parent domain
  This requires control of a subdomain (subdomain takeover or XSS on subdomain)
  
MECHANISM:
  Subdomain: evil.example.com
  Sets: Set-Cookie: session=EVIL; Domain=.example.com
  → Browser now has EVIL "session" cookie for .example.com
  → When user visits example.com → browser sends EVIL session
  → App might use EVIL session instead of legitimate one!
```

---

## Cookie Tossing Attack Scenarios

### Scenario 1: Session Fixation via Tossing

```
1. Attacker controls: static.example.com (compromised/taken over)
2. Victim visits static.example.com (for a static asset)
3. Attacker's server responds:
   Set-Cookie: session=ATTACKER_KNOWN_SESSION; Domain=.example.com
   
4. Victim's browser now has: session=ATTACKER_KNOWN_SESSION for .example.com
5. Victim visits secure.example.com → login
6. App creates new session → but sends Set-Cookie: session=NEW_SESSION
7. Browser now has BOTH cookies!
   Which one does it send? The browser may send BOTH, or the wrong one!
   
8. If app uses the "first" session cookie → ATTACKER_KNOWN_SESSION!
9. Attacker uses their known session → logs into victim's account!
```

### Scenario 2: CSRF Token Poisoning

```
Main app: app.example.com
CSRF token in cookie: csrf_token=LEGITIMATE

1. Attacker controls: static.example.com
2. Static subdomain sets: Set-Cookie: csrf_token=EVIL; Domain=.example.com
3. Browser now has TWO csrf_token cookies!
4. Browser may send: csrf_token=LEGITIMATE; csrf_token=EVIL (both!)
5. App validates CSRF: is EVIL in the list? Maybe yes!
6. → CSRF protection bypassed!

OR: If app takes the "last" cookie value and EVIL is newer → EVIL wins
→ App gets fake CSRF token → attacker can force actions via CSRF!
```

### Scenario 3: CSRF Token Reading

```
Some apps store CSRF token in a non-HttpOnly cookie
Attacker's subdomain reads it (if not HttpOnly!):
  document.cookie → "csrf_token=SECRET_VALUE"

But: Cross-origin, different subdomain...
→ WAIT: If victim visits the attacker's subdomain page that has JS:
  var csrf = document.cookie  → reads .example.com cookies!
  (Since the attacker's subdomain is *.example.com → shares cookie namespace)

→ Attacker exfiltrates the CSRF token!
→ Performs CSRF attack with real token
```

---

## Browser Cookie Priority

```
WHEN BROWSER SENDS MULTIPLE COOKIES WITH SAME NAME:
  Browser sends ALL matching cookies
  HTTP spec doesn't define order clearly
  
  In practice: cookies are ordered by specificity
  More specific path first, then by age (newest first)
  
  Example:
  Cookie: session=LEGITIMATE_VALUE; session=EVIL_VALUE
  
  Which one does the server use?
  → Depends on server-side parsing! Usually FIRST one!
  → PHP, Express: use first occurrence
  → Some frameworks: use last occurrence
  → Inconsistent! → can be exploited!
```

---

## Testing Cookie Tossing

```
STEP 1: Find if any subdomain is vulnerable:
  Check all subdomains for XSS, takeover potential
  (See Module 12 - CORS Subdomain Trust for finding vulnerable subdomains)

STEP 2: Simulate cookie injection:
  If you can set cookies via any means (XSS, response header injection):
  Set: csrf_token=FAKE on .example.com
  
  Visit main app → do they accept FAKE as the CSRF token?

STEP 3: Test with duplicate cookies:
  In Burp → add duplicate Cookie headers:
  Cookie: session=REAL; session=FAKE
  OR (HTTP/1.1 allows multiple values):
  Cookie: session=FAKE; session=REAL
  
  See which one the server uses!

MANUAL TEST IN BROWSER:
  DevTools → Application → Cookies → Add new cookie manually
  Set: name=session, value=FAKE, domain=.example.com
  → Does the app now use FAKE?
```

---

## Fix

```
DEFENSES:
  ✓ Use cookie prefixes to limit scope:
    
    __Host- prefix:
    Set-Cookie: __Host-session=X; Secure; Path=/; HttpOnly
    Rules enforced by browser:
    → Must have Secure flag
    → Must have Path=/
    → Must NOT have Domain attribute
    → Must come from HTTPS
    → Subdomains CANNOT override __Host- cookies!
    
    __Secure- prefix:
    Set-Cookie: __Secure-session=X; Secure; HttpOnly
    Rules:
    → Must have Secure flag
    → Must come from HTTPS
    → Stricter than default but less strict than __Host-
    
  ✓ Use cookie prefixes for ALL sensitive cookies:
    __Host-session=...
    __Host-csrf_token=...
    → Prevents subdomain tossing!
    
  ✓ Validate CSRF token server-side (not just cookie):
    Compare: cookie token == form/header token
    (Attacker who can toss cookie can toss both → defense in depth needed)
    
  ✓ Minimize attack surface: fix subdomain takeover issues
```

---

## Related Notes
- [[12 - Cookie Scope Abuse Domain and Path]] — Domain attribute scope
- [[Module 12 CORS - Subdomain Trust]] — finding subdomain vulnerabilities
- [[Module 11 - CSRF]] — CSRF token bypass via tossing
