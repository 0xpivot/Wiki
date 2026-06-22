---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Content Security Policy (CSP)

Content Security Policy (CSP) is a more advanced mechanism that provides a broader range of protections against various types of attacks, including clickjacking. CSP allows you to specify which sources of content are allowed to be loaded in your web application.

### Syntax and Directives

CSP is defined using the `Content-Security-Policy` header. The header includes directives that specify the allowed sources of content. One of the key directives for preventing clickjacking is `frame-ancestors`.

#### Example Configuration

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: frame-ancestors 'self'
```

In this example, the `frame-ancestors` directive is set to `'self'`, meaning only the current site is allowed to frame the content.

### Implementation in Different Environments

#### Apache

To set the `Content-Security-Policy` header in Apache, you can modify the `.htaccess` file:

```apache
Header always set Content-Security-Policy "frame-ancestors 'self'"
```

#### Nginx

For Nginx, you can configure the header in the server block:

```nginx
add_header Content-Security-Policy "frame-ancestors 'self'";
```

### Multiple Domains

CSP also allows you to specify multiple domains that are allowed to frame your content. This can be useful in scenarios where you need to allow framing from specific trusted domains.

#### Example Configuration

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: frame-ancestors 'self' *.example.com https://trusted.example.com
```

In this example, the `frame-ancestors` directive allows framing from the current site (`'self'`), any subdomains of `example.com`, and the specific domain `https://trusted.example.com`.

### Wildcard Character

When using the wildcard character (`*`), be cautious as it can potentially allow arbitrary sites to frame your content.

#### Example Configuration

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: frame-ancestors 'self' *.example.com
```

In this example, the `frame-ancestors` directive allows framing from the current site (`'self'`) and any subdomains of `example.com`. However, using the wildcard character (`*`) can be risky and should be avoided unless absolutely necessary.

### Secure Coding Practices

To ensure your application is protected against clickjacking using CSP:

1. **Set Strict Framing Policies**: Always set the `frame-ancestors` directive to `'self'` or specific trusted domains.
2. **Test Thoroughly**: Test your application in different environments to ensure compatibility.
3. **Monitor and Update**: Regularly update your security policies and monitor for vulnerabilities.

### Detection and Mitigation

To detect and mitigate clickjacking attacks using CSP:

1. **Use Security Headers**: Ensure your application uses the `Content-Security-Policy` header.
2. **Regular Audits**: Conduct regular security audits to identify potential vulnerabilities.
3. **Educate Users**: Educate users about the risks of clicking on suspicious links or buttons.

### Real-World Example: Recent Breaches

A recent example of a clickjacking attack occurred in 2021, where attackers exploited a vulnerability in a popular social media platform. The attackers used a combination of clickjacking and phishing techniques to trick users into granting access to their accounts. By overlaying a hidden iframe over the login page, the attackers were able to capture user credentials and gain unauthorized access to the accounts.

### Secure Coding Practices

To ensure your application is protected against clickjacking:

1. **Set Strict Framing Policies**: Always set the `X-Frame-Options` header to `DENY` or `SAMEORIGIN`.
2. **Use Content Security Policy (CSP)**: Implement the `frame-ancestors` directive in your CSP to restrict framing.
3. **Test Thoroughly**: Test your application in different environments to ensure compatibility.
4. **Monitor and Update**: Regularly update your security policies and monitor for vulnerabilities.

### Detection and Mitigation

To detect and mitigate clickjacking attacks:

1. **Use Security Headers**: Ensure your application uses the `X-Frame-Options` and `Content-Security-Policy` headers.
2. **Regular Audits**: Conduct regular security audits to identify potential vulnerabilities.
3. **Educate Users**: Educate users about the risks of clicking on suspicious links or buttons.

### Practice Labs

To practice and reinforce your understanding of clickjacking and its prevention mechanisms, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on clickjacking and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning web security.

By following these guidelines and practicing with real-world examples, you can effectively protect your web applications from clickjacking attacks.

### Conclusion

Clickjacking is a serious threat to web security, but with the proper implementation of security headers like `X-Frame-Options` and `Content-Security-Policy`, you can significantly reduce the risk of such attacks. Always stay vigilant and regularly update your security measures to ensure the safety of your web applications.

---
<!-- nav -->
[[06-Combining X-Frame-Options and CSP|Combining X-Frame-Options and CSP]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[08-Content-Security-Policy (CSP) Header|Content-Security-Policy (CSP) Header]]
