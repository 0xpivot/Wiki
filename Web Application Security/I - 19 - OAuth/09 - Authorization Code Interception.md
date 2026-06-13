---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.09 Authorization Code Interception"
---

# 19.09 — Authorization Code Interception

## What Is Authorization Code Interception?

```
AUTHORIZATION CODE:
  Short-lived one-time credential issued by auth server
  Exchanged for access + refresh tokens
  
  PROBLEM:
  The code travels in the URL → redirect URL → browser URL bar
  
  If attacker can intercept code:
  → They can exchange it for tokens (if they also have client_secret)
  → With PKCE: still need code_verifier → harder but not impossible
  
CODE INTERCEPTION VECTORS:
  1. Referrer header leakage (code in URL → sent to 3rd party)
  2. Browser history (URL saved, someone accesses device)
  3. Log files (web server / proxy logs capture redirect URLs)
  4. Network interception (man-in-the-middle)
  5. Open redirect (covered in note 08)
  6. Malicious app on device (mobile: custom URI scheme hijacking)
```

---

## Vector 1: Referrer Header Leakage

```
SCENARIO:
  Auth server redirects:
  https://app.example.com/callback?code=SECRET_CODE&state=...
  
  The callback page loads resources from third-party domains:
  - Analytics: analytics.google.com
  - CDN: cdn.jquery.com
  - Images: images.third-party.com
  
  Browser sends:
  GET /some-resource HTTP/1.1
  Host: analytics.google.com
  Referer: https://app.example.com/callback?code=SECRET_CODE&state=...
  
  → Third-party gets the code in their logs!

HOW TO TEST:
  1. Complete OAuth flow in Burp
  2. Look at ALL requests made AFTER the callback URL
  3. Filter by Referer header containing "callback" or "code="
  4. Any Referer to external domains with code? → BUG!

ALSO: If callback page has JavaScript error:
  Error object sent to error tracking (Sentry, etc.)
  URL with code included in error context → exposed!
```

---

## Vector 2: Custom URI Scheme Hijacking (Mobile)

```
MOBILE APPS USE CUSTOM URI SCHEMES:
  Instead of: https://app.example.com/callback
  They use:   myapp://oauth/callback
  
  Android: Intent filters in AndroidManifest.xml
  iOS: URL schemes in Info.plist
  
ATTACK:
  Malicious app registers same custom scheme:
  myapp://oauth/callback
  
  Android: Multiple apps can register same scheme
  OS prompts user: "Which app to open?" — confusing!
  Or: malicious app gets priority
  
  Result: Malicious app receives:
  myapp://oauth/callback?code=SECRET_CODE
  
DETECTION:
  Look for custom URI scheme in OAuth apps
  Check if multiple apps can register same scheme on target OS
  Android especially vulnerable to this

FIX FOR MOBILE APPS:
  Use Android App Links / iOS Universal Links instead:
  → https-based URLs that only ONE verified app can handle
  → Requires domain ownership proof (/.well-known/assetlinks.json)
  → No scheme hijacking possible!
```

---

## Vector 3: Log File Exposure

```
WEB SERVER LOGS CAPTURE REDIRECT URLS:
  Access log example:
  192.168.1.1 - - [01/Jan/2024:12:00:01] 
  "GET /callback?code=SECRET_CODE&state=abc123 HTTP/1.1" 200 1234
  
  If logs accessible → codes exposed!
  
WHERE TO LOOK:
  /var/log/nginx/access.log
  /var/log/apache2/access.log
  CDN logs, proxy logs, load balancer logs
  Application performance monitoring tools
  
ALSO: Server-side redirect in callback:
  Callback handler should redirect to clean URL ASAP:
  /callback?code=X&state=Y → /dashboard (no code in URL!)
  
  → Limits window where code is in browser URL bar + referrer
  
TESTING:
  Check if app access logs are exposed anywhere
  Check if code persists in URL on callback page (not cleaned up)
```

---

## Vector 4: Browser History and Shared Computers

```
CODE APPEARS IN BROWSER URL BAR:
  During: https://app.example.com/callback?code=SECRET_CODE
  
  Saved to browser history!
  → Another user on shared computer → views browser history → code!
  
  But: codes are usually short-lived (minutes)
  → History-based theft requires quick action
  
  ALSO: Back button reveals callback URL with code
  
MITIGATION:
  Codes should be single-use (most implementations)
  Short expiry (recommended: < 10 minutes, often < 60 seconds)
  App should immediately consume code in server-side code exchange
  Never show code in UI or expose unnecessarily
```

---

## Testing for Code Interception Risks

```bash
# 1. CHECK REFERRER LEAKAGE:
# In Burp, after OAuth callback, filter proxy history:
# Look for: "Referer: https://app.example.com/callback?code="
# In any request to external domains

# 2. CHECK IF CODE PERSISTS IN URL:
# After callback, does the app clean up the URL?
# Click links on callback page → is code in Referer?

# 3. CHECK CODE EXPIRY:
# Save the callback URL, wait 10+ minutes
# Try using the code again → 400 = expired (good)
# → 200 or token issued = no expiry (bad)

# 4. CHECK SINGLE-USE:
# Use the callback URL (complete flow)
# Use the SAME callback URL again immediately
# → Should fail with "invalid_grant" (already used)
# → Still works? → Code reuse attack possible!

# 5. CHECK LOG EXPOSURE:
# Look for /.git/config, /server-status, /info.php
# Or any logs exposed via path traversal or IDOR

# 6. CHECK REFERRER POLICY ON CALLBACK PAGE:
curl -s -D - https://app.example.com/callback?code=TEST 2>&1 | grep -i referrer
# → Referrer-Policy: no-referrer OR strict-origin (good)
# → Absent → browser sends full Referer (bad)
```

---

## Fix

```
DEFENSES AGAINST CODE INTERCEPTION:

1. USE PKCE (even for confidential clients):
   → Even if code intercepted → useless without code_verifier

2. STRICT redirect_uri EXACT MATCH:
   → Prevents code being sent to attacker domain

3. SHORT CODE LIFETIME:
   → Recommend: 10 minutes maximum
   → After expiry → "invalid_grant" error

4. SINGLE-USE CODES:
   → Immediately invalidate after first use
   → Attempt to reuse → alert + reject

5. REFERRER POLICY ON CALLBACK PAGE:
   Referrer-Policy: no-referrer
   → Prevents code in Referer header to any third-party

6. CLEAN URL AFTER EXCHANGE:
   # After exchanging code, redirect to clean URL:
   # Python (Flask):
   @app.route('/callback')
   def callback():
       code = request.args.get('code')
       state = request.args.get('state')
       # ... validate state, exchange code ...
       session['user'] = user_data
       return redirect('/dashboard')  # ← clean URL, no code!

7. NO THIRD-PARTY RESOURCES ON CALLBACK PAGE:
   → If you MUST load analytics, do it AFTER redirect to clean URL

8. ANDROID: USE APP LINKS (HTTPS SCHEME):
   → Not custom URI schemes that can be hijacked
```

---

## Related Notes
- [[08 - Open Redirect in Redirect URI]] — one code interception method
- [[10 - Token Leakage via Referer Header]] — Referer leakage for tokens
- [[05 - PKCE — What It Protects Against]] — PKCE as defense
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
