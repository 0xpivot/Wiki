---
tags: [vapt, access-control, idor, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.03 IDOR — Insecure Direct Object Reference"
portswigger_labs: ["IDOR vulnerability with direct reference to database IDs", "IDOR vulnerability with direct reference to static files"]
---

# 21.03 — IDOR: Insecure Direct Object Reference

## What Is IDOR?

```
IDOR = Insecure Direct Object Reference
OWASP Category: Broken Access Control (A01:2021 — #1!)

DEFINITION:
  App exposes a direct reference to an internal object (database ID, filename, etc.)
  And doesn't verify the caller is authorized to access THAT object
  
  "Direct reference" = the ID itself is exposed to the user
  vs. an indirect/abstracted reference
  
  EXAMPLES:
  /invoice/1234        ← 1234 is a direct DB reference
  /file?name=john.pdf  ← filename is a direct reference
  /api/user/42         ← 42 is a direct DB reference
  
  If you can change 1234 → 1235 → and see another user's invoice:
  → IDOR!
```

---

## Why IDOR Happens

```
DEVELOPER THOUGHT PROCESS (incorrect):
  "The user can only see links to THEIR own invoices"
  "I'll just show invoice #1234 when they click"
  "They don't know about invoice #1235, so they can't access it"
  
  REALITY:
  Users can modify URLs directly
  Users can use Burp Suite
  Users can guess/enumerate IDs
  → The UI not showing the link is NOT a security control!
  
  CORRECT APPROACH:
  "When user requests invoice #1234, verify in the database:
   Does the authenticated user OWN invoice #1234?"
  → Yes → serve it
  → No → 403 Forbidden
```

---

## IDOR in Different Data Locations

```
IDOR APPEARS IN MANY PLACES:
  
  1. URL PATH PARAMETER:
     GET /api/users/42/profile
     → Change 42 to other user IDs
  
  2. QUERY PARAMETER:
     GET /download?invoice_id=1234
     → Change invoice_id
  
  3. POST BODY:
     POST /messages/delete
     {"message_id": 5001}
     → Change message_id
  
  4. COOKIE:
     Cookie: user_id=42
     → Change to other user ID
  
  5. HTTP HEADERS:
     X-User-ID: 42
     → Change to other user ID
  
  6. INDIRECT (in response → use in next request):
     GET /api/orders → returns order IDs in response
     GET /api/orders/FOUND_ID → access ANY of those IDs
  
  (Covered in detail: notes 04-07 per location)
```

---

## Classic IDOR Examples

```
EXAMPLE 1: Invoice Access
  Logged in as user@example.com
  My invoices: GET /invoices?id=1001 → "Invoice $50 from Jan 2024"
  Try: GET /invoices?id=1000 → another user's invoice!
  Try: GET /invoices?id=1002 → another user's invoice!
  Enumerate: for id in range(1, 9999) → ALL invoices!

EXAMPLE 2: File Download
  GET /profile-pictures/john_doe.jpg   ← you know your own filename
  GET /profile-pictures/admin_user.jpg ← try admin's filename
  GET /profile-pictures/               ← directory listing? → ALL files!

EXAMPLE 3: API User Object
  GET /api/v1/user/ME → {id:42, email:you@example.com, role:"user"}
  GET /api/v1/user/1  → {id:1, email:admin@company.com, role:"admin"}
  → admin email exposed, password hash possibly too!

EXAMPLE 4: Password Reset
  POST /reset-password
  {"email": "you@example.com", "token": "abc123"}
  
  Change email:
  {"email": "admin@company.com", "token": "abc123"}
  → If token is valid for ANY user → reset anyone's password!
```

---

## Finding IDORs with Burp Suite

```
METHOD 1: MANUAL TESTING
  1. Browse as User A → note all IDs in requests/responses
  2. For each ID → try incrementing/decrementing
  3. Check if response contains another user's data

METHOD 2: BURP AUTORIZE EXTENSION (highly recommended!)
  1. Install: Burp → Extensions → BApp Store → Autorize
  2. Log in as User B (lower privilege) → get session cookie
  3. Paste User B's cookie into Autorize
  4. Log in as User A (higher privilege) → browse the app normally
  5. Autorize AUTOMATICALLY replays each request with User B's cookie
  6. Colors requests:
     GREEN: User B got same response → potential IDOR!
     RED: User B got different/error response → properly blocked
  
  → Review all GREEN requests!

METHOD 3: BURP INTRUDER FOR ENUMERATION
  1. Find endpoint: GET /api/orders/§1001§
  2. Send to Intruder → Sniper → Numbers payload (1001 → 9999)
  3. Filter by response length (different length = different user's data!)
  4. Or: filter by status code (200 = found, 403 = blocked)
```

---

## Fix

```
CORRECT IMPLEMENTATION:

# BAD (IDOR):
def get_document(doc_id):
    doc = db.query("SELECT * FROM documents WHERE id = ?", [doc_id])
    return doc

# GOOD (ownership check):
def get_document(doc_id, current_user_id):
    doc = db.query(
        "SELECT * FROM documents WHERE id = ? AND owner_id = ?",
        [doc_id, current_user_id]
    )
    if not doc:
        abort(403)  # Don't reveal if doc exists but belongs to someone else
    return doc

# For admin access (still needs explicit check):
def get_document(doc_id, current_user_id, is_admin):
    if is_admin:
        doc = db.query("SELECT * FROM documents WHERE id = ?", [doc_id])
    else:
        doc = db.query(
            "SELECT * FROM documents WHERE id = ? AND owner_id = ?",
            [doc_id, current_user_id]
        )
    if not doc:
        abort(404)  # Consistent 404 (don't differentiate not-found vs forbidden)
    return doc

GUIDANCE:
  Every data access must include the authenticated user's context
  Never trust client-supplied user IDs for authorization
  Return 404 for all unauthorized access (don't confirm object existence)
```

---

## IDOR Severity Assessment

```
SEVERITY DEPENDS ON IMPACT:

CRITICAL:
  - Account takeover via IDOR on reset/email-change endpoints
  - Access to admin-level data
  - Financial data (other users' payments, SSNs)
  - PII mass enumeration (all users' emails, names, etc.)

HIGH:
  - Read access to other users' sensitive content
  - Modify or delete other users' data

MEDIUM:
  - Read access to less-sensitive data
  - Leak of internal IDs but not sensitive data

LOW:
  - Internal IDs leaked but no meaningful data access
  - Predictable IDs but proper ownership check prevents access
```

---

## Related Notes
- [[04 - IDOR in URL Parameters]] — URL-based IDOR
- [[05 - IDOR in POST Body]] — body-based IDOR
- [[09 - BOLA — Broken Object Level Authorization (OWASP API #1)]] — API IDOR
- [[18 - Account Takeover via IDOR on Password Reset]] — high-impact IDOR
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
