---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.09 Shopify Bug IDOR"
---

# 60.09 Shopify Bug: GraphQL IDOR on Admin Panel

## 1. Introduction

Insecure Direct Object References (IDOR), or Broken Object Level Authorization (BOLA), is a vulnerability that occurs when an application exposes a reference to an internal implementation object (like a database key or filename) and fails to adequately verify if the requesting user has the authority to access or modify that specific object.

In multi-tenant SaaS environments like Shopify, isolating tenant data is the most critical security requirement. A vulnerability that allows Tenant A to modify the resources of Tenant B breaks this isolation entirely. This document analyzes a sophisticated IDOR vulnerability (similar to those disclosed in multi-tenant e-commerce platforms) residing within a modern GraphQL API admin panel, focusing on the mechanics of global node IDs and authorization bypasses.

## 2. Architecture and Data Flow

Modern single-page applications (SPAs) frequently utilize GraphQL to fetch and mutate data efficiently. In a multi-tenant environment, the backend must ensure that every GraphQL resolver strictly validates the context of the requested ID against the authenticated user's tenant scope.

### The Attack Flow Diagram

```text
+------------------+                                 +-------------------------+
|                  |                                 |                         |
| Attacker (Store A| =======(1) GraphQL Mutation====>| Public API Gateway      |
|                  |       ID: Z2lkOi8v... (Store B) | (Authentication Layer)  |
+------------------+                                 +-----------+-------------+
                                                                 |
                                                                 | (2) Validates JWT (Passes)
                                                                 |     Forwards to GraphQL Engine
                                                                 v
+------------------+                                 +-------------------------+
|                  |                                 |                         |
| Shared Database  | <======(4) UPDATE Product=======| Backend Microservice    |
| (Tenant A & B)   |                                 | (Missing Authorization) |
+------------------+                                 +-------------------------+
                                                                 ^
                                                                 | (3) GraphQL Resolver fails
                                                                 |     to verify if the target
                                                                 |     ID belongs to Store A
```

## 3. Vulnerability Mechanics: The GraphQL Context

GraphQL APIs often use a concept called "Global Object Identification." Instead of passing simple integer IDs (like `id: 123`), the client passes an opaque, base64-encoded string representing a Global Node ID.

For example, a Shopify product ID might look like this internally: `gid://shopify/Product/9988776655`.
When sent to the client, it is base64 encoded to: `Z2lkOi8vc2hvcGlmeS9Qcm9kdWN0Lzk5ODg3NzY2NTU=`.

### The Vulnerable Mutation
Suppose an administrator of Store A wants to update the price of their product. Their browser sends the following GraphQL mutation:

```graphql
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product {
      id
      title
      price
    }
  }
}
```
**Variables:**
```json
{
  "input": {
    "id": "Z2lkOi8vc2hvcGlmeS9Qcm9kdWN0Lzk5ODg3NzY2NTU=",
    "price": "10.00"
  }
}
```

### The Flaw
The backend GraphQL resolver receives this mutation. It successfully decodes the ID and identifies the target as Product `9988776655`. It then executes the database update: `UPDATE products SET price = 10.00 WHERE id = 9988776655`.

The critical flaw is the missing authorization check. The code *fails to verify* that `product.store_id == current_user.store_id`. If the attacker replaces the base64 ID with the ID of a product belonging to Store B, the backend processes the update, successfully altering a competitor's product.

### Vulnerable Code Snippet (Conceptual Node.js / Apollo Server)

```javascript
const resolvers = {
  Mutation: {
    productUpdate: async (_, { input }, context) => {
      // FLAW: The user is authenticated (context.user exists),
      // but the code never checks if context.user.storeId owns the input.id
      
      const { id, price } = input;
      const decodedId = Buffer.from(id, 'base64').toString('ascii');
      const dbId = decodedId.split('/').pop();
      
      // Direct execution without authorization check!
      await db.query('UPDATE products SET price = ? WHERE id = ?', [price, dbId]);
      
      return { id: input.id, price: price };
    }
  }
};
```

## 4. The Exploit Step-by-Step

Exploiting IDOR in a complex platform requires identifying the correct object types and mapping out the underlying database schema through observation.

