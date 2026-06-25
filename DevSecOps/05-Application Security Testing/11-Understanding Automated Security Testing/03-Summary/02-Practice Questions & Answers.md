---
course: DevSecOps
topic: Understanding Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the difference between positive and negative testing in the context of security testing.**

Negative testing focuses on verifying that the system behaves correctly when it encounters unexpected or invalid input. This type of testing aims to ensure that the software can handle errors gracefully and securely. Positive testing, on the other hand, checks that the system works correctly under valid conditions and expected inputs. It ensures that the software functions as intended when used as designed.

**Q2. How does Static Application Security Testing (SAST) differ from Dynamic Application Security Testing (DAST)? Provide an example of when each might be used.**

Static Application Security Testing (SAST) analyzes the source code without executing it. SAST tools scan the codebase for potential security vulnerabilities such as SQL injection, cross-site scripting (XSS), and buffer overflows. For example, SAST might be used during the development phase to identify issues before the code is deployed.

Dynamic Application Security Testing (DAST), on the other hand, involves running the application and testing it while it is active. DAST tools simulate attacks on the running application to find vulnerabilities such as authentication flaws, session management issues, and configuration weaknesses. DAST is typically used in a staging environment to test the application’s behavior under real-world attack scenarios.

**Q3. Describe the process of vulnerability scanning and its importance in DevSecOps.**

Vulnerability scanning involves using automated tools to match a list of assets (such as servers, applications, and network devices) against a database of known vulnerabilities. The scanner identifies which assets have known vulnerabilities and reports them. This process is crucial in DevSecOps because it helps organizations proactively identify and mitigate security risks before they can be exploited by attackers. Regular vulnerability scans can help maintain a secure environment and comply with regulatory requirements.

**Q4. Discuss the pros and cons of automated security testing compared to manual security testing.**

Pros of Automated Security Testing:
- Faster and more efficient in identifying common vulnerabilities.
- Can be integrated into the CI/CD pipeline for continuous security checks.
- Reduces human error and bias in testing.
- Allows for consistent and repeatable testing processes.

Cons of Automated Security Testing:
- Limited in detecting complex vulnerabilities that require human intuition.
- May generate false positives and negatives.
- Requires regular updates to keep up with new threats and vulnerabilities.

Pros of Manual Security Testing:
- More effective in finding complex vulnerabilities that require human judgment.
- Can provide deeper insights into the security posture of an application.
- Can adapt to unique environments and custom configurations.

Cons of Manual Security Testing:
- Time-consuming and resource-intensive.
- Subject to human error and bias.
- Not scalable for large and complex systems.

**Q5. How can recent real-world examples, such as CVEs, be used to improve automated security testing?**

Recent real-world examples, such as CVEs (Common Vulnerabilities and Exposures), can be used to enhance automated security testing by incorporating the latest vulnerabilities into the testing process. For instance, if a new CVE is discovered that affects a specific version of a library or framework, automated testing tools can be updated to include checks for this vulnerability. This ensures that the testing is up-to-date and can catch newly identified security issues. Additionally, analyzing the root causes of these vulnerabilities can help refine the testing strategies and improve the overall security posture of the application.

**Q6. Explain how integrating SAST and DAST into the CI/CD pipeline can benefit a DevSecOps team.**

Integrating Static Application Security Testing (SAST) and Dynamic Application Security Testing (DAST) into the CI/CD pipeline can significantly benefit a DevSecOps team by ensuring that security is an integral part of the development lifecycle. By automating these tests, teams can:

- Identify and fix security issues early in the development process, reducing the cost and complexity of fixing issues later.
- Ensure that security checks are performed consistently and automatically with every build and deployment.
- Provide immediate feedback to developers about security vulnerabilities, allowing them to address issues promptly.
- Maintain a high level of security throughout the application’s lifecycle, from development to production.

For example, a DevSecOps team could configure their CI/CD pipeline to run SAST on the codebase after each commit and DAST on the deployed application in a staging environment. This setup ensures that both the code and the running application are continuously checked for security vulnerabilities.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/04-Summary/01-Understanding Automated Security Testing|Understanding Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/04-Summary/00-Overview|Overview]]
