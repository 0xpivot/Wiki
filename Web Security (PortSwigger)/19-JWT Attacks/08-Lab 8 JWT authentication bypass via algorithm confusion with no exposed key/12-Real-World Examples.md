---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Real-World Examples

Algorithm confusion attacks have been observed in several real-world scenarios. One notable example is the CVE-2017-15359, where a vulnerability in the `jsonwebtoken` library allowed attackers to bypass authentication by manipulating the signing algorithm.

### CVE-2017-15359

In this case, the `jsonwebtoken` library did not properly validate the algorithm used to sign the token. An attacker could manipulate the token to use a different algorithm, leading to unauthorized access.

#### Impact

This vulnerability affected numerous applications that relied on the `jsonwebtoken` library for authentication. It allowed attackers to bypass authentication mechanisms and gain unauthorized access to sensitive resources.

### Prevention and Defense

To prevent algorithm confusion attacks, it is crucial to implement proper validation of the signing algorithm used in JWTs. Here are some steps to ensure security:

#### Secure Coding Practices

1. **Validate the Algorithm**: Always validate the algorithm used to sign the token. Ensure that the token is signed using the expected algorithm.
2. **Use Strong Algorithms**: Use strong algorithms such as RS256 or ES256 for signing tokens.
3. **Secure Key Management**: Ensure that private keys are securely stored and not exposed to unauthorized users.

#### Configuration Hardening

1. **Disable Weak Algorithms**: Disable weak algorithms such as HS256 in your JWT implementation.
2. **Enforce Strong Policies**: Enforce strong policies for key management and token validation.

#### Detection and Mitigation

1. **Monitor JWT Usage**: Monitor JWT usage in your application to detect any suspicious activity.
2. **Implement Rate Limiting**: Implement rate limiting to prevent brute-force attacks on JWTs.

### Secure Code Example

Here’s an example of secure code that validates the algorithm used to sign the token:

```python
from jose import jwt

def validate_token(token, public_key):
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
        return decoded_token
    except jwt.JWTError as e:
        print(f"Token validation failed: {e}")
        return None

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJhZG1pbiI6dHJ1ZX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
public_key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"

decoded_token = validate_token(token, public_key)
if decoded_token:
    print("Token is valid")
else:
    print("Token is invalid")
```

### Conclusion

In this lab, we explored how to bypass JWT authentication via algorithm confusion attacks. We covered the background of JWTs, the vulnerability, and how to exploit it. We also provided a detailed walkthrough of the steps involved and included real-world examples and secure coding practices to help prevent such attacks.

### Practice Labs

To further practice and understand JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to JWT attacks.
- **OWASP Juice Shop**: Provides a web application with numerous security vulnerabilities, including JWT-related issues.
- **DVWA (Damn Vulnerable Web Application)**: Includes labs for practicing web security techniques, including JWT manipulation.

By mastering these concepts and practicing with real-world examples, you can enhance your skills in detecting and preventing JWT attacks.

---
<!-- nav -->
[[11-Lab Exercises|Lab Exercises]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[13-Step-by-Step Walkthrough|Step-by-Step Walkthrough]]
