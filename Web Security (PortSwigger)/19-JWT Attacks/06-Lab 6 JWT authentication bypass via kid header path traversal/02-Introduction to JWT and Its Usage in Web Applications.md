---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Its Usage in Web Applications

JSON Web Tokens (JWT) are a widely adopted standard for securely transmitting information between parties as a JSON object. They are particularly useful in web applications for managing user sessions and authenticating users. A JWT typically consists of three parts: the header, the payload, and the signature. Each part is Base64Url encoded and separated by dots (`.`).

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9hZG1pbiJ9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFQKMhU5Zk
```

This JWT can be broken down into three parts:

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm.
2. **Payload**: Contains claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing tampering.

### Example of a JWT Header and Payload

Here is an example of a JWT header and payload:

```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "iss": "https://example.com",
  "aud": "https://example.com/admin"
}
```

The `alg` field specifies the algorithm used to sign the token, and the `typ` field indicates that this is a JWT. The payload contains various claims, including the subject (`sub`), name (`name`), issued at time (`iat`), issuer (`iss`), and audience (`aud`).

### Importance of JWT in Web Security

JWTs are crucial in web security because they provide a way to securely transmit information between parties. They are often used for session management, where a user logs in once and receives a token that can be used for subsequent requests. This reduces the need for maintaining session state on the server, making the application more scalable and easier to manage.

However, JWTs also introduce potential security risks if not implemented correctly. One such risk is the use of the `kid` (key ID) header, which can be exploited through path traversal attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/01-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[03-JWT Attacks Overview|JWT Attacks Overview]]
