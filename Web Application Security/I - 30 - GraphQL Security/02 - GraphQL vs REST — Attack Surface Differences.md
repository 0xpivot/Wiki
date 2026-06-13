---
tags: [vapt, graphql, rest, api, methodology]
difficulty: beginner
module: "30 - GraphQL Security"
topic: "30.02 GraphQL vs REST - Attack Surface Differences"
---

# 30.02 — GraphQL vs REST: Attack Surface Differences

## The Paradigm Shift in API Security
When transitioning from testing traditional REST architectures to GraphQL APIs, penetration testers must fundamentally realign their methodology. The transition from REST to GraphQL is not merely a change in payload syntax (JSON vs. GraphQL Query Language); it is a complete restructuring of how the client interacts with the server, how routing is handled, and where authorization logic must be enforced.

In REST, the attack surface is spread horizontally across hundreds of endpoints, verbs, and parameters. In GraphQL, the attack surface is concentrated vertically within a single endpoint, relying on a deeply nested graph of interconnected objects and resolvers.

Understanding these differences is critical to effectively hunting for vulnerabilities in modern web applications.

## Key Differences in the Attack Surface

### 1. Endpoints and Routing
**REST:** Relies on URL paths to dictate the resource being accessed. A typical API might expose `/api/users`, `/api/posts`, `/api/admin/config`. As an attacker, your first goal is *Endpoint Discovery* (fuzzing directories, reading swagger files). The attack surface is horizontal.
**GraphQL:** Exposes a single endpoint, almost universally `/graphql` (or `/api/graphql`, `/v1/graphql`). All requests, regardless of the data being accessed or modified, are sent to this single URL. You do not fuzz for hidden endpoints; instead, you fuzz for hidden *queries* and *mutations* within the schema.

### 2. HTTP Methods and Caching
**REST:** Heavily leverages HTTP verbs (`GET` for read, `POST` for create, `PUT`/`PATCH` for update, `DELETE` for removal). Because `GET` requests are idempotent, REST APIs can easily utilize standard HTTP caching mechanisms (CDN, proxy, browser caching) via headers like `Cache-Control`.
**GraphQL:** Almost universally uses `POST` requests for *everything*, including data retrieval (Queries). Because everything is a `POST` request with a complex JSON body, standard HTTP edge caching (like Cloudflare caching) is entirely bypassed by default. This makes GraphQL inherently more susceptible to Application-Layer Denial of Service (DoS) attacks, as requests hit the backend execution engine directly.

### 3. Status Codes and Error Handling
**REST:** Relies heavily on standard HTTP status codes. If you are unauthorized, you get a `401 Unauthorized`. If a resource doesn't exist, you get a `404 Not Found`. If you send bad data, you get a `400 Bad Request`.
**GraphQL:** By default, GraphQL almost always returns a `200 OK` HTTP status code, even if the query fails completely, if the user is unauthorized, or if a severe internal server error occurs. The actual error is embedded within the JSON response body under the `"errors"` array. 
*VAPT Implication:* Automated security scanners (like default Burp Active Scan or Nessus) often fail spectacularly against GraphQL because they rely on HTTP status codes to detect anomalies. They see a `200 OK` and assume the payload was safely processed, missing critical SQL injection or authorization bypasses.

### 4. Authorization and Access Control
**REST:** Authorization is typically implemented at the controller/route level. A middleware checks if the user has the 'admin' role before allowing access to the `GET /api/admin/users` route. This is relatively straightforward to audit.
**GraphQL:** Because there is only one route, authorization must be implemented at the *Resolver* level (the function that fetches data for a specific field). A single query might invoke 50 different resolvers. If a developer forgets to add an RBAC (Role-Based Access Control) check to the resolver for `User.socialSecurityNumber`, any user who constructs a query requesting that specific field will extract the data, bypassing the intended security model.

### 5. Input Validation and Type Checking
**REST:** Input validation is usually done manually in the controller or via a framework-specific validation library. It is prone to human error, leading to frequent SQL injections or Type Confusion vulnerabilities.
**GraphQL:** Features strict, built-in type checking via the Schema Definition Language. If a mutation expects an `Int` and you send a `"String"`, the GraphQL engine rejects the request before it even reaches the developer's resolver code. This eliminates a vast swath of basic injection attacks, but pushes attackers to look for deeper logical flaws or injections within string-based inputs.

