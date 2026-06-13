---
tags: [vapt, graphql, reconnaissance, discovery, fuzzing]
difficulty: beginner
module: "30 - GraphQL Security"
topic: "30.17 GraphQL Endpoint Discovery"
---

# 30.17 — GraphQL Endpoint Discovery

## What is it?
Before you can enumerate a schema, test for IDORs, or attempt an Introspection query, you must first find the GraphQL endpoint. 

Unlike REST APIs where discovering endpoints requires extensive directory fuzzing (e.g., `ffuf` against `api.target.com/v1/USER_LIST`), GraphQL discovery is typically a one-shot process. You only need to find the single router URL. Once found, the entire attack surface is unlocked.

However, developers sometimes attempt to secure their APIs via "Security by Obscurity" by hiding the GraphQL endpoint on non-standard ports, complex subdomains, or behind obfuscated paths.

## Discovery Techniques

### 1. Common Path Fuzzing
The vast majority of GraphQL implementations use default paths established by their respective frameworks (Apollo, Express-GraphQL, Hasura). You can use tools like `ffuf` or Burp Intruder to rapidly scan a host.

**Common Endpoints:**
- `/graphql` (The universal standard)
- `/api/graphql`
- `/v1/graphql`
- `/v2/graphql`
- `/graphql/v1`
- `/graphql/console`
- `/graphiql` (The interactive IDE - finding this is a jackpot)
- `/playground` (Apollo Server IDE)
- `/altair`

**Fuzzing Command:**
```bash
ffuf -w graphql-endpoints.txt -u https://api.target.com/FUZZ -X POST -H "Content-Type: application/json" -d '{"query":"{__typename}"}' -mc 200
```
*Note:* Always send a valid but minimal GraphQL payload (`{"query":"{__typename}"}`). If you send a standard GET request, the server might return a `400 Bad Request` or `405 Method Not Allowed`, masking the endpoint's existence.

### 2. JavaScript Source Code Analysis
Modern Single Page Applications (React, Vue, Angular) rely heavily on GraphQL client libraries like **Apollo Client**, **Relay**, or **urql**. 

By analyzing the frontend JavaScript bundle, you can almost always find the exact URL the client is configured to communicate with.
1. Open Chrome DevTools -> Sources -> search across all files (Ctrl+Shift+F).
2. Search for keywords: `graphql`, `ApolloClient`, `createNetworkInterface`, `HttpLink`, `query:`, `mutation:`.
3. Look for the initialization of the client:
   ```javascript
   const client = new ApolloClient({
     link: new HttpLink({ uri: 'https://hidden-api.internal.com/gql-router' }),
     cache: new InMemoryCache()
   });
   ```

### 3. HTTP Header and Error Analysis
Sometimes the endpoint is hidden on a different subdomain entirely (e.g., `data.target.com/query`), but the main application reveals its existence via HTTP Headers.

- **Routing Headers:** Look for headers like `X-GraphQL-Routing`, `X-Apollo-Tracing`, or `X-Powered-By: Express-GraphQL`.
- **Forced Errors:** Send a malformed JSON request to the root API endpoint. If the server is a GraphQL gateway, it might accidentally leak stack traces mentioning `graphql-js` or `graphql-ruby`.

### 4. Detecting GraphQL via Universal Queries
If you suspect an endpoint processes GraphQL but it isn't responding to standard POST requests, try sending the query via GET parameters. The GraphQL specification explicitly supports GET requests for queries (though mutations require POST).

**Testing via GET:**
```http
GET /api/data?query={__typename} HTTP/1.1
Host: target.com
```

If the server responds with `{"data": {"__typename": "Query"}}`, you have successfully located the endpoint.

## Visualizing Discovery

```text
========================================================================================
                          GRAPHQL DISCOVERY WORKFLOW
========================================================================================

  1. Passive Discovery (Browser DevTools)
     |--> Network Tab -> Filter by "graphql" or "query"
     |--> If traffic exists, copy URL. Done.

  2. Static Analysis (JS Bundles)
     |--> Search: "ApolloClient", "uri:"
     |--> Extract hardcoded endpoints.

  3. Active Fuzzing (ffuf)
     |--> POST /graphql, /api/graphql, /v1/graphql
     |--> Payload: {"query":"{__typename}"}
     |--> Look for HTTP 200 with {"data":{"__typename":"Query"}}

  4. Alternative Verbs
     |--> GET /graphql?query={__typename}

========================================================================================
```

## Tools for Automated Discovery
- **InQL (Burp Extension):** Passively monitors all traffic flowing through Burp Suite. If it detects a request that looks like GraphQL (based on JSON structure or headers), it flags the endpoint automatically.
- **Nuclei:** ProjectDiscovery's Nuclei scanner has dozens of templates specifically designed to fingerprint GraphQL endpoints and GraphiQL playgrounds across wide infrastructure scopes.
- **GraphQL-Cop:** While primarily an auditing tool, it begins its execution by attempting to discover the endpoint across common paths.

## Real-World Example
A bug bounty target operated a complex web application. Standard directory brute-forcing against `api.company.com` yielded nothing but `404`s. The frontend seemed to communicate exclusively via WebSockets, making standard HTTP inspection difficult.

The pentester downloaded the main `app.bundle.js` file and ran a regex search for `https://.*graphql`. They discovered a hardcoded string pointing to a completely different, undocumented domain: `https://telemetry-gateway.internal.company.com/v1/gql`.

By sending a `POST` request to that endpoint with `{"query": "query { __schema { types { name } } }" }`, they discovered that introspection was enabled, revealing a massive internal schema used for telemetry and administrative monitoring that was never intended to be exposed to the internet.

## How to Fix It
- **Do not rely on Obscurity:** Hiding the `/graphql` endpoint on a weird path (e.g., `/api/v3/x/query`) provides zero actual security. Attackers will find it via JS analysis or traffic interception.
- **Disable Interactive IDEs in Production:** Ensure that GraphiQL, Apollo Studio, and Altair endpoints (`/graphiql`, `/playground`) are strictly disabled in production builds. They provide an attacker with a convenient GUI for exploitation.
- **Require Authentication for the Endpoint:** Ideally, the `/graphql` endpoint itself should reject unauthenticated requests outright (returning a `401 Unauthorized` before the GraphQL engine even parses the query), unless the API is explicitly designed for public, unauthenticated access.

## Chaining Opportunities
- This vuln + [[03 - Introspection Query — Information Disclosure]] → Finding the endpoint is Step 1. Dumping the schema via Introspection is Step 2.
- This vuln + [[04 - GraphQL Enumeration (clairvoyance, graphql-cop)]] → If the endpoint is found but Introspection is disabled, you pivot immediately into field enumeration.

## Related Notes
- [[03 - Introspection Query — Information Disclosure]]
- [[02.04 - Directory Fuzzing and Brute Forcing]]
