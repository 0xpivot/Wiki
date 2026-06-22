---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF

### Detection

Detecting CSRF vulnerabilities requires a combination of static analysis and dynamic testing. Static analysis tools can identify potential CSRF vulnerabilities by analyzing the codebase for missing CSRF tokens or improper validation of headers. Dynamic testing involves simulating attacks to see if the application is vulnerable.

### Prevention

Preventing CSRF attacks involves several strategies:

1. **CSRF Tokens**: Generate unique tokens for each session and include them in forms and AJAX requests. Validate these tokens on the server-side to ensure that the request is legitimate.
2. **SameSite Cookies**: Set the `SameSite` attribute on cookies to restrict their usage to the same site. This prevents cross-site requests from accessing sensitive cookies.
3. **HTTP Headers**: Use the `X-Requested-With` header to ensure that requests are made from the same origin. Additionally, validate the `Origin` and `Referer` headers to ensure that the request comes from a trusted source.
4. **Double Submit Cookie Pattern**: Include a CSRF token in both a cookie and a request parameter. Validate that both match on the server-side.

### Secure Coding Practices

Here is an example of how to implement CSRF protection using CSRF tokens:

#### Vulnerable Code

```python
@app.route('/change-email', methods=['POST'])
def change_email():
    new_email = request.form['email']
    # Change email logic here
    return "Email changed successfully"
```

#### Secure Code

```python
from flask import Flask, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/login', methods=['POST'])
def login():
    # Login logic here
    session['csrf_token'] = generate_csrf_token()
    return redirect(url_for('my_account'))

@app.route('/change-email', methods=['POST'])
def change_email():
    csrf_token = request.form.get('csrf_token')
    if csrf_token != session.get('csrf_token'):
        return "Invalid CSRF token", 403
    new_email = request.form['email']
    # Change email logic here
    return "Email changed successfully"
```

### Configuration Hardening

Ensure that your web server and application frameworks are configured securely. Here is an example of configuring Nginx to enforce the `SameSite` attribute on cookies:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Set-Cookie "sessionid=abc123; SameSite=Strict";
        # Other configurations
    }
}
```

### Mitigations

Mitigate CSRF attacks by implementing the following measures:

1. **Use HTTPS**: Ensure that all communication between the client and server is encrypted using HTTPS.
2. **Rate Limiting**: Implement rate limiting to prevent automated attacks.
3. **User Education**: Educate users about the risks of clicking on suspicious links and the importance of logging out of sessions.

### Conclusion

CSRF is a serious threat to web applications, but it can be effectively mitigated through proper implementation of CSRF tokens, SameSite cookies, and other security measures. By understanding the underlying mechanisms and implementing robust defenses, developers can protect their applications from CSRF attacks.

### Practice Labs

For hands-on practice with CSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive CSRF lab that covers various aspects of the vulnerability.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes CSRF vulnerabilities for educational purposes.
- **DVWA (Damn Vulnerable Web Application)**: Includes a CSRF module that demonstrates different types of CSRF attacks and defenses.

By completing these labs, you can gain practical experience in identifying and mitigating CSRF vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/09-Lab 8 CSRF with broken Referer validation/03-Cross-Site Request Forgery (CSRF)|Cross-Site Request Forgery (CSRF)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/09-Lab 8 CSRF with broken Referer validation/00-Overview|Overview]] | [[05-Lab Exercise CSRF with Broken Referer Validation|Lab Exercise CSRF with Broken Referer Validation]]
