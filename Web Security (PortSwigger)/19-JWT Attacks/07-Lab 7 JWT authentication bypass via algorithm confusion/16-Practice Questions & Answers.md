---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of algorithm confusion in JWT attacks.**

Algorithm confusion, also known as key confusion, is a type of attack where an attacker forces the server to verify the signature of a JSON Web Token (JWT) using a different algorithm than the one used by the developers. Typically, the server uses an asymmetric algorithm (like RSA), but the attacker manipulates the `alg` parameter in the JWT header to use a symmetric algorithm (like HS-256). Since the public key is often publicly available, the attacker can use it to sign the token, leading to unauthorized access if the server does not properly validate the algorithm.

**Q2. How would you exploit an algorithm confusion vulnerability in a JWT-based system?**

To exploit an algorithm confusion vulnerability, follow these steps:

1. **Identify the Public Key**: Find the public key used by the server. Often, the public key is exposed via a standard endpoint like `/jwks.json`.

2. **Modify the JWT**: Change the `alg` parameter in the JWT header to a symmetric algorithm (e.g., HS-256).

3. **Sign the JWT**: Use the public key to sign the modified JWT. This involves encoding the public key in Base64 and using it as the symmetric key.

4. **Inject the Modified JWT**: Send the modified JWT to the server. If the server blindly trusts the `alg` parameter, it will use the public key to verify the token, allowing unauthorized access.

Here’s an example payload:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "administrator",
    "dir": "/admin"
  }
}
```

Sign this payload with the public key encoded in Base64.

**Q3. Why is it important to validate the `alg` parameter in JWTs?**

Validating the `alg` parameter is crucial because it ensures that the server uses the correct algorithm to verify the JWT signature. If the server does not validate the `alg` parameter, an attacker can manipulate it to use a different algorithm, leading to unauthorized access. For instance, changing the algorithm from RSA to HS-256 can allow an attacker to use the public key to sign the token, bypassing the intended security measures.

**Q4. What recent real-world examples demonstrate the risks of algorithm confusion in JWTs?**

One notable example is the OAuth 2.0 authorization code injection vulnerability (CVE-2020-14182). This vulnerability allowed attackers to inject a malicious authorization code into a JWT, leading to unauthorized access. Although this specific vulnerability involved authorization codes rather than direct JWT manipulation, it highlights the importance of validating all aspects of JWTs, including the `alg` parameter.

Another example is the widespread use of vulnerable libraries like `jsonwebtoken` in Node.js applications. These libraries did not enforce strict validation of the `alg` parameter, making them susceptible to algorithm confusion attacks. Developers had to update their libraries and implement additional validation to mitigate these risks.

**Q5. How would you configure a JWT library to prevent algorithm confusion attacks?**

To prevent algorithm confusion attacks, configure the JWT library to enforce strict validation of the `alg` parameter. Here are some best practices:

1. **Whitelist Allowed Algorithms**: Only allow specific algorithms that are known to be secure and appropriate for your application. For example, if you are using RSA, ensure that only RSA algorithms are accepted.

2. **Strict Validation**: Ensure that the library validates the `alg` parameter against a predefined list of allowed algorithms. Reject any JWTs that use unsupported or unexpected algorithms.

3. **Use Secure Libraries**: Use well-maintained and secure JWT libraries that enforce strict validation. For example, in Node.js, use `jwt-decode` for decoding and `jsonwebtoken` with strict configuration.

Here’s an example configuration in Node.js:

```javascript
const jwt = require('jsonwebtoken');

const verifyToken = (token, publicKey) => {
  try {
    const decoded = jwt.verify(token, publicKey, { algorithms: ['RS256'] });
    return decoded;
  } catch (err) {
    console.error('Invalid token:', err);
    return null;
  }
};
```

This configuration ensures that only JWTs with the `RS256` algorithm are accepted, preventing algorithm confusion attacks.

**Q6. Explain how the public key exposure can contribute to algorithm confusion attacks.**

Public key exposure can contribute to algorithm confusion attacks because the public key is often used in both asymmetric and symmetric encryption contexts. When the public key is exposed, an attacker can use it to sign a JWT with a symmetric algorithm (like HS-256), even though the original implementation intended to use an asymmetric algorithm (like RSA).

For example, if the server exposes the public key via `/jwks.json`, an attacker can retrieve this key and use it to sign a JWT with a symmetric algorithm. If the server does not validate the `alg` parameter, it may accept this modified JWT, leading to unauthorized access.

To mitigate this risk, ensure that the server strictly validates the `alg` parameter and only accepts JWTs signed with the intended algorithm. Additionally, avoid exposing sensitive information like the public key unless absolutely necessary.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/15-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]]
