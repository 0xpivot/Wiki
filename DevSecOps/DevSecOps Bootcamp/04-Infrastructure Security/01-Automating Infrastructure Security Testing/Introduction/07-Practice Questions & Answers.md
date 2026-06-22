---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What are some key components of infrastructure that should be scanned for security vulnerabilities?**

Infrastructure scanning involves assessing various components for potential security weaknesses. Key areas include network devices (routers, switches), servers, firewalls, and cloud services. Specific vulnerabilities to look for include misconfigured web servers, outdated software versions, open ports that shouldn't be exposed, and weak encryption protocols. For example, CVE-2021-3427 highlighted a critical vulnerability in Apache Log4j, which could be exploited if the version was not updated.

**Q2. How does dynamic application security testing (DAST) differ from static application security testing (SAST)?**

Dynamic Application Security Testing (DAST) involves testing the application while it is running, simulating attacks to identify vulnerabilities such as SQL injection, cross-site scripting (XSS), and buffer overflows. SAST, on the other hand, analyzes the source code without executing it, aiming to find coding errors and security flaws before the application is deployed. DAST tools like OWASP ZAP or Burp Suite can help in identifying runtime issues, whereas SAST tools like SonarQube focus on code quality and security during the development phase.

**Q3. Explain how automating infrastructure security testing can benefit a DevSecOps pipeline.**

Automating infrastructure security testing in a DevSecOps pipeline ensures that security checks are consistently applied across the entire infrastructure, reducing the risk of human error. It enables continuous monitoring and immediate feedback on security issues, allowing teams to address vulnerabilities quickly. Automation also supports scalability, making it easier to manage security in complex environments. For instance, tools like Ansible or Terraform can be used to automate the deployment and configuration of secure infrastructure settings.

**Q4. What are some common misconfigurations found in web servers that can be identified through infrastructure scanning?**

Common web server misconfigurations include improper file permissions, unnecessary services enabled, default credentials left unchanged, and lack of SSL/TLS encryption. These issues can be detected by scanning tools like Nikto or OpenVAS. For example, a recent breach involved an improperly configured web server that allowed unauthorized access due to default credentials being used, highlighting the importance of regular scanning and configuration reviews.

**Q5. How can you integrate automated security tests into your CI/CD pipeline to ensure ongoing security?**

To integrate automated security tests into a CI/CD pipeline, you can use tools like Jenkins, GitLab CI, or CircleCI to automatically run security scans whenever changes are pushed to the repository. This includes running SAST tools to analyze code, DAST tools to test applications in a live environment, and infrastructure scanning tools to check for configuration issues. By setting up these scans as part of the build process, you ensure that security is checked continuously, and any issues are flagged early. For example, integrating a tool like Trivy for container image scanning can help catch vulnerabilities in Docker images before they are deployed.

**Q6. Why is it important to implement all automated security tests seen in previous modules together in a comprehensive manner?**

Implementing all automated security tests comprehensively ensures a holistic approach to security, covering different aspects of the application lifecycle. This includes code analysis, third-party library checks, container security, and infrastructure scanning. By combining these tests, you create multiple layers of defense, reducing the likelihood of vulnerabilities slipping through. Comprehensive testing also helps in maintaining compliance with security standards and regulations, providing a more robust security posture overall.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/Introduction/06-Module and Course Summary|Module and Course Summary]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/Introduction/00-Overview|Overview]]
