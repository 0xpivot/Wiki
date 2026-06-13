---
tags: [vapt, jwt, beginner]
difficulty: beginner
module: "18 - JWT"
topic: "18.02 JWT Structure (Header.Payload.Signature)"
---

# 18.02 — JWT Structure

## Three Parts

```
JWT = BASE64URL(HEADER) . BASE64URL(PAYLOAD) . SIGNATURE

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJ1c2VySWQiOjEsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNjQwMDg2NDAwfQ
.tFnGiLwHGPwPi8vHGNPd2OuXpEKBb7ZBFj3kFzMjXk

HEADER | PAYLOAD | SIGNATURE
```

---

## Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}

alg: The signing algorithm
  HS256  = HMAC-SHA256 (symmetric, shared secret)
  HS384  = HMAC-SHA384
  HS512  = HMAC-SHA512
  RS256  = RSA-SHA256 (asymmetric: private signs, public verifies)
  RS384  = RSA-SHA384
  RS512  = RSA-SHA512
  ES256  = ECDSA-SHA256
  PS256  = RSASSA-PSS-SHA256
  none   = No signature (DANGEROUS!)
  
typ: Usually "JWT"

ADDITIONAL HEADER CLAIMS (used in attacks!):
  jwk:   Embedded JSON Web Key (attacker can provide their own key!)
  jku:   URL pointing to JWK Set (attacker can point to their server!)
  kid:   Key ID (lookup which key to use — injectable!)
  x5u:   URL of X.509 certificate (similar to jku)
  x5c:   X.509 certificate chain
```

---

## Payload

```json
{
  "iss": "https://example.com",
  "sub": "user_42",
  "aud": "https://api.example.com",
  "exp": 1640086400,
  "nbf": 1640000000,
  "iat": 1640000000,
  "jti": "unique-id-12345",
  "role": "user",
  "email": "alice@example.com"
}

STANDARD CLAIMS:
  iss (issuer):    Who created the token
  sub (subject):   Who the token is about (usually user ID)
  aud (audience):  Who the token is for (intended recipient)
  exp (expiry):    Token expiry (Unix timestamp)
  nbf (not before): Token not valid before this time
  iat (issued at): When token was created
  jti (JWT ID):    Unique token ID (prevents replay)
  
CUSTOM CLAIMS:
  role, email, name, permissions — app-specific data
  THESE ARE NOT ENCRYPTED — anyone can read them!
  Don't include: passwords, secrets, PII (unless necessary)
  
PAYLOAD IS BASE64 ONLY:
  NOT encrypted! Just base64-encoded!
  Anyone with the token can decode and read the payload!
```

---

## Signature

```
SIGNATURE COMPUTATION:

HS256 (HMAC, symmetric):
  signature = HMAC-SHA256(
    base64url(header) + "." + base64url(payload),
    secret_key
  )
  
  BOTH signing and verification use the SAME key
  Server signs on creation, server validates on receipt
  If key is leaked → anyone can forge tokens!

RS256 (RSA, asymmetric):
  signature = RSA-SHA256(
    base64url(header) + "." + base64url(payload),
    private_key
  )
  
  Verification: verify(data, signature, public_key)
  
  Server signs with PRIVATE key (kept secret)
  Anyone can verify with PUBLIC key (shared openly)
  Even if public key is leaked → can't forge (can't sign without private!)
  BETTER for APIs with multiple consumers

VERIFICATION PROCESS:
  1. Split token into header, payload, signature parts
  2. Re-compute expected signature from header+payload + key
  3. Compare computed signature to received signature
  4. If mismatch → token tampered → REJECT!
  5. Check exp (not expired), iss (expected issuer), aud (correct audience)
  6. Extract claims from payload → use for authorization

CRITICAL: If step 3 comparison doesn't happen → ANY payload accepted!
```

---

## BASE64URL Encoding

```
DIFFERENCE FROM REGULAR BASE64:
  Regular base64: +, /, = (padding)
  Base64URL:      -, _, and no padding (= removed)
  
  → URL-safe (can be used in URL parameters, headers without escaping)

DECODE EXAMPLES:
  Header: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
          = base64url decode → {"alg":"HS256","typ":"JWT"}
          
  Payload: eyJ1c2VySWQiOjEsInJvbGUiOiJ1c2VyIn0
           = {"userId":1,"role":"user"}

ENCODE:
  Python: base64.urlsafe_b64encode(data).rstrip(b'=')
  echo -n '{"alg":"none","typ":"JWT"}' | base64 | tr '+/' '-_' | tr -d '='
```

---

## JWT Anatomy Summary

```
TOKEN: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInJvbGUiOiJ1c2VyIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

PART 1 (Header):
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
  → {"alg":"HS256","typ":"JWT"}

PART 2 (Payload):
  eyJ1c2VySWQiOjEsInJvbGUiOiJ1c2VyIn0
  → {"userId":1,"role":"user"}
  
PART 3 (Signature):
  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  → HMAC-SHA256 of "PART1.PART2" using secret key
  → This proves the token hasn't been tampered with!
```

---

## Related Notes
- [[01 - What is a JWT]] — overview
- [[03 - JWT Claims Reference]] — standard claims in detail
- [[04 - Algorithm None Attack]] — exploiting algorithm header
- [[07 - JWT Header Injection jwk claim]] — injecting keys via header
