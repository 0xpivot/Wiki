---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Detection and Prevention

### How to Detect CSRF Attacks

Detecting CSRF attacks can be challenging, but there are several methods to identify potential vulnerabilities:

1. **Manual Testing**: Manually test the web application for CSRF vulnerabilities using tools like Burp Suite.
2. **Automated Scanning**: Use automated scanning tools to detect CSRF vulnerabilities.
3. **Logging and Monitoring**: Monitor server logs for suspicious activity, such as unexpected requests from authenticated users.

### How to Prevent CSRF Attacks

Preventing CSRF attacks requires implementing robust defenses. Here are some best practices:

1. **Use Anti-CSRF Tokens**: Generate unique tokens for each user session and validate them for every request.
2. **Validate Request Methods**: Ensure that token validation applies to all request methods, not just specific ones.
3. **SameSite Cookies**: Use the `SameSite` attribute to restrict cookies to first-party contexts.
4. **Content Security Policy (CSP)**: Implement CSP to mitigate the risk of XSS attacks, which can be used to deliver CSRF payloads.

### Secure Coding Fixes

Here is an example of how to implement anti-CSRF tokens securely:

#### Vulnerable Code

```python
@app.route('/change-email', methods=['POST'])
def change_email():
    email = request.form['email']
    # Change email logic
    return "Email changed successfully"
```

#### Secure Code

```python
import secrets

@app.route('/change-email', methods=['POST'])
def change_email():
    email = request.form['email']
    token = request.form['token']
    
    # Validate token
    if token != session.get('csrf_token'):
        abort(403)
    
    # Change email logic
    return "Email changed successfully"

@app.before_request
def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
```

### Configuration Hardening

Ensure that your web application is configured securely to prevent CSRF attacks. Here are some configuration recommendations:

1. **Set `SameSite` Attribute**: Set the `SameSite` attribute to `Strict` or `Lax` to restrict cookies to first-party contexts.
2. **Enable CSP**: Enable Content Security Policy to mitigate the risk of XSS attacks.

#### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Set-Cookie "session=abc123; SameSite=Strict";
        add_header Content-Security-Policy "default-src 'self'";
    }
}
```

### Mitigations

Implementing the following mitigations can help prevent CSRF attacks:

1. **Regular Security Audits**: Conduct regular security audits to identify and fix vulnerabilities.
2. **User Education**: Educate users about the risks of clicking on suspicious links or visiting untrusted websites.
3. **Two-Factor Authentication (2FA)**: Implement 2FA to add an additional layer of security.

---
<!-- nav -->
[[04-Detailed Explanation of CSRF Attack Mechanics|Detailed Explanation of CSRF Attack Mechanics]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/06-How to Prevent  Defend Against CSRF|How to Prevent  Defend Against CSRF]]
