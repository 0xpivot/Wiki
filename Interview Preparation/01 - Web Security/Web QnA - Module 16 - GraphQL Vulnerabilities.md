---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 16"
---

# Web QnA - Module 16 - GraphQL Vulnerabilities

## Architectural Overview: GraphQL Execution

```text
       [Client]                              [Web Server]
          |                                       |
          |  POST /graphql                        |
          |  {"query": "{ user(id:1) {        |
          |     name, email,                  |
          |     friends {                     |
          |       name, email,                |
          |       friends {                   |
          |         ... (Nested Depth)        |
          |       }                           |
          |     }                             |
          |  }}"}                             |
          |-------------------------------------->|
          |                                       |
          |                                 [GraphQL Engine]
          |                                  /    |     \
          |                            Resolver Resolver Resolver
          |                               /       |        \
          |                          [DB]       [DB]      [Microservice]
          |<--------------------------------------|
          |  {"data": {"user": {...}}}            |
```

## Formal Technical Questions

**Q1: Explain the fundamental difference between Introspection and Information Disclosure in the context of GraphQL, and why disabling Introspection is not a silver bullet.**
**A1:** 
Introspection is a built-in GraphQL feature allowing clients to query the schema itself (using `__schema` or `__type` meta-fields) to discover available queries, mutations, subscriptions, and types. Leaving this enabled in production is considered a vulnerability as it provides attackers with a complete map of the web application's attack surface.
However, disabling introspection is not a silver bullet because of *Information Disclosure* via verbose error messages. If an attacker guesses a field name, GraphQL engines (like Apollo) often return "Did you mean X?" error messages (schema suggestion features). Attackers can script dictionary attacks to brute-force the schema, effectively rebuilding the entire schema even with introspection explicitly disabled. Furthermore, field stuffing or fuzzing can disclose internal fields meant for admin use only.

**Q2: How does Query Batching lead to resource exhaustion, and how does it bypass rate-limiting mechanisms?**
**A2:** 
Query batching allows a client to send an array of multiple queries in a single HTTP request to the web server. Instead of parsing `{"query": "..."}`, the attacker sends `[{"query": "..."}, {"query": "..."}, ...]`.
This bypasses traditional web application firewall (WAF) or IP-based rate limiting because those mechanisms typically track the number of *HTTP requests*. A single HTTP request containing 10,000 login mutations will only register as one hit against the rate limiter, but the GraphQL engine will execute all 10,000 attempts against the resolver. This leads to both authentication brute-forcing and severe Application-layer Denial of Service (DoS) as the backend database is overwhelmed by the burst of resolver executions.

**Q3: Describe how Insecure Direct Object Reference (IDOR) manifests differently in GraphQL compared to traditional web applications.**
**A3:** 
In traditional web applications, IDOR often occurs in the URL (e.g., `/profile/1234`). In GraphQL, the URL is static (usually `/graphql`). IDOR manifests in the query arguments and nested relationships. 
For example, a query might look like: `query { getInvoice(id: "1234") { amount, status } }`. 
The vulnerability exists if the resolver for `getInvoice` simply fetches the record from the database without validating if the currently authenticated user (derived from the HTTP session or token) owns that invoice. Furthermore, IDOR in GraphQL can be nested. Even if `getInvoice` is secure, an attacker might traverse relationships: `query { user(id: "my_id") { invoices(id: "target_id") { amount } } }`. If the `invoices` resolver doesn't check ownership, the authorization check on the root `user` query is bypassed.

## Scenario-Based Questions

**Q4: You are on a Red Team engagement. The target web application uses GraphQL. Introspection is disabled, and the server returns generic error messages (no "Did you mean..."). You capture a legitimate query: `query { currentUser { id, username } }`. How do you proceed to discover hidden mutations and data?**
**A4:** 
Since automated schema extraction via introspection and error-based guessing is thwarted, I must rely on passive intelligence and context-aware fuzzing:
1. **Source Code Mapping:** I will analyze the client-side JavaScript bundles. Often, web applications ship with Apollo client or Relay stores that contain fragmented queries, mutations, or even full schema definitions embedded in the compiled JavaScript.
2. **Contextual Fuzzing:** Using tools like Clairvoyance or customized Burp Suite Intruder payloads, I will fuzz the fields of known types. If `currentUser` has `id` and `username`, I will test `email`, `role`, `isAdmin`, `passwordResetToken`, etc.
3. **HTTP Method Manipulation:** Sometimes, GET requests to `/graphql?query={__schema{types{name}}}` bypass introspection filters that only check POST bodies. 
4. **Operation Name Fuzzing:** Developers sometimes leave legacy operations in the codebase. Fuzzing the `operationName` field with common values (`adminPanel`, `deleteUser`) might yield results if the queries are persisted on the backend.

**Q5: During a web application assessment, you find a mutation: `mutation { updateProfile(userId: 1, email: "attacker@evil.com") { success } }`. When you run it, the server responds with an error: "Unauthorized: Signature mismatch". The application does not use JWTs, just a standard session cookie. What is likely happening, and how might you bypass it?**
**A5:** 
The application is likely employing Persisted Queries or an application-layer signing mechanism for GraphQL payloads to prevent arbitrary query execution. 
With Persisted Queries, the client sends a hash (often SHA-256) instead of the full query string: `{ "extensions": { "persistedQuery": { "version": 1, "sha256Hash": "..." } } }`. If the hash doesn't match a pre-approved query on the server, it fails.
To bypass this:
1. **Hash Extraction:** If the application generates these hashes client-side dynamically, the signing logic and key might be in the client-side JavaScript. I can reverse-engineer it to sign my malicious `updateProfile` mutation.
2. **Fallback Exploitation:** Many implementations allow falling back to full queries if the hash isn't found. I would try removing the `extensions` block entirely and just sending the raw query.
3. **HTTP Parameter Pollution (HPP):** Sending the query via GET while providing a dummy hash in the POST body, tricking the routing layer.

