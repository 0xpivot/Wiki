---
tags: [vapt, http, api, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.23 REST API Architecture"
---

# 02.23 — REST API Architecture

## What is it?

**REST (Representational State Transfer)** is an architectural style for building APIs. RESTful APIs use HTTP methods and URLs to expose resources. Most modern web apps and mobile apps use REST APIs as their backend. Understanding REST is essential because APIs are a major attack surface.

---

## REST Principles

```
1. RESOURCES: Everything is a resource, identified by URL
   /users          = collection of users
   /users/123      = specific user (ID 123)
   /users/123/posts = posts belonging to user 123

2. HTTP METHODS map to CRUD operations:
   GET    /users        → Read all users (list)
   GET    /users/123    → Read one user
   POST   /users        → Create a new user
   PUT    /users/123    → Replace user 123 entirely
   PATCH  /users/123    → Update user 123 partially
   DELETE /users/123    → Delete user 123

3. STATELESS: Each request must contain all information needed
   Server doesn't store session — client sends token with every request

4. REPRESENTATIONS: Resources can be represented as JSON, XML, etc.
   Accept: application/json → client wants JSON
   Content-Type: application/json → sending JSON

5. UNIFORM INTERFACE: Consistent resource naming, HTTP methods
```

---

## REST API Request Examples

```
LIST USERS:
GET /api/v1/users HTTP/1.1
Host: target.com
Authorization: Bearer eyJhb...
Accept: application/json

Response:
[
  {"id": 1, "username": "alice", "email": "alice@test.com"},
  {"id": 2, "username": "bob", "email": "bob@test.com"}
]

GET ONE USER:
GET /api/v1/users/1 HTTP/1.1
Host: target.com
Authorization: Bearer eyJhb...

Response:
{"id": 1, "username": "alice", "email": "alice@test.com", "role": "user"}

CREATE USER:
POST /api/v1/users HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJhb...

{"username": "charlie", "email": "charlie@test.com", "password": "secret"}

UPDATE USER:
PATCH /api/v1/users/1 HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJhb...

{"email": "newemail@test.com"}

DELETE USER:
DELETE /api/v1/users/1 HTTP/1.1
Authorization: Bearer eyJhb...
```

---

## API Versioning

```
COMMON PATTERNS:
  URL version:    /api/v1/users, /api/v2/users
  Header version: Accept: application/vnd.api.v2+json
  Query param:    /api/users?version=2

VAPT SIGNIFICANCE:
  Old versions (v1) may be unpatched or have different security
  Try: /api/v1/admin when /api/v2/admin is protected
  Try: removing /v2/ → might default to v1
  
  Version disclosure in headers/errors → reveals API version
```

---

## Security Context — REST APIs in VAPT

### 1. IDOR — The Most Common API Vulnerability

```
IDOR = Insecure Direct Object Reference
API returns/modifies resources based on ID in URL.
If no authorization check → access other users' data.

EXAMPLE:
  You are User 123.
  GET /api/users/123/profile → returns YOUR profile (correct)
  GET /api/users/124/profile → returns OTHER user's profile (IDOR!)
  
  ATTACK:
  Burp Intruder → fuzz the user ID
  Numbers: 1, 2, 3, 4, ... 1000
  GUIDs: try to predict or enumerate (harder)
  
HORIZONTAL IDOR: Access other users' same-level resources
  /api/users/124/profile (you're user 123)

VERTICAL IDOR: Access higher-privileged resources
  /api/admin/users (you're a regular user)
```

### 2. Mass Assignment via REST API

```
ATTACK:
  API accepts JSON body and passes all fields to ORM/model.
  Extra fields (isAdmin, role, verified) get set!
  
  Normal registration:
  POST /api/users {"username":"alice","password":"test"}
  
  Attack:
  POST /api/users {"username":"alice","password":"test","isAdmin":true,"verified":true}
  
  If API passes all JSON keys to database → you're admin!

FIND MASS ASSIGNMENT:
1. Get an object (GET /api/users/me) → see all fields
2. Try setting any extra field in POST/PUT/PATCH
3. Verify change was applied (GET again)
```

### 3. API Endpoint Discovery

```bash
# Common API paths to check
paths=(
  "/api/" "/api/v1/" "/api/v2/" "/api/v3/"
  "/api/admin" "/api/internal"
  "/api/debug" "/api/health" "/api/status"
  "/api/users" "/api/user"
  "/v1/" "/v2/"
  "/.well-known/" "/openapi.json" "/swagger.json"
  "/swagger-ui.html" "/api-docs" "/docs"
  "/graphql" "/graphiql"
)

for path in "${paths[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
  echo "$path: $code"
done

# Scan for API endpoints
gobuster dir -u https://target.com/api/v1/ \
  -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt

# Find API spec (exposes ALL endpoints!):
curl https://target.com/swagger.json 2>/dev/null | python3 -m json.tool
curl https://target.com/openapi.json 2>/dev/null | python3 -m json.tool
```

### 4. HTTP Method Testing for Each Endpoint

```bash
# Test all methods on each endpoint
for path in /api/users /api/products /api/admin; do
  for method in GET POST PUT DELETE PATCH OPTIONS; do
    code=$(curl -s -o /dev/null -w "%{http_code}" \
      -X $method "https://target.com$path" \
      -H "Authorization: Bearer USER_TOKEN")
    echo "$method $path: $code"
  done
done

# 405 Method Not Allowed → endpoint exists but method blocked
# 403 Forbidden → endpoint exists, auth issue
# 200 OK on DELETE → UNAUTHORIZED DELETION!
```

### 5. API Response Data Leakage

```
APIs often return MORE data than needed.

ATTACK:
GET /api/users/me
Response:
{
  "id": 123,
  "username": "alice",
  "email": "alice@test.com",
  "password_hash": "$2b$10$...",     ← leaking password hash!
  "reset_token": "abc123",           ← leaking reset token!
  "isAdmin": false,                  ← revealing field (useful for mass assignment!)
  "balance": 1000.00,                ← financial data
  "internal_notes": "..."            ← internal data
}

Fix: Filter response fields (projection), don't return entire model objects.
```

---

## Hands-On: REST API Testing

```bash
# Full CRUD test sequence:
BASE="https://target.com/api/v1"
TOKEN="Bearer abc123"

# List resources
curl -H "Authorization: $TOKEN" "$BASE/users"

# Get specific resource
curl -H "Authorization: $TOKEN" "$BASE/users/1"

# Create resource
curl -X POST "$BASE/users" \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com"}'

# Try to access another user's resource (IDOR test)
curl -H "Authorization: $TOKEN" "$BASE/users/2"  # you're user 123!

# Try admin endpoint
curl -H "Authorization: $TOKEN" "$BASE/admin/users"

# Mass assignment test
curl -X PATCH "$BASE/users/me" \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"new@test.com","isAdmin":true,"role":"admin"}'

# Check if change applied
curl -H "Authorization: $TOKEN" "$BASE/users/me" | python3 -m json.tool
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| IDOR | Check ownership on every resource access |
| Mass assignment | Explicit allowlist of accepted fields (not all JSON keys) |
| Method not restricted | Return 405 for disallowed methods, enforce auth on all |
| Over-exposure of data | Filter response fields, use serializer allowlists |
| No rate limiting | Implement rate limiting per user/IP |
| API spec publicly exposed | Protect swagger/openapi behind authentication |

---

## Related Notes
- [[24 - GraphQL How It Differs from REST]] — alternative API style
- [[Module 07 - API Security]] — all OWASP API Top 10
- [[Module 03 - Access Control]] — IDOR and access control
- [[Module 06 - Mass Assignment]] — mass assignment attacks
