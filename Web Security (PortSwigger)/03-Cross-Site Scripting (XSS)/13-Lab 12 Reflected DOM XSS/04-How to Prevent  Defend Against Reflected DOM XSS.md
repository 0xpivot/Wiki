---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against Reflected DOM XSS

### Secure Coding Practices

To prevent Reflected DOM XSS, follow these secure coding practices:

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats and lengths.
2. **Output Encoding**: Encode all user inputs before reflecting them in the response. Use context-aware encoding techniques such as HTML entity encoding, URL encoding, and JavaScript string escaping.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts and prevent inline scripts from executing.

#### Example Secure Code

Here is an example of secure code that prevents Reflected DOM XSS:

```javascript
var param = window.location.search.substring(1);
document.getElementById("output").textContent = param;
```

By using `textContent` instead of `innerHTML`, we prevent the execution of any injected scripts.

### Configuration Hardening

To further harden the application against Reflected DOM XSS, configure the server and client settings as follows:

- **Disable Inline Scripts**: Configure the server to disable inline scripts by setting the `Content-Security-Policy` header.
- **Enable HTTP Headers**: Enable HTTP headers such as `X-XSS-Protection` to provide additional protection against XSS attacks.

#### Example Configuration

Here is an example of configuring the server to set the `Content-Security-Policy` header:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Content-Security-Policy "default-src 'self'";
        try_files $uri $uri/ /index.html;
    }
}
```

### Detection and Prevention Tools

To detect and prevent Reflected DOM XSS, use the following tools:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.
- **SonarQube**: A static code analysis tool that identifies security vulnerabilities in the source code.

### Practice Labs

To practice and master the skills required to detect and prevent Reflected DOM XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice different types of XSS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

---
<!-- nav -->
[[03-Exploiting Reflected DOM XSS|Exploiting Reflected DOM XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/00-Overview|Overview]] | [[05-Understanding Reflected DOM XSS|Understanding Reflected DOM XSS]]
