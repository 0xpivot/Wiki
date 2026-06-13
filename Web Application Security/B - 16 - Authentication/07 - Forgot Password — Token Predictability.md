---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.07 Forgot Password — Token Predictability"
portswigger_labs: ["Password reset broken logic", "Password reset poisoning via middleware"]
---

# 16.07 — Forgot Password: Token Predictability

## What Is a Password Reset Token?

```
FLOW:
  1. User clicks "Forgot Password"
  2. User enters email
  3. Server generates a RESET TOKEN and emails a link:
     https://example.com/reset?token=abcd1234efgh5678
  4. User clicks link → server validates token → allows password change
  
THE TOKEN IS THE KEY:
  Anyone who has the token can reset the password!
  Token must be:
    ✓ Random (unpredictable)
    ✓ Unique per request
    ✓ Short-lived (expire in 15-60 min)
    ✓ Single-use (invalidate after use)
    ✓ Long enough (128+ bits of entropy)
    
  If any of these are violated → attackers can bypass it!
```

---

## Predictable Token Patterns

```
COMMON WEAK TOKEN PATTERNS:

1. SEQUENTIAL / INCREMENTAL:
   Token = 1234 → 1235 → 1236
   → Request reset, get token 5000
   → Victim requests reset, gets token 5001
   → Attacker uses 5001 on victim's email!
   
2. TIMESTAMP-BASED:
   Token = md5(current_timestamp)
   → Request at same second → same token!
   → Brute force timestamps near request time
   
3. USERNAME + TIMESTAMP:
   Token = sha1(email + time())
   → Attacker knows victim's email + approximate time
   → Limited search space!
   
4. USERID-BASED:
   Token = base64(userid)
   → Token for user 100 = "MTAw"
   → User 101 = "MTAx"
   
5. SHORT TOKENS:
   Token = 6-digit PIN = 000000 to 999999 = only 1 million combos
   → No rate limiting? → brute force in minutes!
```

---

## Testing Token Predictability

```bash
# STEP 1: REQUEST MULTIPLE RESET TOKENS:
# Request password reset for test account 1 → note token
# Request password reset for test account 2 → note token
# Request 10 times for test account → note all tokens

# STEP 2: ANALYZE TOKENS:
# Do they look sequential? 
# Are they time-based? (convert timestamp, check if token matches)
# Are they base64-decodable?
# Are they URLs containing username/userid?

# STEP 3: CHECK EXPIRY:
# Try token after 1 hour → still works? (no expiry = bad!)
# Try token AFTER using it once → still works? (not single-use = bad!)

# DECODE TOKEN:
echo "MTAw" | base64 -d  # → "100" → userid-based!

# CHECK IF MD5 OF TIMESTAMP:
python3 -c "
import hashlib, time
# Try timestamps around the time you sent the request
for t in range(int(time.time())-5, int(time.time())+5):
    h = hashlib.md5(str(t).encode()).hexdigest()
    print(f'{t}: {h}')
"

# BURP INTRUDER — BRUTE FORCE SHORT TOKEN:
# GET /reset?token=§FUZZ§&email=victim@example.com
# Payload: numbers 100000 to 999999 (6-digit PIN)
```

---

## Token Reuse and No Expiry

```
TESTING TOKEN EXPIRY:
  1. Request reset token
  2. Wait 2 hours
  3. Try to use the token → still works? BAD!

TESTING SINGLE USE:
  1. Request reset → get token
  2. Use token → reset password
  3. Try token AGAIN
  → If it allows a second reset → token not invalidated!

TESTING OLD TOKEN STILL VALID AFTER NEW REQUEST:
  1. Request reset token #1 for victim
  2. Victim also requests reset token #2
  3. Try token #1 → still works? 
  → Server should invalidate old tokens when new one is issued!

TOKEN NOT TIED TO ACCOUNT:
  Token for alice → use on bob's reset URL?
  GET /reset?token=TOKEN_FROM_ALICE&email=bob@example.com
  → If it resets bob's password → CRITICAL!
```

---

## Exploiting Predictable Tokens

```
SCENARIO: Tokens are sequential integers

1. Create your own account
2. Request a password reset
3. Token received: 10042
4. Target user "victim" requests a reset at similar time
5. Their token is probably 10043 or 10044
6. Request: GET /reset?token=10043&email=victim@example.com
7. → Access victim's account!

SCENARIO: Tokens expire but old ones still valid

1. Victim requests reset (old token from weeks ago in their email)
2. Attacker somehow finds old token (email phishing, log leak, etc.)
3. Uses it → still works!

BURP SEQUENCER:
  Capture reset link → send to Sequencer → analyze entropy
  Burp Sequencer → Manual load → Test token field
  → Reports randomness score
  LOW FIPS score = token is predictable!
```

---

## Fix

```
SECURE TOKEN IMPLEMENTATION:
  
  Python:
  import secrets
  token = secrets.token_urlsafe(32)  # 256-bit URL-safe token
  
  PHP:
  $token = bin2hex(random_bytes(32));  // 256-bit hex string
  
  Node.js:
  const token = crypto.randomBytes(32).toString('hex');
  
  Java:
  SecureRandom sr = new SecureRandom();
  byte[] bytes = new byte[32];
  sr.nextBytes(bytes);
  String token = Base64.getUrlEncoder().encodeToString(bytes);

ADDITIONAL REQUIREMENTS:
  ✓ Store hashed token in DB (hash(token), not token itself)
  ✓ Expire in 15-60 minutes
  ✓ Single-use (delete/invalidate after first use)
  ✓ Invalidate all old tokens when new one issued
  ✓ Tie token to BOTH email AND userid (can't reuse across accounts)
  ✓ Rate limit reset requests (prevent token enumeration)
```

---

## Related Notes
- [[08 - Forgot Password Host Header Poisoning]] — different reset attack
- [[09 - Forgot Password Token Reuse]] — reuse and expiry issues in depth
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
