---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Common Pitfalls and Detection

### Common Pitfalls

When exploiting Reflected DOM XSS, it is important to avoid common pitfalls such as:

- **Encoding Issues**: Ensure that the injected script is properly encoded to bypass any encoding mechanisms.
- **Input Validation**: Some applications may perform basic input validation, which can prevent simple injections.
- **Content Security Policy (CSP)**: Modern browsers support CSP, which can mitigate XSS attacks by restricting the sources of executable scripts.

### Detection Techniques

To detect Reflected DOM XSS vulnerabilities, you can use the following techniques:

- **Manual Testing**: Manually test input fields by injecting various payloads and observing the behavior.
- **Automated Scanners**: Use automated scanners like Burp Suite, OWASP ZAP, or Acunetix to scan for XSS vulnerabilities.
- **Static Analysis Tools**: Use static analysis tools like SonarQube or Fortify to identify potential XSS vulnerabilities in the source code.

### Real-World Breach Example

A notable real-world breach involving Reflected DOM XSS was the **Yahoo! Data Breach** in 2013. Attackers exploited a vulnerability in Yahoo!'s login page, which allowed them to inject malicious scripts and steal user credentials.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/00-Overview|Overview]] | [[03-Exploiting Reflected DOM XSS|Exploiting Reflected DOM XSS]]
