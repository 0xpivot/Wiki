---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Background Theory

### What is Template Literal?

A template literal is a string literal that allows embedded expressions. It is denoted by backticks (`) and can contain placeholders for variables or expressions. For example:

```javascript
let name = "Alice";
let greeting = `Hello, ${name}!`;
console.log(greeting); // Output: Hello, Alice!
```

### Why is XSS Dangerous?

XSS attacks can lead to several severe consequences:

- **Data Theft**: Attackers can steal cookies, session tokens, and other sensitive information.
- **Session Hijacking**: By stealing session tokens, attackers can impersonate legitimate users.
- **Phishing**: Malicious scripts can redirect users to fake login pages to capture their credentials.
- **Defacement**: Attackers can alter the appearance of a website to spread misinformation or propaganda.
- **Malware Distribution**: Malicious scripts can download and execute malware on the victim's machine.

### Real-World Examples

#### CVE-2021-21972: Microsoft Exchange Server

In March 2021, a critical vulnerability was discovered in Microsoft Exchange Server, which allowed attackers to execute arbitrary JavaScript code via a reflected XSS attack. This vulnerability affected versions 2013, 2016, and 2019, and could be exploited to gain unauthorized access to email accounts.

#### CVE-2020-14882: Zoom

In July 2020, a reflected XSS vulnerability was found in Zoom's web portal. This vulnerability allowed attackers to inject malicious scripts into the web portal, potentially leading to session hijacking and data theft.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/03-Exploiting the Vulnerability|Exploiting the Vulnerability]]
