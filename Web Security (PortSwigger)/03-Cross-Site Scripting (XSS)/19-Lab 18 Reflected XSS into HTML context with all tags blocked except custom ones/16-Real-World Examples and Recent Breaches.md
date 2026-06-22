---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Real-World Examples and Recent Breaches

### CVE-2021-21972: Shopify XSS Vulnerability

In 2021, Shopify disclosed an XSS vulnerability (CVE-2021-21972) that allowed attackers to inject malicious scripts into the checkout page. This vulnerability was due to insufficient input validation and sanitization.

#### Impact

- **Data Theft**: Attackers could steal sensitive information such as credit card details.
- **Session Hijacking**: Attackers could hijack user sessions and gain unauthorized access to accounts.

### Prevention and Mitigation

To prevent XSS vulnerabilities, several best practices should be followed:

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats and constraints.
2. **Output Encoding**: Encode all user inputs before rendering them in the HTML context.
3. **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources of executable scripts.

#### Secure Coding Practices

1. **Use Libraries**: Utilize libraries like `OWASP Java Encoder` or `DOMPurify` to encode user inputs.
2. **Sanitize Inputs**: Sanitize inputs using functions like `htmlspecialchars` in PHP or `escape` in JavaScript.

```php
// Example of encoding user input in PHP
$userInput = htmlspecialchars($_GET['query'], ENT_QUOTES, 'UTF-8');
echo "<h1>Search Results for \"$userInput\"</h1>";
```

```javascript
// Example of encoding user input in JavaScript
const userInput = document.getElementById('search').value;
document.getElementById('results').innerHTML = `<h1>Search Results for "${DOMPurify.sanitize(userInput)}"</h1>`;
```

### Configuration Hardening

1. **Enable CSP**: Configure a strict CSP to limit the sources of executable scripts.
2. **Disable Dangerous Features**: Disable features like inline scripts and eval() in the CSP.

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

### Detection Tools

1. **Static Analysis Tools**: Use tools like SonarQube or ESLint to detect potential XSS vulnerabilities in code.
2. **Dynamic Analysis Tools**: Use tools like Burp Suite or OWASP ZAP to test for XSS vulnerabilities in live applications.

### Hands-On Labs

For practical experience in testing and defending against XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice XSS attacks and defenses.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

---
<!-- nav -->
[[15-Lab Walkthrough Reflected XSS with Custom Tags|Lab Walkthrough Reflected XSS with Custom Tags]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[17-Testing for Classic XSS Vulnerabilities|Testing for Classic XSS Vulnerabilities]]
