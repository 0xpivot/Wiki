---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely used method for securely transmitting information between parties as a JSON object. They are compact, URL-safe means of representing claims to be transferred between two parties. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA. JWTs consist of three parts separated by dots (`.`):

1. **Header**: Contains the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims. Claims are statements about an entity (typically, the user) and additional metadata.
3. **Signature**: Used to verify the message wasn't changed along the way, and, in the case of tokens signed with a private key, to verify the sender.

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJQb3J0c2dpdXIifQ.5vKJkqDQyOJhVWJ6n9HrB05o7zj7yTgP5f8Xj9J4
```

This JWT can be broken down into three parts:

1. **Header**:
    ```json
    {
      "alg": "HS256",
      "typ": "JWT"
    }
    ```

2. **Payload**:
    ```json
    {
      "sub": "1234567890",
      "name": "John Doe",
      "iat": 1516239021,
      "iss": "Portswigger"
    }
    ```

3. **Signature**:
    ```
    5vKJkqDQyOJhVWJ6n9HrB05o7zj7yTgP5f8Xj9J4
    ```

The signature is created using the encoded header, the encoded payload, a secret, and the algorithm specified in the header.

### Key Concepts

- **Algorithm (`alg`)**: Specifies the algorithm used to sign the token. Common algorithms include `HS256`, `RS256`, and `ES256`.
- **Type (`typ`)**: Specifies the type of token. Typically set to `JWT`.
- **Subject (`sub`)**: Identifies the principal that is the subject of the JWT.
- **Issuer (`iss`)**: Identifies the principal that issued the JWT.
- **Expiration Time (`exp`)**: Identifies the expiration time on or after which the JWT MUST NOT be accepted for processing.
- **Issued At (`iat`)**: Identifies the time at which the JWT was issued.

### Vulnerabilities in JWTs

JWTs can be vulnerable to various attacks, including:

1. **None Algorithm Attack**
2. **Key ID (KID) Parameter Manipulation**
3. **Token Injection**
4. **Signature Forgery**
5. **Path Traversal via KID**

---
<!-- nav -->
[[06-How to Prevent  Defend Against JWT Authentication Bypass|How to Prevent  Defend Against JWT Authentication Bypass]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[08-JWT Attacks Bypassing Authentication via `kid` Header Path Traversal|JWT Attacks Bypassing Authentication via `kid` Header Path Traversal]]
