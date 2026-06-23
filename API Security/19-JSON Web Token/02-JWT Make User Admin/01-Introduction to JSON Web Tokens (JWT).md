---
course: API Security
topic: JSON Web Token
tags: [api-security]
---

## Introduction to JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely adopted standard for securely transmitting information between parties as a JSON object. JWTs are commonly used in authentication and authorization processes, allowing users to access resources or perform actions within an application. This chapter will delve into the intricacies of JWTs, focusing on how they can be manipulated to elevate user privileges, specifically making a user an administrator. We will cover the background theory, practical examples, recent real-world vulnerabilities, and comprehensive defense mechanisms.

### What is a JWT?

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing tampering and verifying the authenticity of the sender.

The structure of a JWT looks like this:

```
<base64UrlEncode(header)>.<base64UrlEncode(payload)>.<signature>
```

#### Example of a JWT

Here’s a simple example of a JWT:

```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking it down:

- **Header**:
  ```json
  {
    "alg": "HS256",
    "typ": "JWT"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  }
  ```

- **Signature**:
  ```plaintext
  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  ```

### How JWT Works

When a user logs in, the server generates a JWT and sends it to the client. The client then stores this token, typically in local storage or a cookie. On subsequent requests, the client includes the token in the `Authorization` header, usually as a Bearer token.

#### Example of a JWT Request

```http
GET /api/resource HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Why JWT Matters

JWTs provide a stateless mechanism for authentication and authorization, meaning the server does not need to store session information. This makes them ideal for distributed systems and microservices architectures. However, their security relies heavily on proper implementation and protection against various attacks.

### Recent Real-World Examples

Several high-profile breaches have involved JWT vulnerabilities:

- **CVE-2021-21972**: A vulnerability in the `jwt-go` library allowed attackers to bypass signature verification by using non-standard characters in the JWT header.
- **CVE-2021-3279**: A flaw in the `jsonwebtoken` library for Node.js allowed attackers to forge tokens due to improper validation of the `kid` claim.

These examples highlight the importance of keeping libraries up-to-date and implementing robust security measures.

---
<!-- nav -->
[[API Security/19-JSON Web Token/02-JWT Make User Admin/00-Overview|Overview]] | [[02-Making a User Admin via JWT Manipulation|Making a User Admin via JWT Manipulation]]
