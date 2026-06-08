---
tags: [vapt, jwt, beginner]
difficulty: beginner
module: "18 - JWT"
topic: "18.13 JWT in Cookies vs Authorization Header"
---

# 18.13 — JWT in Cookies vs Authorization Header

## Two Ways to Transmit JWTs

```
METHOD 1: Authorization Header
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  
  COMMON IN:
  REST APIs, SPAs (Single Page Applications), mobile apps
  
METHOD 2: Cookie
  Set-Cookie: access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...; HttpOnly; Secure; SameSite=Lax
  
  COMMON IN:
  Traditional web apps, server-rendered apps
  
EACH HAS DIFFERENT ATTACK SURFACE!
```

---

## Authorization Header: Risks

```
STORAGE LOCATION:
  Stored by JavaScript → in memory, localStorage, or sessionStorage
  
  IF IN MEMORY:
  → Lost on page refresh (secure, but poor UX)
  
  IF IN localStorage:
  → XSS can steal it: localStorage.getItem('token')
  → Persists across tabs and browser restarts
  
  IF IN sessionStorage:
  → XSS can steal it: sessionStorage.getItem('token')
  → Tab-scoped, gone on tab close
  
CSRF PROTECTION:
  Browsers don't automatically send Authorization headers cross-origin!
  → CSRF not typically a risk for API-only Bearer token usage
  → BUT: if server also accepts token from cookie OR URL → risk!
  
CORS REQUIREMENT:
  JavaScript must be able to read the response to extract and store the token
  → Server needs proper CORS headers for SPA use
  
XSS IS CATASTROPHIC:
  localStorage JWT + XSS = attacker steals and exfiltrates JWT
  → Attacker uses JWT until it expires (offline, no need to stay on page)
  → Different from cookie: stolen localStorage JWT works from any browser!
```

---

## Cookie: Risks

```
STORAGE LOCATION:
  Managed by browser, HttpOnly → JS can't read it!
  
  IF HttpOnly:
  → XSS CANNOT steal the cookie (major advantage!)
  → XSS can still make authenticated requests using the cookie
    (fetch/XHR sends cookies automatically for same-origin)
  
CSRF IS A RISK:
  Browsers automatically send cookies in cross-site requests
  → Attacker can trigger authenticated actions via CSRF
  → Must use CSRF tokens + SameSite=Lax/Strict to mitigate
  
SUBDOMAIN ISSUES:
  If Domain=.example.com → all subdomains see the cookie
  → Compromised subdomain → can access or manipulate the JWT cookie
  
JWT IN COOKIE SECURITY SETUP:
  Set-Cookie: jwt=TOKEN; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900
```

---

## Attack Comparison Table

```
ATTACK                  | Authorization Header | Cookie
─────────────────────────────────────────────────────────
XSS steals token        | YES (localStorage)   | NO (HttpOnly)
CSRF via token          | NO (not auto-sent)   | YES (auto-sent)
Network sniffing        | YES (no Secure flag) | NO (Secure flag)
Token in URL / logs     | YES (bad practice)   | NO
Subdomain leakage       | NO                   | YES (Domain=.x.com)
```

---

## Finding JWTs in the Wild

```bash
# FIND AUTHORIZATION HEADER IN BURP:
# HTTP History → search for "Bearer" in request headers

# FIND JWT COOKIES:
# HTTP History → search responses for Set-Cookie containing "eyJ"

# IN BROWSER:
# DevTools → Application → Local Storage → look for JWT keys
# DevTools → Application → Cookies → look for JWT-shaped values
# DevTools → Console: localStorage.getItem('token')
#                     document.cookie  → check for eyJ values

# FIND ALL JWTS IN BURP HISTORY:
# Burp → Search → "eyJ" → search in request bodies, headers, responses

# ANALYZE TOKEN:
python3 -c "
import base64, json, sys
for part in sys.argv[1].split('.')[:2]:
    padding = 4 - len(part) % 4
    try:
        print(json.loads(base64.urlsafe_b64decode(part + '='*padding)))
    except: pass
" "PASTE_JWT_HERE"
```

---

## Dual Token Acceptance (Dangerous Pattern)

```
SOME APPS ACCEPT JWT FROM MULTIPLE SOURCES:
  Authorization: Bearer TOKEN  → used by mobile apps
  Cookie: jwt=TOKEN           → used by web frontend
  URL parameter: ?token=TOKEN → used by... someone's bad idea
  
  IF SERVER ACCEPTS ALL THREE:
  → An XSS attack that can't steal the cookie
    can still craft a URL with the token!
  
  OR: If you can't get HttpOnly cookie, forge an Authorization header instead
  
TEST IN BURP:
  Take the JWT from Authorization header → put in cookie and retry
  Take the JWT from cookie → put in Authorization header and retry
  → Does both work? Report as "insecure dual-mode token acceptance"
  
  Also: try ?access_token=JWT in URL → does it work?
  → Report "JWT accepted in URL parameter"
```

---

## Fix

```
RECOMMENDED SETUP:
  
  HIGH-SECURITY WEB APP (traditional):
  → Use HttpOnly cookie for JWT
  → Add CSRF protection (SameSite=Lax + CSRF token)
  → No localStorage
  
  Set-Cookie: access_token=JWT; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=900
  
  SPA + API:
  → Short-lived access token in memory (not localStorage)
  → Refresh token in HttpOnly cookie
  → Strong CSP to mitigate XSS
  → On refresh: API endpoint reads HttpOnly cookie → returns new access token in body
  
  NEVER:
  ✗ Long-lived JWT in localStorage
  ✗ JWT in URL parameters
  ✗ No expiry on JWT
  ✗ JWT accepted from multiple sources without need
```

---

## Related Notes
- [[17.07 - Insecure Session Storage]] — where to store tokens
- [[17.11 - Cookie Flags Attack Scenarios]] — HttpOnly, SameSite details
- [[04 - Algorithm None Attack]] — JWT forgery attacks
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — fix
