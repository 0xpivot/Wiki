---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend

### Secure Coding Practices

To prevent XSS attacks, it is essential to follow secure coding practices:

1. **Input Validation**: Validate all user inputs to ensure they meet the expected format and constraints.
2. **Output Encoding**: Encode user inputs before rendering them on the page. Use appropriate encoding techniques based on the context (HTML, JavaScript, etc.).
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded and executed.

### Example of Secure Code

Here is an example of secure code that properly encodes user inputs:

```javascript
function displaySearchResult(userInput) {
    let encodedInput = userInput.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    let templateString = `The search result is: ${encodedInput}`;
    document.write(templateString);
}

// User input: <script>alert('XSS');</script>
displaySearchResult("<script>alert('XSS');</script>");
```

In this example, the user input is encoded using HTML entity encoding before being inserted into the template string. This prevents the script from being executed.

### Content Security Policy (CSP)

A Content Security Policy (CSP) is a security feature that helps prevent XSS attacks by specifying which sources of content are allowed to be executed on a web page. Here is an example of a CSP header:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.example.com;
```

This CSP header restricts scripts to be loaded only from the same origin (`'self'`) and a trusted CDN (`https://trusted-cdn.example.com`).

### Detection and Prevention Tools

Several tools can help detect and prevent XSS vulnerabilities:

- **OWASP ZAP**: An open-source web application security scanner that can detect XSS vulnerabilities.
- **Burp Suite**: A comprehensive toolkit for web application security testing that includes features for detecting and exploiting XSS.
- **Snyk**: A security platform that integrates with CI/CD pipelines to detect and fix vulnerabilities, including XSS.

### Hands-On Labs

For hands-on practice with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different types of XSS vulnerabilities and exploitation techniques.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several XSS challenges.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable to common web application attacks, including XSS.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/03-Exploiting the Vulnerability|Exploiting the Vulnerability]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/00-Overview|Overview]] | [[05-Understanding the Vulnerability|Understanding the Vulnerability]]
