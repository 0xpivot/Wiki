---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of algorithm confusion attacks in the context of JWT authentication.**

Algorithm confusion attacks involve manipulating the algorithm field (ALG parameter) in a JSON Web Token (JWT) to trick the server into using a different algorithm than intended for verifying the token's signature. Typically, the server expects an asymmetric algorithm (like RSA), but the attacker forces it to use a symmetric algorithm (like HMAC). This can be exploited if the server does not properly validate the algorithm used for signature verification.

**Q2. How would you exploit an algorithm confusion vulnerability in a JWT system without having the public key?**

To exploit an algorithm confusion vulnerability without the public key, follow these steps:

1. Obtain two different JWTs from the server.
2. Use a tool like `jwtforge.py` to derive the public key from these JWTs.
3. Modify the JWT payload to include administrative privileges.
4. Sign the modified JWT using the derived public key with a symmetric algorithm.
5. Send the modified JWT to the server to gain unauthorized access.

**Q3. Why is it important to validate the algorithm field in JWTs?**

Validating the algorithm field in JWTs is crucial because it ensures that the server uses the correct cryptographic algorithm for verifying the token's signature. Failing to validate this field can lead to algorithm confusion attacks, where an attacker tricks the server into using a different algorithm, potentially allowing unauthorized access. Proper validation prevents such vulnerabilities and maintains the integrity and security of the authentication process.

**Q4. How does the `jwtforge.py` tool help in extracting the public key from JWTs?**

The `jwtforge.py` tool helps in extracting the public key from JWTs by leveraging mathematical properties of RSA encryption. Given two signed JWTs, the tool attempts to derive the public key by solving equations related to the RSA encryption process. Specifically, it exploits the deterministic nature of the padding scheme and the known public exponent to calculate potential public keys. Once the public key is derived, it can be used to perform algorithm confusion attacks.

**Q5. What recent real-world example demonstrates the risk of algorithm confusion attacks?**

A notable example is the case of the popular software development platform GitHub, which was affected by a vulnerability related to algorithm confusion in its JWT implementation. In 2020, researchers discovered that GitHub's API allowed attackers to manipulate the algorithm field in JWTs, leading to unauthorized access. This incident highlights the importance of validating the algorithm field and ensuring proper cryptographic practices to prevent such vulnerabilities.

**Q6. How would you configure a JWT system to mitigate algorithm confusion attacks?**

To mitigate algorithm confusion attacks, configure the JWT system as follows:

1. **Validate Algorithm Field**: Ensure the server validates the algorithm field in the JWT header to match the expected algorithm.
2. **Use Strong Algorithms**: Prefer strong, well-established cryptographic algorithms like RS256 over weaker ones.
3. **Public Key Management**: Securely manage public keys and ensure they are not exposed unnecessarily.
4. **Regular Audits**: Conduct regular security audits and penetration testing to identify and fix vulnerabilities.
5. **Update Dependencies**: Keep all cryptographic libraries and dependencies up-to-date to benefit from security patches and improvements.

**Q7. What steps should be taken to ensure secure JWT usage in web applications?**

To ensure secure JWT usage in web applications, follow these best practices:

1. **Strong Key Management**: Use strong, well-protected keys for signing and verifying JWTs.
2. **Algorithm Validation**: Always validate the algorithm field in JWTs to prevent algorithm confusion attacks.
3. **Secure Transmission**: Transmit JWTs securely over HTTPS to prevent interception.
4. **Short Expiry Times**: Set short expiry times for JWTs to limit their validity period.
5. **Regular Updates**: Regularly update cryptographic libraries and dependencies to patch known vulnerabilities.
6. **Audit and Monitoring**: Implement logging and monitoring to detect and respond to suspicious activities involving JWTs.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/16-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]]
