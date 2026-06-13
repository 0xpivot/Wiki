---
tags: [vapt, oauth, csrf, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.06 OAuth State Parameter — CSRF in OAuth"
portswigger_labs: ["Forced OAuth profile linking"]
---

# 19.06 — OAuth State Parameter: CSRF in OAuth

## What Is the state Parameter?

```
STATE PARAMETER:
  Anti-CSRF token for OAuth flows
  
  CLIENT GENERATES: random_state = random_token_value
  CLIENT STORES: session['oauth_state'] = random_state
  CLIENT INCLUDES IN REQUEST:
    https://auth.example.com/oauth/authorize?...&state=random_state
    
  AUTH SERVER RETURNS IT UNCHANGED:
    https://app.example.com/callback?code=AUTH_CODE&state=random_state
    
  CLIENT MUST VALIDATE:
    if state != session['oauth_state']: REJECT!
    del session['oauth_state']  # use once!
```

---

## What Happens Without State Validation

```
OAUTH CSRF ATTACK:
  Attacker initiates OAuth flow with their own account at auth server
  Gets auth code (but doesn't complete — pauses at callback)
  
  Attacker's callback URL:
  https://app.example.com/callback?code=ATTACKER_CODE&state=IGNORED
  
  Attacker creates CSRF page that triggers victim's browser to visit:
  https://app.example.com/callback?code=ATTACKER_CODE
  
  Victim's browser visits → app processes code → exchanges for tokens
  → Attacker's Google account linked to victim's account!
  → Or: Victim logged into attacker's profile!
  
IMPACT DEPENDS ON CONTEXT:
  "Login with Google" flow:
  → Victim is now logged in as attacker's profile!
  → Victim thinks they're in their own account
  → Enters sensitive data → goes to attacker!
  
  "Link Google account" flow:
  → Victim's existing account linked to attacker's Google!
  → Attacker can log in via Google → victim's account!
  → Account takeover!
```

---

## Testing State Parameter

```
STEP 1: Start OAuth flow
  Note the state parameter in the redirect URL:
  https://auth.google.com/oauth?...&state=abc123xyz

STEP 2: After Google authentication, note the callback URL:
  https://app.example.com/callback?code=CODE&state=abc123xyz

STEP 3: TEST A — Remove state:
  Visit: https://app.example.com/callback?code=CODE
  (No state parameter)
  → Login succeeds? → State not validated!

STEP 4: TEST B — Wrong state value:
  Visit: https://app.example.com/callback?code=CODE&state=WRONG_VALUE
  → Login succeeds? → State not checked!

STEP 5: TEST C — State from different session:
  Browser A: Get state = abc123
  Browser B: Start new OAuth flow (get state = xyz789)
  Browser B: Complete OAuth → callback: ?code=CODE&state=xyz789
  
  Now: try using Browser A's code with Browser B's state:
  https://app.example.com/callback?code=BROWSER_A_CODE&state=xyz789
  → If accepted → state not tied to session!

CONFIRMING IMPACT:
  1. Your own test account → complete OAuth → get your OAuth callback URL
  2. CSRF victim into visiting your callback URL
  3. See what account the victim is now logged in as
```

---

## CSRF to Account Takeover via OAuth Linking

```
HIGH-IMPACT SCENARIO:
  App allows linking OAuth identity to existing account
  
  ATTACK:
  1. Attacker starts "Link Google" flow → gets callback URL
  2. CSRF victim into visiting: /oauth/callback?code=ATTACKER_CODE
  3. Victim's account now linked to ATTACKER'S Google identity
  4. Attacker uses Google → logs into victim's account
  
  This is especially dangerous because:
  - No user interaction needed after the CSRF
  - Victim doesn't notice (account still works normally)
  - Attacker has persistent access via OAuth even if victim changes password!
  
DETECTION:
  Look for any endpoint that links OAuth to existing accounts
  Test if state validation is present on the linking callback
```

---

## Fix

```
IMPLEMENTING STATE VALIDATION:

Python (Flask):
  import secrets
  
  @app.route('/oauth/start')
  def oauth_start():
      state = secrets.token_urlsafe(32)
      session['oauth_state'] = state
      auth_url = f"https://auth.example.com/oauth/authorize?...&state={state}"
      return redirect(auth_url)
  
  @app.route('/oauth/callback')
  def oauth_callback():
      returned_state = request.args.get('state')
      stored_state = session.pop('oauth_state', None)  # pop = use once!
      
      if not stored_state or returned_state != stored_state:
          abort(400, "State mismatch — possible CSRF attack!")
      
      # Only proceed if state matches!
      code = request.args.get('code')
      # ... exchange code for tokens ...

Node.js:
  app.get('/oauth/start', (req, res) => {
      const state = crypto.randomBytes(32).toString('hex');
      req.session.oauthState = state;
      res.redirect(`https://auth.example.com/oauth/authorize?...&state=${state}`);
  });
  
  app.get('/oauth/callback', (req, res) => {
      const { code, state } = req.query;
      if (!state || state !== req.session.oauthState) {
          return res.status(400).send('State mismatch!');
      }
      delete req.session.oauthState;  // use once!
      // ... proceed ...
  });

REQUIREMENTS:
  ✓ State = cryptographically random (32 bytes minimum)
  ✓ Store in session (not cookie or URL)
  ✓ Validate on EVERY callback
  ✓ Delete after use (prevent replay)
  ✓ For account linking: add CSRF token to the link initiation too
```

---

## Related Notes
- [[16.20 - OAuth Login CSRF]] — login-specific OAuth CSRF
- [[12 - Account Linking Abuse]] — exploiting account linking
- [[18 - OAuth to Account Takeover Chain]] — full ATO chain
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
