---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.17 HTTP Redirects (301, 302, 307, 308)"
---

# 02.17 — HTTP Redirects (301, 302, 307, 308)

## What is it?

**HTTP redirects** tell clients to go to a different URL. The server responds with a 3xx status code and a `Location` header containing the new URL. Redirects are used for HTTPS enforcement, URL normalization, and navigation — but they're also a common source of **open redirect** vulnerabilities.

---

## Redirect Types

```
STATUS   NAME                  METHOD PRESERVED?   PERMANENT?
──────────────────────────────────────────────────────────────────
301      Moved Permanently      No (GET)            Yes (cached)
302      Found                  No (GET)            No
303      See Other              Always GET          No
307      Temporary Redirect     Yes (original)      No
308      Permanent Redirect     Yes (original)      Yes (cached)

METHOD PRESERVED = Does the redirected request use the same HTTP method?
  301/302/303: Browser changes POST to GET on redirect (by spec for 303, by practice for 301/302)
  307/308: Browser KEEPS the original method (POST stays POST)
```

---

## Redirect Responses

```
HTTP/1.1 301 Moved Permanently
Location: https://www.target.com/new-page
                ↑ Client should go here

HTTP/1.1 302 Found
Location: /dashboard
                ↑ Relative redirect (same host)

The client (browser or curl) then makes a NEW request to the Location URL.
```

---

## When Each is Used

```
301 Moved Permanently:
  HTTP → HTTPS redirect (domain-level)
  Domain change (old.com → new.com)
  Browser caches this → future direct requests skip the redirect

302 Found:
  Temporary redirect
  After form POST → redirect to confirmation page (PRG pattern)
  Conditional redirect based on user state

303 See Other:
  After successful POST → redirect to GET (PRG: Post/Redirect/Get)
  Prevents duplicate form submission on refresh

307 Temporary Redirect:
  Same as 302 but POST stays POST
  API redirects where body must be preserved

308 Permanent Redirect:
  Same as 301 but POST stays POST
  API endpoint moves permanently
```

---

## Security Context — Redirects in VAPT

### 1. Open Redirect

```
DEFINITION: App redirects to a URL from user-controlled input
            without validating the destination.

VULNERABLE CODE (conceptual):
  GET /redirect?next=https://evil.com
  Response: 302 → Location: https://evil.com ← redirects anywhere!

IMPACT:
  - Phishing: send victim a trusted company link → redirects to phishing page
    https://trusted-bank.com/auth/redirect?url=https://evil.com/phishing
    Victim sees trusted-bank.com domain → trusts → clicks → phishing

  - OAuth token theft:
    OAuth callback: redirect_uri=https://app.com/callback
    If callback accepts redirect: redirect_uri=https://evil.com/steal
    → Auth code/token sent to evil.com!

FIND OPEN REDIRECTS:
  Look for parameters: next, url, redirect, redirectTo, return, returnUrl,
                       goto, back, target, path, destination, link

  Test with:
  /redirect?next=https://evil.com
  /redirect?next=//evil.com          ← protocol-relative
  /redirect?next=https:evil.com      ← no double slash
  /redirect?next=\evil.com           ← backslash  
  /redirect?next=/%09/evil.com       ← tab character bypass
  /redirect?next=http://google.com%00.target.com  ← null byte
  /redirect?next=http://target.com.evil.com       ← subdomain confusion
  /redirect?next=javascript:alert(1)              ← XSS via redirect!
```

### 2. SSRF via Redirect

```
Some SSRF filters check the URL before following redirects.
But if the server follows redirects — open redirects bypass SSRF filters!

ATTACK:
1. Server has SSRF protection: blocks http://169.254.169.254/
2. But server follows redirects from whitelisted domains
3. Set up: https://attacker.com → 302 → http://169.254.169.254/
4. SSRF payload: ?url=https://attacker.com/redirect-to-metadata
5. Server fetches attacker.com (allowed) → follows redirect → hits metadata!
```

### 3. Redirect After Authentication — Credential Interception

```
Login flow with redirect:
  GET /login?next=/dashboard
  POST /login (credentials here)
  Response: 302 → Location: /dashboard

If the "next" parameter is replaced with attacker URL:
  /login?next=https://evil.com
  After login → 302 → https://evil.com ← credentials might be in Referer!

Even without stealing creds, phishing attacks work:
  /login?next=https://evil.com
  User logs in → redirected to evil.com → sees "session expired, login again"
  → Second phishing login steals password
```

### 4. 302 vs 307 — CSRF Implication

```
POST /transfer?amount=100&to=attacker HTTP/1.1
→ 302 redirect to /confirmation

Browser follows redirect as GET → CSRF token not resent
→ Server that uses 302 for POST redirects effectively requires token only on POST

307: POST redirects stay POST → token must be valid on redirect too
     More secure for POST-based state changes
```

### 5. Detecting Redirect Chains

```bash
# Follow all redirects and show each hop
curl -sI -L https://target.com 2>&1 | grep -E "HTTP|Location"
# HTTP/1.1 301 → Location: https://target.com/
# HTTP/1.1 302 → Location: /home
# HTTP/1.1 200

# Show redirect chain
curl -vs -L https://target.com 2>&1 | grep -E "< HTTP|< location:|> GET"

# Number of redirects
curl -sI -L -o /dev/null -w "%{num_redirects}" https://target.com
```

---

## Hands-On: Open Redirect Testing

```bash
# Basic open redirect test
curl -sI "https://target.com/redirect?next=https://evil.com" | grep -i location
# Location: https://evil.com → VULNERABLE!

# Test with various bypasses
for payload in \
  "https://evil.com" \
  "//evil.com" \
  "\/evil.com" \
  "https://target.com.evil.com" \
  "https://evil.com?target.com" \
  "https://evil.com#target.com"; do
  
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://target.com/redirect?next=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$payload'))")")
  location=$(curl -sI "https://target.com/redirect?next=$payload" | grep -i "^location:" | head -1)
  echo "$payload → $code | $location"
done

# Burp Suite: send redirect param to Intruder
# Payload: list of redirect bypass techniques
# Check Location header in responses
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Open redirect | Whitelist allowed redirect destinations |
| Redirect parameter without validation | Use relative redirects only, or signed redirect tokens |
| SSRF via open redirect | After URL validation, do not follow redirects to different hosts |
| 302 redirect leaking POST body | Use 303 for POST-to-GET redirects |
| Login redirect to arbitrary URL | Only redirect to same-origin relative paths |

---

## Related Notes
- [[07 - HTTP Status Codes]] — redirect status codes explained
- [[Module 08 - Open Redirect]] — open redirect full attack guide
- [[Module 13 - SSRF]] — SSRF via redirect chains
- [[Module 07 - CSRF]] — redirect and CSRF interaction
