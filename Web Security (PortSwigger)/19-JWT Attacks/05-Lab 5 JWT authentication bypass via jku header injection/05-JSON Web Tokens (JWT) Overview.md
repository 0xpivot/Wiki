---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Tokens (JWT) Overview

JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims to be transferred between two parties. They are commonly used for authentication and information exchange in web applications. A JWT consists of three parts: the header, the payload, and the signature. These parts are Base64Url encoded and separated by dots (`.`).

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTEwMjF9.TJVA95OrM7E2cBab30RMHC9H3yW1zbbV
```

This can be broken down into three parts:

1. **Header**: Contains metadata about the token, such as the type of token and the algorithm used for signing.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token and verifies that it was issued by a trusted party.

### Header Example

The header might look like this:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Where:
- `alg` specifies the algorithm used for signing (e.g., HMAC SHA-256).
- `typ` specifies the type of token (e.g., JWT).

### Payload Example

The payload might look like this:

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239021,
  "exp": 1516240021
}
```

Where:
- `sub` is the subject of the token (e.g., user ID).
- `name` is the name of the user.
- `iat` is the time the token was issued.
- `exp` is the expiration time of the token.

### Signature Example

The signature is created by taking the encoded header and payload, concatenating them with a dot, and then signing the result with a secret key.

### Why JWTs Matter

JWTs provide a secure way to transmit information between parties as a JSON object. Because they are signed, they can be verified and trusted without further interaction with a database. This makes them ideal for stateless authentication in distributed systems.

### Potential Vulnerabilities

Despite their benefits, JWTs can be vulnerable to several attacks, including:

- **Signature Forgery**: If the secret key is compromised, attackers can forge tokens.
- **Token Manipulation**: If the token is not properly validated, attackers can modify the payload.
- **Weak Algorithms**: Using weak algorithms can make tokens susceptible to brute-force attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/04-JSON Web Token (JWT) Overview|JSON Web Token (JWT) Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[06-Lab 5 JWT Authentication Bypass via JKU Header Injection|Lab 5 JWT Authentication Bypass via JKU Header Injection]]
