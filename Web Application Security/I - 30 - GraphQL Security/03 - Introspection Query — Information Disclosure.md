---
tags: [vapt, graphql, reconnaissance, information-disclosure]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.03 Introspection Query - Information Disclosure"
---

# 30.03 — Introspection Query: Information Disclosure

## What is it?
GraphQL Introspection is a built-in feature of the GraphQL specification that allows clients to query the GraphQL server for information *about the server's own schema*. 

When Introspection is enabled, an attacker can ask the server: "What queries do you support? What mutations can I perform? What data types exist? What fields do those types have?" The server will faithfully respond with a massive JSON document detailing the entire architecture of the API.

In a development environment, Introspection is fantastic. It powers tools like GraphiQL, Apollo Studio, and Postman, allowing developers to benefit from auto-completion and documentation. However, leaving Introspection enabled in a production environment is a critical misconfiguration. It provides an attacker with a complete, flawless map of your attack surface, entirely eliminating the need for endpoint fuzzing or guesswork.

## The Introspection Payload
The introspection system is accessed via specific meta-fields, primarily `__schema` and `__type`. 

### The Ultimate Introspection Query
To dump the entire schema, an attacker sends the following heavily standardized query to the `/graphql` endpoint. This query requests all types, queries, mutations, subscriptions, fields, arguments, and even the developer's inline documentation (descriptions).

**Attacker Request:**
```graphql
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args {
        ...InputValue
      }
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
```

## How to Exploit It

### Step 1: Detect the GraphQL Endpoint
Common locations for GraphQL endpoints include:
- `/graphql`
- `/api/graphql`
- `/v1/graphql`
- `/v2/graphql`
- `/graphql/console`

### Step 2: Fire the Introspection Query
Send an HTTP POST request to the endpoint with the `IntrospectionQuery` payload. 

If the server replies with a massive JSON object starting with `{"data":{"__schema":{ ...`, Introspection is enabled. You now have the keys to the kingdom.

### Step 3: Visualize the Schema
Reading a 10,000-line JSON response manually is inefficient. Attackers use visualization tools to parse the introspection response and render an interactive map of the API.

**Popular Tools for Visualization:**
1. **GraphQL Voyager:** Paste the JSON response into GraphQL Voyager, and it generates a beautiful, interactive, node-based graph of all types and relationships.
2. **InQL (Burp Suite Extension):** The InQL extension automatically intercepts introspection responses, parses them, and generates templates for every single query and mutation the server supports, feeding them directly into Burp Repeater.
3. **Altair / GraphiQL:** Desktop clients that take the GraphQL endpoint URL, automatically perform the introspection query in the background, and provide a full IDE with auto-complete.

## Visualizing Introspection

```text
========================================================================================
                          THE INTROSPECTION PROCESS
========================================================================================

  [ Attacker ]
       |
       |  POST /graphql 
       |  {"query": "query { __schema { types { name fields { name } } } }"}
       |----------------------------------------------------------> [ GraphQL Server ]
                                                                           |
                                                                  (Engine parses request)
                                                                  (Recognizes __schema)
                                                                  (Extracts metadata)
       |  HTTP 200 OK
       |  {"data": {"__schema": {"types": [
       |     {"name": "User", "fields": [{"name": "passwordHash"}]},
       |     {"name": "Mutation", "fields": [{"name": "deleteDatabase"}]}
       |  ]}}}
       |<----------------------------------------------------------
       |
  [ Loads JSON into GraphQL Voyager ]
       |
  [ Automatically Discovers: ]
    - deleteDatabase(token: String!)
    - User.passwordHash
    - InternalAdminPanelType
    - createSuperUser()

========================================================================================
```

## What Attackers Look For
Once the schema is dumped and visualized, attackers hunt for specific misconfigurations and hidden features:

1. **Hidden Mutations:** Developers often create mutations for internal administrative use (e.g., `deleteUser`, `makeAdmin`, `resetSystem`) and simply don't build UI buttons for them, assuming they are hidden. Introspection reveals them instantly.
2. **Sensitive Fields on Public Types:** A `User` type might have an `ssn` or `passwordHash` field. If RBAC isn't enforced at the resolver level, an attacker can simply query `query { users { ssn } }`.
3. **Deprecated Fields:** Developers use the `@deprecated` directive to phase out old fields. These fields often contain legacy, vulnerable code that lacks modern security controls. Introspection specifically allows querying for deprecated fields (`includeDeprecated: true`).
4. **Development/Debug Queries:** Queries named `testQuery`, `dumpDb`, or `debugInfo` are frequently left in production schemas by accident.

## Real-World Example
In a famous bug bounty report against a major ride-sharing application, a researcher discovered a GraphQL endpoint at `api.company.com/graphql`. Introspection was enabled. 

By analyzing the schema, the researcher found a mutation called `updateDriverPayoutMethod(driverId: ID!, bankAccountNumber: String!)`. This mutation was never documented in the public API, nor was it used by the rider app. It was an internal mutation meant only for support staff. Because the developers assumed no one outside the support team knew the mutation existed, they didn't implement strict authorization checks on it. The researcher was able to use the mutation to change the bank account details of any driver in the system, resulting in a critical payout.

## How to Fix It
- **Disable Introspection in Production:** The vast majority of GraphQL frameworks (Apollo, Graphene, Absinthe) have a simple configuration flag to disable introspection. This should be unconditionally disabled in production environments.
  ```javascript
  // Apollo Server Example
  const server = new ApolloServer({
    typeDefs,
    resolvers,
    introspection: false, // Explicitly disable
    playground: false,    // Disable the interactive IDE
  });
  ```
- **Filter Schema based on Role:** If introspection *must* be enabled (e.g., for a public API), use a custom introspection plugin that filters the schema based on the user's authentication role. A guest user should never see the `makeAdmin` mutation in their introspection response.

## Chaining Opportunities
- This vuln + [[09 - GraphQL Mutations — Unauthorized Write Operations]] → Finding the hidden administrative mutation via introspection is step one. Exploiting the lack of authorization on that mutation is step two.
- This vuln + [[11 - GraphQL Depth and Complexity DoS]] → Once you map the schema, you can find cyclical relationships (e.g., `User` -> `Posts` -> `Author` -> `Posts`) and exploit them to launch a deeply nested DoS attack.

## Related Notes
- [[04 - GraphQL Enumeration (clairvoyance, graphql-cop)]]
- [[02 - GraphQL vs REST — Attack Surface Differences]]
