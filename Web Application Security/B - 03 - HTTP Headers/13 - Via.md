---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.13 Via — Proxy Chain Disclosure"
---

# 03.13 — Via

## What is it?

The `Via` HTTP header is used by proxies (both forward and reverse proxies) and content delivery networks (CDNs) to track the path of a request or response. When an HTTP request or response passes through one or more intermediate servers, each server appends its protocol version and network node information (hostname, IP address, and sometimes port or application name) to the `Via` header.

While helpful for troubleshooting routing loops and identifying proxy chains, the `Via` header often leaks details about the internal infrastructure of a target network, which can be useful to attackers during reconnaissance.

### Beginner Explanation
Imagine sending a physical letter through several post offices. Each post office stamps the back of the envelope with its branch name and the time it handled the letter. This stamp is like the `Via` header. It tells you exactly which servers (post offices) handled your web request on its way to the final destination. If a server doesn't hide this stamp, an attacker can see the names of all the internal mail centers (internal server names and software versions) and use that information to map out the target's internal network.

---

## Format

```
Via: [protocol-version] [host] [comment]
```

- **protocol-version**: The HTTP protocol version used by the proxy (e.g., `1.1` or `2`).
- **host**: The name or IP address of the proxy (and optional port number).
- **comment**: An optional comment field containing additional information, such as proxy software details or vendor name.

Examples:
- `Via: 1.1 proxy1.internal.corp` (Single proxy disclosing internal domain name)
- `Via: 1.1 varnish (Varnish/6.0)` (Discloses Varnish cache server and exact version)
- `Via: 1.1 squid-proxy:3128` (Discloses Squid proxy running on port 3128)
- `Via: 2 cloudflare` (HTTP/2 proxying through Cloudflare CDN)
- `Via: 1.1 proxy1, 1.1 proxy2` (A request that went through two consecutive proxies)

---

## Categories
- **Security Concept:** Information Disclosure / Reconnaissance
- **Header Type:** Request and Response Header
- **Context:** Web Infrastructure / Reverse Proxies and CDNs

---

## Use Cases

1. **Routing Loop Prevention:** Proxies check the `Via` header to see if they have already processed the request. If they see their own identifier in the header, they drop the request to prevent infinite routing loops.
2. **Path Diagnostics:** Administrators inspect the header to troubleshoot configuration issues or performance bottlenecks along the delivery chain.
3. **Feature Negotiation:** Web servers can detect what version of HTTP is supported by the proxies along the path, allowing them to adjust features dynamically.

---

## Information Disclosed

An unconfigured proxy can reveal critical network context to an external user:

```
EXAMPLE RESPONSE HEADER:
  Via: 1.1 squid-server-01.internal.local:3128 (squid/4.15)

REVEALED SECRETS:
  - Internal Hostname: squid-server-01.internal.local
  - Internal IP Domain: .internal.local
  - Internal Port: 3128
  - Proxy Software & Version: Squid proxy version 4.15 (vulnerable to known CVEs)
```

**Attack Value:**
- **SSRF Targeting:** The disclosed internal domain `.internal.local` gives an attacker hostnames to try targeting with Server-Side Request Forgery (SSRF) attacks.
- **Vulnerability Mapping:** Finding specific software versions (like `squid/4.15`) allows attackers to look up public exploits (CVEs).
- **Port Scanning:** Port information (`3128`) informs the attacker about what ports are open on internal systems.

---

## Commands

To check if a target website leaks proxy information in the `Via` header, use the following `curl` commands to inspect response headers:

```bash
# General search for Via header
curl -s -I "https://example.com" | grep -i "via"

# Check for multiple caching/proxy indicators (Via, X-Cache, X-Served-By, etc.)
curl -s -I "https://example.com" | grep -iE "via|x-cache|x-served-by|x-varnish|server"
```

---

## Sample Output

When running the reconnaissance curl command on a target using Varnish cache, you might receive output like this:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 1256
Connection: keep-alive
Server: Apache/2.4.41 (Ubuntu)
X-Cache: HIT
X-Cache-Hits: 3
Via: 1.1 varnish (Varnish/6.0), 1.1 squid-server.internal:3128
Age: 240
Accept-Ranges: bytes
```

---

## How to Fix / Secure

| Risk / Issue | Mitigation / Action |
|--------------|---------------------|
| **Internal Hostname Leak** | Configure reverse proxies to strip the `Via` header or rewrite the host field to a generic name (e.g. `Via: 1.1 reverse-proxy`). |
| **Software Version Leak** | Disable proxy comments containing product versions (e.g. configure Squid to disable `httpd_suppress_version_string` or customize Varnish headers). |
| **Request Leakage (Client Side)** | When performing penetration testing or internal requests, ensure your own proxy (like Burp Suite) is configured to strip client-side `Via` headers to remain stealthy. |

---

## Related Notes
- [[12 - Forwarded]] — RFC 7239 standard proxy header
- [[02 - X-Forwarded-For]] — IP disclosure
- [[52 - X-Powered-By]] — other tech fingerprinting header
- [[53 - Server]] — server version disclosure