### Step 1: Object Enumeration
The attacker browses a competitor's store (Store B) and views a target product. By inspecting the HTML source or network traffic on the public storefront, they locate a public product ID or handle. If the platform exposes the GraphQL Node ID publicly, the attacker simply copies it.

### Step 2: ID Construction
If only the raw integer ID is exposed (e.g., `12345`), the attacker deduces the format used by the GraphQL API by observing their own store's traffic.
Format: `gid://shopify/Product/12345`
Base64 Encode: `Z2lkOi8vc2hvcGlmeS9Qcm9kdWN0LzEyMzQ1`

### Step 3: Mutation Forgery
The attacker logs into their *own* store's admin panel (Store A). They intercept a legitimate product update request using Burp Suite. They swap the `id` variable in the GraphQL payload with the encoded ID of Store B's product. They change the `price` variable to `0.01`.

### Step 4: Execution
The attacker forwards the modified request. The server returns a `200 OK` with the updated product details. The attacker has successfully changed the price of a competitor's product to one cent.

## 5. Advanced Bypasses: Bypassing Type Checks

Sometimes developers implement partial checks. For example, they might check if an ID belongs to the user, but they fail to check the *Type* of the object in the Global ID.
If the mutation expects a `Product` ID, but the attacker provides an `Order` ID that *does* belong to them (e.g., `gid://shopify/Order/999`), the backend might attempt to parse it. 

If the database query blindly extracts the integer and runs `UPDATE products SET price = 10 WHERE id = 999`, it might inadvertently overwrite Product `999` (belonging to another user) simply because the attacker owned Order `999`. This is a complex logic flaw stemming from insecure polymorphic ID handling.

## 6. Real-World Consequences

In a platform like Shopify, an admin-level IDOR is devastating. An attacker could:
- **Financial Sabotage:** Change competitors' product prices to free.
- **Data Exfiltration:** Read the private customer lists (PII) of other merchants.
- **Defacement:** Alter the theme and template files of other stores.
- **Ransomware:** Delete all products from a target store and demand payment for restoration.

## 7. Secure Coding and Remediation

Fixing IDOR requires a systemic shift from checking IDs to enforcing authorization context.

### 1. The Contextual Database Query
The most robust defense is to modify the data access layer (the SQL queries or ORM calls) to inherently include the ownership context. The ID alone is never enough to retrieve or modify an object.

**Secure Code Snippet (Node.js)**
```javascript
const resolvers = {
  Mutation: {
    productUpdate: async (_, { input }, context) => {
      // Secure implementation
      const { id, price } = input;
      const decodedId = Buffer.from(id, 'base64').toString('ascii');
      const dbId = decodedId.split('/').pop();
      const userStoreId = context.user.storeId; // Derived from trusted JWT
      
      // The query inherently enforces authorization!
      const result = await db.query(
        'UPDATE products SET price = ? WHERE id = ? AND store_id = ?', 
        [price, dbId, userStoreId]
      );
      
      if (result.affectedRows === 0) {
        throw new Error("Product not found or unauthorized");
      }
      return { id: input.id, price: price };
    }
  }
};
```

### 2. Centralized Authorization Middleware
Use specialized authorization libraries (like Pundit in Ruby, or CASL in JavaScript) to define policies for every object type. Before a GraphQL resolver executes its core logic, the middleware evaluates the policy: `can(context.user, 'update', Product, dbId)`. If the policy returns false, the action is blocked.

## 8. Chaining Opportunities

- **IDOR + Mass Assignment:** Once an IDOR is found, an attacker can attempt Mass Assignment by injecting undocumented JSON keys (e.g., `"is_admin": true`) into the mutation payload to see if the vulnerable resolver inadvertently saves them.
- **IDOR + SSRF:** Finding an IDOR in a "Webhook Configuration" endpoint. The attacker modifies another user's webhook to point to `http://169.254.169.254`, triggering an SSRF that executes within the victim's tenant context.

## 9. Related Notes

- [[01 - API1 — Broken Object Level Authorization (BOLA)]]
- [[09 - GraphQL Security Deep Dive]]
- [[14 - Advanced API Parameter Tampering]]
- [[06 - HackerOne Disclosed Reports Top 10]]
