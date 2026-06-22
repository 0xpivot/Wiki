---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend

### Detection

To detect XSS vulnerabilities, use automated tools like static analysis tools (e.g., SonarQube) and dynamic analysis tools (e.g., Burp Suite). These tools can help identify potential XSS vulnerabilities in your application.

### Prevention

1. **Input Validation**: Validate all user inputs to ensure they do not contain malicious scripts. Use regular expressions to filter out disallowed characters and tags.

2. **Output Encoding**: Encode all user inputs before reflecting them in the HTML output. Use libraries like `OWASP Java Encoder` to encode user inputs.

3. **Content Security Policy (CSP)**: Implement a Content Security Policy (CSP) to restrict the sources from which scripts can be loaded. This helps prevent malicious scripts from executing.

4. **Secure Coding Practices**: Follow secure coding practices such as the OWASP Top Ten and the OWASP Application Security Verification Standard (ASVS).

### Secure Code Fix

#### Vulnerable Code

```java
String userInput = request.getParameter("query");
response.getWriter().write("<div>" + userInput + "</div>");
```

#### Fixed Code

```java
import org.owasp.encoder.Encode;

String userInput = request.getParameter("query");
response.getWriter().write("<div>" + Encode.forHtml(userInput) + "</div>");
```

### Configuration Hardening

#### Example CSP Configuration

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://trusted-scripts.example.com;";
```

### Mitigations

1. **Use Libraries**: Use established libraries for encoding and validating user inputs.
2. **Regular Audits**: Conduct regular security audits and penetration testing to identify and mitigate vulnerabilities.
3. **Educate Developers**: Educate developers about secure coding practices and the importance of input validation and output encoding.

---
<!-- nav -->
[[10-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[12-Identifying Allowed Tags|Identifying Allowed Tags]]
