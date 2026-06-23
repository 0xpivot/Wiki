---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Attacks

Welcome to the Web Security Academy series, where we delve deep into various aspects of web security. Today, we will focus on a specific type of attack involving JSON Web Tokens (JWTs), specifically the "JWK Header Injection" attack. This attack allows an attacker to bypass authentication mechanisms by injecting a malicious JWK (JSON Web Key) into the JWT header. Let's start by understanding the basics of JWTs and their role in web applications.

### What is a JWT?

A JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It consists of three parts: the header, the payload, and the signature. These parts are Base64Url encoded and separated by dots (`.`).

#### Structure of a JWT

```mermaid
graph TD
    A[Header] --> B[Payload]
    B --> C[Signature]
```

- **Header**: Contains metadata about the token, such as the type of token and the signing algorithm.
- **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
- **Signature**: Ensures the integrity of the token and verifies that it was issued by a trusted party.

#### Example of a JWT

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking down the example:

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

### Why JWTs Matter

JWTs are widely used in web applications for session management and authentication. They provide a stateless way to manage sessions, meaning the server does not need to store session information, reducing the load on the server. However, this also means that the security of the application heavily relies on the proper implementation and validation of JWTs.

### Real-World Examples

Recent breaches and vulnerabilities involving JWTs include:

- **CVE-2021-21974**: A vulnerability in the `jwt-go` library allowed attackers to bypass authentication by manipulating the JWT header.
- **CVE-2021-3279**: A vulnerability in the `auth0/node-jsonwebtoken` library allowed attackers to inject arbitrary keys into the JWT header.

These examples highlight the importance of properly validating and securing JWTs in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/00-Overview|Overview]] | [[02-JWT Attacks Overview|JWT Attacks Overview]]
