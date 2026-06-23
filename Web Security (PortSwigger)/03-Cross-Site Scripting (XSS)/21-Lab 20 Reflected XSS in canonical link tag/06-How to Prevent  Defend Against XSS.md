---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Detection

To detect XSS vulnerabilities, use automated tools like Burp Suite, OWASP ZAP, or static analysis tools like SonarQube. These tools can help identify potential injection points and payloads.

### Prevention

To prevent XSS vulnerabilities, follow these best practices:

1. **Input Validation**: Validate all user input to ensure it meets expected formats and constraints.
2. **Output Encoding**: Encode all user input before rendering it in the browser. Use libraries like OWASP Java Encoder or Microsoft Anti-XSS Library.
3. **Content Security Policy (CSP)**: Implement a strict Content Security Policy to restrict the sources of executable scripts.
4. **HTTP Headers**: Set appropriate HTTP headers to mitigate XSS attacks, such as `X-Content-Type-Options`, `X-Frame-Options`, and `Strict-Transport-Security`.

### Secure Coding Fixes

#### Vulnerable Code

```html
<link rel="canonical" href="https://example.com/page?callback=<%= user_input %>">
```

#### Secure Code

```html
<link rel="canonical" href="https://example.com/page?callback=<%= encodeForHTML(user_input) %>">
```

### Configuration Hardening

#### Content Security Policy (CSP)

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'";
```

#### HTTP Headers

```nginx
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

---
<!-- nav -->
[[05-Detailed Walkthrough of the Lab|Detailed Walkthrough of the Lab]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/07-How to Prevent  Defend|How to Prevent  Defend]]
