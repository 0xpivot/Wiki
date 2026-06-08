---
tags: [vapt, csrf, defense, beginner]
difficulty: beginner
module: "11 - CSRF"
topic: "11.10 Defense — Tokens, SameSite, Double-Submit Cookie"
---

# 11.10 — Defense: CSRF Tokens, SameSite, Double-Submit Cookie

## Defense Layer 1 — CSRF Tokens (Primary Defense)

```
HOW IT WORKS:
  1. Server generates cryptographically random token (32+ bytes)
  2. Token stored in server session: session['csrf'] = token
  3. Token embedded in every HTML form as hidden field
  4. On form submit: validate submitted token matches session token
  5. If mismatch → reject request with 403 Forbidden

PROPERTIES OF A GOOD CSRF TOKEN:
  ✓ Unpredictable (cryptographically random)
  ✓ Unique per session (different for each user session)
  ✓ Validated server-side on EVERY state-changing request
  ✓ Not tied to URL parameters (avoid Referer leakage)
  ✓ Invalidated on logout
```

---

## Implementing CSRF Tokens (by Language/Framework)

```python
# PYTHON / FLASK:
import secrets

@app.before_request
def set_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)

# IN TEMPLATE:
# <input type="hidden" name="csrf_token" value="{{ session['csrf_token'] }}">

# VALIDATE:
@app.route('/change-email', methods=['POST'])
def change_email():
    submitted = request.form.get('csrf_token')
    if not submitted or submitted != session.get('csrf_token'):
        abort(403)
    # proceed safely
```

```javascript
// NODE.JS / EXPRESS (using csurf middleware):
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});

app.post('/submit', csrfProtection, (req, res) => {
  // csurf validates automatically, returns 403 on failure
  res.send('success');
});
```

```php
// PHP:
// Generate:
if (!isset($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

// Embed in form:
// <input name="csrf_token" value="<?= htmlspecialchars($_SESSION['csrf_token']) ?>">

// Validate:
if (!hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'] ?? '')) {
    http_response_code(403);
    exit('CSRF validation failed');
}
```

---

## Defense Layer 2 — SameSite Cookies

```
SET COOKIES WITH SameSite=Lax OR SameSite=Strict:

SameSite=Lax (recommended for most apps):
  Set-Cookie: session=abc123; SameSite=Lax; Secure; HttpOnly; Path=/
  
  ✓ Blocks cross-site POST CSRF (most common attack!)
  ✓ Allows top-level navigation (user-friendly)
  ✗ Doesn't block GET-based CSRF (→ ensure GET is idempotent!)

SameSite=Strict (maximum security):
  Set-Cookie: session=abc123; SameSite=Strict; Secure; HttpOnly; Path=/
  
  ✓ Blocks all cross-site requests
  ✗ User-unfriendly: clicking links from external sites = logged out!
  
IMPORTANT:
  SameSite alone is not sufficient! It's a defense-in-depth layer.
  Still implement CSRF tokens for critical actions.
  Reason: SameSite=Lax can be bypassed via GET, sibling subdomains, etc.
```

---

## Defense Layer 3 — Double-Submit Cookie Pattern

```
WHEN TO USE: Stateless apps where server doesn't store session data

HOW IT WORKS:
  1. Server sets random cookie: Set-Cookie: csrf=RANDOM_VALUE
  2. Client also sends same value in form/header: X-CSRF-Token: RANDOM_VALUE
  3. Server validates: cookie value == header/form value
  
  Since attacker can't read the cookie (SOP), they can't include matching value!

IMPLEMENTATION:
  Set-Cookie: csrf-token=abc123xyz; Secure; SameSite=Strict; Path=/
  
  Form: <input name="X-CSRF-Token" value="abc123xyz">
  OR
  Header: X-CSRF-Token: abc123xyz
  
  Server: if request.cookies['csrf-token'] != request.headers['X-CSRF-Token']:
              abort(403)

WEAKNESS:
  If attacker can set cookies via CRLF injection or subdomain control →
  they can set their own csrf-token cookie AND submit matching header!
  → Broken double-submit!
  
  Solution: HMAC-based double-submit (sign token with server secret):
    cookie value: HMAC(server_secret, session_id)
    attacker can't forge without knowing server_secret
```

---

## Defense Layer 4 — Verify Origin and Referer Headers

