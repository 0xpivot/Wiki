---
tags: [vapt, authentication, defense, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.28 Defense — Rate Limiting, Lockout, MFA, Secure Password Storage"
---

# 16.28 — Defense: Authentication Security

## Secure Password Storage

```
RULE: NEVER STORE PLAINTEXT PASSWORDS!
      NEVER STORE REVERSIBLY ENCRYPTED PASSWORDS!
      
GOOD HASHING ALGORITHMS (adaptive, slow by design):
  bcrypt:   Work factor 12+. Industry standard for passwords.
  Argon2id: Winner of Password Hashing Competition. Best choice for new apps.
  scrypt:   Memory-hard, good for high-security.
  PBKDF2:   Acceptable (FIPS-compliant, required by some regulations).
  
BAD (DO NOT USE):
  MD5, SHA1, SHA256, SHA512 alone → too fast (billions/sec on GPU)
  Unsalted hash → rainbow table attacks
  MD5(password): cracked instantly with 14 billion hashes/sec
  
IMPLEMENTATION:

# Python - bcrypt:
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
# Verify:
bcrypt.checkpw(password.encode('utf-8'), hashed)

# Python - Argon2id (recommended for new code):
from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
hashed = ph.hash(password)
ph.verify(hashed, password)

# PHP - bcrypt (built in):
$hashed = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
password_verify($password, $hashed);

# Node.js:
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(password, 12);
const match = await bcrypt.compare(password, hash);

# Java - Spring Security:
BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);
String hash = encoder.encode(password);
encoder.matches(rawPassword, hash);
```

---

## Rate Limiting

```
RATE LIMIT LOGIN ENDPOINTS:
  Goal: Limit brute force attempts to impractical speed

IMPLEMENTATION:

Nginx (simple rate limit):
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  
  location /login {
      limit_req zone=login burst=3 nodelay;
  }
  # → Max 5 login attempts per minute per IP

Express.js (rate limiter):
  const rateLimit = require('express-rate-limit');
  const loginLimiter = rateLimit({
      windowMs: 15 * 60 * 1000,  // 15 minutes
      max: 20,                     // 20 attempts per 15 min
      message: 'Too many login attempts, please try again later.',
      standardHeaders: true,
  });
  app.post('/login', loginLimiter, handleLogin);

Django (django-ratelimit):
  @ratelimit(key='ip', rate='5/m', method='POST', block=True)
  def login_view(request):
      ...
```

---

## Account Lockout

```
LOCKOUT POLICY:
  Lock account after N consecutive failures
  Unlock after T minutes automatically (not permanent!)
  Notify user by email when locked
  
  CAREFUL:
  Too aggressive → Denial of Service on accounts!
  Too lenient → Brute force effective
  Balance: 10-20 attempts, 30 min lockout
  
IMPLEMENTATION (Python example):
  LOCKOUT_THRESHOLD = 10
  LOCKOUT_DURATION = 30 * 60  # 30 minutes in seconds
  
  def check_lockout(username, redis_client):
      key = f"login_failures:{username}"
      failures = int(redis_client.get(key) or 0)
      if failures >= LOCKOUT_THRESHOLD:
          return True  # locked!
      return False
  
  def record_failure(username, redis_client):
      key = f"login_failures:{username}"
      redis_client.incr(key)
      redis_client.expire(key, LOCKOUT_DURATION)  # auto-expire
  
  def reset_failures(username, redis_client):
      redis_client.delete(f"login_failures:{username}")

ALSO APPLY TO:
  - OTP/MFA code submissions
  - Password reset submissions
  - Security question answers
```

---

## Multi-Factor Authentication (MFA)

```
MFA HIERARCHY (weakest to strongest):
  SMS OTP     → acceptable but vulnerable to SIM swap
  Email OTP   → acceptable for low-risk
  TOTP App    → Google Authenticator, Authy — good for most apps
  Push Notify → Duo, Microsoft Authenticator — with number matching!
  FIDO2/WebAuthn → hardware key or platform authenticator — best!

TOTP IMPLEMENTATION (Python - pyotp):
  import pyotp
  
  # Setup (when user enables MFA):
  secret = pyotp.random_base32()  # generate and save per user
  totp = pyotp.TOTP(secret)
  qr_url = totp.provisioning_uri("user@example.com", issuer_name="MyApp")
  # Show QR code to user → they scan in Google Authenticator
  
  # Verify (on each login):
  totp = pyotp.TOTP(user.totp_secret)
  if not totp.verify(submitted_code, valid_window=1):
      return "Invalid OTP"
  # valid_window=1 allows T-1 and T+1 windows for clock skew
  
  # PREVENT REUSE:
  # Cache used (secret+code+window) in Redis for 90 seconds!

WEBAUTHN/FIDO2 (overview):
  Use a library: py_webauthn (Python), node-fido2 (Node.js), webauthn4j (Java)
  Platform authenticator: fingerprint / Face ID on device
  Roaming authenticator: YubiKey, Google Titan Key
  Phishing-resistant: bound to origin, can't be replayed elsewhere!
```

---

## Secure Session Management

```
SESSION SECURITY:
  ✓ Regenerate session ID on login (prevent session fixation):
    request.session.cycle_key()  # Django
    session.regenerate_id()       # PHP
    
  ✓ HttpOnly + Secure + SameSite on session cookies:
    Set-Cookie: session=XXX; HttpOnly; Secure; SameSite=Lax; Path=/
    
  ✓ Short session lifetime:
    Idle timeout: 15-30 min for sensitive apps
    Absolute timeout: 8-24 hours max
    
  ✓ Invalidate session on logout:
    DELETE from sessions WHERE id = :session_id
    (Don't just clear the cookie — also invalidate server-side!)
    
  ✓ Re-authenticate for sensitive actions:
    Changing email, password, phone, 2FA settings
    → Require current password even when logged in!
```

---

## Authentication Security Checklist

```
✓ Passwords hashed with bcrypt/Argon2id (never MD5/SHA1/plaintext)
✓ Rate limiting on login (5-10 attempts per minute per IP)
✓ Account lockout after 10-20 failures (30 min, not permanent)
✓ Generic error messages ("Invalid username or password")
✓ MFA available (TOTP minimum, FIDO2 for admins)
✓ Session regenerated on login
✓ HttpOnly, Secure, SameSite=Lax on session cookies
✓ CSRF token on login form
✓ Re-authentication for critical actions (password/email/MFA change)
✓ Password reset tokens: 128-bit random, 15 min expiry, single-use
✓ Strong password policy enforced server-side
✓ Breach check (HaveIBeenPwned API integration)
✓ No credentials in URL (POST for login, headers for API tokens)
✓ Debug mode disabled in production
✓ Generic 404/500 pages (no stack traces)
```

---

## Related Notes
- [[01 - Username Enumeration]] — errors that bypass this defense
- [[02 - Password Brute Force]] — what rate limiting defends against
- [[11 - MFA Bypass Response Manipulation]] — what server-side validation prevents
- [[07 - Forgot Password Token Predictability]] — token hardening
