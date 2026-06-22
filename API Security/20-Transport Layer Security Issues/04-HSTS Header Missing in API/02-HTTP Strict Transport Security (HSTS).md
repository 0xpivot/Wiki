---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## HTTP Strict Transport Security (HSTS)

HTTP Strict Transport Security (HSTS) is an important security feature that forces browsers to interact with a website over HTTPS instead of HTTP. This prevents man-in-the-middle (MITM) attacks and ensures that all communication is encrypted.

### How HSTS Works

When a server sends an HSTS header, it instructs the browser to remember that the site should only be accessed over HTTPS. Subsequent requests to the site are automatically converted to HTTPS, even if the user types in an HTTP URL.

#### Example of an HSTS Header

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

- `max-age`: Specifies the duration (in seconds) that the browser should remember the HSTS policy.
- `includeSubDomains`: Indicates that the HSTS policy applies to all subdomains of the specified domain.

### Why HSTS Matters

Without HSTS, an attacker could perform a MITM attack by intercepting the initial HTTP request and redirecting it to an insecure connection. HSTS mitigates this risk by ensuring that all connections are made over HTTPS.

### Real-World Example: CVE-2019-11324

In 2019, a vulnerability was discovered in the Apache HTTP Server where the server did not properly enforce HSTS policies. This allowed attackers to bypass HSTS and perform MITM attacks. The vulnerability was assigned the CVE identifier CVE-2019-11324.

#### Impact of CVE-2019-11324

- **Confidentiality**: Attackers could intercept and read sensitive data transmitted over HTTP.
- **Integrity**: Data could be altered during transmission without detection.

### How to Implement HSTS

To implement HSTS, you need to configure your web server to send the appropriate HSTS header. Here is an example configuration for an Apache server:

```apache
<VirtualHost *:443>
    ServerName www.example.com
    DocumentRoot /var/www/html

    <IfModule mod_headers.c>
        Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    </IfModule>

    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
</VirtualHost>
```

### Common Pitfalls in HSTS Implementation

- **Missing HSTS Header**: If the HSTS header is not sent, the browser will not enforce HTTPS connections.
- **Incorrect Configuration**: Incorrect values for `max-age` or missing `includeSubDomains` can limit the effectiveness of HSTS.

### How to Detect HSTS Issues

You can use tools like `curl` to check if the HSTS header is present:

```sh
curl -I https://www.example.com
```

Look for the `Strict-Transport-Security` header in the response.

### How to Prevent / Defend Against HSTS Issues

#### Secure Coding Fixes

Ensure that your web server is configured to send the HSTS header. Compare the following insecure and secure configurations:

**Insecure Configuration:**

```apache
<VirtualHost *:443>
    ServerName www.example.com
    DocumentRoot /var/www/html

    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
</VirtualHost>
```

**Secure Configuration:**

```apache
<VirtualHost *:443>
    ServerName www.example.com
    DocumentRoot /var/www/html

    <IfModule mod_headers.c>
        Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    </IfModule>

    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
</VirtualHost>
```

#### Hardening Measures

- **Regular Audits**: Regularly audit your web server configurations to ensure that HSTS is properly implemented.
- **Automated Tools**: Use automated tools like `hstspreload.org` to check if your site is eligible for preloading in browsers.

### Real-World Example: ReservePay API Vulnerability

Let's consider the ReservePay API vulnerability mentioned in the lecture. The issue was that the API did not include the HSTS header, making it susceptible to MITM attacks.

#### Analysis of the ReservePay API

The instructor analyzed the ReservePay API and observed that the API did not include the HSTS header. This means that the API could be accessed over HTTP, which is insecure.

#### HTTP Request and Response

Here is an example of an HTTP request and response to the ReservePay API:

**HTTP Request:**

```http
GET /account/images HTTP/1.1
Host: api.reservepay.com
User-Agent: curl/7.64.1
Accept: */*
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Date: Tue, 01 Aug 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: application/json
Content-Length: 123

{
    "amount": 100,
    "currency": "USD",
    "image": "AP.dot.image"
}
```

Notice that the response does not include the `Strict-Transport-Security` header.

#### How to Fix the Issue

To fix the issue, the ReservePay API server should be configured to send the HSTS header. Here is an example configuration:

```apache
<VirtualHost *:443>
    ServerName api.reservepay.com
    DocumentRoot /var/www/html

    <IfModule mod_headers.c>
        Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    </IfModule>

    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
</VirtualHost>
```

### Hands-On Lab Suggestions

For hands-on practice with HSTS and API security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on HSTS and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.

These labs provide practical experience in identifying and fixing HSTS issues in real-world scenarios.

### Conclusion

Ensuring that APIs use TLS and HSTS correctly is essential for maintaining the security of data transmitted over the network. By implementing HSTS, you can protect against MITM attacks and ensure that all communication is encrypted. Regular audits and hardening measures are necessary to maintain the security of your APIs.

By following the steps outlined in this chapter, you can effectively identify and mitigate HSTS issues in your APIs, ensuring that your data remains secure and confidential.

---
<!-- nav -->
[[API Security/20-Transport Layer Security Issues/04-HSTS Header Missing in API/01-Introduction to Transport Layer Security (TLS)|Introduction to Transport Layer Security (TLS)]] | [[API Security/20-Transport Layer Security Issues/04-HSTS Header Missing in API/00-Overview|Overview]] | [[03-Transport Layer Security Issues HSTS Header Missing in API|Transport Layer Security Issues HSTS Header Missing in API]]
