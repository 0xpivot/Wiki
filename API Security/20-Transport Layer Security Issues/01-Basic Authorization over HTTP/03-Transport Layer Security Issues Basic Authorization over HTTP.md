---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Transport Layer Security Issues: Basic Authorization over HTTP

### Introduction to Transport Layer Security (TLS)

Transport Layer Security (TLS) is a cryptographic protocol designed to provide communications security over a computer network. It is widely used to secure web traffic, ensuring that data transmitted between a client and a server remains confidential and unaltered. TLS is the successor to Secure Sockets Layer (SSL), which was widely used until vulnerabilities were discovered.

#### Why TLS Matters

TLS is crucial because it encrypts data in transit, preventing eavesdropping and man-in-the-middle attacks. Without TLS, data sent over the internet can be intercepted and read by unauthorized parties. This includes sensitive information such as passwords, credit card numbers, and personal data.

### Basic Authorization over HTTP

Basic Authorization is an HTTP authentication scheme that uses Base64 encoding to transmit credentials. However, when used over HTTP instead of HTTPS (HTTP over TLS), these credentials are transmitted in plain text, making them vulnerable to interception.

#### How Basic Authorization Works

When a client attempts to access a resource protected by Basic Authentication, the server responds with a `401 Unauthorized` status code and a `WWW-Authenticate` header. The client then sends a `Authorization` header with the username and password encoded in Base64.

```http
GET /protected-resource HTTP/1.1
Host: example.com
```

Server Response:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Basic realm="Secure Area"
```

Client Request with Credentials:

```http
GET /protected-resource HTTP/1.1
Host: example.com
Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
```

In this example, `QWxhZGRpbjpvcGVuIHNlc2F2ZQ==` is the Base64-encoded string of `Aladdin:open sesame`.

#### Vulnerabilities of Basic Authorization over HTTP

Using Basic Authorization over HTTP exposes credentials to interception. An attacker can use tools like Wireshark or tcpdump to capture network traffic and decode the Base64-encoded credentials.

#### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a vulnerability in the Apache Struts framework where sensitive information, including credentials, was exposed due to improper handling of HTTP headers. This vulnerability highlights the importance of securing HTTP traffic with TLS.

### JWT Tokens and Authorization

JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims to be transferred between two parties. They are often used for authentication and information exchange.

#### How JWT Works

A JWT consists of three parts: Header, Payload, and Signature. The header typically contains the type of token and the signing algorithm. The payload contains the claims, and the signature is used to verify the integrity of the token.

Example JWT:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  },
  "signature": "<signature>"
}
```

When using JWTs over HTTP, the token is transmitted in the `Authorization` header.

```http
GET /api/resource HTTP/1.1
Host: example.com
Authorization: Bearer <jwt-token>
```

#### Vulnerabilities of JWT over HTTP

Similar to Basic Authorization, transmitting JWTs over HTTP exposes the token to interception. An attacker can capture the token and use it to impersonate the user.

### Real-World Example: OAuth 2.0 Token Leakage

OAuth 2.0 is a widely used authorization framework that relies on tokens for authentication. In 2019, a vulnerability was discovered in the OAuth 2.0 implementation of several popular services, including Google and Facebook. The vulnerability allowed attackers to intercept and reuse OAuth tokens, leading to unauthorized access.

### How to Prevent / Defend Against Basic Authorization and JWT Over HTTP

#### Detection

To detect the use of Basic Authorization or JWT over HTTP, you can use network monitoring tools like Wireshark or tcpdump. These tools can capture and analyze network traffic to identify unprotected credentials and tokens.

#### Prevention

1. **Use HTTPS**: Always use HTTPS (HTTP over TLS) to encrypt data in transit. This ensures that credentials and tokens are not exposed to interception.

2. **Secure Coding Practices**:
   - Ensure that all APIs and endpoints are configured to use HTTPS.
   - Implement strict security policies that enforce the use of HTTPS.

3. **Configuration Hardening**:
   - Configure web servers to redirect HTTP traffic to HTTPS.
   - Use HSTS (HTTP Strict Transport Security) to enforce secure connections.

4. **Secure Code Fix**:
   - **Vulnerable Code**:
     ```http
     GET /api/resource HTTP/1.1
     Host: example.com
     Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
     ```
   - **Fixed Code**:
     ```http
     GET /api/resource HTTP/1.1
     Host: example.com
     Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
     ```

     Note: The above example shows the same request, but in practice, the server should be configured to enforce HTTPS.

5. **Network Configuration**:
   - Configure web servers to enforce HTTPS:
     ```nginx
     server {
         listen 80;
         server_name example.com;
         return 301 https://$host$request_uri;
     }

     server {
         listen 443 ssl;
         server_name example.com;

         ssl_certificate /path/to/cert.pem;
         ssl_certificate_key /path/to/key.pem;

         location / {
             proxy_pass http://backend;
         }
     }
     ```

### Practice Labs

For hands-on experience with API security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on web security, including API security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web app for security testing.

These labs provide practical scenarios to test and understand the vulnerabilities discussed.

### Conclusion

Transport Layer Security (TLS) is essential for securing data in transit. Using Basic Authorization or JWT over HTTP exposes credentials and tokens to interception, leading to potential security breaches. By enforcing HTTPS and implementing secure coding practices, you can mitigate these risks and ensure the confidentiality and integrity of your data.

By understanding the concepts, detecting vulnerabilities, and implementing robust defenses, you can significantly enhance the security of your applications and APIs.

---
<!-- nav -->
[[02-Transport Layer Security Issues Basic Authorization Over HTTP|Transport Layer Security Issues Basic Authorization Over HTTP]] | [[API Security/20-Transport Layer Security Issues/01-Basic Authorization over HTTP/00-Overview|Overview]] | [[API Security/20-Transport Layer Security Issues/01-Basic Authorization over HTTP/04-Practice Questions & Answers|Practice Questions & Answers]]
