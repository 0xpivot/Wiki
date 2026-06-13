---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.12 MFA Bypass — Code Reuse"
---

# 16.12 — MFA Bypass: Code Reuse

## OTP Reuse Vulnerabilities

```
TYPES OF OTP:
  TOTP (Time-based OTP): Google Authenticator, Authy
    - 6-digit code, changes every 30 seconds
    - Based on: HMAC(secret, floor(timestamp / 30))
    
  HOTP (Counter-based OTP): Some hardware tokens
    - Code based on counter, not time
    - Counter increments each use
    
  SMS/Email OTP: Code sent per request
    - Usually 4-8 digits
    - Expires after N minutes or on use
    
THE REUSE VULNERABILITY:
  After OTP is successfully used → should be immediately invalidated!
  If not → attacker who intercepted the OTP can still use it!
```

---

## Testing TOTP Reuse

```
TEST 1: SAME SESSION, SECOND USE:
  1. Login → get to MFA page
  2. Use TOTP code → access granted → you're in
  3. Logout
  4. Login again → on MFA page
  5. Enter the SAME code (if still within 30s window)
  → If accepted → code not invalidated after first use!
  
  Even if you can't use same code for second full login,
  test cross-request reuse within the SAME session.

TEST 2: PREVIOUS WINDOW CODE:
  1. Note the OTP code at second 0 of a 30s window (e.g., code = "123456")
  2. Wait until window changes (second 30+) → new code "789012"
  3. On the MFA page, enter old code "123456"
  → Most implementations allow T-1 window for clock skew
  → Does the OLD code (now expired) still work?
  
TEST 3: PARALLEL SESSIONS:
  1. Open two browser tabs, both on MFA page (same session)
  2. Enter OTP in Tab 1 → success
  3. Quickly enter SAME OTP in Tab 2
  → If Tab 2 also succeeds → OTP not invalidated server-side
```

---

## SMS / Email OTP Reuse

```
SMS OTP REUSE SCENARIOS:

1. REQUEST MULTIPLE CODES — ALL VALID:
   Request OTP code 3 times
   → All 3 codes might still be valid!
   → Use the first code after receiving the third → works?
   
2. CODE DOESN'T EXPIRE AFTER USE:
   Verify OTP → success → you're in
   Now go back (browser back button) → re-submit OTP form with same code
   → If it processes again → reuse possible!
   
3. PREVIOUS EMAIL OTP STILL VALID:
   Yesterday's unclicked OTP email → does the old code still work?
   Test with your own account:
   - Request OTP, don't use it
   - Wait 24 hours
   - Try old code
   - If it works → no expiry!
   
4. REUSE ACROSS DIFFERENT LOGIN SESSIONS:
   OTP issued in session A → use in session B
   (e.g., request OTP, then clear cookies, login again, use old code)
```

---

## Backup Codes Reuse

```
BACKUP CODES:
  One-time-use codes for when you lose your authenticator
  Format: xxxxx-xxxxx or 8-10 digit numbers
  Typically 8-10 backup codes provided
  
REUSE TESTS:
  1. Register backup codes
  2. Use backup code #1 → access granted
  3. Try backup code #1 again
  → Should fail! If it succeeds → not invalidated after use!
  
ADDITIONAL TESTS:
  - Do backup codes have different rate limit than TOTP?
  - Can you generate unlimited new backup codes? (reset + get new ones)
  - Are backup codes hashed in the database?
    (If leaked/SQLi → unhashed backup codes = direct account access!)
```

---

## Fix

```
CORRECT IMPLEMENTATION:

TOTP — PREVENT REUSE:
  # Track used codes per user per time window:
  def verify_totp(user_id, code):
      window = current_time // 30
      # Check code is correct:
      if not pyotp.TOTP(user.totp_secret).verify(code): return False
      # Check this exact code+window wasn't used:
      if redis.get(f"totp_used:{user_id}:{window}:{code}"):
          return False  # Already used in this window!
      # Mark as used for this window:
      redis.setex(f"totp_used:{user_id}:{window}:{code}", 90, 1)
      return True

SMS/EMAIL OTP:
  - Invalidate immediately after successful use
  - Hard expiry (15 minutes maximum)
  - Only one active OTP at a time (issuing new one invalidates old)
  - Rate limit: max 5 OTPs per hour

BACKUP CODES:
  - Delete backup code from DB immediately after use
  - Store hashed (bcrypt/SHA256) not plaintext
  - Limit to 1 active set of backup codes
  - Require re-authentication to view/regenerate
```

---

## Related Notes
- [[11 - MFA Bypass Response Manipulation]] — response-based bypass
- [[13 - MFA Bypass Brute Force OTP]] — brute force the code
- [[14 - MFA Bypass Backup Code Abuse]] — abusing backup codes
