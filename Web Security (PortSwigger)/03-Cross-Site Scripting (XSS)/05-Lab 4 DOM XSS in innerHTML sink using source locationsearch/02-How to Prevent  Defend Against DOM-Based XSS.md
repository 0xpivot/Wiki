---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against DOM-Based XSS

### Detection

To detect DOM-Based XSS vulnerabilities, use automated tools such as static analysis tools and dynamic analysis tools. These tools can identify potential vulnerabilities in the code and help you understand the flow of data within the application.

### Prevention

1. **Sanitize Input**:
   Ensure that all user input is properly sanitized before being used to update the DOM. Use libraries or functions that can safely escape HTML and JavaScript code.

2. **Use Content Security Policy (CSP)**:
   Implement a Content Security Policy (CSP) to restrict the sources of executable scripts. This can help mitigate the impact of XSS attacks.

3. **Avoid Using `innerHTML`**:
   Avoid using `innerHTML` to update the DOM with user input. Instead, use safer methods such as `textContent` or `innerText`.

4. **Escape Output**:
   Escape output before rendering it in the DOM. Use functions like `encodeURIComponent` to ensure that special characters are properly encoded.

### Secure Coding Fixes

#### Vulnerable Code

```javascript
document.getElementById('content').innerHTML = decodeURIComponent(location.search.substring(1));
```

#### Secure Code

```javascript
document.getElementById('content').textContent = decodeURIComponent(location.search.substring(1));
```

By using `textContent` instead of `innerHTML`, the code ensures that the content is treated as plain text and not as executable HTML.

### Configuration Hardening

Ensure that your web server and application are configured securely. Disable unnecessary features and enable security features such as CSP.

### Mitigations

1. **Input Validation**:
   Validate all user input to ensure it meets expected formats and constraints.

2. **Output Encoding**:
   Encode all output to prevent malicious scripts from being executed.

3. **Security Headers**:
   Use security headers such as `X-Content-Type-Options`, `X-XSS-Protection`, and `Strict-Transport-Security` to enhance security.

### Hands-On Labs

To practice and gain hands-on experience with DOM-Based XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various types of XSS, including DOM-Based XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to learn and practice web security techniques.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/05-Lab 4 DOM XSS in innerHTML sink using source locationsearch/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/05-Lab 4 DOM XSS in innerHTML sink using source locationsearch/00-Overview|Overview]] | [[03-Understanding DOM-Based XSS|Understanding DOM-Based XSS]]
