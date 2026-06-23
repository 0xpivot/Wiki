---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against DOM-Based Open Redirection

### Detection

To detect DOM-based open redirection vulnerabilities, you can use automated tools like static analysis tools and dynamic analysis tools. These tools can help identify insecure JavaScript code that reads and manipulates URL parameters.

### Prevention

To prevent DOM-based open redirection vulnerabilities, follow these best practices:

1. **Validate and Sanitize Input**: Ensure that any input used to construct URLs is properly validated and sanitized.
2. **Use a Whitelist of Allowed URLs**: Only allow redirection to a predefined list of trusted URLs.
3. **Avoid Using Untrusted Input Directly**: Do not use untrusted input directly in URL construction. Instead, map the input to a safe internal identifier.

### Secure Coding Fix

Here is an example of how to securely handle the `redirect` parameter:

#### Vulnerable Code

```javascript
var urlParams = new URLSearchParams(window.location.search);
var redirectUrl = urlParams.get('redirect');
if (redirectUrl) {
    window.location.href = redirectUrl;
}
```

#### Secure Code

```javascript
var urlParams = new URLSearchParams(window.location.search);
var redirectParam = urlParams.get('redirect');
var allowedUrls = ['http://safe-url.com', 'https://another-safe-url.com'];
if (allowedUrls.includes(redirectParam)) {
    window.location.href = redirectParam;
} else {
    window.location.href = '/default-page';
}
```

### Configuration Hardening

Ensure that your web application framework and server configurations are hardened against such vulnerabilities. For example, configure your web server to reject requests with suspicious URL parameters.

### Real-World Example: Secure Configuration

Here is an example of a secure configuration in an Nginx server:

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        if ($arg_redirect ~* ^http://malicious\.com/) {
            return 403;
        }
        try_files $uri $uri/ /index.html;
    }
}
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs, including DOM-based vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and practicing web security.

By thoroughly understanding and practicing the concepts covered in this chapter, you will be well-equipped to identify, exploit, and defend against DOM-based open redirection vulnerabilities.

---
<!-- nav -->
[[03-Exploiting DOM-Based Open Redirection|Exploiting DOM-Based Open Redirection]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/00-Overview|Overview]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/05-Lab Setup and Environment|Lab Setup and Environment]]
