---
tags: [vapt, access-control, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.02 Horizontal Privilege Escalation"
portswigger_labs: ["User ID controlled by request parameter"]
---

# 21.02 — Horizontal Privilege Escalation

## What Is Horizontal Privilege Escalation?

```
HORIZONTAL ESCALATION:
  Accessing resources owned by OTHER users at the SAME privilege level
  
  Example:
  You are User #42 (regular user)
  You access User #43's data (also regular user)
  → Same privilege level, different user → HORIZONTAL!
  
  VS VERTICAL:
  You are User #42 (regular user)
  You access Admin panel (higher privilege) → VERTICAL!
  
  COMMON FORMS:
  - Accessing another user's account settings
  - Viewing another user's orders, messages, documents
  - Modifying or deleting another user's data
  - Resetting another user's password
  
  IMPACT: Data breach, account takeover, privacy violation
```

---

## The Core Problem: Predictable or User-Controlled IDs

```
VULNERABLE PATTERN:
  GET /user/42/profile   → you are user 42
  
  Try: GET /user/43/profile → if it works → IDOR!
  
  The ID (42, 43) is:
  - Predictable (sequential integers)
  - User-controlled (in URL, body, or cookie)
  - Not validated against session
  
  SERVER SHOULD CHECK:
  "Is the authenticated user (from session) authorized to access user ID 43?"
  → If user 42 → deny!
  → If admin → allow!
```

---

## Common Attack Scenarios

```
SCENARIO 1: Direct URL manipulation
  GET /account?id=42         ← your account
  GET /account?id=43         ← someone else's account
  → Check response → other user's data? → HORIZONTAL ESCALATION!

SCENARIO 2: Order/invoice access
  GET /orders/10042          ← your order
  GET /orders/10041          ← another user's order
  → Shows order details? → BUG!

SCENARIO 3: File download
  GET /download?file_id=5001  ← your document
  GET /download?file_id=5000  ← another user's document
  → Triggers download? → BUG!

SCENARIO 4: API response contains other users' data
  GET /api/messages → returns YOUR messages
  GET /api/messages?user_id=OTHER → returns THEIR messages
  → OR: GET /api/messages/123 (message ID 123 owned by another)

SCENARIO 5: Password reset targeting another user
  POST /reset-password
  {"user_id": 43, "password": "newpassword"}
  → Resets user 43's password? → ACCOUNT TAKEOVER via HORIZONTAL!
```

---

## Testing Horizontal Escalation

```bash
# STEP 1: IDENTIFY USER-SPECIFIC ENDPOINTS:
# Look for URLs with IDs, usernames in Burp history:
# /users/42/profile, /api/orders/10042, /messages?to=john@email.com

# STEP 2: CREATE TWO TEST ACCOUNTS:
# Account A: victim account (your "victim" in testing)
# Account B: attacker account (what you test from)

# STEP 3: WITH ACCOUNT A — NOTE ALL IDs:
# Profile ID, order IDs, message IDs, document IDs, etc.

# STEP 4: WITH ACCOUNT B — TRY TO ACCESS ACCOUNT A'S RESOURCES:
# Swap Account B's ID for Account A's ID in each request

# BURP APPROACH:
# 1. Log in as Account B
# 2. Open BURP REPEATER
# 3. Paste request with Account A's ID in any identifier field
# 4. Forward → 200 response with Account A's data? → BUG!

# AUTOMATED APPROACH — Burp Autorize extension:
# 1. Log in as Account A → browse site → generate history
# 2. Configure Autorize with Account B's session token
# 3. Autorize replays every request from Account A's session
#    using Account B's credentials
# 4. Marks any requests that returned same data → possible IDOR!

# STEP 5: CHECK FOR ENUMERABLE IDs:
# Sequential integers: try id-1, id+1, id+100
# UUIDs: less enumerable but still test if any ID provides access
```

---

## When IDs Are Non-Predictable (UUIDs)

```
SOME APPS USE UUIDs:
  /documents/a3f8b7c2-4e6d-4f9a-b8c1-d2e5f6a7b8c9
  
  UUIDs are hard to guess → but:
  
  1. ARE THEY TRULY RANDOM?
     Some UUIDs include timestamp (UUID v1) → partially guessable!
     UUID v4 → truly random → much harder
     
  2. DO THEY APPEAR ANYWHERE?
     UUID in Referer header when sharing documents
     UUID in email "share" links → if email forwarded → exposed
     UUID in response from another endpoint → leak!
     
  3. DOES ENDPOINT ACCEPT ANY ID?
     Even with UUID, endpoint must validate ownership
     PUT /documents/RANDOM_UUID {"content": "..."} → updates document
     If UUID guessed/leaked → attacker can modify it!
     
  TESTING:
  Focus on endpoints where UUIDs might appear in other responses
  Try GUIDs from one endpoint in requests to another
```

---

## Fix

```
CORRECT AUTHORIZATION — CHECK OWNERSHIP EVERY TIME:

# BAD:
@app.route('/api/orders/<int:order_id>')
def get_order(order_id):
    order = db.get_order(order_id)  # WRONG: any order!
    return jsonify(order)

# GOOD:
@app.route('/api/orders/<int:order_id>')
@require_login
def get_order(order_id):
    user_id = session['user_id']
    order = db.get_order_for_user(order_id, user_id)  # ← must match!
    if not order:
        abort(403)  # or 404 to not reveal existence
    return jsonify(order)

# Database query that enforces ownership:
# SELECT * FROM orders WHERE id = ? AND user_id = ?
# → Returns nothing if order doesn't belong to this user!

PRINCIPLE: 
  Never fetch by ID alone — always include authenticated user's ID
  Any "not found" returns 403 or 404 (never reveal ownership)
  
USE UUIDs FOR IDs IN RESPONSES:
  Makes enumeration harder (still need ownership checks!)
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — higher privilege escalation
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR details
- [[04 - IDOR in URL Parameters]] — specific IDOR patterns
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
