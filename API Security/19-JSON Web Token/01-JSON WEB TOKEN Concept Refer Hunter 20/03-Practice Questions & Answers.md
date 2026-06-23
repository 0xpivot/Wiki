---
course: API Security
topic: JSON Web Token
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the structure of a JSON Web Token (JWT).**

A JSON Web Token (JWT) consists of three parts separated by dots (.). These parts are:

1. **Header**: This contains the type of token, which is JWT, and the signing algorithm being used, such as HMAC SHA256 or RSA.
2. **Payload**: This contains the claims. Claims are statements about an entity (typically, the user) and additional data. There are three types of claims: registered, public, and private.
3. **Signature**: This is used to verify the message wasn't changed along the way, and, in the case of tokens signed with a private key, it can also verify that the sender of the JWT is who it says it is.

For example, a JWT might look like this: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

**Q2. How can JWTs be exploited if weak keys are used?**

If weak keys are used in JWTs, they can be vulnerable to brute-force attacks. An attacker can attempt to guess the secret key used to sign the JWT. If the key is weak (e.g., a simple string), the attacker has a higher chance of successfully guessing the key. Once the key is known, the attacker can modify the payload of the JWT and generate a new signature, effectively impersonating a legitimate user.

For example, if a JWT uses the HS256 algorithm and the secret key is "secret", an attacker can use tools like `jwtcrack` to brute-force the key and then modify the payload to gain unauthorized access.

**Q3. What are some common attacks against JWTs and how can they be mitigated?**

Some common attacks against JWTs include:

1. **Brute-forcing the secret key**: If the key is weak, attackers can use brute-force methods to guess the key.
   - **Mitigation**: Use strong, randomly generated keys and ensure they are kept secure.

2. **Token manipulation**: Attackers can modify the payload of a JWT and generate a new signature if they know the secret key.
   - **Mitigation**: Use asymmetric encryption (RSA) instead of symmetric encryption (HMAC) to prevent attackers from generating valid signatures without the private key.

3. **Expired token reuse**: Some systems do not properly check the expiration time of JWTs.
   - **Mitigation**: Ensure that the expiration time (`exp`) claim is checked on the server side before accepting the token.

4. **None algorithm attack**: Some implementations allow the use of the "none" algorithm, which means no signature is required.
   - **Mitigation**: Disable support for the "none" algorithm in your JWT implementation.

**Q4. How does the JWT signature protect the integrity of the message?**

The JWT signature ensures the integrity of the message by verifying that the message has not been tampered with during transmission. When a JWT is created, a signature is generated using the header and payload, combined with a secret key or a private/public key pair. This signature is appended to the end of the JWT.

When the JWT is received, the recipient recomputes the signature using the same method and compares it to the signature included in the JWT. If the signatures match, the message is considered authentic and unaltered. If they do not match, the message has been tampered with, and the JWT should be rejected.

For example, if an attacker modifies the payload of a JWT, the recomputed signature will not match the original signature, indicating that the message has been altered.

**Q5. Describe a recent real-world example where JWT vulnerabilities were exploited.**

One notable example is the OAuth 2.0 and OpenID Connect vulnerability (CVE-2020-14720), also known as "OIDC nonce bypass". This vulnerability allowed attackers to bypass the nonce validation in OAuth 2.0 and OpenID Connect flows, leading to potential session hijacking.

In this scenario, the attacker could intercept the authorization code and use it to obtain an ID token without proper nonce validation. The nonce is a random value that should be unique for each authorization request and is used to prevent replay attacks. However, due to the vulnerability, the nonce was not properly validated, allowing the attacker to reuse the authorization code and obtain a valid JWT.

To mitigate such vulnerabilities, it is crucial to implement proper nonce validation and ensure that all security measures specified in the OAuth 2.0 and OpenID Connect standards are followed.

---
<!-- nav -->
[[API Security/19-JSON Web Token/01-JSON WEB TOKEN Concept Refer Hunter 20/02-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]] | [[API Security/19-JSON Web Token/01-JSON WEB TOKEN Concept Refer Hunter 20/00-Overview|Overview]]
