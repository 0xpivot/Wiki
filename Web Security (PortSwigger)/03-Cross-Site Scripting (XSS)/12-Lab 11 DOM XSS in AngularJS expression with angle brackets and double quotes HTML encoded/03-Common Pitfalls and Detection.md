---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Common Pitfalls and Detection

### Common Mistakes

1. **Improper Input Validation**: Failing to validate user input can lead to successful XSS attacks.
2. **Insufficient Output Encoding**: Not properly encoding output can allow malicious scripts to be executed.
3. **Reliance on Client-Side Sanitization**: Relying solely on client-side sanitization can be bypassed by attackers.

### Detection

1. **Static Analysis Tools**: Use tools like ESLint, SonarQube, or OWASP ZAP to scan for potential XSS vulnerabilities.
2. **Dynamic Analysis Tools**: Use tools like Burp Suite or OWASP ZAP to test for XSS vulnerabilities during runtime.
3. **Manual Testing**: Perform manual testing by injecting payloads and observing the behavior.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/02-Background Theory|Background Theory]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/00-Overview|Overview]] | [[04-Exploiting the DOM-Based XSS Vulnerability|Exploiting the DOM-Based XSS Vulnerability]]
