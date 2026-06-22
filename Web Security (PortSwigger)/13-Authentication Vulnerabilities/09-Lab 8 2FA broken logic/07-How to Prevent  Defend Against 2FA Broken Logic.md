---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against 2FA Broken Logic

### Detection

To detect potential 2FA logic flaws, you can perform the following checks:

1. **Code Review**: Conduct thorough code reviews to identify any logical errors in the 2FA process.
2. **Penetration Testing**: Perform penetration testing to identify vulnerabilities in the 2FA implementation.
3. **Logging and Monitoring**: Implement logging and monitoring to detect unusual patterns in the authentication process.

### Prevention

To prevent 2FA broken logic vulnerabilities, follow these best practices:

1. **Proper Validation**: Ensure that the initial authentication is properly validated before sending the 2FA request.
2. **Secure Implementation**: Follow secure coding practices to implement the 2FA process correctly.
3. **Regular Audits**: Regularly audit the 2FA implementation to identify and fix any potential vulnerabilities.

### Secure Coding Fix

Here is an example of a vulnerable and secure implementation of the 2FA process:

#### Vulnerable Code

```python
def authenticate(username, password, otp):
    if check_password(username, password):
        if verify_otp(username, otp):
            return True
    return False
```

#### Secure Code

```python
def authenticate(username, password, otp):
    if check_password(username, password):
        if verify_otp(username, otp):
            return True
    else:
        return False
```

### Configuration Hardening

Ensure that your 2FA configuration is hardened by following these steps:

1. **Disable Weak Algorithms**: Disable weak algorithms such as SHA-1 for hashing.
2. **Use Strong Encryption**: Use strong encryption algorithms for storing and transmitting sensitive data.
3. **Enable Multi-Factor Authentication**: Enable multi-factor authentication for all users.

### Real-World Example: Secure 2FA Implementation

A secure 2FA implementation can be seen in many modern applications. For example, Google Authenticator uses time-based one-time passwords (TOTP) to generate 2FA codes. This ensures that even if an attacker intercepts a 2FA code, it will be invalid after a short period.

---
<!-- nav -->
[[06-Hands-On Practice|Hands-On Practice]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/00-Overview|Overview]] | [[08-Multi-Threading in Web Security|Multi-Threading in Web Security]]
