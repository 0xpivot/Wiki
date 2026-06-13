---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.11 MFA Bypass — Response Manipulation"
portswigger_labs: ["2FA bypass using a brute-force attack", "2FA simple bypass"]
---

# 16.11 — MFA Bypass: Response Manipulation

## How MFA Works (and Where It Can Break)

```
TYPICAL 2-FACTOR AUTH FLOW:
  1. User submits username + password → AUTHENTICATED (first factor)
  2. Server sends OTP to phone/email
  3. User submits OTP → FULLY LOGGED IN (second factor)
  4. Server sets session cookie with full privileges
  
WHERE BYPASSES HAPPEN:
  - Step 1 → Step 3: Skip the OTP entirely (direct navigation)
  - Step 3: Manipulate the server's response on wrong OTP
  - Step 3: Brute force the OTP (weak OTP + no rate limit)
  - Step 1 → Step 3: Steal session cookie from step 1 (partial session)
```

---

## Bypass 1: Direct URL Navigation (Skip 2FA)

```
MOST COMMON BYPASS:

After first-factor login (correct password):
  Normal flow: GET /mfa-verify → submit OTP → GET /dashboard

Try SKIPPING:
  After password accepted → immediately navigate to:
  GET /dashboard
  GET /account
  GET /api/profile

Why it works:
  App created a "partial" session after first factor
  Doesn't check if MFA was completed before serving /dashboard
  → If server doesn't verify MFA completion → bypass!

HOW TO TEST:
  1. Login with valid credentials → you're on /mfa-verify page
  2. In Burp, forward the response but then change URL
  3. Navigate directly to /dashboard
  4. Or: open new browser tab → visit /dashboard
  5. → If you see dashboard content → 2FA bypassed!
```

---

## Bypass 2: Response Manipulation

```
CONCEPT:
  After submitting WRONG OTP, server returns:
  HTTP 200 {"success": false, "mfa_valid": false, "redirect": "/mfa-verify"}
  
  After submitting CORRECT OTP, server returns:
  HTTP 200 {"success": true, "mfa_valid": true, "redirect": "/dashboard"}
  
  BYPASS: Intercept the failed response → change "false" to "true"!
  
HOW TO TEST IN BURP:
  1. Set Burp to intercept responses (Proxy → Options → Intercept responses)
  2. Submit wrong OTP
  3. Intercept the response
  4. Change: "mfa_valid":false → "mfa_valid":true
             "success":false → "success":true
             HTTP 401 → HTTP 200
             "verified": 0 → "verified": 1
  5. Forward modified response → do you get in?
  
BURP MATCH AND REPLACE (for automation):
  Proxy → Options → Match and Replace
  Match: "mfa_valid":false
  Replace: "mfa_valid":true
```

---

## Bypass 3: Status Code Manipulation

```
IF THE APP USES HTTP STATUS CODE TO DETERMINE SUCCESS:
  Wrong OTP: HTTP 401 Unauthorized
  Right OTP: HTTP 200 OK → redirect to dashboard
  
BYPASS:
  Intercept wrong OTP response
  Change 401 → 200
  If client-side JavaScript checks the status code → success!
  
  Also try:
  - 403 → 200
  - 400 → 302 (redirect)
  
WHEN THIS WORKS:
  Client-side JavaScript code like:
  if (response.status === 200) { window.location = '/dashboard'; }
  → Changing status code in Burp fools the client-side check!
```

---

## Bypass 4: Cookie Value Manipulation

```
SOME APPS SET A COOKIE AFTER FIRST FACTOR:
  POST /login → Set-Cookie: auth=step1complete
  POST /mfa → Set-Cookie: auth=fullaccess
  
OR:
  POST /login → Set-Cookie: mfa_required=true
  POST /mfa  → Set-Cookie: mfa_required=false
  
BYPASS:
  After first-factor login, manually edit the cookie:
  mfa_required=true → mfa_required=false
  auth=step1complete → auth=fullaccess
  
  Burp → Proxy → Cookie Jar
  Or: Developer Tools → Application → Cookies → Edit value
  
  If server trusts cookie value without server-side verification → bypass!
```

---

## Bypass 5: Reusing OTPs (Code Reuse)

```
TIME-BASED OTP (TOTP — like Google Authenticator):
  30-second window → code changes every 30 seconds
  
  IF CODE IS NOT INVALIDATED AFTER FIRST USE:
  Alice uses OTP "123456" to login
  Old OTP "123456" is still valid for 30 seconds
  → Another session could use the same OTP!
  
  TEST: Use OTP → immediately try same OTP in second browser tab
  → If second tab also succeeds → OTP not invalidated after use!
  
  Also test: Is the previous OTP (from 30s ago) still accepted?
  → Some implementations allow T-1 and T windows for clock skew
```

---

## Fix

```
DEFENSES:
  ✓ Server-side MFA completion flag (not cookie-based):
    Store mfa_completed in server-side session, not in cookie
    
  ✓ Validate before EVERY request to protected endpoints:
    Not just on the MFA page itself
    if not session.mfa_completed: redirect to /mfa
    
  ✓ Don't use response content to determine MFA outcome:
    The auth decision should be server-side, not in the HTTP body
    
  ✓ Invalidate OTP immediately after use:
    Mark TOTP code as used for that 30s window
    
  ✓ Separate "partial session" from full session:
    After step 1: session has a "pre-mfa" flag
    After step 2: session upgrades to full auth
    Pre-MFA session cannot access protected resources
```

---

## Related Notes
- [[12 - MFA Bypass Code Reuse]] — OTP reuse in depth
- [[13 - MFA Bypass Brute Force OTP]] — brute force the 6-digit code
- [[14 - MFA Bypass Backup Code Abuse]] — alternative bypass path
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
