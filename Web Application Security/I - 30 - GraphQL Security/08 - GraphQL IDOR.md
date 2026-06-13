---
tags: [vapt, graphql, idor, bola, authorization]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.08 GraphQL IDOR"
---

# 30.08 — GraphQL IDOR (Insecure Direct Object Reference)

## What is it?
Insecure Direct Object Reference (IDOR), also known as Broken Object Level Authorization (BOLA), is arguably the most common and devastating vulnerability in GraphQL APIs. 

In a REST API, an IDOR looks like changing `GET /api/users/123` to `GET /api/users/456`. In GraphQL, the concept is identical, but the execution and discovery are vastly more complex because the attack surface isn't a flat list of URLs; it's a deeply interconnected graph of objects.

GraphQL introduces several unique patterns that exacerbate IDOR vulnerabilities, primarily because authorization must be manually enforced at the individual resolver level for every single object type, rather than at a top-level route. If a developer forgets an authorization check on a nested resolver, an attacker can traverse the graph to access unauthorized data.

## Attack Vectors for GraphQL IDOR

### 1. Direct Argument IDOR (The Classic)
This is the GraphQL equivalent of the REST IDOR. The attacker simply changes an ID parameter in a top-level query.

**Vulnerable Query:**
```graphql
query {
  getReceipt(orderId: 1001) {
    total
    creditCardLast4
    billingAddress
  }
}
```
**The Attack:** The attacker changes `1001` to `1002`. If the `getReceipt` resolver fetches the order from the database without checking if the currently authenticated user actually owns order `1002`, the IDOR succeeds.

### 2. Nested Relationship IDOR (The Graph Traversal)
This is where GraphQL becomes extremely dangerous. A top-level query might be perfectly secure, but a nested relationship might be vulnerable.

Imagine a secure system where you cannot directly query another user's profile. However, you *can* query your own profile, and your profile object contains a `messages` array, and each message has a `sender` object.

**Vulnerable Query:**
```graphql
query {
  myProfile {          # Secure: correctly returns only YOUR profile
    messages {         # Secure: correctly returns only YOUR messages
      sender {         # VULNERABLE: Returns the full User object of the sender
        email
        privatePhoneNumber
        passwordResetToken
      }
    }
  }
}
```
**The Attack:** The developer secured the `myProfile` resolver, but forgot to restrict what fields can be accessed when a `User` object is resolved via the `sender` relationship. The attacker simply messages an admin, then queries their own messages to extract the admin's private data.

### 3. The Relay Node Interface (Global Object Discovery)
Many GraphQL APIs implement the **Relay Specification**, which mandates a global `node(id: ID!)` query. This query allows the client to fetch *any* object in the entire database if they know its Global ID (usually a base64 encoded string like `VXNlcjoxMjM=` which decodes to `User:123`).

**The Attack:** If the developer implements the `node` query but forgets to apply context-aware authorization checks inside it, an attacker can bypass all custom queries and fetch any object directly.
```graphql
query {
  node(id: "T3JkZXI6Nzc3") { # Base64 for "Order:777"
    ... on Order {
      total
      customerName
    }
  }
}
```
Even if `getOrder(id: 777)` is secure, the global `node` query might bypass those checks!

## Visualizing Nested IDOR

```text
========================================================================================
                          REST vs GRAPHQL (NESTED IDOR)
========================================================================================

 [ REST API Defense ]
  GET /users/me          --> Success
  GET /users/admin       --> 403 Forbidden (Blocked at Route Level)
  GET /messages/1        --> Success
  GET /users/admin/phone --> 403 Forbidden (Blocked at Route Level)

----------------------------------------------------------------------------------------

 [ GRAPHQL Graph Traversal Bypass ]
 
  query {
    myMessages {
      id
      recipient {        --> Resolves to "Admin" User Object
        phoneNumber      --> Exploit! (No field-level auth check)
      }
    }
  }

  * The attacker bypassed the front door (GET /users/admin) 
    by walking through the side door (myMessages -> recipient).

========================================================================================
```

## How to Test for IDOR in GraphQL
1. **Enumerate the Schema:** Map out all queries that accept an `id`, `uuid`, or `hash` as an argument.
2. **Swap IDs:** Standard testing. Create User A and User B. Authenticate as User A, and pass User B's IDs into the queries.
3. **Hunt for Relay Nodes:** Check if the schema supports the `node(id: ID!)` query. If it does, decode your own objects' IDs to understand the format (e.g., Base64 `Type:ID`), then encode the target's ID and query it directly.
4. **Traverse the Graph:** Do not just test top-level queries. Actively look for circular references or deep relationships (e.g., `company -> employees -> user -> paymentMethods`). Try to walk the graph from a public object to a private object.

## Real-World Example
A Bug Bounty hunter was testing a financial dashboard API built on GraphQL. The top-level query `query { getInvoice(id: 45) { amount } }` was completely secure. If you asked for an invoice you didn't own, the server returned an unauthorized error.

However, the hunter noticed a mutation used to add comments to invoices. They created an invoice, added a comment, and noticed the response included the `author` object.
They crafted a new query traversing backward:
```graphql
query {
  getComment(id: 999) { # 999 is a comment made by the victim on their own invoice
    text
    invoice {
      amount
      billingDetails
    }
  }
}
```
The developer secured the `getInvoice` resolver, but failed to secure the `invoice` resolver that belonged to the `Comment` object. By accessing the invoice *through* the comment, the attacker bypassed the IDOR protection entirely and dumped the victim's financial data.

## How to Fix It
- **Context-Aware Resolvers:** Resolvers must never blindly fetch data based solely on the requested ID. They must always evaluate the ID against the currently authenticated user's context (e.g., `SELECT * FROM invoices WHERE id = ? AND owner_id = ?`).
- **Centralized Authorization Logic:** Do not write authorization checks directly inside the resolver functions. Extract authorization logic into a centralized service layer. The resolver should simply call `AuthService.getInvoice(userId, invoiceId)`.
- **Field-Level Authorization Directives:** Use schema directives like `@auth(requires: USER)` or `@owner` to declaratively enforce security rules on specific fields in the SDL, ensuring they cannot be bypassed via graph traversal.

## Chaining Opportunities
- This vuln + [[04 - GraphQL Enumeration (clairvoyance, graphql-cop)]] → You must first discover the hidden fields or deeply nested relationship structures before you can traverse them for IDOR.
- This vuln + [[09 - GraphQL Mutations — Unauthorized Write Operations]] → Finding an IDOR in a query is a data leak. Finding an IDOR in a mutation (e.g., `updateProfile(userId: 2, email: "hacker@evil.com")`) results in full Account Takeover.

## Related Notes
- [[09 - GraphQL Mutations — Unauthorized Write Operations]]
- [[21.01 - What is Access Control]]
- [[21.03 - IDOR Insecure Direct Object Reference]]
