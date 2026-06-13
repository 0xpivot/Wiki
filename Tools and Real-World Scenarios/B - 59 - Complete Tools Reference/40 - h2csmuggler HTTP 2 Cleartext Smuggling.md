---
tags: [tools, web-testing, exploiter, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.40 h2csmuggler HTTP 2 Cleartext Smuggling"
---

# h2csmuggler HTTP/2 Cleartext Smuggling

## 1. Introduction to HTTP/2 Cleartext (h2c)

As modern web infrastructure transitions to HTTP/2 for performance benefits, new classes of vulnerabilities have emerged. While classic HTTP Request Smuggling relies on ambiguous `Content-Length` and `Transfer-Encoding` headers in HTTP/1.1, **h2c Smuggling** exploits the mechanism used to upgrade an HTTP/1.1 connection to an HTTP/2 Cleartext (h2c) connection.

**h2csmuggler** is a cutting-edge tool designed to identify and exploit h2c upgrade vulnerabilities. By abusing poorly configured reverse proxies and load balancers, an attacker can establish a direct, unmonitored HTTP/2 tunnel to the backend server, entirely bypassing the frontend's routing rules, access controls, and Web Application Firewalls (WAFs).

## 2. Under the Hood: The Mechanics of h2c Smuggling

The vulnerability originates from how the HTTP/1.1 `Upgrade: h2c` header is processed.

In a normal scenario, if a client wants to upgrade to h2c, it sends an HTTP/1.1 request with the headers:
```http
Connection: Upgrade, HTTP2-Settings
Upgrade: h2c
HTTP2-Settings: <base64url encoding of HTTP/2 SETTINGS payload>
```

If the server supports h2c, it responds with `101 Switching Protocols`, and from that point forward, the TCP socket uses the binary HTTP/2 protocol.

### 2.1 The Proxied Infrastructure Flaw

In modern architectures, a frontend proxy (like Nginx, HAProxy, or AWS ALB) sits before the backend server.
1. The proxy evaluates the incoming HTTP/1.1 request, checks access controls (e.g., blocking `/admin`), and forwards the request to the backend.
2. If the client includes the `Upgrade: h2c` header, a vulnerable proxy might not understand or act on the upgrade itself. Instead, it blindly forwards the upgrade headers to the backend.
3. The backend server *does* understand h2c, agrees to the upgrade, and sends a `101 Switching Protocols` response back through the proxy.
4. The proxy sees the `101` status and assumes the client and backend have agreed to use an opaque protocol (like WebSockets). The proxy then stops parsing the HTTP traffic and simply acts as a dumb, transparent TCP tunnel between the client and the backend.

### 2.2 The Exploit

Once the proxy steps out of the way and acts as a dumb TCP tunnel, the attacker has a direct, uninspected line to the backend. The attacker can now send HTTP/2 requests directly to the backend server. Since the frontend proxy is no longer enforcing access controls (because it's no longer parsing the requests), the attacker can access restricted endpoints like `/internal/api` or `/admin` that the proxy was supposed to protect.

## 3. Architecture and Attack Flow Diagram

```ascii
                      [Attacker Running h2csmuggler]
                                   |
                (1) HTTP/1.1 GET / (Upgrade: h2c)
                                   |
+-------------------------------------------------------------------------+
| ============================                                            |
| FRONTEND REVERSE PROXY                                                  |
| ============================                                            |
|  - Blocks /admin                                                        |
|  - Doesn't terminate h2c; forwards Upgrade headers blindly.             |
+-------------------------------------------------------------------------+
                                   |
                (2) Forwards Upgrade Request
                                   |
+-------------------------------------------------------------------------+
| ============================                                            |
| BACKEND WEB SERVER                                                      |
| ============================                                            |
|  - Accepts h2c upgrade.                                                 |
|  - Sends '101 Switching Protocols'.                                     |
+-------------------------------------------------------------------------+
                                   |
                (3) 101 Switching Protocols
                                   |
          (Proxy transitions into a transparent TCP tunnel)
                                   |
                 (4) h2csmuggler sends HTTP/2 frames
                     Direct request: GET /admin
                                   |
      (Proxy blindly forwards binary frames; ACLs bypassed)
                                   |
                  (5) Backend responds with /admin data
```

## 4. Usage and Syntax of h2csmuggler

`h2csmuggler` automates the complex process of negotiating the h2c upgrade, verifying the proxy's behavior, and multiplexing the smuggled requests over the HTTP/2 tunnel.

### 4.1 Basic Detection

To simply check if an endpoint is vulnerable to h2c smuggling:
```bash
python3 h2csmuggler.py -x https://target.com/
```
*(The tool will attempt to upgrade the connection on the root path and identify if the backend responds with a 101 status).*

### 4.2 Exploiting and Bypassing ACLs

If you know that the frontend proxy blocks `/admin`, but you suspect the infrastructure is vulnerable to h2c smuggling, you can use h2csmuggler to reach the restricted endpoint:

```bash
python3 h2csmuggler.py -x https://target.com/ -X GET -d /admin
```
**Explanation:**
- `-x`: The external URL to initiate the upgrade (e.g., the public, unrestricted endpoint).
- `-X`: The HTTP method to use in the smuggled HTTP/2 request.
- `-d`: The internal destination path to request over the smuggled tunnel.

### 4.3 Custom Headers and Authentication

You can inject custom headers into the smuggled request to further abuse internal routing or satisfy backend authentication requirements:
```bash
python3 h2csmuggler.py -x https://target.com/ -d /api/internal -H "X-Forwarded-For: 127.0.0.1" -H "Authorization: Bearer Token"
```

## 5. Exploitation Scenarios and Impact

### 5.1 Bypassing WAFs

Web Application Firewalls rely on inspecting HTTP traffic. When the connection is upgraded to h2c, the proxy/WAF stops inspecting the traffic and just forwards the binary data. An attacker can use h2csmuggler to send malicious payloads (SQLi, XSS, Command Injection) that the WAF would normally block, completely bypassing the security perimeter.

### 5.2 Accessing Internal Services

Often, a single frontend proxy routes traffic to multiple backend microservices based on the Host header or URL path. By establishing an h2c tunnel, the attacker can manipulate the HTTP/2 pseudo-headers (like `:authority` and `:path`) to request internal microservices that are not exposed to the public internet.

## 6. Advanced Usage: Connection Multiplexing

HTTP/2 allows connection multiplexing. `h2csmuggler` leverages this by maintaining the smuggled tunnel and sending multiple concurrent requests. This means that after bypassing the frontend proxy once, the attacker can run brute-force attacks, directory fuzzing, or data exfiltration over the single smuggled connection, maximizing speed and minimizing logs on the frontend proxy (which only sees a single 101 status connection).

## 7. Defensive Considerations and Mitigation

Securing an environment against h2c smuggling requires strict configuration of the frontend proxies and load balancers:
- **Do Not Blindly Forward Upgrade Headers:** Ensure that the proxy strips the `Upgrade` header and the `Connection` header before forwarding requests to the backend. Proxies should explicitly manage protocol upgrades.
- **Terminate HTTP/2 at the Edge:** Have the frontend proxy handle all HTTP/2 and h2c traffic natively, terminating the connection and forwarding standard HTTP/1.1 or controlled HTTP/2 traffic to the backend.
- **Backend Hardening:** Configure backend servers to reject h2c upgrades entirely unless they are specifically required for a known, trusted internal architecture. Avoid using h2c in production; use standard HTTP/2 over TLS (h2) instead.
- **Enforce Access Controls on the Backend:** Defense-in-depth dictates that access controls shouldn't rely solely on the frontend proxy. The backend should also verify authorization.

## 8. Chaining Opportunities

- **SSRF to RCE:** Use the h2c tunnel to bypass frontend restrictions and hit an internal SSRF endpoint, leading to full internal network compromise. See [[15 - Server-Side Request Forgery (SSRF)]].
- **Exploiting Backend Vulnerabilities:** Chain h2c smuggling with tools like SQLmap or Commix to exploit backend systems without interference from the WAF. See [[22 - SQLmap Advanced Usage]] and [[36 - Commix Command Injection Exploiter]].
- **API Abuse:** Access restricted administrative API endpoints to extract sensitive data or modify configurations. See [[03 - API Authentication Bypasses]].

## 9. Appendix: In-Depth h2c Smuggling Operations and Payloads

### A.1 The HTTP/1.1 Upgrade Request (Verbose)
To fully understand the vulnerability, here is the exact raw HTTP request sent by `h2csmuggler` to initiate the tunnel:
```http
GET / HTTP/1.1
Host: target.com
Upgrade: h2c
HTTP2-Settings: AAMAAABkAARAAAAAAAIAAAAA
Connection: Upgrade, HTTP2-Settings
User-Agent: h2csmuggler/1.0
Accept: */*

```
If the backend accepts, it replies:
```http
HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: h2c

[Binary HTTP/2 Frames Follow...]
```
The frontend proxy simply forwards these frames back and forth.

### A.2 Manually Interacting with the Smuggled Tunnel
While `h2csmuggler` automates the process, you can theoretically interact with the tunnel using custom HTTP/2 clients. Once the 101 response is received, the socket must immediately switch to speaking HTTP/2 binary framing. This is why standard tools like `curl` or `Burp Suite` (without specialized extensions) struggle to exploit this natively. `h2csmuggler` implements a custom HTTP/2 framing layer over the raw TCP socket to achieve this.

### A.3 Abusing Internal Routing via Pseudo-Headers
HTTP/2 uses pseudo-headers (prefixed with a colon) instead of the standard request line.
When sending the smuggled request over the tunnel, `h2csmuggler` constructs these headers:
- `:method`: POST
- `:path`: /internal/admin/config
- `:authority`: internal-service.local
- `:scheme`: http

By manipulating the `:authority` header, the attacker can exploit SSRF or target specific microservices within a Kubernetes cluster that the backend load balancer routes to, completely bypassing the external ingress controllers.

### A.4 Bypassing Path Normalization
Sometimes, frontend proxies normalize paths (e.g., converting `/api/../admin` to `/admin`) and block them. By smuggling the request, the proxy never sees the `:path` header. The attacker can send complex, un-normalized paths directly to the backend application server, which might have different path normalization logic, leading to directory traversal or endpoint exposure.

### A.5 Troubleshooting h2csmuggler
- **Connection Resets (RST_STREAM):** If the backend immediately sends an HTTP/2 `RST_STREAM` frame after the upgrade, it means the server supports h2c but rejected the specific request. Ensure your smuggled request is perfectly formatted and includes required headers (like `Accept`, `User-Agent`).
- **No 101 Response:** If the server responds with a 200 OK instead of 101, it means either the frontend proxy stripped the `Upgrade` headers or the backend does not support h2c.

## 10. Related Notes

- [[39 - smuggler HTTP Request Smuggling Detector]]
- [[09 - HTTP Protocol Weaknesses]]
- [[45 - Web Application Firewalls and Bypasses]]
- [[24 - Advanced Proxy Configurations]]
- [[54 - HTTP2 Binary Protocol Analysis]]
- [[11 - Bypass Strategies for WAFs]]
