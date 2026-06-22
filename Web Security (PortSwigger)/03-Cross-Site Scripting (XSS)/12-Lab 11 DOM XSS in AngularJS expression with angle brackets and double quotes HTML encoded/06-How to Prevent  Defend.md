---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend

### Secure Coding Practices

1. **Input Validation**: Validate all user input to ensure it meets expected formats and constraints.
2. **Output Encoding**: Encode all output to prevent malicious scripts from being executed. Use libraries like `DOMPurify` to sanitize user input.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources from which scripts can be loaded.

### Secure Code Fix

#### Vulnerable Code

```html
<div>{{ searchTerm }}</div>
```

#### Fixed Code

```html
<div>{{ searchTerm | escape }}</div>
```

In this fixed code, the `escape` filter ensures that user input is properly encoded before being rendered in the DOM.

### Configuration Hardening

1. **Enable CSP**: Configure Content Security Policy to restrict script execution to trusted sources.
2. **Disable Dangerous Features**: Disable dangerous features like inline scripts and eval functions.
3. **Use Strict Contextual Escaping (SCE)**: Enable SCE in AngularJS to enforce strict output encoding.

### Mitigations

1. **Use Libraries**: Utilize libraries like `DOMPurify` to sanitize user input.
2. **Regular Audits**: Conduct regular security audits to identify and mitigate potential vulnerabilities.
3. **Educate Developers**: Educate developers about secure coding practices and the importance of input validation and output encoding.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/05-Hands-On Practice|Hands-On Practice]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/07-Real-World Examples|Real-World Examples]]
