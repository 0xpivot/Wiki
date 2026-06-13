---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.13 Scope Escalation"
---

# 19.13 — Scope Escalation

## What Are OAuth Scopes?

```
OAUTH SCOPES = PERMISSIONS:
  When requesting OAuth authorization, you specify scopes:
  "I need read access to email"
  "I need read/write access to files"
  
  User consent screen shows the requested scopes:
  "This app wants to: Read your email, Access your contacts"
  
  Auth server issues token with ONLY those scopes:
  { "scope": "email contacts" }
  
  Resource server validates scope before returning data:
  GET /api/v1/emails → checks token has "email" scope
  GET /api/v1/delete-account → requires "admin" scope → rejected!
  
PURPOSE:
  Least-privilege principle for tokens
  Users can see/approve exactly what access is granted
```

---

## Attack 1: Requesting Extra Scope

```
SIMPLE ESCALATION:
  Normal request: scope=email profile
  Modified request: scope=email profile admin delete contacts
  
  → Does auth server grant the extra scopes?
  
  WHAT COULD GO WRONG:
  - Auth server trusts client to specify any scope
  - No per-client scope restriction configured
  - "Admin" scope not properly protected
  
TESTING:
  1. Intercept authorization request in Burp
  2. Modify scope parameter to include extra scopes:
     scope=email+profile+admin
     scope=openid+email+admin+write+delete
  3. Complete auth flow → check access token's scopes
  
  # Check token scopes (JWT):
  echo "ACCESS_TOKEN" | cut -d'.' -f2 | base64 -d 2>/dev/null | python3 -m json.tool
  # Or: check "scope" field in /oauth/token response
  # Or: call /oauth/introspect or userinfo to see granted scopes
```

---

## Attack 2: Scope Upgrade Without Re-Authorization

```
SOME APPS ALLOW:
  Using existing refresh token to obtain upgraded scopes
  Without re-prompting the user for consent!
  
  POST /oauth/token
  grant_type=refresh_token&
  refresh_token=REFRESH_TOKEN&
  scope=email admin  ← added admin!
  
  → If server grants admin without new consent → escalation!
  
WHAT SHOULD HAPPEN:
  Token refresh should only grant scopes originally authorized
  If more scopes requested → should require new authorization + consent
  
TESTING:
  1. Complete OAuth with limited scope (email only)
  2. Get refresh token
  3. Try refreshing with broader scope:
     scope=email admin write
  4. Check if access token comes back with admin scope
```

---

## Attack 3: Scope Mismatch (Token vs Resource Server)

```
THE VALIDATION PROBLEM:
  Token has scope: "email"
  
  Resource server endpoints:
  GET /api/users → requires "users.read" scope? But token has "email"?
  
  IF resource server doesn't validate scope strictly:
  → Token with "email" scope can access /api/users → privilege escalation!
  
  COMMON SCENARIO:
  - Microservices architecture
  - Resource servers added later without strict scope enforcement
  - "scope" field exists but is never checked
  
TESTING:
  1. Get access token with limited scope (e.g., "read")
  2. Try accessing endpoints that should require higher scope:
     - Admin API endpoints
     - DELETE operations
     - User management
  3. If access granted → scope not validated by resource server
```

---

## Attack 4: Scope Confusion in Multi-Tenant Apps

```
MULTI-TENANT SCOPE ISSUE:
  Tenant A's client registers scopes: files.read files.write
  Tenant B's client registers scopes: admin.read admin.write
  
  If scope enforcement is per-client-id but not per-tenant:
  → Use Tenant A's client to request admin.write scope
  → Auth server checks: is "admin.write" a valid scope? Yes (globally)
  → Grants it!
  
REAL-WORLD:
  Custom OAuth server implementations often miss this
  Standard providers (Google, Okta) handle this correctly
  Roll-your-own auth servers frequently get it wrong
```

---

## Attack 5: Insufficient Scope for Sensitive APIs

```
IMPLICIT ESCALATION: SCOPE TOO BROAD
  Common pattern in APIs:
  Scope: "api.access" → grants access to ALL API endpoints
  
  This isn't a bypass — the scope is intentionally broad
  BUT: overly broad scopes mean any token can access everything
  
  TESTING:
  1. Get token with most basic scope
  2. Try ALL API endpoints, not just expected ones
  3. If "api.access" token can reach admin endpoints → scope design flaw
  
  REPORT AS:
  "Insufficient scope granularity — all API access via single scope"
  Recommendation: separate scopes for sensitive operations
```

---

## Testing Scope Escalation Systematically

```bash
# STEP 1: DISCOVER AVAILABLE SCOPES:
# Check API docs, OAuth registration pages
# Check /oauth/authorize response for accepted scope values
# Try common scope names:
COMMON_SCOPES="read write admin delete user profile email openid offline_access api"

# STEP 2: INTERCEPT AUTHORIZATION REQUEST:
# Modify scope parameter: scope=email+admin+write+delete
# Check what scopes are granted in the response token

# STEP 3: DECODE ACCESS TOKEN:
# If JWT:
python3 -c "
import base64, json, sys
token = 'YOUR_ACCESS_TOKEN'
payload = token.split('.')[1]
padding = '=' * (4 - len(payload) % 4)
data = base64.b64decode(payload + padding)
print(json.dumps(json.loads(data), indent=2))
"
# Look for 'scope' or 'scp' field

# STEP 4: TEST REFRESH WITH ESCALATED SCOPE:
curl -X POST https://auth.target.com/oauth/token \
  -d "grant_type=refresh_token&refresh_token=REFRESH_TOKEN&scope=email+admin"

# STEP 5: TEST ENDPOINT ACCESS WITH SCOPED TOKEN:
# Use limited-scope token on high-privilege endpoints:
curl -H "Authorization: Bearer LIMITED_SCOPE_TOKEN" \
  https://api.target.com/admin/users
```

---

## Fix

```
PREVENTING SCOPE ESCALATION:

1. PER-CLIENT SCOPE REGISTRATION:
   # Auth server: each client explicitly allowed scopes
   client_id: my-mobile-app
   allowed_scopes: [email, profile, photos.read]
   
   # Request for admin scope → rejected at auth server level

2. VALIDATE SCOPES AT AUTH SERVER:
   # Never grant scopes not in client's allowed list:
   requested_scopes = set(request.scope.split())
   allowed_scopes = set(client.allowed_scopes)
   granted_scopes = requested_scopes & allowed_scopes  # intersection!

3. RESOURCE SERVER VALIDATES SCOPE:
   # Every endpoint must check the token's scope:
   # Python:
   def require_scope(scope):
       def decorator(f):
           def wrapper(*args, **kwargs):
               token_scopes = get_token_scopes(request)
               if scope not in token_scopes:
                   return error(403, f"Missing scope: {scope}")
               return f(*args, **kwargs)
           return wrapper
       return decorator
   
   @require_scope('admin.write')
   def delete_user(user_id):
       ...

4. SCOPE BINDING ON REFRESH:
   # Refresh token cannot grant more than originally authorized:
   new_scope = min_scope(refresh_token.original_scope, requested_scope)

5. PRINCIPLE OF LEAST PRIVILEGE IN SCOPE DESIGN:
   Don't use single "api.access" for everything
   Use fine-grained scopes: "users.read", "users.write", "admin.users.delete"
```

---

## Related Notes
- [[04 - Client Credentials Flow]] — scope in machine-to-machine
- [[19 - OpenID Connect OIDC Attack Surface]] — OIDC scope issues
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