**Q6: You successfully exploited an XSS vulnerability on a web application that relies heavily on GraphQL for state management. How do you pivot this into a full account takeover via the GraphQL endpoint?**
**A6:** 
With XSS, I have execution in the victim's browser, meaning I inherit their session cookies and LocalStorage (if used for auth tokens). 
To achieve account takeover:
1. **Dynamic Schema Interaction:** I will write a JavaScript payload that sends an asynchronous `fetch` request to the `/graphql` endpoint from the victim's context.
2. **Mutation Execution:** I will construct a payload that executes an `updateUser` mutation to change the victim's email address to one I control, or change their password directly if the mutation does not require the "current password".
```javascript
fetch('/graphql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: `mutation { updateEmail(newEmail: "attacker@evil.com") { success } }`
  })
});
```
3. **Data Exfiltration:** Alternatively, I can query sensitive fields (e.g., `query { myWallet { privateKey, balance } }`) and exfiltrate the JSON response to my external server.

## Deep-Dive Defensive Questions

**Q7: Explain the concept of "Query Cost Analysis" in GraphQL defense. How does it prevent resource exhaustion better than simple depth limiting?**
**A7:** 
Simple depth limiting restricts how deeply nested a query can be (e.g., max depth of 5). However, a malicious user can still construct a query with a depth of 3 that requests 10,000 items per level, causing massive database load (e.g., `users(first: 1000) { posts(first: 1000) { comments(first: 1000) } }`).
Query Cost Analysis calculates a dynamic "cost" for a query *before* execution based on an Abstract Syntax Tree (AST) evaluation. The security team assigns weights to different fields. A scalar field like `name` might cost 1, while a database-intensive field like `transactions` might cost 10. Multipliers are applied for pagination arguments (e.g., `first: 1000` multiplies the cost of nested fields by 1000). 
Before the engine executes the query, it calculates the total cost. If the cost exceeds a predefined threshold (e.g., 5000), the query is rejected outright. This is vastly superior to depth limiting as it directly correlates with actual computational expense.

**Q8: How should authorization be properly implemented in a GraphQL architecture to prevent nested IDORs?**
**A8:** 
Authorization must **never** be implemented in the GraphQL routing or controller layer. It must be implemented in the *Business Logic Layer*.
When the GraphQL engine resolves a query, it should pass the execution context (which contains the authenticated user's details) down to the resolvers. However, resolvers themselves shouldn't contain raw authorization checks either.
Instead, the resolver should delegate to a dedicated service class or data model layer.
For example:
`Resolver -> getInvoice(id)` -> calls `InvoiceService.getById(userContext, id)`.
The `InvoiceService` is responsible for querying the database and explicitly appending a `WHERE owner_id = userContext.id` clause. This ensures that regardless of how the invoice is requested—whether at the root level or deeply nested inside another query—the business logic enforcing data ownership is always invoked.

## Real-World Attack Scenario

**The Circular DoS Attack**
A financial tech company deployed a new web dashboard powered by GraphQL. The application allowed users to view their network of referrals. The schema included a `User` type with a `referredBy` field (pointing to another `User`) and a `referrals` field (returning an array of `User` objects).

1. **Reconnaissance:** The attacker discovered the endpoint and mapped the schema using a leaked client-side dictionary.
2. **Vulnerability Identification:** The attacker noted the bidirectional relationship between `User -> referredBy` and `User -> referrals`. There was no maximum depth limit configured on the GraphQL server.
3. **Exploitation:** The attacker crafted a deeply nested query:
```graphql
query {
  user(id: "1337") {
    referrals {
      referredBy {
        referrals {
          referredBy {
            referrals {
              name
            }
          }
        }
      }
    }
  }
}
```
4. **Impact:** The attacker duplicated this nesting 1,000 levels deep. When submitted, the GraphQL engine attempted to resolve the tree. Since each step required an expensive database JOIN and object instantiation, the server's CPU spiked to 100%, and the Node.js event loop became completely blocked. The entire web application went offline for all legitimate users. A single malicious HTTP request resulted in total Application DoS.

## Chaining Opportunities

- **GraphQL Batching -> Rate Limit Bypass -> Account Takeover:** Attackers can bypass login rate limits by batching 50,000 mutation attempts (`login(user, pass)`) into a single array payload.
- **CSRF -> GraphQL Mutation:** If the `/graphql` endpoint uses cookie-based authentication and lacks CSRF tokens, attackers can trick victims into executing state-changing mutations via a malicious web page.
- **SQL Injection in Resolvers:** GraphQL is just a routing language. If the backend resolver concatenates user input into a SQL string without parameterization, standard SQLi can be achieved through GraphQL query arguments.

## Related Notes
- [[02 - Web Application Firewalls (WAF) Bypass]]
- [[07 - Insecure Direct Object Reference (IDOR)]]
- [[12 - Application Denial of Service (DoS)]]
- [[21 - Advanced Cross-Site Scripting (XSS)]]
