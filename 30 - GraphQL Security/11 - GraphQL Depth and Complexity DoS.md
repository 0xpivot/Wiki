---
tags: [vapt, graphql, dos, complexity, performance]
difficulty: advanced
module: "30 - GraphQL Security"
topic: "30.11 GraphQL Depth and Complexity DoS"
---

# 30.11 — GraphQL Depth and Complexity DoS

## What is it?
In a REST API, Application-Layer Denial of Service (DoS) attacks usually involve finding an extremely slow, unindexed database query (like a complex search) and hitting that endpoint repeatedly with multiple HTTP requests until the server crashes.

GraphQL changes the game. Because the *client* dictates the shape and size of the response, an attacker doesn't need to send thousands of requests. A single, perfectly crafted GraphQL query can force the server to execute millions of database operations, instantly exhausting CPU, memory, and database connection pools.

This vulnerability exists because of two fundamental GraphQL features:
1. **The Graph Structure (Cyclical Relationships):** Objects often reference each other in loops.
2. **Execution Strategy:** By default, GraphQL resolves fields recursively.

If the developer fails to implement robust Depth Limiting or Query Cost Analysis, the API is critically vulnerable to single-request DoS attacks.

## Attack Vectors

### 1. Cyclical Query (Depth DoS)
The most common attack relies on cyclical relationships within the schema. 
Imagine a schema where a `User` has an array of `Posts`, and a `Post` has an `Author` (which is a `User`). This creates a circular reference: `User -> Post -> User -> Post`.

**Attacker Request (The payload):**
```graphql
query {
  user(id: 1) {
    name
    posts {
      title
      author {
        name
        posts {
          title
          author {
            name
            posts {
              title
              # ... repeat 1,000 times ...
            }
          }
        }
      }
    }
  }
}
```

**The Impact:** 
The GraphQL engine will attempt to resolve this query. If each user has 10 posts, the first level resolves 1 user. The second level resolves 10 posts. The third level resolves 10 authors. The fourth level resolves 100 posts (10 posts for each of the 10 authors). The fifth level resolves 100 authors. The data grows exponentially ($10^N$). 
By nesting the query 20 levels deep, the server must perform quintillions of database lookups or allocate petabytes of RAM to construct the JSON response. The server process (e.g., Node.js V8 engine) will immediately run out of memory and crash (`OOM Error`), taking down the entire API for all users.

### 2. Alias DoS (Width Expansion)
If the server implements Depth Limiting (e.g., "Queries cannot exceed 5 levels of nesting"), attackers pivot to expanding the *width* of the query using Aliases (See [[30.07 GraphQL Alias-Based Rate Limit Bypass]]).

**Attacker Request:**
```graphql
query {
  q1: complexSearch(term: "A") { results }
  q2: complexSearch(term: "B") { results }
  q3: complexSearch(term: "C") { results }
  # ... repeat 10,000 times ...
  q10000: complexSearch(term: "Z") { results }
}
```

**The Impact:**
The depth is only 2 levels, bypassing the Depth Limiter. However, the server must execute the `complexSearch` resolver 10,000 times concurrently. If the search takes 100ms to execute, 10,000 searches will lock the server CPU for 1,000 seconds, causing all subsequent legitimate requests to timeout.

### 3. Array Amplification (Pagination DoS)
If an endpoint allows fetching a list of items and allows the client to specify the limits (`first`, `limit`), attackers can request massive arrays of complex objects.

**Attacker Request:**
```graphql
query {
  getUsers(first: 999999999) {
    id
    profilePicture(size: "LARGE") # Causes heavy image processing
  }
}
```

## Visualizing Cyclical DoS

```text
========================================================================================
                          THE EXPONENTIAL EXPLOSION
========================================================================================

  [ Query ]
  user {               (1 User)
    posts {            (10 Posts)
      author {         (10 Users)
        posts {        (100 Posts)
          author {     (100 Users)
            posts {    (1,000 Posts)
              author { (1,000 Users)
                ...    (Continues Exponentially)
              }
            }
          }
        }
      }
    }
  }

  * Database connection pool exhausts.
  * Node.js event loop blocks.
  * Memory allocation hits V8 limit (~1.5GB).
  * API crashes with 502 Bad Gateway.

========================================================================================
```

## How to Test for Complexity DoS
1. **Analyze the Schema:** Look for circular references (e.g., `Thread -> Message -> Thread`, `User -> Follower -> User`).
2. **Test Depth Limits:** Construct a query nested 15-20 levels deep. Send it. If the server takes a long time to respond or returns a 500/502 error instead of a validation error (like `"Max query depth exceeded"`), it is vulnerable. *Warning: Do this cautiously in production environments, as it will cause a real DoS.*
3. **Test Width Limits:** Pick a moderately heavy query. Use a script to alias it 1,000 times in a single request. Monitor the response time.
4. **Test Pagination:** Find queries that return lists. Set the `limit` argument to `2147483647` (Max Int) and observe the server's behavior.

## Real-World Example
A Bug Bounty hunter noticed that an e-commerce API allowed querying a `Category` object, which contained an array of `Product` objects, which in turn contained an array of `Category` objects representing "Related Categories."

The hunter sent a single query alternating between `Category -> Product -> Category -> Product` nested 30 levels deep. The API Gateway (AWS API Gateway) immediately returned a `504 Gateway Timeout`. The hunter checked the application status page and saw that the backend ECS containers had instantly flatlined due to Out Of Memory exceptions, causing a 5-minute outage while the auto-scaler spun up new containers. The report was triaged as Critical.

## How to Fix It
Fixing this requires multiple layers of defense, as one mitigation alone is insufficient:

1. **Maximum Query Depth:** Configure the GraphQL engine to reject queries exceeding a certain depth (e.g., maximum 7 levels). This stops cyclical attacks.
2. **Maximum Query Cost (Complexity Analysis):** Assign a "cost" to every field. `user.id` might cost 1 point. `user.avatar` might cost 5 points. `complexSearch` costs 50 points. Configure the server to reject any query with a total cost exceeding 1,000 points. This stops Alias DoS and Width Expansion attacks.
3. **Pagination Limits:** Hardcode maximum limits in the resolvers. If a user requests `first: 10000`, the resolver should override it to `first: 100` or return an error.

## Chaining Opportunities
- This vuln + [[07 - GraphQL Alias-Based Rate Limit Bypass]] → Aliasing is the primary mechanism to bypass Depth Limits and achieve DoS via Width Expansion.
- This vuln + [[03 - Introspection Query — Information Disclosure]] → Introspection is heavily utilized by attackers to programmatically identify circular references in the schema to build the DoS payloads.

## Related Notes
- [[07 - GraphQL Alias-Based Rate Limit Bypass]]
- [[01 - What is GraphQL?]]
