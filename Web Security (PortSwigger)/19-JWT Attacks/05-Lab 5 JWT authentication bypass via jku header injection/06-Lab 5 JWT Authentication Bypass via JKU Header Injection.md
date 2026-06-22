---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Lab 5: JWT Authentication Bypass via JKU Header Injection

In this lab, we will explore how to exploit a JWT authentication system by injecting a custom `jku` header. We will assume that the previous attack vectors did not work, and we will focus on the `jku` header injection.

### Background

In the previous lab, we were able to exploit the application by injecting a `jwk` parameter. However, in this lab, we will attempt to inject the `jku` parameter. The `jku` header stands for JSON Web Key set URL and is used to specify a URL from which the server can fetch a key or a set of keys to verify the signature of the token.

If the application allows you to enter an arbitrary `jku` parameter and it actually accepts it without any verification, then you could add a URL in that parameter, which includes your own key set.

### Steps to Exploit the Vulnerability

1. **Identify the JWT Structure**: Analyze the structure of the JWT to understand its components.
2. **Inject the `jku` Header**: Modify the JWT to include a custom `jku` header pointing to a malicious JWKS URL.
3. **Create a Malicious JWKS**: Create a JWKS containing a custom key that you control.
4. **Sign the JWT**: Sign the JWT with your custom key and send it to the application.

### Example of Exploitation

Let's walk through an example of how to exploit this vulnerability.

#### Step 1: Identify the JWT Structure

Assume the original JWT looks like this:

```plaintext
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.eyJrIjp7ImtpZCI6IjEiLCJrdHkiOiJFUyIsImNydiI6IlAtMjU2IiwieCI6ImxhbGFsYWxhIiwieSI6ImxhbGFsYWxhIiwidXNlIjoic2lnIn19
```

#### Step 2: Inject the `jku` Header

Modify the JWT to include a custom `jku` header:

```plaintext
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImprdSI6Imh0dHBzOi8vbXlvdXNlci5jb20vamtxcyJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.eyJrIjp7ImtpZCI6IjEiLCJrdHkiOiJFUyIsImNydiI6IlAtMjU2IiwieCI6ImxhbGFsYWxhIiwieSI6ImxhbGFsYWxhIiwidXNlIjoic2lnIn19
```

#### Step 3: Create a Malicious JWKS

Create a JWKS containing a custom key that you control:

```json
{
  "keys": [
    {
      "kty": "EC",
      "crv": "P-256",
      "kid": "1",
      "x": "lalalala",
      "y": "lalalala",
      "use": "sig"
    }
  ]
}
```

Host this JWKS at a URL that you control, e.g., `https://myserver.com/jwks`.

#### Step 4: Sign the JWT

Sign the JWT with your custom key and send it to the application:

```plaintext
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImprdSI6Imh0dHBzOi8vbXlvdXNlci5jb20vamtxcyJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.eyJrIjp7ImtpZCI6IjEiLCJrdHkiOiJFUyIsImNydiI6IlAtMjU2IiwieCI6ImxhbGFsYWxhIiwieSI6ImxhbGFsYWxhIiwidXNlIjoic2lnIn19
```

### Real-World Examples

Recent real-world examples of JWT vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in the `jwt-go` library allowed attackers to bypass signature validation by using a `none` algorithm.
- **CVE-2021-22107**: A vulnerability in the `auth0/node-jsonwebtoken` library allowed attackers to bypass signature validation by using a `none` algorithm.

These vulnerabilities highlight the importance of proper validation and key management in JWT-based authentication systems.

### How to Prevent / Defend

To prevent and defend against JWT attacks, follow these best practices:

1. **Validate the Algorithm**: Ensure that the algorithm specified in the JWT header is valid and supported by the server.
2. **Validate the Key**: Ensure that the key used to sign the JWT is valid and trusted by the server.
3. **Use HTTPS**: Ensure that all communication between the client and the server is encrypted using HTTPS.
4. **Monitor and Log**: Monitor and log all JWT-related activities to detect and respond to potential attacks.

#### Secure Code Fix

Compare the vulnerable and secure versions of the code:

**Vulnerable Code**

```python
import jwt

def authenticate(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded["sub"]
    except jwt.exceptions.DecodeError:
        return None
```

**Secure Code**

```python
import jwt

def authenticate(token):
    try:
        decoded = jwt.decode(token, key="your-secret-key", algorithms=["HS256"])
        return decoded["sub"]
    except jwt.exceptions.DecodeError:
        return None
```

In the secure version, the `key` and `algorithms` parameters are explicitly set to ensure proper validation.

#### Configuration Hardening

Ensure that your JWT-related configurations are hardened:

- **Disable `none` Algorithm**: Ensure that the `none` algorithm is disabled in your JWT configuration.
- **Validate Keys**: Ensure that the keys used to sign JWTs are validated and trusted by the server.

### Conclusion

JWTs are a powerful tool for transmitting information between parties, but they also introduce security risks if not properly managed. By understanding the components of JWTs and the common attack vectors, you can better protect your applications from potential vulnerabilities.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on JWT authentication bypass.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing JWT attacks.
- **DVWA**: Offers a vulnerable web application for practicing various web security attacks, including JWT attacks.

By completing these labs, you can gain practical experience in identifying and defending against JWT vulnerabilities.

---
<!-- nav -->
[[05-JSON Web Tokens (JWT) Overview|JSON Web Tokens (JWT) Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/07-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]]
