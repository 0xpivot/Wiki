---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Understanding HTTP Host Header Attacks

### Background Theory

HTTP Host Header attacks are a type of web security vulnerability that exploits the way web servers handle the `Host` header in HTTP requests. The `Host` header is used to specify the domain name of the server being requested. This header is crucial for virtual hosting, where multiple domains are hosted on the same IP address. However, if the server does not properly validate or sanitize the `Host` header, it can lead to various security issues, including authentication bypasses.

### The Role of the `Host` Header

The `Host` header is defined in the HTTP/1.1 protocol specification (RFC 7230). It is mandatory for HTTP/1.1 requests and is used to determine which website is being accessed. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this request, the server will serve the content for `www.example.com`.

### Enumerating Directories Using `robots.txt`

Before diving into the specifics of the `Host` header attack, it's important to understand how attackers might discover sensitive directories or pages. One common technique is to check for a `robots.txt` file. This file is used to instruct web crawlers (like search engines) about which parts of the site should not be indexed.

For example, consider the following `robots.txt` file:

```plaintext
User-agent: *
Disallow: /admin/
```

This file tells crawlers not to index the `/admin/` directory. An attacker might use this information to target the `/admin/` directory specifically.

### Example of `robots.txt` Discovery

Let's assume we are testing a web application and find the following `robots.txt` file:

```plaintext
User-agent: *
Disallow: /admin/
```

This indicates that the `/admin/` directory exists and is likely to contain sensitive information or functionality.

### Accessing the Admin Interface

Given the presence of the `/admin/` directory, an attacker might attempt to access it directly:

```http
GET /admin/ HTTP/1.1
Host: www.example.com
```

However, the server might respond with a message indicating that the admin interface is only available to local users:

```http
HTTP/1.1 403 Forbidden
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>403 Forbidden</title>
</head>
<body>
    <h1>Admin interface is only available to local users.</h1>
</body>
</html>
```

### Exploiting the `Host` Header

To bypass the authentication mechanism, an attacker might manipulate the `Host` header. For instance, setting the `Host` header to `localhost` or `127.0.0.1` might trick the server into thinking the request is coming from a local user:

```http
GET /admin/ HTTP/1.1
Host: localhost
```

If the server does not properly validate the `Host` header, it might allow the request, leading to unauthorized access.

### Real-World Examples

#### CVE-2019-16758

One notable example of a `Host` header vulnerability is CVE-2019-16758, which affected the WordPress REST API. In this case, an attacker could manipulate the `Host` header to bypass authentication and gain unauthorized access to administrative functions.

#### Recent Breaches

Another example is the breach of a popular e-commerce platform in 2021, where an attacker exploited a similar vulnerability to access the admin panel and steal customer data.

### How to Prevent / Defend

#### Detection

To detect potential `Host` header vulnerabilities, organizations can use tools like Burp Suite, ZAP, or custom scripts to test for improper handling of the `Host` header.

#### Prevention

1. **Validate the `Host` Header**: Ensure that the `Host` header matches the expected domain name. For example, if the server is configured to serve `www.example.com`, it should reject requests with a different `Host` header.

2. **Use Secure Coding Practices**: Implement proper input validation and sanitization for all headers, including the `Host` header.

3. **Configuration Hardening**: Configure web servers and applications to enforce strict validation of the `Host` header. For example, in Apache, you can use the `ServerName` directive to set the expected domain name:

    ```apache
    ServerName www.example.com
    ```

4. **Secure Configuration Files**: Ensure that configuration files like `robots.txt` do not expose sensitive information unnecessarily.

### Secure Code Fix

#### Vulnerable Code

Consider a simple PHP script that checks the `Host` header:

```php
<?php
$host = $_SERVER['HTTP_HOST'];
if ($host == 'localhost') {
    // Allow access to admin interface
} else {
    echo "Access denied";
}
?>
```

#### Fixed Code

To fix this vulnerability, ensure that the `Host` header is validated against the expected domain:

```php
<?php
$expected_host = 'www.example.com';
$host = $_SERVER['HTTP_HOST'];

if ($host === $expected_host) {
    // Allow access to admin interface
} else {
    echo "Access denied";
}
?>
```

### Practice Labs

For hands-on practice with `Host` header attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various web security topics, including `Host` header manipulation.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web vulnerabilities, including those related to HTTP headers.

### Conclusion

Understanding and defending against `Host` header attacks is crucial for maintaining the security of web applications. By properly validating and sanitizing the `Host` header, organizations can prevent unauthorized access and protect sensitive information. Regularly testing and updating configurations can help mitigate these risks effectively.

---
<!-- nav -->
[[02-HTTP Host Header Attacks|HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/03-Lab 2 Host header authentication bypass/00-Overview|Overview]] | [[04-Understanding HTTP Host Headers|Understanding HTTP Host Headers]]
