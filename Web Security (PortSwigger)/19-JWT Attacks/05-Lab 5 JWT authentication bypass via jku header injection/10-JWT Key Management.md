---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Key Management

One of the critical aspects of JWTs is the management of cryptographic keys used to sign and verify tokens. There are several ways to manage these keys, including:

1. **Symmetric Keys**: Both the issuer and the verifier share the same secret key.
2. **Asymmetric Keys**: The issuer uses a private key to sign the token, and the verifier uses the corresponding public key to verify the signature.

### Asymmetric Key Management

When using asymmetric keys, the public key is often made available through a JSON Web Key Set (JWKS). This set contains one or more JSON Web Keys (JWKs) that can be used to verify the signature of a JWT.

#### JSON Web Key Set (JWKS)

A JWKS is a JSON document containing one or more JWKs. Each JWK represents a cryptographic key and includes metadata about the key, such as its type, algorithm, and value.

### Example JWKS

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "1",
      "use": "sig",
      "n": "lalalala",
      "e": "AQAB"
    },
    {
      "kty": "EC",
      "crv": "P-256",
      "kid": "2",
      "x": "lalalala",
      "y": "lalalala",
      "use": "sig"
    }
  ]
}
```

In this example, the JWKS contains two keys: one RSA key and one EC key. Each key has a unique identifier (`kid`), which can be used to match the key with the token.

### JSON Web Key (JWK)

A JWK is a JSON representation of a cryptographic key. It includes fields such as `kty` (key type), `kid` (key ID), `use` (usage), and the actual key material.

### Example JWK

```json
{
  "kty": "RSA",
  "kid": "1",
  "use": "sig",
  "n": "lalalala",
  "e": "AQAB"
}
```

This JWK represents an RSA key with a modulus (`n`) and exponent (`e`). The `kid` field is used to identify the key within a JWKS.

---
<!-- nav -->
[[09-JWT Attack via `jku` Header Injection|JWT Attack via `jku` Header Injection]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[11-JWT Vulnerabilities and Attacks|JWT Vulnerabilities and Attacks]]
