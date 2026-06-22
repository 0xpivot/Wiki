---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against DOM-Based Vulnerabilities

### Detection

To detect DOM-based vulnerabilities, use automated tools such as static analysis tools and dynamic analysis tools. These tools can help identify potential vulnerabilities in the code.

### Prevention

1. **Input Validation**: Validate all user input on both the client and server sides.
2. **Content Security Policy (CSP)**: Implement a strict Content Security Policy to restrict the sources of executable scripts.
3. **Sanitize Inputs**: Sanitize user inputs to ensure they do not contain malicious scripts.

#### Secure Coding Practices

Here is an example of insecure code and its secure counterpart:

**Insecure Code:**

```javascript
document.getElementById("comment").innerHTML = "<script>alert('XSS')</script>";
```

**Secure Code:**

```javascript
document.getElementById("comment").textContent = "<script>alert('XSS')</script>";
```

By using `textContent` instead of `innerHTML`, we prevent the execution of any embedded scripts.

### Hardening Configuration

1. **Enable CSP**: Enable and configure a strict Content Security Policy.
2. **Disable Unnecessary Features**: Disable unnecessary features that can be exploited, such as inline scripts.

#### Example CSP Configuration

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://trustedscripts.example.com;";
```

This configuration restricts the sources of executable scripts to trusted domains.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs covering different types of web vulnerabilities, including DOM-based XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide practical experience in identifying and mitigating DOM-based vulnerabilities.

---
<!-- nav -->
[[04-Finding DOM Clobbering Vulnerabilities|Finding DOM Clobbering Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/07-Lab 7 Clobbering DOM attributes to bypass HTML filters/00-Overview|Overview]] | [[06-Testing for Cross-Site Scripting (XSS)|Testing for Cross-Site Scripting (XSS)]]
