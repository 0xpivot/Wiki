---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the `kid` parameter in JWT headers can be exploited for path traversal.**

The `kid` parameter in JWT headers is used to specify which key should be used to verify the signature of the token. If the server does not properly validate or sanitize the `kid` value, an attacker can manipulate it to point to arbitrary files on the server's filesystem. This is known as path traversal or directory traversal. By specifying a path that points to a known file (like `/dev/null`), an attacker can trick the server into using that file's contents as the key to verify the token. Since `/dev/null` is an empty file, the attacker can sign their modified token with an empty string, effectively bypassing the signature verification process.

**Q2. How would you exploit a JWT authentication bypass via the `kid` header path traversal in a lab environment?**

To exploit a JWT authentication bypass via the `kid` header path traversal, follow these steps:

1. **Identify the `kid` Parameter**: Use Burp Suite or similar tools to intercept and analyze the JWT token sent during a legitimate login attempt. Look for the `kid` parameter in the JWT header.

2. **Test Path Traversal Vulnerability**: Modify the `kid` parameter to include a path traversal sequence (e.g., `../../../../dev/null`) to point to a known file like `/dev/null`. Send the modified JWT token to the server and observe the response.

3. **Sign the Token with an Empty String**: If the server accepts the modified `kid` parameter, use a tool like the JWT Editor extension in Burp Suite to sign the token with an empty string. This can be achieved by using a base64-encoded null byte (`AA==`).

4. **Access Restricted Resources**: With the modified and signed JWT token, attempt to access restricted resources such as the admin panel. If successful, you can perform actions like deleting a specific user.

**Q3. Why is it important for the server to use a symmetric algorithm for this type of attack to succeed?**

For the JWT authentication bypass via the `kid` header path traversal to succeed, the server must use a symmetric algorithm to sign and verify the JWT token. Symmetric algorithms use the same key for both encryption and decryption. If the server uses a symmetric algorithm, an attacker can exploit the path traversal vulnerability to force the server to use a known file (like `/dev/null`) as the key. Since `/dev/null` is an empty file, the attacker can sign their modified token with an empty string, and the server will accept it because the signature matches. If the server uses an asymmetric algorithm (which requires a private key for signing and a public key for verification), this attack would not work because the attacker cannot obtain the private key.

**Q4. What recent real-world examples or CVEs demonstrate the exploitation of JWT authentication bypass via the `kid` header path traversal?**

One notable example is the CVE-2021-27905, which affected the Auth0 platform. Auth0 is a popular identity and access management service that uses JWTs for authentication. The vulnerability arose due to improper validation of the `kid` parameter, allowing attackers to perform path traversal and gain unauthorized access to sensitive resources. This CVE highlights the importance of proper input validation and secure coding practices to prevent such vulnerabilities.

**Q5. How can developers mitigate the risk of JWT authentication bypass via the `kid` header path traversal?**

Developers can mitigate the risk of JWT authentication bypass via the `kid` header path traversal by implementing the following security measures:

1. **Validate and Sanitize Input**: Ensure that the `kid` parameter is validated and sanitized to prevent path traversal attacks. Only allow predefined or trusted values for the `kid` parameter.

2. **Use Asymmetric Algorithms**: Preferably use asymmetric algorithms (such as RSA) for signing JWTs. This ensures that even if an attacker manipulates the `kid` parameter, they cannot sign the token without the private key.

3. **Implement Least Privilege Principle**: Restrict the permissions of the server process to minimize the risk of exposing sensitive files through path traversal attacks.

4. **Regular Audits and Penetration Testing**: Conduct regular security audits and penetration testing to identify and address potential vulnerabilities in JWT implementation.

By following these best practices, developers can significantly reduce the risk of JWT authentication bypass attacks.

---
<!-- nav -->
[[14-Understanding Path Traversal Attacks|Understanding Path Traversal Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]]
