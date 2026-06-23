---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Path Traversal via KID Parameter

One specific vulnerability in JWTs is the manipulation of the `kid` (key ID) parameter to perform path traversal attacks. This occurs when the server uses the `kid` parameter to determine which cryptographic key to use for verifying the token's signature, and the `kid` value is not properly validated.

### Understanding the `kid` Parameter

The `kid` parameter is used to identify which key should be used to verify the signature of the JWT. The JWS (JSON Web Signature) specification does not define a concrete structure for this ID; it can be any arbitrary string chosen by the developer. However, if this parameter is vulnerable to directory traversal, an attacker could potentially trick the server into using an arbitrary file on the server's filesystem as the key to sign the token.

### Example Scenario

Consider a scenario where a server uses multiple cryptographic keys to sign different types of data. The server might use the `kid` parameter to identify which key to use. If the `kid` parameter is not properly validated, an attacker could manipulate it to perform path traversal.

#### Attacker's Goal

The attacker's goal is to make the server use a file that they control as the key to verify the token's signature. This can be achieved by manipulating the `kid` parameter to point to a file on the server's filesystem.

### Real-World Example

A real-world example of this vulnerability can be found in the CVE-2021-21315, where a path traversal vulnerability in the `kid` parameter allowed attackers to bypass authentication in certain applications.

### Exploitation Steps

1. **Identify the JWT**: Obtain a valid JWT from the application.
2. **Manipulate the `kid` Parameter**: Modify the `kid` parameter to point to a file on the server's filesystem.
3. **Forge the Signature**: Use the contents of the file to forge the signature of the JWT.

#### Step-by-Step Exploitation

1. **Obtain a Valid JWT**:
    ```http
    GET /api/user HTTP/1.1
    Host: example.com
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJQb3J0c2dpdXIifQ.5vKJkqDQyOJhVWJ6n9HrB05o7zj7yTgP5f8Xj9J4
    ```

2. **Modify the `kid` Parameter**:
    ```json
    {
      "alg": "HS256",
      "typ": "JWT",
      "kid": "/etc/passwd"
    }
    ```

3. **Forge the Signature**:
    - Decode the header and payload.
    - Read the contents of `/etc/passwd`.
    - Use the contents of `/etc/passwd` to forge the signature.

### Mermaid Diagram

```mermaid
sequenceDiagram
    participant User
    participant Server
    participant Attacker
    User->>Server: Request JWT
    Server-->>User: JWT
    Attacker->>Attacker: Modify kid to /etc/passwd
    Attacker->>Server: Send modified JWT
    Server-->>Attacker: Response based on forged JWT
```

### Detection and Prevention

#### How to Detect

- **Logging**: Monitor logs for unusual `kid` values.
- **Auditing**: Regularly audit JWT configurations and usage patterns.
- **Security Scanning**: Use tools like Burp Suite, OWASP ZAP, or static analysis tools to detect potential vulnerabilities.

#### How to Prevent

1. **Validate `kid` Parameter**:
    - Ensure the `kid` parameter is validated against a whitelist of allowed values.
    - Use a secure method to map `kid` values to keys.

2. **Secure Configuration**:
    - Ensure the server does not allow path traversal in the `kid` parameter.
    - Harden the server configuration to prevent unauthorized access to sensitive files.

3. **Use Strong Algorithms**:
    - Use strong cryptographic algorithms like `RS256` or `ES256` instead of `HS256`.

4. **Regular Audits**:
    - Perform regular security audits and penetration testing to identify and mitigate vulnerabilities.

### Secure Code Example

#### Vulnerable Code

```python
import jwt

def validate_jwt(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        kid = decoded.get("kid")
        if kid:
            key = open(kid, "rb").read()
            jwt.decode(token, key)
    except jwt.exceptions.DecodeError:
        return False
    return True
```

#### Secure Code

```python
import jwt

def validate_jwt(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        kid = decoded.get("kid")
        if kid and kid in ALLOWED_KIDS:
            key = open(ALLOWED_KIDS[kid], "rb").read()
            jwt.decode(token, key)
    except jwt.exceptions.DecodeError:
        return False
    return True
```

### Conclusion

Path traversal via the `kid` parameter is a serious vulnerability in JWT implementations. By understanding the structure and behavior of JWTs, and implementing proper validation and security measures, developers can significantly reduce the risk of such attacks. Regular security audits and penetration testing are essential to ensure the security of JWT-based systems.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive lab on JWT authentication bypass via the `kid` header.
- **OWASP Juice Shop**: Provides a variety of web security challenges, including JWT-related vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios where JWTs can be exploited.
- **WebGoat**: Offers interactive lessons on web security, including JWT vulnerabilities.

By practicing these labs, you can gain a deeper understanding of JWT vulnerabilities and how to defend against them.

---
<!-- nav -->
[[11-Path Traversal Attack via `kid` Header|Path Traversal Attack via `kid` Header]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[13-Path Traversal via `kid` Header|Path Traversal via `kid` Header]]
