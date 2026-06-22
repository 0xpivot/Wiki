---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Its Components

JSON Web Tokens (JWTs) are a widely used method for securely transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed using a secret key or a public/private key pair. JWTs consist of three parts: the header, the payload, and the signature.

### Header

The header typically consists of two parts: the type of the token, which is `JWT`, and the signing algorithm being used, such as `HS256` or `RS256`. Here is an example of a JWT header:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload

The payload contains the claims. Claims are statements about an entity (typically, the user) and additional data. There are three types of claims: registered, public, and private. Registered claims are a set of predefined claims that are not mandatory but recommended to provide a level of interoperability among different systems. Public claims can be defined at will by those using JWTs, but to avoid collisions, they should be defined in the `https://www.iab.com/` namespace. Private claims are custom claims created to share information between parties that agree on using them.

Here is an example of a JWT payload:

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

### Signature

The signature is used to verify the message wasn't changed along the way, and, in the case of tokens signed with a private key, it can also verify that the sender of the JWT is who it says it is. To create the signature, you take the encoded header, the encoded payload, a secret, and the algorithm specified in the header, and sign the combination of these three.

Here is an example of a JWT signature:

```text
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

---
<!-- nav -->
[[02-Introduction to JWT Authentication Bypass via Weak Signing Key|Introduction to JWT Authentication Bypass via Weak Signing Key]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[04-How to Prevent  Defend Against Weak JWT Keys|How to Prevent  Defend Against Weak JWT Keys]]
