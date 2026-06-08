---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.56 Clear-Site-Data — Logout Clearing"
---

# 03.56 — Clear-Site-Data

## What is it?

`Clear-Site-Data` is a response header that tells the browser to clear stored data for the current origin. It's primarily used during logout to ensure the browser removes all cached data, cookies, and storage — preventing cached access after logout.

---

## Values

```
Clear-Site-Data: "cache"      → clear HTTP cache
Clear-Site-Data: "cookies"    → clear all cookies for this origin
Clear-Site-Data: "storage"    → clear localStorage, sessionStorage, IndexedDB
Clear-Site-Data: "executionContexts"  → close all windows for origin
Clear-Site-Data: "*"          → clear everything!

RECOMMENDED FOR LOGOUT:
  Clear-Site-Data: "cache", "cookies", "storage"
```

---

## VAPT Relevance: Missing Clear-Site-Data on Logout

```
SCENARIO:
  User logs out. Server invalidates session on backend.
  But browser still has:
    - Cached authenticated pages
    - Old cookies (if not explicitly cleared by Set-Cookie: session=; expires=past)
    - localStorage: {"user": "admin", "token": "abc"}
    - sessionStorage: sensitive data
  
  ATTACK:
    Attacker with physical access or XSS:
    → Read localStorage: localStorage.getItem('token')
    → Still valid? → Still authenticated!
    
    OR: Browser cached page at /dashboard
    → Even after logout, cached version shows sensitive data!
    → Press back button → see previous user's data!
```

---

## Attack: Shared Browser Data Theft

```
SCENARIO: Public computer (library, cafe)
  
  Previous user logged out (without Clear-Site-Data):
  → localStorage still has auth token
  → Browser cache still has account page
  
  Next user:
  → DevTools → Application → Local Storage → see previous user's token!
  → Back button → see previous user's account page!
  
  WITH Clear-Site-Data: "*" on logout:
  → All of this is cleared immediately!
```

---

## Testing

```bash
# Check if logout clears site data:
curl -sI https://target.com/logout \
  -X POST -H "Cookie: session=test" | grep -i "clear-site-data"

# If missing → manual check:
# 1. Log in → check localStorage (DevTools → Application → LocalStorage)
# 2. Log out
# 3. Check localStorage again → still has data? → VULNERABLE!

# Also check:
# - Back button after logout → cached authenticated page shown?
# - Cookie still present after logout?
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Cached pages after logout | Add `Clear-Site-Data: "cache"` on logout |
| Tokens in localStorage persist | Add `Clear-Site-Data: "storage"` |
| Cookies not cleared | Add `Clear-Site-Data: "cookies"` AND Set-Cookie with past expiry |

**Recommended logout response:**
```
HTTP/1.1 302 Found
Clear-Site-Data: "cache", "cookies", "storage"
Set-Cookie: session=; Max-Age=0; Secure; HttpOnly; SameSite=Strict
Location: /login
```

---

## Related Notes
- [[47 - Set-Cookie flags]] — cookie expiry on logout
- [[17 - Cookie]] — cookie management
- [[02.12 - Sessions How Server-Side Sessions Work]] — session termination
