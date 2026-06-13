---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.15 Referer — Info Leakage, CSRF Bypass, Token Leakage"
---

# 03.15 — Referer

## What is it?

The `Referer` header (intentionally misspelled in the HTTP spec) tells the server which URL the user came from. When you click a link, your browser includes the current page URL in the `Referer` header of the request to the destination.

**Note:** Modern browsers also send `Referrer-Policy` response header to control how much is shared.

---

## Sensitive Data Leakage via Referer

```
SCENARIO: URL contains sensitive token/data

  https://target.com/reset?token=SECRET_RESET_TOKEN

  User clicks any external link on this page:
    → GET https://external-site.com/ HTTP/1.1
       Referer: https://target.com/reset?token=SECRET_RESET_TOKEN

  External site logs/receives the SECRET token!

COMMON CASES:
  - Password reset tokens in URL
  - Session IDs in URL (never do this)
  - OAuth codes in URL redirects
  - Search queries with PII
  - File download tokens

MITIGATION: Referrer-Policy: no-referrer (or origin-when-cross-origin)
```

---

## CSRF Bypass via Referer Manipulation

```
SCENARIO: Some apps check Referer for CSRF protection instead of token.
  If Referer is from target.com → allow
  Otherwise → reject

BYPASS TECHNIQUES:

1. Remove Referer entirely:
   <meta name="referrer" content="no-referrer">
   <img referrerpolicy="no-referrer" src="...">
   → No Referer header sent → some apps allow if Referer is missing!

2. Include target.com in attacker's URL:
   https://attacker.com/?target.com
   Referer: https://attacker.com/?target.com
   App checks if "target.com" is in Referer → it is! → bypass!

3. Make request from subdomain:
   If app allows *.target.com:
   Subdomain XSS → CSRF from sub.target.com → Referer matches!
```

---

## Attack: Referer-Based Injection

```
If app stores or reflects Referer:

SQLi via Referer:
  GET /page HTTP/1.1
  Referer: https://attacker.com/' OR SLEEP(5)--

XSS via Referer:
  GET /page HTTP/1.1
  Referer: <script>alert(1)</script>
  → If admin views request logs → stored XSS!

Server-Side Logging:
  Many apps log Referer → same injection vectors as User-Agent
```

---

## Referrer-Policy Security Header

```
Controls how much Referer info is sent:

no-referrer:              → No Referer header ever sent
no-referrer-when-downgrade: → No Referer when going HTTPS→HTTP
same-origin:              → Only send Referer for same-origin requests
origin:                   → Only send origin (https://target.com), no path
strict-origin:            → Origin only, only for same-security-level
origin-when-cross-origin: → Full URL for same-origin, origin only for cross-origin
strict-origin-when-cross-origin: → Default (Chrome 85+, most secure common option)
unsafe-url:               → Always send full URL (DANGEROUS)

RECOMMENDED:
  Referrer-Policy: strict-origin-when-cross-origin
```

---

## Hands-On: Referer Testing

```bash
# Send custom Referer
curl -H "Referer: https://attacker.com" https://target.com/action

# Test CSRF bypass (empty Referer)
curl -X POST https://target.com/change-password \
  -d "new_pass=evil" \
  --referer ""  # no referer

# Referer injection test
curl -H "Referer: https://attacker.com/' OR '1'='1" https://target.com/

# Check Referrer-Policy on responses
curl -sI https://target.com | grep -i referrer-policy
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Sensitive tokens in URL (leaked via Referer) | Don't put secrets in URLs; use POST body |
| CSRF protection via Referer only | Use CSRF tokens instead; Referer is bypassable |
| Referer stored/displayed unsanitized | Sanitize before storage/display |
| No Referrer-Policy | Set `Referrer-Policy: strict-origin-when-cross-origin` |

---

## Related Notes
- [[16 - Origin]] — similar header for CORS
- [[Module 07 - CSRF]] — Referer-based CSRF protection bypass
- [[Module 03 - HTTP Headers Security]] — security headers
