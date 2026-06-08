---
tags: [vapt, access-control, defense]
difficulty: intermediate
module: "21 - Access Control"
topic: "21.20 Defense — Server-Side Authorization, Object-Level Checks"
---

# 21.20 — Defense: Server-Side Authorization, Object-Level Checks

## Complete Access Control Security Checklist

```
AUTHENTICATION (who you are):
  □ Every protected endpoint checks authentication
  □ Session/token validation before any business logic
  □ Consistent 401 for unauthenticated requests

FUNCTION-LEVEL (can you use this function?):
  □ Admin endpoints require admin role (server-side check)
  □ Role checked from session/JWT (NEVER from request params)
  □ HTTP methods: each method independently authorized
  □ API versions: same authorization across all versions
  □ Default DENY — explicitly grant access, don't block

OBJECT-LEVEL (can you access this SPECIFIC object?):
  □ All DB queries include user_id/tenant_id filter
  □ Ownership verified before any read/write/delete
  □ IDs cannot be swapped between users
  □ File access validated against allowed paths

DATA LEAKAGE (what you return):
  □ Response fields filtered to only what caller needs
  □ Sensitive fields not returned to low-privilege users
  □ Separate serialization schemas per role
  □ No internal IDs leaking that enable further IDOR

PARAMETER TRUST:
  □ Role/permission from session, not request body
  □ Price/discount from DB, not client
  □ User ID from session, not URL/body/cookie
  □ No mass assignment vulnerabilities

HEADERS:
  □ Referer header NOT used for access control
  □ X-Forwarded-For NOT used for security decisions
  □ X-Original-URL / X-Rewrite-URL rejected or validated
  □ X-User-ID type headers only from trusted internal sources

GRAPHQL:
  □ Field-level authorization on each resolver
  □ Introspection disabled in production
  □ Batching limited or monitored
  □ Depth limiting enabled

TESTING:
  □ Two-account horizontal escalation tests
  □ Role escalation tests (regular → admin)
  □ IDOR testing on all resource endpoints
  □ Burp Autorize extension used for automated testing
```

---

## Core Authorization Pattern

```python
# THE GOLDEN PATTERN:
# 1. Authenticate (who are you?)
# 2. Authorize (are you allowed to do THIS to THIS object?)
# 3. Fetch (get the data)
# 4. Return (only what they need)

from flask import session, abort, jsonify
from functools import wraps

# Step 1: Authentication middleware
def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            abort(401, "Authentication required")
        return f(*args, **kwargs)
    return decorated

# Step 2a: Function-level authorization
def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()  # from server-side session
            if user.role != required_role:
                abort(403, "Insufficient permissions")
            return f(*args, **kwargs)
        return decorator
    return decorator

# Step 2b: Object-level authorization (INLINE in handler)
@app.route('/api/orders/<int:order_id>')
@require_login
def get_order(order_id):
    current_user_id = session['user_id']
    
    # Fetch WITH ownership check:
    order = db.execute(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        [order_id, current_user_id]
    ).fetchone()
    
    if not order:
        abort(404)  # Don't reveal: not found vs unauthorized
    
    # Step 4: Return only what they need:
    return jsonify({
        "id": order["id"],
        "items": order["items"],
        "total": order["total"],
        "created_at": order["created_at"]
        # NOT: order["payment_method"], order["internal_notes"], etc.
    })

# Admin can see any order:
@app.route('/admin/orders/<int:order_id>')
@require_login
@require_role('admin')
def admin_get_order(order_id):
    order = db.execute("SELECT * FROM orders WHERE id = ?", [order_id]).fetchone()
    if not order:
        abort(404)
    return jsonify(order)  # Admin gets full object
```

---

## Database Query Patterns

