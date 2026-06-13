---
tags: [vapt, oauth, beginner]
difficulty: beginner
module: "19 - OAuth"
topic: "19.01 OAuth 2.0 Overview and Flow Types"
portswigger_labs: ["Authentication bypass via OAuth implicit flow"]
---

# 19.01 — OAuth 2.0 Overview and Flow Types

## What Is OAuth 2.0?

```
OAUTH 2.0:
  Authorization framework — lets apps access resources on behalf of users
  WITHOUT users sharing their passwords with those apps
  
  "Login with Google" = OAuth in action!
  
ACTORS:
  Resource Owner:   The user (owns their data)
  Client:           The app wanting access (e.g., a third-party website)
  Authorization Server: Where user authenticates (Google, Facebook, Okta)
  Resource Server:  API serving the protected data (Gmail API, GitHub API)
  
ANALOGY:
  You want a hotel room key (access token)
  You show ID (authenticate) at front desk (auth server)
  Hotel gives you key (access token)
  Key lets you in your room (resource server) but not others!
  You never gave the front desk access to your house keys!
```

---

## OAuth Flow Types (Grant Types)

```
1. AUTHORIZATION CODE FLOW (most secure, use this!):
   For: Server-side apps that can keep secrets
   Flow: auth code → exchange for tokens (server-side exchange!)
   Security: Client secret never exposed to browser!
   
2. AUTHORIZATION CODE + PKCE (for public clients):
   For: SPAs, mobile apps (can't keep secrets!)
   Security: Code Verifier/Challenge replaces client secret
   Modern replacement for Implicit flow
   
3. IMPLICIT FLOW (deprecated, avoid!):
   For: Old SPAs (pre-PKCE era)
   Returns: Access token directly in URL fragment (#access_token=...)
   Problem: Token in URL = logs, history, Referer leakage
   Deprecated in OAuth 2.1
   
4. CLIENT CREDENTIALS FLOW:
   For: Machine-to-machine (no user involved)
   Flow: client_id + client_secret → access token directly
   Use: Backend services calling other backend services
   
5. DEVICE AUTHORIZATION FLOW:
   For: Devices without browsers (smart TV, CLI tools)
   User completes auth on separate device

WHAT TO TEST:
  Which flows are enabled?
  Is Implicit flow still active? (Should be disabled)
  Are PKCE requirements enforced for public clients?
```

---

## OAuth vs OpenID Connect (OIDC)

```
OAUTH 2.0:
  Purpose: Authorization (giving apps ACCESS to resources)
  Result:  Access token (opaque or JWT)
  Q: "Can this app access my Google Drive?"
  
OPENID CONNECT (OIDC):
  Purpose: Authentication (proving identity)
  Built ON TOP OF OAuth 2.0
  Result: ID token (JWT with identity claims)
  Q: "Who is this person? Are they really alice@gmail.com?"
  
  Additional endpoints:
  /userinfo → returns user profile when called with access token
  /.well-known/openid-configuration → discovery document
  
  Additional token:
  ID Token (JWT): {"iss": "google.com", "sub": "1234567890", "email": "alice@gmail.com"}
  
"LOGIN WITH GOOGLE" IS OIDC, NOT JUST OAUTH!
```

---

## Tokens in OAuth

```
ACCESS TOKEN:
  Short-lived credential to access resources
  Not for authentication!
  Passed to Resource Server (API)
  Format: opaque string or JWT
  Lifetime: 15 min to 1 hour typically
  
REFRESH TOKEN:
  Long-lived token to get new access tokens
  Only used with Authorization Server
  Should be stored very securely
  Lifetime: days to months
  
ID TOKEN (OIDC only):
  JWT containing user identity claims
  Used for authentication (who is this person?)
  NOT passed to Resource Server as auth
  Validate at Client side (check signature, iss, aud, exp)
  
AUTHORIZATION CODE:
  Temporary, single-use code
  Exchanged for tokens (access + refresh)
  Lifetime: 10-60 seconds!
  Very limited scope of use
```

---

## Finding OAuth in the Wild

```bash
# SIGNS OF OAUTH IN USE:
# 1. "Login with Google/Facebook/GitHub" buttons
# 2. Redirect URLs containing /oauth, /callback, /auth
# 3. URLs with: code=, state=, access_token=
# 4. Authorization headers with Bearer tokens
# 5. JWKS endpoints: /.well-known/jwks.json

# DISCOVER OAUTH ENDPOINTS:
curl https://target.com/.well-known/openid-configuration  # OIDC discovery
# Returns: authorization_endpoint, token_endpoint, userinfo_endpoint, jwks_uri

# CHECK WHAT GRANT TYPES ARE SUPPORTED:
# Look at authorization_endpoint response_type parameter
# response_type=code → authorization code
# response_type=token → implicit (bad!)
# response_type=code+id_token → hybrid (complex)

# IN BURP:
# Filter HTTP History for: /oauth/, /auth/, /authorize, callback?code=
```

---

## Related Notes
- [[02 - Authorization Code Flow Step by Step]] — detailed flow explanation
- [[03 - Implicit Flow Vulnerabilities]] — deprecated but still seen
- [[05 - PKCE What It Protects Against]] — modern public client security
- [[06 - OAuth State Parameter CSRF in OAuth]] — anti-CSRF in OAuth
