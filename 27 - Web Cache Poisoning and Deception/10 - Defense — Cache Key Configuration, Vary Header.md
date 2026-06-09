---
tags: [vapt, cache, defense, beginner]
difficulty: beginner
module: "27 - Web Cache Poisoning and Deception"
topic: "27.10 Defense — Cache Key Configuration, Vary Header"
---

# 27.10 — Defense: Cache Key Configuration, Vary Header

## What is it?
Web Cache Poisoning and Deception are infrastructure-level vulnerabilities. They occur because the Cache Server (CDN/Proxy) and the Backend Server have different understandings of what makes an HTTP request unique, or what constitutes a static file.

To defend against these attacks, developers and DevOps engineers must tightly align the configurations of the cache and the application. The two most important tools for this are the **Vary Header** and strict **Cache Key Configuration**.

Think of it like establishing a strict contract between a warehouse (Cache) and a factory (Backend). The factory must put highly specific labels on every box so the warehouse knows exactly who is allowed to receive it, and the warehouse must never guess the contents of a box just by looking at its shape.

## Key Defensive Strategies

### 1. The `Vary` Header (Defeating Cache Poisoning)
If the backend application changes its HTML based on a specific HTTP header (like `User-Agent`, `X-Forwarded-Host`, `Accept-Language`, or `Origin`), it **MUST** tell the Cache Server about it.
- **How it works:** The backend application includes `Vary: X-Forwarded-Host` in its HTTP response.
- **The Result:** The Cache Server reads the `Vary` header. It updates its Cache Key for that specific URL. Instead of the key being `[URL] + [Host]`, the key becomes `[URL] + [Host] + [X-Forwarded-Host]`.
- **The Defense:** If an attacker sends `X-Forwarded-Host: evil.com`, the cache saves it under the `evil.com` key. When a legitimate user arrives without that header, the cache keys do not match, and the legitimate user is safely routed to the backend.

### 2. Strict Cache-Control (Defeating Cache Deception)
Endpoints that return sensitive, user-specific data (JSON APIs, dashboards, settings pages) must never be cached under any circumstances.
- **The Fix:** The backend must explicitly set `Cache-Control: no-store, private, max-age=0` on sensitive routes.
- **The CDN Rule:** The CDN (Cloudflare, Akamai, Varnish) must be configured to strictly obey backend `Cache-Control` headers, overriding any wildcard path or extension-based caching rules.

### 3. Strict Routing & Normalization (Defeating Deception & Poisoning)
The backend framework must not be overly permissive.
- **No Fat GETs:** Configure the web server or WAF to drop `GET` requests that contain a body or a `Content-Length` header.
- **Extension Validation:** If a route is `/api/user`, the framework must return a `404 Not Found` if the user requests `/api/user.css` or `/api/user/fake.js`. Do not gracefully ignore trailing extensions.

### 4. Cache Key Normalization at the Edge
If the backend doesn't need certain headers, the Edge Proxy/CDN should aggressively strip them before forwarding the request.
- If your application doesn't use `X-Forwarded-Host`, configure Cloudflare to drop that header from incoming public traffic. This mathematically eliminates the attack vector before it reaches your backend.

## ASCII Diagram
```text
================================================================================
                    SECURE CACHING ARCHITECTURE
================================================================================

[Attacker Attempts Cache Poisoning]
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

[Secure Backend]
Backend generates HTML using `evil.com`.
Backend explicitly adds Header: `Vary: X-Forwarded-Host`

[Secure Cache]
Cache reads the Vary header.
Stores HTML under Key: `GET / | target.com | evil.com`

[Victim Connection]
GET / HTTP/1.1
Host: target.com
(No X-Forwarded-Host header)

[Cache Evaluation]
Cache evaluates Key: `GET / | target.com | (empty)`
Does this match the attacker's key? NO.
Cache fetches a fresh, clean copy for the Victim. ATTACK BLOCKED!

--------------------------------------------------------------------------------

[Attacker Attempts Cache Deception]
Victim clicks: GET /api/user_data/fake.css HTTP/1.1

[Secure Backend]
Backend sees `/fake.css`.
Backend routing table says: "I only know `/api/user_data`."
Backend returns `404 Not Found`. ATTACK BLOCKED!
================================================================================
```

## Developer Checklist
- [ ] Are all endpoints returning sensitive data tagged with `Cache-Control: no-store, private`?
- [ ] Does the CDN/Proxy strictly obey the backend's `Cache-Control` directives?
- [ ] If the application uses HTTP headers to alter the response (e.g., for localization or CORS), does it return the corresponding `Vary` header?
- [ ] Are unneeded or obscure HTTP headers (e.g., `X-Original-URL`, `X-Rewrite-URL`) stripped by the WAF/Edge Proxy before reaching the backend?
- [ ] Does the application return 404 errors for invalid static extensions appended to dynamic routes?
- [ ] Is the web server configured to reject `GET` requests that contain an HTTP body?

## Related Notes
- [[27.02 Cache Keys and Unkeyed Inputs]]
- [[27.09 Web Cache Deception Attack]]
