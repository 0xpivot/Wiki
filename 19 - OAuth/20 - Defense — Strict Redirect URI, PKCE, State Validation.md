---
tags: [vapt, oauth, defense]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.20 Defense — Strict Redirect URI, PKCE, State Validation"
---

# 19.20 — Defense: Strict Redirect URI, PKCE, State Validation

## Complete OAuth Security Checklist

```
CATEGORY 1: REDIRECT URI
  □ Exact match validation (not prefix, not regex, not domain-only)
  □ No wildcards registered
  □ No open redirects on registered domains
  □ Normalize before comparison (URL decode, lowercase, resolve ../)
  □ Register separate URIs per environment (dev/staging/prod)
  □ Register HTTPS URIs only (not http://)
  □ Mobile: use App Links/Universal Links (not custom URI schemes)

CATEGORY 2: STATE PARAMETER
  □ Always generate state before authorization request
  □ Use cryptographically secure random (32+ bytes)
  □ Store in server-side session (not cookie, localStorage, or URL)
  □ Always validate: present + matches stored + timing
  □ Delete from session after validation (single-use)
  □ Use constant-time comparison

CATEGORY 3: PKCE
  □ Required for all public clients (SPA, mobile)
  □ Required for all confidential clients too (defense in depth)
  □ Only S256 accepted (reject plain or missing)
  □ code_verifier: 43-128 chars, cryptographically random
  □ Server validates SHA256(verifier) == stored challenge

CATEGORY 4: TOKENS
  □ Access tokens: max 60 minutes expiry
  □ Refresh tokens: single-use rotation
  □ Refresh tokens: invalidated on logout
  □ Refresh tokens: invalidated on password change
  □ JTI claim in all tokens (for revocation)
  □ Revocation on logout via JTI blocklist

CATEGORY 5: CLIENT CREDENTIALS
  □ client_secret stored in secrets manager, not code
  □ Public clients: no client_secret issued (use PKCE)
  □ Rotate secrets regularly
  □ Per-client scope registration (minimum required scopes)

CATEGORY 6: OIDC-SPECIFIC (if using OIDC)
  □ Validate ID token signature
  □ Validate iss (exact match to trusted issuer)
  □ Validate aud (must match your client_id)
  □ Validate exp (not expired)
  □ Validate nonce (prevents replay)
  □ Bind accounts by (iss + sub), not email
  □ Require email_verified=true before trusting email

CATEGORY 7: SCOPES
  □ Per-client allowed scope list enforced
  □ Resource server validates scope on every endpoint
  □ Refresh tokens cannot escalate scope

CATEGORY 8: ACCOUNT LINKING
  □ State validated on linking callback (same as login)
  □ Require authenticated session to initiate linking
  □ Confirm + re-auth for sensitive linking operations
  □ Email notifications on link/unlink events
  □ Link by provider sub, not email
```

---

## Complete Implementation Reference

### Correct Authorization Flow (Python/Flask)

```python
import secrets
import hashlib
import base64
import time
import requests
from flask import Flask, session, request, redirect, abort
from authlib.jose import jwt

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# OAuth Configuration (loaded from environment — never hardcode!)
import os
CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']
REDIRECT_URI = os.environ['OAUTH_REDIRECT_URI']
AUTH_ENDPOINT = "https://auth.example.com/oauth/authorize"
TOKEN_ENDPOINT = "https://auth.example.com/oauth/token"
JWKS_URI = "https://auth.example.com/.well-known/jwks.json"
TRUSTED_ISSUER = "https://auth.example.com"

def generate_pkce():
    """Generate PKCE code_verifier and code_challenge"""
    verifier = secrets.token_urlsafe(32)  # 43+ chars, cryptographically random
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return verifier, challenge

@app.route('/login')
def login():
    # Generate state (anti-CSRF)
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Generate PKCE
    code_verifier, code_challenge = generate_pkce()
    session['code_verifier'] = code_verifier
    
    # Generate nonce (for OIDC ID token replay prevention)
    nonce = secrets.token_urlsafe(16)
    session['oauth_nonce'] = nonce
    
    auth_url = (
        f"{AUTH_ENDPOINT}?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256&"
        f"nonce={nonce}"
    )
    return redirect(auth_url)

@app.route('/oauth/callback')
def callback():
    # --- STATE VALIDATION (anti-CSRF) ---
    received_state = request.args.get('state')
    stored_state = session.pop('oauth_state', None)
    
    if not stored_state or not received_state:
        abort(400, "Missing state parameter")
    if not secrets.compare_digest(received_state, stored_state):
        abort(400, "State mismatch — possible CSRF attack")
    
    # --- ERROR HANDLING ---
    error = request.args.get('error')
    if error:
        return f"OAuth error: {error}", 400
    
    code = request.args.get('code')
    if not code:
        abort(400, "Missing authorization code")
    
    # --- TOKEN EXCHANGE ---
    code_verifier = session.pop('code_verifier', None)
    if not code_verifier:
        abort(400, "Missing PKCE verifier")
    
    token_response = requests.post(TOKEN_ENDPOINT, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code_verifier': code_verifier,
    })
    
    if not token_response.ok:
        abort(400, "Token exchange failed")
    
    tokens = token_response.json()
    
    # --- ID TOKEN VALIDATION (OIDC) ---
    id_token = tokens.get('id_token')
    if id_token:
        validate_id_token(id_token)
    
    # Store session (NEVER store raw token in client-side storage!)
    session['user_id'] = get_user_from_token(tokens['access_token'])
    session['access_token'] = tokens['access_token']
    
    # Redirect to CLEAN URL (removes code from browser history/URL bar)
    return redirect('/dashboard')

def validate_id_token(id_token):
    """Validate OIDC ID token"""
    jwks = fetch_jwks()
    
    claims = jwt.decode(id_token, jwks)
    
    # Validate required claims
    if claims['iss'] != TRUSTED_ISSUER:
        abort(400, "Untrusted issuer")
    if claims['aud'] != CLIENT_ID:
        abort(400, "Token not for this client")
    if claims['exp'] < int(time.time()):
        abort(400, "Expired token")
    
    # Validate nonce
    stored_nonce = session.pop('oauth_nonce', None)
    if claims.get('nonce') != stored_nonce:
        abort(400, "Nonce mismatch")
    
    # Only trust verified emails
    if not claims.get('email_verified', False):
        abort(400, "Email not verified")
    
    return claims

def fetch_jwks():
    """Fetch JWKS (cache in production!)"""
    response = requests.get(JWKS_URI)
    return response.json()
```