```python
# ORIGIN HEADER CHECK (modern browsers, reliable):
@app.before_request
def verify_origin():
    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')
        
        allowed_origin = 'https://target.com'
        
        if origin and not origin.startswith(allowed_origin):
            abort(403)
        elif not origin and referer and not referer.startswith(allowed_origin):
            abort(403)
        # If both absent: may need to block or allow based on risk tolerance

# IMPORTANT: Origin and Referer checks are supplementary, not primary!
# These can be bypassed (see note 05 - Referer bypass techniques)
# Always use CSRF tokens as primary defense!
```

---

## Defense Layer 5 — Require Re-Authentication for Critical Actions

```
FOR HIGH-RISK ACTIONS, REQUIRE PASSWORD CONFIRMATION:
  ✓ Email change → require current password
  ✓ Password change → require current password
  ✓ Enable/disable 2FA → require password
  ✓ Add payment methods → require password
  ✓ Delete account → require password
  
EFFECT ON CSRF:
  Attacker can forge the request, but can't forge the password!
  Unless they also have the password via phishing/credential theft.
  
  This is defense-in-depth that makes CSRF → ATO nearly impossible.
```

---

## Common Mistakes to Avoid

```
MISTAKE 1: Token in URL parameter
  BAD: GET /change-email?email=x&csrf=TOKEN
  → TOKEN leaks in Referer headers! Logs! Browser history!
  GOOD: Token in hidden form field or custom header

MISTAKE 2: Token not tied to session
  BAD: Any valid token from any session works!
  GOOD: token = session['user_id'] + session['random']

MISTAKE 3: Validate only on some requests
  BAD: Checking token for /admin but not /settings/change-email
  GOOD: Validate on ALL state-changing requests

MISTAKE 4: Token reuse without rotation
  BAD: Same token for entire account lifetime
  GOOD: Rotate on sensitive action OR per-form token
  (Per-request rotation can break back button; per-session is common)

MISTAKE 5: Accepting GET for state changes
  BAD: GET /delete?id=123 deletes a record
  GOOD: Delete requires POST with CSRF token

MISTAKE 6: Using request body origin detection alone
  BAD: Trust "origin" in JSON body
  GOOD: Check HTTP headers, not attacker-controlled body!
```

---

## Defense Checklist

```
CSRF PROTECTION CHECKLIST:
  [ ] CSRF token on every state-changing form
  [ ] Token is cryptographically random (use secrets.token_hex / random_bytes)
  [ ] Token tied to user session (not global pool)
  [ ] Token validated on server side for every POST/PUT/DELETE/PATCH
  [ ] Token NOT in URL (use hidden form field or header)
  [ ] SameSite=Lax or Strict on session cookie
  [ ] HttpOnly on session cookie (XSS can't steal it)
  [ ] Secure flag on session cookie (HTTPS only)
  [ ] Critical actions require password re-entry
  [ ] GET endpoints are truly idempotent (no state changes!)
  [ ] CSRF protection in frameworks is enabled (not disabled accidentally)
  [ ] Test CSRF bypass techniques (notes 05 and 06) against your implementation
```

---

## Framework-Specific Notes

```
DJANGO: Has built-in CSRF middleware ({% csrf_token %} in templates)
  → Ensure middleware is enabled in MIDDLEWARE setting
  → Ensure @csrf_exempt is NOT applied to sensitive views

RAILS: authenticity_token built-in for forms
  → protect_from_forgery with: :exception (default in Rails 5+)
  → Do NOT use protect_from_forgery with: :null_session on auth endpoints

LARAVEL: @csrf blade directive / csrf_field() helper
  → VerifyCsrfToken middleware enabled by default
  → Don't add sensitive routes to $except list in middleware

EXPRESS: Use csurf middleware (or helmet CSRF protection)
  → Configure for cookie-based or session-based tokens

SPRING: CsrfFilter enabled by default in Spring Security
  → Do NOT disable it with csrf().disable() on protected endpoints
```

---

## Related Notes
- [[01 - What is CSRF]] — fundamentals
- [[05 - CSRF Token Bypass Techniques]] — how tokens get bypassed
- [[06 - SameSite Cookie Bypass]] — SameSite bypass techniques
- [[09 - CSRF to Account Takeover]] — what happens when defenses fail
