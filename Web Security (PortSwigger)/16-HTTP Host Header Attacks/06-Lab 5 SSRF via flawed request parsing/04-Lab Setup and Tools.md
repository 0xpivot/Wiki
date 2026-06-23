---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Lab Setup and Tools

For this lab, we will use Burp Suite to test for SSRF vulnerabilities involving the `Host` header. Burp Suite is a powerful toolkit for performing security testing of web applications.

### Setting Up Burp Suite

1. **Install Burp Suite**: Download and install Burp Suite from the official website.
2. **Start Burp Suite**: Launch Burp Suite and configure it to intercept traffic.

### Using Burp Suite Intruder

Burp Suite Intruder is a powerful tool for testing web applications for vulnerabilities. Here’s how to set it up:

1. **Capture Traffic**: Navigate to the target website and capture the HTTP request using Burp Suite.
2. **Send to Repeater**: Right-click the captured request and select “Send to Repeater”.
3. **Configure Repeater**: In the Repeater tab, modify the `Host` header to test for SSRF vulnerabilities.

### Testing for SSRF Vulnerabilities

Let’s walk through the steps to test for SSRF vulnerabilities using Burp Suite.

1. **Navigate to Home Page**: Click on the home page of the target website.
2. **Send Request to Repeater**: Capture the request and send it to Repeater.
3. **Modify Host Header**: Change the `Host` header to an attacker-controlled server, such as a Collaborator server.

### Example HTTP Request and Response

Here’s an example of an HTTP request and response:

```http
GET /path/to/resource HTTP/1.1
Host: www.example.com
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Hello World!</h1>
</body>
</html>
```

### Testing with Collaborator

Collaborator is a tool provided by Burp Suite to help detect SSRF vulnerabilities. Here’s how to use it:

1. **Get Collaborator Server**: Go to the Collaborator tab in Burp Suite and click “Get Collaborator Server”. Copy the server URL.
2. **Modify Host Header**: In the Repeater tab, replace the `Host` header with the Collaborator server URL.
3. **Send Request**: Send the modified request and observe the response.

### Example with Collaborator

```http
GET /path/to/resource HTTP/1.1
Host: collaborator.example.com
```

Response:

```http
HTTP/1.1 403 Forbidden
Content-Type: text/plain
Content-Length: 11

Forbidden
```

### Analyzing Results

If the response indicates a `403 Forbidden` status, it means the server is rejecting the request due to the invalid `Host` header. This is a good sign, but we need to check for inconsistencies or ambiguities in how the `Host` header is handled.

### Testing Partial Host Headers

Let’s test partial host headers to see if the server accepts them:

1. **Partial Host Header**: Modify the `Host` header to include a partial domain, such as `dot.runa`.
2. **Send Request**: Send the modified request and observe the response.

### Example with Partial Host Header

```http
GET /path/to/resource HTTP/1.1
Host: dot.runa
```

Response:

```http
HTTP/1.1 403 Forbidden
Content-Type: text/plain
Content-Length: 11

Forbidden
```

### Testing Subdomains

Next, let’s test subdomains to see if the server accepts them:

1. **Subdomain Host Header**: Modify the `Host` header to include a subdomain, such as `RanaKhalil.com`.
2. **Send Request**: Send the modified request and observe the response.

### Example with Subdomain Host Header

```http
GET /path/to/resource HTTP/1.1
Host: RanaKhalil.com
```

Response:

```http
HTTP/1.1 403 Forbidden
Content-Type: text/plain
Content-Length: 11

Forbidden
```

### Conclusion

By thoroughly testing the `Host` header, we can identify potential SSRF vulnerabilities and ensure that the server handles the `Host` header correctly. Proper validation and secure coding practices are essential to prevent such vulnerabilities.

### How to Prevent / Defend

#### Detection

1. **Use Burp Suite**: Regularly use Burp Suite to test for SSRF vulnerabilities.
2. **Monitor Logs**: Monitor server logs for suspicious activity related to the `Host` header.

#### Prevention

1. **Whitelist Hosts**: Maintain a whitelist of allowed hosts and validate the `Host` header against this list.
2. **Secure Libraries**: Use secure libraries that handle HTTP requests safely.
3. **Regular Audits**: Conduct regular security audits to identify and mitigate vulnerabilities.

### Secure Code Fix

Here’s an example of how to properly validate the `Host` header in a Python Flask application:

```python
from flask import Flask, request

app = Flask(__name__)

allowed_hosts = ['www.example.com', 'subdomain.example.com']

@app.before_request
def validate_host_header():
    host = request.headers.get('Host')
    if host not in allowed_hosts:
        return "Forbidden", 403

@app.route('/')
def index():
    return "Hello World!"

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the `Host` header is checked against a list of allowed hosts. If the host is not in the list, a `403 Forbidden` response is returned.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on SSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.

These labs provide practical experience in identifying and mitigating SSRF vulnerabilities involving the `Host` header.

### Summary

Understanding and properly handling the `Host` header is crucial for preventing SSRF vulnerabilities. By validating input, using secure libraries, and conducting regular audits, you can ensure that your web application is secure against such attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/03-HTTP Host Header Attacks|HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/05-Understanding HTTP Host Header Attacks|Understanding HTTP Host Header Attacks]]
