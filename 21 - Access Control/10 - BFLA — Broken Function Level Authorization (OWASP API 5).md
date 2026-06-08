---
tags: [vapt, access-control, api, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.10 BFLA — Broken Function Level Authorization (OWASP API #5)"
---

# 21.10 — BFLA: Broken Function Level Authorization (OWASP API #5)

## BOLA vs BFLA

```
BOLA (API1):  "Can I access OTHER USERS' objects?"
              User → accesses another user's /orders/ID → wrong user's data
              Object-level: the OBJECT belongs to wrong person
              
BFLA (API5):  "Can I call ADMIN FUNCTIONS I shouldn't have access to?"
              Regular user → calls /admin/delete-user → privilege escalation
              Function-level: the FUNCTION requires higher privilege

BFLA = Vertical Privilege Escalation at API function level
BOLA = Horizontal Privilege Escalation at API object level
```

---

## BFLA Attack Patterns

```
PATTERN 1: ADMIN ENDPOINTS ACCESSIBLE TO REGULAR USERS
  Normal user endpoint: GET /api/v1/users/me
  Admin endpoint:       GET /api/v1/admin/users → lists all users!
  
  Regular user has valid session → hits admin endpoint → works!
  
PATTERN 2: HTTP METHOD ESCALATION
  GET /api/v1/users/42 → read user (allowed for regular users)
  DELETE /api/v1/users/42 → delete user (admin-only)
  
  Regular user → DELETE request → server doesn't check method-level permission → success!
  
PATTERN 3: VERSION-BASED BYPASS
  API v2: GET /api/v2/admin/users → properly protected (403)
  API v1: GET /api/v1/admin/users → old version, no auth check → BFLA!
  
  Legacy API versions often have weaker controls!
  
PATTERN 4: UNDOCUMENTED ENDPOINTS
  App has: /api/users/me, /api/orders
  Hidden: /api/users/all, /api/admin/export, /api/debug
  → Test undocumented paths → might be unprotected!
```

---

## Finding BFLA Vulnerabilities

```bash
# STEP 1: IDENTIFY ADMIN/HIGH-PRIVILEGE API FUNCTIONS:
# From API documentation (if available):
curl https://api.target.com/swagger.json | python3 -m json.tool | grep -E '"path"|operationId'
# Look for: /admin, /management, /internal, /users (plural)

# From API responses (admin actions visible in UI but restricted?):
# Watch Burp Proxy when logged in as admin
# Note endpoints only admin uses

# STEP 2: MAP PRIVILEGE LEVELS:
# What can regular users do?
# What can admins do?
# Are there other roles? (manager, moderator, billing)

# STEP 3: TEST ADMIN ENDPOINTS AS REGULAR USER:
# Switch to regular user session → try admin endpoints:
curl -H "Authorization: Bearer REGULAR_USER_TOKEN" \
  https://api.target.com/api/v1/admin/users
# → 200 → BFLA!

# STEP 4: TEST ALL HTTP METHODS:
for METHOD in GET POST PUT DELETE PATCH; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X $METHOD \
    -H "Authorization: Bearer REGULAR_TOKEN" \
    https://api.target.com/api/v1/users)
  echo "$METHOD: $code"
done
# POST 200 where only GET should work → BFLA!

# STEP 5: TEST API VERSION ENDPOINTS:
BASE_URL="https://api.target.com"
for VERSION in v1 v2 v3 v4 v0; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer REGULAR_TOKEN" \
    "$BASE_URL/api/$VERSION/admin/users")
  echo "v$VERSION admin/users: $code"
done
# Old versions might not have access controls

# STEP 6: ENUMERATE UNDOCUMENTED PATHS:
feroxbuster -u https://api.target.com/api/v1 \
  -w /usr/share/wordlists/SecLists/Discovery/Web-Content/api/api-endpoints-res.txt \
  -H "Authorization: Bearer REGULAR_TOKEN" \
  --status-codes 200,201,204
```

---

## BFLA via Parameter-Based Function Selection

```
SOME APIS USE PARAMETERS TO SELECT FUNCTIONS:
  POST /api/action
  {"action": "get_profile"}
  
  What other "action" values exist?
  {"action": "get_all_users"}
  {"action": "delete_user"}
  {"action": "make_admin"}
  {"action": "export_database"}
  
  → Server routes to different functions based on "action" value
  → If no role check on function level → BFLA via action parameter!
  
  ALSO:
  GET /api/reports?type=user_report
  Try: ?type=all_users_report, ?type=admin_report, ?type=system_logs
  
  POST /api/export?format=csv&data=my_orders
  Try: ?data=all_orders, ?data=all_users
```

---

## Fix

```
FUNCTION-LEVEL AUTHORIZATION:

PRINCIPLE: Every function must check caller's role/permission
  NOT just: "Is user logged in?" (authentication)
  BUT:      "Is this user ALLOWED to call THIS function?" (authorization)

# PYTHON FLASK — Role-based decorator:
from functools import wraps
from flask import session, abort

def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                abort(401)
            if user.role != role and not user.has_permission(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

# Apply to each admin endpoint:
@app.route('/api/v1/admin/users', methods=['GET'])
@require_role('admin')
def list_all_users():
    return jsonify(db.get_all_users())

@app.route('/api/v1/admin/users/<int:user_id>', methods=['DELETE'])
@require_role('admin')
def delete_user(user_id):
    db.delete_user(user_id)
    return jsonify({"status": "deleted"})

# Node.js Express — Middleware approach:
const requireAdmin = (req, res, next) => {
    if (!req.user || req.user.role !== 'admin') {
        return res.status(403).json({error: 'Admin access required'});
    }
    next();
};

router.get('/admin/users', authenticate, requireAdmin, listUsers);
router.delete('/admin/users/:id', authenticate, requireAdmin, deleteUser);

DENY BY DEFAULT:
  All API endpoints → 403 by default
  Explicitly grant access to specific roles
  Never use "hide it" as security!
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — same concept in web apps
- [[09 - BOLA — Broken Object Level Authorization (OWASP API #1)]] — object-level API auth
- [[11 - Forced Browsing / Unprotected Admin Endpoints]] — finding hidden endpoints
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
