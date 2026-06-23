---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against DOM-Based XSS

### Detection

Detecting DOM-based XSS vulnerabilities requires a combination of static analysis and dynamic testing. Static analysis tools can identify potential vulnerabilities in the code, while dynamic testing tools can simulate attacks and detect vulnerabilities in real-time.

### Prevention

Preventing DOM-based XSS vulnerabilities involves several best practices:

1. **Input Validation**: Validate all user inputs to ensure they do not contain malicious scripts.
2. **Output Encoding**: Encode all outputs to prevent the execution of malicious scripts.
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources of executable scripts.
4. **Sanitize User Inputs**: Sanitize user inputs to remove any potentially harmful characters or scripts.

### Secure Coding Fixes

#### Vulnerable Code

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Page</title>
</head>
<body>
    <script>
        window.addEventListener('message', function(event) {
            var data = JSON.parse(event.data);
            console.log(data.message);
        });
    </script>
</body>
</html>
```

#### Secure Code

```html
<!DOCTYPE html>
<html>
<head>
    <title>Secure Page</title>
</head>
<body>
    <script>
        window.addEventListener('message', function(event) {
            try {
                var data = JSON.parse(event.data);
                console.log(data.message);
            } catch (error) {
                console.error('Invalid JSON:', error);
            }
        });
    </script>
</body>
</html>
```

### Configuration Hardening

Implementing a Content Security Policy (CSP) can help prevent DOM-based XSS vulnerabilities. Here is an example of a CSP configuration:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline';
```

### Mitigations

Mitigating DOM-based XSS vulnerabilities involves several steps:

1. **Regular Security Audits**: Conduct regular security audits to identify and fix vulnerabilities.
2. **Security Training**: Train developers on secure coding practices to prevent vulnerabilities.
3. **Use of Security Tools**: Use security tools to detect and prevent vulnerabilities.

---
<!-- nav -->
[[07-Hands-On Practice|Hands-On Practice]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/00-Overview|Overview]] | [[09-Lab Setup and Environment|Lab Setup and Environment]]
