---
tags: [vapt, access-control, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.12 Parameter Tampering (role=admin, isAdmin=true)"
portswigger_labs: ["User role controlled by request parameter"]
---

# 21.12 — Parameter Tampering (role=admin, isAdmin=true)

## What Is Parameter Tampering?

```
PARAMETER TAMPERING:
  Modifying request parameters to change application behavior
  
  SPECIFICALLY FOR ACCESS CONTROL:
  Sending parameters that indicate privilege level
  And server trusts them without server-side verification
  
  COMMON PARAMETERS TO TAMPER:
  role=admin         → privilege level
  isAdmin=true       → boolean admin flag
  user_type=staff    → user type
  level=9            → numeric privilege level
  permission=all     → permission set
  admin=1            → numeric boolean
  group=admin        → group membership
  
  LOCATIONS:
  Query string: ?role=admin
  POST body:    role=admin
  Cookies:      role=admin (covered in note 06)
  JSON body:    {"role": "admin"}
  Hidden form fields: <input type="hidden" name="role" value="user">
```

---

## Finding Parameters to Tamper

```
STEP 1: LOOK FOR ROLE/PRIVILEGE PARAMETERS IN:

Query strings:
  /profile?user_type=standard → try user_type=premium, user_type=admin

POST bodies:
  POST /purchase → role=standard → try role=vip, role=staff

Hidden form fields:
  <input type="hidden" name="role" value="user">
  → In Burp, unhide and modify before submitting

URL path (role in path):
  /users/standard/dashboard → try /users/admin/dashboard

Cookies (see note 06):
  Cookie: role=user → try role=admin

JSON API bodies:
  {"user_type": "free"} → {"user_type": "premium"} or {"user_type": "admin"}
  
STEP 2: NOTE WHAT PARAMETERS APPEAR IN API RESPONSES:
  GET /api/me → {"role": "user", "is_admin": false}
  → Try sending: {"is_admin": true} in POST body updates
```

---

## Common Tamper Targets

```
isAdmin / is_admin:
  Original request: isAdmin=false (or not included)
  Tampered:         isAdmin=true
  → Does app grant admin access? → Vertical escalation!

role / user_role:
  Original: role=user
  Tampered: role=admin, role=superadmin, role=staff, role=moderator
  → Which values exist? (Check docs or try common values)

accountType / account_type:
  Original: accountType=free
  Tampered: accountType=premium, accountType=enterprise
  → Unlock premium features without paying!

verified / email_verified:
  Original: verified=false (email not yet verified)
  Tampered: verified=true
  → Bypass email verification requirement!

active / enabled:
  Original: active=false (account disabled)
  Tampered: active=true
  → Re-enable disabled account!

accessLevel / level:
  Original: level=1
  Tampered: level=9, level=999
  → Numeric privilege escalation!
```

---

## Testing Parameter Tampering

```bash
# STEP 1: FIND PRIVILEGE-RELATED PARAMETERS
# Scan forms for hidden fields:
# In Burp: right-click response → "Show response in browser" → view source
# Look for <input type="hidden" name="role">

# Scan POST bodies in Burp proxy history:
# Filter by method=POST → search body for "role|admin|type|level|permission"

# STEP 2: TEST IN BURP REPEATER

# Example 1: Query parameter tampering
GET /dashboard?user_type=standard HTTP/1.1
Host: target.com
Cookie: session=YOUR_SESSION
→ Repeat with: ?user_type=admin

# Example 2: POST body tampering (form)
POST /register HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
name=John&email=john@example.com&role=user
→ Change: role=admin

# Example 3: POST body tampering (JSON)
POST /api/profile/update HTTP/1.1
Content-Type: application/json
{"name": "John", "user_type": "standard"}
→ Change: {"name": "John", "user_type": "admin"}

# STEP 3: CHECK RESPONSE
# Any change in response? → elevated access? → BUG!
# "isAdmin": true in response? → confirmed privilege escalation!

# STEP 4: TRY BONUS PARAMETERS (not in original request):
# Add parameters that weren't there:
POST /login
{"username": "john", "password": "pass", "admin": true, "bypass_2fa": true}
# → Does adding these parameters change behavior? → Parameter injection bug!
```

---

## Hidden Form Field Tampering

```
HTML FORM WITH HIDDEN FIELDS:
  <form method="POST" action="/buy">
    <input type="text" name="product_id" value="123">
    <input type="hidden" name="price" value="99.99">
    <input type="hidden" name="user_type" value="standard">
    <button type="submit">Buy Now</button>
  </form>
  
  PROBLEM: Hidden fields are in the DOM → user can modify them!
  
  ATTACK:
  In Browser DevTools:
  $('input[name=price]').val('0.01')      → price manipulation!
  $('input[name=user_type]').val('admin') → role escalation!
  
  Or in Burp: intercept POST → modify hidden field values
  
  SERVER MUST VALIDATE:
  Never trust price from form → look up price from DB by product_id!
  Never trust role from form → get from server-side session!
  
  FINDING IN BURP:
  POST /buy HTTP/1.1
  Content-Type: application/x-www-form-urlencoded
  product_id=123&price=99.99&user_type=standard
  → Modify price to 0.01 → does purchase go through at $0.01?
  → Modify user_type → does it affect access?
```

---

## Fix

```
NEVER TRUST CLIENT-PROVIDED PRIVILEGE PARAMETERS:

BAD:
  @app.route('/dashboard')
  def dashboard():
      role = request.args.get('role', 'user')  # client-controlled!
      if role == 'admin':
          return render_admin_dashboard()
      return render_user_dashboard()

BAD:
  def purchase():
      price = float(request.form['price'])  # client-controlled!
      charge_card(price)

GOOD:
  @app.route('/dashboard')
  @require_login
  def dashboard():
      user = db.get_user(session['user_id'])  # from server-side session!
      if user.role == 'admin':
          return render_admin_dashboard()
      return render_user_dashboard()

GOOD:
  def purchase():
      product_id = request.form['product_id']
      product = db.get_product(product_id)  # look up price from DB!
      price = product.price  # never from client!
      charge_card(price)

RULE:
  Privilege, role, price, discount, any sensitive value:
  → Always from TRUSTED SERVER-SIDE SOURCE (database, session)
  → Never from client request (URL, body, cookie, header)
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — privilege escalation context
- [[08 - Mass Assignment Vulnerability]] — bulk parameter injection
- [[06 - IDOR in Cookies]] — cookie-based parameter tampering
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
