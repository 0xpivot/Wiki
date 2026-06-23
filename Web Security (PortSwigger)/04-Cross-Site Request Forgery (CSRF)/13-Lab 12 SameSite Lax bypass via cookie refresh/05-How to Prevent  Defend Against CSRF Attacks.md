---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF Attacks

### Detection

To detect CSRF vulnerabilities, you can use automated tools like Burp Suite or OWASP ZAP. These tools can help identify forms and endpoints that lack CSRF tokens and check the `SameSite` attribute of session cookies.

### Prevention

To prevent CSRF attacks, follow these best practices:

1. **Use CSRF Tokens**: Ensure that all forms and AJAX requests include a unique CSRF token.
2. **Configure SameSite Attribute**: Set the `SameSite` attribute to `Strict` or `Lax` to mitigate cross-site request forgery.
3. **Secure Flag**: Always set the `Secure` flag on session cookies to ensure they are only transmitted over HTTPS.
4. **HttpOnly Flag**: Set the `HttpOnly` flag to prevent access to the cookie via JavaScript, reducing the risk of XSS attacks.

### Secure Coding Fixes

#### Vulnerable Code

```html
<form method="POST" action="/submit">
    <!-- Missing csrf_token field -->
    <!-- Other form fields -->
</form>
```

#### Fixed Code

```html
<form method="POST" action="/submit">
    <input type="hidden" name="csrf_token" value="unique_token_value">
    <!-- Other form fields -->
</form>
```

### Configuration Hardening

Ensure your web server and application frameworks are configured to set the `SameSite` attribute correctly. Here is an example of configuring the `SameSite` attribute in a Django application:

#### Django Settings

```python
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Real-World Lab Exercises

To practice detecting and preventing CSRF attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about CSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web app for learning security concepts.

By thoroughly understanding the mechanisms behind CSRF and implementing robust security measures, you can significantly reduce the risk of such attacks in your web applications.

---
<!-- nav -->
[[04-Detecting and Exploiting CSRF Vulnerabilities|Detecting and Exploiting CSRF Vulnerabilities]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/13-Lab 12 SameSite Lax bypass via cookie refresh/00-Overview|Overview]] | [[06-SameSite Attribute and CSRF Mitigation|SameSite Attribute and CSRF Mitigation]]
