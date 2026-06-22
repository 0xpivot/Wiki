---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Understanding Algorithm Confusion

### What is Algorithm Confusion?

Algorithm confusion happens when an attacker manipulates the algorithm field in the JWT header to trick the server into accepting a token signed with a different algorithm than intended. This can lead to unauthorized access if the server does not enforce strict validation of the signing algorithm.

### Why Algorithm Confusion Matters

Algorithm confusion attacks exploit the lack of proper validation of the signing algorithm. By changing the algorithm, an attacker can bypass the intended security measures and gain unauthorized access to resources.

### How Algorithm Confusion Works

The attacker modifies the `alg` field in the JWT header to use a different algorithm, typically one that does not require a secret key (like `none`). The server, expecting a specific algorithm, may accept the token without proper validation, leading to unauthorized access.

#### Example of Algorithm Confusion

Consider a JWT signed with `HS256`:

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

An attacker can change the `alg` field to `none`:

```json
{
  "header": {
    "alg": "none",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  },
  "signature": ""
}
```

If the server does not validate the algorithm, it may accept this token, leading to unauthorized access.

### Real-World Example: CVE-2017-15356

CVE-2017-15356 affected several libraries and frameworks that implemented JWT. The vulnerability allowed attackers to bypass authentication by manipulating the algorithm used to sign the token. This led to unauthorized access to sensitive resources.

---
<!-- nav -->
[[13-Step-by-Step Walkthrough|Step-by-Step Walkthrough]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[15-Understanding the Vulnerability|Understanding the Vulnerability]]
