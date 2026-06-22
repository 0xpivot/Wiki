---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF

### Detection

Detecting CSRF attacks can be challenging because the requests appear legitimate from the server's perspective. However, there are some indicators that can help identify potential CSRF attacks:

1. **Unusual Request Patterns**: Monitor for unusual patterns of requests, such as frequent requests from the same IP address.
2. **Behavioral Analysis**: Implement behavioral analysis to detect anomalies in user behavior.
3. **Logging and Monitoring**: Maintain detailed logs of all requests and monitor them for suspicious activity.

### Prevention

Preventing CSRF attacks requires implementing robust CSRF protection mechanisms:

1. **CSRF Tokens**: Always include CSRF tokens in forms and requests.
2. **Double Submit Cookie Pattern**: Use a double submit cookie pattern where the token is included both in a cookie and as a form field.
3. **SameSite Cookies**: Set the `SameSite` attribute on cookies to prevent cross-site requests.
4. **HTTP Headers**: Use HTTP headers like `X-Requested-With` to verify the origin of the request.

### Secure Coding Practices

Implementing secure coding practices is crucial to prevent CSRF attacks:

#### Vulnerable Code

```python
@app.route('/submit', methods=['POST'])
def submit():
    # Process the request without checking the CSRF token
    return "Request processed successfully"
```

#### Secure Code

```python
@app.route('/submit', methods=['POST'])
def submit():
    if 'csrf_token' not in session or session['csrf_token'] != request.form['csrf_token']:
        return "Invalid CSRF token", 400
    # Process the request
    return "Request processed successfully"
```

### Configuration Hardening

Hardening configurations can also help prevent CSRF attacks:

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Content-Type-Options nosniff;
        add_header Referrer-Policy "no-referrer";
    }
}
```

#### Apache Configuration

```apache
<Directory "/var/www/html">
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options nosniff
    Header always set Referrer-Policy "no-referrer"
</Directory>
```

### Common Pitfalls

When implementing CSRF protection, there are several common pitfalls to avoid:

1. **Token Generation**: Ensure that CSRF tokens are generated securely and are sufficiently random.
2. **Token Storage**: Store CSRF tokens securely and ensure they are not exposed in the URL or other easily accessible locations.
3. **Token Validation**: Validate CSRF tokens strictly and ensure that the validation logic cannot be bypassed.
4. **Token Expiration**: Implement token expiration to prevent reuse of old tokens.

### Hands-On Labs

For hands-on practice with CSRF attacks and defenses, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on CSRF attacks and defenses.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including CSRF.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web security attacks and defenses.

By thoroughly understanding and implementing these concepts, you can effectively protect your web applications from CSRF attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/04-Lab 3 CSRF where token validation depends on token being present/04-Cross-Site Request Forgery (CSRF)|Cross-Site Request Forgery (CSRF)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/04-Lab 3 CSRF where token validation depends on token being present/00-Overview|Overview]] | [[06-Understanding CSRF Tokens|Understanding CSRF Tokens]]
