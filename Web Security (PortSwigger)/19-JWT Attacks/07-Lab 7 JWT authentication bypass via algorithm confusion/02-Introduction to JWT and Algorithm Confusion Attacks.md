---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Algorithm Confusion Attacks

### What is JWT?
JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims to be transferred between two parties. They are typically used in web applications to securely transmit information between client and server. A JWT consists of three parts: the header, the payload, and the signature. These parts are Base64Url encoded and separated by dots (`.`).

#### Header
The header typically contains two parts: the type of the token, which is `JWT`, and the signing algorithm being used, such as `HS256` (HMAC SHA-256) or `RS256` (RSA SHA-256).

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### Payload
The payload contains the claims. Claims are statements about an entity (typically, the user) and additional data. There are three types of claims: registered, public, and private.

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

#### Signature
The signature is used to verify the integrity of the message. It is created using the header, the payload, a secret, and the algorithm specified in the header.

```plaintext
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

### Why JWT Matters
JWTs are widely used in web applications for authentication and authorization purposes. They provide a stateless mechanism for maintaining session information, which is particularly useful in distributed systems and microservices architectures.

### How JWT Works Under the Hood
When a user logs in, the server generates a JWT and sends it to the client. The client stores this token and includes it in subsequent requests to the server. The server verifies the token to ensure it has not been tampered with and that the user is authenticated.

### Algorithm Confusion Attack
An algorithm confusion attack occurs when an attacker manipulates the `alg` field in the JWT header to trick the server into using a different algorithm than intended. This can lead to unauthorized access if the server blindly trusts the value of the `alg` parameter.

### Real-World Example: CVE-2019-16759
In 2019, a vulnerability was discovered in the `jsonwebtoken` library for Node.js, where the library did not properly validate the `alg` field. An attacker could manipulate the `alg` field to use a weaker algorithm, leading to unauthorized access. This vulnerability was assigned the CVE identifier CVE-2019-16759.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/01-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[03-Introduction to JWT and Its Importance|Introduction to JWT and Its Importance]]
