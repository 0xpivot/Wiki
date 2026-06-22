---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Its Importance in Web Security

JSON Web Tokens (JWTs) are a widely used method for securely transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA. JWTs are commonly used for authentication and information exchange due to their compact, URL-safe, and verifiable nature.

### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains the type of token and the signing algorithm used.
2. **Payload**: Contains the claims. Claims are statements about an entity (typically, the user) and additional data.
3. **Signature**: Used to verify the message wasn't changed along the way, and, in the case of tokens signed with a private key, to verify the sender.

The structure can be visualized as follows:

```mermaid
graph LR
    A[Header] --> B[Payload]
    B --> C[Signature]
```

### Example of a JWT

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJyb2xlcyI6WyJhZG1pbiJdfQ.5PnWZVU7K6oqQy8r0kD5X9Hr5v4b6X7B
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
    "iat": 1516239021,
    "roles": ["admin"]
  }
  ```

- **Signature**:
  ```plaintext
  5PnWZVU7K6oqQy8r0kD5X9Hr5v4b6X7B
  ```

### Importance of JWT in Authentication

JWTs are crucial in web applications because they allow stateless authentication. This means that the server does not need to store session information, making it easier to scale. However, this also introduces potential security risks if not implemented correctly.

---
<!-- nav -->
[[02-Introduction to JWT and Its Components|Introduction to JWT and Its Components]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/04-JSON Web Token (JWT) Overview|JSON Web Token (JWT) Overview]]
