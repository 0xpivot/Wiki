---
tags: [vapt, graphql, authorization, bfla, privilege-escalation]
difficulty: advanced
module: "30 - GraphQL Security"
topic: "30.14 GraphQL Authorization Bypass"
---

# 30.14 — GraphQL Authorization Bypass (BFLA)

## What is it?
While Insecure Direct Object Reference (See [[30.08 GraphQL IDOR]]) focuses on accessing *data* belonging to someone else, Authorization Bypass—specifically Broken Function Level Authorization (BFLA)—focuses on executing *actions* or accessing *administrative functions* that the user does not have the privilege to perform.

In REST architectures, preventing BFLA is relatively straightforward: developers map roles to URL paths (e.g., `RequireRole('admin')` on `/api/admin/*`). 

In GraphQL, there are no paths. Everything routes through `/graphql`. Therefore, authorization logic must be intricately woven into the schema execution pipeline. If developers fail to attach authorization rules to specific Mutations or Queries, any authenticated user (or sometimes even unauthenticated users) can execute administrative functions, leading to immediate Privilege Escalation.

## The Authorization Attack Surface

### 1. Missing Resolver-Level Authorization
The most common cause of BFLA in GraphQL is simply forgetting to write the authorization check inside the resolver function.

**Vulnerable Resolver Logic:**
```javascript
const resolvers = {
  Mutation: {
    // SECURE: Checks if the user is an admin
    deletePost: async (_, { id }, context) => {
      if (context.user.role !== 'ADMIN') throw new Error('Unauthorized');
      return await db.posts.delete(id);
    },

    // VULNERABLE: Developer forgot the context check!
    deleteUser: async (_, { id }) => {
      return await db.users.delete(id);
    }
  }
};
```

**The Attack:** An attacker with a standard "Viewer" or "Customer" account discovers the `deleteUser` mutation via Introspection or Enumeration. Because the resolver lacks the `context.user.role === 'ADMIN'` check, the GraphQL engine happily executes the deletion logic.

### 2. Flawed Middleware / Gateway Authorization
To avoid writing authorization checks in every single resolver, organizations often use API Gateways (like Kong or an Nginx reverse proxy) or GraphQL Middleware to enforce security. However, these tools are often misconfigured to rely on HTTP layer data rather than GraphQL AST parsing.

**The Flaw:**
A WAF rule might try to block access to the `adminData` query by looking for the string `"adminData"` in the HTTP request body.
`Rule: BLOCK IF body CONTAINS "adminData" AND role != 'ADMIN'`

**The Bypass (Using Aliases or Variables):**
Attackers can easily bypass regex-based WAF rules by using GraphQL's structural flexibility.
- Using Variables: The query is `query Get($q: String!) { ... }` and the WAF doesn't parse the `variables` JSON object.
- Using Aliases: `query { hidden_data: adminData { secret } }`. If the WAF only looks for `query { adminData`, it misses the alias.
- Using Encoding: Sending the query in Unicode or using line breaks and excessive whitespace that breaks the WAF's simple regex.

### 3. Exploiting Custom Directives
Developers often write custom schema directives to handle authorization declaratively (e.g., `@auth(role: "ADMIN")`). 

**Schema:**
```graphql
type Mutation {
  promoteUser(id: ID!): User @auth(role: "ADMIN")
}
```

If the implementation of the `@auth` directive is flawed—for example, if it checks `context.user.role.includes(args.role)` and the attacker's role is `"SUB_ADMIN"`, the `.includes()` method evaluates to true. Exploiting flaws in custom directive logic is a high-yield tactic.

## Visualizing GraphQL BFLA

```text
========================================================================================
                          GRAPHQL PRIVILEGE ESCALATION
========================================================================================

  [ Attacker (Role: Standard User) ]
       |
       |  mutation { setSystemMaintenanceMode(enabled: true) }
       |-----------------------------------------------------------> [ GraphQL Engine ]
                                                                             |
                                     (Parses syntax. Valid mutation.)        |
                                     (Routes to resolver.)                   |
                                                                             v
                                                           [ setSystemMaintenanceMode() ]
                                                                (NO RBAC CHECK FOUND)
                                                                (Updates DB setting)
                                                                             |
       |  { "data": { "setSystemMaintenanceMode": "Success" } }
       |<--------------------------------------------------------------------+
       |
  [ Entire application is taken offline by a standard user ]

========================================================================================
```

## How to Test for Authorization Bypass
1. **Map the Privileged Schema:** Obtain two accounts: an Admin account and a Standard account. Use Introspection on the Admin account to map out all sensitive queries and mutations (e.g., `makeAdmin`, `deleteAccount`, `viewAuditLogs`).
2. **Execute as Standard User:** Take the sensitive mutations discovered via the Admin account and attempt to execute them using the Bearer token of the Standard account. If the server responds with data or a success message instead of a `403` or `"Unauthorized"` error, you have a confirmed BFLA vulnerability.
3. **Execute Unauthenticated:** Strip the `Authorization` header entirely. Attempt to execute the mutations. Some resolvers check if the role matches, but fail open if the `context.user` object is null.
4. **Bypass Middleware:** If you receive an unauthorized error, try obfuscating the query (using aliases, fragments, or variables) to determine if the authorization is improperly handled at a WAF/Gateway layer instead of deep within the GraphQL execution engine.

## Real-World Example
A Bug Bounty researcher was investigating a cloud-based CRM. The application used GraphQL. By intercepting traffic from an Administrator account, they found a mutation used to reset any user's Two-Factor Authentication:
`mutation { resetMFA(userId: "123") { newRecoveryCodes } }`

The researcher logged into their own low-privileged "Guest" account, intercepted a completely different request, and replaced the payload with the `resetMFA` mutation, targeting the CEO's `userId`. 

The developers had correctly secured all the "Read" queries, but they assumed the `resetMFA` mutation was safe because only the Admin UI had the button to trigger it. The GraphQL resolver for `resetMFA` lacked a role check. The researcher successfully disabled the CEO's 2FA and gained the recovery codes, resulting in a critical Account Takeover.

## How to Fix It
- **Mandatory Resolver Context Checks:** Every single resolver that performs a sensitive action or accesses sensitive data MUST verify the role of the user requesting it.
  ```javascript
  // The correct way
  if (!context.user || context.user.role !== 'ADMIN') {
    throw new AuthenticationError('Requires admin privileges');
  }
  ```
- **Use Authorization Directives:** Frameworks like Apollo support schema directives. Using `@auth(requires: ADMIN)` directly in the schema definition makes security declarative and much harder for developers to "forget" during implementation.
- **Fail Closed:** Ensure that if `context.user` is undefined (unauthenticated), all resolvers default to throwing an Unauthorized error.

## Chaining Opportunities
- This vuln + [[30.04 GraphQL Enumeration (clairvoyance, graphql-cop)]] → Because low-privileged users don't have the UI buttons for administrative actions, you must use enumeration to discover the names of the privileged mutations before you can attempt to bypass their authorization.
- This vuln + [[30.09 GraphQL Mutations — Unauthorized Write Operations]] → BFLA is the primary mechanism that makes unauthorized write operations possible.

## Related Notes
- [[30.08 GraphQL IDOR]]
- [[21.01 What is Access Control]]
