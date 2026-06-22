---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## How to Prevent / Defend Against JWT Authentication Bypass

To prevent JWT authentication bypass via path traversal attacks, you need to implement several security measures:

### Secure Handling of the `kid` Header

Ensure that the `kid` header is properly validated and sanitized before being used to load keys from the filesystem. Avoid using the `kid` value directly in filesystem operations.

### Example of Secure Handling

Here is an example of secure handling of the `kid` header in Python:

```python
def validate_kid(kid):
    # Whitelist allowed kid values
    allowed_kids = ["public_key_1", "public_key_2"]
    if kid not in allowed_kids:
        raise ValueError("Invalid kid value")

def load_public_key(kid):
    validate_kid(kid)
    # Load the public key from a safe location
    return open(f"/safe/path/{kid}.pem", "rb").read()

# Example usage
try:
    public_key = load_public_key("public_key_1")
except ValueError as e:
    print(e)
```

### Secure Configuration of JWT Libraries

Use JWT libraries that have built-in protections against common vulnerabilities. For example, the `pyjwt` library in Python has options to disable unsafe features.

### Example of Secure Configuration in `pyjwt`

```python
import jwt

# Disable unsafe features
options = {
    "verify_signature": True,
    "verify_aud": True,
    "verify_iat": True,
    "verify_exp": True,
    "verify_nbf": True,
    "verify_iss": True,
    "verify_sub": True,
    "verify_jti": True,
    "require_aud": False,
    "require_iat": False,
    "require_exp": False,
    "require_nbf": False,
    "require_iss": False,
    "require_sub": False,
    "require_jti": False
}

# Decode the JWT with secure options
decoded_jwt = jwt.decode(token, public_key, algorithms=["HS256"], options=options)
```

### Regular Security Audits and Penetration Testing

Regularly conduct security audits and penetration testing to identify and mitigate vulnerabilities in JWT implementations.

### Example of Security Audit Report

Here is an example of a security audit report entry for JWT vulnerabilities:

```
Finding: JWT Authentication Bypass via Path Traversal
Description: The application uses the `kid` header to load public keys from the filesystem without proper validation.
Impact: An attacker can manipulate the `kid` header to access arbitrary files on the server's filesystem.
Recommendation: Validate and sanitize the `kid` header before using it to load keys. Use a whitelist of allowed `kid` values.
```

### Secure Coding Practices

Implement secure coding practices to ensure that JWTs are handled securely throughout the application lifecycle.

### Example of Secure Coding Practices

```python
def authenticate_user(username, password):
    # Validate username and password
    if not validate_credentials(username, password):
        return None

    # Generate JWT with secure options
    payload = {
        "sub": username,
        "name": "John Doe",
        "iat": int(time.time()),
        "iss": "https://example.com",
        "aud": "https://example.com/admin"
    }
    token = jwt.encode(payload, "secret", algorithm="HS256", headers={"kid": "public_key_1"})
    return token

def validate_credentials(username, password):
    # Check credentials against database
    return check_db(username, password)
```

### Secure Storage of JWT Secrets

Store JWT secrets securely and limit their exposure. Use environment variables or secure vaults to manage secrets.

### Example of Secure Secret Management

```bash
# Store secret in environment variable
export JWT_SECRET="my_secret_key"

# Use secret in application
import os
import jwt

secret = os.getenv("JWT_SECRET")
token = jwt.encode(payload, secret, algorithm="HS256")
```

### Conclusion

JWTs are a powerful tool for managing user sessions and authenticating users in web applications. However, they also introduce potential security risks if not implemented correctly. By understanding the structure and usage of JWTs, and implementing secure handling of the `kid` header, you can prevent JWT authentication bypass via path traversal attacks.

### Practice Labs

To practice and reinforce your understanding of JWT attacks, you can use the following labs:

- **PortSwigger Web Security Academy**: Lab 6 - JWT authentication bypass via KID header path traversal
- **OWASP Juice Shop**: Various JWT-related challenges
- **DVWA**: JWT-related vulnerabilities

These labs provide hands-on experience with real-world scenarios and help you develop the skills needed to identify and mitigate JWT vulnerabilities.

---
<!-- nav -->
[[05-Crafting the Malicious JWT|Crafting the Malicious JWT]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/07-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]]
