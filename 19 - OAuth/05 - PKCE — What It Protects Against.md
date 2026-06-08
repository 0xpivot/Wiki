---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.05 PKCE — What It Protects Against"
---

# 19.05 — PKCE: What It Protects Against

## What Is PKCE?

```
PKCE = Proof Key for Code Exchange
Pronounced: "Pixie"

PURPOSE:
  Protect Auth Code flow for PUBLIC CLIENTS (mobile apps, SPAs)
  that cannot safely store a client_secret
  
WHY NEEDED:
  Public clients = apps where code is visible to users
  Mobile app: code can be decompiled → client_secret stolen!
  SPA: JavaScript visible in browser → client_secret stolen!
  
  Without PKCE: Attacker who intercepts authorization code
  → Can exchange it for tokens (no secret required)
  
  With PKCE: Code is useless without the code_verifier
  → Even if attacker intercepts code → can't exchange it!
```

---

## How PKCE Works

```
STEP 1: CLIENT GENERATES CODE VERIFIER
  code_verifier = random string (43-128 chars, URL-safe)
  Example: "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
  
STEP 2: CLIENT COMPUTES CODE CHALLENGE
  code_challenge = BASE64URL(SHA256(code_verifier))
  Example: "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
  
STEP 3: CLIENT SENDS CODE CHALLENGE IN AUTHORIZATION REQUEST
  https://auth.example.com/oauth/authorize?
    client_id=CLIENT_ID&
    redirect_uri=https://app.example.com/callback&
    response_type=code&
    scope=email&
    state=STATE&
    code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
    code_challenge_method=S256
    
STEP 4: AUTH SERVER STORES code_challenge, RETURNS code

STEP 5: CLIENT SENDS code_verifier WHEN EXCHANGING CODE
  POST /oauth/token
  code=AUTH_CODE&
  client_id=CLIENT_ID&
  redirect_uri=...&
  grant_type=authorization_code&
  code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk  ← SECRET!
  
STEP 6: AUTH SERVER VERIFIES
  SHA256(code_verifier) == stored code_challenge?
  → If match → exchange code for tokens!
  → If mismatch → REJECT!

WHY SECURE:
  code_verifier never left the client
  Auth code alone is useless without code_verifier
  Even if someone intercepts the authorization code → can't exchange it!
```

---

## PKCE Attack Surface

### Plain PKCE (Downgrade Attack)

```
code_challenge_method can be:
  S256 = BASE64URL(SHA256(verifier))  ← SECURE!
  plain = code_verifier == code_challenge  ← INSECURE!
  
  With "plain": challenge == verifier
  Anyone who sees the code_challenge → knows the code_verifier!
  code_challenge is in the redirect URL → visible!
  
ATTACK:
  Intercept the authorization URL → note code_challenge
  When victim gets auth code → use code_challenge as code_verifier!
  POST /token { code=X, code_verifier=SAME_AS_CODE_CHALLENGE }
  
  → Exchanges the code without knowing the real verifier!
  → Only works if plain method is supported!
  
TEST:
  In Burp, find the authorization request
  Change: code_challenge_method=S256 → code_challenge_method=plain
  And: code_challenge=SAME_AS_VERIFIER
  → Does auth server accept plain? → vulnerability!
  
FIX: Require S256 method, reject plain
```

### Weak Code Verifier

```
IF code_verifier IS PREDICTABLE:
  Some implementations use weak random: rand() based
  → Attacker who observed auth session can try to predict code_verifier
  
FIX:
  Use cryptographically secure random:
  Python: secrets.token_urlsafe(32) → 43+ chars of strong random
  
  REQUIREMENTS (RFC 7636):
  - 43-128 characters
  - Characters: A-Z, a-z, 0-9, -, ., _, ~
  - Cryptographically random
```

### PKCE Not Enforced for Confidential Clients

```
SOME AUTH SERVERS:
  Enforce PKCE for public clients (mobile/SPA)
  But NOT for confidential clients (server-side apps)
  
  → Code interception against confidential client → PKCE doesn't protect!
  But: client_secret does (see authorization code flow security)
  
BEST PRACTICE:
  Enforce PKCE for ALL clients (confidential and public alike)
  Defense in depth!
```

---

## Testing PKCE Implementation

```bash
# TEST IF PKCE IS REQUIRED:
# Remove PKCE params from authorization request:
https://auth.example.com/oauth/authorize?
  client_id=CLIENT_ID&
  redirect_uri=REDIRECT&
  response_type=code&
  scope=email&
  state=STATE
  (NO code_challenge or code_challenge_method!)

# If auth server accepts this → PKCE not required for public clients!

# TEST IF PLAIN IS ACCEPTED:
# Change code_challenge_method to plain:
# And set code_challenge = same as code_verifier

# TEST CODE INTERCEPTION WITHOUT VERIFIER:
# 1. Get authorization code (from callback URL)
# 2. Try to exchange it WITHOUT code_verifier:
curl -X POST https://auth.example.com/oauth/token \
  -d "code=AUTH_CODE&client_id=CLIENT_ID&grant_type=authorization_code&redirect_uri=REDIRECT"
# No code_verifier → should fail if PKCE enforced
```

---

## Fix

```
PKCE IMPLEMENTATION:

Client side (JavaScript):
  function generateCodeVerifier() {
      const array = new Uint8Array(32);
      window.crypto.getRandomValues(array);
      return btoa(String.fromCharCode.apply(null, array))
          .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  }
  
  async function generateCodeChallenge(verifier) {
      const digest = await crypto.subtle.digest('SHA-256',
          new TextEncoder().encode(verifier));
      return btoa(String.fromCharCode(...new Uint8Array(digest)))
          .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  }

Auth Server requirements:
  ✓ Require PKCE for all public clients (SPAs, mobile apps)
  ✓ Support S256 method only (reject "plain")
  ✓ Bind code to code_challenge at issuance
  ✓ Verify SHA256(code_verifier) == stored code_challenge at exchange
  ✓ Consider requiring PKCE for confidential clients too (defense in depth)
```

---

## Related Notes
- [[09 - Authorization Code Interception]] — what PKCE protects against
- [[02 - Authorization Code Flow Step by Step]] — code flow context
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full defense
