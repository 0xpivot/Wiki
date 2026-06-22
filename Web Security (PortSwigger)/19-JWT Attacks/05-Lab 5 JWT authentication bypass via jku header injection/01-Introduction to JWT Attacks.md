---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Attacks

In this section, we will delve into the intricacies of JSON Web Tokens (JWTs) and explore a specific type of attack known as JWT authentication bypass via `jku` header injection. This attack exploits vulnerabilities in the way JWTs are validated and can lead to unauthorized access to sensitive resources. We will cover the necessary background, the mechanics of the attack, real-world examples, and most importantly, how to defend against such vulnerabilities.

### What is a JSON Web Token (JWT)?

A JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It allows you to encode information in a JSON object and sign it cryptographically. JWTs are commonly used for authentication and information exchange in web applications.

#### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token by verifying that it was issued by a trusted party.

Here is an example of a JWT:

```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking down the components:

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

JWTs are widely used because they provide a simple and secure method for transmitting information between parties as a JSON object. They are particularly useful in stateless environments like microservices architectures, where maintaining session state across multiple services can be challenging.

However, JWTs also introduce potential security risks if not implemented correctly. One such risk is the `jku` header injection attack, which we will explore in detail.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[02-Introduction to JWT and Its Components|Introduction to JWT and Its Components]]
