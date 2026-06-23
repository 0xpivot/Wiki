---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of static code analysis in a DevSecOps pipeline.**

Static code analysis is a crucial step in a DevSecOps pipeline as it helps identify potential security vulnerabilities and coding errors before the code is compiled or executed. This type of analysis is performed on the source code without actually running it, allowing developers to catch issues early in the development process. By integrating static code analysis into the pipeline, teams can ensure that their code adheres to security standards and best practices, reducing the risk of security breaches and improving overall software quality.

**Q2. How does dynamic application testing (ZAP) complement static code analysis in a DevSecOps pipeline?**

Dynamic Application Testing (ZAP) complements static code analysis by providing runtime security assessments. While static code analysis examines the code for potential vulnerabilities, ZAP performs tests on the running application to detect security flaws that might not be evident from the source code alone. ZAP can identify issues such as SQL injection, cross-site scripting (XSS), and other runtime vulnerabilities. By combining both static and dynamic testing, a more comprehensive security assessment is achieved, ensuring that the application is secure both in design and in execution.

**Q3. Describe the role of manual testing in the context of a DevSecOps pipeline.**

Manual testing plays a critical role in the DevSecOps pipeline by providing human oversight and judgment that automated tests may miss. Manual testing allows testers to explore the application in ways that automated scripts cannot, uncovering usability issues, unexpected behavior, and security vulnerabilities that automated tools might overlook. It is particularly important for complex systems where certain aspects of functionality or security cannot be fully tested using automated methods. Additionally, manual testing can help validate the results of automated tests and ensure that the application meets the desired quality and security standards before deployment.

**Q4. What are the implications of having only warnings left after all the scans in a DevSecOps pipeline?**

If only warnings remain after all the scans in a DevSecOps pipeline, it implies that there are no critical or blocking issues identified by the static and dynamic security scans. Warnings typically indicate potential issues that are less severe than errors but still require attention. The presence of only warnings suggests that the codebase and application are relatively clean from major security vulnerabilities. However, it is still important to review and address these warnings to ensure that the application remains secure and robust. Ignoring warnings could lead to minor security issues that might escalate over time.

**Q5. How would you configure a manual approval step before deploying to production in a CI/CD pipeline?**

To configure a manual approval step before deploying to production in a CI/CD pipeline, you can use a tool like Jenkins, GitLab CI, or CircleCI. Here’s a basic example using Jenkins:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Build steps
            }
        }
        stage('Test') {
            steps {
                // Test steps
            }
        }
        stage('Scan') {
            steps {
                // Static and dynamic scan steps
            }
        }
        stage('Manual Approval') {
            steps {
                input message: 'Approve deployment to production?', ok: 'Deploy'
            }
        }
        stage('Deploy to Production') {
            steps {
                // Deployment steps
            }
        }
    }
}
```

In this example, the `input` step pauses the pipeline and waits for a user to approve the deployment to production. Once approved, the pipeline continues to the deployment stage. This ensures that a human checks the status of the build and tests before proceeding with the production deployment, adding an extra layer of safety and control.

**Q6. Discuss recent real-world examples where the lack of proper security scanning led to significant breaches.**

One notable example is the Capital One data breach in 2019, where a misconfigured web application firewall allowed unauthorized access to sensitive customer data. The breach affected over 100 million customers and resulted in significant financial and reputational damage. If Capital One had implemented a robust DevSecOps pipeline with regular static and dynamic security scans, the misconfiguration might have been detected earlier, potentially preventing the breach.

Another example is the Equifax data breach in 2017, which exposed personal information of approximately 147 million consumers. The breach was caused by a vulnerability in the Apache Struts framework that was not properly patched. A comprehensive DevSecOps pipeline with regular security scans and timely patch management could have helped mitigate this risk.

These examples highlight the importance of integrating security scans into the DevSecOps pipeline to proactively identify and address vulnerabilities before they can be exploited.

---
<!-- nav -->
[[01-Introduction to DevSecOps Pipeline with Static and Dynamic Security Scans|Introduction to DevSecOps Pipeline with Static and Dynamic Security Scans]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/02-Overview of Complete DevSecOps Pipeline with Static and Dynamic Security Scans/00-Overview|Overview]]
