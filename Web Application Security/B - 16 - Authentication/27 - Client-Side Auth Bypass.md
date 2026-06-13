---
tags: [vapt, authentication, javascript, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.27 Client-Side Auth Bypass (JavaScript checks)"
---

# 16.27 — Client-Side Auth Bypass

## What Is Client-Side Auth?

```
CLIENT-SIDE AUTHENTICATION:
  Using JavaScript to control access — without server verification!
  
  EXAMPLES:
  - JavaScript checks if a cookie exists → shows/hides menu items
  - JavaScript decodes a JWT → reads "isAdmin": false → hides admin panel
  - JavaScript checks localStorage.getItem('loggedIn') === 'true'
  - Redirect to /login based on a JavaScript check (no server enforce)
  
THE PROBLEM:
  Attacker can see and modify JavaScript code!
  Or: make requests directly to "hidden" APIs (bypassing JS entirely)
  
  JavaScript = enforced only in the browser, by the browser
  Server knows nothing about what JavaScript "decided"
  → Server must ALWAYS verify auth, regardless of client
```

---

## Common Client-Side Auth Patterns

### 1. JavaScript-Only Redirect

```javascript
// VULNERABLE CODE:
if (!localStorage.getItem('authToken')) {
    window.location.href = '/login';  // only redirect, no server check!
}

// BYPASS:
// Method 1: Set the token manually:
localStorage.setItem('authToken', 'anything');
// Refresh page → redirect doesn't fire → access the page!

// Method 2: Pause execution before redirect:
// Open DevTools → Sources → set breakpoint on redirect line
// Pause → inspect page content before redirect fires!

// Method 3: Access API directly (bypass frontend entirely):
// The JavaScript may redirect, but the API endpoints are still accessible:
fetch('/api/admin/users').then(r => r.json()).then(console.log)
// → Server might respond with data if no server-side auth!
```

### 2. Role Stored in Client

```javascript
// VULNERABLE: Role stored in cookie or localStorage
const userRole = localStorage.getItem('role');  // 'user'

if (userRole === 'admin') {
    document.getElementById('adminPanel').style.display = 'block';
}

// BYPASS: Change the stored role:
localStorage.setItem('role', 'admin');
// Refresh → admin panel visible!

// BUT DOES THE SERVER VERIFY ON API CALLS?
// Try: POST /api/admin/delete-user
// If server checks session role (server-side) → blocked!
// If server trusts a role parameter in request body → vulnerable!
```

### 3. JWT Read Client-Side Only

```javascript
// VULNERABLE: JWT decoded client-side, not verified server-side
const token = getCookie('auth');
const payload = JSON.parse(atob(token.split('.')[1]));

if (payload.isAdmin) {
    // show admin UI
}

// Server should verify JWT signature AND check role server-side!
// If server doesn't: forge JWT with isAdmin:true → bypass!
// (See Module: JWT for JWT attack details)
```

---

## Testing Methodology

```
STEP 1: View Page Source / JavaScript
  Ctrl+U → search for:
  - "isAdmin", "role", "admin", "auth"
  - "redirect", "window.location", "href"
  - localStorage, sessionStorage, cookies referenced in JS
  
STEP 2: Browser DevTools
  Console → type: localStorage.getItem('role')
  Change: localStorage.setItem('role', 'admin')
  
STEP 3: Try Direct API Calls
  Even if frontend hides the button, try the API:
  Burp → Repeater → POST /api/admin/users
  Does it return data without server-side auth check?
  
STEP 4: Burp Spider / Content Discovery
  Find admin endpoints not linked from the main page
  feroxbuster -u https://target.com/admin/ -w wordlist.txt

STEP 5: Network Tab
  Open DevTools → Network → trigger hidden actions via JS
  Look for API calls made by admin UI → copy and replay without auth!
```

---

## Bypass Examples

```bash
# BYPASS JAVASCRIPT REDIRECT VIA CURL:
# Frontend redirects to /login in JavaScript
# But actual page content exists server-side:
curl https://target.com/admin/dashboard
# Does server return admin content? → Client-only redirect!

# MANIPULATE COOKIE TO FAKE ROLE:
# Cookie: role=user
# Try: role=admin
curl https://target.com/admin \
  -H "Cookie: session=VALID_SESSION; role=admin"

# JAVASCRIPT DISABLED:
# In Firefox: about:config → javascript.enabled → false
# Visit protected page → if it loads without JS-based redirect → bypass!

# DEVTOOLS BREAKPOINT:
# Sources tab → find the redirect line
# Click line number → breakpoint set
# Page loads → pauses before redirect
# DevTools Console: examine page content!
```

---

## Fix

```
THE RULE:
  Every access control check MUST be enforced server-side!
  Client-side checks = UX only (hide buttons, improve experience)
  Client-side checks = NEVER security
  
SERVER-SIDE ENFORCEMENT:
  # Every API endpoint checks auth:
  @app.route('/api/admin/users')
  @require_admin  # decorator that checks session server-side
  def get_admin_users():
      ...
  
  # Middleware on every protected route:
  if not request.user.is_authenticated():
      return redirect(401)
  if not request.user.has_role('admin'):
      return abort(403)
      
NEVER TRUST:
  ✗ JavaScript localStorage values
  ✗ Cookies without server-side validation
  ✗ Client-controlled role parameters in request body
  ✗ JWT claims without signature verification
```

---

## Related Notes
- [[11 - MFA Bypass Response Manipulation]] — another client-side trust issue
- [[Module: JWT]] — JWT client-side auth bypass
- [[Module: Access Control]] — proper RBAC implementation
