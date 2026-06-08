---
tags: [vapt, jwt, beginner]
difficulty: beginner
module: "18 - JWT"
topic: "18.03 JWT Claims Reference (iss, sub, aud, exp, nbf, iat, jti)"
---

# 18.03 — JWT Claims Reference

## Standard Claims (RFC 7519)

### iss — Issuer

```
PURPOSE: Who created and signed this token?
FORMAT: String (usually URL or name)
EXAMPLE: "iss": "https://auth.example.com"

ATTACK: What if iss is not validated?
  Token from attacker's server (different iss) → accepted by target app!
  → SUBSTITUTION ATTACK: steal token format → sign with own key → accepted!
  
TEST: Decode token → change iss value → re-encode (no re-sign if alg=none)
      Does server accept tokens with wrong iss?

FIX: Always validate iss matches expected issuer:
  if payload.iss != "https://auth.example.com": reject!
```

### sub — Subject

```
PURPOSE: Who is this token for? (Usually user identifier)
FORMAT: String (user ID, email, username)
EXAMPLE: "sub": "user_42"  OR  "sub": "alice@example.com"

ATTACK: IDOR via sub
  Your token: "sub": "42"
  Try changing to: "sub": "1" (admin user?)
  → If no signature validation → could access admin account!
  
NOTE: Only exploitable if signature is not checked (alg=none) 
      or secret is known (brute forced)
```

### aud — Audience

```
PURPOSE: Who is this token FOR? (Intended recipients)
FORMAT: String or array of strings
EXAMPLE: "aud": "https://api.example.com"
         "aud": ["api.example.com", "billing.example.com"]

ATTACK: What if aud is not validated?
  A token issued for service A could be replayed against service B!
  
SCENARIO:
  User logs into app.example.com → gets token with aud="app.example.com"
  Admin API at admin.example.com → if it doesn't check aud:
  → Attacker uses user's token to access admin API!
  
FIX: Always validate aud matches your service identifier
```

### exp — Expiration Time

```
PURPOSE: Token is invalid after this Unix timestamp
FORMAT: Integer (Unix timestamp seconds)
EXAMPLE: "exp": 1640086400  (= 2022-01-01 00:00:00 UTC)

ATTACK: What if exp is not validated?
  Use a token from months/years ago → still accepted!
  → Perfect for attackers who stole old tokens
  
TEST:
  Decode your token → note exp timestamp
  Wait until after expiry → try using the token
  → If still works → exp not validated!
  
  OR: modify exp to past timestamp → if still works → not validated!
  
REPORTING: "JWT expiry (exp claim) not validated"
FIX: Always check: if current_time > payload.exp: reject!
```

### nbf — Not Before

```
PURPOSE: Token is invalid BEFORE this timestamp
FORMAT: Integer (Unix timestamp)
EXAMPLE: "nbf": 1640000000

USAGE: Delayed-activation tokens (e.g., password reset link valid in 5 min)
ATTACK: Not commonly exploited directly
       But if not checked: can use a token before its valid window
```

### iat — Issued At

```
PURPOSE: When was the token created?
FORMAT: Integer (Unix timestamp)
EXAMPLE: "iat": 1640000000

USAGE: For calculating token age, logging
ATTACK: If server uses iat to calculate expiry:
  Modify iat to a future timestamp → token seems newer → longer validity!
  (Only if server calculates exp from iat instead of having explicit exp)
```

### jti — JWT ID

```
PURPOSE: Unique identifier for this specific token
FORMAT: String (usually UUID)
EXAMPLE: "jti": "c8fa6cfd-4a3d-4a2d-b8c1-3a4a5b6c7d8e"

USAGE: Prevent replay attacks (server tracks used jti values)
ATTACK: If jti is not tracked:
  Replay the same token multiple times → all succeed
  → One-time tokens (e.g., password reset via JWT) reusable!
  
FIX: Store used jti values in cache/DB (with TTL = token expiry)
     On token validation: check jti not in used_jtis
```

---

## Custom Claims (App-Specific)

```
COMMON CUSTOM CLAIMS AND ATTACKS:
  
  "role": "user"       → try changing to "admin"
  "isAdmin": false     → try changing to true
  "permissions": [..] → try adding permissions
  "plan": "free"       → try changing to "enterprise"
  "userId": 42         → try changing to 1 (admin?)
  "email": "alice@.."  → try changing to victim's email
  
THESE ONLY WORK IF:
  - Signature not verified (alg=none attack)
  - Secret is known (brute forced)
  - Header injection allows attacker's key
  
METHODOLOGY:
  1. Decode token → read all claims
  2. Identify which claims control access/identity
  3. Attempt tampering via relevant attack (alg=none, weak secret, etc.)
```

---

## Claim Validation Checklist

```
SERVER SHOULD VALIDATE:
  ✓ Signature valid (using correct algorithm + correct key)
  ✓ alg is expected (whitelist: only accept RS256, reject "none")
  ✓ exp > current timestamp (not expired)
  ✓ nbf < current timestamp (valid now)
  ✓ iss matches expected issuer
  ✓ aud matches this service's identifier
  ✓ jti not seen before (if replay protection needed)
  ✓ sub is a valid, active user (not deleted)
  
IF ANY FAIL → REJECT! Log the attempt for security monitoring.
```

---

## Related Notes
- [[04 - Algorithm None Attack]] — exploiting alg header
- [[10 - JWT Expiry Manipulation]] — attacking exp claim
- [[11 - JWT Replay Attack]] — attacking jti
- [[12 - JWT Substitution Attack]] — swapping tokens between users/services
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — proper validation
