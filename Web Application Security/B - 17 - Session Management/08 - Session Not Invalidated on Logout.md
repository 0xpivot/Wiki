---
tags: [vapt, session-management, beginner]
difficulty: beginner
module: "17 - Session Management"
topic: "17.08 Session Not Invalidated on Logout"
---

# 17.08 — Session Not Invalidated on Logout

## The Problem

```
WHAT LOGOUT SHOULD DO:
  1. Invalidate session server-side (delete from database/cache)
  2. Clear session cookie on client (send Set-Cookie with Max-Age=0 or expired date)
  
WHAT BROKEN LOGOUT DOES:
  Only clears the cookie on the client side!
  The session still exists on the server!
  
  → Session token still in Burp history
  → Replay old session token → still logged in!
  → Attacker who stole session token earlier → still works!
  → Attacker on shared computer looks at browser history → reuses session!
```

---

## Testing for Broken Logout

```
STEP 1: Log in → Note your session token
  (Check cookies in DevTools → Application → Cookies)
  Or: Burp → HTTP History → find Set-Cookie with session token
  
  Session value: abc123xyzdef456
  
STEP 2: Perform some authenticated action (confirm session works):
  GET /account → 200 OK, shows your account
  
STEP 3: Log out (click logout button or navigate to /logout)

STEP 4: Try the OLD session token directly:
  Burp → Repeater → GET /account
  Add old cookie: Cookie: session=abc123xyzdef456
  
  → 200 OK, shows your account? → SESSION NOT INVALIDATED ON LOGOUT!
  → 302 redirect to /login? → Correctly invalidated! (good)

COMMAND LINE TEST:
  # Capture session before logout:
  SESSION=$(curl -c cookies.txt -s -X POST https://target.com/login \
    -d "username=test&password=test" \
    -D - | grep -i "set-cookie" | grep "session=" | cut -d= -f2 | cut -d';' -f1)
  
  # Confirm works:
  curl -H "Cookie: session=$SESSION" https://target.com/account  # should work
  
  # Logout:
  curl -b cookies.txt https://target.com/logout
  
  # Try old session:
  curl -H "Cookie: session=$SESSION" https://target.com/account
  # 200 = not invalidated! 302 = invalidated correctly!
```

---

## Why This Happens (Client-Side Only Logout)

```javascript
// WRONG IMPLEMENTATION:
// Server-side /logout handler:
def logout(request):
    response.delete_cookie('session')  // only clears cookie!
    return redirect('/login')
    // The session in the database/memory is NEVER deleted!

// CORRECT IMPLEMENTATION:
def logout(request):
    session_id = request.cookies.get('session')
    db.execute("DELETE FROM sessions WHERE id = ?", [session_id])  // ← DELETE IT!
    response.delete_cookie('session')
    return redirect('/login')
```

---

## Additional Logout Scenarios

```
SCENARIO 1: PASSWORD CHANGE DOESN'T INVALIDATE SESSIONS
  User changes password on device A
  Other sessions (device B, stolen session) → still valid!
  
  TEST:
  1. Login on two browser tabs (same or different)
  2. Change password in tab A
  3. Try to access protected page in tab B
  → If tab B still works → sessions not invalidated on password change!
  
  FIX: On password change → delete ALL user sessions from DB
  
SCENARIO 2: ROLE CHANGE DOESN'T INVALIDATE SESSION
  Admin demotes user to viewer
  User's existing session → still has admin privileges!
  
  TEST:
  1. Login as admin
  2. Note session token
  3. Admin reduces your privileges
  4. Try old session → still admin?
  
  FIX: On role/permission change → delete user's active sessions

SCENARIO 3: SESSION TIMEOUT — COOKIE EXPIRES BUT SESSION LIVES
  Cookie has Max-Age=3600 (1 hour)
  Client: cookie deleted after 1 hour
  Server: session row never deleted!
  
  → Browser naturally expires cookie → seems secure
  → But attacker with raw cookie value → still works after 1 hour!
  
  FIX: Server-side session expiry as well!
  Add expires_at column to sessions table
  On session lookup: check if expired → if so, reject AND delete
```

---

## Fix

```
SERVER-SIDE SESSION INVALIDATION:

Python (Flask):
  @app.route('/logout')
  def logout():
      session_id = request.cookies.get('session_id')
      db.execute("DELETE FROM sessions WHERE id = ?", [session_id])
      response = make_response(redirect('/login'))
      response.set_cookie('session_id', '', max_age=0, expires=0)
      return response

Django:
  from django.contrib.auth import logout
  logout(request)  # ← Django's built-in: flushes session from DB + cookie

Node.js (express-session):
  app.get('/logout', (req, res) => {
      req.session.destroy(err => {  // ← destroys server-side session!
          res.clearCookie('connect.sid');
          res.redirect('/login');
      });
  });

ADDITIONAL:
  ✓ Invalidate all sessions on password change
  ✓ Invalidate all sessions on role change
  ✓ Session expiry on server-side (not just cookie expiry)
  ✓ "Logout everywhere" feature for users to revoke all sessions
```

---

## Related Notes
- [[09 - Long-Lived Sessions]] — session lifetime management
- [[10 - Concurrent Session Not Invalidated]] — managing multiple sessions
- [[15 - Defense Secure Session Configuration]] — full hardening
