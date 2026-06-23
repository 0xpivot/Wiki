---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Token (JWT) Overview

JSON Web Tokens (JWTs) are a compact, URL-safe means of representing claims to be transferred between two parties. They are typically used to securely transmit information between parties as an encoded JSON object. JWTs consist of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing tampering and verifying the authenticity of the sender.

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

This can be broken down into three parts:

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
  ```
  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  ```

The signature is created by taking the encoded header, the encoded payload, a secret, and the algorithm specified in the header, and then hashing them together.

### Importance of JWTs

JWTs are widely used in web applications for authentication and authorization purposes. They provide a stateless mechanism for maintaining session information, which is particularly useful in distributed systems and microservices architectures.

---
<!-- nav -->
[[03-Introduction to JWT and Its Importance in Web Security|Introduction to JWT and Its Importance in Web Security]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[05-JSON Web Tokens (JWT) Overview|JSON Web Tokens (JWT) Overview]]
