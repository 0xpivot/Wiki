---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Authentication Bypass via Flawed Signature Verification

One common vulnerability in JWT implementations is flawed signature verification. This occurs when the server does not properly validate the signature of the JWT, allowing attackers to modify the payload and still have the token accepted.

### Example Scenario

Consider a web application that uses JWTs for authentication. The JWT structure might look like this:

```json
{
  "iss": "sportswigger",
  "exp": 1637236800,
  "sub": "regular_user"
}
```

The `iss` field represents the issuer of the token, the `exp` field represents the expiration time, and the `sub` field represents the subject (user) associated with the token.

### Attack Vector

If the server does not properly verify the signature of the JWT, an attacker can modify the payload and still have the token accepted. For example, the attacker could change the `sub` field to `"admin"` and attempt to access administrative resources.

#### Steps to Exploit

1. **Obtain a Valid Token**: The attacker needs to obtain a valid JWT from a legitimate user.
2. **Modify the Payload**: The attacker modifies the payload to change the `sub` field to `"admin"`.
3. **Forge the Signature**: Since the server does not properly verify the signature, the attacker can either leave the signature unchanged or generate a new one using a different algorithm.
4. **Submit the Modified Token**: The attacker submits the modified token to the server, which accepts it due to the flawed signature verification.

### Real-World Example

A real-world example of this vulnerability occurred in a popular open-source project. The project used JWTs for authentication but did not properly verify the signatures. An attacker was able to modify the payload and gain unauthorized access to sensitive resources.

#### CVE Example

CVE-2021-3279: This CVE describes a vulnerability in a web application where the server did not properly verify the signatures of JWTs. An attacker could modify the payload and gain unauthorized access.

### Code Example

Here is an example of a vulnerable server-side implementation in Python:

```python
import jwt

def authenticate(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        if decoded["sub"] == "admin":
            return "Access granted to admin resources"
        else:
            return "Access granted to regular user resources"
    except jwt.exceptions.DecodeError:
        return "Invalid token"

# Vulnerable token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYzNzIzNjgwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

print(authenticate(token))
```

In this example, the server does not properly verify the signature of the JWT, allowing the attacker to modify the payload and still have the token accepted.

### How to Prevent / Defend

To prevent this type of attack, the server must properly verify the signature of the JWT. Here are some steps to ensure proper signature verification:

1. **Use Strong Signing Algorithms**: Ensure that the signing algorithm used is strong and cannot be easily forged.
2. **Verify the Signature**: Always verify the signature of the JWT before accepting it.
3. **Use Secure Key Management**: Ensure that the keys used for signing and verifying JWTs are securely managed and not exposed to unauthorized users.

#### Secure Implementation

Here is an example of a secure server-side implementation in Python:

```python
import jwt

SECRET_KEY = "your_secret_key"

def authenticate(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if decoded["sub"] == "admin":
            return "Access granted to admin resources"
        else:
            return "Access granted to regular user resources"
    except jwt.exceptions.DecodeError:
        return "Invalid token"

# Secure token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYzNzIzNjgwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

print(authenticate(token))
```

In this example, the server properly verifies the signature of the JWT using a secret key and a strong signing algorithm.

### Detection and Prevention

To detect and prevent this type of attack, you can implement the following measures:

1. **Regular Security Audits**: Regularly audit your JWT implementation to ensure that it properly verifies signatures.
2. **Use Security Tools**: Use security tools such as static analysis tools and penetration testing tools to identify vulnerabilities in your JWT implementation.
3. **Monitor Logs**: Monitor logs for suspicious activity, such as repeated attempts to submit invalid tokens.

### Practice Labs

To practice and understand JWT attacks, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs on JWT attacks, including authentication bypass via flawed signature verification.
- **OWASP Juice Shop**: A deliberately insecure web application that includes JWT-related vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Another deliberately insecure web application that includes JWT-related vulnerabilities.

These labs provide hands-on experience with JWT attacks and help you understand how to detect and prevent them.

### Conclusion

JWTs are a powerful tool for authentication and authorization, but they must be implemented securely to prevent attacks. By properly verifying the signatures of JWTs, you can ensure that your application is secure against authentication bypass attacks. Always follow best practices for secure key management and regularly audit your JWT implementation to identify and mitigate vulnerabilities.

---
<!-- nav -->
[[10-JWT Attacks Authentication Bypass via Flawed Signature Verification|JWT Attacks Authentication Bypass via Flawed Signature Verification]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[12-Non-Algorithm Attack|Non-Algorithm Attack]]
