---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Token (JWT) Overview

JSON Web Tokens (JWTs) are a compact, URL-safe means of representing claims to be transferred between two parties. They are commonly used for authentication and information exchange in web applications. A JWT consists of three parts: the header, the payload, and the signature. These components are Base64Url encoded and separated by dots (`.`).

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJyb2xlcyI6WyJhZG1pbiIsInVzZXIiXX0.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
```

This can be broken down into three parts:

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
    ```json
    {
      "alg": "HS256",
      "typ": "JWT"
    }
    ```

2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
    ```json
    {
      "sub": "1234567890",
      "name": "John Doe",
      "iat": 1516239021,
      "roles": ["admin", "user"]
    }
    ```

3. **Signature**: Ensures the integrity of the token. It is created by taking the encoded header and payload, a secret, and the algorithm specified in the header.
    ```json
    HMACSHA256(
      base64UrlEncode(header) + "." +
      base64UrlEncode(payload),
      secret)
    ```

### Why JWTs Matter

JWTs provide a secure way to transmit information between parties as a JSON object. Because they are signed, they can be trusted to ensure that the sender is who they say they are. This makes them ideal for authentication and authorization purposes.

### How JWTs Work Under the Hood

When a user logs in, the server generates a JWT and sends it to the client. The client stores this token and includes it in subsequent requests to the server. The server verifies the token and extracts the claims to determine the user's identity and permissions.

### Common Mistakes Without JWTs

Without proper implementation and validation, JWTs can be vulnerable to attacks. For instance, if the server does not properly validate the signature, an attacker could manipulate the token to gain unauthorized access.

---
<!-- nav -->
[[04-Introduction to JWT and Its Structure|Introduction to JWT and Its Structure]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[06-Background Theory on JWT and CSRF Tokens|Background Theory on JWT and CSRF Tokens]]
