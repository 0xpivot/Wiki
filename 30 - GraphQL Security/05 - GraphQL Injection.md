---
tags: [vapt, graphql, injection, sqli, nosqli]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.05 GraphQL Injection"
---

# 30.05 — GraphQL Injection (SQLi, NoSQLi, Command Injection)

## What is it?
A common misconception among developers is that moving to GraphQL automatically protects an application from injection attacks like SQL Injection (SQLi) or NoSQL Injection. This is dangerously false. 

GraphQL provides strict *type checking* (e.g., ensuring a string is a string and an integer is an integer), but it does absolutely nothing to sanitize the *contents* of those inputs before passing them to the underlying database or operating system. If a GraphQL resolver takes a string argument and concatenates it directly into a raw SQL query or an `exec()` command, the application is vulnerable to injection.

Because GraphQL often aggregates data from multiple disparate backends (PostgreSQL, MongoDB, internal REST APIs, legacy SOAP services), a single GraphQL endpoint might be vulnerable to SQLi, NoSQLi, and OS Command Injection simultaneously, depending on which field and resolver you interact with.

## The Injection Attack Surface

In traditional REST APIs, injections are found in URL parameters, query strings, or JSON body fields. In GraphQL, injections occur within **Arguments** passed to queries and mutations.

### 1. SQL Injection via Inline Arguments
If the GraphQL execution engine passes an argument directly to a vulnerable SQL query inside the resolver, standard SQLi techniques apply.

**Vulnerable Resolver Logic (Node.js / Express):**
```javascript
const resolvers = {
  Query: {
    user: async (_, { username }) => {
      // VULNERABLE: Direct concatenation of the GraphQL argument
      const query = `SELECT * FROM users WHERE username = '${username}'`;
      return await db.query(query);
    }
  }
};
```

**Attacker Request (Inline Payload):**
```graphql
query {
  user(username: "admin' OR 1=1 --") {
    id
    email
    passwordHash
  }
}
```

### 2. The Type Checking Hurdle
GraphQL strictly enforces types. If the schema expects an `Int` for a user ID, you cannot inject `' OR 1=1 --` into that field because the GraphQL engine will reject it with a `400 Bad Request` or an execution error before the resolver is ever called.

**Blocked by Schema:**
```graphql
query {
  user(id: "1 OR 1=1") { # Engine blocks this if `id` is typed as Int!
    name
  }
}
```

**The Workaround:** Attackers focus their injection efforts on fields typed as `String`, `ID` (which accepts strings), or Custom Scalars (like `JSON` or `Upload`). If a developer uses a `String` type for a seemingly numeric field (e.g., `zipCode: String`), that becomes a prime target.

### 3. Injection via GraphQL Variables
Professional GraphQL clients rarely hardcode arguments directly into the query string (inline). Instead, they use GraphQL Variables. Attackers must test both inline arguments and variables, as WAFs might only inspect the query string and ignore the variables JSON object.

**Attacker Request (Using Variables):**
```json
{
  "query": "query GetUser($uname: String!) { user(username: $uname) { email } }",
  "variables": {
    "uname": "admin' UNION SELECT email, password FROM users --"
  }
}
```

### 4. NoSQL Injection
Because GraphQL is heavily adopted in the JavaScript/Node.js ecosystem, it is frequently backed by MongoDB. NoSQL injection is highly prevalent in GraphQL mutations.

**Attacker Request (NoSQL Object Injection via JSON variables):**
```json
{
  "query": "mutation Login($creds: LoginInput!) { login(input: $creds) { token } }",
  "variables": {
    "creds": {
      "username": "admin",
      "password": { "$ne": null } 
    }
  }
}
```
*Note:* If the `LoginInput` schema explicitly expects a string for the password, the NoSQL `$ne` object might be rejected by the type checker. However, if the developer used a generic `JSON` scalar type for an input configuration, NoSQL injection becomes trivial.

## Visualizing GraphQL Injection

```text
========================================================================================
                          HOW INJECTION FLOWS IN GRAPHQL
========================================================================================

  [ Client Payload ] 
   query { user(name: "admin'--") { id } }
         |
         v
  [ GraphQL Engine ]
         | -> 1. Parses query structure
         | -> 2. Checks types (Is "admin'--" a String? Yes.)
         | -> 3. Validation Passes. Routes to Resolver.
         v
  [ Resolver Function ]
         | -> Receives: args.name = "admin'--"
         | -> Executes: SELECT * FROM users WHERE name = 'admin'--'
         v
  [ PostgreSQL Database ]
         | -> Evaluates SQL. Ignores trailing quote due to comment.
         | -> Returns the Admin user record.
         v
  [ GraphQL Engine ]
         | -> Formats response based on requested fields ({ id })
         v
  [ Attacker ] <- Receives { "data": { "user": { "id": "1" } } }

========================================================================================
```

## How to Test for Injection
1. **Enumerate the Schema:** Dump the schema (via Introspection or Clairvoyance).
2. **Identify Target Fields:** Map all Queries and Mutations. Filter for arguments that accept `String`, `ID`, or custom unstructured scalars.
3. **Fuzz the Arguments:** Send standard SQLi polyglots (e.g., `'"`), blind time-based payloads (`pg_sleep(5)`), and OS command terminators (`; sleep 5 #`).
4. **Monitor the Errors:** If the application returns a raw database error in the `errors` array (`"message": "syntax error at or near '...'"`), you have a confirmed injection vulnerability.
5. **Extract Data:** Use UNION-based techniques or Error-based techniques. Since GraphQL lets you dictate the return shape, UNION attacks are often cleaner than in REST APIs.

## Real-World Example
An attacker targeted a cryptocurrency exchange's GraphQL API. They found a query used to fetch historical price charts:
`query { chartData(symbol: "BTC", timeframe: "1H") { price time } }`

The `timeframe` argument was typed as a `String`. The attacker injected a time-based blind SQLi payload:
`query { chartData(symbol: "BTC", timeframe: "1H'; SELECT pg_sleep(10)--") { price } }`

The server took exactly 10 seconds to respond. The attacker confirmed that the `timeframe` argument was concatenated directly into a Postgres query used by the analytics microservice. They proceeded to use boolean-based blind SQLi to extract API keys from an adjacent database table.

## How to Fix It
- **Parameterized Queries (Prepared Statements):** The defense against SQLi in GraphQL is the exact same as in REST. Resolvers must never concatenate GraphQL arguments directly into database queries. Always use ORMs (Prisma, Sequelize) or parameterized queries safely.
- **Strict Custom Scalars:** If an argument requires a specific format (like a Date, an Email, or a Zip Code), do not use the generic `String` type. Create custom GraphQL scalars (`scalar EmailAddress`) and implement regex validation within the scalar's parser logic. If the input fails the regex, it is rejected before reaching the resolver.

## Chaining Opportunities
- This vuln + [[10 - Chaining Playbook (Database Credentials)]] → Use GraphQL SQLi to extract credentials from `.env` files or the `users` table, escalating to full application compromise.
- This vuln + [[15 - Deserialization (Python Pickle)]] → If a GraphQL argument accepts a base64 encoded string that the resolver subsequently deserializes (common in Python/Graphene architectures), you can achieve Remote Code Execution.

## Related Notes
- [[06 - SQL Injection]]
- [[01 - What is GraphQL?]]
