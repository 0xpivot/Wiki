---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF Attacks

### Detection

Detecting CSRF vulnerabilities involves monitoring for suspicious activity and analyzing logs for unauthorized actions. Automated tools like Burp Suite and OWASP ZAP can help in identifying potential vulnerabilities.

### Prevention

Preventing CSRF attacks requires implementing robust security measures:

1. **CSRF Tokens**: Use unique, unpredictable tokens for each session and verify them on the server-side.
2. **SameSite Cookies**: Set the `SameSite` attribute on cookies to restrict their usage to the same site.
3. **HTTP Headers**: Use the `Content-Security-Policy` header to mitigate the risk of XSS attacks, which can be used to steal CSRF tokens.

### Secure Coding Practices

Secure coding practices are crucial in preventing CSRF vulnerabilities. Here’s an example of how to implement CSRF protection in a web application:

#### Vulnerable Code

```python
@app.route('/transfer', methods=['POST'])
def transfer():
    to = request.form['to']
    amount = request.form['amount']
    # Perform transfer logic
    return "Transfer successful"
```

#### Secure Code

```python
@app.route('/transfer', methods=['POST'])
def transfer():
    if request.form.get('csrf_token') != session['csrf_token']:
        abort(403)
    to = request.form['to']
    amount = request.form['amount']
    # Perform transfer logic
    return "Transfer successful"
```

### Configuration Hardening

Hardening the configuration of web servers and applications can further mitigate the risk of CSRF attacks:

- **Web Server Configuration**: Ensure that web servers are configured to enforce secure protocols and headers.
- **Application Configuration**: Configure applications to use secure coding practices and implement CSRF protection mechanisms.

### Real-World Example: Secure Configuration

Here’s an example of configuring a web server to enforce secure headers:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;

    add_header Content-Security-Policy "default-src 'self'";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
}
```

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/08-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]] | [[10-How to Prevent  Defend Against CSRF|How to Prevent  Defend Against CSRF]]
