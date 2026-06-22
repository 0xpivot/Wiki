---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Detection

To detect XSS vulnerabilities, use automated tools such as:

- **Burp Suite**: Scan for XSS vulnerabilities using the scanner.
- **OWASP ZAP**: Use the active scanner to identify potential XSS issues.
- **Static Analysis Tools**: Tools like SonarQube can identify insecure coding practices that lead to XSS.

### Prevention

To prevent XSS vulnerabilities, follow these best practices:

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats and constraints.
2. **Output Encoding**: Encode all user inputs before reflecting them in the response. Use context-aware encoding techniques.
3. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded.
4. **Sanitize User Inputs**: Use libraries like OWASP Java HTML Sanitizer to sanitize user inputs before rendering them.

### Secure Coding Fixes

#### Vulnerable Code

```php
echo "<script>var name = '" . $_GET['name'] . "';</script>";
```

#### Secure Code

```php
$name = htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
echo "<script>var name = '" . $name . "';</script>";
```

### Configuration Hardening

#### Content Security Policy (CSP)

Add the following CSP header to your HTTP responses:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
```

This restricts the sources from which scripts can be loaded, reducing the risk of XSS attacks.

### Hands-On Labs

To practice and master XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of XSS labs, including reflected, stored, and DOM-based XSS.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing various web security vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

By thoroughly understanding and practicing these concepts, you can effectively identify and mitigate XSS vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/02-Exploiting the Vulnerability|Exploiting the Vulnerability]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/00-Overview|Overview]] | [[04-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]]
