---
course: DevSecOps
topic: Understanding Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the main differences between manual and automated security testing.**

Automated security testing involves the use of software tools to perform security checks without human intervention, whereas manual security testing requires human expertise to review and test systems. Automated testing is typically faster and more consistent, but it may miss nuances that a human tester could identify. Manual testing allows for a deeper understanding of the system under test and can adapt to complex situations, but it is time-consuming and prone to human error. Automated testing is often integrated into continuous integration/continuous deployment (CI/CD) pipelines, while manual testing might involve activities like code reviews or penetration testing.

**Q2. How would you integrate automated security testing into a build pipeline?**

To integrate automated security testing into a build pipeline, you would first choose appropriate tools such as static application security testing (SAST), dynamic application security testing (DAST), or dependency checking tools. These tools should be configured to run automatically as part of the build process. For example, you can use a CI/CD tool like Jenkins or GitLab CI to trigger these security tests whenever changes are pushed to the repository. The configuration might include setting up scripts or jobs that execute the security tests and fail the build if vulnerabilities are found. This ensures that security issues are caught early in the development cycle.

**Q3. Why is automated security testing mainly focused on negative testing?**

Automated security testing is primarily focused on negative testing because it aims to identify potential vulnerabilities and weaknesses in the system. Negative testing involves looking for unexpected behaviors, abuse cases, and errors rather than confirming expected outcomes. This approach helps uncover issues that might not be apparent through positive testing alone. Automated tools are well-suited for this type of testing because they can quickly scan large amounts of code or interact with applications in ways that might be difficult or time-consuming for humans to replicate.

**Q4. Provide an example of how manual and automated security testing can complement each other.**

Manual and automated security testing can complement each other effectively. For example, consider a scenario where a new web application is being developed. Automated SAST tools can be used to scan the codebase for common vulnerabilities like SQL injection or cross-site scripting (XSS). These tools can flag potential issues that developers can then investigate further. However, automated tools might miss certain nuances or context-specific issues. A manual code review by a skilled developer can catch these subtleties and provide a more comprehensive assessment. Additionally, automated DAST tools can simulate attacks against the live application, but a manual penetration test can explore the system in a more creative and adaptive manner, potentially uncovering more sophisticated attack vectors.

**Q5. Discuss the concept of third-party trust verification in automated security testing.**

Third-party trust verification in automated security testing involves ensuring the integrity and authenticity of third-party components or modules used in an application. This is particularly important given the prevalence of open-source libraries and dependencies. Automated tools can verify digital signatures associated with these components to ensure they come from trusted sources and have not been tampered with. For example, tools like Snyk or OWASP Dependency-Check can scan project dependencies and report on known vulnerabilities or untrusted sources. This automated verification complements manual efforts to research and vet third-party providers, providing a more robust security posture.

**Q6. Why is it important to budget time for configuring automated security testing tools?**

It is crucial to budget time for configuring automated security testing tools because the setup and configuration process can be time-consuming and complex. While automated tools can significantly speed up the testing process once they are properly configured, they require careful setup to ensure they are effective and efficient. This includes selecting the right tools, configuring them to fit the specific needs of the project, and integrating them into the existing development workflow. Without proper configuration, automated tools may produce false positives or negatives, leading to wasted time and potential security gaps. Therefore, allocating sufficient time for configuration is essential to maximize the benefits of automated security testing.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/02-Manual vs Automated Testing/01-Understanding Automated Security Testing|Understanding Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/11-Understanding Automated Security Testing/02-Manual vs Automated Testing/00-Overview|Overview]]
