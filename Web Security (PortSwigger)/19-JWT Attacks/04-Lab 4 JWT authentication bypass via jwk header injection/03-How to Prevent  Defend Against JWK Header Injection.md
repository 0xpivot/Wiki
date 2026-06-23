---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## How to Prevent / Defend Against JWK Header Injection

### Detection

1. **Monitor JWT Usage**: Use tools like Burp Suite or OWASP ZAP to monitor JWT usage and detect any suspicious modifications.
2. **Audit Logs**: Implement logging to track JWT usage and detect any unauthorized access attempts.

### Prevention

1. **Strict Signature Verification**: Ensure that the server strictly verifies the signature of the JWT.
2. **Use Strong Keys**: Use strong keys for signing JWTs and ensure they are not easily brute-forced.
3. **Disallow `none` Algorithm**: Configure your JWT implementation to disallow the `none` algorithm.
4. **Secure Custom Headers**: Ensure that custom headers like `jwk` are handled securely and cannot be exploited.

### Secure Coding Fixes

#### Vulnerable Code

```python
from flask import Flask, request
import jwt

app = Flask(__name__)

@app.route('/api/admin', methods=['POST'])
def admin_panel():
    token = request.headers.get('Authorization').split()[1]
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        if decoded['sub'] == 'admin':
            return {"message": "Access granted"}
        else:
            return {"message": "Access denied"}, 403
    except jwt.exceptions.DecodeError:
        return {"message": "Invalid token"}, 401

if __name__ == '__main__':
    app.run()
```

#### Fixed Code

```python
from flask import Flask, request
import jwt

app = Flask(__name__)
SECRET_KEY = 'your_secret_key'

@app.route('/api/admin', methods=['POST'])
def admin_panel():
    token = request.headers.get('Authorization').split()[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["RS256"])
        if decoded['sub'] == 'admin':
            return {"message": "Access granted"}
        else:
            return {"message": "Access denied"}, 403
    except jwt.exceptions.DecodeError:
        return {"message": "Invalid token"}, 401

if __name__ == '__main__':
    app.run()
```

### Configuration Hardening

1. **Disable Unnecessary Algorithms**: Ensure that unnecessary algorithms like `none` are disabled.
2. **Use Strong Keys**: Use strong keys for signing JWTs and ensure they are not easily brute-forced.
3. **Monitor JWT Usage**: Use tools like Burp Suite or OWASP ZAP to monitor JWT usage and detect any suspicious modifications.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including JWT attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing different types of attacks, including JWT manipulation.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for practicing web security techniques.

By thoroughly understanding and implementing these preventive measures, you can significantly reduce the risk of JWT-related vulnerabilities in your applications.

---
<!-- nav -->
[[02-JWT Attacks Overview|JWT Attacks Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/04-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]]
