---
tags: [vapt, oauth, beginner]
difficulty: beginner
module: "19 - OAuth"
topic: "19.04 Client Credentials Flow"
---

# 19.04 — Client Credentials Flow

## What Is Client Credentials?

```
CLIENT CREDENTIALS FLOW:
  Machine-to-machine OAuth — no user involved!
  
  Use case:
  Backend service A → needs to call Backend service B's API
  No human user authenticates — the application itself authenticates
  
ACTORS:
  Client (Service A): requests access
  Authorization Server: validates client credentials, issues token
  Resource Server (Service B): serves the API
  
NO USER → NO USER CONSENT SCREEN → NO REDIRECT URIs
This is the simplest OAuth flow!
```

---

## How It Works

```
STEP 1: Client authenticates directly to auth server:
  POST /oauth/token
  Content-Type: application/x-www-form-urlencoded
  Authorization: Basic BASE64(client_id:client_secret)
  
  grant_type=client_credentials&
  scope=api.read api.write

STEP 2: Auth server returns access token:
  {
    "access_token": "ACCESS_TOKEN_HERE",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "api.read api.write"
  }
  
STEP 3: Client uses token:
  GET https://api.serviceB.com/data
  Authorization: Bearer ACCESS_TOKEN_HERE
```

---

## Attack Surface

### Client Secret Exposure

```
CLIENT SECRET = THE PASSWORD FOR THIS FLOW
  If exposed → attacker can impersonate the service!
  
WHERE SECRETS LEAK:
  - Frontend JavaScript code (mobile apps, SPAs)
  - GitHub repositories (accidentally committed)
  - Docker images (baked into image layers)
  - Environment files (.env committed to repo)
  - CI/CD logs (printed during build)
  - API documentation examples
  
IMPACT OF LEAKED SECRET:
  POST /oauth/token
  grant_type=client_credentials&
  client_id=LEAKED_ID&
  client_secret=LEAKED_SECRET&
  scope=api.read
  
  → Gets valid access token → impersonates the service!
  → May have elevated privileges (service accounts often have broad access)
```

### Testing Client Credentials

```bash
# CHECK IF CLIENT CREDENTIALS ENDPOINT IS ACCESSIBLE:
curl -X POST https://auth.target.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=test&client_secret=test&scope=read"

# LOOK FOR EXPOSED SECRETS IN:
# 1. JavaScript source (mobile apps, web apps)
grep -r "client_secret" /path/to/app/js/
grep -r "OAUTH_SECRET\|CLIENT_SECRET" .

# 2. GitHub Dorks:
# "client_secret" "target.com"
# "OAUTH" "SECRET" "target.com" filename:.env

# 3. Docker images:
docker history IMAGE_NAME  # shows layers, may reveal env vars in commands

# 4. Request headers:
# Watch for Basic auth in token requests → decode to get client_id:secret
echo "Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ=" | base64 -d
# → client_id:client_secret

# TEST WITH FOUND SECRETS:
curl -X POST https://auth.target.com/oauth/token \
  -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&scope=admin"
```

### Scope Escalation

```
CHECK WHAT SCOPES ARE AVAILABLE:
  The token request specifies scope
  What happens if you request more scope than you should have?
  
  POST /oauth/token
  grant_type=client_credentials&
  scope=api.read api.write api.admin  ← added admin scope!
  
  → Server should reject scopes not registered for this client
  → But if it grants them → unauthorized access!
  
TEST:
  Normal request: scope=api.read
  Modified request: scope=api.read api.admin
  → If admin scope granted → escalation!
```

---

## Fix

```
PROTECTING CLIENT CREDENTIALS:

  ✓ NEVER include client_secret in frontend code (JS, mobile apps)
  ✓ Store in secure secrets manager (AWS Secrets Manager, HashiCorp Vault)
  ✓ Use environment variables (never hardcode)
  ✓ Rotate secrets regularly
  ✓ Scope limitation: register minimum required scopes per client
  ✓ IP allowlist for machine-to-machine clients (if possible)
  ✓ Short-lived tokens with refresh (or just short-lived, regenerate as needed)
  ✓ Audit log all client credential token issuances
  
FOR MOBILE APPS (can't keep secrets):
  → Don't use client credentials flow at all!
  → Use Auth Code + PKCE for user-facing flows
  → Proxy requests through your backend (which holds the secret)
```

---

## Related Notes
- [[15 - Client Secret Exposure]] — detailed secret exposure scenarios
- [[13 - Scope Escalation]] — requesting unauthorized scopes
- [[01 - OAuth 2.0 Overview and Flow Types]] — all OAuth flow types
