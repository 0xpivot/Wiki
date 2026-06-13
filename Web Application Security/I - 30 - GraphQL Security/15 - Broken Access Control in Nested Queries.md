---
tags: [vapt, graphql, bac, nested-queries, authorization]
difficulty: advanced
module: "30 - GraphQL Security"
topic: "30.15 Broken Access Control in Nested Queries"
---

# 30.15 — Broken Access Control in Nested Queries

## What is it?
In GraphQL, data is retrieved as a graph. A single query can traverse across multiple distinct domain objects (e.g., `Organization` -> `User` -> `BillingDetails`). 

**Broken Access Control in Nested Queries** is a specific, highly prevalent form of IDOR/Authorization Bypass that occurs because developers often apply strong security checks to the *Root Query* (the top level of the request) but completely neglect to secure the *Nested Field Resolvers* (the subsequent nodes in the graph).

Developers mistakenly assume that if a user passed the security check at the front door (the Root Query), they are authorized to wander anywhere inside the house (the nested fields). In GraphQL, this assumption is fatally flawed.

## The Root vs. Nested Security Flaw

### The Flawed Assumption
Imagine a schema where a `Company` object contains an array of `Employee` objects.

**The Developer's Logic:**
1. Secure the `getCompany(id)` root query. Ensure the user belongs to the company.
2. If the user passes, return the `Company` object.
3. The GraphQL engine then automatically resolves the `employees` field on that company.

**Secure Root Query:**
```graphql
query {
  getCompany(id: "MY_COMPANY_123") { # Secure: Backend verifies I am an employee
    name
    employees {                      # Secure: I am allowed to see my coworkers
      name
      salary                         # VULNERABLE: No field-level check!
    }
  }
}
```

### The Attack (The "Side Door")
The attacker doesn't need to break the `getCompany` logic. They just need to find *another* path in the graph that leads to the `Employee` object—a path the developer didn't anticipate.

Suppose there is a public root query called `getPublicPost(id)`. A post has an `author` field, which resolves to an `Employee`.

**Attacker Request:**
```graphql
query {
  getPublicPost(id: "999") { # Secure: It's a public blog post. Anyone can read it.
    title
    author {                 # Resolves to the Employee object
      name
      salary                 # EXPLOIT: The attacker accessed a private field!
    }
  }
}
```

The developer secured the `Company -> employees -> salary` path, but forgot that the GraphQL engine allows the attacker to traverse `PublicPost -> author -> salary`. Because the `salary` resolver itself lacked an explicit authorization check, the attacker dumped the payroll data.

## Visualizing Graph Traversal Bypasses

```text
========================================================================================
                          THE GRAPH TRAVERSAL BYPASS
========================================================================================

 [ Intended Secure Path ] (Blocked)
 
   query getCompany(id: "RIVAL_COMPANY") ----> [ Root Resolver: DENIED 403 ]
      |
      +--> employees
             |
             +--> salary (Never reached)


 [ Attacker Alternate Path ] (Success)

   query getPublicPost(id: "1") ----> [ Root Resolver: ALLOWED 200 ]
      |
      +--> author (Returns Employee object)
             |
             +--> salary ----> [ Nested Resolver: NO AUTH CHECK ] ----> Returns $150,000

========================================================================================
```

## How to Test for Nested Access Control Flaws
1. **Map the Graph:** Use tools like GraphQL Voyager to visualize the schema. Look for sensitive object types (e.g., `User`, `Billing`, `AdminData`).
2. **Find Alternate Entry Points:** Identify every possible path to reach the sensitive object. Can you reach a `User` via `getCompany`? Can you reach it via `getPost`? Can you reach it via `searchComments`?
3. **Test Field Defenses:** Craft queries that traverse the alternate, less-secure paths. Request sensitive fields (`passwordHash`, `ssn`, `internalNotes`) on the destination object.
4. **Deep Nesting:** Try traversing deeply. `query { myProfile { friends { friends { privateEmail } } } }`. If the `privateEmail` resolver assumes that the parent object was always `myProfile`, the deep nesting will bypass the logic.

## Real-World Example
During a penetration test of a healthcare application, the API had strict controls preventing patients from querying other patients' data. `query { patient(id: 2) { medicalRecords } }` failed securely.

However, the application had a messaging system. A patient could query their own messages.
The pentester crafted this query:
```graphql
query {
  myMessages {
    thread {
      participants { # Array of Patient objects
        id
        medicalRecords { # VULNERABLE NESTED RESOLVER
          diagnosis
          prescriptions
        }
      }
    }
  }
}
```
By looking at a group message thread, the pentester was able to traverse the graph to the `participants` node, which returned `Patient` objects. Because the `medicalRecords` field resolver lacked its own context check, the pentester extracted the highly confidential health data of every user in the chat thread.

## How to Fix It
- **Field-Level Authorization (The Golden Rule):** You must never rely on path-based security in GraphQL. Authorization MUST be enforced at the resolver level for the specific field being accessed, regardless of how the user arrived at that field.
  ```javascript
  // Secure Nested Resolver
  const EmployeeResolvers = {
    salary: (employee, args, context) => {
      // It doesn't matter if we got here via Company or Post.
      // Can the current user view this specific employee's salary?
      if (context.user.id !== employee.id && context.user.role !== 'HR') {
        throw new Error("Unauthorized");
      }
      return employee.salary;
    }
  }
  ```
- **Data Loaders and Centralized Services:** Push the authorization logic down into the data-fetching layer. If the resolver calls `UserService.getSalary(employeeId)`, the `UserService` should check permissions before querying the database, ensuring security is universal across all GraphQL entry points.

## Chaining Opportunities
- This vuln + [[30.08 GraphQL IDOR]] → This is essentially the mechanism that makes GraphQL IDORs so complex and devastating.
- This vuln + [[30.11 GraphQL Depth and Complexity DoS]] → Attackers often use nested query structures to perform DoS attacks while simultaneously hunting for access control flaws.

## Related Notes
- [[30.08 GraphQL IDOR]]
- [[30.14 GraphQL Authorization Bypass]]
