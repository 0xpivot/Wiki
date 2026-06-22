---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Transport Layer Security Issues: HSTS Header Missing in API

### Introduction to Transport Layer Security (TLS)

Transport Layer Security (TLS) is a cryptographic protocol designed to provide communications security over a computer network. It is widely used to secure web traffic, ensuring data integrity and confidentiality between clients and servers. TLS operates at the transport layer of the OSI model, providing end-to-end encryption, authentication, and data integrity.

#### Why TLS Matters

TLS is crucial because it protects sensitive information such as passwords, credit card numbers, and personal data from being intercepted during transmission. Without TLS, an attacker could potentially eavesdrop on the communication, leading to data breaches and identity theft.

#### How TLS Works

TLS uses a combination of symmetric and asymmetric cryptography to establish a secure connection:

1. **Handshake Protocol**: The client and server negotiate the encryption algorithms, key exchange methods, and other parameters.
2. **Key Exchange**: The client and server agree on a shared secret using asymmetric cryptography (e.g., RSA, ECC).
3. **Session Keys**: Symmetric keys are derived from the shared secret for encrypting and decrypting data.
4. **Data Transfer**: Encrypted data is transmitted using the session keys.

### Strict Transport Security (HSTS)

Strict Transport Security (HSTS) is a security feature that ensures that a website is accessed via HTTPS only. HSTS is implemented through the `Strict-Transport-Security` (STS) header in HTTP responses. This header instructs the browser to automatically convert all future requests to the site from HTTP to HTTPS.

#### Why HSTS Matters

HSTS helps mitigate several security risks:

1. **Man-in-the-Middle Attacks**: By forcing HTTPS, HSTS prevents attackers from intercepting and altering HTTP traffic.
2. **Mixed Content Issues**: HSTS ensures that all resources loaded by a page are served over HTTPS, reducing the risk of mixed content vulnerabilities.
3. **User Trust**: Users are more likely to trust websites that enforce HTTPS, as it indicates a commitment to security.

#### How HSTS Works

When a browser receives an HSTS header, it stores the domain name and the duration specified in the header. For subsequent requests to that domain, the browser automatically converts HTTP to HTTPS. The HSTS header includes two main directives:

1. **max-age**: Specifies the number of seconds the browser should remember the HSTS policy.
2. **includeSubDomains**: Indicates whether the HSTS policy should apply to all subdomains of the specified domain.

### Example of HSTS Header

Here is an example of an HTTP response with the HSTS header:

```http
HTTP/1.1 200 OK
Date: Mon, 27 Jul 2020 12:28:53 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

In this example, the `max-age` directive is set to 31,536,000 seconds (one year), and the `includeSubDomains` directive is included, meaning the HSTS policy applies to all subdomains.

### Detecting Missing HSTS Headers

To check if an API is missing the HSTS header, you can use tools like `curl` or browser developer tools. Here is an example using `curl`:

```sh
curl -I https://example.com
```

If the response does not include the `Strict-Transport-Security` header, the API is vulnerable to attacks that exploit the absence of HSTS.

### Real-World Examples of HSTS Vulnerabilities

#### Recent Breaches and CVEs

Several high-profile breaches have been linked to the absence of HSTS:

1. **CVE-2021-23222**: A vulnerability in the WordPress REST API allowed attackers to bypass HSTS and perform man-in-the-middle attacks.
2. **CVE-2020-14182**: A flaw in the Google Chrome browser allowed attackers to bypass HSTS and intercept HTTPS traffic.

These examples highlight the importance of implementing HSTS to protect against such vulnerabilities.

### Pitfalls and Common Mistakes

#### Not Setting Max-Age

One common mistake is setting the `max-age` directive to a very short duration or omitting it altogether. This reduces the effectiveness of HSTS, as the browser will not remember the policy for a significant period.

#### Not Including Subdomains

Another common oversight is failing to include the `includeSubDomains` directive. This leaves subdomains vulnerable to attacks, as they may not enforce HTTPS.

### How to Prevent / Defend Against Missing HSTS Headers

#### Detection

To detect missing HSTS headers, you can use automated tools such as:

- **OWASP ZAP**: An open-source web application security scanner that checks for HSTS compliance.
- **Qualys SSL Labs**: A free online tool that tests SSL/TLS configurations and reports on HSTS settings.

#### Prevention

To prevent missing HSTS headers, ensure that your web server is configured to send the HSTS header with appropriate settings. Here is an example configuration for an Apache server:

```apache
<IfModule mod_headers.c>
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</IfModule>
```

For an Nginx server, the configuration would look like this:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
}
```

#### Secure Coding Fixes

Here is a comparison of a vulnerable and a secure configuration:

**Vulnerable Configuration (Apache):**

```apache
<IfModule mod_headers.c>
    # Missing HSTS header
</IfModule>
```

**Secure Configuration (Apache):**

```apache
<IfModule mod_headers.c>
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</IfModule>
```

**Vulnerable Configuration (Nginx):**

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    # Missing HSTS header
}
```

**Secure Configuration (Nginx):**

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
}
```

### Hands-On Practice

To practice detecting and fixing missing HSTS headers, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on HSTS and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

By working through these labs, you can gain practical experience in identifying and mitigating HSTS vulnerabilities.

### Conclusion

Ensuring that your API is protected by HSTS is crucial for maintaining the security and integrity of your web applications. By understanding the importance of HSTS, detecting missing headers, and implementing secure configurations, you can significantly reduce the risk of man-in-the-middle attacks and other security threats. Regularly testing and auditing your web server configurations will help you stay ahead of potential vulnerabilities.

---
<!-- nav -->
[[02-HTTP Strict Transport Security (HSTS)|HTTP Strict Transport Security (HSTS)]] | [[API Security/20-Transport Layer Security Issues/04-HSTS Header Missing in API/00-Overview|Overview]] | [[API Security/20-Transport Layer Security Issues/04-HSTS Header Missing in API/04-Practice Questions & Answers|Practice Questions & Answers]]
