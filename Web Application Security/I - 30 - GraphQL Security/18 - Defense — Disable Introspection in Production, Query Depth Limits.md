---
tags: [vapt, graphql, defense, mitigation, architecture]
difficulty: advanced
module: "30 - GraphQL Security"
topic: "30.18 Defense - Disable Introspection, Query Depth, Cost Analysis"
---

# 30.18 — Defense: Securing GraphQL in Production

## The GraphQL Security Paradigm
Securing a GraphQL API requires abandoning the perimeter-defense mindset of REST. You cannot rely solely on a Web Application Firewall (WAF) or route-level middleware. Because GraphQL relies on a single endpoint and deeply nested, client-dictated queries, security must be implemented structurally within the schema, the engine configuration, and the resolvers.

A secure GraphQL implementation relies on five foundational pillars.

## 1. Disable Introspection and IDEs
The most critical configuration error is leaving developer tools active in production.
- **Introspection:** Must be disabled unconditionally. If an attacker cannot easily dump the schema, their attack speed drops drastically.
- **Field Suggestions:** Disable the "Did you mean X?" error messages to prevent Clairvoyance enumeration.
- **Playgrounds:** Ensure GraphiQL, Apollo Playground, and Altair routes are stripped from the production build.

```javascript
// Apollo Server Production Config
const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV !== 'production', // Disable in Prod
  playground: false,
  formatError: (err) => {
    // Sanitize stack traces and suppress suggestion leaks
    if (err.message.startsWith('Cannot query field')) return new Error('Invalid query structure');
    return new Error('Internal Server Error');
  }
});
```

## 2. Implement Query Complexity and Depth Limiting
Because attackers can dictate the shape of the query, you must prevent Application-Layer DoS attacks (Cyclical and Alias attacks).

- **Depth Limiting:** Use libraries like `graphql-depth-limit`. Reject any query that nests deeper than 5 or 7 levels. This completely neutralizes cyclical DoS attacks.
- **Cost Analysis (Complexity):** Assign a computational cost to every field. `user.name` = 1. `searchDatabase()` = 50. Use `graphql-query-complexity` to calculate the total cost of the incoming query. If the cost exceeds a threshold (e.g., 500 points), the engine rejects the query before executing any resolvers. This neutralizes Alias batching DoS.

## 3. Implement Resolver-Level Authorization
Never trust the route. Never assume path-based authorization.
- **Context-Aware Resolvers:** Every resolver that accesses sensitive data or modifies state must verify the role of `context.user`.
- **Field-Level Granularity:** Do not just authorize the top-level query. Authorize the nested fields. If a user queries `Company -> Employees -> Salary`, the `Salary` resolver must explicitly check if the user is HR, regardless of how they reached that node.
- **Declarative Directives:** Use schema directives like `@auth(requires: ADMIN)` to handle authorization. This removes the burden of writing manual `if (user.role)` checks in every single resolver, drastically reducing human error.

```graphql
type Mutation {
  deleteAccount(id: ID!): Boolean @auth(requires: ADMIN)
}
```

## 4. Disable Query Batching
If your frontend application does not explicitly rely on sending JSON arrays to batch multiple queries into a single HTTP request, disable array batching entirely at the GraphQL engine layer.
This prevents attackers from bypassing WAF rate limits by sending 10,000 login mutations in a single request. If batching is necessary, enforce a strict limit (e.g., max 3 queries per batch).

## 5. Utilize Persisted Queries (Query Allowlisting)
**Persisted Queries** represent the ultimate defense for a GraphQL API.
In a highly secure environment, the frontend client should *never* send raw GraphQL query strings to the server. 

**How it works:**
1. During the build phase of the frontend application, a script parses all the GraphQL queries used in the code.
2. It hashes each query (e.g., `SHA-256(query) -> 8f4e3c...`).
3. It uploads a map of hashes-to-queries to the GraphQL server.
4. In production, the frontend client only sends the Hash (and variables) to the server, not the raw query string.
   `POST /graphql { "queryId": "8f4e3c...", "variables": { "id": 1 } }`

**Security Benefit:** The server completely rejects any raw query string. It only executes queries that match a known, pre-approved hash. This renders Introspection, Enumeration, Injection, Mass Assignment, and Malicious Depth attacks mathematically impossible, as the attacker cannot force the server to execute arbitrary structures.

## Visualizing Defense-in-Depth

```text
========================================================================================
                          GRAPHQL DEFENSE IN DEPTH
========================================================================================

  [ Attacker Payload ]
       |
       v
  [ 1. Transport Layer (WAF/Gateway) ]
       | -> Rate limits HTTP requests. Blocks SQLi signatures in variables.
       v
  [ 2. Engine Validation Phase ]
       | -> Checks if Introspection is requested? (Rejects)
       | -> Checks Persisted Query Hash? (Rejects unknown queries)
       | -> Calculates Query Depth? (Rejects > 7 levels)
       | -> Calculates Query Cost? (Rejects > 1000 points)
       v
  [ 3. Execution Phase (Resolvers) ]
       | -> @auth Directive evaluates Role? (Rejects unauthorized)
       | -> Custom Scalar parses Input? (Strips invalid characters)
       | -> Executes Business Logic.

========================================================================================
```

## Chaining Opportunities
- This defense directly mitigates [[30.11 GraphQL Depth and Complexity DoS]].
- This defense directly mitigates [[30.06 GraphQL Batching Attacks (brute force via batching)]].
- This defense directly mitigates [[30.03 Introspection Query — Information Disclosure]].

## Related Notes
- [[01 - What is GraphQL?]]
- [[30.14 GraphQL Authorization Bypass]]
