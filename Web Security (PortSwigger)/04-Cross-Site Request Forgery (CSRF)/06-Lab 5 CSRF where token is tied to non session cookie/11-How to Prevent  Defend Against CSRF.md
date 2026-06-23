---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF

To prevent CSRF attacks, web applications should implement robust CSRF protections. Here are some best practices:

### Secure Coding Practices

1. **Use CSRF Tokens**: Generate unique, unpredictable CSRF tokens for each user session and include them in forms and requests.
2. **Validate CSRF Tokens**: On the server side, validate that the CSRF token in the request matches the one stored in the session.
3. **Use SameSite Cookies**: Set the `SameSite` attribute to `Strict` to prevent cookies from being sent in cross-site requests.
4. **Check Referer Header**: Ensure that requests originate from the same origin as the web application.

### Example of Secure Code

Here is an example of secure code that implements CSRF protections:

```python
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = 'super_secret_key'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Perform authentication logic
        session['csrf_token'] = generate_csrf_token()
        return redirect(url_for('account_settings'))
    return render_template_string('''
        <form method="POST" action="/login">
            <input type="hidden" name="csrf_token" value="{{ session.csrf_token }}">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password">
            <button type="submit">Login</button>
        </form>
    ''')

@app.route('/account/settings', methods=['GET', 'POST'])
def account_settings():
    if request.method == 'POST':
        csrf_token = request.form['csrf_token']
        if csrf_token != session['csrf_token']:
            return "Invalid CSRF token"
        # Process account settings logic
    return render_template_string('''
        <form method="POST" action="/account/settings">
            <input type="hidden" name="csrf_token" value="{{ session.csrf_token }}">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email">
            <button type="submit">Save</button>
        </form>
    ''')

def generate_csrf_token():
    import secrets
    return secrets.token_urlsafe(16)

if __name__ == '___main__":
    app.run(debug=True)
```

### Configuration Hardening

1. **Enable SameSite Attribute**: Ensure that all cookies include the `SameSite=Strict` attribute.
2. **Disable Referer Header Spoofing**: Configure web servers to prevent the `Referer` header from being spoofed.

### Detection and Mitigation

1. **Monitor Logs**: Regularly review server logs for suspicious activity, such as unexpected changes to user accounts.
2. **Implement Rate Limiting**: Limit the number of requests that can be made within a certain time frame to prevent brute-force attacks.
3. **Educate Users**: Inform users about the risks of clicking on links or visiting pages from untrusted sources.

### Real-World Example of Detection and Mitigation

Consider a recent breach where a financial institution detected a series of unauthorized transactions. Upon investigation, they found that the transactions were initiated via a CSRF attack. To mitigate the risk, they implemented the following measures:

1. **Enabled SameSite Attribute**: All session cookies were configured with `SameSite=Strict`.
2. **Implemented CSRF Tokens**: Unique CSRF tokens were generated for each user session and validated on the server side.
3. **Educated Users**: Users were informed about the risks of clicking on links or visiting pages from untrusted sources.

### Practice Labs

To gain hands-on experience with CSRF vulnerabilities and defenses, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on CSRF attacks and defenses.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including CSRF.
- **DVWA (Damn Vulnerable Web Application)**: Includes a variety of web application vulnerabilities, including CSRF, for educational purposes.
- **WebGoat**: A deliberately insecure Java web application designed to teach web application security lessons.

By following these best practices and engaging in hands-on practice, you can effectively prevent and mitigate CSRF attacks in your web applications.

---
<!-- nav -->
[[10-Detailed Explanation of CSRF Attack with Non-Session Cookie Token|Detailed Explanation of CSRF Attack with Non-Session Cookie Token]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/06-Lab 5 CSRF where token is tied to non session cookie/00-Overview|Overview]] | [[12-Understanding Cross-Site Request Forgery (CSRF)|Understanding Cross-Site Request Forgery (CSRF)]]
