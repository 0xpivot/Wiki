---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Server Request Forgery (SRF)

### What is Server Request Forgery (SRF)?

Server Request Forgery (SRF) is a type of security vulnerability that allows an attacker to trick a server into making unauthorized requests on behalf of the attacker. This can lead to unauthorized access, theft of sensitive data, and other malicious activities.

### Why is SRF Important?

SRF attacks can lead to significant security risks, including unauthorized access to sensitive data and systems. For example, in the Equifax breach in 2017 (CVE-2017-5638), an attacker exploited an unpatched Apache Struts vulnerability to inject malicious scripts, leading to the theft of sensitive personal data of millions of customers.

### How Does SRF Work?

An attacker can trick a server into making unauthorized requests by exploiting vulnerabilities in the application's validation and sanitization mechanisms. This can involve techniques such as injecting scripts via user input fields or exploiting vulnerabilities in third-party libraries.

#### Example: Injecting Scripts via User Input Fields

An attacker can inject a script via a user input field, such as a comment form.

```html
<!-- Vulnerable code -->
<textarea name="comment"></textarea>
<button>Submit</button>

<!-- Injected script -->
<script>alert('XSS');</script>
```

#### Example: Exploiting Third-Party Libraries

An attacker can exploit vulnerabilities in third-party libraries to inject malicious scripts.

```javascript
// Vulnerable library
function renderComment(comment) {
    document.getElementById('result').innerHTML = comment;
}

// Injected script
renderComment('<script>alert("XSS");</script>');
```

### Common Pitfalls and Detection

Common pitfalls include failing to properly validate and sanitize external JavaScript code. Tools like Burp Suite and ZAP can be used to detect SRF vulnerabilities.

### How to Prevent / Defend

#### Secure Coding Practices

Validate and sanitize all user input to prevent injection of malicious scripts. Use libraries and frameworks that provide built-in protection against SRF.

#### Configuration Hardening

Use Content Security Policy (CSP) to restrict the sources of scripts that can be executed. For example:

```http
Content-Security-Policy: default-src 'self'
```

#### Real-World Example: Equifax Breach

In the Equifax breach, an attacker exploited an unpatched Apache Struts vulnerability to inject malicious scripts, leading to the theft of sensitive personal data. To prevent such breaches, ensure that all external JavaScript code is properly validated and sanitized and use secure coding practices to prevent SRF.

### Conclusion

Understanding and preventing common security attacks such as session ID and token revocation, cross-site scripting (XSS), weak authentication checks, external JavaScript injection, and server request forgery (SRF) is crucial for maintaining the security of web applications. By implementing secure coding practices, configuration hardening, and using tools to detect vulnerabilities, you can significantly reduce the risk of security breaches.

### Practice Labs

To practice and reinforce your understanding of these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice detecting and preventing XSS, CSRF, and other web application vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

By engaging in these labs, you can gain hands-on experience in identifying and mitigating security vulnerabilities in web applications.

---
<!-- nav -->
[[08-External JavaScript Injection|External JavaScript Injection]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/00-Overview|Overview]] | [[10-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]]
