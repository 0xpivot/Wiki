---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF

### Detection

Detecting CSRF attacks can be challenging, but there are several methods to identify potential vulnerabilities:

- **Logging and Monitoring**: Implement logging and monitoring to track unusual activity patterns.
- **Security Scanners**: Use automated security scanners to detect CSRF vulnerabilities in web applications.
- **Penetration Testing**: Conduct regular penetration testing to identify and mitigate CSRF risks.

### Prevention

Preventing CSRF attacks involves implementing robust security measures:

- **CSRF Tokens**: Always use CSRF tokens and include them as parameters in forms or requests.
- **Double Submit Cookie**: For stateless applications, use the double submit cookie defense.
- **SameSite Attribute**: Set the `SameSite` attribute on cookies to prevent them from being included in cross-site requests.

### Secure Coding Fixes

Here is an example of a vulnerable and a secure implementation of CSRF protection:

#### Vulnerable Code

```html
<form action="/submit" method="POST">
    <input type="hidden" name="csrf_token" value="12345">
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```

#### Secure Code

```html
<form action="/submit" method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```

### Configuration Hardening

Hardening configurations can further enhance CSRF protection:

- **Web Application Firewall (WAF)**: Configure WAF rules to block suspicious requests.
- **Content Security Policy (CSP)**: Implement CSP to restrict the sources of content that can be loaded.

### Real-World Example: CVE-2021-21972 Fix

For the WordPress REST API vulnerability (CVE-2021-21972), the fix involved adding CSRF protection to the affected endpoints. This included generating and validating CSRF tokens for each request.

### Practice Labs

To practice and master CSRF protection, consider the following real-world labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on CSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including CSRF, for hands-on learning.

By understanding the principles, mechanisms, and mitigation strategies for CSRF, developers can build more secure web applications and protect users from unauthorized actions.

---
<!-- nav -->
[[09-How to Prevent  Defend Against CSRF Attacks|How to Prevent  Defend Against CSRF Attacks]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/11-Practice Labs|Practice Labs]]
