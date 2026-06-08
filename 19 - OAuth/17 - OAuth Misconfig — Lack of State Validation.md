---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.17 OAuth Misconfig — Lack of State Validation"
---

# 19.17 — OAuth Misconfig: Lack of State Validation

## The State Parameter Recap

```
STATE PARAMETER = OAUTH'S ANTI-CSRF MECHANISM

CORRECT FLOW:
  Client → generates random state → stores in session
  Client → sends state in auth request
  Auth server → echoes state back in callback
  Client → compares received state with stored state
           MISMATCH → REJECT!
           MATCH → proceed
  
WHAT BREAKS WITHOUT STATE VALIDATION:
  → OAuth CSRF attacks (see 19.06)
  → Session confusion attacks
  → Various redirect/code confusion attacks
  
  (This note covers the misconfigurations — WHY state validation fails,
   not just that it does)
```

---

## Misconfiguration 1: State Parameter Not Generated

```
MOST BASIC FAILURE:
  App initiates OAuth WITHOUT including state:
  
  https://auth.google.com/o/oauth2/auth?
    client_id=CLIENT_ID&
    redirect_uri=https://app.example.com/callback&
    response_type=code&
    scope=email
    (NO state parameter!)
  
  → App has nothing to validate against
  → Any code sent to callback will be accepted
  → OAuth CSRF trivially possible
  
  TESTING:
  Check the initial authorization URL in Burp
  Is state= parameter present?
  If not → state not generated → definitely not validated
```

---

## Misconfiguration 2: State Sent But Not Validated

```
SLIGHTLY LESS BASIC:
  App generates state, includes in request
  Auth server returns state in callback
  App receives state back... and ignores it!
  
  Code (vulnerable):
  @app.route('/callback')
  def callback():
      code = request.args.get('code')
      state = request.args.get('state')  # received...
      # ... but never compared with session['oauth_state']!
      token = exchange_code(code)  # just proceeds!
  
  TESTING:
  1. Start OAuth flow → note state value
  2. After auth, note callback URL
  3. Modify state to wrong value OR remove it
  4. Visit callback with wrong/no state
  → App still processes? → State received but not validated!
```

---

## Misconfiguration 3: Weak State (Predictable)

```
STATE MUST BE:
  - Cryptographically random (256 bits = 32 bytes min)
  - Unguessable by attacker
  
WEAK STATE EXAMPLES:
  state=1234                    ← sequential number
  state=USERID                  ← user's own ID
  state=TIMESTAMP               ← predictable
  state=abc (static value)      ← reused across requests!
  state=MD5(user_id)            ← deterministic, brute-forceable
  state=CRC32(session_id)       ← short/predictable
  
IMPACT OF WEAK STATE:
  Attacker can GUESS the state value
  → Craft CSRF page with correct state
  → CSRF protection bypassed!
  
TESTING:
  Generate multiple OAuth flows (different sessions)
  Collect state values
  Do they show a pattern? Length? Character set?
  Are they the same across flows? → static/reused!
```

---

## Misconfiguration 4: State Not Tied to Session

```
STATE MUST BE SESSION-BOUND:
  state value stored in: THIS user's THIS session
  
  If state is:
  - Stored in a global variable (all users share same state!)
  - Stored in localStorage (accessible via XSS)
  - Not deleted after use (replay attack)
  
  ATTACK SCENARIO (state not session-bound):
  User A starts OAuth → state=abc123
  Attacker also starts OAuth → state=def456
  
  Attacker drops their callback, gets state=def456
  Sends User A the callback with: ?code=ATTACKER_CODE&state=def456
  App checks: is def456 a valid state? Yes! (not bound to session)
  → Linked!
  
TESTING:
  Browser 1: Start OAuth → state=STATE_1
  Browser 2: Start OAuth → state=STATE_2
  
  Complete OAuth in Browser 2 → get callback URL with code+STATE_2
  
  Now: Take that callback URL (with code and STATE_2)
  Visit it in Browser 1's session
  → If it works → state not tied to session!
  
  (State from Browser 2 should only work in Browser 2's session)
```

---

## Misconfiguration 5: State Accepted After Use

```
SINGLE-USE REQUIREMENT:
  After validating state in callback → DELETE it from session!
  
  If state is not deleted:
  → Replay attack: same callback URL can be visited multiple times
  → Same code can be replayed (if code also reusable... layered bug)
  
  TESTING:
  Complete OAuth flow → let it succeed
  Immediately visit the SAME callback URL again
  → If second visit proceeds → state not invalidated after use!
```

---

## Complete Checklist for State Validation Testing

```bash
# AUTOMATED APPROACH IN BURP:

# 1. INTERCEPT AUTHORIZATION REQUEST:
# GET /oauth/authorize?...&state=CURRENT_STATE HTTP/1.1
# Note the state value

# 2. COMPLETE AUTH (get code):
# You'll get: /callback?code=CODE&state=CURRENT_STATE

# 3. TEST: Remove state entirely:
# Replay /callback?code=CODE (no state parameter)
# → 200/success = not validated!

# 4. TEST: Wrong state value:
# Replay /callback?code=CODE&state=WRONGVALUE
# → 200/success = state not checked!

# 5. TEST: State from different session (if you have two browsers):
# → Described above (session binding)

# 6. TEST: Reuse same callback URL:
# → Described above (single use)

# 7. TEST: Weak state - analyze multiple state values:
python3 -c "
states = ['STATE1', 'STATE2', 'STATE3']  # collect multiple
# Analyze:
lengths = set(len(s) for s in states)
print('Lengths:', lengths)
# Are they all same length? Short? Numeric only?
"
```

---

## Fix

```
CORRECT STATE IMPLEMENTATION:

import secrets
from flask import session, request, abort, redirect

@app.route('/oauth/start')
def oauth_start():
    # Generate cryptographically random state
    state = secrets.token_urlsafe(32)  # 256 bits of entropy
    
    # Store in server-side session (not localStorage, not URL)
    session['oauth_state'] = state
    
    auth_url = (
        f"https://auth.example.com/oauth/authorize?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=email&"
        f"state={state}"
    )
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    received_state = request.args.get('state')
    stored_state = session.pop('oauth_state', None)  # pop = single use!
    
    # MUST validate: present + matches + was something expected
    if not stored_state or not received_state:
        abort(400, "Missing state parameter")
    if not secrets.compare_digest(received_state, stored_state):
        abort(400, "State mismatch — possible CSRF attack")
    
    # Safe to proceed with code exchange
    code = request.args.get('code')
    # ...

REQUIREMENTS SUMMARY:
  ✓ Random: secrets.token_urlsafe(32) or os.urandom(32)
  ✓ Session-bound: stored in server-side session
  ✓ Single-use: pop from session after validation
  ✓ Always validated: no shortcuts or bypass conditions
  ✓ Constant-time compare: secrets.compare_digest (avoids timing attack)
```

---

## Related Notes
- [[06 - OAuth State Parameter — CSRF in OAuth]] — CSRF attacks using state weakness
- [[12 - Account Linking Abuse]] — account linking CSRF chain
- [[16 - OAuth Misconfig — Wildcard Redirect URI]] — related misconfig
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
