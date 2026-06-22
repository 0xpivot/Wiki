---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Detection

To detect XSS vulnerabilities, use automated tools such as:

- **Burp Suite**: Scan web applications for vulnerabilities.
- **OWASP ZAP**: Free and open-source tool for finding security vulnerabilities.
- **Static Code Analysis Tools**: Tools like SonarQube and Fortify can help identify insecure coding practices.

### Prevention

To prevent XSS attacks, follow these best practices:

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats.
2. **Output Encoding**: Encode all user inputs before reflecting them back to the page. Use libraries like `OWASP Java Encoder` or `Microsoft Anti-XSS Library`.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts. Here is an example of a CSP header:

   ```http
   Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
   ```

### Secure Coding Fixes

#### Vulnerable Code

```html
<p>Your search query was: <%= request.getParameter("query") %></p>
```

#### Secure Code

```html
<p>Your search query was: <%= encoder.encodeForHTML(request.getParameter("query")) %></p>
```

### Configuration Hardening

#### Example of a Secure Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://trustedscripts.example.com;";
        root /var/www/html;
        index index.html;
    }
}
```

### Mitigation Strategies

1. **Use HTTPOnly Cookies**: Set the `HttpOnly` flag on cookies to prevent them from being accessed via JavaScript.
2. **Subresource Integrity (SRI)**: Use SRI to ensure that external scripts are not tampered with.

---
<!-- nav -->
[[06-How to Prevent  Defend Against Reflected XSS|How to Prevent  Defend Against Reflected XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]] | [[08-Identifying Input Parameters|Identifying Input Parameters]]
