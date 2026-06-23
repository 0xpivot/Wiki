---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Lab Exercise: Web Cache Poisoning via Ambiguous Requests

In this lab, we will simulate a web cache poisoning attack using ambiguous requests. The goal is to poison the cache so that the homepage serves a payload that alerts on the victim's cookie.

### Prerequisites

Before starting the lab, ensure you have an account on the Web Security Academy. You can sign up at [Portswigger.net/WebSecurity](https://portswigger.net/web-security).

### Steps to Complete the Lab

1. **Log In to the Web Security Academy**:
   - Visit [Portswigger.net/WebSecurity](https://portswigger.net/web-security).
   - Click on the sign-up button to create an account.
   - Log in to your account.

2. **Access the Lab**:
   - Click on "Academy".
   - Select "All Content".
   - Search for "host header attacks".
   - Select "Lab Number Three: Web Cache Poisoning via Ambiguous Requests".

3. **Understand the Vulnerability**:
   - The lab is vulnerable to web cache poisoning due to discrepancies in how the cache and the backend application handle ambiguous requests.
   - The goal is to perform a web cache poisoning attack that alerts on the victim's cookie.

4. **Perform the Attack**:
   - Identify the vulnerable parameter, which is likely the `Host` header.
   - Craft a request with an ambiguous `Host` header to poison the cache.
   - Ensure the poisoned cache serves the payload to the victim.

### Example Request and Response

Here’s an example of how to craft the request and observe the response:

```http
GET /index.html HTTP/1.1
Host: attacker.com
Cookie: session=abc123
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<html>
<head>
<script>alert(document.cookie)</script>
</head>
<body>
Welcome to the homepage!
</body>
</html>
```

### How to Prevent / Defend Against This Attack

#### Detection

Monitor your logs for unusual `Host` headers and unexpected cache behavior.

#### Prevention

1. **Validate the `Host` Header**: Ensure that the `Host` header is validated against a list of allowed domains.
2. **Unique Cache Keys**: Configure your caching proxy to use a unique cache key that includes the `Host` header.
3. **Regular Audits**: Regularly audit your caching proxy configurations to ensure they are secure.

### Secure Coding Practices

Here’s an example of how to securely validate the `Host` header in a Python Flask application:

```python
from flask import Flask, request

app = Flask(__name__)

@app.before_request
def validate_host_header():
    allowed_hosts = ['example.com', 'www.example.com']
    if request.host not in allowed_hosts:
        return "Invalid Host header", 400

@app.route('/')
def index():
    return "Welcome to the homepage!"

if __name__ == '__main__':
    app.run()
```

In this example, the `validate_host_header` function checks if the `Host` header matches any of the allowed hosts. If not, it returns a 400 error.

### Conclusion

Understanding and preventing HTTP Host Header attacks and web cache poisoning is crucial for maintaining the security of web applications. By validating the `Host` header, configuring unique cache keys, and regularly auditing your systems, you can significantly reduce the risk of these types of attacks.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to HTTP Host Header attacks and web cache poisoning.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another popular platform for learning web security through practical exercises.

By completing these labs, you can gain a deeper understanding of how to defend against HTTP Host Header attacks and web cache poisoning.

---
<!-- nav -->
[[05-HTTP Host Header Attacks|HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/07-Understanding HTTP Host Header Attacks|Understanding HTTP Host Header Attacks]]
