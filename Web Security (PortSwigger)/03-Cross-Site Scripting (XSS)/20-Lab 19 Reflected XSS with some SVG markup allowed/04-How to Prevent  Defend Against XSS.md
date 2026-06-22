---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Detection

To detect XSS vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.
- **XSS Hunter**: A tool that helps detect and analyze XSS vulnerabilities.

### Prevention

#### Secure Coding Practices

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats and lengths.
2. **Output Encoding**: Encode all user inputs before reflecting them back in the response. Use functions like `htmlspecialchars` in PHP or `HttpUtility.HtmlEncode` in .NET.
3. **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources of executable scripts.

#### Example of Secure Code

Here is an example of secure code that prevents XSS:

```php
<?php
$query = $_GET['query'];
$safeQuery = htmlspecialchars($query, ENT_QUOTES, 'UTF-8');
echo "<div id='results'>$safeQuery</div>";
?>
```

#### Configuration Hardening

1. **Disable Unnecessary Features**: Disable features that are not required, such as certain HTML tags and events.
2. **Use Strict Content Security Policy (CSP)**: Configure a strict CSP to limit the sources of executable scripts.

#### Example of CSP Configuration

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://trusted-cdn.com";
```

### Secure Coding Fixes

#### Vulnerable Code

```php
<?php
$query = $_GET['query'];
echo "<div id='results'>$query</div>";
?>
```

#### Fixed Code

```php
<?php
$query = $_GET['query'];
$safeQuery = htmlspecialchars($query, ENT_QUOTES, 'UTF-8');
echo "<div id='results'>$safeQuery</div>";
?>
```

### Real-World Mitigation

Real-world mitigation strategies include:

- **Regular Security Audits**: Conduct regular security audits to identify and fix vulnerabilities.
- **Security Training**: Train developers on secure coding practices and the latest security threats.
- **Patch Management**: Keep all software and dependencies up to date with the latest security patches.

### Conclusion

In this lab, we explored a Reflected XSS vulnerability where the web application allowed certain SVG tags and events. By injecting a script that called the `alert` function, we demonstrated the potential impact of such an attack. To prevent XSS, it is crucial to implement secure coding practices, use output encoding, and configure a strict Content Security Policy. Regular security audits and training are also essential to maintain the security of web applications.

### Practice Labs

For further practice, you can explore the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice different types of XSS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

By mastering XSS vulnerabilities and their prevention techniques, you can significantly enhance the security of web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/03-Exploiting the Vulnerability|Exploiting the Vulnerability]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/00-Overview|Overview]] | [[05-Identifying Input Fields|Identifying Input Fields]]
