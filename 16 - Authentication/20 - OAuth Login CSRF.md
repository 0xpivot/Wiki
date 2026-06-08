---
tags: [vapt, authentication, oauth, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.20 OAuth Login CSRF"
portswigger_labs: ["CSRF via OAuth"]
---

# 16.20 — OAuth Login CSRF

## OAuth Login Flow Overview

```
OAUTH 2.0 AUTHORIZATION CODE FLOW:
  1. User clicks "Login with Google"
  2. App redirects to Google:
     https://accounts.google.com/oauth?
       client_id=APP_ID&
       redirect_uri=https://example.com/callback&
       response_type=code&
       state=RANDOM_STATE_VALUE    ← anti-CSRF!
       scope=email profile
       
  3. User authenticates at Google → Google redirects back:
     https://example.com/callback?
       code=AUTH_CODE&
       state=RANDOM_STATE_VALUE    ← must match!
       
  4. App exchanges code for token → logs user in
  
THE STATE PARAMETER = ANTI-CSRF TOKEN FOR OAUTH!
  Without state: attacker can CSRF the OAuth callback
```

---

## OAuth CSRF Attack

```
IF STATE PARAMETER IS MISSING OR NOT VALIDATED:

ATTACK:
  1. Attacker starts OAuth login flow with their own account
  2. Google redirects to attacker (they pause before step 3):
     https://example.com/callback?code=ATTACKERS_AUTH_CODE
     
  3. Attacker creates CSRF page that triggers:
     GET /callback?code=ATTACKERS_AUTH_CODE
     
  4. Victim visits attacker's page → victim's browser makes the request
  5. Victim's session is now linked to attacker's Google account!
  
  6. Attacker logs into their Google account on example.com
  7. → Attacker is logged in as VICTIM! (their session was linked to attacker's OAuth)
  
IMPACT:
  Account takeover via OAuth CSRF
  Victim's existing account linked to attacker's identity
```

---

## Testing OAuth CSRF

```
STEP 1: Start the OAuth flow (Login with Google/GitHub/etc.)
  Note the state parameter in the redirect URL

STEP 2: Arrive at the callback URL with state + code
  https://example.com/callback?code=xxx&state=yyy

STEP 3: TEST IF STATE IS VALIDATED:
  a) Remove state parameter:
     https://example.com/callback?code=xxx
     → If login succeeds → no state validation!
     
  b) Change state to wrong value:
     https://example.com/callback?code=xxx&state=WRONG
     → If login succeeds → state not validated!
     
  c) Use state from different session:
     Get state from your session
     Submit callback in a different browser (different session)
     → If it works → state not tied to session!

STEP 4: If state not validated → full OAuth CSRF possible!
```

---

## Account Linking CSRF

```
SCENARIO: App allows linking Google to existing account

FLOW:
  Logged-in user → "Link Google account" → OAuth flow → account linked
  
IF NO CSRF PROTECTION ON LINKING:
  1. Attacker gets code from their own Google OAuth flow (pauses at callback)
  2. CSRF victim into visiting: /link-google?code=ATTACKER_CODE&state=VALID_STATE
  3. Victim's existing account gets linked to attacker's Google identity!
  4. Attacker logs in via Google → lands in VICTIM's account!
  
THIS IS ACCOUNT TAKEOVER VIA OAUTH LINKING CSRF!
  
TEST:
  - Start "link Google" flow
  - Complete Google auth but pause at callback
  - Note callback URL
  - CSRF victim into visiting the callback URL
  - Does their account get linked to your Google identity?
```

---

## Real HTTP Example

```http
--- STEP 1: ATTACKER GENERATES THEIR OWN OAUTH CODE ---
GET /auth/google/callback?code=4/ATTACKER_CODE&state=IGNORED HTTP/1.1
Host: victim.example.com
Cookie: (VICTIM's session!)

--- IF THIS RESPONSE REDIRECTS TO DASHBOARD ---
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: auth_token=...

--- THEN VICTIM IS LOGGED IN AS ATTACKER ---
```

---

## Fix

```
DEFENSES:
  ✓ ALWAYS use the state parameter:
    state = generate_secure_random_token()
    session['oauth_state'] = state
    → Include in authorization URL
    
  ✓ VALIDATE state on callback:
    if request.params.state != session['oauth_state']:
        abort(400, "State mismatch — CSRF attack?")
    del session['oauth_state']  # use once!
    
  ✓ PKCE (Proof Key for Code Exchange):
    For public clients, use PKCE instead of/in addition to state
    
  ✓ Bind state to session (not just cookie):
    Ensure state from session A can't be used in session B
```

---

## Related Notes
- [[16 - Login CSRF]] — regular login CSRF
- [[Module 11 - CSRF]] — CSRF fundamentals
- [[Module: JWT]] — another OAuth-related token attack
- [[Module: OAuth]] — deep dive on OAuth attack surface
