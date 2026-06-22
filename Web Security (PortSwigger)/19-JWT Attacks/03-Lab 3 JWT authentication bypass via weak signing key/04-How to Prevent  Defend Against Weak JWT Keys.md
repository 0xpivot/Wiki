---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## How to Prevent / Defend Against Weak JWT Keys

### Detection

To detect potential attacks involving weak JWT keys, organizations should implement monitoring and logging mechanisms. These mechanisms should track the usage of JWTs and alert on any suspicious activity, such as an unusually high number of failed authentication attempts.

### Prevention

#### Secure Key Management

1. **Use Strong Keys**: Ensure that the signing key is strong and complex. Avoid using default or easily guessable keys.
2. **Rotate Keys Regularly**: Rotate the signing key periodically to minimize the window of opportunity for attackers.
3. **Secure Storage**: Store the signing key securely, ensuring that it is not exposed in source code or configuration files.

#### Secure Coding Practices

1. **Validate JWTs Properly**: Always validate JWTs on the server-side to ensure that they have not been tampered with.
2. **Use HTTPS**: Ensure that all communication involving JWTs is encrypted using HTTPS to prevent interception and tampering.

#### Configuration Hardening

1. **Disable Weak Algorithms**: Disable weak hashing algorithms in your JWT implementation. Use strong algorithms like HS512 instead of HS256.
2. **Implement Rate Limiting**: Implement rate limiting on authentication endpoints to prevent brute-force attacks.

### Secure-Coding Fixes

#### Vulnerable Code Example

```python
import jwt

secret_key = "weak_secret_key"

def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token
```

#### Secure Code Example

```python
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Generate a strong RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

public_key = private_key.public_key()

# Serialize the keys
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, private_pem, algorithm="RS256")
    return token
```

### Complete Example: JWT Request and Response

#### HTTP Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### Common Mistakes and Pitfalls

1. **Hardcoding Secrets**: Avoid hardcoding secrets in your code or configuration files. Use environment variables or secure vaults instead.
2. **Exposing JWTs**: Ensure that JWTs are not exposed in URLs or logs. Use secure storage mechanisms like HTTP-only cookies.
3. **Ignoring Expiry**: Always set and enforce expiry times on JWTs to limit their validity period.

### Hands-On Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on JWT authentication and related attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including JWT attacks.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and testing web security concepts.

By thoroughly understanding the concepts, mechanisms, and preventive measures associated with JWT attacks, you can significantly enhance the security of your web applications.

---
<!-- nav -->
[[03-Introduction to JWT and Its Components|Introduction to JWT and Its Components]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[05-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]]
