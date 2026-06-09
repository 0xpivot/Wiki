---
tags: [vapt, graphql, enumeration, tooling, brute-force]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.04 GraphQL Enumeration (clairvoyance, graphql-cop)"
---

# 30.04 — GraphQL Enumeration (Without Introspection)

## The Problem: Introspection is Disabled
In [[03 - Introspection Query — Information Disclosure]], we explored how leaving introspection enabled provides an attacker with a flawless map of the API. However, modern security practices dictate that introspection must be disabled in production. 

When you send the `__schema` query to a properly hardened GraphQL server, you receive an error:
```json
{
  "errors": [
    {
      "message": "GraphQL introspection is not allowed by Apollo Server, but the query contained __schema or __type. To enable introspection, pass introspection: true to ApolloServer in production"
    }
  ]
}
```

Does this mean the API is secure? Absolutely not. GraphQL was built to be exceptionally developer-friendly. Even with introspection explicitly disabled, the GraphQL engine's inherent error-handling mechanisms often leak the schema structure piece by piece. Attackers use advanced enumeration and brute-forcing tools to dynamically reconstruct the schema without ever using `__schema`.

## The Core Vulnerability: Field Suggestions (Clairvoyance)
The primary mechanism for bypassing disabled introspection relies on **Field Suggestions**. 

When a developer makes a typo in a GraphQL query, the engine attempts to be helpful by suggesting the correct field name using a string similarity algorithm (usually Levenshtein distance). 

**Attacker Request (Guessing):**
```graphql
query {
  user {
    emailAddress
  }
}
```

**Server Response (The Leak):**
```json
{
  "errors": [
    {
      "message": "Cannot query field \"emailAddress\" on type \"User\". Did you mean \"email\"?"
    }
  ]
}
```

By intentionally sending malformed queries containing dictionary words, an attacker can force the server to reveal the actual, valid fields and types. This technique is known as **Clairvoyance**.

## Tools of the Trade

### 1. Clairvoyance (Schema Reconstruction)
`Clairvoyance` (often implemented as a standalone Python script or integrated into frameworks) automates the process of brute-forcing field suggestions to reconstruct a disabled schema.

**How it works:**
1. It queries a common entry point (like `query { __typename }`) to establish a base type.
2. It sends a massive wordlist of common developer terms (e.g., `id`, `name`, `admin`, `password`, `secret`, `token`) against that type.
3. It parses the "Did you mean X?" error messages.
4. It extracts the leaked field names and types, and then recursively repeats the process on the newly discovered types.
5. It compiles the findings and outputs a valid `schema.json` file, effectively bypassing the introspection restriction.

### 2. GraphQL-Cop
`graphql-cop` is a lightweight security auditing tool specific to GraphQL. It performs rapid, automated checks for common misconfigurations without needing a full schema dump.

**What it checks:**
- Introspection enabled?
- GraphiQL or Apollo Studio exposed?
- Are Alias-based Rate Limit bypasses possible? (See [[30.07 GraphQL Alias-Based Rate Limit Bypass]])
- Are GET-based queries allowed? (Bypassing CSRF protections)
- Information leakage via errors?

### 3. InQL (Burp Suite Extension)
InQL is the premier tool for GraphQL analysis within Burp Suite. While it shines when introspection is enabled, its Scanner feature is excellent for automatically detecting endpoints and managing complex GraphQL payloads, making manual enumeration significantly easier.

## Visualizing the Clairvoyance Attack

```text
========================================================================================
                          SCHEMA RECONSTRUCTION VIA ERRORS
========================================================================================

  [ Attacker (Wordlist: "adm", "usr", "pass") ]
       |
       |  POST /graphql {"query": "query { adm }"}
       |--------------------------------------------> [ GraphQL Server ]
       |                                                    | (Checks Schema)
       |  HTTP 200 OK                                       | (Fails, calculates Levenshtein)
       |<-------------------------------------------- { "errors": ["Did you mean 'admin'?"] }
       |
  [ Discovers Field: 'admin' ]
       |
       |  POST /graphql {"query": "query { admin { pass } }"}
       |--------------------------------------------> [ GraphQL Server ]
       |                                                    | 
       |<-------------------------------------------- { "errors": ["Did you mean 'password'?"] }
       |
  [ Discovers Field: 'password' ]
       |
  [ RECONSTRUCTED SCHEMA PARTIAL ]
    type Query {
      admin: AdminType
    }
    type AdminType {
      password: String
    }

========================================================================================
```

## Manual Enumeration Tactics

If automated tools fail or are blocked by a WAF, you must enumerate manually.

1. **Fingerprinting the Engine:** Different GraphQL engines return different default error formats. Apollo Server errors look slightly different from Hasura or Graphene. Identifying the engine helps you tailor your wordlists.
2. **Abusing `__typename`:** Even with introspection disabled, the `__typename` meta-field is almost always accessible. You can inject it into any object you discover to immediately reveal the underlying Backend Type name, which helps inform your dictionary attacks.
   ```graphql
   query {
     user(id: 1) {
       __typename
       name
     }
   }
   ```
   *Response:* `"user": { "__typename": "Administrator", "name": "Alice" }` -> You now know to brute-force fields common to an "Administrator" type.
3. **Analyzing Frontend Traffic:** The most reliable way to enumerate a GraphQL API is to simply use the web application with Burp Suite open. Because GraphQL clients often use Fragments and heavily nested queries to fetch data for the UI, intercepting legitimate traffic will reveal massive portions of the schema without ever triggering security alerts.

## Real-World Example
During a red team engagement, the target organization had disabled introspection. Automated scanners reported the API as secure. The attacker used a custom script based on Clairvoyance logic, targeting the `Mutation` root type. By sending a dictionary of common administrative actions (`del`, `upd`, `cre`, `set`), the server responded with: `Cannot query field "del" on type "Mutation". Did you mean "deleteSystemUser"?`

This single error message leaked the existence of a highly privileged mutation. The attacker then brute-forced the arguments for `deleteSystemUser` using the same "Did you mean?" technique, eventually constructing a valid payload to delete the CEO's account, resulting in critical impact.

## How to Fix It
- **Disable Field Suggestions:** Disabling introspection is not enough. You must also configure the GraphQL engine to suppress "Did you mean X?" suggestions in production environments.
- **Normalize Errors:** Ensure that production error messages are heavily sanitized. The server should return a generic `Internal Server Error` or `Validation Failed` message without echoing back structural details of the schema.
- **Query Allowlisting:** In highly secure environments, implement Persisted Queries (or Query Allowlisting). The backend only accepts pre-approved, hardcoded queries via a hash identifier, completely neutralizing arbitrary query enumeration and injection attacks.

## Chaining Opportunities
- This vuln + [[09 - GraphQL Mutations — Unauthorized Write Operations]] → Enumeration reveals the existence of the mutations; lack of authorization allows you to exploit them.
- This vuln + [[08 - GraphQL IDOR]] → By enumerating hidden ID fields (e.g., finding out that an object has an `internalUuid` alongside its public `id`), you can leverage those hidden fields for Insecure Direct Object Reference attacks.

## Related Notes
- [[03 - Introspection Query — Information Disclosure]]
- [[02 - GraphQL vs REST — Attack Surface Differences]]
