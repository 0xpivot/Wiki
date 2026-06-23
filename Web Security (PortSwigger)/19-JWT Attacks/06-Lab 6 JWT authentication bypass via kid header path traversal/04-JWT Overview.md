---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Overview

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs consist of three parts: the header, the payload, and the signature. Each part is Base64Url encoded and separated by dots (`.`).

### Header

The header typically consists of two parts: the type of the token, which is `JWT`, and the signing algorithm being used, such as `HS256` (HMAC SHA-256).

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload

The payload contains claims. Claims are statements about an entity (typically, the user) and additional data. There are three types of claims:

- **Registered claims**: These are a set of predefined claims such as `iss` (issuer), `exp` (expiration time), `sub` (subject), etc.
- **Public claims**: These can be defined at will by those using JWTs. But to avoid collisions, they should be defined in the IANA JSON Web Token Registry or be defined as a URI that contains a collision-resistant namespace.
- **Private claims**: These are custom claims created to share information between parties that agree on using them.

Example payload:

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

### Signature

The signature is used to verify the message wasn’t changed along the way, and, in the case of tokens signed with a private key, it can also verify that the sender of the JWT is who it says it is.

To create the signature, you take the encoded header, the encoded payload, a secret, the algorithm specified in the header, and sign the header and payload, producing a signature.

```plaintext
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

### Example JWT

A complete JWT might look like this:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Vulnerabilities in JWTs

JWTs can be vulnerable to various attacks, including:

- **Signature Bypass**: An attacker might manipulate the JWT to bypass the signature validation.
- **Algorithm Confusion**: An attacker might change the algorithm used to sign the JWT.
- **Path Traversal**: An attacker might exploit vulnerabilities in the JWT parsing logic to read arbitrary files.

---
<!-- nav -->
[[03-JWT Attacks Overview|JWT Attacks Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[05-Crafting the Malicious JWT|Crafting the Malicious JWT]]