---

### Redirect URI Validation (Auth Server Side)

```python
from urllib.parse import urlparse, urlunparse
import unicodedata

REGISTERED_REDIRECT_URIS = {
    "my-app-client-id": [
        "https://app.example.com/oauth/callback",
        "https://staging.example.com/oauth/callback",
    ]
}

def normalize_uri(uri):
    """Normalize URI for comparison"""
    parsed = urlparse(uri)
    # Lowercase scheme and host
    scheme = parsed.scheme.lower()
    host = parsed.netloc.lower()
    # Normalize path (resolve ..)
    path = posixpath.normpath(parsed.path) if parsed.path else '/'
    # Remove default ports
    if (scheme == 'https' and host.endswith(':443')):
        host = host[:-4]
    if (scheme == 'http' and host.endswith(':80')):
        host = host[:-3]
    # Reconstruct without query or fragment
    return urlunparse((scheme, host, path, '', '', ''))

def validate_redirect_uri(client_id, requested_uri):
    registered = REGISTERED_REDIRECT_URIS.get(client_id, [])
    normalized_requested = normalize_uri(requested_uri)
    normalized_registered = [normalize_uri(u) for u in registered]
    
    if normalized_requested not in normalized_registered:
        raise ValueError(f"Invalid redirect_uri: {requested_uri}")
    
    return requested_uri
```

---

### Token Storage Best Practices

```javascript
// IN THE BROWSER:
// ✗ NEVER: localStorage.setItem('access_token', token)
// ✗ NEVER: document.cookie = `token=${token}` (non-HttpOnly)
// ✓ OK:    Memory variable (lost on tab close)
// ✓ BEST:  HttpOnly Secure cookie (server sets it)

// SERVER SETS TOKEN AS HTTPONLY COOKIE:
// Python Flask:
response = make_response(redirect('/dashboard'))
response.set_cookie(
    'session_token',
    value=session_token,
    httponly=True,    # Can't be read by JavaScript
    secure=True,      # HTTPS only
    samesite='Lax',   # CSRF protection
    max_age=3600,     # 1 hour
    path='/',
)
return response

// SPA approach — access token in memory:
let accessToken = null;  // In-memory only, not persisted!

function setToken(token) {
    accessToken = token;  // Dies when page/tab closes
}

function getToken() {
    return accessToken;
}
// → XSS can't steal from localStorage because it's not there!
// → XSS CAN still use the token if it runs in same session... 
//   but at least it's not persistent
```

---

## Security Headers for OAuth Endpoints

```
# Nginx config for OAuth callback endpoint:
location /oauth/callback {
    proxy_pass http://backend;
    
    # Prevent token leakage via Referer:
    add_header Referrer-Policy "no-referrer" always;
    
    # Prevent caching of OAuth responses:
    add_header Cache-Control "no-store, no-cache, must-revalidate" always;
    add_header Pragma "no-cache" always;
    
    # Security headers:
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
}
```

---

## Related Notes
- [[06 - OAuth State Parameter — CSRF in OAuth]] — CSRF details
- [[05 - PKCE — What It Protects Against]] — PKCE details
- [[07 - Redirect URI Manipulation]] — redirect_uri attacks
- [[19 - OpenID Connect OIDC Attack Surface]] — OIDC specifics
- [[18 - OAuth to Account Takeover Chain]] — full attack chains
