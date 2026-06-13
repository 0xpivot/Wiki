---
tags: [vapt, cors, beginner]
difficulty: beginner
module: "12 - CORS"
topic: "12.02 Simple vs Preflight Requests"
---

# 12.02 — Simple vs Preflight Requests

## Why the Distinction Matters

```
CORS HAS TWO MODES:

SIMPLE REQUEST: Browser sends request directly — no preflight
  → Designed for HTML form compatibility (backward compatibility!)
  → These worked cross-origin BEFORE CORS existed (forms always sent)
  → Server must STILL send CORS headers for JS to read response
  → But the request itself ALWAYS goes through!

PREFLIGHT REQUEST: Browser asks permission first via OPTIONS
  → For "complex" requests that didn't exist before CORS
  → Server can BLOCK the actual request if preflight fails
  → Provides more granular control
```

---

## Simple Request Criteria

```
A request is SIMPLE if ALL of the following are true:

METHOD: GET, POST, or HEAD only
  ✓ GET
  ✓ POST  
  ✓ HEAD
  ✗ PUT, DELETE, PATCH, OPTIONS, CONNECT, TRACE → requires preflight

CONTENT-TYPE (only relevant for POST):
  ✓ application/x-www-form-urlencoded
  ✓ multipart/form-data
  ✓ text/plain
  ✗ application/json → requires preflight!
  ✗ application/xml  → requires preflight!
  ✗ Any custom type  → requires preflight!

HEADERS (only "safe" headers):
  ✓ Accept
  ✓ Accept-Language
  ✓ Content-Language
  ✓ Content-Type (with above restrictions)
  ✗ Authorization  → requires preflight!
  ✗ X-CSRF-Token   → requires preflight!
  ✗ Any custom header → requires preflight!

ALL CONDITIONS MUST BE TRUE:
  If any one fails → preflight required!
```

---

## Simple Request Flow

```
SIMPLE REQUEST (no preflight):

Browser JS:                        Server:
  fetch('https://api.other.com/data')
  
  GET /data HTTP/1.1
  Origin: https://app.mysite.com   ← browser adds automatically
  ─────────────────────────────────────────────────────→
  
                                   HTTP/1.1 200 OK
                                   Access-Control-Allow-Origin: https://app.mysite.com
  ←─────────────────────────────────────────────────────
  
  Browser checks ACAO header:
  ✓ Origin matches → JS can read the response!
  ✗ No ACAO or wrong origin → JS blocked from reading (but request DID go!)
  
IMPORTANT: THE REQUEST GOES REGARDLESS!
  The server receives and processes the simple request
  even if CORS fails. CORS only controls whether
  the BROWSER can read the response!
  
  This is why CSRF works on simple requests!
```

---

## Preflight Request Flow

```
PREFLIGHT REQUEST (complex request):

Browser JS:                        Server:
  fetch('https://api.other.com/data', {
    method: 'DELETE',
    headers: { 'Authorization': 'Bearer token' }
  })
  
  STEP 1 — PREFLIGHT:
  OPTIONS /data HTTP/1.1
  Origin: https://app.mysite.com
  Access-Control-Request-Method: DELETE
  Access-Control-Request-Headers: Authorization
  ─────────────────────────────────────────────────────→
  
                                   HTTP/1.1 204 No Content
                                   Access-Control-Allow-Origin: https://app.mysite.com
                                   Access-Control-Allow-Methods: GET, POST, DELETE
                                   Access-Control-Allow-Headers: Authorization
                                   Access-Control-Max-Age: 86400
  ←─────────────────────────────────────────────────────
  
  STEP 2 — ACTUAL REQUEST (only if preflight approved):
  DELETE /data HTTP/1.1
  Origin: https://app.mysite.com
  Authorization: Bearer token
  ─────────────────────────────────────────────────────→
  
                                   HTTP/1.1 200 OK
                                   Access-Control-Allow-Origin: https://app.mysite.com
  ←─────────────────────────────────────────────────────
  
  If preflight FAILED:
  Browser: does NOT send the actual DELETE request!
  JS gets CORS error.
```

---

## Security Implications

```
SIMPLE REQUESTS AND CSRF:
  HTML forms have always been simple requests.
  Browsers send simple requests to any domain (no preflight).
  This is WHY CSRF is possible — simple requests bypass CORS!
  
  CSRF attack uses simple request:
  <form method="POST" enctype="application/x-www-form-urlencoded">
  → Simple request → no preflight → server receives and processes it!

PREFLIGHT PROTECTION:
  If an endpoint REQUIRES:
  ✓ Content-Type: application/json
  ✓ Authorization: Bearer ...
  ✓ PUT/DELETE method
  
  Then CSRF is much harder (needs CORS bypass for preflight to pass).
  This is a natural protection of JSON APIs!
  But NOT complete protection (see CORS misconfiguration notes).

CREDENTIALS AND PREFLIGHT:
  Preflight itself DOES NOT include credentials (no cookies!)
  This means server can't see who is making the preflight.
  Actual request includes credentials (if configured).
```

---

## Max-Age Caching

```
Access-Control-Max-Age: 3600
  → Browser caches preflight result for 3600 seconds (1 hour)
  → Subsequent requests don't need to preflight again
  
PENTESTING NOTE:
  If you change Origin in a cached-preflight scenario:
  May need to clear browser cache or use incognito mode.
  
  Chrome max: 7200 seconds (2 hours)
  Firefox max: 86400 seconds (24 hours)
```

---

## Testing Simple vs Preflight in Burp

```bash
# TEST 1: SIMPLE REQUEST — check if ACAO is returned:
curl -v -H "Origin: https://evil.com" https://target.com/api/data
# If ACAO: https://evil.com AND ACAC: true → vulnerable!

# TEST 2: FORCE A PREFLIGHT — use PUT or add custom header:
curl -v -X OPTIONS \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: DELETE" \
  -H "Access-Control-Request-Headers: Authorization" \
  https://target.com/api/data
# Check: Does server allow evil.com in preflight response?

# IN BURP:
# 1. Intercept a request to API
# 2. Add/change: Origin: https://evil.com
# 3. Send and check response headers
# 4. Also test: Origin: null
# 5. Also test: Origin: https://target.com.evil.com
```

---

## Related Notes
- [[01 - What is CORS and Why It Exists]] — CORS overview
- [[03 - CORS Headers Full Reference]] — all headers
- [[04 - Origin Reflection Misconfiguration]] — exploiting reflected origin
- [[Module 11 - CSRF]] — simple requests enable CSRF!
