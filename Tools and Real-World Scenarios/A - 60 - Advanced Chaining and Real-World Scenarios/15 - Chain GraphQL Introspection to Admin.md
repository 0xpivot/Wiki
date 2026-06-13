---
tags: [chaining, advanced, real-world, vapt]
difficulty: expert
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.15 Chain GraphQL to Admin"
---

# Advanced Chaining: GraphQL Introspection to Admin Takeover

## Introduction

GraphQL has rapidly replaced REST as the dominant paradigm for modern API development, offering unparalleled flexibility for front-end developers. However, this flexibility introduces a massive attack surface. Unlike REST, where endpoints are discrete and predictable, GraphQL operates through a single endpoint that exposes a complex, interconnected graph of data and operations.

This document outlines a highly effective attack chain targeting a modern single-page application (SPA). The attacker discovers a hidden GraphQL endpoint, reconstructs the schema via forced introspection, identifies an undocumented administrative mutation, exploits an IDOR/BOLA vulnerability to map user IDs, and leverages GraphQL batching to bypass rate limits, culminating in a complete vertical privilege escalation to Administrator.

This scenario highlights why traditional API security controls (like simple WAF rules or endpoint rate limiting) often fail against GraphQL architectures.

---

## The Attack Kill-Chain Architecture

The following ASCII diagram illustrates the flow from initial endpoint discovery to administrative takeover.

```text
+-----------------------+
|       Attacker        |
+-----------+-----------+
            | 1. Discovers `/v1/graphql` Endpoint
            | 2. Attempts Introspection (Blocked)
            v
+-----------------------+       3. Bypass via Clairvoyance / Field Suggestions
|   GraphQL API Gateway |  <------------------------------------------------+
+-----------+-----------+                                                   |
            | 4. Reconstructs full GraphQL Schema                           |
            v                                                               |
+-----------------------+                                                   |
|  Attacker Workspace   | (Analyzes schema offline)                         |
|  (InQL / GraphQLmap)  | -> Discovers `updateUserRole` hidden mutation     |
+-----------+-----------+                                                   |
            | 5. Exploit BOLA/IDOR in `getUser` query                       |
            |    to enumerate valid administrative User IDs                 |
            v                                                               |
+-----------------------+                                                   |
|   GraphQL API Gateway |  <------------------------------------------------+
+-----------+-----------+
            | 6. Prepares malicious mutation payload
            | 7. Uses Query Aliasing to bypass Rate Limiting / WAF
            v
+-----------------------+
|  Backend Resolvers    | (Executes the batched mutations)
|  & Database           | -> Updates attacker's role to "SUPER_ADMIN"
+-----------+-----------+
            | 8. Success Response
            v
+-----------------------+
| Administrator Console | (Attacker logs in with full privileges)
+-----------------------+
```

---

## Phase 1: Endpoint Discovery and Schema Reconstruction

The target application is a modern e-commerce platform. During passive reconnaissance, the attacker identifies traffic flowing to `/api/v1/graphql`. 

### 1.1 Introspection Attempts
The foundation of GraphQL security testing is obtaining the schema—the blueprint of all possible queries, mutations, and data types. The standard method is sending an Introspection Query.

```graphql
# Standard Introspection Query
query {
  __schema {
    types {
      name
    }
  }
}
```

The server responds with an error: `GraphQL introspection is not allowed`. The developers have disabled introspection in production, a common but insufficient security measure.

### 1.2 Bypassing Disabled Introspection
While full introspection is disabled, the GraphQL engine (e.g., Apollo, Hasura) often leaves "Field Suggestions" enabled by default. If a developer typos a query, the server responds with a helpful error: `Cannot query field "usrs" on type "Query". Did you mean "users"?`

Attackers use tools like `Clairvoyance` or `GraphQL Cop` to brute-force the schema using massive wordlists, relying on these error messages to accurately reconstruct the entire schema graph.

```bash
# Using Clairvoyance to reconstruct the schema via field suggestions
clairvoyance -u https://api.target.com/v1/graphql -o schema.json
```

---

## Phase 2: Schema Analysis and Vulnerability Discovery

With the `schema.json` reconstructed, the attacker imports it into a local visualization tool like GraphQL Voyager or Insomnia.

### 2.1 Identifying Hidden Operations
Analyzing the mutations (the operations used to modify data), the attacker discovers several undocumented, administrative mutations that are not utilized by the frontend application but exist in the backend schema:

```graphql
# Discovered hidden mutations
type Mutation {
  updateProfile(input: ProfileInput!): User!
  deleteAccount(id: ID!): Boolean!
  # HIDDEN / INTERNAL MUTATION
  internal_updateUserRole(userId: ID!, newRole: RoleEnum!): User!
}

enum RoleEnum {
  USER
  MANAGER
  SUPER_ADMIN
}
```

The `internal_updateUserRole` mutation is the golden ticket. However, it requires a valid `userId` (which are UUIDs, not sequential integers) and a `RoleEnum`.

---

## Phase 3: Exploiting BOLA (Broken Object Level Authorization)

To use the mutation on themselves, the attacker needs their own `userId`, which is hidden from the UI. Furthermore, they want to map out existing administrators.

