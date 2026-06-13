---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.09 Forgot Password — Token Reuse"
portswigger_labs: ["Password reset broken logic"]
---

# 16.09 — Forgot Password: Token Reuse

## What Is Token Reuse?

```
MULTIPLE WAYS A TOKEN CAN BE REUSED:

1. TOKEN NOT INVALIDATED AFTER USE:
   - Use token → reset password
   - Try same token again → STILL WORKS!
   - Attacker who stole token can use it multiple times

2. TOKEN NOT TIED TO EMAIL/ACCOUNT:
   - Request reset for account A → get tokenA
   - Use tokenA in reset form for account B
   - → Resets account B's password!
   
3. OLD TOKENS NOT INVALIDATED ON NEW REQUEST:
   - Request reset → tokenA generated (email sent)
   - Request reset again → tokenB generated (new email)
   - Try tokenA anyway → STILL WORKS!
   - Old token should have been invalidated when new one was issued

4. TOKEN SURVIVES PASSWORD CHANGE:
   - User changes their password manually (not via reset)
   - Old reset token from before the change → still works!
```

---

## Testing Token Reuse

```
TEST 1 — Multi-use token:
  1. Request password reset for your test account
  2. Receive token via email
  3. Use token → reset password successfully
  4. Try the SAME token again
  5. → If it works again → VULNERABLE (not single-use)

TEST 2 — Token not tied to account:
  1. Request reset for account_a@test.com
  2. Receive token: abc123
  3. Go to reset page, change email parameter:
     GET /reset?token=abc123&email=victim@example.com
     OR: POST /reset { token: "abc123", email: "victim@example.com" }
  4. → If it resets victim's password → CRITICAL!

TEST 3 — Old token still valid:
  1. Request reset → token1 (save this)
  2. Wait a minute
  3. Request reset again → token2
  4. Try token1 from step 1
  5. → If token1 still works → old tokens not invalidated!

TEST 4 — Token survives password change:
  1. Request reset → token
  2. Instead of using reset link, login and change password manually
  3. Now try the reset token
  4. → If it resets your ALREADY-CHANGED password → token not cleared!
```

---

## Exploiting: Token Not Tied to Account

```http
NORMAL FLOW:
GET /reset-password?token=abc123&email=legitimate@example.com HTTP/1.1

ATTACK:
GET /reset-password?token=abc123&email=victim@example.com HTTP/1.1
                                  ↑ changed to victim's email!

OR POST FORM:
POST /reset-password HTTP/1.1
Content-Type: application/x-www-form-urlencoded

token=abc123&email=victim@example.com&new_password=Hacked1!

→ Server checks: is token abc123 valid?
  YES → resets... BUT WHOSE ACCOUNT?
  WRONG: resets whatever email is in the form!
  RIGHT: should only reset the account the token was issued for
```

---

## Fix

```
CORRECT TOKEN IMPLEMENTATION:

1. SINGLE USE:
   After successful use → DELETE or INVALIDATE the token in DB:
   
   # Python:
   db.execute("DELETE FROM password_resets WHERE token = ?", [token])
   # Or: UPDATE password_resets SET used = TRUE WHERE token = ?

2. TIE TOKEN TO ACCOUNT:
   Token lookup should return the user it was issued for:
   
   # Python — WRONG:
   user = db.fetch("SELECT user_id FROM resets WHERE token = ?", [token])
   # Then set password for user_id from FORM or URL parameter!
   
   # Python — RIGHT:
   reset = db.fetch("SELECT user_id FROM resets WHERE token = ? AND used = FALSE", [token])
   # Set password for reset.user_id (from DB, NOT from request!)
   # Never trust email/user_id from the request body!
   
3. INVALIDATE OLD TOKENS:
   When issuing new token, delete all previous tokens for that user:
   db.execute("DELETE FROM password_resets WHERE user_id = ?", [user_id])
   # Then insert new token
   
4. EXPIRE ON PASSWORD CHANGE:
   When user changes password (any method), clear all reset tokens:
   db.execute("DELETE FROM password_resets WHERE user_id = ?", [user_id])
```

---

## Related Notes
- [[07 - Forgot Password Token Predictability]] — randomness issues
- [[08 - Forgot Password Host Header Poisoning]] — link URL poisoning
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
