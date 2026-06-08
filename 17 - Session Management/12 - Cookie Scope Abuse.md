---
tags: [vapt, session-management, cookies, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.12 Cookie Scope Abuse (Domain and Path)"
---

# 17.12 — Cookie Scope Abuse (Domain and Path)

## Domain Attribute

```
Set-Cookie: session=X; Domain=.example.com
                            ↑ dot prefix = ALL subdomains!
                            
WITHOUT Domain (or with exact host):
  Cookie only sent to: www.example.com (exact host)
  
WITH Domain=.example.com:
  Cookie sent to ALL of:
  www.example.com
  api.example.com
  static.example.com
  evil.example.com  ← if attacker controls this subdomain!
  
ATTACK:
  If attacker can control any subdomain of example.com
  → They receive the session cookie in every request to their subdomain!
  → Attacker can steal the cookie from their own subdomain's server
```

---

## Domain Oversharing Attack

```
SCENARIO:
  Main app:     secure.example.com  (high-security banking)
  Static files: static.example.com  (just serving JS/CSS)
  
  Cookie set: Set-Cookie: bank_session=SECRET; Domain=.example.com
  
  CONSEQUENCE:
  Every request to static.example.com also sends bank_session=SECRET
  
  If static.example.com is compromised or XSS-able:
  → Attacker on static.example.com receives the bank session cookie!
  
FIX:
  Set Domain=secure.example.com (exact host, no dot prefix)
  → Cookie only sent to the specific secure.example.com
  → static.example.com never sees the cookie

TESTING:
  Check all Set-Cookie headers
  Is Domain overly broad? (.example.com instead of specific subdomain)
  Is there any other subdomain that could receive this cookie unexpectedly?
  
  Check: request to static.example.com → does it include session cookie?
  DevTools → Network → filter requests to other subdomains → check Cookie header
```

---

## Subdomain Cookie Injection

```
ATTACKER-CONTROLLED SUBDOMAIN:
  If attacker owns: attacker.example.com (via subdomain takeover or similar)
  
  They can SET a cookie for the parent domain:
  Set-Cookie: session=FAKE_VALUE; Domain=.example.com
  
  → This cookie is now sent to secure.example.com!
  → Session fixation via cookie injection!
  
  (This is why SameSite=Strict is valuable — limits cross-subdomain cookie use)
  
TESTING SUBDOMAIN TAKEOVER FOR COOKIE INJECTION:
  Find dangling CNAME: stale.example.com CNAME → abandoned-cloud-resource
  Take over the cloud resource
  Serve a page that sets cookies with Domain=.example.com
  
  See also: Module 12 CORS - Subdomain Trust (similar attack chain)
```

---

## Path Attribute

```
Set-Cookie: admin_session=X; Path=/admin

PATH ATTRIBUTE CONTROLS:
  Cookie only sent to URLs that START WITH the specified path
  
  /admin → sends admin_session cookie
  /admin/users → sends admin_session cookie
  /admin/settings → sends admin_session cookie
  /dashboard → does NOT send admin_session cookie
  /api/... → does NOT send admin_session cookie
  
PATH IS NOT A SECURITY FEATURE:
  JavaScript on the page can still read cookies from all paths!
  (Unless HttpOnly, but then JS can't read any of them)
  
  <script>document.cookie</script> → shows ALL cookies from ALL paths!
  
  Path only controls NETWORK sending, not JavaScript access!
  So path-based segregation provides minimal security benefit.
```

---

## Cookie Tossing (Covered More in 17.13)

```
RELATED CONCEPT:
  If attacker controls a subdomain → they can SET a cookie for a path
  that the main app will then see and use
  
  Example:
  Main app: example.com/api/token (reads "token" cookie)
  Attacker subdomain sets: Set-Cookie: token=EVIL_VALUE; Domain=.example.com; Path=/api
  
  → When victim visits example.com → browser sends EVIL_VALUE for /api requests
  → This overrides or conflicts with legitimate token!
```

---

## Testing Cookie Scope

```bash
# CHECK DOMAIN SCOPE:
curl -I https://target.com | grep -i set-cookie
# Note Domain attribute
# Is it .target.com or target.com?

# CHECK IF SUBDOMAINS RECEIVE COOKIE:
curl -v https://api.target.com/public \
  -H "Cookie: session=YOUR_SESSION"
# Does the API response leak data showing it received the session?

# AUTOMATED SCOPE CHECK:
python3 -c "
import requests

# Try to access session cookie from different subdomain
r1 = requests.get('https://www.target.com', allow_redirects=False)
session = r1.cookies.get('session')

# Try sending to other subdomain
r2 = requests.get('https://api.target.com/', cookies={'session': session})
print(r2.status_code, r2.text[:200])
"

# CHECK ALL SET-COOKIE HEADERS ON THE SITE:
curl -s https://target.com -D - | grep -i "^set-cookie"
```

---

## Fix

```
DOMAIN ATTRIBUTE BEST PRACTICES:
  ✓ Use exact host (no dot prefix) for sensitive cookies:
    Set-Cookie: session=X; HttpOnly; Secure; SameSite=Lax
    (No Domain attribute = defaults to exact originating host)
    
  ✓ Only use Domain=.example.com when cross-subdomain sharing NEEDED
    (e.g., shared SSO between app.example.com and api.example.com)
    
  ✓ Never set Domain to parent domain if you have untrusted subdomains
  
  ✓ For highest security: keep sessions to a single subdomain
    Don't let admin sessions leak to CDN/static subdomains

PATH ATTRIBUTE:
  Path=/  is the safest (broadly scoped, no false sense of security)
  Path restriction gives minimal security benefit (JavaScript bypasses it)
  Don't rely on Path for session isolation
```

---

## Related Notes
- [[11 - Cookie Flags Attack Scenarios]] — HttpOnly, Secure, SameSite
- [[13 - Cookie Tossing]] — subdomain-based cookie injection
- [[Module 12 CORS - Subdomain Trust]] — related subdomain attacks
