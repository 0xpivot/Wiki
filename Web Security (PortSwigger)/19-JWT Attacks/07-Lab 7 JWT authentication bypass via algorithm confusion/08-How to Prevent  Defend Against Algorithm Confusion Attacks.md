---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## How to Prevent / Defend Against Algorithm Confusion Attacks

### Detection

- **Monitor JWT Requests**: Use tools like Burp Suite to monitor JWT requests and detect any anomalies.
- **Log JWT Verifications**: Log JWT verifications to detect any failed attempts.

### Prevention

- **Validate the `alg` Field**: Ensure the server validates the `alg` field and does not blindly trust its value.
- **Use Strong Algorithms**: Use strong algorithms like `RS256` and avoid weak algorithms like `HS256`.

### Secure Coding Fixes

#### Vulnerable Code

```python
import jwt

def verify_token(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except jwt.exceptions.DecodeError:
        return None
```

#### Secure Code

```python
import jwt

def verify_token(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": True, "verify_aud": True, "verify_iat": True, "verify_exp": True, "verify_nbf": True, "verify_iss": True, "verify_sub": True, "verify_jti": True, "require_exp": True, "require_iat": True, "require_nbf": True, "require_iss": True, "require_sub": True, "require_aud": True, "require_jti": True})
        return decoded
    except jwt.exceptions.DecodeError:
        return None
```

### Configuration Hardening

- **Disable Weak Algorithms**: Disable weak algorithms like `HS256` and use strong algorithms like `RS256`.
- **Enable Strict Validation**: Enable strict validation of JWTs to prevent attacks.

### Mitigations

- **Use JWT Libraries with Strong Validation**: Use JWT libraries that enforce strong validation of JWTs.
- **Regularly Update Libraries**: Regularly update JWT libraries to ensure they have the latest security patches.

---
<!-- nav -->
[[07-Detailed Walkthrough|Detailed Walkthrough]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[09-How to Prevent  Defend Against Algorithm Confusion|How to Prevent  Defend Against Algorithm Confusion]]
