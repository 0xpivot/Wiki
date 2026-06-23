---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Understanding the Attack

### Accessing the JWKS Endpoint
To perform an algorithm confusion attack, the attacker first needs to access the JWKS (JSON Web Key Set) endpoint. This endpoint provides the public keys used to verify the signatures of JWTs.

```http
GET /.well-known/jwks.json HTTP/1.1
Host: example.com
```

The response from the server will contain the public keys in JSON format:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "123456",
      "use": "sig",
      "n": "lGc...",
      "e": "AQAB"
    }
  ]
}
```

### Extracting the Public Key
From the JWKS response, the attacker extracts the public key. This key is used to sign the JWT with a symmetric algorithm instead of the asymmetric one originally intended.

### Modifying the JWT Header
The attacker modifies the `alg` field in the JWT header to use a symmetric algorithm, such as `HS256`.

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Signing the Token
Using the extracted public key, the attacker signs the modified JWT. This is done using a tool like the JWT Editor in Burp Suite.

### Testing the Attack
The attacker sends the modified JWT to the server and checks if the server accepts it. If the server blindly trusts the `alg` parameter, it may accept the token and grant unauthorized access.

---
<!-- nav -->
[[13-Understanding JWT Algorithms|Understanding JWT Algorithms]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/15-Conclusion|Conclusion]]
