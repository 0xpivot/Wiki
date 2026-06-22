---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## HTTP Host Header Attacks

### Introduction

HTTP Host Header attacks are a class of vulnerabilities that occur when a web application improperly validates or processes the `Host` header in an HTTP request. The `Host` header is used to specify the domain name of the server being contacted, and it plays a crucial role in virtual hosting, where multiple domains are hosted on the same IP address. If the `Host` header is not properly validated, an attacker can manipulate it to bypass security mechanisms, such as input validation, and potentially gain unauthorized access to sensitive resources.

### Understanding the `Host` Header

The `Host` header is a required part of an HTTP/1.1 request. It specifies the domain name of the server to which the request is being sent. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this example, the `Host` header indicates that the request is intended for `www.example.com`.

#### Purpose of the `Host` Header

- **Virtual Hosting**: Allows multiple websites to share the same IP address. The server uses the `Host` header to determine which website to serve.
- **Security**: Helps ensure that requests are directed to the correct domain, preventing misrouting and potential security issues.

### Vulnerabilities Related to the `Host` Header

When a web application fails to validate the `Host` header correctly, it can be exploited in several ways:

#### Bypassing Validation Logic

One common method is to find a legitimate vulnerable subdomain of the original domain to perform the attack. This is more challenging because the attacker needs to identify a subdomain that is both legitimate and vulnerable.

##### Example Scenario

Consider a web application that allows users to upload files. The application validates the `Host` header to ensure that uploads are only accepted from a trusted domain, say `uploads.example.com`. An attacker might attempt to bypass this validation by using a subdomain like `uploads-vulnerable.example.com`, which is also controlled by the attacker.

```http
POST /upload HTTP/1.1
Host: uploads-vulnerable.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
```

If the application does not properly validate the subdomain, the attacker could successfully upload malicious files.

### Ambiguous Requests and Duplicate Host Headers

Another technique is to send ambiguous requests with duplicate `Host` headers. Some applications may validate the first `Host` header and process the second without further validation.

##### Example Scenario

An attacker sends a request with two `Host` headers:

```http
GET /admin HTTP/1.1
Host: www.example.com
Host: evil.example.com
```

If the application validates the first `Host` header (`www.example.com`) and processes the second (`evil.example.com`) without additional checks, the attacker could potentially access administrative functions.

### Absolute URLs in the Request Line

Attacks can also involve supplying an absolute URL in the request line and modifying the `Host` header to contain an arbitrary value. Depending on how the backend processes the request, discrepancies can arise where precedence is given to the request line, leading to bypasses.

##### Example Scenario

An attacker crafts a request with an absolute URL in the request line and an arbitrary `Host` header:

```http
GET http://www.example.com/admin HTTP/1.1
Host: evil.example.com
```

If the application validates the absolute URL but ignores the `Host` header, the attacker could bypass validation and access sensitive resources.

### Indented HTTP Headers

Some servers interpret indented headers as line wrapping, treating them as part of the preceding header's value or ignoring them altogether. This can be exploited to bypass validation.

##### Example Scenario

An attacker sends a request with indented `Host` headers:

```http
GET /admin HTTP/1.1
Host: www.example.com
 Host: evil.example.com
```

If the server interprets the indented `Host` header as part of the preceding header, the attacker could potentially bypass validation.

### Real-World Examples and CVEs

Several real-world vulnerabilities have been discovered due to improper handling of the `Host` header. Here are a few notable examples:

- **CVE-2021-3186**: A vulnerability in the Apache HTTP Server allowed attackers to bypass certain security measures by manipulating the `Host` header.
- **CVE-2020-1938**: A vulnerability in the Nginx web server allowed attackers to bypass security restrictions by sending requests with multiple `Host` headers.

### How to Prevent / Defend Against HTTP Host Header Attacks

#### Detection

To detect potential HTTP Host Header attacks, implement logging and monitoring of incoming requests. Look for patterns such as:

- Multiple `Host` headers in a single request.
- Indented `Host` headers.
- Absolute URLs in the request line.

#### Prevention

1. **Strict Validation**: Ensure that the `Host` header is strictly validated against a list of trusted domains.
2. **Consistent Parsing**: Implement consistent parsing of HTTP headers to avoid discrepancies.
3. **Secure Configuration**: Harden web server configurations to reject requests with invalid or suspicious `Host` headers.

##### Secure Code Fix Example

**Vulnerable Code**

```python
def handle_request(request):
    host = request.headers.get('Host')
    if host == 'trusted.example.com':
        # Process request
        pass
```

**Fixed Code**

```python
def handle_request(request):
    host = request.headers.get('Host')
    if host and host.strip() == 'trusted.example.com':
        # Process request
        pass
```

#### Hardening Web Servers

Configure web servers to reject requests with invalid `Host` headers. For example, in Nginx:

```nginx
server {
    listen 80;
    server_name trusted.example.com;

    if ($host != 'trusted.example.com') {
        return 444;
    }

    location / {
        # Your configuration here
    }
}
```

### Hands-On Experience in Lab Environments

To gain practical experience with HTTP Host Header attacks, consider the following lab environments:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice various web security techniques, including HTTP Host Header attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for learning web security concepts.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

### Conclusion

HTTP Host Header attacks are a significant threat to web applications that do not properly validate or process the `Host` header. By understanding the vulnerabilities and implementing strict validation and hardening measures, developers can protect their applications from these types of attacks. Regularly testing and monitoring for suspicious activity is essential to maintaining the security of web applications.

---

This comprehensive guide covers the theoretical and practical aspects of HTTP Host Header attacks, providing deep insights into the vulnerabilities, real-world examples, and detailed steps to prevent and defend against such attacks.

---
<!-- nav -->
[[02-Finding and Exporting Host Header Vulnerabilities|Finding and Exporting Host Header Vulnerabilities]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/04-Hands-On Labs|Hands-On Labs]]
