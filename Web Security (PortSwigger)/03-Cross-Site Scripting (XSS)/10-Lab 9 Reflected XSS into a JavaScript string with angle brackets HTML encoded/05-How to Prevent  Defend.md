---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend

### Detection

To detect XSS vulnerabilities, you can use automated tools like:

- **Burp Suite**: A popular web application security testing tool that includes features for detecting and exploiting XSS.
- **OWASP ZAP**: An open-source web application security scanner that can identify XSS vulnerabilities.

### Prevention

#### Secure Coding Practices

1. **Input Validation**: Validate all user inputs to ensure they conform to expected formats.
2. **Output Encoding**: Encode user inputs appropriately based on the context in which they are used.
   - **JavaScript Context**: Use libraries like `DOMPurify` to sanitize user inputs.
   - **HTML Context**: Use functions like `htmlspecialchars` in PHP or `HttpUtility.HtmlEncode` in .NET to encode special characters.

#### Example of Secure Coding

**Vulnerable Code**

```javascript
var userInput = '<%= user_input %>';
```

**Secure Code**

```javascript
var userInput = '<%= HttpUtility.JavaScriptStringEncode(user_input) %>';
```

### Configuration Hardening

1. **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources from which scripts can be loaded.
2. **HTTP Headers**: Use security-related HTTP headers like `X-XSS-Protection` and `X-Content-Type-Options`.

#### Example of CSP Configuration

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'";
```

### Mitigation Techniques

1. **Subresource Integrity (SRI)**: Use SRI to ensure that external scripts are not tampered with.
2. **Web Application Firewall (WAF)**: Deploy a WAF to filter out malicious requests.

### Hands-On Labs

For practical experience with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on various types of XSS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/04-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/00-Overview|Overview]] | [[06-Lab Setup|Lab Setup]]
