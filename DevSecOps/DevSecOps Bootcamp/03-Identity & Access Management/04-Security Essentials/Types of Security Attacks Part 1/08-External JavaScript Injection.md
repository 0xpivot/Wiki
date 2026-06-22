---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## External JavaScript Injection

### What is External JavaScript Injection?

External JavaScript injection occurs when an application fails to properly validate and sanitize external JavaScript code, allowing an attacker to inject malicious scripts.

### Why is External JavaScript Injection Important?

External JavaScript injection can lead to unauthorized access, theft of sensitive data, and other malicious activities. For example, in the Target breach in 2013 (CVE-2013-0001), an attacker exploited external JavaScript injection to steal credit card information from millions of customers.

### How Does External JavaScript Injection Work?

An attacker can inject malicious scripts into a web page by exploiting vulnerabilities in the application's validation and sanitization mechanisms. This can involve techniques such as injecting scripts via user input fields or exploiting vulnerabilities in third-party libraries.

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

Common pitfalls include failing to properly validate and sanitize external JavaScript code. Tools like Burp Suite and ZAP can be used to detect external JavaScript injection vulnerabilities.

### How to Prevent / Defend

#### Secure Coding Practices

Validate and sanitize all user input to prevent injection of malicious scripts. Use libraries and frameworks that provide built-in protection against external JavaScript injection.

#### Configuration Hardening

Use Content Security Policy (CSP) to restrict the sources of scripts that can be executed. For example:

```http
Content-Security-Policy: default-src 'self'
```

#### Real--World Example: Target Breach

In the Target breach, an attacker exploited external JavaScript injection to steal credit card information from millions of customers. To prevent such breaches, ensure that all external JavaScript code is properly validated and sanitized and use secure coding practices to prevent external JavaScript injection.

---
<!-- nav -->
[[07-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/00-Overview|Overview]] | [[09-Server Request Forgery (SRF)|Server Request Forgery (SRF)]]
