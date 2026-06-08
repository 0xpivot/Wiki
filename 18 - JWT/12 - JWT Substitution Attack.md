---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.12 JWT Substitution Attack (swapping tokens between users)"
---

# 18.12 — JWT Substitution Attack

## What Is a Substitution Attack?

```
SUBSTITUTION ATTACK:
  Use a VALID token (correctly signed by the server)
  in a DIFFERENT context than intended
  
  TYPES:
  1. User A's token used to access User B's resources
     (Missing sub/userId validation in resource authorization)
     
  2. Token for Service A used at Service B
     (Missing aud validation — see 18.11 replay)
     
  3. Token from one environment used in another
     (Staging token used in production, or vice versa)
     
  4. Token from API v1 used on API v2
     (Version not validated in token)
```

---

## Attack: Cross-User Token Substitution

```
SCENARIO:
  Attacker (userId: 100) logs in → gets JWT:
  { "sub": "100", "email": "attacker@evil.com", "role": "user" }
  
  Victim (userId: 42) somehow logs in to attacker's OAuth provider
  OR: Attacker can issue themselves a token with sub=42
  
  SIMPLIFIED SCENARIO — IDOR via JWT:
  API call: GET /api/documents
  JWT payload: {"sub": "100"}
  Backend: SELECT * FROM documents WHERE user_id = jwt.sub
  
  IF ATTACKER CAN FORGE sub (via alg=none or known secret):
  JWT payload: {"sub": "42"}
  → Gets victim 42's documents!
  
  THIS IS JWT-BASED IDOR!
```

---

## Attack: Environment Substitution

```
SCENARIO:
  Company has: staging.example.com and app.example.com
  Both share the SAME JWT_SECRET (bad practice!)
  
  Attacker creates admin account on staging:
  staging JWT: {"userId": 1, "role": "admin", "iss": "staging.example.com"}
  
  Try this JWT on production:
  → If iss not validated → production accepts staging admin JWT!
  → Attacker is admin on production!
  
TEST:
  1. Check if staging JWT is accepted by production
  2. Decode JWT → does iss claim exist?
  3. If iss validation missing on prod → staging tokens work!
```

---

## Testing Cross-User Substitution

```bash
# STEP 1: Log in as User A → capture JWT A
# STEP 2: Log in as User B (attacker controls) → capture JWT B

# STEP 3: Check what claims identify the user:
python3 -c "
import base64, json, sys
token = sys.argv[1]
payload = json.loads(base64.urlsafe_b64decode(token.split('.')[1] + '=='))
print(json.dumps(payload, indent=2))
"

# Look for: sub, userId, user_id, email, username

# STEP 4: If you can forge tokens (alg=none / known secret):
# Change sub/userId to target user → test authorization

# STEP 5: Test API authorization:
# As user A, what resources can you access with user B's JWT?
curl https://target.com/api/profile \
  -H "Authorization: Bearer USER_A_JWT"
# → Shows User A's profile (expected)

# Now try:
curl https://target.com/api/users/100/profile \  # User 100's profile
  -H "Authorization: Bearer USER_A_JWT"  # User A's token
# → If shows User 100's data → IDOR (not JWT specific, but JWT-enabled)

# KEY QUESTION: Does the backend validate that the JWT's sub matches
# the resource being accessed? Or does it just check "is JWT valid"?
```

---

## OAuth Multi-Tenant Token Confusion

```
MULTI-TENANT APP:
  Same app, different organizations (tenants)
  
  Tenant A: company-a.app.com
  Tenant B: company-b.app.com
  
  JWT for tenant A user:
  { "sub": "alice", "tenant": "company-a", "role": "admin" }
  
  If tenant not validated at Tenant B's endpoints:
  → Alice can use her Tenant A admin JWT to access Tenant B's data!
  
TEST:
  1. Login at tenant A → get JWT
  2. Use JWT at tenant B's API
  3. Can you access tenant B's resources?
  
FIX:
  ✓ Always validate tenant claim in JWT
  ✓ All resource queries must include tenant filter:
    SELECT * FROM docs WHERE tenant_id = jwt.tenant AND id = doc_id
  ✓ aud claim should include tenant identifier
```

---

## Fix

```
DEFENSES AGAINST SUBSTITUTION ATTACKS:

  ✓ Validate sub against the resource being accessed:
    NOT: if jwt_valid → serve resource
    YES: if jwt_valid AND jwt.sub == resource.owner_id → serve resource
    
  ✓ Validate aud (audience):
    Token issued for Service A → rejected by Service B
    
  ✓ Validate iss (issuer):
    Production → only accept tokens from production auth server
    Staging → only accept tokens from staging auth server
    
  ✓ Validate tenant in multi-tenant apps:
    All DB queries must include tenant context from JWT
    
  ✓ Never share JWT secrets across environments!
    Different secret per environment (prod, staging, dev)
    
  ✓ Row-level authorization:
    After JWT validation → check specific resource ownership:
    if document.owner_id != jwt.sub: return 403
```

---

## Related Notes
- [[11 - JWT Replay Attack]] — cross-service replay (aud)
- [[03 - JWT Claims Reference]] — sub, aud, iss claims
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
