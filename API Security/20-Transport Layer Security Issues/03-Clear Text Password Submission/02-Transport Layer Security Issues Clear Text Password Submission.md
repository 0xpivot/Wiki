---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Transport Layer Security Issues: Clear Text Password Submission

### Introduction to Transport Layer Security (TLS)

Transport Layer Security (TLS) is a cryptographic protocol designed to provide communications security over a computer network. It aims to prevent eavesdropping, tampering, and message forgery. TLS is widely used to secure web traffic, email, and other internet protocols. However, when TLS is not properly implemented or configured, it can lead to significant security vulnerabilities, such as clear text password submission.

### Understanding Clear Text Password Submission

Clear text password submission occurs when passwords are transmitted over the network in plain, unencrypted form. This means that anyone who intercepts the communication can easily read and misuse the password. This is a serious security issue because it can lead to unauthorized access to systems and data.

#### Why Clear Text Password Submission Matters

Clear text password submission is a critical security flaw because:

1. **Eavesdropping**: An attacker can intercept the network traffic and read the password.
2. **Man-in-the-Middle Attacks**: An attacker can position themselves between the client and server, capturing and possibly modifying the password.
3. **Data Leakage**: Passwords can be stored in logs, caches, or other unintended places, leading to further exposure.

#### How Clear Text Password Submission Works

When a user submits a password to an API endpoint, the password should be encrypted using TLS. However, if TLS is not enabled or is improperly configured, the password is sent in plain text. This can happen due to several reasons:

- **Misconfiguration**: The server might not enforce TLS.
- **Client-Side Issues**: The client might not use TLS when connecting to the server.
- **Mixed Content**: The server might serve some resources over HTTP instead of HTTPS.

### Real-World Examples of Clear Text Password Submission

Several high-profile breaches have occurred due to clear text password submission. Here are a few recent examples:

- **CVE-2021-21972**: A vulnerability in the Zoom app allowed passwords to be sent in plain text over HTTP.
- **CVE-2022-22965**: A misconfiguration in the Microsoft Exchange Server allowed passwords to be sent in plain text.

These examples highlight the importance of ensuring that all communication channels are properly secured with TLS.

### Detailed Example: Clear Text Password Submission in an API Request

Consider an API endpoint `/login` that accepts a username and password. Let's examine a scenario where the password is submitted in plain text.

#### Vulnerable Code Example

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # Process login
    return f"Welcome {username}!"

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the password is submitted in plain text. If the server is not configured to use TLS, the password can be intercepted.

#### HTTP Request and Response

Here is an example of an HTTP request and response:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 26

username=admin&password=admin
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 13

Welcome admin!
```

### How to Detect Clear Text Password Submission

Detecting clear text password submission involves monitoring network traffic and checking for unencrypted passwords. Tools like Wireshark can be used to capture and analyze network packets.

#### Using Wireshark

1. **Capture Traffic**: Use Wireshark to capture network traffic.
2. **Filter Packets**: Filter packets based on HTTP or specific endpoints.
3. **Inspect Data**: Look for plain text passwords in the captured packets.

### How to Prevent / Defend Against Clear Text Password Submission

#### Secure Configuration

Ensure that the server enforces TLS for all connections. This can be done by configuring the web server to redirect HTTP requests to HTTPS.

##### Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    location / {
        proxy_pass http://localhost:5000;
    }
}
```

#### Secure Coding Practices

Ensure that passwords are never logged or stored in plain text. Use strong hashing algorithms like bcrypt for storing passwords.

##### Secure Password Storage

```python
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)
```

#### Secure Client-Side Configuration

Ensure that the client uses TLS when connecting to the server. This can be enforced by setting the `secure` flag on cookies and using HSTS (HTTP Strict Transport Security).

##### HSTS Configuration

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
}
```

### Practical Labs for Hands-On Practice

To gain practical experience with securing APIs against clear text password submission, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on securing web applications.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

### Conclusion

Clear text password submission is a serious security issue that can lead to unauthorized access and data breaches. By understanding the risks, detecting vulnerabilities, and implementing secure configurations and coding practices, you can significantly reduce the likelihood of such issues occurring in your applications. Always ensure that all communication channels are properly secured with TLS to protect sensitive information.

---
<!-- nav -->
[[01-Introduction to Transport Layer Security Issues|Introduction to Transport Layer Security Issues]] | [[API Security/20-Transport Layer Security Issues/03-Clear Text Password Submission/00-Overview|Overview]] | [[API Security/20-Transport Layer Security Issues/03-Clear Text Password Submission/03-Practice Questions & Answers|Practice Questions & Answers]]
