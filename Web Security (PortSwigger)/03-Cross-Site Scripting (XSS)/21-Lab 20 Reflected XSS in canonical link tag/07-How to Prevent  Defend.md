---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend

### Detection

- **Web Application Firewalls (WAF)**: Use WAFs to detect and block suspicious requests.
- **Security Scanners**: Regularly scan your web application for vulnerabilities using tools like Burp Suite, OWASP ZAP, or Acunetix.

### Prevention

- **Input Validation**: Ensure all user inputs are validated and sanitized.
- **Output Encoding**: Encode all user inputs before rendering them in the HTML.
- **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.

### Secure Coding Fixes

#### Vulnerable Code

```php
<?php
$url = $_GET['url'];
echo "<link rel='canonical' href='$url'>";
?>
```

#### Secure Code

```php
<?php
$url = htmlspecialchars($_GET['url'], ENT_QUOTES, 'UTF-8');
echo "<link rel='canonical' href='$url'>";
?>
```

### Configuration Hardening

#### Content Security Policy (CSP)

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

### Additional Defenses

- **HTTP Headers**: Set appropriate HTTP headers like `X-XSS-Protection`.
- **Regular Audits**: Conduct regular security audits and penetration testing.

### Practice Labs

For hands-on practice with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various types of XSS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities, including XSS, for educational purposes.

By thoroughly understanding and implementing these preventive measures, you can significantly reduce the risk of XSS attacks on your web applications.

---
<!-- nav -->
[[06-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/08-Practice Labs|Practice Labs]]
