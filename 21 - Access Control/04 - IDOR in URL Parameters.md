---
tags: [vapt, access-control, idor, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.04 IDOR in URL Parameters"
---

# 21.04 — IDOR in URL Parameters

## URL Parameter IDOR Patterns

```
MOST VISIBLE FORM OF IDOR:
  The object reference is directly in the URL
  → Users can easily modify it → easy to test!
  
  PATTERNS:
  /api/users/42             ← path parameter (ID in path)
  /profile?user_id=42       ← query parameter (ID after ?)
  /orders/2024/10042        ← multiple path parameters
  /files/reports/q4-2024.pdf ← filename as reference
```

---

## Path Parameter IDOR

```
EXAMPLES:
  GET /api/users/42/profile
  GET /api/users/42/orders
  GET /api/accounts/ACC-001/transactions
  DELETE /api/posts/1234
  PUT /api/documents/5678
  
  TESTING:
  Change the ID segment:
  /api/users/42/profile → /api/users/43/profile
  /api/users/42/profile → /api/users/1/profile  (admin?)
  /api/users/42/profile → /api/users/0/profile  (edge case)
  /api/users/42/profile → /api/users/99999/profile (non-existent)
  
  ALSO TEST METHODS:
  GET /api/posts/1234      → another user's post?
  DELETE /api/posts/1234   → delete another user's post?
  PUT /api/posts/1234      → modify another user's post?
  
  → Each HTTP method may have its own access control (or lack thereof!)
```

---

## Query Parameter IDOR

```
EXAMPLES:
  GET /profile?id=42
  GET /invoice?invoice_id=10042
  GET /download?doc=report.pdf
  GET /messages?thread=8891
  
  TESTING:
  Intercept in Burp → change parameter value:
  id=42 → id=1 (admin?), id=43 (next user)
  invoice_id=10042 → invoice_id=10041
  
  FINDING QUERY PARAMETER IDORs:
  Burp Proxy History → filter for requests with numeric params
  
  AUTOMATE:
  # Burp Intruder (Sniper mode):
  GET /invoice?id=§10042§
  Payload: Numbers from 10001 to 11000
  Filter: content-length != baseline → found IDOR!
```

---

## Filename/Indirect Reference IDOR

```
FILES AS REFERENCES:
  GET /uploads/invoice_john.pdf
  GET /reports/2024-q4-admin.pdf
  GET /exports/user_data_42.csv
  
  TESTING:
  Predict other filenames:
  → Replace username: john → admin, jane, bob...
  → Replace year: 2024 → 2023, 2022...
  → Replace ID: 42 → 1, 43, 100...
  
  IF DIRECTORY LISTING ENABLED:
  GET /uploads/ → lists all files → BIG BUG!
  GET /exports/ → all user data exports visible!
  
  FUZZING FILENAMES:
  feroxbuster -u https://target.com/uploads/ \
    -w /usr/share/wordlists/SecLists/Usernames/Names/names.txt \
    --status-codes 200
```

---

## Response-Embedded IDs

```
SECOND-ORDER IDOR:
  You make one request → response contains IDs you shouldn't know
  You use those IDs in another request
  
  EXAMPLE:
  GET /api/dashboard →
  {
    "user_id": 42,
    "connected_accounts": [101, 102, 103],   ← other account IDs?
    "shared_docs": [5001, 5002]               ← doc IDs?
  }
  
  GET /api/accounts/101 → another user's account data!
  
  TESTING:
  Extract ALL IDs from API responses
  Try each ID against every endpoint
  → Sometimes IDs from response B unlock content at endpoint C
```

---

## Testing with Burp Suite Intruder

```
SYSTEMATIC ID ENUMERATION:

1. IDENTIFY THE ENDPOINT:
   GET /api/invoices/§10042§ HTTP/1.1

2. SEND TO INTRUDER:
   Right-click → Send to Intruder

3. CONFIGURE PAYLOAD:
   Positions: §10042§
   Payload type: Numbers
   From: 10000, To: 10100, Step: 1

4. RUN AND FILTER RESULTS:
   After running, sort by:
   - Status Code (200 = found, 403 = blocked)
   - Content Length (different length = different content)
   
   Response length differs from "not found" response → IDOR!

5. COMPARE RESPONSES:
   View responses → is it another user's invoice?

BURP AUTORIZE (easier for testing from two accounts):
  Note 03 covers Autorize setup
```

---

## Fix

```
SECURE ENDPOINT IMPLEMENTATION:

# Flask example — always include user context:
from flask import session, abort, jsonify, request

@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
@require_login
def get_invoice(invoice_id):
    user_id = session['user_id']
    
    invoice = db.execute(
        "SELECT * FROM invoices WHERE id = ? AND user_id = ?",
        [invoice_id, user_id]
    ).fetchone()
    
    if not invoice:
        abort(404)  # use 404 (not 403) to avoid confirming existence
    
    return jsonify(invoice)

# For admins who legitimately need to see any invoice:
@app.route('/admin/invoices/<int:invoice_id>', methods=['GET'])
@require_admin
def admin_get_invoice(invoice_id):
    invoice = db.execute(
        "SELECT * FROM invoices WHERE id = ?",
        [invoice_id]
    ).fetchone()
    
    if not invoice:
        abort(404)
    
    return jsonify(invoice)
```

---

## Related Notes
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR overview
- [[05 - IDOR in POST Body]] — IDOR in request body
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
