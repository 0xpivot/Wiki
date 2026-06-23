---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Understanding CSRF Tokens and Their Role in Web Security

### What is a CSRF Token?

A Cross-Site Request Forgery (CSRF) token is a unique identifier used to protect against CSRF attacks. A CSRF attack occurs when an attacker tricks a user into performing an unwanted action on a website where they are authenticated. The CSRF token acts as a one-time password that must be included in each request to ensure that the request originates from the intended user and not from an attacker.

#### Why Are CSRF Tokens Important?

CSRF tokens are crucial because they help prevent attackers from exploiting the authenticated session of a user. Without a CSRF token, an attacker could craft a malicious request that would appear to come from the authenticated user, potentially leading to unauthorized actions such as transferring funds, posting messages, or changing account settings.

#### How Do CSRF Tokens Work Under the Hood?

When a user visits a webpage, the server generates a unique CSRF token and includes it in the form data or as a hidden field in the HTML. This token is then sent back to the server along with the user's request. The server verifies the token to ensure that the request is legitimate. If the token does not match or is missing, the request is rejected.

### Extracting CSRF Tokens from Requests

In the context of the given lecture, we need to extract the CSRF token from the response of a login request. This token will be used in subsequent requests to authenticate the user and prevent CSRF attacks.

#### Example of Extracting CSRF Tokens

Let's consider a scenario where we need to extract the CSRF token from a login request. Here’s a step-by-step breakdown:

1. **Send a GET request to the login endpoint**:
    ```http
    GET /login HTTP/1.1
    Host: example.com
    ```

2. **Receive the response containing the CSRF token**:
    ```html
    <html>
      <body>
        <form method="POST" action="/login">
          <input type="hidden" name="csrf_token" value="abc123">
          <!-- Other form fields -->
        </form>
      </body>
    </html>
    ```

3. **Extract the CSRF token from the response**:
    ```python
    import re

    def get_csrf_token(response):
        csrf_match = re.search(r'<input type="hidden" name="csrf_token" value="([^"]+)"', response.text)
        if csrf_match:
            return csrf_match.group(1)
        else:
            raise ValueError("CSRF token not found in the response")

    # Example usage
    response = session.get('https://example.com/login')
    csrf_token = get_csrf_token(response)
    print(csrf_token)  # Output: abc123
    ```

### Using CSRF Tokens in Subsequent Requests

Once the CSRF token is extracted, it needs to be included in subsequent requests to maintain the integrity of the session.

#### Example of Using CSRF Tokens in a POST Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=secret&csrf_token=abc123
```

### Extracting CSRF Tokens Multiple Times

In the given lecture, the CSRF token needs to be extracted multiple times: during the initial login request, the `.htaccess` request, and the web shell upload request.

#### Function to Extract CSRF Tokens

To avoid repetitive code, we can create a reusable function to extract the CSRF token:

```python
def get_csrf_token(session, url):
    response = session.get(url)
    csrf_match = re.search(r'<input type="hidden" name="csrf_token" value="([^"]+)"', response.text)
    if csrf_match:
        return csrf_match.group(1)
    else:
        raise ValueError("CSRF token not found in the response")

# Example usage
login_url = 'https://example.com/login'
csrf_token = get_csrf_token(session, login_url)
print(csrf_token)  # Output: abc123
```

### Real-World Examples of CSRF Attacks

#### Recent CVEs and Breaches Involving CSRF

- **CVE-2021-3427**: A vulnerability in the WordPress REST API allowed attackers to perform CSRF attacks, leading to unauthorized actions such as deleting posts or changing user roles.
- **Breaches involving CSRF**: In 2022, several financial institutions experienced breaches where attackers exploited CSRF vulnerabilities to transfer funds from users' accounts.

### How to Prevent / Defend Against CSRF Attacks

#### Detection

- **Logging and Monitoring**: Implement logging and monitoring to detect unusual patterns of activity that may indicate a CSRF attack.
- **Security Tools**: Use security tools like Burp Suite or OWASP ZAP to test for CSRF vulnerabilities.

#### Prevention

- **CSRF Tokens**: Always use CSRF tokens in forms and APIs to ensure that requests originate from the intended user.
- **SameSite Cookies**: Set the `SameSite` attribute on cookies to `Strict` or `Lax` to prevent cross-site request forgery.
- **Secure Coding Practices**: Follow secure coding practices to avoid introducing vulnerabilities that can be exploited through CSRF attacks.

#### Secure Code Fix

Here’s an example of how to implement CSRF protection in a Flask application:

```python
from flask import Flask, render_template, request, redirect, session
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validate username and password
        if request.form['username'] == 'admin' and request.form['password'] == 'secret':
            session['csrf_token'] = secrets.token_hex(16)
            return redirect('/dashboard')
        else:
            return 'Invalid credentials'
    else:
        session['csrf_token'] = secrets.token_hex(16)
        return render_template('login.html', csrf_token=session['csrf_token'])

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form['csrf_token'] != session['csrf_token']:
            return 'CSRF token mismatch'
        # Process form data
        return 'Form submitted successfully'
    else:
        return render_template('dashboard.html', csrf_token=session['csrf_token'])

if __name__ == '__main__':
    app.run(debug=True)
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

- **Missing CSRF Tokens**: Failing to include CSRF tokens in forms and APIs can leave the application vulnerable to CSRF attacks.
- **Weak CSRF Tokens**: Using weak or predictable CSRF tokens can make them easier to guess, reducing their effectiveness.

#### Best Practices

- **Use Strong CSRF Tokens**: Generate strong, random CSRF tokens using secure libraries.
- **Validate CSRF Tokens**: Always validate CSRF tokens on the server-side to ensure they match the expected value.
- **Regular Security Audits**: Conduct regular security audits and penetration testing to identify and mitigate CSRF vulnerabilities.

### Practice Labs

For hands-on practice with CSRF tokens and file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on CSRF and file upload vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including CSRF protection.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web security skills.

By thoroughly understanding and implementing CSRF protection, you can significantly enhance the security of your web applications and protect against unauthorized actions.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/05-Lab 4 Web shell upload via extension blacklist bypass/04-File Upload Vulnerabilities|File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/05-Lab 4 Web shell upload via extension blacklist bypass/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/05-Lab 4 Web shell upload via extension blacklist bypass/06-Practice Questions & Answers|Practice Questions & Answers]]
