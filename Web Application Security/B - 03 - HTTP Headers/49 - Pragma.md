---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.49 Pragma: no-cache — Legacy Cache Control"
---

# 03.49 — Pragma

## What is it?

`Pragma` is a legacy HTTP header introduced in HTTP/1.0. The most common directive, `Pragma: no-cache`, is used to instruct caches not to serve a cached copy of the requested resource. 

In modern HTTP/1.1 and HTTP/2 implementations, `Cache-Control` has superseded `Pragma`. However, `Pragma` is still widely found in modern web traffic. This is because many developers include `Pragma: no-cache` in request and response headers to ensure backward compatibility with ancient proxies, clients, or Content Delivery Networks (CDNs) that do not support HTTP/1.1.

According to RFC specifications, the `Pragma` header is defined as a *request* header, meaning clients use it to request that the proxy reload the resource from the origin server. However, it is frequently used incorrectly as a *response* header by backend applications attempting to prevent caching.

---

## Use Cases

### 1. Identifying Sensitive Pages Leaking to Public Caches
When performing a Vulnerability Assessment and Penetration Testing (VAPT), security testers check if pages containing sensitive data (e.g., bank statements, profile configurations, personally identifiable information) are caching their content. If a backend application only returns `Pragma: no-cache` but fails to include modern `Cache-Control` headers (like `Cache-Control: no-store, private`), modern intermediate proxy servers and CDNs might cache the page. This leaves the sensitive page vulnerable to Web Cache Deception and unauthorized access.

### 2. Backward Compatibility in Legacy Web Clients
In older enterprise networks or legacy client systems (e.g., embedded software, ancient web browsers), HTTP/1.1 `Cache-Control` might not be fully parsed. Including `Pragma: no-cache` ensures that these legacy systems force a new request to the origin server rather than reading from a local browser cache.

---

## Commands

Use these commands to analyze how target application servers handle caching and whether they rely solely on legacy headers.

### 1. Inspecting Cache Headers of a Target Endpoint
Retrieve the headers of a specific page to check for the coexistence of `Pragma` and `Cache-Control`:
```bash
curl -s -D - -o /dev/null https://target.local/dashboard.php | grep -iE "pragma|cache-control|expires"
```

### 2. Testing CDN Caching Behavior
Determine if an intermediate CDN node caches a page by inspecting caching indicators (like `Age` or `X-Cache` headers) when only `Pragma` is present:
```bash
curl -s -I -H "Pragma: no-cache" https://target.local/static/profile.json | grep -iE "age|x-cache|cache-control"
```

---

## Sample Output

### Vulnerable Configuration (Legacy Header Only)
The response contains only `Pragma` without modern `Cache-Control` headers. Additionally, the CDN is returning a `HIT` (cached copy) with an `Age` counter, indicating that the cache is ignoring `Pragma: no-cache`.
```http
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:27:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 320
Connection: keep-alive
Pragma: no-cache
X-Cache: HIT
Age: 120
Server: CustomServer/1.0

{
  "user": "victim_user",
  "ssn": "000-12-3456",
  "balance": "$50,000"
}
```

### Secure Configuration (Modern Cache Control Applied)
The server correctly prevents caching by applying explicit HTTP/1.1 directives that instruct all layers (browsers, proxies, CDNs) to not cache or store the response.
```http
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:27:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 320
Connection: keep-alive
Cache-Control: no-store, no-cache, must-revalidate, private
Pragma: no-cache
Expires: 0
X-Cache: MISS
Server: CustomServer/1.0

{
  "user": "victim_user",
  "ssn": "000-12-3456",
  "balance": "$50,000"
}
```

---

## How to Fix / Secure

To secure sensitive endpoints against web caching vulnerabilities:

| Risk | Fix / Mitigation |
|------|------------------|
| **Relying solely on Pragma** | Do not rely on `Pragma` to control cache behavior. Always set `Cache-Control: no-store, no-cache, must-revalidate` on all responses containing private or sensitive information. |
| **Improper response header usage** | Note that RFC 7234 deprecates `Pragma` as a response header. If backward compatibility is required, keep `Pragma: no-cache`, but pair it with modern headers. |
| **Web Cache Deception** | Configure the web server/CDN to restrict caching based on strict file extensions (e.g., only static assets like `.jpg`, `.css`) rather than trusting path segments or headers alone. |

---

## Related Notes
- [[48 - Cache-Control]] — modern cache control header
- [[50 - Expires]] — another legacy cache header
