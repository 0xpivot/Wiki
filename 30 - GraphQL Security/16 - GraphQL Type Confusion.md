---
tags: [vapt, graphql, type-confusion, scalars, logic-flaw]
difficulty: advanced
module: "30 - GraphQL Security"
topic: "30.16 GraphQL Type Confusion"
---

# 30.16 — GraphQL Type Confusion

## What is it?
One of GraphQL's greatest strengths is its strict, statically-typed schema. If a field expects an `Int` and an attacker sends a `"String"`, the GraphQL engine rejects the payload before it ever reaches the application logic. 

However, **Type Confusion** vulnerabilities arise when attackers exploit edge cases in how the GraphQL execution engine handles arrays, null values, or weakly typed Custom Scalars (like `JSON` or `Object`). By supplying an unexpected data structure that technically bypasses the GraphQL engine's type validator but breaks the underlying backend resolver (e.g., Node.js/Express or PHP), attackers can cause logic flaws, bypass authentication, or crash the server.

## Attack Vectors

### 1. The Array/Object Confusion (NoSQL Injection)
In JavaScript backends (especially those using MongoDB/Mongoose), backend logic often expects a `String` but will technically accept an `Array` or an `Object` if the GraphQL typing isn't perfectly strict.

If the developer uses a generic `JSON` scalar to allow flexible inputs, the GraphQL engine won't enforce a specific type.

**Vulnerable Resolver:**
```javascript
// Expects 'password' to be a String.
const user = await db.users.findOne({ email: args.email, password: args.password });
```

**The Attack:**
Because the argument uses a custom `JSON` scalar (or lacks strict typing), the attacker supplies a MongoDB query operator object instead of a string password.
**Attacker Request Variables:**
```json
{
  "email": "admin@target.com",
  "password": {"$ne": "impossible_string"}
}
```
The MongoDB driver evaluates `password != "impossible_string"`, which is true for the admin account, resulting in a complete authentication bypass.

### 2. Null Injection (Bypassing Required Fields)
The GraphQL schema uses the `!` modifier to indicate a field is required (e.g., `email: String!`). 
However, attackers can sometimes bypass this by manipulating how Variables are passed versus how inline arguments are parsed.

If a developer implements conditional logic based on the *presence* of an argument rather than its value, an attacker might pass `null` or an empty array `[]` to trigger unexpected code paths, especially if the schema lacked the `!` modifier but the backend assumed the data would always be present.

### 3. Exploiting Weak Custom Scalars
Standard scalars are `Int`, `Float`, `String`, `Boolean`, and `ID`.
Because these are restrictive, developers often define **Custom Scalars** like `Date`, `Email`, `UUID`, or `Upload`. 

If the developer fails to implement robust validation parsing *inside* the Custom Scalar definition, it defaults to acting like a generic string or object, entirely negating GraphQL's built-in type protection.

**Vulnerable Scalar Definition:**
```javascript
const { GraphQLScalarType } = require('graphql');
const EmailScalar = new GraphQLScalarType({
  name: 'Email',
  description: 'Custom email scalar type',
  parseValue(value) {
    return value; // VULNERABLE: No regex validation actually implemented!
  }
});
```
**The Attack:** The schema requires an `Email`, but because the scalar's parser logic is empty, the attacker can pass SQL injection payloads (`"admin' OR 1=1--"`) into the email field.

## Visualizing Type Confusion

```text
========================================================================================
                          GRAPHQL TYPE CONFUSION (NoSQLi)
========================================================================================

  [ Attacker ]
       |
       | Variables: { "filter": { "$ne": null } }
       |-----------------------------------------------------------> [ GraphQL Engine ]
                                                                             |
                                      (Schema accepts 'JSON' scalar)         |
                                      (Type check passes!)                   |
                                                                             v
                                                                   [ Node.js Resolver ]
                                              db.users.find({ role: args.filter })
                                                                             |
                                                                             v
                                                                    [ MongoDB ]
                                                (Returns ALL users where role != null)

========================================================================================
```

## How to Test for Type Confusion
1. **Analyze Input Types:** Look for arguments in the schema that use custom scalars (e.g., `Object`, `JSON`, `Map`, `Mixed`). These are prime targets for NoSQL object injection.
2. **Array Substitution:** If an argument expects a `String`, try passing an Array `["admin"]` or an Object `{"$regex": ".*"}` in the GraphQL Variables JSON. Sometimes, outdated or misconfigured GraphQL engines will pass the array through to the resolver.
3. **Variable Mismatches:** Declare a variable as a less restrictive type in the query header, but pass it to a restrictive field.
   ```graphql
   # Declare $val as String (Allows anything)
   query bypass($val: String) {
     # Pass it to a field expecting an Enum or ID
     secureOperation(target: $val) 
   }
   ```
4. **Fuzz Custom Scalars:** If you see a scalar like `Date` or `Email`, do not assume it is safe. Intentionally pass malformed strings, SQLi payloads, or XSS payloads. If the server returns a database error instead of a GraphQL validation error, the custom scalar is poorly implemented.

## Real-World Example
A pentester was analyzing a GraphQL API backed by MongoDB. They noticed a mutation: `updateProfile(metaData: JSON!)`. 

The `metaData` field was intended for the frontend to store simple key-value UI preferences. Because it was typed as `JSON!`, the GraphQL engine performed no validation on the contents. 

The pentester knew the backend resolver likely performed a MongoDB update: `db.users.update({_id: userId}, {$set: metaData})`.
They supplied the following payload:
```json
{
  "metaData": {
    "role": "ADMIN",
    "$push": { "activeTokens": "attacker_token" }
  }
}
```
Because the custom `JSON` scalar allowed arbitrary object structures, the payload flowed directly into the MongoDB driver, allowing the attacker to utilize MongoDB operators (`$push`) to inject their own session token into the administrator's account structure, achieving Account Takeover.

## How to Fix It
- **Avoid Generic Scalars:** Never use `JSON`, `Object`, or `Mixed` custom scalars for input arguments if the backend merges that data directly into a database query. Always define strict, typed Input Objects (`input ProfilePreferences { theme: String, notifications: Boolean }`).
- **Implement Robust Custom Scalars:** If you create a custom scalar like `Email`, you MUST implement the `parseValue` and `parseLiteral` functions to strictly validate the input using Regex or libraries before returning the value to the resolver.
- **Backend Type Assertion:** Do not rely solely on GraphQL. The backend resolver logic (Node.js/Python) should defensively assert the type of the arguments it receives before passing them to sensitive functions like `exec()` or database drivers.

## Chaining Opportunities
- This vuln + [[30.05 GraphQL Injection]] → Type confusion (especially via custom scalars) is the primary vehicle for smuggling NoSQL injection payloads through the GraphQL engine layer.
- This vuln + [[30.09 GraphQL Mutations — Unauthorized Write Operations]] → Abusing unstructured inputs to perform mass assignment.

## Related Notes
- [[30.05 GraphQL Injection]]
- [[06.20 - NoSQL Injection]]