```sql
-- ALWAYS INCLUDE USER CONTEXT IN QUERIES:

-- BAD: Fetches any row with matching id:
SELECT * FROM documents WHERE id = ?

-- GOOD: Verifies ownership:
SELECT * FROM documents WHERE id = ? AND user_id = ?

-- FOR MULTI-TENANT APPS (tenant isolation):
SELECT * FROM documents WHERE id = ? AND tenant_id = ? AND user_id = ?

-- DELETE with ownership:
DELETE FROM comments WHERE id = ? AND user_id = ?
-- If rowcount=0 → either doesn't exist OR not owned → return 404!

-- UPDATE with ownership:
UPDATE documents SET title = ? WHERE id = ? AND user_id = ?
-- rowcount=0 → document not found/not owned

-- ADMIN QUERY (all rows, no user filter):
-- Only in admin context (separate function, admin role checked!)
SELECT * FROM documents WHERE id = ?
```

---

## Response Serialization by Role

```python
# DIFFERENT VIEWS OF THE SAME MODEL:

class UserModel:
    id: int
    name: str
    email: str
    password_hash: str    # NEVER return!
    api_key: str          # Return to owner only
    role: str             # Return to admin only
    internal_notes: str   # Return to admin only
    created_at: datetime

# Pydantic schemas for different contexts:
from pydantic import BaseModel

class UserPublicView(BaseModel):
    id: int
    name: str
    # No email, no api_key, no role, no notes

class UserOwnView(BaseModel):
    id: int
    name: str
    email: str
    api_key: str        # owner can see their own key
    created_at: datetime

class UserAdminView(BaseModel):
    id: int
    name: str
    email: str
    role: str
    internal_notes: str
    created_at: datetime
    # Still no password_hash!

# In the handler:
def get_user(user_id, requesting_user):
    user = db.get_user(user_id)
    
    if requesting_user.role == 'admin':
        return UserAdminView.from_orm(user)
    elif requesting_user.id == user_id:
        return UserOwnView.from_orm(user)
    else:
        return UserPublicView.from_orm(user)
```

---

## Automated Testing with Burp Autorize

```
SETTING UP AUTORIZE FOR IDOR TESTING:

1. INSTALL:
   Burp → Extensions → BApp Store → Autorize → Install

2. CONFIGURE:
   Autorize tab → add "Unauthenticated" config:
   - Remove Authorization header
   - Remove session cookie
   
   Add "Low-privilege user" config:
   - Set Authorization header to regular user's token
   - OR: set cookie to regular user's session

3. START:
   Click "Intercept is on" in Autorize

4. BROWSE AS HIGH-PRIVILEGE USER (admin):
   All requests go through Autorize
   Autorize replays each with low-privilege credentials
   Colors results:
   GREEN: Same response → potential IDOR!
   RED: Different response (403 etc.) → properly blocked!
   YELLOW: Content-length same but slightly different

5. REVIEW GREEN ITEMS:
   For each green → compare responses
   Sensitive data visible to low-privilege? → IDOR confirmed!
```

---

## Penetration Testing Checklist

```
TEST CHECKLIST FOR ACCESS CONTROL:

VERTICAL ESCALATION:
  □ Access admin endpoints as regular user → should be 403
  □ Try role parameter tampering (role=admin in body/cookie)
  □ Try JWT claim modification (role claim)
  □ Try mass assignment (is_admin=true in registration)
  □ Try HTTP method switching on admin endpoints
  □ Try path traversal variants (/ADMIN, /admin/../admin)
  □ Try Referer header bypass

HORIZONTAL ESCALATION (IDOR):
  □ Test all resource endpoints with two accounts
  □ Enumerate IDs (sequential integers → try adjacent)
  □ Change IDs in URL, body, cookies, headers
  □ Test all HTTP methods (GET, POST, PUT, DELETE, PATCH)
  □ Use Burp Autorize for systematic testing

API-SPECIFIC:
  □ Test all API versions (v1, v2, etc.)
  □ Test admin API endpoints as regular user
  □ Test GraphQL field access and mutations
  □ Check response for over-exposed fields

DATA LEAKAGE:
  □ Check API responses for sensitive fields (password_hash, api_key)
  □ Check if responses include other users' IDs
  □ Check error messages for information disclosure
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — admin access
- [[02 - Horizontal Privilege Escalation]] — cross-user access
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR fundamentals
- [[09 - BOLA — Broken Object Level Authorization (OWASP API #1)]] — API BOLA
- [[16 - GraphQL Authorization Bypass]] — GraphQL auth
