---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Its Components

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. They are compact, URL-safe means of representing claims to be transferred between two parties. JWTs consist of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Used to verify the integrity of the message and ensure that the token was not tampered with.

### Example of a JWT

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

This JWT consists of three parts:

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
      "iat": 1516239022
    }
    ```

3. **Signature**:
    ```plaintext
    SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
    ```

The signature is created using the encoded header, the encoded payload, a secret, and the algorithm specified in the header.

### Why JWTs Matter

JWTs are crucial in web applications because they provide a way to securely transmit information between parties. They are often used for authentication and authorization purposes, allowing users to access resources based on their identity and permissions.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/01-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[03-Introduction to JWT and Its Importance in Web Security|Introduction to JWT and Its Importance in Web Security]]
