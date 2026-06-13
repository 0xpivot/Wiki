---
tags: [vapt, access-control, api, idor, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.09 BOLA — Broken Object Level Authorization (OWASP API #1)"
---

# 21.09 — BOLA: Broken Object Level Authorization (OWASP API #1)

## BOLA = IDOR for APIs

```
BOLA = Broken Object Level Authorization
OWASP API Security Top 10: API1:2023

SAME ROOT CAUSE AS IDOR:
  API endpoints manipulate objects using IDs from client
  Server doesn't verify caller is authorized to access that ID
  
  WHY SEPARATE CATEGORY:
  APIs have specific patterns that differ from web apps:
  - REST APIs return JSON objects with explicit IDs
  - CRUD operations on resources (GET, POST, PUT, DELETE)
  - Object references are everywhere in API responses
  - APIs often return more data than web UIs (full object vs. display fields)
  
  API1 = #1 OWASP API risk because it's EXTREMELY COMMON in APIs!
```

---

## REST API BOLA Patterns

```
RESOURCE-BASED URLS (classic REST):
  GET    /api/v1/users/{user_id}           ← read user
  PUT    /api/v1/users/{user_id}           ← update user
  DELETE /api/v1/users/{user_id}           ← delete user
  
  GET    /api/v1/users/{user_id}/orders    ← user's orders
  GET    /api/v1/orders/{order_id}         ← specific order
  PUT    /api/v1/orders/{order_id}/items   ← order items
  
  BOLA TEST: change {user_id} or {order_id} to other values!
  
NESTED RESOURCE BOLA:
  GET /api/v1/companies/42/employees/100
  → Change 42 to another company_id:
  GET /api/v1/companies/43/employees/100
  → Access employee 100 from company 43 (if you're in company 42)!
  
  OR: Employee 100 is in company 42, but what if:
  GET /api/v1/companies/42/employees/200  ← employee in another company!
  → Does server validate that employee 200 belongs to company 42?
```

---

## Finding BOLA in APIs

```bash
# STEP 1: ENUMERATE API ENDPOINTS
# From documentation:
curl https://api.target.com/swagger.json  # Swagger/OpenAPI spec
curl https://api.target.com/api-docs
curl https://api.target.com/.well-known/openapi.json

# From JS source:
grep -r "api\|endpoint\|/v1\|/v2" app.js

# Brute force:
feroxbuster -u https://api.target.com -w api-endpoints-wordlist.txt

# STEP 2: COLLECT ALL OBJECT IDs FROM RESPONSES
# Log in as attacker → make API calls → note all IDs in responses:
# user_id, order_id, account_id, document_id, etc.

# STEP 3: CREATE VICTIM ACCOUNT → note IDs
# victim user_id: 43
# victim order_id: 10042
# victim document_id: DOC-7801

# STEP 4: FROM ATTACKER ACCOUNT — ACCESS VICTIM's OBJECTS:
# Using your session (attacker):
curl -H "Authorization: Bearer ATTACKER_TOKEN" \
  https://api.target.com/api/v1/orders/10042  # VICTIM's order
# → Got victim's order details? → BOLA!

# STEP 5: TEST ALL METHODS:
for METHOD in GET PUT DELETE PATCH; do
  curl -s -o /dev/null -w "$METHOD: %{http_code}\n" \
    -X $METHOD \
    -H "Authorization: Bearer ATTACKER_TOKEN" \
    https://api.target.com/api/v1/users/VICTIM_ID
done

# STEP 6: USE BURP AUTORIZE (see note 03):
# Automated BOLA detection across all endpoints
```

---

## BOLA in API Responses (Data Leakage)

```
APIs OFTEN RETURN MORE DATA THAN NEEDED:
  GET /api/v1/users/42
  Expected: {name: "John", email: "john@example.com"}
  
  Actual response:
  {
    "id": 42,
    "name": "John",
    "email": "john@example.com",
    "password_hash": "$2b$12$...",    ← NEVER should be here!
    "api_key": "sk_live_...",          ← CRITICAL!
    "internal_notes": "VIP customer",  ← private data
    "credit_card_last4": "4242",        ← financial data
    "is_admin": false,                  ← tells attacker their role
    "reset_token": "abc123..."          ← allows account takeover!
  }
  
  → Even if attacker is authorized to read some fields,
    API returns ALL fields → data exposure!
  
TESTING:
  Examine API responses carefully → look for unexpected fields
  Check if ALL fields are appropriate for the caller's role
  Low-privilege user accessing their own record → sensitive fields exposed?
```

---

## BOLA via Object References in Responses

```
CHAINED BOLA:
  Response from one endpoint contains IDs → use in another endpoint
  
  EXAMPLE:
  GET /api/v1/orders/10042 →
  {
    "id": 10042,
    "user_id": 43,            ← victim's user ID!
    "payment_method_id": 5001 ← victim's payment method!
  }
  
  Now use discovered IDs:
  GET /api/v1/payment_methods/5001 → victim's credit card details!
  GET /api/v1/users/43 → victim's full profile!
  
  Even if 10042 is "your" order → the embedded IDs expose victim's data!
  
ALWAYS TEST:
  Any ID embedded in a response → try it against all relevant endpoints!
```

---

## Fix

```
CORRECT BOLA PREVENTION:

1. ALWAYS VERIFY OWNERSHIP IN QUERIES:
   # BAD:
   SELECT * FROM orders WHERE id = :order_id
   
   # GOOD:
   SELECT * FROM orders WHERE id = :order_id AND user_id = :authenticated_user_id

2. AUTHORIZATION MIDDLEWARE ON EVERY ENDPOINT:
   # Node.js Express middleware:
   async function authorizeOrderAccess(req, res, next) {
     const orderId = parseInt(req.params.order_id);
     const userId = req.user.id;  // from authenticated session
     
     const order = await db.query(
       'SELECT user_id FROM orders WHERE id = $1',
       [orderId]
     );
     
     if (!order || order.user_id !== userId) {
       return res.status(403).json({error: 'Access denied'});
     }
     
     req.order = order;  // attach for use in handler
     next();
   }
   
   router.get('/orders/:order_id', authenticate, authorizeOrderAccess, getOrder);

3. FIELD-LEVEL DATA MINIMIZATION:
   Return ONLY what the caller needs:
   # Don't serialize entire DB model
   # Use separate response schemas for different roles
   UserPublicSchema = {name, bio, avatar}      # public
   UserOwnSchema = {name, bio, email, settings} # owner of account  
   UserAdminSchema = {everything}               # admin only

4. USE UUIDS FOR OBJECT IDs:
   → Harder to enumerate than sequential integers
   → Still need ownership checks, but reduces automated enumeration risk
```

---

## Related Notes
- [[03 - IDOR — Insecure Direct Object Reference]] — web IDOR (same concept)
- [[04 - IDOR in URL Parameters]] — URL patterns
- [[10 - BFLA — Broken Function Level Authorization (OWASP API #5)]] — function-level API auth
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
