---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair (using RSA or ECDSA).

### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Used to verify the integrity of the token. It ensures that the token was not tampered with.

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTAxMjF9.6nHvK5rWQyqU2hPb58J6ZD7Tz6k7o7j8
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
    "iat": 1516310021,
    "exp": 1516310121
  }
  ```

- **Signature**:
  ```plaintext
  6nHvK5rWQyqU2hPb58J6ZD7Tz6k7o7j8
  ```

### Signing Algorithms

There are several signing algorithms available for JWTs:

- **HS256**: HMAC using SHA-256 hash algorithm.
- **RS256**: RSA using SHA-256 hash algorithm.
- **ES256**: Elliptic Curve using SHA-256 hash algorithm.

### Why JWTs Matter

JWTs are crucial in web applications because they provide a secure way to transmit information between parties. They are often used for authentication and authorization purposes. By verifying the signature, the server can ensure that the token has not been tampered with and that it was issued by a trusted party.

---
<!-- nav -->
[[04-How to Prevent  Defend Against Weak JWT Keys|How to Prevent  Defend Against Weak JWT Keys]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[06-JWT Attacks Authentication Bypass via Weak Signing Key|JWT Attacks Authentication Bypass via Weak Signing Key]]
