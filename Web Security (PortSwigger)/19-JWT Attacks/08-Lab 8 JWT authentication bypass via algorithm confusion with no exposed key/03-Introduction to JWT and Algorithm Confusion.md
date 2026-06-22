---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Algorithm Confusion

### What is JWT?

JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It allows you to encode information in a JSON object and sign it cryptographically. This encoded information can be used to verify the integrity of the data and ensure that the sender is who they claim to be.

A typical JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the authenticity of the token by verifying that it hasn't been tampered with.

### Why JWT Matters

JWTs are widely used in web applications for authentication and authorization purposes. They provide a way to securely transmit information between parties as a JSON object. The compactness and ease of parsing make JWTs popular for stateless authentication mechanisms.

### How JWT Works Under the Hood

When a user logs in, the server generates a JWT and sends it back to the client. The client stores this token and includes it in the `Authorization` header of subsequent requests. The server verifies the token and extracts the claims to determine the user's identity and permissions.

#### Example of a JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  },
  "signature": "dJ3Rr...your_signature_here"
}
```

### Algorithm Confusion Attack

Algorithm confusion occurs when a JWT is signed using a different algorithm than what the server expects. This can lead to vulnerabilities if the server does not properly validate the algorithm used to sign the token.

### Real-World Examples

One notable real-world example of an algorithm confusion attack is the CVE-2017-15356, which affected several libraries and frameworks that implemented JWT. This vulnerability allowed attackers to bypass authentication by manipulating the algorithm used to sign the token.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/02-Introduction to JWT and Algorithm Confusion Attacks|Introduction to JWT and Algorithm Confusion Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/04-JSON Web Token (JWT) Overview|JSON Web Token (JWT) Overview]]
