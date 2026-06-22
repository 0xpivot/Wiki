---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against Access Control Vulnerabilities

### Detection

To detect access control vulnerabilities, implement logging and monitoring of access attempts. Look for patterns of unauthorized access or unusual requests that involve non-standard headers.

### Prevention

To prevent access control vulnerabilities, follow these best practices:

1. **Do Not Trust Non-Standard Headers**: Avoid using non-standard headers like `X-Original-URL` for critical operations. If these headers are necessary, ensure they are properly validated and sanitized.

2. **Validate URLs**: Always validate the URL against the expected format and permissions. Ensure that the URL matches the expected path and that the user has the appropriate permissions to access the resource.

3. **Use Secure Coding Practices**: Implement secure coding practices to prevent common vulnerabilities. Use input validation, output encoding, and other security measures to protect against attacks.

### Secure Code Fix

Here is an example of how to securely handle the `X-Original-URL` header:

#### Vulnerable Code

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/<path:path>')
def handle_request(path):
    original_url = request.headers.get('X-Original-URL', path)
    if original_url == '/admin':
        return "Welcome to the Admin Panel"
    else:
        return "Access Denied"

if __name__ == '__main__':
    app.run()
```

#### Secure Code

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/<path:path>')
def handle_request(path):
    original_url = request.headers.get('X-Original-URL', path)
    if original_url == '/admin' and request.user.is_admin:
        return "Welcome to the Admin Panel"
    else:
        return "Access Denied"

if __name__ == '__main__':
    app.run()
```

In the secure code, the application checks both the URL and the user's permissions before granting access to the administrative panel.

### Configuration Hardening

Ensure that your web server and application frameworks are configured to reject or ignore non-standard headers that are not necessary for the operation of the application.

#### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        if ($http_x_original_url ~* "^/admin") {
            return 403;
        }
        # Other configurations
    }
}
```

This configuration ensures that requests with the `X-Original-URL` header set to `/admin` are rejected with a 403 Forbidden response.

### Mitigations

Implement additional mitigations such as:

- **Rate Limiting**: Limit the number of requests from a single IP address to prevent brute-force attacks.
- **Web Application Firewalls (WAF)**: Use WAFs to detect and block suspicious requests.
- **Security Audits**: Regularly perform security audits and penetration testing to identify and fix vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/04-Common Pitfalls and Mistakes|Common Pitfalls and Mistakes]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/00-Overview|Overview]] | [[06-How to Prevent  Defend Against URL-Based Access Control Vulnerabilities|How to Prevent  Defend Against URL-Based Access Control Vulnerabilities]]
