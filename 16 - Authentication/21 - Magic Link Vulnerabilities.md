---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.21 Magic Link Vulnerabilities"
---

# 16.21 — Magic Link Vulnerabilities

## What Are Magic Links?

```
MAGIC LINK:
  Passwordless authentication via email link
  
  FLOW:
  1. User enters email → "Send me a login link"
  2. Server generates a single-use token → emails link:
     https://example.com/auth/magic?token=a1b2c3d4e5f6...
  3. User clicks link → token validated → user logged in!
  4. No password required — link itself = credential
  
ADVANTAGES:
  - No password to phish, brute force, or reuse
  - Simple UX
  
DISADVANTAGES:
  - Email access = full account access (email is the root credential)
  - Link may be forwarded, screenshot, etc.
  
WHERE USED:
  Notion, Slack (email fallback), dev tools, SaaS products
```

---

## Magic Link Vulnerabilities

### 1. Token Not Expiring

```
TEST:
  1. Request magic link for your own account
  2. Don't use it immediately — wait 2 hours
  3. Click the link → if it still works → no expiry!
  
IMPACT:
  Magic links in old emails = permanent backdoor!
  
FIX:
  Expire magic links after 10-15 minutes maximum
```

### 2. Token Not Single-Use

```
TEST:
  1. Request magic link
  2. Click it → logged in
  3. Click the SAME link again (from email or browser history)
  4. → If you're logged in again → not single-use!
  
IMPACT:
  Forwarded email = permanent login capability for recipient
  
FIX:
  Invalidate token immediately on first use
```

### 3. Token Predictability

```
(Same as password reset token predictability — see note 16.07)
  - Sequential tokens
  - Short tokens (4-6 chars)
  - Timestamp-based tokens
  
TEST:
  Request multiple magic links → analyze token patterns
  Run through Burp Sequencer for entropy analysis
```

### 4. Token Leaked via Referer Header

```
SCENARIO:
  User clicks magic link in email:
  https://example.com/auth/magic?token=SECRET_TOKEN
  
  The landing page /auth/magic loads external resources!
  (Analytics script, images, tracking pixels)
  
  Browser sends to those external servers:
  Referer: https://example.com/auth/magic?token=SECRET_TOKEN
  ↑ TOKEN IN REFERER!
  
  External analytics server logs the full URL including token!
  → Token leaked to third party!
  
TEST:
  Inspect the magic link landing page
  Check what external resources it loads
  In Burp → check if Referer is sent with token to third parties
  
FIX:
  After consuming token in URL → redirect to clean URL!
  GET /auth/magic?token=XXX → validate → redirect to /dashboard
  OR: Use Referrer-Policy: no-referrer header on the page
  OR: Use POST form instead of GET link
```

### 5. Token in URL Shared via Third-Party

```
SCENARIOS WHERE MAGIC LINK LEAKS:
  - User copies link → pastes in chat/Slack → token exposed
  - Browser history → visible to anyone with device access
  - Server logs (if app logs all request URLs)
  - Reverse proxy logs
  - URL in browser's address bar when page loads
  
FIX:
  Exchange token ONCE → immediately redirect to clean URL
  Don't show the token URL in address bar after auth:
  POST /auth/magic { token: XXX }  (no token in URL!)
```

---

## Testing Methodology

```
CHECKLIST:
  ✓ Request magic link → save it
  ✓ Try 2 hours later → still works? (no expiry)
  ✓ Use once → try again (not single-use?)
  ✓ Request 5 links → analyze token entropy (predictable?)
  ✓ Click link → inspect network tab → external Referer leaking?
  ✓ Try changing email in URL (token=X&email=victim@example.com)
  ✓ Token tied to email or just valid globally?
```

---

## Fix

```
SECURE MAGIC LINK IMPLEMENTATION:
  ✓ 128+ bit random token: secrets.token_urlsafe(32)
  ✓ Expire in 15 minutes max
  ✓ Single-use: delete on first use
  ✓ Tie to email (token maps to specific user in DB)
  ✓ Redirect to clean URL after consuming token:
    GET /magic?token=XXX → validate → 302 → /dashboard
    (Token gone from URL immediately)
  ✓ Referrer-Policy: no-referrer on auth pages
  ✓ Rate limit link requests (prevent enumeration/spam)
```

---

## Related Notes
- [[07 - Forgot Password Token Predictability]] — same token concepts
- [[09 - Forgot Password Token Reuse]] — single-use enforcement
- [[28 - Defense Rate Limiting Lockout MFA]] — defense guide
