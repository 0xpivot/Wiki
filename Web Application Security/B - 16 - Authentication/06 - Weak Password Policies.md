---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.06 Weak Password Policies"
---

# 16.06 — Weak Password Policies

## What Makes a Password Policy Weak?

```
WEAK POLICY INDICATORS:
  ✗ No minimum length (allows "a" as password)
  ✗ Very short minimum (< 8 characters)
  ✗ No complexity requirement (allows "password")
  ✗ Allows common passwords ("password", "123456", "qwerty")
  ✗ Allows username as password
  ✗ No maximum age / never rotated (old leaked passwords still work)
  ✗ Password stored in plaintext or MD5/SHA1 (unsalted)
  ✗ Password visible in URL or logs
  ✗ No lockout after failed attempts
  ✗ Password hints that are too helpful
  ✗ Security questions with guessable answers (mother's maiden name)
```

---

## Testing Password Policy

```
STEP 1: REGISTER OR CHANGE PASSWORD — TEST LIMITS:

Try the following passwords and note which are accepted:
  "a"           → reveals minimum length = 1 (bad!)
  "aaaaaa"      → check length minimum
  "password"    → is this blocked?
  "123456"      → is this blocked?
  "P@ssw0rd"    → does it accept simple complexity tricks?
  "aA1!aA1!"    → is complexity required?
  username itself → can they use their username as password?
  
  Too-long test: send 500-character password → does it truncate?
  → If truncated: "aaaa....aaaa" = "aaaa" (bypass!)

STEP 2: CHECK REGISTRATION RESPONSE:
  Does error message tell you the exact policy?
  "Password must be at least 8 characters" → reveals minimum
  
STEP 3: CHECK PASSWORD CHANGE:
  Can you change to the same password?
  Can you change to a password from 3 changes ago?
  (History policies = more secure)
```

---

## Password Truncation Attack

```
SOME SYSTEMS TRUNCATE PASSWORDS:
  If max password length = 20 chars and you set:
  "MySecurePassword1234IGNORED_AFTER_20"
  
  System stores: "MySecurePassword1234"
  
  LOGIN WITH: "MySecurePassword1234ANYTHING_HERE"
  → ALSO WORKS! Because it gets truncated to same value!
  
  MORE DANGEROUS CASE:
  If "password" and "password!@#$%^&*()" both work
  → effective minimum is just "password"
  
TESTING:
  1. Register with password: "Aaa11111111111111111" (20 chars)
  2. Try logging in with: "Aaa11111111111111111!!!!" (24 chars)
  3. If it works → truncation happening!
```

---

## Security Questions

```
PROBLEMS WITH SECURITY QUESTIONS:
  1. Answers are often guessable or publicly available
     "What's your mother's maiden name?" → LinkedIn, obituaries!
     "What city were you born in?" → Facebook profile!
     "What's your pet's name?" → Instagram photos!
     
  2. If the answer is a word, it can be brute forced
     500 most common dog names + 500 most common cities = quick attack
     
  3. Reset link bypasses password entirely → security question = your password!
  
TESTING:
  - Try common answers: "smith", "london", "fluffy", "123"
  - For a known target: OSINT their social media for answers
  - Test if answers are case-sensitive: "London" vs "london"
  - Test if spaces matter: "new york" vs "newyork"
  
EXAMPLE: Brute forcing security question:
  POST /forgot-password/verify
  email=victim@example.com&answer=§FUZZ§
  
  → No lockout? → try all 100 dog names → get in!
```

---

## Findings to Report

```
VAPT FINDING: "Weak Password Policy"
  
  Severity: Medium (account takeover impact)
  
  Evidence:
    - Accepted password: "a" (1 character)
    - Accepted password: "password" (common dictionary word)
    - No limit on failed login attempts observed
    
  Impact:
    - Brute force attacks require minimal effort
    - Dictionary attacks on login page practical
    
  Recommendation:
    - Minimum 12 characters
    - Complexity (mix of character classes)
    - Block top 10,000 common passwords (NIST SP 800-63B)
    - Implement HIBP API check on password set
    - Rate limit login attempts
```

---

## NIST Password Guidelines (SP 800-63B)

```
WHAT NIST ACTUALLY RECOMMENDS (often surprising!):
  ✓ Length: 8+ characters minimum (15+ recommended)
  ✓ Block known-compromised passwords (HIBP API check)
  ✓ Allow all printable ASCII (spaces too!)
  ✓ NO required complexity rules (uppercase+number+symbol requirements)
     Reason: Users meet complexity by making passwords LESS memorable!
             P@ssw0rd is WORSE than "CorrectHorseBatteryStaple"
  ✓ NO mandatory rotation (unless breach suspected)
     Reason: Rotation leads to predictable patterns (Password1→Password2)
  ✓ NO password hints or security questions
  ✓ Hash with bcrypt/scrypt/Argon2 (NOT MD5/SHA1/SHA256!)
```

---

## Fix

```
IMPLEMENTATION:
  ✓ Minimum 12 characters
  ✓ No maximum length restriction (allow passphrases!)
  ✓ Check against HaveIBeenPwned on password creation:
  
  import requests
  def check_hibp(password):
      sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
      prefix, suffix = sha1[:5], sha1[5:]
      resp = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
      return suffix in resp.text  # True = compromised password
      
  ✓ Hash with bcrypt (cost factor 12+) or Argon2id
  ✓ Salt every hash (bcrypt/Argon2 do this automatically)
  ✓ Rate limit + lockout (see note 16.28)
```

---

## Related Notes
- [[02 - Password Brute Force]] — exploiting weak policies
- [[07 - Forgot Password Token Predictability]] — password reset weaknesses
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
