---
tags: [vapt, session-management, defense, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.15 Defense — Secure Session Configuration"
---

# 17.15 — Defense: Secure Session Configuration

## Session ID Generation

```
REQUIREMENTS:
  ✓ 128-bit minimum entropy (256-bit recommended)
  ✓ Cryptographically secure PRNG (not Math.random()!)
  
IMPLEMENTATIONS:
  Python:  import secrets; session_id = secrets.token_hex(32)
  PHP:     $id = bin2hex(random_bytes(32));
  Node.js: crypto.randomBytes(32).toString('hex')
  Java:    SecureRandom + Base64 encoding
  
NEVER:
  ✗ Sequential numbers
  ✗ Timestamp-based
  ✗ MD5/SHA1 of predictable data
  ✗ username + timestamp
```

---

## Cookie Configuration

```
THE IDEAL COOKIE:
  Set-Cookie: __Host-session=TOKEN; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
  
  Breaking it down:
  __Host- prefix    → browser enforces Secure, Path=/, no Domain attrib
  HttpOnly          → JavaScript cannot read (blocks XSS theft)
  Secure            → HTTPS only (blocks network sniffing)
  SameSite=Lax      → Cross-site POST blocked (blocks CSRF)
  Path=/            → Sent for all paths (required for __Host-)
  Max-Age=3600      → Cookie expires in 1 hour (absolute limit)

FRAMEWORK SETTINGS:

  Django (settings.py):
  SESSION_COOKIE_NAME = '__Host-session'  # note: frameworks may not support prefix
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_SAMESITE = 'Lax'
  SESSION_COOKIE_AGE = 3600  # 1 hour absolute
  SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # optional: no persistent sessions

  Flask:
  SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_SAMESITE = 'Lax'
  PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
  
  Express.js:
  app.use(session({
    name: '__Host-session',
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      maxAge: 3600000  // 1 hour
    },
    rolling: true  // reset timer on each request (idle timeout)
  }));
  
  Spring Boot (application.properties):
  server.servlet.session.cookie.http-only=true
  server.servlet.session.cookie.secure=true
  server.servlet.session.cookie.same-site=lax
  server.servlet.session.timeout=3600
```

---

## Session Lifecycle Management

```
ON AUTHENTICATION:
  ✓ Regenerate session ID immediately after login!
  ✓ Clear all previous session state (prevent fixation)
  
  Django: request.session.cycle_key()
  Express: req.session.regenerate(callback)
  PHP: session_regenerate_id(true)

ON LOGOUT:
  ✓ Delete session from server-side store
  ✓ Delete cookie from client (Max-Age=0)
  ✓ Redirect to login (never serve content after logout)
  
  # Python:
  db.delete_session(session_id)
  response.delete_cookie('session')
  return redirect('/login')

ON PASSWORD CHANGE:
  ✓ Invalidate ALL other sessions for this user
  ✓ Keep current session (user just re-authenticated)
  
  db.execute("DELETE FROM sessions WHERE user_id = ? AND id != ?",
             [user_id, current_session_id])

ON EMAIL/PHONE CHANGE:
  ✓ Invalidate all sessions (requires re-login)

SESSION TIMEOUT:
  ✓ Idle timeout: 30 minutes inactivity
  ✓ Absolute timeout: 8 hours maximum
  
  # Track last_active in session:
  if now - session.last_active > IDLE_TIMEOUT: logout()
  if now - session.created_at > ABSOLUTE_TIMEOUT: logout()
  session.last_active = now
```

---

## Session Storage Backend

```
USE SECURE, EXTERNAL SESSION STORE (not memory!):
  
  Redis:
    Fast, supports TTL (auto-expiry), supports clustering
    Secure with: AUTH password, TLS, bind to localhost
    
    # Python + Redis:
    from redis import Redis
    from flask_session import Session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = Redis(host='localhost', port=6379, password='STRONG_PASS')
    
  Database (PostgreSQL, MySQL):
    Persistent, can be audited, supports concurrent session listing
    Slower than Redis but more durable
    
  NEVER:
    ✗ In-process memory (doesn't scale to multiple servers)
    ✗ File system (race conditions, file permissions)
    ✗ JWT in cookie without tracking (can't revoke without blocklist)
```

---

## Session Security Checklist

```
CONFIGURATION:
  ✓ HttpOnly flag on session cookie
  ✓ Secure flag on session cookie (HTTPS only)
  ✓ SameSite=Lax (or Strict for high-security)
  ✓ Appropriate Max-Age (1-8 hours, not 1 year)
  ✓ Cookie prefix (__Host- or __Secure-)
  
GENERATION:
  ✓ 256-bit cryptographically random session ID
  ✓ Not predictable, no patterns
  ✓ Tested with Burp Sequencer
  
LIFECYCLE:
  ✓ Session regenerated on login (prevents fixation)
  ✓ Session deleted on logout (server-side)
  ✓ Session expires server-side (not just cookie expiry)
  ✓ Idle timeout (30 min) AND absolute timeout (8 hours)
  ✓ All sessions invalidated on password change
  ✓ User can view and revoke active sessions
  
STORAGE:
  ✓ Session data in server-side store (Redis/DB)
  ✓ Not in localStorage (XSS risk)
  ✓ Not in URL parameters
  
CONCURRENT SESSIONS:
  ✓ Policy defined: allow or limit?
  ✓ User notified of new sessions?
  ✓ "Log out everywhere" feature available?
```

---

## Burp Testing Checklist

```
FOR EVERY WEB APP:
  1. Burp Sequencer → capture 200 tokens → analyze entropy
  2. Check Set-Cookie for HttpOnly, Secure, SameSite
  3. Check if session ID changes after login (fixation test)
  4. Logout → replay old token → still works? (invalidation test)
  5. Check expiry: wait >30 min → try → timeout working?
  6. Check localStorage for sensitive tokens (DevTools)
  7. Check URL parameters for tokens
  8. Password change → other session still works?
```

---

## Related Notes
- [[01 - What is a Session]] — fundamentals
- [[02 - Session Token Entropy and Predictability]] — entropy requirements
- [[03 - Session Fixation]] — attack this defends against
- [[11 - Cookie Flags Attack Scenarios]] — cookie attribute details
- [[16.28 - Defense Rate Limiting Lockout MFA]] — auth hardening
