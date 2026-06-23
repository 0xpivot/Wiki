---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against DOM-Based Vulnerabilities

### Detection

To detect DOM-based vulnerabilities, you can use automated tools like static analysis tools and dynamic analysis tools. Additionally, manual code review is essential to identify insecure JavaScript patterns.

### Prevention

1. **Sanitize Inputs**: Ensure that all user inputs are properly sanitized before being inserted into the DOM.
2. **Use Content Security Policy (CSP)**: Implement a strict CSP to restrict the execution of inline scripts and external resources.
3. **Escape Output**: Always escape output to prevent script injection.

#### Secure Coding Fix

Here is an example of how to securely handle user inputs in JavaScript:

```javascript
// Insecure code
document.getElementById("content").innerHTML = decodeURIComponent(document.cookie);

// Secure code
function sanitizeInput(input) {
    return input.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

document.getElementById("content").innerHTML = sanitizeInput(decodeURIComponent(document.cookie));
```

### Configuration Hardening

1. **Enable HTTP Headers**: Use headers like `X-XSS-Protection` and `Content-Security-Policy` to enhance security.
2. **Disable Inline Scripts**: Configure the CSP to disallow inline scripts.

#### Example: Secure Configuration

```http
HTTP/1.1 200 OK
Date: Tue, 01 Aug 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Security-Policy: default-src 'self'; script-src 'self'
X-XSS-Protection: 1; mode=block
```

---
<!-- nav -->
[[02-DOM-Based Vulnerabilities|DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/00-Overview|Overview]] | [[04-Identifying Insecure JavaScript|Identifying Insecure JavaScript]]
