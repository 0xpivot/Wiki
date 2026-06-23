---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Security Essentials: Types of Security Attacks Part 2

### Introduction to Security Issues in Libraries and Frameworks

When developing applications, developers often rely on third-party libraries and frameworks to speed up development and reduce the likelihood of introducing bugs. However, these libraries and frameworks can also introduce vulnerabilities if they contain security issues. These issues can be either intentional or accidental, but once discovered, they become public knowledge, which can be exploited by attackers.

#### Accidental Security Issues

Accidental security issues occur due to programming errors or oversights. When such an issue is discovered, the library or framework developers typically address it by releasing a new version that fixes the problem. This is particularly true for well-known and widely used frameworks such as React, Angular, Vue.js, and others.

### Public Disclosure of Security Issues

Once a security issue is discovered, it becomes public information. This means that everyone, including attackers, is aware of the vulnerability. There are several ways in which these vulnerabilities can be discovered:

- **Community Discovery**: Developers and security researchers within the community might identify the vulnerability during routine testing or while auditing the codebase.
- **Hacking Attempts**: Attackers might exploit the vulnerability to gain unauthorized access to systems or data, leading to the discovery of the issue.
- **Security Audits**: Formal security audits conducted by organizations or independent security firms can uncover vulnerabilities.

### Spread of Information

Once a vulnerability is discovered, the information spreads rapidly. This can happen through various channels:

- **Blog Articles**: Security researchers often publish detailed blog posts explaining the vulnerability and how it can be exploited.
- **YouTube Tutorials**: Video tutorials demonstrating the exploitation process can be found on platforms like YouTube.
- **Social Media**: News about the vulnerability can quickly spread through social media platforms like Twitter, LinkedIn, and Reddit.

### Real-World Examples

Let's look at some recent real-world examples of vulnerabilities discovered in popular frameworks:

#### Example 1: React XSS Vulnerability (CVE-2021-21985)

In 2021, a Cross-Site Scripting (XSS) vulnerability was discovered in React. This vulnerability allowed attackers to inject malicious scripts into web pages viewed by other users.

**Vulnerable Code:**
```javascript
// Vulnerable code snippet
const userInput = "<script>alert('XSS')</script>";
const element = <div dangerouslySetInnerHTML={{__html: userInput}} />;
```

**Fixed Code:**
```javascript
// Fixed code snippet
const userInput = "<script>alert('XSS')</script>";
const sanitizedInput = sanitize(userInput); // Sanitize user input
const element = <div dangerouslySetInnerHTML={{__html: sanitizedInput}} />;
```

**Explanation:**
The `dangerouslySetInnerHTML` prop in React allows rendering HTML content directly. If user input is not properly sanitized, it can lead to XSS attacks. In the fixed code, the `sanitize` function ensures that the user input is safe before being rendered.

#### Example 2: Angular Prototype Pollution (CVE-2020-28497)

In 2020, a prototype pollution vulnerability was discovered in Angular. This vulnerability could allow attackers to modify the prototype of objects, leading to unexpected behavior and potential security risks.

**Vulnerable Code:**
```typescript
// Vulnerable code snippet
@Component({
  selector: 'app-root',
  template: `<input [(ngModel)]="data.name">`
})
export class AppComponent {
  data = { name: '' };
}
```

**Fixed Code:**
```typescript
// Fixed code snippet
@Component({
  selector: 'app-root',
  template: `<input [(ngModel)]="data.name">`
})
export class AppComponent {
  data = { name: '' };

  constructor() {
    Object.freeze(this.data);
  }
}
```

**Explanation:**
Prototype pollution occurs when an attacker can modify the prototype of an object, affecting all instances of that object. In the fixed code, `Object.freeze` is used to prevent modifications to the `data` object.

### How to Prevent / Defend Against Vulnerabilities

To protect against vulnerabilities in third-party libraries and frameworks, developers should follow these best practices:

#### 1. Stay Updated

Regularly check for updates and patches released by the framework developers. Subscribe to their mailing lists and follow their social media accounts to stay informed.

#### 2. Use Version Control

Ensure that your application uses the latest stable version of the framework. Avoid using outdated versions that may contain known vulnerabilities.

#### 3. Security Audits

Conduct regular security audits of your application to identify and mitigate potential vulnerabilities. Use tools like SonarQube, OWASP ZAP, and Burp Suite for automated scanning.

#### 4. Input Validation and Sanitization

Always validate and sanitize user inputs to prevent common attacks like XSS and SQL injection. Use libraries like DOMPurify for sanitizing HTML content.

#### 5. Secure Coding Practices

Adopt secure coding practices such as least privilege, input validation, and error handling. Follow the OWASP Top Ten guidelines for web application security.

### Detection and Prevention Tools

Several tools can help detect and prevent vulnerabilities in your application:

- **Dependency Check**: A tool that scans your project dependencies for known vulnerabilities.
- **Snyk**: A service that monitors your dependencies for vulnerabilities and provides automatic fixes.
- **OWASP Dependency-Check**: An open-source tool that identifies project dependencies with known vulnerabilities.

### Conclusion

Using third-party libraries and frameworks can significantly speed up development, but it also introduces the risk of security vulnerabilities. By staying updated, conducting regular security audits, and following secure coding practices, developers can minimize these risks and ensure the security of their applications.

### Practice Labs

For hands-on experience with securing applications against vulnerabilities in third-party libraries and frameworks, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including XSS and SQL injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

By engaging with these labs, you can gain practical experience in identifying and mitigating security vulnerabilities in real-world scenarios.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 2/03-Introduction to Security Essentials in DevSecOps|Introduction to Security Essentials in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 2/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 2/05-Background on Apache Struts and Its Vulnerabilities|Background on Apache Struts and Its Vulnerabilities]]
