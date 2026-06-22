---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Finding and Exporting Host Header Vulnerabilities

To find and export host header vulnerabilities, several techniques and tools can be used:

### Techniques

1. **Manual Testing**: Sending crafted HTTP requests with different Host headers to observe the server's behavior.
2. **Automated Scanning**: Using automated tools to scan for host header vulnerabilities.

### Tools

- **Burp Suite**: A popular tool for manual testing and automated scanning.
- **OWASP ZAP**: An open-source tool for automated scanning and manual testing.

### Real-World Example: Manual Testing

Here is an example of manual testing using Burp Suite:

1. **Intercept Traffic**: Use Burp Suite to intercept HTTP traffic between the client and server.
2. **Modify Host Header**: Modify the Host header in the intercepted request.
3. **Observe Response**: Observe the server's response to determine if the Host header is trusted.

### HTTP Request Example of Manual Testing

Here is an example of an HTTP request with a modified Host header:

```http
GET /index.html HTTP/1.1
Host: evil.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
```

### HTTP Response Example of Manual Testing

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
    <title>Login Page</title>
</head>
<body>
    <h1>Welcome to evil.com</h1>
    <form method="POST">
        <input type="text" name="username">
        <input type="password" name="password">
        <button type="submit">Login</button>
    </form>
</body>
</html>
```

### Mermaid Diagram: Manual Testing Flow

A mermaid diagram can help visualize the manual testing flow involving the Host header:

```mermaid
sequenceDiagram
    participant Tester
    participant Server
    Tester->>Server: GET /index.html HTTP/1.1\r\nHost: evil.com
    Server-->>Tester: HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Login Page</title>\r\n</head>\r\n<body>\r\n<h1>Welcome to evil.com</h1>\r\n<form method="POST">\r\n<input type="text" name="username">\r\n<input type="password" name="password">\r\n<button type="submit">Login</button>\r\n</form>\r\n</body>\r\n</html>
```

---
<!-- nav -->
[[01-What is the HTTP Host Header|What is the HTTP Host Header]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/03-HTTP Host Header Attacks|HTTP Host Header Attacks]]
