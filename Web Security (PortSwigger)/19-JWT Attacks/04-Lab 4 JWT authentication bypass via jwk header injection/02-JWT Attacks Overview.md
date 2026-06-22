---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attacks Overview

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. They are compact, URL-safe means of representing claims to be transferred between two parties. JWTs consist of three parts separated by dots (`.`): a header, a payload, and a signature. The header typically consists of two parts: the type of the token, which is `JWT`, and the signing algorithm being used, such as HMAC SHA256 or RSA.

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTEwMjF9.TJVA95OrM7E2cBjhpJOMIbRhx8soQMK1EhhMK8LH7AA
```

This JWT can be broken down into three parts:

1. **Header**: 
    ```
    {
      "alg": "HS256",
      "typ": "JWT"
    }
    ```

2. **Payload**:
    ```
    {
      "sub": "1234567890",
      "name": "John Doe",
      "iat": 1516310021,
      "exp": 1516311021
    }
    ```

3. **Signature**:
    ```
    TJVA95OrM7E2cBjhpJOMIbRhx8soQMK1EhhMK8LH7AA
    ```

The signature is created by taking the encoded header, the encoded payload, a secret, and the algorithm specified in the header, and signing them.

### Vulnerabilities in JWTs

JWTs can be vulnerable to several types of attacks, including:

- **None Algorithm Attack**
- **JWK Header Injection**
- **Token Replay Attacks**
- **Weak Signature Algorithms**

In this chapter, we will focus on the **JWK Header Injection** attack, which was exploited in the lab exercise mentioned in the transcript.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/01-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/00-Overview|Overview]] | [[03-How to Prevent  Defend Against JWK Header Injection|How to Prevent  Defend Against JWK Header Injection]]
