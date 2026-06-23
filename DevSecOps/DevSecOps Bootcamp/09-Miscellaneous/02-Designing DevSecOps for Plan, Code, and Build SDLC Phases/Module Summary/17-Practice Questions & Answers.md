---
course: DevSecOps
topic: Designing DevSecOps for Plan, Code, and Build SDLC Phases
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the importance of performing security checks at the design phase before any code is written.**

Performing security checks at the design phase is crucial because it allows teams to identify and mitigate potential security risks early in the development process. By addressing these issues before coding begins, developers can avoid costly rework and ensure that security is integrated into the architecture from the start. This proactive approach helps in building more secure applications by preventing vulnerabilities from being introduced in the first place.

**Q2. How would you implement source code testing effectively in a DevSecOps pipeline?**

To implement source code testing effectively in a DevSecOps pipeline, you should integrate static application security testing (SAST) tools into your continuous integration/continuous deployment (CI/CD) process. This involves setting up automated scans that analyze the source code for security vulnerabilities and coding errors. Tools like SonarQube or Fortify can be configured to run automatically whenever new code is committed. Additionally, ensuring that developers are trained to write secure code and understand the results of these scans can help improve the overall security posture of the project.

**Q3. What types of vulnerability scans should be performed on compiled code, and why?**

On compiled code, dynamic application security testing (DAST) and binary analysis tools should be used. DAST simulates attacks against the running application to find vulnerabilities such as SQL injection, cross-site scripting (XSS), and buffer overflows. Binary analysis tools, like those provided by Checkmarx or Veracode, can inspect the compiled binaries for security flaws that might not be evident in the source code. These scans are essential because they can uncover vulnerabilities that were missed during the earlier stages of development, ensuring that the final product is as secure as possible.

**Q4. Why is it important to continue security testing throughout the entire software development lifecycle (SDLC)?**

Continuing security testing throughout the SDLC is important because it ensures that security is not treated as an afterthought but is integrated into every phase of development. Security threats evolve rapidly, and new vulnerabilities can be introduced at any stage. By maintaining consistent security testing, teams can catch and address issues as they arise, reducing the risk of security breaches. This comprehensive approach also supports compliance requirements and helps build trust with end-users by demonstrating a commitment to security.

**Q5. Provide an example of how recent real-world breaches could have been prevented with better implementation of DevSecOps practices.**

One notable example is the Capital One data breach in 2019, where a misconfigured web application firewall allowed unauthorized access to customer data. This breach could have been mitigated with better DevSecOps practices. Specifically, implementing robust vulnerability scanning and penetration testing in the CI/CD pipeline could have identified the misconfiguration earlier. Additionally, integrating security monitoring and alerting systems could have detected unusual activity and triggered immediate action. By embedding security into every phase of the SDLC, organizations can significantly reduce the likelihood of such breaches occurring.

---
<!-- nav -->
[[16-Vulnerability SQL Injection|Vulnerability SQL Injection]] | [[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/02-Designing DevSecOps for Plan, Code, and Build SDLC Phases/Module Summary/00-Overview|Overview]]
