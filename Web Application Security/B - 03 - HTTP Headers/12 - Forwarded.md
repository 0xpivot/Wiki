---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.12 Forwarded — RFC 7239, Abuse Patterns"
---

# 03.12 — Forwarded

## What is it?

`Forwarded` is an HTTP request header standardized in RFC 7239. It is designed to group proxy-related routing information that was historically scattered across several non-standard headers, namely `X-Forwarded-For` (client IP), `X-Forwarded-Host` (original target host), and `X-Forwarded-Proto` (original protocol).

When a client sends a request through one or more reverse proxies, load balancers, or CDNs, the proxy adds or appends to the `Forwarded` header to let the backend server know the original client's IP, protocol, and target host. However, if the backend server blindly trusts client-controlled input in this header without verification, it becomes vulnerable to IP spoofing, Host header injection, or protocol downgrade attacks.

### Beginner Explanation
Imagine ordering a package online and having it routed through three different courier stations before it reaches your door. At each station, the courier writes on a single shipping label: "Handled for [Original Sender] by [Station ID] using [Express Delivery] to [Host Address]." This unified label is what the `Forwarded` header does. Instead of writing separate stickers (like `X-Forwarded-For`), it combines all the routing details into one clean line. If the final delivery driver (the web server) doesn't check if the label was tampered with by the sender, the sender could lie on the label and claim they are "localhost" or that they used a secure delivery method when they did not.

---

## Syntax

```
Forwarded: for=1.2.3.4; by=5.5.5.5; host=target.com; proto=https
```

- **`for=`**: The IP address of the client that initiated the request (equivalent to `X-Forwarded-For`).
- **`by=`**: The IP address of the proxy interface that received the request.
- **`host=`**: The host parameter of the request header field (equivalent to `X-Forwarded-Host`).
- **`proto=`**: The protocol used to make the request (either `http` or `https`; equivalent to `X-Forwarded-Proto`).

**Comma-Separated Chain for Multiple Proxies:**
```
Forwarded: for=1.2.3.4, for=5.6.7.8; by=9.9.9.9; proto=https
```

---

## Categories
- **Security Concept:** Access Control Bypass / Information Spoofing
- **Header Type:** Request Header
- **Context:** Web Infrastructure / Proxy and Load Balancer Routing

---

## Use Cases

1. **IP Tracking and Logging:** Enabling backend servers behind load balancers to log the real client IP address rather than the internal IP of the load balancer.
2. **Dynamic Link Generation:** Helping applications generate absolute URLs (e.g., in emails or redirects) using the original protocol (`proto`) and host (`host`) requested by the user, even when the server runs on a different port internally.
3. **Location-Based Customization:** Tailoring application content based on the client IP country or region passed through the `for` field.

---

## Security Implications

### 1. IP Spoofing via Forwarded Header
If a backend application uses the client IP from the `Forwarded: for=` parameter to authenticate users (e.g., allowing access to admin panels only from `/admin` if the IP is `127.0.0.1` or an internal network), an attacker can easily bypass this check.
```
ATTACK REQUEST:
  GET /admin HTTP/1.1
  Host: vulnerable.com
  Forwarded: for=127.0.0.1
```
If the proxy does not strip or overwrite the client-supplied `Forwarded` header, the backend sees the client IP as `127.0.0.1` and grants access.

### 2. Host Override (Password Reset Poisoning)
If the application generates password reset links using the host parameter:
```
ATTACK REQUEST:
  POST /password-reset HTTP/1.1
  Host: vulnerable.com
  Forwarded: host=evil.com
```
If the backend uses `Forwarded: host` to build the reset link, the email sent to the user will contain `https://evil.com/reset-token?id=123`, sending the secret token to the attacker.

### 3. Protocol Downgrade Bypass
If the server redirects HTTP traffic to HTTPS, but relies on `Forwarded: proto` to determine if the connection is already secure:
```
ATTACK REQUEST:
  GET /login HTTP/1.1
  Forwarded: proto=https; for=1.2.3.4
```
Even if the attacker sent the request over unencrypted HTTP, the application assumes it is secure and bypasses the redirect, potentially exposing credentials in transit.

---

## Commands

Penetration testers can use the following commands to test for IP spoofing and host override vulnerabilities:

```bash
# Test IP restriction bypass on admin panel
curl -H "Forwarded: for=127.0.0.1" -s -I "https://example.com/admin"

# Test host redirection / poisoning
curl -H "Forwarded: host=attacker.com" -s -I "https://example.com/login"

# Test protocol downgrade checks
curl -H "Forwarded: proto=https; for=10.0.0.1" -s -I "http://example.com/"
```

---

## Sample Output

A target server vulnerable to `Forwarded` header injection might return a `200 OK` or reflect the host header in its redirects. Here is an example of a successful Host override redirect response:

```http
HTTP/1.1 302 Found
Date: Tue, 16 Jun 2026 10:20:38 GMT
Content-Type: text/html; charset=utf-8
Connection: keep-alive
Location: https://attacker.com/login?redirect=true
Content-Length: 0
```

---

## How to Fix / Secure

| Risk / Issue | Mitigation / Action |
|--------------|---------------------|
| **Bypassing IP ACLs** | Never trust client-provided headers for security decisions. If using `Forwarded`, configure the edge proxy to completely strip client-supplied headers and construct a new one from the actual TCP socket connection. |
| **Host Header Poisoning** | Configure the backend web server to validate the `host` value against a strict whitelist of allowed domains before using it in redirects or link generation. |
| **Protocol Spoofing** | Configure the proxy to drop the `proto` parameter unless it is explicitly set by the edge load balancer, and enforce TLS globally on the load balancer itself. |

---

## Related Notes
- [[02 - X-Forwarded-For]] — IP forwarding (non-standard but prevalent)
- [[03 - X-Forwarded-Host]] — Host forwarding header
- [[04 - X-Forwarded-Proto]] — Protocol forwarding header
- [[13 - Via]] — proxy chain disclosure header
