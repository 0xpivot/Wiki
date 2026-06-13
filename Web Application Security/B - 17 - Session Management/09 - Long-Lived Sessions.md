---
tags: [vapt, session-management, beginner]
difficulty: beginner
module: "17 - Session Management"
topic: "17.09 Long-Lived Sessions"
---

# 17.09 — Long-Lived Sessions

## The Risk of Never-Expiring Sessions

```
PROBLEM:
  If session never expires → stolen session is useful forever!
  
  Attacker steals session token today
  Uses it 6 months later → still works!
  
  Also:
  User forgets to logout on shared computer
  Session lives forever → next user has access indefinitely
  
SESSION LIFETIME CONCEPTS:
  Idle timeout:    Session expires after N minutes of inactivity
  Absolute timeout: Session expires after N hours regardless of activity
  
  BOTH should be applied!
  
  Without idle timeout:   Stolen session + attacker keeps it alive = forever
  Without absolute timeout: Active attacker keeps refreshing → stays in forever
```

---

## Testing for Long-Lived Sessions

```
TEST 1: IDLE TIMEOUT
  1. Log in
  2. Do NOT make any requests for 30+ minutes
  3. Try to access a protected page
  → If still authenticated → no idle timeout!

TEST 2: ABSOLUTE TIMEOUT
  1. Log in
  2. Keep using the app actively (every few minutes)
  3. After 8+ hours: try to access protected page
  → If still authenticated → no absolute timeout!

TEST 3: REMEMBER ME TOKEN
  1. Log in with "Remember Me" checked
  2. Note the persistent cookie (usually longer-lived than session cookie)
  3. Close and reopen browser (session cookies cleared, persistent cookies kept)
  4. How long does the persistent cookie work?
  → If it works for 30+ days → is that appropriate for the sensitivity?

TEST 4: CHECK COOKIE EXPIRY:
  DevTools → Application → Cookies
  Look at "Expires / Max-Age" column
  
  "Session" = expires when browser closes (OK for non-persistent)
  "2025-01-15T10:00:00" = 1 year from now (check if appropriate!)
  
  Burp: look at Set-Cookie header in login response:
  Set-Cookie: session=X; Max-Age=31536000  ← 1 year! Is that appropriate?
  Set-Cookie: session=X; Max-Age=1800      ← 30 min! More appropriate for banking
```

---

## Remember Me Functionality

```
"REMEMBER ME" INCREASES RISK:
  Normal session: lives in browser session storage → gone on browser close
  Remember Me: lives in persistent cookie → survives browser restarts
  
  Risk factors:
  - Longer token lifetime → more time for attacker to use stolen token
  - Persists on disk → shared computers, disk theft, malware
  
TESTING REMEMBER ME TOKEN:
  1. Login with Remember Me
  2. Note the long-lived cookie: remember_token=xyz
  3. What happens on password change?
     → Is remember_token invalidated? (should be!)
  4. What is the expiry?
     → 30 days? 90 days? 1 year? Never?
  
VULNERABILITIES:
  - Token not invalidated on logout
  - Token not invalidated on password change
  - Token is predictable (user_id + timestamp)
  - Same token works across devices (no device binding)
  - Infinite number of valid tokens (each login adds more)
```

---

## Appropriate Session Lifetimes

```
INDUSTRY RECOMMENDATIONS:

HIGH SECURITY (banking, healthcare, admin):
  Idle timeout:    5-15 minutes
  Absolute timeout: 1-4 hours
  Remember Me:     Not recommended / disabled
  
MEDIUM SECURITY (e-commerce, email):
  Idle timeout:    30-60 minutes
  Absolute timeout: 8-24 hours
  Remember Me:     30 days maximum, with security controls
  
LOW SECURITY (public content, read-only):
  Idle timeout:    2-8 hours
  Absolute timeout: 7-30 days
  Remember Me:     OK with user consent
  
API TOKENS:
  Short-lived access tokens: 15-60 minutes
  Refresh tokens: 7-30 days (more like Remember Me)
  Machine-to-machine: longer, but rotate regularly
```

---

## Fix

```
IMPLEMENTING TIMEOUTS:

Python (Flask example):
  from datetime import datetime, timedelta
  
  # Check idle timeout:
  last_active = session.get('last_active')
  if last_active and datetime.now() - last_active > timedelta(minutes=30):
      session.clear()
      return redirect('/login')
  session['last_active'] = datetime.now()
  
  # Check absolute timeout:
  created_at = session.get('created_at')
  if created_at and datetime.now() - created_at > timedelta(hours=8):
      session.clear()
      return redirect('/login')

Django:
  SESSION_COOKIE_AGE = 3600  # 1 hour absolute (in settings.py)
  SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # for non-persistent sessions
  
  # Custom idle timeout middleware:
  IDLE_TIMEOUT = 1800  # 30 minutes
  # Implement via middleware that checks last request time

Node.js (express-session):
  session({
      secret: 'strong-secret',
      resave: false,
      saveUninitialized: false,
      cookie: { 
          maxAge: 30 * 60 * 1000  // 30 minutes
      },
      rolling: true  // reset timer on each request (idle timeout behavior)
  })
```

---

## Related Notes
- [[08 - Session Not Invalidated on Logout]] — logout invalidation
- [[10 - Concurrent Session Not Invalidated]] — multiple sessions
- [[15 - Defense Secure Session Configuration]] — full hardening
