---
tags: [vapt, session-management, intermediate]
difficulty: intermediate
module: "17 - Session Management"
topic: "17.06 Session Puzzle / Session Confusion"
---

# 17.06 — Session Puzzle / Session Confusion

## What Is Session Puzzle?

```
SESSION PUZZLE (also called Session Variable Overloading):
  App uses session variables in different flows/pages
  Two different flows share or overwrite each other's session variables
  
  RESULT:
  An attacker can use one flow to set session state
  that another flow trusts, bypassing security checks!

EXAMPLE:
  /forgot-password flow sets:  session['user_id'] = email_lookup_result
  /login flow also reads:      session['user_id'] to know who's logged in
  
  Attack: Use forgot-password to set session['user_id'] to victim's ID
  → Then access /account (which reads session['user_id'])
  → Logged in as victim WITHOUT knowing their password!
```

---

## Classic Session Puzzle Attack

```
STEP 1: Understand what session variables each flow sets

STEP 2: Find a flow that sets a privileged variable:
  /forgot-password?email=victim@example.com
  → Sets session['user_email'] = "victim@example.com"
  → Sets session['reset_requested'] = True
  
STEP 3: Find another flow that reads the same variable with different meaning:
  /login success:
  → Sets session['user_email'] = logged_in_user
  → Grants access to account
  
STEP 4: Use forgot-password to set the value, then access account page:
  GET /forgot-password?email=victim@example.com  → sets session var
  GET /account  → reads session['user_email'] → shows victim's account!

REAL EXAMPLE (simplified):
  Registration: POST /register → sets session['pending_user'] = new_user_id
  Login:        GET /dashboard → checks if session['user_id'] OR session['pending_user']
  
  Attacker registers as normal user → session['pending_user'] = attacker_id
  Attacker then visits /dashboard → app checks pending_user → thinks it's logged in!
```

---

## Testing for Session Confusion

```
METHODOLOGY:
  
  STEP 1: Map all flows that USE session:
  - Login, registration, forgot password, email verification
  - Multi-step forms (checkout, wizard steps)
  - OAuth flows
  
  STEP 2: For each flow, note what session variables are set:
  - Login: session[user_id] = X, session[role] = Y
  - ForgotPW: session[reset_email] = Z
  - Registration: session[unverified_user] = W
  
  STEP 3: Look for overlapping variable names used differently
  
  STEP 4: Test cross-flow pollution:
  - Complete step 1 of flow A → check if it affects flow B
  - Example: Start password reset for victim → then try to access /account
  - Example: Start registration → skip to dashboard
```

---

## Password Reset Session Pollution

```
COMMON VULNERABILITY PATTERN:

App stores reset candidate in session:
  POST /forgot-password
  Body: email=victim@example.com
  
  Server: session['reset_user_id'] = 42  ← victim's user_id!
  Redirects to: GET /forgot-password/verify  (enter the token)
  
BUT:
  GET /account reads: session.get('user_id') or session.get('reset_user_id')
  → Both treated as "current user"!
  
Attacker:
  1. POST /forgot-password (email=victim@example.com)
  2. GET /account
  → /account sees reset_user_id = 42 → shows victim's account!

TEST:
  1. Send forgot password for victim
  2. Without entering any code, navigate to /account
  3. Whose account do you see?
```

---

## Multi-Step Form Session Confusion

```
CHECKOUT FLOW EXAMPLE:
  Step 1: Add to cart → session['cart_items'] = [...]
  Step 2: Enter address → session['delivery_address'] = X
  Step 3: Enter payment → session['payment_method'] = Y
  Step 4: Confirm → process session['cart_items'] for session['user_id']
  
CONFUSION ATTACK:
  What if an anonymous user sets session variables via step 1-3,
  then a logged-in user completes step 4?
  
  If session is shared or confused:
  → Wrong cart processed for the logged-in user
  → Or: anonymous user's address used → information leak

SKIPPING STEPS:
  Try accessing step 3 or step 4 directly without completing steps 1 and 2
  → Missing session variables handled gracefully?
  → Or does it process with null/default values that have security implications?
```

---

## Fix

```
DEFENSES:
  ✓ Use separate, clearly named session variables per flow
  ✓ Don't share session variable names across different flows
  ✓ Clear session variables after each flow completes:
    del session['reset_user_id']  after password reset completes
    
  ✓ Separate session namespaces:
    session['auth']['user_id']    for authentication state
    session['reset']['user_id']   for password reset state
    session['checkout']['...]     for checkout state
    
  ✓ After login: clear all non-auth session variables
    → Prevents pre-set variables from previous flows affecting auth
    
  ✓ Verify flow completeness before trusting state:
    Don't trust session['checkout_complete'] at step 4
    Verify all previous steps actually completed!
```

---

## Related Notes
- [[01 - What is a Session]] — session fundamentals
- [[03 - Session Fixation]] — related session manipulation attack
- [[08 - Session Not Invalidated on Logout]] — session lifecycle
- [[15 - Defense Secure Session Configuration]] — full hardening
