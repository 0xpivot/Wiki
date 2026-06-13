---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.11 JWT Replay Attack"
---

# 18.11 — JWT Replay Attack

## What Is a Replay Attack?

```
REPLAY ATTACK:
  Use a previously captured valid token again to perform actions
  that the original token was already used for
  
  OR: Use a valid token in a different context than intended
  
SCENARIOS:
  1. One-time use tokens used multiple times
     (Password reset JWT, email verification JWT)
  2. Valid access token used after logout
     (Server doesn't track revoked tokens)
  3. Token from one service used at another
     (aud claim not validated)
  4. Captured token from network → replayed by attacker
```

---

## Scenario 1: One-Time Token Reuse

```
PASSWORD RESET VIA JWT:
  GET /reset-password?token=JWT_TOKEN
  
  JWT payload: { "type": "reset", "userId": 42, "exp": 1640086400 }
  
  SECURE BEHAVIOR:
  1. User uses token → password changed
  2. Token marked as used in database (jti stored)
  3. Token used again → server checks DB → already used → REJECT!
  
  VULNERABLE BEHAVIOR:
  1. User uses token → password changed
  2. No jti tracking
  3. Token used again → within expiry window → ACCEPTED!
  
TEST:
  Request password reset → get email with link
  Click link → change password → success!
  Go back and click SAME link again
  → If it loads the reset form again → replay possible!
  → If it says "invalid or expired token" → not replayable

EMAIL VERIFICATION REPLAY:
  Same concept: GET /verify?token=JWT
  Verify once → mark as used → verify again → should fail
  If not tracked → can verify any email multiple times
  → Could bypass email verification flows
```

---

## Scenario 2: Logout + Token Still Valid

```
JWT STATELESS PROBLEM:
  Server issues JWT → user has token → server forgets
  User logs out → server just says "delete your cookie"
  But JWT is still cryptographically valid!
  
  Attacker captured the JWT before logout → uses it after logout
  → Server has no record of logout → token still valid → ACCEPTED!
  
TEST:
  1. Login → capture JWT
  2. Logout (click logout or POST /logout)
  3. Use the old JWT immediately:
     curl https://target.com/api/profile -H "Authorization: Bearer OLD_JWT"
  → 200 OK = token not invalidated on logout! (vulnerability)
  → 401 = token invalidated (requires JWT blocklist — rare, good!)

WORKAROUND WITHOUT BLOCKLIST:
  Short token expiry (5-15 min) → token expires naturally soon
  → Acceptable risk if expiry is short enough
```

---

## Scenario 3: Cross-Service Replay (Missing aud)

```
ENTERPRISE SETUP:
  auth.company.com issues JWTs for all services
  JWTs contain: aud = "https://hr.company.com"
  
  hr.company.com validates aud = "https://hr.company.com" → accepts
  payroll.company.com validates aud = "https://payroll.company.com" → rejects hr tokens!
  
  VULNERABLE: payroll.company.com doesn't check aud!
  → Use HR JWT at payroll.company.com → ACCEPTED!
  
TEST:
  Get your JWT from Service A
  Try using it at Service B (different application on same domain)
  → Accepted? → Missing audience validation
  
  Check your JWT payload for aud claim
  If aud is missing → server might accept this token for ANY service!
```

---

## jti — JWT ID for Replay Prevention

```
jti (JWT ID) CLAIM:
  Unique identifier for each JWT (UUID typically)
  
  Server should:
  1. Generate unique jti for each issued JWT
  2. When JWT is used: check if jti was seen before
  3. If seen before: REJECT (replay attempt!)
  4. Store jti in DB/cache until token expiry (then can delete)
  
  For one-time tokens (reset, verify):
  1. Use JWT → mark jti as "used" in DB
  2. On next use: jti in "used" set → REJECT
  
IMPLEMENTATION:
  # Redis for tracking:
  def validate_jwt(token):
      payload = verify_signature(token)
      jti = payload.get('jti')
      
      if jti is None:
          # No jti → either reject or allow without replay protection
          pass
      
      # Check if used:
      if redis.exists(f"jwt_used:{jti}"):
          raise Exception("Token already used")
      
      # Mark as used (with TTL = token expiry):
      remaining = payload['exp'] - time.time()
      redis.setex(f"jwt_used:{jti}", int(remaining), "1")
      
      return payload
```

---

## Fix

```
REPLAY ATTACK DEFENSES:

  ✓ jti tracking for one-time tokens:
    Store used jti in Redis with TTL equal to token expiry
    
  ✓ Short expiry for access tokens:
    15 minutes → captured token expires quickly
    
  ✓ JWT blocklist for logout:
    Store revoked JWTs until their expiry
    (Expensive but correct for stateless JWT)
    
  ✓ Refresh token rotation:
    Short-lived access tokens (15 min)
    Long-lived refresh tokens (24 hours)
    Refresh token one-time use (rotate on each refresh)
    → Stolen access token expires fast; stolen refresh token detectable
    
  ✓ Always validate aud claim:
    if payload.aud != EXPECTED_AUDIENCE: reject!
    
  ✓ Validate iss claim:
    Only accept tokens from your own auth server
```

---

## Related Notes
- [[03 - JWT Claims Reference]] — jti claim details
- [[10 - JWT Expiry Manipulation]] — exp claim bypass
- [[12 - JWT Substitution Attack]] — cross-user/service token swap
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