### 3.1 IDOR / BOLA in GraphQL Queries
The attacker analyzes the `getUser` query. They notice that while the frontend only requests basic info, the schema allows requesting deeply nested data. 

```graphql
# Exploiting BOLA to extract UUIDs and Roles of other users
query {
  getPublicReviews {
    reviewText
    author {
      id          # Extracting the UUID
      email
      role        # Extracting the role
    }
  }
}
```

Because the developers failed to implement proper object-level authorization on the `author` type resolver, the attacker can extract the internal UUID and role of every user who has left a public review.

**Discovery:** The attacker finds their own UUID: `123e4567-e89b-12d3-a456-426614174000`.

---

## Phase 4: Exploiting the Mutation and Bypassing Limits

The attacker now attempts to execute the hidden administrative mutation to escalate their own privileges.

```graphql
mutation {
  internal_updateUserRole(
    userId: "123e4567-e89b-12d3-a456-426614174000", 
    newRole: SUPER_ADMIN
  ) {
    id
    role
  }
}
```

**Obstacle:** The server responds with `HTTP 429 Too Many Requests` or a WAF block. The API gateway is configured to block requests containing administrative keywords like `internal_updateUserRole` from non-whitelisted IP addresses.

### 4.1 Bypassing WAF and Rate Limits via Query Aliasing
GraphQL possesses a unique feature called **Aliasing**, which allows multiple instances of the same query or mutation to be sent in a single HTTP request. This fundamentally breaks traditional WAFs and rate-limiters, which expect one action per HTTP request.

The attacker crafts a batched payload. By sending hundreds of different mutations in one request, they bypass the rate limiter (which only counts 1 HTTP request). Furthermore, by renaming the operation, they can sometimes obfuscate the payload from simplistic WAF regex rules.

```graphql
# Using Aliasing to bypass limitations
mutation PrivilegeEscalation {
  attempt1: internal_updateUserRole(userId: "123e...", newRole: SUPER_ADMIN) { role }
  attempt2: updateProfile(input: { bio: "benign" }) { id }
  # The WAF might parse the request, see attempt2, and allow it, 
  # failing to deeply parse the AST to catch attempt1.
}
```

The server processes the GraphQL AST (Abstract Syntax Tree), executes `attempt1`, and successfully updates the attacker's role in the backend database.

### 4.2 Vertical Privilege Escalation Achieved
The attacker refreshes their session token. Because the backend authorization middleware now reads their role as `SUPER_ADMIN`, the UI unlocks the administrative dashboards. The attacker has achieved complete application takeover.

---

## Impact and Business Risk

The impact of this GraphQL chain is severe:
1. **Total Application Control:** The attacker has `SUPER_ADMIN` privileges, allowing them to view all user data, modify financial transactions, and alter application settings.
2. **Data Exposure:** Through the BOLA vulnerability, the attacker was able to scrape the PII of any user connected to a public object.
3. **Bypass of Perimeter Defenses:** The use of Query Aliasing renders traditional API gateways and WAFs ineffective, demonstrating that GraphQL security must be handled at the application/resolver level.

---

## Mitigation and Defense in Depth

Securing GraphQL requires specialized paradigms that differ significantly from REST security:

1. **Disable Introspection and Field Suggestions:**
   - In production, disable introspection entirely.
   - Crucially, disable "Field Suggestions" (e.g., in Apollo Server, ensure `NODE_ENV=production` which turns off stack traces and suggestions). This prevents tools like Clairvoyance from mapping the schema.

2. **Implement Robust Authorization at the Resolver Level:**
   - Do not rely on hiding mutations. All administrative operations must explicitly check the authorization context of the user making the request.
   - Implement Object Level Authorization. The `author` resolver should check if the currently authenticated user is authorized to view the `id` and `role` fields of the requested user. If not, return `null` or an error.

3. **GraphQL-Specific Rate Limiting (Query Complexity Analysis):**
   - Traditional HTTP rate limiting is useless against Query Aliasing.
   - Implement **Query Complexity Analysis**. Assign a "cost" to each field and mutation (e.g., `updateProfile` costs 1, `internal_updateUserRole` costs 50). Reject any GraphQL request where the total AST complexity exceeds a maximum threshold (e.g., max cost of 100 per request).
   - Implement **Max Depth** restrictions to prevent deeply nested queries (e.g., `user -> posts -> comments -> author -> posts`), which can lead to Denial of Service (DoS).

4. **WAFs for GraphQL:**
   - Deploy modern Web Application Firewalls capable of natively parsing GraphQL ASTs, rather than relying on flat regex rules against JSON bodies.

---

## Chaining Opportunities

- **GraphQL to SSRF:** GraphQL resolvers often fetch data from internal microservices. By exploiting injection flaws within the GraphQL arguments, an attacker can manipulate the resolver to perform SSRF against internal infrastructure.
- **GraphQL to SQLi:** If the resolver directly concatenates GraphQL arguments into backend SQL queries without parameterization, the attacker can leverage the flexible nature of GraphQL to execute highly complex SQL Injection payloads.

## Related Notes
- [[07 - Web Application Firewalls and Evasion]]
- [[20 - API Security Testing methodologies]]
- [[28 - Insecure Direct Object Reference (IDOR)]]
- [[34 - GraphQL Security and Exploitation]]
