---
tags: [vapt, graphql, api, reconnaissance, foundations]
difficulty: beginner
module: "30 - GraphQL Security"
topic: "30.01 What is GraphQL?"
---

# 30.01 — What is GraphQL?

## What is it?
GraphQL is an open-source data query and manipulation language for APIs, as well as a runtime for fulfilling those queries with your existing data. Developed internally by Facebook in 2012 before being publicly released in 2015, GraphQL provides an alternative to traditional REST architectures. 

Unlike REST, which relies on multiple endpoints returning fixed data structures (`/api/users`, `/api/posts`, `/api/comments`), GraphQL exposes a **single endpoint** (usually `/graphql`). Clients send a heavily structured query to this endpoint specifying *exactly* what data they want, and the server responds with a JSON payload mirroring the structure of the request.

This fundamental shift in architecture solves two massive problems that plagued traditional REST APIs in the era of mobile applications:
1. **Over-fetching:** Getting more data than you need. If a mobile app just needs the user's name and profile picture to render a header, a REST API endpoint like `/api/user/123` might return 50 fields (email, address, billing history, preferences). This wastes mobile data and battery life.
2. **Under-fetching (N+1 Problem):** Getting too little data and having to make subsequent requests. To load a blog post and its top 3 comments, a client using REST might have to request `/api/posts/1` (1 request), then extract the comment IDs, then request `/api/comments/45`, `/api/comments/46`, and `/api/comments/47` (3 additional requests). In GraphQL, this is solved in a single query.

While GraphQL is incredibly powerful and efficient for frontend developers, its flexibility fundamentally shifts the burden of security. In REST, security is primarily implemented at the endpoint level (e.g., checking if the user is authorized to hit `GET /api/admin/users`). In GraphQL, because there is only one endpoint, security must be meticulously enforced at the **resolver** and **object/field** level, a paradigm shift that developers frequently fail to implement correctly, resulting in widespread vulnerabilities.

## Core Concepts of GraphQL

To attack GraphQL, you must first deeply understand its internal mechanics.

### 1. The Schema and Strong Typing
GraphQL APIs are strictly typed. The server defines a **Schema** using the GraphQL Schema Definition Language (SDL). The schema is a contract between the client and the server, declaring exactly what data can be queried, what mutations can be executed, and what custom types exist.

```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts: [Post]
}

type Post {
  id: ID!
  title: String!
  body: String!
  author: User!
}
```
*(The `!` denotes a non-nullable field, meaning it will always return a value).*

### 2. Operations: Queries, Mutations, and Subscriptions
GraphQL has three core operation types:

#### **Queries (Read)**
Queries are used to fetch data. They are analogous to `GET` requests in REST. The client asks for exactly what it needs.

**Client Request:**
```graphql
query {
  user(id: "1") {
    name
    posts {
      title
    }
  }
}
```

**Server Response:**
```json
{
  "data": {
    "user": {
      "name": "Alice",
      "posts": [
        { "title": "My First Blog Post" },
        { "title": "GraphQL is Awesome" }
      ]
    }
  }
}
```

#### **Mutations (Write/Update/Delete)**
Mutations are used to modify data on the server. They are analogous to `POST`, `PUT`, `PATCH`, and `DELETE` requests in REST. While they technically look similar to queries, by convention, mutations alter state.

**Client Request:**
```graphql
mutation {
  createPost(title: "Hacking GraphQL", body: "It begins here.", authorId: "1") {
    id
    title
  }
}
```

#### **Subscriptions (Real-time)**
Subscriptions allow clients to listen to real-time messages from the server, typically implemented over WebSockets.

**Client Request:**
```graphql
subscription {
  postAdded {
    id
    title
  }
}
```

### 3. Resolvers
Resolvers are the most critical component from a security perspective. A resolver is a backend function responsible for fetching the data for a specific field in the schema. When a query comes in, the GraphQL execution engine parses the query into an Abstract Syntax Tree (AST) and walks down the tree, invoking the corresponding resolver for each requested field.

If a client requests `user(id: 1) { name, email, posts { title } }`, the engine calls:
1. The resolver for the `user` field (fetching the user from the database).
2. The resolvers for `name` and `email` (extracting them from the user object).
3. The resolver for `posts` (making a secondary database query to fetch posts authored by the user).

