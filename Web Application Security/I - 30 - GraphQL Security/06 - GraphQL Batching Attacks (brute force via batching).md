---
tags: [vapt, graphql, rate-limiting, brute-force, batching]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.06 GraphQL Batching Attacks"
---

# 30.06 — GraphQL Batching Attacks

## What is it?
One of the most powerful performance optimization features of GraphQL is **Query Batching**. In a traditional REST API, if a client needs to fetch data from 10 different endpoints, it must make 10 separate HTTP requests. This incurs significant network overhead.

GraphQL solves this by allowing the client to send an *array* of queries in a single HTTP request. The GraphQL server processes all the queries in the array, bundles the results, and returns them in a single JSON array response.

While fantastic for network latency, Query Batching creates a catastrophic bypass for traditional rate-limiting and Web Application Firewalls (WAFs). If an API limits users to 100 HTTP requests per minute to prevent password brute-forcing, an attacker can simply send 1 HTTP request containing an array of 10,000 login mutations. The WAF sees a single HTTP request and allows it. The GraphQL server processes all 10,000 logins instantly.

## The Batching Payload

A standard, single GraphQL request looks like a JSON object:
```json
{
  "query": "query { user(id: 1) { name } }"
}
```

A **Batched** GraphQL request is simply a JSON array containing multiple query objects:
```json
[
  { "query": "query { user(id: 1) { name } }" },
  { "query": "query { user(id: 2) { name } }" },
  { "query": "query { user(id: 3) { name } }" }
]
```
The server will respond with:
```json
[
  { "data": { "user": { "name": "Alice" } } },
  { "data": { "user": { "name": "Bob" } } },
  { "data": { "user": { "name": "Charlie" } } }
]
```

## How to Exploit It

### Scenario 1: OTP / 2FA Brute Forcing
Imagine an application that sends a 4-digit OTP (0000-9999) to a user's phone. In REST, brute-forcing 10,000 combinations would require 10,000 HTTP requests, which would undoubtedly trigger an IP ban or rate limit.

In GraphQL, you generate a single payload array with 10,000 mutation objects, each testing a different OTP.

**Attacker Request:**
```json
[
  { "query": "mutation { verifyOTP(code: \"0000\") { token } }" },
  { "query": "mutation { verifyOTP(code: \"0001\") { token } }" },
  { "query": "mutation { verifyOTP(code: \"0002\") { token } }" },
  ...
  { "query": "mutation { verifyOTP(code: \"9999\") { token } }" }
]
```
You send exactly **one** HTTP POST request. The server executes all 10,000 mutations. You then search the massive response array for the one object that returns a valid `token` instead of an error. The 2FA is bypassed instantly.

### Scenario 2: Password Spraying / Credential Stuffing
Attackers can use batching to test a list of 1,000 common passwords against a single admin account, or test one common password (`Password123!`) against 1,000 different usernames, all within a single HTTP request, completely bypassing Cloudflare, AWS WAF, or Nginx rate limiting.

### Scenario 3: Object Enumeration (IDOR Discovery)
Instead of relying on multi-threaded tools like Intruder or Ffuf to scan for valid user IDs (e.g., `user(id: 1)` to `user(id: 500)`), you can batch 500 queries together. This allows you to scrape entire databases in seconds without generating noisy network traffic.

## Visualizing the Batching Bypass

```text
========================================================================================
                          TRADITIONAL RATE LIMITING vs BATCHING
========================================================================================

 [ REST API: Blocked by WAF ]
 
  Req 1: POST /login {user, pass1} ----> [ WAF ] ----> [ Server ]
  Req 2: POST /login {user, pass2} ----> [ WAF ] ----> [ Server ]
  Req 3: POST /login {user, pass3} ----> [ WAF ] ----> [ Server ]
  ...
  Req 6: POST /login {user, pass6} ----> [ WAF (Rate Limit Hit! 429 Too Many Requests) ] --X

----------------------------------------------------------------------------------------

 [ GRAPHQL API: Bypassed via Batching ]

  Req 1: POST /graphql 
         [
           {query: mutation login(pass1)},
           {query: mutation login(pass2)},
           ...
           {query: mutation login(pass1000)}
         ] 
                 |
                 v
              [ WAF ] (Inspects HTTP Layer. Sees 1 Request. Allows.)
                 |
                 v
         [ GraphQL Engine ] (Iterates over array, executes 1000 logins internally)
                 |
                 v
   <------- [ 999 Errors, 1 Success Token ]

========================================================================================
```

## Real-World Example
A major fintech application implemented a strict 5-request-per-minute rate limit on their login endpoint to prevent brute-forcing. A pentester noticed the application used Apollo GraphQL. They intercepted the login request and wrapped the JSON payload in an array (`[ {query...} ]`). The server processed it successfully. 

The pentester then used a python script to generate a JSON array containing 5,000 login mutations, each testing a different password from the rockyou.txt wordlist against an employee's email address. They sent the 10MB JSON payload in a single HTTP request. The WAF allowed it (it was just one request). Ten seconds later, the server responded with an array containing 4,999 errors and 1 valid JWT. The rate limit was utterly useless.

## How to Fix It
- **Disable Batching:** If your application does not explicitly rely on query batching for performance, disable it entirely in the GraphQL engine configuration. If the server receives an array instead of a JSON object, it should return a 400 Bad Request.
- **Limit Batch Size:** If batching is necessary, configure the GraphQL engine to enforce a strict maximum batch size (e.g., max 5 queries per request).
- **Application-Layer Rate Limiting:** Stop relying on API Gateways or WAFs to perform IP-based rate limiting on the HTTP request. Implement rate limiting *inside the resolver logic*. For example, the `login` resolver should check Redis to see how many times that specific username or IP address has attempted to log in, regardless of whether the requests came individually or batched.

## Chaining Opportunities
- This vuln + [[07 - GraphQL Alias-Based Rate Limit Bypass]] → If the developers learn about this and disable JSON array batching, you can instantly pivot to Alias-based batching to achieve the exact same result.
- This vuln + [[16 - Authentication — Brute Forcing]] → Batching is the ultimate enabler for high-speed authentication attacks against modern single-page applications.

## Related Notes
- [[07 - GraphQL Alias-Based Rate Limit Bypass]]
- [[01 - What is GraphQL?]]
