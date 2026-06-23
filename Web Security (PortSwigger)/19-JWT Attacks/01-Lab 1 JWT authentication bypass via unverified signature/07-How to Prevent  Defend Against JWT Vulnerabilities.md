---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## How to Prevent / Defend Against JWT Vulnerabilities

### Detection

To detect JWT vulnerabilities, you can:

1. **Review Code**: Ensure that JWT signatures are properly verified.
2. **Use Security Scanners**: Tools like Burp Suite can help identify JWT-related vulnerabilities.
3. **Monitor Logs**: Look for unusual patterns in JWT usage.

### Prevention

To prevent JWT vulnerabilities, follow these best practices:

1. **Verify Signatures**: Always verify the signature of incoming JWTs.
2. **Use Strong Algorithms**: Use strong signing algorithms like RS256 instead of HS256.
3. **Secure Secret Keys**: Store secret keys securely and rotate them regularly.
4. **Limit Token Lifetime**: Set short expiration times for JWTs to minimize the window of opportunity for attacks.

### Secure Coding Fixes

Here’s an example of how to securely verify JWTs in Node.js:

```javascript
const jwt = require('jsonwebtoken');

function verifyToken(token, secret) {
    try {
        const decoded = jwt.verify(token, secret);
        return decoded;
    } catch (err) {
        throw new Error('Invalid token');
    }
}

// Usage
try {
    const decoded = verifyToken('your.jwt.token', 'your_secret_key');
    console.log(decoded);
} catch (err) {
    console.error(err.message);
}
```

### Configuration Hardening

Ensure your JWT configuration is hardened:

```json
{
  "secret": "your_secure_secret_key",
  "algorithm": "RS256",
  "expiresIn": "1h"
}
```

### Mitigations

1. **Rate Limiting**: Implement rate limiting to prevent brute-force attacks.
2. **Logging and Monitoring**: Log and monitor JWT usage to detect suspicious activity.
3. **Security Headers**: Use security headers like `Content-Security-Policy` to mitigate XSS attacks.

---
<!-- nav -->
[[06-Lab Setup and Overview|Lab Setup and Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/08-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]]
