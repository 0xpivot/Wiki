---
tags: [vapt, oauth, oidc, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.19 OpenID Connect (OIDC) Attack Surface"
---

# 19.19 — OpenID Connect (OIDC) Attack Surface

## OIDC vs OAuth: The Difference

```
OAUTH 2.0: Authorization framework
  → "Can this app access my files?"
  → Answers: WHO CAN DO WHAT
  → Grants access tokens for API calls
  
OPENID CONNECT (OIDC): Authentication layer on top of OAuth 2.0
  → "Who is this user?"
  → Answers: WHO IS THIS PERSON
  → Adds ID tokens (JWTs) with user identity info
  
BUILT ON TOP OF OAUTH:
  Uses same flows (auth code, implicit, etc.)
  ADDS:
  - scope=openid (triggers OIDC behavior)
  - ID Token (JWT with identity claims)
  - UserInfo endpoint (/userinfo)
  - Discovery document (/.well-known/openid-configuration)
  - Standard claims (sub, email, name, picture, etc.)
```

---

## OIDC Specific Components

```
1. ID TOKEN (a JWT):
   {
     "iss": "https://accounts.google.com",  ← issuer
     "sub": "10769150350006150715113082367", ← subject (user ID)
     "aud": "YOUR_CLIENT_ID",               ← audience (must match client_id!)
     "exp": 1735689600,                     ← expiry
     "iat": 1735686000,                     ← issued at
     "email": "user@gmail.com",
     "email_verified": true,
     "name": "John Doe",
     "picture": "https://...profile.jpg"
   }
   
   Signed by OIDC provider → verifiable
   Contains: WHO the user is (unlike access token: WHAT they can do)

2. DISCOVERY DOCUMENT:
   GET /.well-known/openid-configuration
   → Returns JSON with all endpoints, supported algorithms, JWKS URI
   
3. USERINFO ENDPOINT:
   GET /userinfo
   Authorization: Bearer ACCESS_TOKEN
   → Returns current user info (email, name, etc.)

4. JWKS ENDPOINT:
   GET /.well-known/jwks.json  (or URL from discovery)
   → Public keys used to verify ID token signatures
```

---

## Attack 1: ID Token Validation Failures

```
CRITICAL VALIDATIONS THAT ARE OFTEN SKIPPED:

1. SIGNATURE VALIDATION:
   App receives ID token but doesn't verify signature!
   → Attacker can forge any ID token:
   {"alg":"none"} → sign with nothing
   {"iss":"https://attacker.com"} → sign with attacker's key
   
   WHAT SHOULD BE DONE:
   Fetch JWKS from discovery → verify signature using provider's public key

2. ISS (ISSUER) VALIDATION:
   Token claims iss=https://accounts.google.com
   App must verify: is this issuer trusted by our app?
   
   ATTACK: Attacker creates OIDC provider at https://attacker.com
   Claims iss=https://attacker.com
   If app doesn't check iss → accepts attacker's ID token!
   
3. AUD (AUDIENCE) VALIDATION:
   Token aud must match YOUR client_id exactly!
   
   ATTACK: Attacker registers another app at same OIDC provider
   Gets ID token for victim user → aud=ATTACKER_APP_ID
   If target app doesn't check aud → accepts token meant for attacker's app!
   
4. EXP VALIDATION:
   Expired token should be rejected → check exp!
   
5. NONCE VALIDATION:
   App sends random nonce in auth request
   OIDC provider includes it in ID token
   App must verify nonce matches what was sent
   → Prevents replay of old ID tokens
   
TESTING:
  Decode received ID token (base64url)
  Modify claims (sub, email, iss)
  Try submitting modified token (with alg=none)
  → If accepted → validation failure!
```

---

## Attack 2: Sub vs Email for Identity Binding

```
THE SUB CLAIM IS THE USER'S PERMANENT IDENTITY:
  sub = stable, unique ID within the provider
  email = can change!
  
BAD PRACTICE — Binding by email:
  App does: SELECT * FROM users WHERE email = id_token.email
  
  ATTACK 1: Email reuse
  - User deletes Google account
  - New user gets same Gmail address
  - New user logs in → gets OLD user's account!
  
  ATTACK 2: Email claim manipulation
  - OIDC provider allows unverified email
  - Attacker creates account with email=victim@target.com (unverified)
  - Gets ID token with email=victim@target.com, email_verified=false
  - App doesn't check email_verified → treats as victim!
  
GOOD PRACTICE:
  Bind by: (iss, sub) pair
  "Google user 10769150350006150715113082367" = always the same person
  Table: oidc_identities { provider_iss, provider_sub, app_user_id }
  
  ALWAYS REQUIRE: email_verified=true if matching by email at all
```

---

## Attack 3: OIDC Provider Confusion

```
MULTI-PROVIDER APPS:
  App supports: Google, Facebook, GitHub OIDC
  
  All can claim email=user@gmail.com
  
  ATTACK:
  1. Create GitHub account with email=victim@gmail.com (victim's Gmail)
  2. Log in via GitHub OIDC → GitHub issues ID token with email=victim@gmail.com
  3. App does: SELECT * FROM users WHERE email = 'victim@gmail.com'
  4. Finds victim's account (created via Google) → logged in as victim!
  
  This is PROVIDER CONFUSION:
  GitHub's email claim for one person ≠ Google's email claim for same address
  
FIX:
  Bind by: provider + sub (not just email)
  "Google/10769..." is different from "GitHub/67890..."
  Even if same email → different accounts unless explicitly linked
```

---

## Attack 4: Discovery Document Tampering / SSRF

```
OIDC DISCOVERY:
  App fetches: https://accounts.google.com/.well-known/openid-configuration
  Gets: jwks_uri, token_endpoint, userinfo_endpoint, etc.
  
ATTACK SURFACE:
  If attacker can influence the issuer URL the app uses for discovery:
  → Point to attacker's OIDC provider
  → Return attacker's JWKS, endpoints
  → Attacker controls what "Google" says the user is!
  
  ALSO: SSRF via jwks_uri
  App fetches JWKS from URL in discovery document
  If app doesn't validate this URL:
  → jwks_uri=http://internal.service/ → SSRF!
  → Like JWT jku injection (note 08 in JWT module)
  
TESTING:
  Does app fetch the discovery document dynamically or cache it?
  Is there an "iss" or "provider_url" parameter you can control?
  Try setting it to your OIDC provider
```

---

## OIDC Claims Reference for Pentesting

```
CLAIMS TO INSPECT IN ID TOKENS:

  iss     → Trusted issuer? Validate exact match
  sub     → Unique user ID (use this for account binding!)
  aud     → Must match YOUR client_id
  exp     → Must be in the future
  iat     → When issued (check for replay with old tokens)
  nonce   → Must match what you sent (prevents replay)
  
  email         → May change → don't use as primary identifier
  email_verified → MUST be true to trust email claim
  phone_number  → Similarly, check phone_number_verified
  
  amr   → Authentication methods (password, mfa, etc.)
         → "pwd" only → user just used password, no MFA
         → Useful: some apps require "mfa" in amr for sensitive ops
         
  acr   → Authentication context class reference
         → Level of assurance of authentication
         
TESTING APPROACH:
  1. Decode ID token → inspect all claims
  2. What does app use for identity? sub? email?
  3. Modify claims → does app reject invalid tokens?
  4. Check email_verified enforcement
```

---

## Fix

```
CORRECT OIDC IMPLEMENTATION:

1. VALIDATE ID TOKEN PROPERLY:
   Python (using authlib or similar):
   from authlib.integrations.requests_client import OAuth2Session
   
   # Fetch JWKS and validate:
   def validate_id_token(id_token, client_id, issuer):
       jwks_uri = discover_jwks_uri(issuer)  # from /.well-known/openid-configuration
       jwks = fetch_jwks(jwks_uri)
       
       claims = jwt.decode(
           id_token,
           jwks,
           claims_options={
               "iss": {"essential": True, "value": issuer},
               "aud": {"essential": True, "value": client_id},
               "exp": {"essential": True},
               "sub": {"essential": True},
           }
       )
       return claims

2. BIND ACCOUNTS BY (iss, sub) NOT EMAIL:
   # Store: { provider_iss: "https://accounts.google.com", 
   #          provider_sub: "10769150350006150715113082367",
   #          app_user_id: 42 }

3. REQUIRE email_verified:
   if not claims.get('email_verified'):
       raise ValueError("Email not verified by OIDC provider")

4. VALIDATE NONCE:
   # Generate nonce, store in session, include in auth request
   # Verify nonce in ID token matches session nonce
   if claims.get('nonce') != session.pop('oidc_nonce', None):
       raise ValueError("Nonce mismatch!")

5. CACHE DISCOVERY DOCUMENT SAFELY:
   # Don't refetch on every request → cache for 24h
   # But verify cache is for the EXPECTED issuer
   # Don't allow user-controlled issuer URLs
```

---

## Related Notes
- [[01 - OAuth 2.0 Overview and Flow Types]] — OAuth vs OIDC
- [[18 - JWT — What is a JWT]] — ID tokens are JWTs
- [[18 - JWT — Algorithm None Attack]] — ID token forgery
- [[12 - Account Linking Abuse]] — email-based account confusion
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
