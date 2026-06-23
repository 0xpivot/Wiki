---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Using Encrypted Channels

### What Are Encrypted Channels?

Encrypted channels ensure that data transmitted between a client and a server is protected from eavesdropping and interception. Common protocols for encrypted channels include HTTPS, SSH, and TLS.

### Why Use Encrypted Channels?

Unencrypted channels can expose sensitive data, such as passwords, to attackers. By using encrypted channels, data is scrambled during transmission, making it unreadable to unauthorized parties.

### How to Use Encrypted Channels

Ensure that all communication involving sensitive data uses encrypted channels. For web applications, this means using HTTPS instead of HTTP.

#### Real-World Example: Heartbleed (CVE-2014-0160)

The Heartbleed vulnerability (CVE-2014-0160) in OpenSSL allowed attackers to steal sensitive information, including private keys and passwords, from encrypted connections. Using encrypted channels correctly would have mitigated this risk.

### How to Prevent / Defend

**Detection:**
- Use network monitoring tools to detect unencrypted traffic.
- Regularly check SSL/TLS certificates for expiration and vulnerabilities.

**Prevention:**
- Always use HTTPS for web applications.
- Enable TLS for other network communications.

**Secure Coding Fix:**
```http
# Example of an HTTPS request
GET /api/data HTTP/1.1
Host: example.com
Accept: application/json
Authorization: Bearer <token>
```

---
<!-- nav -->
[[21-Username Enumeration and Brute Force Attacks|Username Enumeration and Brute Force Attacks]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[23-Using POST Requests for Credentials|Using POST Requests for Credentials]]
