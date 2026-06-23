---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks

HTTP Host Header attacks are a class of vulnerabilities that arise from improper handling of the `Host` header in HTTP requests. The `Host` header is used by the server to determine which website or virtual host should process the request. These attacks can lead to various security issues, including web cache poisoning, cross-site scripting (XSS), and other forms of injection attacks.

### What is the `Host` Header?

The `Host` header is a mandatory part of HTTP/1.1 requests. It specifies the domain name and port number of the server being contacted. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this example, the `Host` header tells the server that the request is intended for `www.example.com`.

### Why Does the `Host` Header Matter?

The `Host` header is crucial for servers that host multiple websites on a single IP address. Without the `Host` header, the server would not know which website to serve. However, this flexibility can also introduce security risks if the server does not properly validate or sanitize the `Host` header.

### Real-World Example: CVE-2021-23017

A notable real-world example of a `Host` header vulnerability is CVE-2021-23017, which affected the Apache HTTP Server. This vulnerability allowed attackers to bypass certain security restrictions by manipulating the `Host` header. By sending a specially crafted `Host` header, an attacker could cause the server to serve files from unintended locations, potentially leading to unauthorized data exposure.

### How to Prevent / Defend Against `Host` Header Attacks

#### Detection

To detect potential `Host` header attacks, you can monitor your logs for unusual or unexpected `Host` headers. Tools like `fail2ban` or custom log analysis scripts can help identify suspicious activity.

#### Prevention

1. **Validate the `Host` Header**: Ensure that the `Host` header matches a list of valid domains for your server. Reject requests with invalid `Host` headers.
2. **Use Strict Transport Security (HSTS)**: Enforce HTTPS connections to prevent man-in-the-middle attacks that might manipulate the `Host` header.
3. **Content Security Policy (CSP)**: Implement a strict CSP to mitigate the impact of XSS attacks that might result from `Host` header manipulation.

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

---
<!-- nav -->
[[01-Introduction to HTTP Host Header Attacks and Web Cache Poisoning|Introduction to HTTP Host Header Attacks and Web Cache Poisoning]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/00-Overview|Overview]] | [[03-Introduction to Web Caching|Introduction to Web Caching]]
