---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the JKU parameter can be exploited in a JWT authentication bypass.**

The JKU (JSON Web Key Set URL) parameter in a JWT can be exploited if the server does not validate the URL properly. An attacker can inject a URL pointing to their own server containing a public key. When the server attempts to verify the JWT signature using the public key fetched from the injected URL, it can be tricked into accepting a forged token signed with the corresponding private key. This allows unauthorized access to protected resources.

**Q2. How would you exploit the JKU parameter to gain administrative access in a JWT-based system?**

To exploit the JKU parameter for administrative access:

1. Generate an RSA key pair.
2. Upload the public key to an exploit server in the required JWK format.
3. Modify the JWT to include the JKU parameter pointing to the exploit server URL.
4. Change the subject claim to "admin".
5. Sign the modified JWT with the private key corresponding to the uploaded public key.
6. Submit the forged JWT to the server, which will fetch the public key from the JKU URL and verify the signature, granting administrative access.

**Q3. Why is it important for a server to validate the JKU parameter before fetching the key set?**

Validating the JKU parameter is crucial because it prevents attackers from injecting malicious URLs. If the server fetches a key set from an untrusted source, it can be tricked into accepting forged JWTs signed with a key controlled by the attacker. This can lead to unauthorized access, privilege escalation, and other security breaches. Proper validation ensures that only trusted key sets are used for verifying JWT signatures.

**Q4. What recent real-world examples or CVEs demonstrate the risks associated with improper validation of the JKU parameter in JWTs?**

One notable example is the CVE-2020-14774, which affected the Auth0 service. Due to improper validation of the `jku` parameter, attackers could inject a malicious URL to provide a custom public key, allowing them to forge JWTs and impersonate users. This vulnerability highlights the importance of strict validation of external parameters in JWT-based systems to prevent such exploits.

**Q5. How can you configure a JWT-based system to securely handle the JKU parameter?**

To securely handle the JKU parameter in a JWT-based system:

1. Validate that the URL in the JKU parameter points to a trusted domain.
2. Implement rate limiting and logging for requests involving the JKU parameter to detect and mitigate potential abuse.
3. Use a secure connection (HTTPS) to fetch the key set from the specified URL.
4. Cache the fetched key set to reduce the risk of replay attacks and improve performance.
5. Regularly audit and update the list of trusted domains to ensure only authorized sources are used.

By implementing these measures, the system can minimize the risk of exploitation through the JKU parameter.

---
<!-- nav -->
[[12-Understanding the `jku` Header Injection Attack|Understanding the `jku` Header Injection Attack]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]]
