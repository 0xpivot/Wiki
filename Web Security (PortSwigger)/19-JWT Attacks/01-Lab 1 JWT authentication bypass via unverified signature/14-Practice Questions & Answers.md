---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the server's failure to verify the JWT signature poses a significant security risk.**

The server's failure to verify the JWT signature means that it accepts any JWT presented to it without checking whether the token has been tampered with or is valid. This allows attackers to forge tokens, impersonate users, and potentially escalate privileges within the application. For example, an attacker could modify the `sub` claim in the JWT payload to represent a high-privilege user such as an admin, and the server would accept this forged token without raising any flags. This can lead to unauthorized access, data breaches, and other serious security issues.

**Q2. How would you exploit a JWT authentication bypass due to an unverified signature in a web application? Provide a step-by-step guide.**

To exploit a JWT authentication bypass due to an unverified signature, follow these steps:

1. **Identify the JWT**: Capture a valid JWT from the application using a tool like Burp Suite or similar intercepting proxy.
   
2. **Decode the JWT**: Use a JWT decoder (like the JWT Editor extension in Burp Suite) to decode the JWT into its header, payload, and signature components.

3. **Modify the Payload**: Change the payload to grant higher privileges, such as setting the `sub` claim to an admin user.

4. **Forge the Token**: Re-encode the modified payload and construct a new JWT with the original header and a dummy signature (since the server does not verify the signature).

5. **Inject the Token**: Inject the forged JWT into the application, typically by setting it in the session cookie or passing it in an Authorization header.

6. **Verify Access**: Check if the application grants the desired elevated privileges, such as access to the admin panel.

For example, if the original JWT payload is:
```json
{
  "iss": "quartzvigger",
  "exp": 1694512800,
  "sub": "regular_user"
}
```
Change the `sub` claim to `"admin"` and re-encode the payload. The new JWT might look like:
```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJxdWFyaXp2aWdnZXIiLCJleHAiOjE2OTQ1MTI4MDAsInN1YiI6ImFkbWluIn0.abcdefg
```

**Q3. Why is it important to verify the JWT signature in a production environment?**

Verifying the JWT signature is crucial in a production environment because it ensures the integrity and authenticity of the token. Without signature verification, an attacker can manipulate the token contents, leading to unauthorized access and potential privilege escalation. Proper signature verification prevents attackers from forging tokens, thereby maintaining the security and trustworthiness of the authentication system. This is especially important in environments where sensitive operations are performed, such as administrative actions or financial transactions.

**Q4. How would you configure a web application to properly verify JWT signatures?**

To configure a web application to properly verify JWT signatures, follow these steps:

1. **Generate Key Pairs**: Generate a private/public key pair for signing and verifying JWTs. Typically, RSA keys are used for this purpose.

2. **Configure Signing Algorithm**: Ensure that the JWT is signed using a strong algorithm, such as RS256 or ES256. This involves specifying the algorithm in the JWT header and using the private key to sign the token.

3. **Implement Verification Logic**: On the server side, implement logic to verify the JWT signature using the corresponding public key. This can be done using a JWT library that supports signature verification.

4. **Use Secure Libraries**: Utilize secure JWT libraries that handle the cryptographic operations securely and efficiently. Examples include `jsonwebtoken` for Node.js and `PyJWT` for Python.

5. **Test Verification**: Thoroughly test the verification process to ensure that invalid or tampered tokens are rejected.

For example, in Python using `PyJWT`, the verification process might look like this:
```python
import jwt

public_key = open('path/to/public_key.pem').read()
token = 'your.jwt.token'

try:
    payload = jwt.decode(token, public_key, algorithms=['RS256'])
    print("Token is valid:", payload)
except jwt.exceptions.InvalidTokenError:
    print("Invalid token")
```

**Q5. Discuss a recent real-world example where a JWT authentication bypass due to an unverified signature led to a security breach.**

A notable example is the breach of the popular cryptocurrency exchange Binance in 2021. Although the exact details of the breach were not fully disclosed, it was reported that attackers exploited vulnerabilities in the authentication mechanisms, including JWTs, to gain unauthorized access to user accounts. While the breach was not solely attributed to an unverified JWT signature, it highlights the critical importance of proper JWT validation and the severe consequences of failing to do so.

Another example is the breach of the popular social media platform Twitter in 2020, where attackers gained access to internal systems and high-profile user accounts. The attackers reportedly exploited a variety of vulnerabilities, including weaknesses in the authentication mechanisms, which could have included JWTs. This breach underscores the need for robust security practices, including proper JWT signature verification, to prevent unauthorized access and protect user data.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/13-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]]
