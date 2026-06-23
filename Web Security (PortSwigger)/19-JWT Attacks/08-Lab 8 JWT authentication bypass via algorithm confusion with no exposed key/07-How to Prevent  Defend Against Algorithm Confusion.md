---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## How to Prevent / Defend Against Algorithm Confusion

### Detection

To detect algorithm confusion, you can use automated tools like Burp Suite or other web security scanners. These tools can help identify if the server is vulnerable to algorithm manipulation.

#### Automated Tools

1. **Burp Suite**: Capture the JWT in the request, modify the `alg` field, and send the modified request to the server.
2. **OWASP ZAP**: Similar to Burp Suite, capture the JWT, modify the `alg` field, and send the modified request to the server.

### Prevention

To prevent algorithm confusion, you should enforce strict validation of the signing algorithm used to sign the JWT. This ensures that the server only accepts tokens signed with the expected algorithm.

#### Secure Coding Practices

1. **Validate the Algorithm**: Ensure that the server validates the `alg` field in the JWT header and only accepts tokens signed with the expected algorithm.
2. **Use Strong Algorithms**: Use strong algorithms like `RS256` or `ES256` instead of weaker ones like `HS256`.

#### Example of Secure Code

Vulnerable code:

```python
def validate_jwt(token):
    decoded_token = jwt.decode(token, options={"verify_signature": False})
    return decoded_token
```

Secure code:

```python
def validate_jwt(token):
    decoded_token = jwt.decode(token, options={"verify_signature": True, "algorithms": ["HS256"]})
    return decoded_token
```

### Hardening

To harden the JWT implementation, you should:

1. **Enforce Strict Validation**: Ensure that the server enforces strict validation of the signing algorithm.
2. **Use Strong Algorithms**: Use strong algorithms like `RS256` or `ES256` instead of weaker ones like `HS256`.
3. **Monitor and Log**: Monitor and log JWT-related activities to detect and respond to potential attacks.

### Real-World Example: Hardening

In the CVE-2017-15356 example, hardening involved enforcing strict validation of the signing algorithm and using strong algorithms like `RS256` or `ES256`.

---
<!-- nav -->
[[06-Detecting and Exploiting Algorithm Confusion|Detecting and Exploiting Algorithm Confusion]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/08-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]]
