---
tags: [vapt, access-control, idor, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.05 IDOR in POST Body"
---

# 21.05 — IDOR in POST Body

## POST Body IDOR

```
MANY ACTIONS USE POST REQUESTS:
  Creating, updating, deleting resources
  Object IDs often in the request BODY (not URL)
  
  JSON BODY:
  POST /api/messages/delete
  Content-Type: application/json
  {"message_id": 5001}
  
  FORM-ENCODED:
  POST /update-profile
  Content-Type: application/x-www-form-urlencoded
  user_id=42&name=John&email=john@example.com
  
  ATTACK:
  Change message_id: 5001 → 5000 → delete another user's message!
  Change user_id: 42 → 1 → update admin's profile!
```

---

## Common POST Body IDOR Patterns

```
PATTERN 1: Delete operations
  POST /api/comments/delete
  {"comment_id": 1234}
  → Change comment_id → delete other users' comments!

PATTERN 2: Update operations
  POST /api/orders/update
  {"order_id": 9999, "status": "delivered"}
  → Change order_id → update other users' orders!
  
  OR:
  POST /api/user/update
  {"user_id": 42, "email": "new@email.com"}
  → Change user_id → modify other users' emails!

PATTERN 3: Share/grant access
  POST /api/documents/share
  {"doc_id": 5001, "share_with": "attacker@evil.com"}
  → Share another user's document with yourself!

PATTERN 4: Payment/order operations
  POST /api/apply-discount
  {"order_id": 10001, "code": "SAVE10"}
  → Apply discount to another user's order?
  → Or: see another user's order total?

PATTERN 5: Transfer operations
  POST /api/transfer
  {"from_account": 1001, "to_account": ATTACKER_ACCOUNT, "amount": 1000}
  → Transfer FROM another user's account!
```

---

## Testing POST Body IDOR

```bash
# STEP 1: IDENTIFY POST REQUESTS WITH OBJECT IDs IN BODY
# In Burp Proxy History:
# Filter: Method = POST
# Look for requests with: id, user_id, account_id, doc_id, etc. in body

# STEP 2: SEND TO REPEATER
# Right-click → Send to Repeater (Ctrl+R)

# STEP 3: MODIFY IDs:
# JSON body:
# Original: {"message_id": 5001}
# Modified: {"message_id": 5000}

# STEP 4: COMPARE RESPONSES:
# Different user's data returned? → IDOR!
# "Access denied" or same user's data → properly controlled

# STEP 5: TEST ALL RELEVANT OPERATIONS:
# GET, POST, PUT, PATCH, DELETE
# Each operation may have its own (absent) access control!

# STEP 6: MASS TESTING WITH INTRUDER:
# Identify numeric ID in JSON body
# Send to Intruder:
# Payload position: "message_id": §5001§
# Payload: Numbers 5000-5100
# Filter by length → find hits!

# ALSO TEST:
# MISSING id in body → does server use session user ID? (correct!)
#                      or return all records? (IDOR!)
POST /api/messages/delete
{}  ← no message_id
→ Returns error? Good. Returns something? Bug!
```

---

## JSON vs Form-Encoded Body IDOR

```
SAME VULNERABILITY, DIFFERENT FORMAT:

JSON:
  POST /api/update
  Content-Type: application/json
  {"user_id": 42, "name": "John"}
  → Try: {"user_id": 1, "name": "Hacked"}

FORM-ENCODED:
  POST /update-profile
  Content-Type: application/x-www-form-urlencoded
  user_id=42&name=John
  → Try: user_id=1&name=Hacked

XML (less common):
  POST /api/update
  Content-Type: text/xml
  <request><user_id>42</user_id><name>John</name></request>
  → Try: <user_id>1</user_id>

CONTENT-TYPE BYPASS:
  Some apps only check body format for one content type
  Try switching content type:
  JSON endpoint → send as form-encoded
  → Server might parse differently → bypass validation!
```

---

## Second-Order IDOR via POST

```
ADVANCED PATTERN:
  POST /api/send-invoice → queues sending to user_id stored in session
  
  But what if the invoice is created with:
  POST /api/create-invoice
  {"recipient_id": 43, "amount": 1000}
  
  Then:
  POST /api/send-invoice
  {"invoice_id": [last created invoice ID]}
  
  → Sends invoice to user 43 (charges them?) → unintended!
  → Or: recipient_id not validated at creation time
  
  ANOTHER PATTERN:
  POST /api/export-data
  {"user_id": 43}
  → Schedules data export for user 43?
  → Export result accessible to attacker?
```

---

## Fix

```
SECURE POST ENDPOINT:

# BAD — trusts user_id from body:
@app.route('/api/messages/delete', methods=['POST'])
def delete_message():
    data = request.get_json()
    message_id = data['message_id']
    db.delete("DELETE FROM messages WHERE id = ?", [message_id])  # WRONG!
    return jsonify({"status": "deleted"})

# GOOD — validates ownership using session:
@app.route('/api/messages/delete', methods=['POST'])
@require_login
def delete_message():
    user_id = session['user_id']
    data = request.get_json()
    
    # Ensure message_id is provided and is an integer:
    try:
        message_id = int(data['message_id'])
    except (KeyError, ValueError):
        abort(400, "Invalid message_id")
    
    # Delete ONLY if user owns the message:
    result = db.execute(
        "DELETE FROM messages WHERE id = ? AND user_id = ?",
        [message_id, user_id]
    )
    
    if result.rowcount == 0:
        abort(404)  # Either doesn't exist or doesn't belong to user
    
    return jsonify({"status": "deleted"})

# NEVER accept user_id from body for user-specific operations:
# If operation is for "current user" → get user_id from SESSION only!
```

---

## Related Notes
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR overview
- [[04 - IDOR in URL Parameters]] — URL IDOR
- [[06 - IDOR in Cookies]] — cookie-based IDOR
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
