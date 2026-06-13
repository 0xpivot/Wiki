---
tags: [vapt, session-management, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.03 Session Fixation"
---

# 17.03 — Session Fixation

## What Is Session Fixation?

```
NORMAL FLOW:
  Victim visits site → server creates session ID X for anonymous user
  Victim logs in → server REPLACES session X with NEW session Y
  Attacker doesn't know session Y → can't hijack!
  
SESSION FIXATION ATTACK:
  1. Attacker visits site → gets session ID: abc123
  2. Attacker tricks victim into using the SAME session ID:
     Send link: https://target.com/login?session_id=abc123
     OR: CSS injection to set cookie
     OR: HTTP response splitting to set cookie
  3. Victim visits the link → server assigns session abc123 to victim!
  4. Victim logs in → server keeps session ID abc123 (doesn't regenerate!)
  5. Attacker uses abc123 in their browser → THEY ARE LOGGED IN AS VICTIM!
  
THE KEY MISTAKE:
  Server doesn't generate a NEW session ID after successful login!
```

---

## Attack Methods to "Fix" the Session

```
METHOD 1: URL PARAMETER
  Many older apps accept session ID via URL:
  https://target.com/?PHPSESSID=ATTACKER_KNOWN_SESSION
  
  Attacker sends this URL to victim:
  "Click here to view our special offer!"
  
  Victim visits → browser now has session PHPSESSID=ATTACKER_KNOWN_SESSION
  Victim logs in → session ID unchanged → attacker hijacks!

METHOD 2: COOKIE INJECTION VIA SUBDOMAIN
  If app is at app.example.com
  Attacker compromises subdomain static.example.com
  Injects header from subdomain:
  Set-Cookie: session=abc123; Domain=.example.com
  → Cookie set for ALL of *.example.com!
  → Victim visits app.example.com → their session = abc123

METHOD 3: SELF-XSS / HTML INJECTION
  If attacker can inject HTML (not full XSS):
  <meta http-equiv="Set-Cookie" content="session=abc123">
  → In some browsers, this sets the cookie!
```

---

## Testing for Session Fixation

```
STEP 1: Get a fresh session before login:
  Visit the site as anonymous user
  Note your session ID: PHPSESSID=test_value_from_before_login
  
STEP 2: Log in with a test account

STEP 3: Check session ID after login:
  If session ID = same as before login → SESSION FIXATION VULNERABILITY!
  If session ID changed → correctly regenerated → no vulnerability

EXAMPLE (browser DevTools):
  Before login: Cookie: session=aaaa1111bbbb2222
  After login:  Cookie: session=cccc3333dddd4444  ← different = GOOD!
  After login:  Cookie: session=aaaa1111bbbb2222  ← same = VULNERABLE!

BURP TEST:
  Intercept the POST /login request
  Note the session cookie in the request
  Observe the session cookie in the response
  Compare: same value = fixation possible
```

---

## Exploiting Session Fixation

```
STEP 1: Create your own session on target.com (just visit it):
  GET https://target.com/
  Response: Set-Cookie: session=KNOWN_SESSION_123
  
STEP 2: Craft a URL that sets the session:
  If app accepts session via URL:
  https://target.com/login?session=KNOWN_SESSION_123
  
  OR: If app accepts session in POST body:
  Create a form that auto-submits with the session value
  
STEP 3: Send to victim:
  "Click this to access your account"
  
STEP 4: Wait for victim to log in (or: victim was already logged in and you're waiting)

STEP 5: Use KNOWN_SESSION_123 in your own browser:
  DevTools → Application → Cookies → add session=KNOWN_SESSION_123
  Visit https://target.com/account
  → You are now logged in as victim!
```

---

## Fix

```
THE FIX: REGENERATE SESSION ID ON LOGIN!

PHP:
  session_regenerate_id(true);  // ← call this immediately after successful login!
  // true = delete old session

Python (Django):
  request.session.cycle_key()  # ← Django's built-in session rotation

Python (Flask + Flask-Login):
  flask_login does NOT automatically regenerate
  Manual: session.clear() → session['user_id'] = user.id
  OR use flask-paranoid extension

Node.js (express-session):
  req.session.regenerate(callback)  // ← call after successful login!

Rails:
  reset_session  # ← call after successful auth

REQUIREMENT:
  ✓ New session ID generated on every successful authentication
  ✓ Old session ID destroyed immediately
  ✓ Also regenerate on privilege escalation (gaining admin role)
```

---

## Related Notes
- [[02 - Session Token Entropy and Predictability]] — making tokens unpredictable
- [[04 - Session Hijacking via Cookie Theft XSS]] — stealing existing sessions
- [[11 - Cookie Flags Attack Scenarios]] — cookie attributes that limit fixation
- [[15 - Defense Secure Session Configuration]] — full hardening
