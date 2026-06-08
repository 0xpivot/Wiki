---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.17 JWT Confusion in Multi-Tenant Apps"
---

# 18.17 — JWT Confusion in Multi-Tenant Apps

## Multi-Tenant Architecture

```
MULTI-TENANT:
  One application, multiple customers (tenants)
  Each tenant has isolated data and users
  
  Examples:
  - Salesforce: each company = one tenant
  - Slack: each workspace = one tenant
  - SaaS CRM: each organization = one tenant
  
JWT IN MULTI-TENANT:
  JWT payload often includes tenant identifier:
  {
    "sub": "user_42",
    "tenant": "company-a",
    "role": "admin",
    "exp": ...
  }
  
VULNERABILITY:
  If server doesn't validate that token's tenant matches the accessed resource's tenant
  → Cross-tenant data access!
```

---

## Cross-Tenant Data Access

```
ATTACK SCENARIO:

  Tenant A has admin user Alice:
  JWT: {"sub": "alice", "tenant": "company-a", "role": "admin"}
  
  Tenant B has regular user Bob:
  JWT: {"sub": "bob", "tenant": "company-b", "role": "user"}
  
  Alice tries to access Tenant B's customer data:
  GET /api/customers?tenant=company-b
  Authorization: Bearer ALICE_JWT
  
  VULNERABLE BACKEND:
  // Just checks if user is authenticated, not which tenant!
  if (jwt.verify(token, secret)) {
      const customers = db.query('SELECT * FROM customers WHERE tenant = ?', [req.query.tenant]);
      // ↑ Takes tenant from URL parameter, not from JWT!
      // Alice can set ?tenant=company-b → gets company-b's customers!
  }
  
  SECURE BACKEND:
  if (jwt.verify(token, secret)) {
      const jwt_tenant = jwt.decode(token).tenant;
      // ↑ Takes tenant ONLY from JWT, never from request parameters!
      const customers = db.query('SELECT * FROM customers WHERE tenant = ?', [jwt_tenant]);
  }
```

---

## IDOR via Tenant + Resource ID

```
SCENARIO:
  Tenant A: /api/files/1001 (File 1001 belongs to Tenant A)
  Tenant B: /api/files/2001 (File 2001 belongs to Tenant B)
  
  Alice (Tenant A) accesses her own files:
  GET /api/files/1001  → with Alice's JWT → works!
  
  Alice accesses Tenant B's file:
  GET /api/files/2001  → with Alice's JWT → should fail!
  
  VULNERABLE QUERY:
  SELECT * FROM files WHERE id = ?  # No tenant check!
  → Returns file 2001 regardless of JWT's tenant!
  
  SECURE QUERY:
  SELECT * FROM files WHERE id = ? AND tenant = jwt.tenant
  → File 2001 belongs to Tenant B → Alice's tenant is A → empty result!
```

---

## Shared JWT Secret Across Tenants

```
SOME PLATFORMS:
  Each tenant has their own JWT secret
  → Token from Tenant A can't be used at Tenant B (different secret!)
  
  OR: All tenants share ONE secret
  → More convenient but dangerous!
  
ATTACK WITH SHARED SECRET:
  1. Crack or know the shared JWT secret
  2. Forge a token for ANY tenant:
     {"sub": "admin_user", "tenant": "victim-company", "role": "admin"}
  3. → Access victim company's data!
  
TEST:
  If you have multiple tenant accounts (or two trial accounts):
  1. Get JWT from Tenant A → decode → note structure
  2. If you can crack/forge the JWT → change tenant to Tenant B
  3. See if you access Tenant B's data
```

---

## Testing Multi-Tenant JWT Issues

```
METHODOLOGY:
  
  STEP 1: Get accounts in two different tenants:
  Register two accounts (if self-service registration)
  OR: Use "free trial" twice with different org names
  
  STEP 2: Decode both JWTs → find tenant identifier field:
  Account A: {"tenant": "acme-corp", "sub": "alice", ...}
  Account B: {"tenant": "evil-corp", "sub": "attacker", ...}
  
  STEP 3: Check for tenant IDOR:
  Using Account A's JWT:
  GET /api/data?org=evil-corp          → tenant from URL param?
  GET /api/tenants/evil-corp/users     → tenant in URL path?
  GET /api/users?tenant=evil-corp      → different tenant in query?
  
  → Does server validate JWT.tenant matches URL tenant?
  
  STEP 4: Try forging tenant (if JWT has weakness):
  - alg=none → change tenant claim
  - Known secret → sign modified JWT with different tenant
  
  STEP 5: Resource enumeration across tenants:
  List Tenant A resources (get IDs)
  Try accessing same IDs without tenant filter
  → Tenant B data accessible?
```

---

## Fix

```
MULTI-TENANT SECURITY REQUIREMENTS:

  ✓ ALL resources have tenant filter in DB queries:
    # WRONG:
    SELECT * FROM reports WHERE id = ?
    
    # RIGHT:
    SELECT * FROM reports WHERE id = ? AND tenant_id = jwt.tenant_id
    
  ✓ Tenant from JWT only — never from URL/body:
    # WRONG:
    tenant = request.args.get('tenant')  # user-controlled!
    
    # RIGHT:
    tenant = jwt_payload['tenant']  # from verified JWT!
    
  ✓ Separate JWT secrets per tenant (if feasible):
    Each tenant's users get tokens signed with that tenant's secret
    → Even forged JWT can't cross tenants without knowing the target's secret
    
  ✓ Logging: log cross-tenant access attempts as security events
  
  ✓ Automated testing: each CI/CD run tests that Tenant A can't access Tenant B
```

---

## Related Notes
- [[12 - JWT Substitution Attack]] — cross-user/service token swapping
- [[03 - JWT Claims Reference]] — aud claim for audience restriction
- [[Module: Access Control]] — IDOR and authorization patterns
