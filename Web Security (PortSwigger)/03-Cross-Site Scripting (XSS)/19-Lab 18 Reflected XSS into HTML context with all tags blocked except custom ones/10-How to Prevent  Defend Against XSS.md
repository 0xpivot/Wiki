---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Detection

To detect XSS vulnerabilities, you can use automated tools like:

- **Burp Suite**: Scan for XSS vulnerabilities using the Intruder and Scanner modules.
- **OWASP ZAP**: Another popular tool for detecting XSS and other web application vulnerabilities.

### Prevention

1. **Input Validation and Sanitization**:
   - Validate all user inputs to ensure they meet expected formats.
   - Sanitize inputs to remove or escape potentially dangerous characters.

2. **Content Security Policy (CSP)**:
   - Implement CSP to restrict the sources from which scripts can be loaded.
   - Example CSP header:
     ```http
     Content-Security-Policy: default-src 'self'; script-src 'self'
     ```

3. **Output Encoding**:
   - Encode all user inputs before embedding them into the HTML response.
   - Use libraries like `htmlspecialchars` in PHP or `DOMPurify` in JavaScript to encode inputs.

### Secure Coding Fixes

#### Vulnerable Code

```php
<?php
$query = $_GET['query'];
echo "<h1>Search Results for: $query</h1>";
?>
```

#### Secure Code

```php
<?php
$query = $_GET['query'];
$safeQuery = htmlspecialchars($query, ENT_QUOTES, 'UTF-8');
echo "<h1>Search Results for: $safeQuery</h1>";
?>
```

### Configuration Hardening

Ensure that your web server and application configurations are hardened against XSS attacks:

- **Disable Dangerous Headers**:
  - Disable headers like `X-XSS-Protection` if they are not necessary.
- **Enable Strict Transport Security (HSTS)**:
  - Ensure that all connections are encrypted using HTTPS.
  - Example HSTS header:
    ```http
    Strict-Transport-Security: max-age=31536000; includeSubDomains
    ```

### Real-World Example: Secure Configuration

Consider a real-world example where a web application uses both CSP and HSTS to enhance security:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Hands-On Practice Labs

For further practice and mastery of XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on different types of XSS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities, including XSS, for educational purposes.

By thoroughly understanding and practicing these concepts, you can significantly improve your ability to detect and prevent XSS vulnerabilities in web applications.

---

This comprehensive explanation covers every aspect of the lab, providing deep insights into XSS vulnerabilities, their mechanics, real-world examples, and robust defense mechanisms.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/09-Hands-On Practice|Hands-On Practice]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[11-How to Prevent  Defend|How to Prevent  Defend]]
