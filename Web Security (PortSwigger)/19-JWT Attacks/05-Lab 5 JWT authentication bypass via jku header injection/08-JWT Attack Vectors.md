---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attack Vectors

There are several attack vectors that can be exploited to compromise JWT-based authentication systems. Some of the most common ones include:

1. **None Algorithm Attack**: Exploiting the `none` algorithm to bypass signature validation.
2. **JWK Injection**: Injecting a custom JWK to sign the token with a different key.
3. **JKU Header Injection**: Injecting a custom `jku` header to specify a malicious JWKS URL.

### None Algorithm Attack

In this attack, the attacker modifies the `alg` field in the JWT header to `"none"`, effectively bypassing signature validation. The server may accept the token if it does not properly validate the algorithm.

#### Example of None Algorithm Attack

```plaintext
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.
```

Here, the `alg` field is set to `"none"`, and the signature is empty. The server may accept this token if it does not enforce proper validation.

### JWK Injection

In this attack, the attacker injects a custom JWK into the JWT payload to sign the token with a different key. This can be done by modifying the `jwk` parameter in the JWT.

#### Example of JWK Injection

```plaintext
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyLCJqdGkiOiJodHRwczovL2V4YW1wbGUuY29tL2p3ayJ9.eyJrIjp7ImtpZCI6IjEiLCJrdHkiOiJFUyIsImNydiI6IlAtMjU2IiwieCI6ImxhbGFsYWxhIiwieSI6ImxhbGFsYWxhIiwidXNlIjoic2lnIn19
```

Here, the `jwk` parameter is injected into the payload, specifying a custom EC key. The server may accept this token if it does not properly validate the key.

### JKU Header Injection

In this attack, the attacker injects a custom `jku` header into the JWT to specify a malicious JWKS URL. The server may fetch the key from this URL and use it to verify the signature of the token.

#### Example of JKU Header Injection

```plaintext
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImprdSI6Imh0dHBzOi8vbXlvdXNlci5jb20vamtxcyJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.eyJrIjp7ImtpZCI6IjEiLCJrdHkiOiJFUyIsImNydiI6IlAtMjU2IiwieCI6ImxhbGFsYWxhIiwieSI6ImxhbGFsYWxhIiwidXNlIjoic2lnIn19
```

Here, the `jku` header is injected into the JWT, specifying a malicious JWKS URL. The server may fetch the key from this URL and use it to verify the signature of the token.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/07-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[09-JWT Attack via `jku` Header Injection|JWT Attack via `jku` Header Injection]]
