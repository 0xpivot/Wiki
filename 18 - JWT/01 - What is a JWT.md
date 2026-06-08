---
tags: [vapt, jwt, beginner]
difficulty: beginner
module: "18 - JWT"
topic: "18.01 What is a JWT?"
portswigger_labs: ["JWT authentication bypass via unverified signature", "JWT authentication bypass via flawed signature verification"]
---

# 18.01 — What Is a JWT?

## JSON Web Token Overview

```
JWT (JSON Web Token):
  A compact, URL-safe way to represent claims securely between parties
  
  KEY PROPERTY: Self-contained!
  The token ITSELF contains the user data AND proof of authenticity
  No database lookup needed to know who the user is
  
COMMON USES:
  - API authentication (Authorization: Bearer TOKEN)
  - SSO across services
  - Stateless session management
  - Secure information exchange
  
WHERE YOU'LL SEE JWTs:
  Authorization header: Authorization: Bearer eyJhbGciOi...
  Cookie: session=eyJhbGciOi...
  URL parameter: ?token=eyJhbGciOi... (bad practice)
  localStorage: window.localStorage.getItem('token')
  WebSocket handshake header
```

---

## JWT vs Traditional Session

```
TRADITIONAL SESSION:
  Server stores: { session_id: "abc123" → user_id: 42, role: "admin" }
  Client has:    session_id=abc123 (just a random ID)
  
  On each request:
  Client → sends abc123 → Server looks up in DB → gets user data
  
  REVOCATION: Easy (delete from DB)
  SCALING: Needs shared session store (Redis)
  
JWT SESSION:
  Server creates: { user_id: 42, role: "admin", exp: 1640086400 }
  Server signs with secret/private key
  Client has: base64(header).base64(payload).signature
  
  On each request:
  Client → sends JWT → Server validates signature → reads user data from JWT
  No DB lookup!
  
  REVOCATION: Hard (must track blocklist or wait for expiry)
  SCALING: Easy (any server can validate with shared key/public key)
```

---

## Identifying JWTs

```
JWTs START WITH: eyJ

  eyJ = base64-decoded: {"
  All JWT headers start with {"alg": ... which encodes as eyJ...
  
EXAMPLES:
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 .
  eyJ1c2VyX2lkIjo0Miwicm9sZSI6InVzZXIifQ .
  [signature]
  
DECODE IMMEDIATELY:
  Browser: jwt.io → paste token → see decoded
  CLI: echo "PAYLOAD_PART" | base64 -d
  Python: 
    import base64, json
    payload = "eyJ1c2VyX2lkIjo0Miwicm9sZSI6InVzZXIifQ"
    print(json.loads(base64.b64decode(payload + "==")))
    
WHERE TO LOOK IN BURP:
  HTTP History → search for "eyJ" in request/response bodies
  Burp → Decoder → paste JWT part → base64 decode → JSON visible
  Also: look in cookies, Authorization headers, responses
```

---

## Why JWTs Can Be Attacked

```
ATTACK SURFACE:
  1. Signature not verified at all!
     (Just decode payload, ignore signature)
     
  2. Algorithm "none" accepted:
     (Remove signature entirely, change payload)
     
  3. Algorithm confusion:
     (Forge with different algorithm using public key)
     
  4. Weak secret:
     (Brute force the HMAC secret → forge any payload)
     
  5. Header injection:
     (Tell server to use attacker's key for verification)
     
  6. Claims not validated:
     (exp not checked → expired tokens still work)
     (aud not checked → tokens from other apps accepted)
     
  BOTTOM LINE:
  JWT gives a FALSE sense of security if not implemented correctly!
  Developers see "signed" and think "safe" without verifying HOW it's signed.
```

---

## Quick Decode Cheatsheet

```bash
# DECODE FULL JWT:
JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInJvbGUiOiJ1c2VyIn0.signature"

echo $JWT | cut -d. -f1 | base64 -d 2>/dev/null; echo  # header
echo $JWT | cut -d. -f2 | base64 -d 2>/dev/null; echo  # payload

# PYTHON ONE-LINER:
python3 -c "
import base64, json, sys
token = sys.argv[1] if len(sys.argv)>1 else 'YOUR_JWT_HERE'
parts = token.split('.')
for i, part in enumerate(['Header','Payload']):
    pad = 4 - len(parts[i]) % 4
    decoded = base64.b64decode(parts[i] + '='*pad)
    print(f'{part}: {json.dumps(json.loads(decoded), indent=2)}')
" $JWT

# JWT.IO: (browser)
# Visit: https://jwt.io
# Paste token → see decoded header, payload, and signature verification
```

---

## Related Notes
- [[02 - JWT Structure]] — header, payload, signature in detail
- [[03 - JWT Claims Reference]] — standard JWT claims
- [[04 - Algorithm None Attack]] — most common JWT bypass
- [[17.14 - Client-Side Session Tokens]] — where JWTs fit in session management
