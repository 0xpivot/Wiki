---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.25 Autocomplete on Sensitive Fields"
---

# 16.25 — Autocomplete on Sensitive Fields

## What Is Autocomplete?

```
BROWSER AUTOCOMPLETE:
  Browsers save form field values and suggest them on future visits
  
  Saved by default: username, email, phone, address, credit card, passwords
  
  Password manager / browser: offers to save/fill passwords
  
THE SECURITY ISSUE:
  Sensitive fields (password, CVV, OTP, secret answer) saved by browser
  → On shared computers: next user sees suggested values!
  → Browser credential databases can be extracted by malware
  → If browser profile synced to cloud: credentials in cloud!
```

---

## What Should Have Autocomplete Disabled

```
HIGH RISK - Should disable autocomplete:
  ✗ Password fields (especially for credit card PINs, not login passwords)
  ✗ Credit card number: <input name="cc_number" autocomplete="cc-number">
     Actually autocomplete="cc-number" is a proper value — this enables payment autofill
     The SENSITIVE ones you want to disable: CVV, backup codes, OTPs
  ✗ One-Time Password (OTP) fields
  ✗ Security question answers
  ✗ Secret keys / API keys displayed in forms
  
NOTE ON PASSWORDS:
  OWASP used to say: autocomplete="off" on password fields
  But NIST SP 800-63B NOW says: ALLOW paste and password manager autofill!
  Password managers improve security (users use stronger passwords)
  → DON'T disable on login password fields!
  → DO disable on CVV, OTP, one-time codes
```

---

## Testing

```bash
# CHECK HTML SOURCE FOR AUTOCOMPLETE:
curl -s https://target.com/login | grep -i autocomplete
curl -s https://target.com/checkout | grep -i autocomplete

# IN BROWSER:
# View page source → Ctrl+F → search "autocomplete"
# Inspect the sensitive input fields → check attribute

# EXAMPLE - MISSING AUTOCOMPLETE OFF:
# <input type="password" name="current_password"> ← missing on CVV-like fields
# <input type="text" name="otp">  ← OTP should have autocomplete="off"
# <input type="text" name="cvv">  ← should have autocomplete="off"
# <input type="text" name="backup_code"> ← should have autocomplete="off"

# GOOD (for OTP/CVV):
# <input type="text" name="otp" autocomplete="off">
# <input type="text" name="cvv" autocomplete="off">

# GOOD (for password - allow password manager):
# <input type="password" name="password" autocomplete="current-password">
```

---

## Severity Assessment

```
SEVERITY: Low / Informational
  
  This is a LOW priority finding in most VAPT reports
  
  Factors that raise severity:
  - Credit card CVV fields without autocomplete="off"
  - OTP fields saving to browser history
  - Application on shared workstations (kiosks, shared computers)
  
  Factors that keep it informational:
  - Standard login password field (password managers are GOOD)
  - Modern browsers often ignore autocomplete="off" on passwords anyway
  
REPORTING TEMPLATE:
  Title: "Autocomplete enabled on sensitive form fields"
  Severity: Low
  CWE: CWE-525
  Evidence: [field name, URL, HTML snippet]
  Recommendation: Add autocomplete="off" to CVV, OTP, and security question fields
```

---

## Fix

```html
<!-- SENSITIVE FIELDS — DISABLE AUTOCOMPLETE: -->
<input type="text"     name="otp"          autocomplete="off">
<input type="text"     name="cvv"          autocomplete="off">
<input type="text"     name="backup_code"  autocomplete="off">
<input type="text"     name="secret_answer" autocomplete="off">

<!-- PASSWORD FIELDS — ALLOW PASSWORD MANAGER: -->
<input type="password" name="password"     autocomplete="current-password">
<input type="password" name="new_password" autocomplete="new-password">

<!-- PAYMENT — USE SPECIFIC AUTOCOMPLETE VALUES (not off): -->
<input type="text"   name="cc_number"     autocomplete="cc-number">
<input type="text"   name="cc_exp"        autocomplete="cc-exp">
<input type="text"   name="cc_name"       autocomplete="cc-name">
<input type="text"   name="cvv"           autocomplete="off">  ← CVV = off
```

---

## Related Notes
- [[26 - Verbose Error Messages]] — also low-severity finding
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
