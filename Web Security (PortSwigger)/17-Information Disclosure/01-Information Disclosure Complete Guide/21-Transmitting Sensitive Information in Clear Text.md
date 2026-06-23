---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Transmitting Sensitive Information in Clear Text

### What Is Information Disclosure via Clear Text Transmission?

Information disclosure occurs when sensitive data is transmitted over a communication channel in plain text, making it susceptible to interception by unauthorized parties. This typically happens when HTTP is used instead of HTTPS. HTTP is a protocol that transmits data in plain text, which means anyone with access to the network traffic can read the data being sent. On the other hand, HTTPS encrypts the data, ensuring that even if the data is intercepted, it cannot be easily read.

### Why Does This Matter?

Sensitive information, such as passwords, credit card numbers, and personal identification details, should be protected during transmission. If this information is disclosed, it can lead to significant security risks, including identity theft, financial fraud, and unauthorized access to accounts.

### How Does This Work Under the Hood?

When a client sends a request to a server over HTTP, the data is sent in plain text. This means that if an attacker intercepts the network traffic, they can read the contents of the request and response. For example, consider the following HTTP request:

```http
GET /login HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```

And the corresponding response:

```http
HTTP/1.1 200 OK
Date: Mon, 23 May 2023 20:38:34 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <form action="/login" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username"><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
```

If this data is intercepted, the attacker can see the entire request and response, including any sensitive information.

### Real-World Examples

One of the most notable examples of information disclosure through clear text transmission is the Heartbleed bug (CVE-2014-0160). This vulnerability affected OpenSSL, a widely-used cryptographic library, and allowed attackers to steal sensitive information from memory, including private keys, passwords, and other confidential data. This was possible because the data was not properly encrypted during transmission.

### How to Prevent / Defend

#### Detection

To detect whether sensitive information is being transmitted in clear text, you can use tools like Wireshark or tcpdump to capture and analyze network traffic. These tools allow you to inspect the contents of HTTP requests and responses to identify any sensitive data being sent in plain text.

#### Prevention

To prevent information disclosure via clear text transmission, you should always use HTTPS instead of HTTP. HTTPS uses SSL/TLS to encrypt the data being transmitted, ensuring that even if the data is intercepted, it cannot be easily read.

Here is an example of an HTTPS request and response:

```http
GET /login HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

HTTP/1.1 200 OK
Date: Mon, 23 May 2023 20:38:34 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <form action="/login" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username"><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
```

In this case, the data is encrypted, and even if an attacker intercepts the traffic, they will not be able to read the contents of the request and response.

### Secure Coding Fixes

#### Vulnerable Code

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
    app.run()
```

#### Fixed Code

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # Process login
    return f"Welcome {username}!", 200, {'Content-Security-Policy': "default-src 'self'"}

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
```

In the fixed code, the `ssl_context` parameter is set to `'adhoc'`, which enables HTTPS for the Flask application. This ensures that the data is encrypted during transmission.

### Hands-On Labs

For hands-on practice with this topic, you can use the following labs:

- **PortSwigger Web Security Academy**: This lab provides exercises on detecting and preventing information disclosure via clear text transmission.
- **OWASP Juice Shop**: This lab includes scenarios where sensitive information is transmitted in clear text, and you can practice identifying and fixing these issues.

---
<!-- nav -->
[[20-Reviewing Third-Party Technology Configurations|Reviewing Third-Party Technology Configurations]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]] | [[22-Understanding Sensitive Data and Information Disclosure|Understanding Sensitive Data and Information Disclosure]]
