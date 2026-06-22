---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a user's browser into executing unwanted actions on a web application in which the user is currently authenticated. This can lead to unauthorized transactions, such as changing email addresses, transferring funds, or posting messages, without the user's knowledge or consent. To understand CSRF thoroughly, we need to delve into its mechanics, recent real-world examples, and effective defense strategies.

### What is CSRF?

CSRF attacks exploit the trust a web application places in a user's browser. When a user logs into a web application, their browser stores a session identifier (often a cookie) that authenticates them for subsequent requests. An attacker can craft a malicious request that uses this session identifier to perform actions on behalf of the user.

#### Example Scenario

Consider a banking website where a user is logged in. An attacker crafts a malicious link that, when clicked, sends a request to the bank's server to transfer money from the user's account to the attacker's account. If the user's browser includes the session identifier in the request, the bank's server will execute the transaction as if the user initiated it.

### How CSRF Works

To understand how CSRF works, let's break down the process:

1. **User Authentication**: The user logs into a web application, and the server sets a session identifier (cookie) in the user's browser.
2. **Malicious Link**: The attacker crafts a malicious link or script that, when executed, sends a request to the web application.
3. **Session Identifier**: The user's browser automatically includes the session identifier in the request.
4. **Action Execution**: The web application processes the request, assuming it was initiated by the user due to the presence of the session identifier.

#### Example Code

Here’s a simple example of a CSRF attack:

```html
<!-- Malicious HTML -->
<a href="http://bank.example.com/transfer?amount=1000&to=attacker">Click here</a>
```

When the user clicks the link, the browser sends a GET request to the bank's server with the session identifier included in the cookies.

### Real-World Examples

Recent real-world examples of CSRF vulnerabilities include:

- **CVE-2021-21972**: A CSRF vulnerability in the WordPress REST API allowed attackers to create new users with admin privileges.
- **CVE-2020-14182**: A CSRF vulnerability in the Cisco Webex Meetings Server allowed attackers to change the password of any user.

These vulnerabilities highlight the importance of implementing robust CSRF protections.

### CSRF Tokens

To mitigate CSRF attacks, web applications often use CSRF tokens. These tokens are unique, random values that are generated and associated with the user's session. They are included in forms and requests to ensure that the request originates from a legitimate source.

#### Token Generation and Validation

1. **Token Generation**: When a user logs in, the server generates a unique CSRF token and associates it with the user's session.
2. **Token Inclusion**: The token is included in forms and requests sent by the user's browser.
3. **Token Validation**: When the server receives a request, it checks if the included CSRF token matches the one associated with the user's session.

#### Example Code

Here’s an example of how CSRF tokens can be implemented in a web application:

```python
# Python Flask Example
from flask import Flask, session, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/login', methods=['POST'])
def login():
    # Generate CSRF token
    session['csrf_token'] = os.urandom(16).hex()
    return redirect(url_for('index'))

@app.route('/change_email', methods=['POST'])
def change_email():
    # Validate CSRF token
    if request.form.get('csrf_token') != session.get('csrf_token'):
        return "Invalid CSRF token", 403
    
    # Change email logic
    new_email = request.form.get('email')
    # Update user's email in the database
    return "Email changed successfully"

@app.route('/form')
def form():
    csrf_token = session.get('csrf_token')
    return f'''
    <form method="post" action="/change_email">
        <input type="hidden" name="csrf_token" value="{csrf_token}">
        <input type="email" name="email" placeholder="New Email">
        <button type="submit">Change Email</button>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
```

### Secure Transmission of CSRF Tokens

There are two primary methods for securely transmitting CSRF tokens:

1. **Hidden Field in Forms**: The CSRF token is included as a hidden field in an HTML form.
2. **HTTP Headers**: The CSRF token is included in the `X-CSRF-Token` header of the request.

#### Hidden Field Example

```html
<form method="post" action="/change_email">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="email" name="email" placeholder="New Email">
    <button type="submit">Change Email</button>
</form>
```

#### HTTP Header Example

```http
POST /change_email HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
X-CSRF-Token: {{ csrf_token }}

email=new@example.com
```

### Pitfalls and Common Mistakes

1. **Inconsistent Token Usage**: Failing to include the CSRF token in all forms and requests.
2. **Weak Token Generation**: Using predictable or weak random number generators for token generation.
3. **Token Leakage**: Exposing the CSRF token in URLs or other insecure locations.

### How to Prevent / Defend Against CSRF

#### Detection

1. **Logging and Monitoring**: Implement logging and monitoring to detect unusual patterns of activity.
2. **Security Tools**: Use security tools like Burp Suite or OWASP ZAP to test for CSRF vulnerabilities.

#### Prevention

1. **Use CSRF Tokens**: Ensure that CSRF tokens are used consistently across all forms and requests.
2. **Secure Token Storage**: Store CSRF tokens securely and regenerate them periodically.
3. **Validate Tokens**: Always validate the CSRF token before executing any sensitive actions.

#### Secure Coding Fixes

Here’s an example of a vulnerable and secure implementation:

**Vulnerable Code**

```html
<!-- Vulnerable Form -->
<form method="post" action="/change_email">
    <input type="email" name="email" placeholder="New Email">
    <button type="submit">Change Email</button>
</form>
```

**Secure Code**

```html
<!-- Secure Form -->
<form method="post" action="/change_email">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="email" name="email" placeholder="New Email">
    <button type="submit">Change Email</button>
</form>
```

### Configuration Hardening

1. **Set Secure Flags**: Ensure that cookies have the `HttpOnly` and `Secure` flags set.
2. **Content Security Policy (CSP)**: Implement a strict CSP to prevent inline scripts and external resources from executing.

#### Example CSP

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
```

### Practice Labs

For hands-on practice with CSRF, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on CSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By understanding the mechanics of CSRF, recent real-world examples, and effective defense strategies, you can better protect web applications from this type of attack.

---
<!-- nav -->
[[04-Conditions for a Successful CSRF Attack|Conditions for a Successful CSRF Attack]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]] | [[06-Exploiting CSRF Vulnerabilities|Exploiting CSRF Vulnerabilities]]
