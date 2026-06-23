---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.46 Access-Control-Max-Age — Preflight Caching"
---

# 03.46 — Access-Control-Max-Age

## What is it?

`Access-Control-Max-Age` is an HTTP response header that tells web browsers how long (in seconds) they should remember (cache) the results of a CORS preflight request (the `OPTIONS` request). 

A preflight request is a preliminary check that browsers make before sending certain types of cross-origin requests (like `POST` with JSON payload, or requests with custom headers) to verify if the server permits the action. If `Access-Control-Max-Age` is set, the browser does not need to send another preflight request for the specified duration, reducing latency and network traffic.

### Beginner Explanation
Think of a preflight request like a security guard at the entrance of a building. Before you (the browser) enter with a package (the actual request), the guard checks your ID (preflight `OPTIONS` request). If the guard gives you a pass, you don't want to get checked again every single time you walk in and out of the door. The `Access-Control-Max-Age` header acts like a temporary pass badge that says: "This visitor is pre-approved for the next 10 minutes. Don't check their ID again until this pass expires."

---

## Format

```
Access-Control-Max-Age: <delta-seconds>
```

- `<delta-seconds>`: The maximum number of seconds the results can be cached.
  - `Access-Control-Max-Age: 600` (10 minutes - typical recommended value)
  - `Access-Control-Max-Age: 3600` (1 hour)
  - `Access-Control-Max-Age: 0` (Disabled caching; every request requires preflight)
  - `Access-Control-Max-Age: -1` (Disabled caching; standard-compliant way to force preflight)

**Browser-Specific Maximum Limits:**
Browsers impose their own maximum limits to prevent long-term caching of stale CORS rules:
- **Chrome / Chromium:** 7200 seconds (2 hours)
- **Firefox:** 86400 seconds (24 hours)

---

## Categories
- **Security Concept:** Cross-Origin Resource Sharing (CORS)
- **Header Type:** Response Header
- **Context:** Web Application Security / Client-side Cache Control

---

## Use Cases

1. **Performance Optimization:** Reducing the number of HTTP requests for high-traffic API endpoints that receive frequent cross-origin requests.
2. **Resource Reduction:** Reducing the load on backend servers by preventing redundant `OPTIONS` requests from reaching the application logic.
3. **CORS Configuration Rollouts:** Using low max-age values during deployment changes so that CORS fixes or updates apply quickly to client browsers without requiring users to clear their caches.

---

## Security Implication: Stale CORS Policy Cache

```
SCENARIO:
  Day 1: A server has a weak CORS configuration (e.g., Access-Control-Allow-Origin: *).
         Access-Control-Max-Age: 86400 is set, caching this rule for 24 hours.
         An attacker visits a malicious site that makes cross-origin calls to the server.
         The attacker's browser caches the vulnerable CORS policy.

  Day 1 (1 hour later): The server administrator detects the CORS vulnerability and fixes the policy.

  Day 2 (12 hours later): The attacker's browser still holds the cached (vulnerable) policy.
         The attacker can continue sending cross-origin requests and reading response data because the browser relies on the cached preflight response.

  IMPACT: Vulnerabilities can persist on clients even after they are fixed on the server.
```

---

## Commands

To inspect the `Access-Control-Max-Age` header returned by a server during a CORS preflight request, use the following `curl` command. Note that we must send an `OPTIONS` request with `Origin` and `Access-Control-Request-Method` headers to trigger a preflight response.

```bash
curl -X OPTIONS -I -s "https://httpbin.org/status/200" \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Custom-Header"
```

---

## Sample Output

When the server supports CORS and defines a preflight cache lifetime, the response headers will include `Access-Control-Max-Age`:

```http
HTTP/2 200 OK
Date: Tue, 16 Jun 2026 10:20:38 GMT
Content-Type: text/html; charset=utf-8
Connection: keep-alive
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: X-Custom-Header
Access-Control-Max-Age: 600
Access-Control-Allow-Credentials: true
Cache-Control: no-cache
```

---

## How to Fix / Secure

| Risk / Issue | Mitigation / Action |
|--------------|---------------------|
| **Excessive Max-Age** | Limit `Access-Control-Max-Age` to 600 seconds (10 minutes) or 1800 seconds (30 minutes) to balance performance and agility. |
| **Stale CORS Policies** | Reduce the cache duration temporarily when introducing CORS modifications, then raise it back once configuration stability is verified. |
| **DoS via OPTIONS flooding** | Apply rate limiting specifically targeting `OPTIONS` requests if caching is disabled or set to 0. |

---

## Related Notes
- [[41 - Access-Control-Allow-Origin]] — ACAO header
- [[43 - Access-Control-Allow-Methods]] — methods in preflight
- [[Module 08 - CORS]] — full CORS exploitation
