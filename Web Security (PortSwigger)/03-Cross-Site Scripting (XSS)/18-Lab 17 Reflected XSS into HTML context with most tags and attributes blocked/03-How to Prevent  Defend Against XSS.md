---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Detection

- **Web Application Firewalls (WAF)**: WAFs can detect and block malicious payloads.
- **Security Scanners**: Tools like Burp Suite, OWASP ZAP can scan for XSS vulnerabilities.

### Prevention

- **Input Validation**: Ensure that all user inputs are validated and sanitized.
- **Output Encoding**: Encode all user inputs before rendering them in the HTML context.
- **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.

### Secure Coding Fixes

#### Vulnerable Code

```html
<!-- Vulnerable Code -->
<body>
    <div><?php echo $_GET['q']; ?></div>
</body>
```

#### Secure Code

```html
<!-- Secure Code -->
<body>
    <div><?php echo htmlspecialchars($_GET['q'], ENT_QUOTES, 'UTF-8'); ?></div>
</body>
```

### Configuration Hardening

#### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Content-Security-Policy "default-src 'self'";
        add_header X-XSS-Protection "1; mode=block";
    }
}
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-31166**: A Reflected XSS vulnerability in WordPress plugins.
- **CVE-2022-22965**: A Reflected XSS vulnerability in Joomla.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**
- **OWASP Juice Shop**
- **DVWA (Damn Vulnerable Web Application)**
- **WebGoat**

These labs provide a controlled environment to practice identifying and exploiting XSS vulnerabilities.

---
<!-- nav -->
[[02-Exploiting Reflected XSS|Exploiting Reflected XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/04-Understanding the Lab Environment|Understanding the Lab Environment]]