**Security Implication:** Because the client controls the query structure, the client controls *which* resolvers are executed and in *what combination*. If access control is not implemented deeply within every sensitive resolver, attackers can traverse the graph to access unauthorized data.

## Architectural Architecture: REST vs GraphQL

```text
========================================================================================
                          TRADITIONAL REST ARCHITECTURE
========================================================================================
 
 [ Client ]
     |
     |--- GET /users/123 -------------------------> [ /users endpoint handler ]
     |<-- {id: 123, name: "Alice"} ----------------      | (Checks Auth for /users)
     |                                                   | (Queries DB for User)
     |--- GET /users/123/posts -------------------> [ /posts endpoint handler ]
     |<-- [{id: 1, title: "..."}] -----------------      | (Checks Auth for /posts)
     |                                                   | (Queries DB for Posts)
     |
     | (Multiple Round Trips)
     | (Security is Endpoint-Based)

========================================================================================
                            GRAPHQL ARCHITECTURE
========================================================================================

 [ Client ]
     |
     |--- POST /graphql --------------------------> [ GraphQL Execution Engine ]
     |    {                                                  |
     |      user(id: 123) {                                  |--> Resolver: user(123)
     |        name                                           |      (Must check Auth!)
     |        posts { title }                                |
     |      }                                                |--> Resolver: posts
     |    }                                                  |      (Must check Auth!)
     |                                                       |
     |<-- { data: { user: { name: "...", posts: [] } } } <---/
     |
     | (Single Round Trip)
     | (Security must be Object/Field-Based)

========================================================================================
```

## Security Implications of GraphQL

GraphQL fundamentally alters the attack surface of an API:

1. **Single Endpoint, Massive Attack Surface:** In REST, finding a vulnerable endpoint requires brute-forcing or crawling directories (`/api/v1/hidden_admin_panel`). In GraphQL, the entire API exists at `/graphql`. The attack surface isn't discovered by finding hidden URLs; it's discovered by querying the schema structure (Introspection).
2. **Client-Directed Execution:** The client dictates the shape and depth of the query. A malicious client can construct a query that is syntactically valid but computationally devastating, leading to Denial of Service (DoS).
3. **Complex Authorization:** In REST, if you aren't an admin, the `GET /api/admin/users` endpoint rejects you immediately. In GraphQL, a regular user might legitimately query `user(id: 123)`. But what if they query `user(id: 123) { isAdmin, passwordHash }`? The backend must ensure that the user has permission not just to view the `user` object, but specifically to view the `passwordHash` field. This granular level of authorization is notoriously difficult to implement correctly.
4. **Information Disclosure by Design:** GraphQL was built to be developer-friendly. Features like **Introspection** (where the API tells you its entire schema) and **Detailed Error Messages** (which leak database structure and stack traces) are often left enabled in production, providing attackers with a perfect roadmap.

## Real-World Example
Consider a blogging platform that transitions from REST to GraphQL. In their old REST API, they had an endpoint `/api/authors/{id}` that returned public author profiles. 

When they switched to GraphQL, they created an `Author` type:
```graphql
type Author {
  id: ID!
  name: String!
  bio: String
  internalNotes: String # Intended only for admins
}
```

Because the frontend application never requests the `internalNotes` field, the developers assumed it was hidden. However, an attacker using Burp Suite discovers the GraphQL endpoint, manually crafts a query including `internalNotes`, and immediately gains access to confidential administrative comments about every author, because the resolver for `internalNotes` lacked explicit role-based access controls (RBAC).

## Chaining Opportunities
- This vuln + [[04 - GraphQL Enumeration (clairvoyance, graphql-cop)]] → Understanding the fundamental structure of GraphQL is required before you can effectively map out a target's schema and discover hidden mutations.
- This vuln + [[14 - GraphQL Authorization Bypass]] → The core concept of object-level resolvers is the foundation for understanding why authorization bypasses are so prevalent in GraphQL.

## Related Notes
- [[02 - GraphQL vs REST — Attack Surface Differences]]
- [[03 - Introspection Query — Information Disclosure]]
- [[02.24 - GraphQL How It Differs from REST]]
