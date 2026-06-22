---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Token (JWT) Overview

JSON Web Tokens (JWTs) are a widely used method for securely transmitting information between parties as a JSON object. They are particularly useful in web applications for maintaining state across different requests, such as authentication and authorization. A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, including the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing modification of the header and payload.

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

- **Header**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9` (Base64 encoded)
  - Decoded: `{ "alg": "HS256", "typ": "JWT" }`
- **Payload**: `eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ` (Base64 encoded)
  - Decoded: `{ "sub": "1234567890", "name": "John Doe", "iat": 1516239022 }`
- **Signature**: `SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

### Signing Algorithms

The `alg` field in the header specifies the algorithm used to sign the token. Common algorithms include:

- **HS256**: HMAC using SHA-256 hash algorithm.
- **RS256**: RSA using SHA-256 hash algorithm.
- **ES256**: Elliptic Curve using SHA-256 hash algorithm.

### Vulnerabilities in JWTs

One of the most critical vulnerabilities in JWTs is **algorithm confusion**, where an attacker can manipulate the `alg` field to bypass authentication or authorization checks. This is particularly dangerous when the server supports multiple signing algorithms but does not properly validate the algorithm used.

---
<!-- nav -->
[[03-Introduction to JWT and Algorithm Confusion|Introduction to JWT and Algorithm Confusion]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[05-Algorithm Confusion Attack|Algorithm Confusion Attack]]
