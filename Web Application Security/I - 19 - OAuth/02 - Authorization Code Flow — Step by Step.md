---
tags: [vapt, oauth, beginner]
difficulty: beginner
module: "19 - OAuth"
topic: "19.02 Authorization Code Flow — Step by Step"
---

# 19.02 — Authorization Code Flow: Step by Step

## The Full Flow

```
PARTICIPANTS:
  User → Browser → Client App → Authorization Server → Resource Server

STEP 1: USER INITIATES
  User clicks "Login with Google" on app.example.com

STEP 2: CLIENT REDIRECTS TO AUTH SERVER
  Browser redirected to:
  https://accounts.google.com/oauth/authorize?
    client_id=CLIENT_ID&
    redirect_uri=https://app.example.com/callback&
    response_type=code&
    scope=email+profile&
    state=RANDOM_CSRF_TOKEN

  PARAMETERS:
  client_id      → identifies the app to Google
  redirect_uri   → where Google sends user back
  response_type  → "code" = we want authorization code
  scope          → what we're requesting access to
  state          → anti-CSRF token (verify on return!)

STEP 3: USER AUTHENTICATES AND CONSENTS AT GOOGLE
  User logs into Google (if not already)
  Google shows: "app.example.com wants to: view your email, view your profile"
  User clicks Allow

STEP 4: AUTHORIZATION SERVER REDIRECTS BACK WITH CODE
  Browser redirected to:
  https://app.example.com/callback?
    code=AUTHORIZATION_CODE_abc123&
    state=RANDOM_CSRF_TOKEN   ← VERIFY THIS MATCHES!

  code: one-time, short-lived (10-60 seconds!), SINGLE-USE

STEP 5: CLIENT EXCHANGES CODE FOR TOKENS (SERVER-SIDE!)
  app.example.com server (backend) calls Google:
  POST https://oauth2.googleapis.com/token
  Content-Type: application/x-www-form-urlencoded
  
  code=AUTHORIZATION_CODE_abc123&
  client_id=CLIENT_ID&
  client_secret=CLIENT_SECRET&    ← NEVER in browser!
  redirect_uri=https://app.example.com/callback&
  grant_type=authorization_code

STEP 6: AUTH SERVER RETURNS TOKENS
  {
    "access_token": "ya29.XXXXX",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "1//XXXXX",
    "id_token": "eyJhbGci..."      (OIDC only)
  }

STEP 7: CLIENT USES ACCESS TOKEN TO GET USER INFO
  GET https://www.googleapis.com/oauth2/v2/userinfo
  Authorization: Bearer ya29.XXXXX
  
  Response: { "email": "alice@gmail.com", "name": "Alice" }

STEP 8: CLIENT LOGS USER IN
  Creates local session for alice@gmail.com
  User is authenticated!
```

---

## Why Auth Code Flow Is Secure

```
KEY SECURITY PROPERTY:
  Client Secret NEVER leaves the server!
  
  Browser sees:
  1. The redirect to auth server (step 2) → client_id visible, OK
  2. The callback with code (step 4) → short-lived code, OK
  
  Browser NEVER sees:
  - client_secret (used in step 5 server-side)
  - access_token (returned to server in step 6)
  - refresh_token (returned to server in step 6)
  
  Attacker who intercepts the auth code (from URL, logs, etc.):
  → Cannot exchange it without client_secret!
  → Code is useless without the server's secret
  (Unless: see 19.09 Authorization Code Interception)
```

---

## What to Check in Burp

```
BURP INTERCEPTION POINTS:
  
  1. STEP 2 REDIRECT (Browser → Auth Server):
     Note: client_id, redirect_uri, scope, state
     Check: Is state present? Is it random?
     
  2. STEP 4 CALLBACK (Auth Server → App):
     Note: code, state
     Check: Is state validated?
     Try: Remove state parameter → does it work? (state not validated!)
     Try: Change state → does it work? (state value not checked!)
     
  3. STEP 5 TOKEN EXCHANGE (App Server → Auth Server):
     Usually not visible in browser (server-side)
     But: check if any token exchange happens client-side (Implicit flow?)
     
  4. STEP 7 USER INFO (App Server → Resource Server):
     Usually server-side, but check CORS headers on /userinfo

THINGS TO TEST:
  - redirect_uri manipulation (see 19.07)
  - state parameter (see 19.06)
  - scope escalation (see 19.13)
  - Token in response URL (should NOT be there in code flow!)
```

---

## Related Notes
- [[01 - OAuth 2.0 Overview and Flow Types]] — all flow types
- [[03 - Implicit Flow Vulnerabilities]] — what NOT to do
- [[06 - OAuth State Parameter CSRF in OAuth]] — state parameter security
- [[07 - Redirect URI Manipulation]] — manipulating redirect_uri
