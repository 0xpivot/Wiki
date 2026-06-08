---
tags: [vapt, access-control, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.13 HTTP Method Bypass (GET vs POST vs PUT)"
---

# 21.13 — HTTP Method Bypass (GET vs POST vs PUT)

## The Method Bypass Idea

```
APPS OFTEN CHECK ACCESS CONTROL PER HTTP METHOD:
  GET /admin/users → requires admin role → 403 for regular users
  
  BUT: POST /admin/users → has no access control check?
  
  Some apps apply access control only to specific methods:
  "Protected GET" but forgot "Protected POST"
  
  THIS HAPPENS BECAUSE:
  Developers think: "This is a read endpoint, I'll protect the read"
  Forget: the same URL with POST might write data!
  
  OR: Framework route definition issues:
  @app.route('/admin/users', methods=['GET'])  ← protected
  @app.route('/admin/users', methods=['POST']) ← forgot to protect!
```

---

## HTTP Method Override Headers

```
SOME FRAMEWORKS SUPPORT METHOD OVERRIDE:
  HTML forms only support GET and POST
  
  Workarounds to simulate DELETE, PUT from forms:
  - X-HTTP-Method-Override: DELETE
  - X-Method-Override: DELETE  
  - _method=DELETE (form field)
  
  SERVER PROCESSES BASED ON OVERRIDE, NOT ACTUAL METHOD:
  POST /admin/users/42 HTTP/1.1
  X-HTTP-Method-Override: DELETE
  
  → Server sees: "DELETE request to /admin/users/42"
  → Executes delete logic!
  
  BYPASS SCENARIO:
  DELETE /admin/users/42 → properly protected (checks admin role)
  POST /admin/users/42 with X-HTTP-Method-Override: DELETE → no check!
  
  WHY: Access control checked on original HTTP method (POST)
  But server processes as DELETE method (via override)
```

---

## Testing Method-Based Access Control

```bash
# BASELINE: What does the endpoint return for each method?
TARGET="https://target.com/admin/users"
BASE_COOKIE="session=REGULAR_USER_SESSION"

for METHOD in GET POST PUT DELETE PATCH HEAD OPTIONS TRACE; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X "$METHOD" \
    -b "$BASE_COOKIE" \
    "$TARGET")
  echo "$METHOD: $CODE"
done

# Example output:
# GET: 403    ← blocked (correct)
# POST: 200   ← NOT blocked (bug!)
# PUT: 403
# DELETE: 403
# PATCH: 200  ← NOT blocked (bug!)

# TEST METHOD OVERRIDE HEADERS:
for OVERRIDE in DELETE PUT PATCH; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "X-HTTP-Method-Override: $OVERRIDE" \
    -H "X-Method-Override: $OVERRIDE" \
    -d "_method=$OVERRIDE" \
    -b "$BASE_COOKIE" \
    "$TARGET/42")
  echo "POST with override $OVERRIDE: $CODE"
done

# ALSO TEST:
# Content-Type manipulation (JSON vs form — might hit different code paths)
curl -X POST "$TARGET" \
  -b "$BASE_COOKIE" \
  -H "Content-Type: application/json" \
  -d '{"action": "list_all"}'

curl -X POST "$TARGET" \
  -b "$BASE_COOKIE" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "action=list_all"
```

---

## HEAD Method for Recon

```
HEAD METHOD = GET but no response body:
  GET /admin/users → 403 Forbidden (body: "Access Denied")
  HEAD /admin/users → ??? 
  
  INFORMATION FROM HEAD:
  → Status code (200 vs 403)
  → Content-Length (200 with data vs 200 with error)
  → Response headers (content-type, x-powered-by, etc.)
  
  IF HEAD RETURNS 200 WHILE GET RETURNS 403:
  → Access control only on GET body, not HEAD method
  → Content-Length might reveal size of data you'd get as admin!
  
  ALSO: Some endpoints that "just return headers" have fewer checks
  
  TEST:
  HEAD /admin/users
  HEAD /admin/export-data
  HEAD /api/internal/stats
```

---

## TRACE Method Information Disclosure

```
HTTP TRACE:
  Server echoes the request back in the response
  Designed for debugging
  
  RISK:
  XST (Cross-Site Tracing):
  JavaScript can't read HttpOnly cookies normally
  But: TRACE echoes ALL headers including Cookie!
  → XSS + TRACE = read HttpOnly cookies via JavaScript!
  
  (Modern browsers block cross-origin TRACE, mitigating this)
  
  BUT: TRACE on same origin still leaks:
  - Authorization headers
  - Internal proxy headers
  - Custom authentication headers
  
  TEST:
  curl -X TRACE https://target.com/ -v
  
  FIX: Disable TRACE in webserver:
  # Apache: TraceEnable Off
  # Nginx: Handled by limiting methods
  location / {
    limit_except GET POST { deny all; }
  }
```

---

## OPTIONS Method Enumeration

```
OPTIONS METHOD:
  Returns what HTTP methods are allowed on an endpoint
  
  curl -X OPTIONS https://target.com/admin/users -v
  HTTP/1.1 200 OK
  Allow: GET, POST, PUT, DELETE, OPTIONS
  
  → Tells you what the server supports!
  → Good recon: know which methods to test
  
  ALSO: CORS preflight uses OPTIONS
  → Check CORS headers too (see CORS module)
  
  FINDINGS:
  If TRACE or CONNECT in Allow header → test those methods
  If more methods than expected → test unexpected ones for access control gaps
```

---

## Fix

```
METHOD-LEVEL ACCESS CONTROL:

APPLY ACCESS CONTROL INDEPENDENT OF METHOD:
  # BAD: Only protecting GET
  @app.route('/admin/users', methods=['GET'])
  @require_admin
  def list_admin_users():
      return jsonify(db.get_all_users())
  
  @app.route('/admin/users', methods=['POST'])  # UNPROTECTED!
  def create_user():
      return jsonify(db.create_user(request.json))
  
  # GOOD: Protect ALL methods
  @app.route('/admin/users', methods=['GET', 'POST'])
  @require_admin  # ← applies to ALL methods
  def admin_users():
      if request.method == 'GET':
          return jsonify(db.get_all_users())
      elif request.method == 'POST':
          return jsonify(db.create_user(request.json))

DISABLE METHOD OVERRIDE IF NOT NEEDED:
  # If app doesn't need override, disable it:
  # Rails: config.action_dispatch.perform_deep_munge = false
  # Express: don't use method-override middleware
  # If needed: still check authorization AFTER override resolution

ALLOWLIST METHODS:
  # Only allow methods you actually support:
  # Nginx:
  if ($request_method !~ ^(GET|POST|PUT|DELETE|PATCH)$) {
    return 405;
  }
  
  # Express:
  app.use((req, res, next) => {
    const allowed = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];
    if (!allowed.includes(req.method)) {
      return res.status(405).json({error: 'Method Not Allowed'});
    }
    next();
  });
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — accessing admin functions
- [[11 - Forced Browsing / Unprotected Admin Endpoints]] — endpoint access
- [[10 - BFLA — Broken Function Level Authorization (OWASP API #5)]] — function-level auth
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
