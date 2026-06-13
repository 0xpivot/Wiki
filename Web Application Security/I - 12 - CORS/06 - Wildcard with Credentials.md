---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.06 Wildcard with Credentials"
---

# 12.06 — Wildcard with Credentials

## The Rule: * and Credentials Don't Mix

```
SPECIFICATION (CORS W3C):
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Credentials: true
  
  IS INVALID! Browsers REJECT this combination.
  
  Browser: "I see ACAO: * — that's a wildcard, meaning anyone."
           "I see ACAC: true — that allows sending cookies."
           "These two together are dangerous."
           "I will NOT send cookies, and I will NOT allow reading the response."
  
BROWSER BEHAVIOR:
  fetch('https://target.com/api', {credentials: 'include'})
  Response: ACAO: * + ACAC: true
  Result: CORS error! Blocked! Even though wildcard is set.

SO WHY IS IT IN THE NOTES?
  1. Some backends still set this combination (broken configs)
  2. Non-browser clients (curl, Postman) DON'T enforce this rule
  3. The null origin bypass can sometimes achieve similar results
  4. Some misconfigured proxies/CDNs may rewrite headers oddly
  5. Testing for it reveals intent: developer WANTED to allow all + creds
     → may have implemented a flawed workaround (reflected origin!)
```

---

## The Workaround Developers Try (and Get Wrong)

```
DEVELOPER REASONING:
  "ACAO: * + ACAC: true doesn't work in browsers..."
  "So I'll just reflect the origin back! That solves it!"
  
  BAD FIX:
    if (request.headers.origin) {
      response.setHeader('Access-Control-Allow-Origin', request.headers.origin);
      response.setHeader('Access-Control-Allow-Credentials', 'true');
    }
  
  THIS IS WORSE THAN WILDCARD!
  Wildcard + credentials: browser blocks it (no harm!)
  Reflected origin + credentials: browser ALLOWS it → CRITICAL VULN!
  
  Developers trying to "fix" the wildcard+creds error often introduce
  the origin reflection vulnerability instead!
```

---

## What * Actually Allows

```
WILDCARD WITHOUT CREDENTIALS:
  Access-Control-Allow-Origin: *
  (no Access-Control-Allow-Credentials header)
  
  ALLOWS:
  ✓ Any origin to read the response
  ✗ But NO cookies sent with the request
  ✗ No Authorization header sent
  
  RISK:
  If the API doesn't need authentication → public data is readable
  If API uses tokens in body (not cookies) → could be an issue
  
  TYPICAL USE CASE (safe):
  Public API endpoints: CDNs, fonts, public datasets
  No sensitive data returned
  No user-specific data

WILDCARD + CREDENTIALS (blocked):
  Browser blocks this → no direct exploit in browsers
  
  BUT TEST FOR IT because:
  1. Developer intent shows broken security thinking
  2. May indicate a reflected-origin fix was attempted nearby
  3. Non-browser clients can access without credentials anyway
  4. May work with null origin trick in edge cases
```

---

## Testing Wildcard Misconfigurations

```bash
# TEST 1: WILDCARD WITHOUT CREDENTIALS:
curl -v -H "Origin: https://evil.com" https://target.com/api/public
# ACAO: * → fine for public data
# Try: fetch('https://target.com/api/public') from evil.com → works!

# TEST 2: WILDCARD + CREDENTIALS (browser blocks, curl doesn't):
curl -v \
  -H "Origin: https://evil.com" \
  -H "Cookie: session=YOUR_SESSION" \
  https://target.com/api/account
# If response has ACAO: * + ACAC: true → broken config, browser blocks it
# But note it for the report!

# TEST 3: LOOK FOR REFLECTED ORIGIN WORKAROUND:
# Change Origin to anything and check if ACAO matches:
curl -v -H "Origin: https://aaaaa.com" https://target.com/api/account
# If ACAO: https://aaaaa.com → reflected origin! → CRITICAL

# TEST 4: WHAT HAPPENS WITH NO ORIGIN HEADER?
curl -v https://target.com/api/account
# No ACAO in response → good (SOP protects browser requests)
```

---

## Wildcard in Preflight (Methods and Headers)

```
NOTE: Wildcard for METHODS and HEADERS is different from ACAO wildcard!

Access-Control-Allow-Methods: *      ← Chrome 97+ supports this
Access-Control-Allow-Headers: *      ← Chrome 97+ supports this

These are generally fine (they don't involve credentials).

BUT: some developers also set:
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
Access-Control-Allow-Credentials: true

→ The ACAO: * + ACAC: true is still rejected by browsers
→ Methods and headers wildcards don't make it worse (browser still blocks)
→ But again: developer intent is to allow everything → look for reflected origin!
```

---

## Reporting Wildcard + Credentials

```
SEVERITY: Low-Medium (browser blocks it, but shows intent)

REPORT TEXT:
  The server returns both Access-Control-Allow-Origin: * and 
  Access-Control-Allow-Credentials: true. While modern browsers
  reject this combination and do not allow the request, this 
  configuration indicates that the developer intended to allow all 
  origins with credentials. This often leads to developers implementing
  an origin reflection workaround (which IS exploitable — see [CORS-04]).
  
  Additionally, non-browser clients (curl, Postman) do not enforce this
  browser rule and CAN access the endpoint cross-origin.

RECOMMENDATION:
  Replace Access-Control-Allow-Origin: * with a strict whitelist of 
  allowed origins. Never reflect the Origin header blindly.
```

---

## Related Notes
- [[04 - Origin Reflection Misconfiguration]] — the dangerous "fix" for this
- [[05 - Null Origin Misconfiguration]] — null origin trick
- [[03 - CORS Headers Full Reference]] — header rules
- [[12 - Defense Strict Origin Whitelisting]] — correct implementation
