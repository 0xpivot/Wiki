---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Detection

To detect XSS vulnerabilities, you can use automated tools like:

- **Burp Suite**: A popular tool for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.
- **Acunetix**: A commercial web vulnerability scanner.

These tools can help identify potential XSS vulnerabilities by analyzing the application's responses to various inputs.

### Prevention

To prevent XSS vulnerabilities, follow these best practices:

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats and constraints.
2. **Output Encoding**: Encode all user inputs before reflecting them back in the response. Use appropriate encoding methods based on the context (HTML, JavaScript, etc.).
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources of executable scripts.
4. **HTTP Headers**: Use HTTP headers like `X-XSS-Protection` and `X-Content-Type-Options` to enhance security.

### Secure Coding Fixes

#### Vulnerable Code

```html
<script>
    var searchTerm = "<%= request.getParameter('search') %>";
    document.write("You searched for: " + searchTerm);
</script>
```

#### Fixed Code

```html
<script>
    var searchTerm = "<%= request.getParameter('search').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;') %>";
    document.write("You searched for: " + searchTerm);
</script>
```

In the fixed code, we replace `<`, `>`, `"`, and `'` with their respective HTML entities to prevent script injection.

### Configuration Hardening

#### Content Security Policy (CSP)

Implement a strict CSP to restrict the sources of executable scripts:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
```

#### HTTP Headers

Use the following HTTP headers to enhance security:

```http
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
```

### Real-World Example: Secure Search Function

Consider the following secure implementation of the search function:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results</h1>
    <script>
        var searchTerm = "<%= request.getParameter('search').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;') %>";
        document.write("You searched for: " + searchTerm);
    </script>
</body>
</html>
```

In this implementation, all user inputs are properly encoded before being reflected back in the response, preventing any potential XSS attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/23-Lab 22 Reflected XSS into a JavaScript string with angle brackets and double quotes HTML encoded and single quotes escaped/04-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/23-Lab 22 Reflected XSS into a JavaScript string with angle brackets and double quotes HTML encoded and single quotes escaped/00-Overview|Overview]] | [[06-Real-World Examples|Real-World Examples]]
