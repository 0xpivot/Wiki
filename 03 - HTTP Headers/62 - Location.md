---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.62 Location — Open Redirect"
portswigger_labs: ["DOM-based open redirect"]
---

# 03.62 — Location

## What is it?

The `Location` response header is used with 3xx redirect responses to specify where the browser should go next. It's also used in 201 Created responses to point to the newly created resource. Attackers exploit misconfigured `Location` values to redirect users to malicious sites (open redirect), bypass auth, or assist in phishing.

---

## How Location is Used

```
REDIRECT:
  HTTP/1.1 302 Found
  Location: https://target.com/dashboard
  → Browser follows to /dashboard

CREATED:
  HTTP/1.1 201 Created
  Location: https://api.target.com/resource/123
  → New resource URL

OPEN REDIRECT (vulnerable):
  GET /redirect?url=https://target.com → safe
  GET /redirect?url=https://evil.com  → dangerous!
  
  HTTP/1.1 302 Found
  Location: https://evil.com   ← controlled by attacker!
```

---

## Attack: Open Redirect for Phishing

```
ATTACK SETUP:
  1. Find open redirect: https://bank.com/redirect?to=https://evil.com
  2. Craft URL: https://bank.com/redirect?to=https://evil-bank.com/login
  3. Send to victim: "Your account needs verification — click here"
  4. URL shows bank.com domain → victim trusts it!
  5. Redirected to evil-bank.com → phishing!
  
WHY VICTIMS FALL FOR IT:
  They see "bank.com" in the URL → trust it!
  First redirect brings them to evil site → game over!
```

---

## Attack: OAuth Token Theft via Open Redirect

```
OAUTH FLOW:
  Authorization URL: https://oauth.com/auth?redirect_uri=https://app.com/callback
  
  If app.com has open redirect:
  https://oauth.com/auth?redirect_uri=https://app.com/redirect?to=https://evil.com
  
  OAuth server validates redirect_uri: "app.com/redirect? → that's app.com → allowed!"
  
  But redirects to evil.com with auth CODE:
  https://evil.com/?code=OAUTH_CODE_HERE
  
  → Attacker steals OAuth code → account takeover!
```

---

## Attack: SSRF via Open Redirect

```
SOME SSRF PROTECTIONS: block direct internal URLs
  Reject: url=http://169.254.169.254/

BYPASS: Use open redirect as proxy!
  url=https://target.com/redirect?to=http://169.254.169.254/metadata
  
  Step 1: Server fetches target.com/redirect (seems safe!)
  Step 2: target.com redirects to 169.254.169.254!
  Step 3: Server follows redirect → hits internal metadata!
  → SSRF via open redirect!
```

---

## Bypass Techniques for Weak Validation

```
VALIDATION: only allow URLs containing "target.com"

BYPASSES:
  https://evil.com#target.com        ← fragment with target.com
  https://evil.com?redirect=target.com  ← query param
  https://target.com.evil.com        ← subdomain that looks like target
  https://evil.com\@target.com       ← browser might parse as evil.com
  //evil.com (protocol-relative)     ← some validators miss this
  /\evil.com                         ← some browsers interpret as absolute
  https://target.com%0d%0aLocation: https://evil.com  ← header injection!
```

---

## Testing

```bash
# Find redirect parameters:
# Common: ?url=, ?redirect=, ?next=, ?returnTo=, ?goto=, ?target=, ?r=, ?dest=

# Basic test:
curl -sI "https://target.com/redirect?to=https://evil.com" | grep "^Location:"
# Location: https://evil.com → OPEN REDIRECT!

# Test bypass:
curl -sI "https://target.com/redirect?to=//evil.com" | grep Location
curl -sI "https://target.com/redirect?to=https://evil.com%09" | grep Location

# Automate with redirects following:
curl -L "https://target.com/login?next=https://evil.com" -v 2>&1 | grep "Location:"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Open redirect | Use allowlist of valid redirect destinations |
| Dynamic redirect from URL param | Map to internal names (not raw URLs) |
| OAuth redirect_uri bypass | Exact string match, not contains-check |

---

## Related Notes
- [[02.17 - HTTP Redirects]] — redirect types and security
- [[Module 06 - SSRF]] — SSRF via open redirect
- [[Module 14 - OAuth]] — OAuth token theft via open redirect
