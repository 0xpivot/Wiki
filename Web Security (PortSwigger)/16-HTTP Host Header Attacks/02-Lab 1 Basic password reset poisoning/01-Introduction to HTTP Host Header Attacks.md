---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks

HTTP Host Header attacks are a class of vulnerabilities that arise due to improper handling of the `Host` header in HTTP requests. The `Host` header is used by the server to determine which website to serve when multiple websites are hosted on the same IP address. This header can be manipulated by attackers to redirect traffic to malicious sites, leading to various security issues such as phishing, session hijacking, and more.

In this chapter, we will delve into the specifics of HTTP Host Header attacks, focusing on a particular type of attack called "Password Reset Poisoning." We will cover the background theory, mechanics, real-world examples, and provide detailed steps on how to prevent and defend against these attacks.

### Background Theory

The `Host` header is a crucial part of HTTP requests. It specifies the domain name of the server being contacted. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

This header is essential because many servers host multiple domains on a single IP address. Without the `Host` header, the server would not know which site to serve.

#### Vulnerability in Password Reset Functionality

Many websites offer a password reset feature where users can request a new password via email. The process typically involves sending a link to the user's email address. This link often contains a unique token that allows the user to reset their password.

However, if the website does not properly validate the `Host` header, an attacker can manipulate the `Host` header to redirect the password reset link to a malicious domain. This is known as "Password Reset Poisoning."

### Mechanics of Password Reset Poisoning

Let's break down the steps involved in a password reset poisoning attack:

1. **User Request**: A user requests a password reset.
2. **Email Sent**: The website sends an email with a password reset link.
3. **Link Manipulation**: An attacker intercepts the email and modifies the `Host` header in the HTTP request to point to a malicious domain.
4. **Malicious Link**: The user clicks on the modified link, which redirects them to the attacker's domain.
5. **Credential Theft**: The attacker captures the user's credentials and gains unauthorized access.

#### Example Scenario

Consider a scenario where a user named Carlos requests a password reset. The website sends an email with the following link:

```
https://www.example.com/reset-password?token=abc123
```

An attacker intercepts this email and modifies the `Host` header in the HTTP request to point to a malicious domain:

```http
GET /reset-password?token=abc123 HTTP/1.1
Host: evil.com
```

When Carlos clicks on the link, he is redirected to `evil.com`, where the attacker can capture his credentials.

### Real-World Examples

Several real-world examples highlight the severity of HTTP Host Header attacks:

1. **CVE-2021-3116**: This vulnerability affected the popular web application framework Django. Attackers could manipulate the `Host` header to bypass certain security checks, leading to unauthorized access.
2. **CVE-2020-13777**: This vulnerability affected the WordPress plugin "WPML Multilingual CMS." Attackers could manipulate the `Host` header to inject malicious content into the website.

These examples demonstrate the critical nature of ensuring proper validation of the `Host` header.

### Detailed Steps to Perform a Password Reset Poisoning Attack

To illustrate the attack, let's walk through a detailed example using the PortSwigger Web Security Academy.

#### Step 1: Access the Lab

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Navigate to the "Academy" section.
4. Search for "Host header attacks" and select "Basic Password Reset Poisoning."

#### Step 2: Understand the Lab Environment

The lab environment includes:
- A vulnerable website (`www.example.com`).
- An email client on the exploit server (`exploit-01.portswigger.net`).

#### Step 3: Perform the Attack

1. **Request Password Reset**:
   - Log in to the vulnerable website using the provided credentials.
   - Navigate to the password reset functionality and request a password reset.

2. **Intercept the Email**:
   - The email containing the password reset link will be sent to the email client on the exploit server.
   - Intercept the email and note the link.

3. **Modify the Host Header**:
   - Use a tool like Burp Suite to modify the `Host` header in the HTTP request.
   - Set the `Host` header to a malicious domain (e.g., `evil.com`).

4. **Redirect the User**:
   - Send the modified link to Carlos.
   - When Carlos clicks on the link, he will be redirected to the malicious domain.

#### Code Example

Here is a complete example of the HTTP request and response:

```http
GET /reset-password?token=abc123 HTTP/1.1
Host: evil.com
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Password Reset</title>
</head>
<body>
    <h1>Password Reset</h1>
    <p>Please enter your new password:</p>
    <form action="/submit-new-password" method="POST">
        <input type="password" name="new_password" required>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

### Common Pitfalls and Mistakes

1. **Improper Validation**: Failing to validate the `Host` header can lead to successful attacks.
2. **Trust Issues**: Trusting user input without proper sanitization can result in security vulnerabilities.
3. **Configuration Errors**: Misconfigured web servers or applications can expose the system to attacks.

### How to Prevent / Defend Against HTTP Host Header Attacks

#### Detection

1. **Logging and Monitoring**: Implement logging and monitoring to detect unusual `Host` header values.
2. **IDS/IPS**: Use Intrusion Detection Systems (IDS) and Intrusion Prevention Systems (IPS) to identify and block suspicious activity.

#### Prevention

1. **Validate Host Header**: Ensure that the `Host` header matches the expected domain.
2. **Secure Configuration**: Configure web servers and applications to reject requests with invalid `Host` headers.
3. **Use HTTPS**: Enforce HTTPS to prevent man-in-the-middle attacks.

#### Secure Coding Fixes

Here is an example of how to securely validate the `Host` header in a web application:

```python
def validate_host_header(request):
    allowed_hosts = ['www.example.com']
    host_header = request.headers.get('Host')
    
    if host_header not in allowed_hosts:
        raise ValueError("Invalid Host header")
```

#### Configuration Hardening

Here is an example of how to configure Nginx to reject requests with invalid `Host` headers:

```nginx
server {
    listen 80;
    server_name www.example.com;

    if ($host != 'www.example.com') {
        return 444;
    }

    location / {
        # Your application logic here
    }
}
```

### Conclusion

HTTP Host Header attacks, particularly password reset poisoning, pose significant risks to web applications. By understanding the mechanics of these attacks and implementing robust preventive measures, organizations can significantly reduce the likelihood of successful attacks.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs, including the "Basic Password Reset Poisoning" lab.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another popular platform for learning web security.

By engaging with these labs, you can gain practical experience in identifying and defending against HTTP Host Header attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/02-Lab 1 Basic password reset poisoning/00-Overview|Overview]] | [[02-HTTP Host Header Attacks Password Reset Poisoning|HTTP Host Header Attacks Password Reset Poisoning]]
