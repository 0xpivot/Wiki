---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## How to Prevent Host Header Attacks

Preventing host header attacks involves implementing best practices, detecting common misconfigurations, and taking practical steps to secure applications.

### Best Practices

1. **Validate Host Headers**: Ensure that the Host header matches the expected domain.
2. **Use HTTPS**: Enforce HTTPS to prevent man-in-the-middle attacks.
3. **Content Security Policy (CSP)**: Implement CSP to mitigate XSS attacks.

### Common Misconfigurations

1. **Trust All Host Headers**: Trusting all Host headers without validation.
2. **Insecure Cookies**: Setting cookies without the `Secure` flag.

### Practical Steps

1. **Implement Input Validation**: Validate all input, including the Host header.
2. **Use Content Security Policy (CSP)**: Implement CSP to mitigate XSS attacks.
3. **Enforce HTTPS**: Enforce HTTPS to prevent man-in-the-middle attacks.

### Secure Coding Fixes

Here is an example of a vulnerable code snippet:

```python
# Vulnerable Code
def handle_request(request):
    host = request.headers.get('Host')
    if host == 'example.com':
        return render_template('index.html')
    else:
        return redirect(host)
```

Here is the corresponding secure code:

```python
# Secure Code
def handle_request(request):
    host = request.headers.get('Host')
    if host == 'example.com':
        return render_template('index.html')
    else:
        return "Invalid Host"
```

### Detection and Prevention

Detection involves monitoring logs and using automated tools to identify potential host header attacks. Prevention involves implementing the best practices and secure coding fixes mentioned above.

### Real-World Example: Secure Configuration

Here is an example of a secure configuration using Nginx:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        if ($host != 'example.com') {
            return 403;
        }
        proxy_pass http://backend;
    }
}
```

### HTTP Request Example of Secure Configuration

Here is an example of an HTTP request with a secure configuration:

```http
GET /index.html HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
```

### HTTP Response Example of Secure Configuration

Here is a corresponding HTTP response:

```http
HTTP/1.1 200 OK
Date: Mon, 27 Jul 2021 12:28:53 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: keep-alive

<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Welcome to Example.com</h1>
</body>
</html>
```

### Mermaid Diagram: Secure Configuration Flow

A mermaid diagram can help visualize the secure configuration flow involving the Host header:

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: GET /index.html HTTP/1.1\r\nHost: example.com
    Server-->>Client: HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Example Page</title>\r\n</head>\r\n<body>\r\n<h1>Welcome to Example.com</h1>\r\n</body>\r\n</html>
```

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/04-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/00-Overview|Overview]] | [[06-Password Reset Poisoning|Password Reset Poisoning]]
