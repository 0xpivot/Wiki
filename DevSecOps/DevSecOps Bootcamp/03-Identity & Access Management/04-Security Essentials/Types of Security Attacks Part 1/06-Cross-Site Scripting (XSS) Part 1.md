---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Cross-Site Scripting (XSS)

### What is Cross-Site Scripting (XSS)?

Cross-Site Scripting (XSS) is a type of security vulnerability that allows an attacker to inject malicious scripts into web pages viewed by other users. These scripts can steal session IDs, tokens, and other sensitive information, leading to unauthorized access and other malicious activities.

### Why is XSS Important?

XSS attacks can lead to significant security risks, including session hijacking, defacement of websites, and theft of sensitive data. For example, in the Equifax breach in 2017 (CVE-2017-5638), an attacker exploited an unpatched Apache Struts vulnerability to inject malicious scripts, leading to the theft of sensitive personal data of millions of customers.

### How Does XSS Work?

An attacker injects a script into a web page, which is then executed by the victim's browser. This script can steal session IDs, tokens, and other sensitive information. There are three main types of XSS attacks: stored, reflected, and DOM-based.

#### Stored XSS

Stored XSS occurs when the injected script is permanently stored on the server, such as in a database. When a user views the page, the script is executed.

```html
<!-- Vulnerable code -->
<textarea name="comment"></textarea>
<button>Submit</button>

<!-- Injected script -->
<script>alert('XSS');</script>
```

#### Reflected XSS

Reflected XSS occurs when the injected script is included in a URL and is reflected back to the user. When the user clicks on the link, the script is executed.

```http
GET /search?q=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
```

#### DOM-Based XSS

DOM-based XSS occurs when the script is executed based on the Document Object Model (DOM) rather than being sent from the server.

```javascript
// Vulnerable code
var searchParam = window.location.search.substring(1);
document.getElementById('result').innerHTML = searchParam;
```

### Common Pitfalls and Detection

Common pitfalls include failing to properly sanitize user input and not using Content Security Policy (CSP) to mitigate XSS attacks. Tools like Burp Suite and ZAP can be used to detect XSS vulnerabilities.

### How to Prevent / Defend

#### Secure Coding Practices

Sanitize user input to prevent injection of malicious scripts. Use libraries and frameworks that provide built-in protection against XSS.

#### Configuration Hardening

Use Content Security Policy (CSP) to restrict the sources of scripts that can be executed. For example:

```http
Content-Security-Policy: default-src 'self'
```

#### Real-World Example: Equifax Breach

In the Equifax breach, an attacker exploited an unpatched Apache Struts vulnerability to inject malicious scripts, leading to the theft of sensitive personal data. To prevent such breaches, ensure that all software is up-to-date and use secure coding practices to prevent XSS attacks.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/05-Client-Side Request Forgery (CSRF)|Client-Side Request Forgery (CSRF)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/00-Overview|Overview]] | [[07-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]]
