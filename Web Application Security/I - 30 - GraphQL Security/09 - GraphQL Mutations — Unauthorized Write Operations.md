---
tags: [vapt, graphql, mutations, mass-assignment, authorization]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.09 GraphQL Mutations - Unauthorized Write Operations"
---

# 30.09 — GraphQL Mutations: Unauthorized Write Operations

## What is it?
In GraphQL, **Mutations** are the equivalent of `POST`, `PUT`, `PATCH`, and `DELETE` requests in REST. They are explicitly designed to alter state on the server (create, update, or destroy data). 

Vulnerabilities in mutations are almost always critical because they move beyond Information Disclosure (like Queries) and directly into Data Integrity violations, Privilege Escalation, and Account Takeover. The two primary flaws found in GraphQL mutations are **Missing Authorization (IDOR/BOLA)** and **Mass Assignment**.

## Attack Vectors for Mutations

### 1. Missing Authorization (Mutation IDOR)
Just as a query resolver might fail to check if you own the record you are reading (See [[08 - GraphQL IDOR]]), a mutation resolver might fail to check if you have permission to modify the record.

**Vulnerable Mutation Schema:**
```graphql
type Mutation {
  updateEmail(userId: ID!, newEmail: String!): User
}
```

**The Attack:** 
If the backend resolver takes the `userId` argument and immediately executes an `UPDATE users SET email = ? WHERE id = ?` without verifying that the authenticated session belongs to `userId`, an attacker can achieve massive account takeover by simply swapping the ID and pointing the victim's email to an attacker-controlled address.

**Attacker Request:**
```graphql
mutation {
  updateEmail(userId: "ADMIN_ID_123", newEmail: "hacker@evil.com") {
    id
    email
  }
}
```

### 2. Mass Assignment (Over-posting)
GraphQL's strong typing encourages developers to use **Input Object Types**. Instead of passing 20 separate arguments to a mutation, developers create a single `Input` object. 

**Vulnerable Schema Example:**
```graphql
input UserUpdateInput {
  firstName: String
  lastName: String
  bio: String
  role: String      # Danger!
  isAdmin: Boolean  # Danger!
}

type Mutation {
  updateProfile(input: UserUpdateInput!): User
}
```

**The Attack:** 
The frontend UI might only provide form fields for `firstName` and `bio`. However, the GraphQL engine accepts the entire `UserUpdateInput` object. If the developer blindly takes the input object and merges it into the database (`db.users.update(id, input)`), an attacker can manually append sensitive fields to the mutation payload to escalate their privileges.

**Attacker Request:**
```graphql
mutation {
  updateProfile(input: {
    firstName: "Alice",
    isAdmin: true,
    role: "SuperAdmin"
  }) {
    id
    role
  }
}
```

### 3. Bypassing Application Logic via Unexpected Mutations
Developers often create internal mutations for administration, debugging, or automated CRON jobs, assuming they are safe because they aren't wired up to the frontend UI. 

Examples:
- `verifyEmailWithoutToken(userId: ID!)`
- `forcePasswordReset(userId: ID!, newPass: String!)`
- `addAdminRole(userId: ID!)`

If Introspection is enabled (See [[03 - Introspection Query — Information Disclosure]]) or the schema is enumerated via Clairvoyance (See [[04 - GraphQL Enumeration (clairvoyance, graphql-cop)]]), an attacker will discover these mutations. Because developers assumed they were "hidden", they frequently lack strict RBAC checks, leading to instant systemic compromise.

## Visualizing Mass Assignment

```text
========================================================================================
                          MASS ASSIGNMENT IN GRAPHQL
========================================================================================

  [ Frontend UI ]
  Only shows fields for: "Name", "Bio"
         |
  [ Attacker (Burp Suite) ]
  Intercepts the mutation and adds: "isAdmin: true"
         |
  mutation { updateProfile(input: { name: "A", bio: "B", isAdmin: true }) }
         |
         v
  [ GraphQL Engine ]
  Schema accepts 'isAdmin'. Types match. Forwards to Resolver.
         |
         v
  [ Resolver ]
  const newUserData = args.input;
  db.collection('users').updateOne({id: session.id}, {$set: newUserData});
         |
         v
  [ Database ]
  User is now an Administrator.

========================================================================================
```

## How to Test for Mutation Vulnerabilities
1. **Enumerate all Mutations:** Use Introspection or enumeration tools to get a complete list of every mutation the server accepts.
2. **Review Input Types:** For every mutation, inspect its `input` arguments. Look for sensitive fields like `role`, `status`, `balance`, `isAdmin`, `verified`, or `ownerId`.
3. **Attempt Mass Assignment:** Even if a field isn't explicitly defined in the `Input` type, try injecting it anyway. Sometimes the GraphQL engine passes undeclared JSON fields through to the resolver if the type checking isn't perfectly strict (or if the input type uses a custom unstructured `JSON` scalar).
4. **Test for IDOR:** For every mutation that takes an `ID` (e.g., `deletePost(id: ID!)`), log in as User A, create a resource, note its ID, then log in as User B and attempt to execute the mutation against User A's ID.

## Real-World Example
A pentester was analyzing a SaaS application's GraphQL endpoint. The application had a feature where users could invite colleagues to their team via email. The mutation was structured as follows:

```graphql
mutation {
  inviteUser(teamId: 10, email: "colleague@company.com", role: "VIEWER") {
    status
  }
}
```

The pentester noticed the `role` parameter. They changed it from `"VIEWER"` to `"OWNER"` and executed the request. The server accepted the mutation. The pentester had successfully invited a rogue account to a target team with full administrative ownership privileges, bypassing the entire billing and permission structure of the SaaS platform.

## How to Fix It
- **Explicit Field Mapping (Prevent Mass Assignment):** Resolvers should *never* blindly merge user input directly into the database. Developers must explicitly map and assign only the safe, expected fields from the input argument to the database model.
- **Separate Input Types:** Do not use the same `UserUpdateInput` type for both regular users and administrators. Create a specific `AdminUserUpdateInput` for admin operations, and a restricted `PublicUserUpdateInput` for standard users.
- **Contextual Authorization:** Every mutation that modifies a resource MUST verify that the `context.user` (the authenticated session) has the explicit right to modify the resource specified in the mutation arguments.

## Chaining Opportunities
- This vuln + [[03 - Introspection Query — Information Disclosure]] → Introspection is the absolute best way to find Mass Assignment vectors, as it reveals the exact structure of the Input Types expected by the server.
- This vuln + [[06 - GraphQL Batching Attacks (brute force via batching)]] → If a mutation allows sending a private message, an attacker can batch 10,000 `sendMessage` mutations in a single HTTP request to mass-spam users, bypassing anti-spam WAF rules.

## Related Notes
- [[08 - GraphQL IDOR]]
- [[25.15 - Hidden API Parameters]] (Mass Assignment in REST)
