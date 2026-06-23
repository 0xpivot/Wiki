---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Understanding Host Header Vulnerabilities

Host header vulnerabilities occur when an application improperly handles or trusts the Host header. Attackers can manipulate the Host header to perform various types of attacks, such as:

- **Cross-Site Scripting (XSS)**: Injecting malicious scripts into web pages viewed by other users.
- **Cross-Site Request Forgery (CSRF)**: Forcing authenticated users to execute unwanted actions.
- **Phishing**: Redirecting users to malicious sites that mimic legitimate ones.

### How Attackers Manipulate the Host Header

Attackers can manipulate the Host header by sending requests with crafted headers. For example, an attacker might send a request with a Host header that points to a different domain:

```http
GET /index.html HTTP/1.1
Host: evil.com
```

If the server trusts the Host header without validation, it may serve content intended for `evil.com` instead of the intended domain.

### Real-World Examples of Host Header Attacks

Several real-world examples highlight the risks associated with host header vulnerabilities:

- **CVE-2018-16843**: A vulnerability in WordPress allowed attackers to bypass authentication by manipulating the Host header.
- **CVE-2019-11510**: A vulnerability in the Jenkins CI server allowed attackers to bypass authentication and gain administrative access by manipulating the Host header.

### HTTP Request Example of an Attack

Here is an example of an HTTP request with a manipulated Host header:

```http
GET /login.php HTTP/1.1
Host: evil.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
```

### HTTP Response Example of an Attack

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

### Mermaid Diagram: Attack Flow

A mermaid diagram can help visualize the attack flow involving the Host header:

```mermaid
sequenceDiagram
    participant Attacker
    participant Server
    Attacker->>Server: GET /login.php HTTP/1.1\r\nHost: evil.com
    Server-->>Attacker: HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Login Page</title>\r\n</head>\r\n<body>\r\n<h1>Welcome to evil.com</h1>\r\n<form method="POST">\r\n<input type="text" name="username">\r\n<input type="password" name="password">\r\n<button type="submit">Login</button>\r\n</form>\r\n</body>\r\n</html>
```

---
<!-- nav -->
[[08-Understanding HTTP Host Headers|Understanding HTTP Host Headers]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/00-Overview|Overview]] | [[10-Understanding the HTTP Host Header|Understanding the HTTP Host Header]]
