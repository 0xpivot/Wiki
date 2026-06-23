---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Attacks

### What is JWT?

JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It allows you to encode information in a JSON object that can be digitally signed using a secret or a public/private key pair. JWTs are commonly used for authentication and information exchange in web applications.

#### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token and verifies that it has not been tampered with.

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTQ2MjF9.7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o
```

The above JWT can be broken down as follows:

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
    "exp": 1516314621
  }
  ```

- **Signature**:
  ```plaintext
  7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o
  ```

### Why JWT Matters

JWTs are widely used because they provide a secure way to transmit information between parties as a JSON object. They are compact and can be easily transmitted through URL, POST parameter, or inside an HTTP header. This makes them ideal for stateless authentication in distributed systems.

### How JWT Works Under the Hood

When a user logs in, the server generates a JWT and sends it back to the client. The client stores this token, typically in local storage or a cookie. On subsequent requests, the client includes the token in the `Authorization` header. The server then verifies the token and extracts the claims to authenticate the user.

#### Signing Algorithms

JWTs can be signed using various algorithms, including:

- **HS256**: HMAC using SHA-256 hash algorithm.
- **RS256**: RSA using SHA-256 hash algorithm.
- **ES256**: Elliptic Curve using SHA-256 hash algorithm.

### Common Pitfalls Without JWT

Without proper implementation and verification of JWTs, several security issues can arise:

- **Unverified Signature**: If the server does not verify the signature, attackers can modify the token and gain unauthorized access.
- **Weak Algorithms**: Using weak or deprecated algorithms can make the tokens vulnerable to attacks.
- **Token Exposure**: Storing tokens insecurely can lead to theft and unauthorized access.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/01-Introduction to JSON Web Tokens (JWT)|Introduction to JSON Web Tokens (JWT)]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[03-Introduction to JWT and CSRF Tokens|Introduction to JWT and CSRF Tokens]]
