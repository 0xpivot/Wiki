---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Missing HSTS

### What is HSTS?

HSTS (HTTP Strict Transport Security) is a security policy mechanism that helps to mitigate the risk of SSL/TLS stripping attacks by ensuring that browsers only communicate with the server over HTTPS.

#### How Does HSTS Work?

When a server sets the `Strict-Transport-Security` header, it instructs the browser to only communicate with the server over HTTPS for a specified period. This prevents man-in-the-middle attacks that attempt to downgrade the connection to HTTP.

### Real-World Example

In the case of the Equifax breach (CVE-2017-5638), the lack of HSTS contributed to the exposure of sensitive data due to SSL/TLS stripping attacks.

### How to Prevent / Defend

#### Detection

To detect missing HSTS, you can use tools like SSL Labs' SSL Test or Qualys SSL Server Test to check if the `Strict-Transport-Security` header is set.

#### Prevention

1. **Set HSTS Header**: Ensure that your server sets the `Strict-Transport-Security` header with appropriate parameters.

2. **Preload List**: Consider adding your domain to the HSTS preload list to ensure that browsers enforce HSTS from the first visit.

### Secure Configuration Example

#### Vulnerable Configuration

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;
}
```

#### Fixed Configuration

Ensure that the `Strict-Transport-Security` header is set:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
}
```

### Practice Labs

For hands-on experience with these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on HTTP authentication, SSL/TLS, and HSTS.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security assessments.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for learning about web application security.

By thoroughly understanding and implementing these security measures, you can significantly reduce the risk of transport layer security issues in your applications.

---
<!-- nav -->
[[API Security/20-Transport Layer Security Issues/02-Basic of Transport Layer Security/03-Clear Text Password Submission|Clear Text Password Submission]] | [[API Security/20-Transport Layer Security Issues/02-Basic of Transport Layer Security/00-Overview|Overview]] | [[API Security/20-Transport Layer Security Issues/02-Basic of Transport Layer Security/05-SSLTLS Issues|SSLTLS Issues]]
