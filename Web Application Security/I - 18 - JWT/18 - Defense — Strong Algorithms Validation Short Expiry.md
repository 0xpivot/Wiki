---
tags: [vapt, jwt, defense, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.18 Defense — Strong Algorithms, Validation, Short Expiry"
---

# 18.18 — Defense: JWT Security

## Algorithm Security

```
ALGORITHM CHOICE:
  ✓ RS256 (RSA-SHA256) — RECOMMENDED for APIs:
    + Private key signs → only server can issue tokens
    + Public key verifies → any service can validate
    + Even if source code stolen → can't forge tokens (no private key)
    
  ✓ HS256 (HMAC-SHA256) — OK for simple single-server:
    + Fast, simple
    - Shared secret → if leaked, attacker can forge!
    - Minimum 256-bit random secret required
    
  ✗ NEVER: "none", RS256 with a weak key, shared secrets across services

KEY GENERATION:
  # Generate RSA key pair:
  openssl genrsa -out private.pem 2048
  openssl rsa -in private.pem -pubout -out public.pem
  
  # Generate strong HS256 secret:
  python3 -c "import secrets; print(secrets.token_hex(32))"
  # → 64-char hex = 256-bit secret
  
  # Store in environment variable:
  export JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  export JWT_PRIVATE_KEY=$(cat private.pem)
  export JWT_PUBLIC_KEY=$(cat public.pem)
```

---

## Token Generation

```python
# PYTHON (PyJWT) - SECURE JWT GENERATION:
import jwt
import os
from datetime import datetime, timedelta, timezone
import uuid

def create_access_token(user_id, role, email):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'email': email,
        'role': role,
        'iss': 'https://auth.example.com',
        'aud': 'https://api.example.com',
        'iat': now,
        'exp': now + timedelta(minutes=15),  # SHORT EXPIRY!
        'jti': str(uuid.uuid4())             # UNIQUE ID!
    }
    
    private_key = os.environ['JWT_PRIVATE_KEY']
    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token

def create_refresh_token(user_id, session_id):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'session_id': session_id,
        'type': 'refresh',
        'iss': 'https://auth.example.com',
        'iat': now,
        'exp': now + timedelta(days=7),
        'jti': str(uuid.uuid4())
    }
    
    private_key = os.environ['JWT_PRIVATE_KEY']
    return jwt.encode(payload, private_key, algorithm='RS256')
```

---

## Token Validation

```python
# PYTHON (PyJWT) - SECURE JWT VALIDATION:
import jwt
import os
from datetime import datetime, timezone

PUBLIC_KEY = os.environ['JWT_PUBLIC_KEY']
EXPECTED_ISSUER = 'https://auth.example.com'
EXPECTED_AUDIENCE = 'https://api.example.com'
EXPECTED_ALGORITHM = 'RS256'

def validate_token(token):
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=[EXPECTED_ALGORITHM],  # WHITELIST! Not from header!
            issuer=EXPECTED_ISSUER,            # Validate iss!
            audience=EXPECTED_AUDIENCE,        # Validate aud!
            options={
                'verify_exp': True,            # Always verify expiry!
                'verify_iss': True,            # Always verify issuer!
                'verify_aud': True,            # Always verify audience!
                'require': ['exp', 'iss', 'aud', 'sub', 'jti']  # Required claims!
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expired")
    except jwt.InvalidIssuerError:
        raise AuthError("Invalid issuer")
    except jwt.InvalidAudienceError:
        raise AuthError("Invalid audience")
    except jwt.DecodeError:
        raise AuthError("Invalid token format")
    except jwt.InvalidSignatureError:
        raise AuthError("Invalid signature")

# Node.js (jsonwebtoken):
const jwt = require('jsonwebtoken');
const PUBLIC_KEY = fs.readFileSync('public.pem');

function validateToken(token) {
    return jwt.verify(token, PUBLIC_KEY, {
        algorithms: ['RS256'],          // Whitelist!
        issuer: 'https://auth.example.com',
        audience: 'https://api.example.com',
        ignoreExpiration: false         // Never set to true!
    });
}
```

---

## JWT Security Checklist

```
GENERATION:
  ✓ Use RS256 (or strong HS256 secret if RS256 not feasible)
  ✓ Include exp (15 min for access tokens)
  ✓ Include jti (UUID) for replay prevention
  ✓ Include iss (your auth server URL)
  ✓ Include aud (intended recipient service)
  ✓ Include sub (user identifier)
  ✓ Store private key securely (not in code, use env vars / vault)
  
VALIDATION (every request):
  ✓ Verify signature using hardcoded algorithm (not from header!)
  ✓ Verify exp (reject expired tokens)
  ✓ Verify iss (reject tokens from other issuers)
  ✓ Verify aud (reject tokens for other services)
  ✓ For one-time tokens: check jti against used-token store
  ✓ Never accept "alg: none"
  ✓ Never trust jwk, jku, kid headers to determine verification key
    (If using kid: validate against internal allowlist only!)
    
STORAGE AND TRANSMISSION:
  ✓ Access tokens: short-lived, HttpOnly cookie or in-memory (not localStorage)
  ✓ Refresh tokens: HttpOnly cookie with SameSite=Strict
  ✓ Never send tokens in URL parameters
  ✓ Use HTTPS always
  
LIFECYCLE:
  ✓ Access token: 15 minutes
  ✓ Refresh token: 7-30 days (with rotation!)
  ✓ Invalidate all tokens on: logout, password change, email change
  ✓ Refresh token rotation (single-use + reuse detection)
  
OPERATIONS:
  ✓ Never commit JWT secrets to version control
  ✓ Rotate keys periodically (support key_id for graceful rotation)
  ✓ Monitor for unusual token usage patterns
  ✓ Log failed JWT validation attempts
```

---

## Key Rotation

```python
# SUPPORTING MULTIPLE KEYS (for rotation without logout storms):
SIGNING_KEYS = {
    "key-2024-01": load_private_key("key-2024-01-private.pem"),
    "key-2024-06": load_private_key("key-2024-06-private.pem"),  # current
}
VERIFICATION_KEYS = {
    "key-2024-01": load_public_key("key-2024-01-public.pem"),
    "key-2024-06": load_public_key("key-2024-06-public.pem"),
}
CURRENT_KID = "key-2024-06"

# SIGN with current key:
def sign(payload):
    return jwt.encode(payload, SIGNING_KEYS[CURRENT_KID], 
                      algorithm='RS256',
                      headers={'kid': CURRENT_KID})

# VERIFY with whichever key the token specifies:
def verify(token):
    header = jwt.get_unverified_header(token)
    kid = header.get('kid')
    
    if kid not in VERIFICATION_KEYS:  # ALLOWLIST CHECK!
        raise AuthError("Unknown key ID")
    
    return jwt.decode(token, VERIFICATION_KEYS[kid], algorithms=['RS256'])
```

---

## Related Notes
- [[04 - Algorithm None Attack]] — what this prevents
- [[05 - RS256 to HS256 Algorithm Confusion]] — what this prevents
- [[06 - Weak Secret Brute Force]] — why strong secrets matter
- [[07 - JWT Header Injection jwk claim]] — why not to trust jwk
- [[08 - JWT Header Injection jku claim]] — why not to trust jku
- [[16 - Refresh Token Attacks]] — refresh token security