## Visualizing the Attack Surface Shift

```text
========================================================================================
                          ATTACK SURFACE: REST vs GRAPHQL
========================================================================================

 [ REST ATTACK SURFACE ] — HORIZONTAL
 
    GET /api/users/1       --> Check IDOR, SQLi
    POST /api/users        --> Check Mass Assignment, XSS
    PUT /api/users/1       --> Check Auth Bypass, CSRF
    DELETE /api/users/1    --> Check Privilege Escalation
    GET /api/hidden_admin  --> Found via DirBuster / Fuzzing

    * Attackers scan ACROSS multiple URLs and HTTP Verbs.
    * Security relies on Route-based Middleware.

----------------------------------------------------------------------------------------

 [ GRAPHQL ATTACK SURFACE ] — VERTICAL / NESTED

                   POST /graphql (Always 200 OK)
                                |
          +---------------------+---------------------+
          |                     |                     |
     Query (Read)         Mutation (Write)    Subscription (Listen)
          |                     |                     |
   +------+------+       +------+------+       +------+------+
   |             |       |             |       |             |
 user()       posts() update()   deleteUser() onMessage()   onAlert()
   |             |
+--+--+       +--+--+
|     |       |     |
id  email   title author
      |             |
 (Auth Bypass?)  (IDOR?)

    * Attackers scan DOWN into the nested object graph.
    * Security relies on Field-Level Resolvers.
    * Discovered via Introspection, not directory brute-forcing.

========================================================================================
```

## How This Impacts Penetration Testing Methodology

When attacking a GraphQL API, your workflow changes significantly:

1. **Discovery is Schema-centric:** Instead of running `ffuf` or `dirb` against a wordlist of common endpoints, you attempt an **Introspection Query**. If introspection is disabled, you use tools like `clairvoyance` to brute-force the schema structure using GraphQL's helpful error messages ("Did you mean X?").
2. **Scan for Batching:** GraphQL supports query batching (sending an array of queries in a single HTTP request). Attackers use this to bypass rate limits. Instead of sending 1,000 HTTP requests to brute-force an OTP, you send 1 HTTP request containing 1,000 batched GraphQL queries.
3. **Hunt for Inconsistent Resolvers:** The golden goose in GraphQL pentesting is finding a deeply nested object that lacks the authorization checks present at the top level. For example, `query { myProfile { email } }` might be secure, but `query { otherUser(id:2) { friends { email } } }` might expose the email because the `friends` resolver forgot to verify privacy settings.
4. **Denial of Service via Complexity:** Because the client dictates the structure, attackers can craft exponentially complex, deeply nested queries (`query { user { posts { author { posts { author { ... } } } } } }`) to exhaust server CPU and memory, unless the server explicitly implements Query Depth Limiting.

## Real-World Example
A bug bounty hunter was testing a major e-commerce platform. The platform used GraphQL. The hunter attempted to find IDOR by changing the user ID in a mutation. The server returned:

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "errors": [
    {
      "message": "User is not authorized to perform this action.",
      "path": ["updateProfile"]
    }
  ],
  "data": {
    "updateProfile": null
  }
}
```

A traditional vulnerability scanner saw the `HTTP 200 OK` and assumed the request was successful, completely missing the fact that the application successfully blocked the attack. The hunter, understanding GraphQL, knew they had to write custom Burp Match/Replace rules or use a GraphQL-aware scanner (like InQL) to accurately parse the `errors` array to determine if their payloads were actually bypassing security controls.

## Chaining Opportunities
- This vuln + [[04 - GraphQL Enumeration (clairvoyance, graphql-cop)]] → Because endpoints aren't discovered via traditional fuzzing, you must rely on GraphQL-specific enumeration techniques to map the attack surface.
- This vuln + [[06 - GraphQL Batching Attacks (brute force via batching)]] → Exploit the single-endpoint nature of GraphQL to bypass traditional IP-based rate limiting on the WAF.

## Related Notes
- [[01 - What is GraphQL?]]
- [[03 - Introspection Query — Information Disclosure]]
- [[05 - GraphQL Injection]]
