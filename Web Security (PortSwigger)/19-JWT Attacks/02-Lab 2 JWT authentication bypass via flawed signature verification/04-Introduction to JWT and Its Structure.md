---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Its Structure

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs are often used for authentication and information exchange due to their compact, URL-safe, and verifiable nature.

### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing tampering and verifying the sender.

The structure can be visualized using a mermaid diagram:

```mermaid
graph TD;
    A[Header] --> B[Payload];
    B --> C[Signature];
```

### Example of a JWT

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
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

### Importance of JWT Signature Verification

The signature is crucial for ensuring the authenticity and integrity of the JWT. Without proper verification, an attacker could manipulate the token, leading to unauthorized access or other security issues.

---
<!-- nav -->
[[03-Introduction to JWT Authentication Bypass via Flawed Signature Verification|Introduction to JWT Authentication Bypass via Flawed Signature Verification]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[05-JSON Web Token (JWT) Overview|JSON Web Token (JWT) Overview]]
