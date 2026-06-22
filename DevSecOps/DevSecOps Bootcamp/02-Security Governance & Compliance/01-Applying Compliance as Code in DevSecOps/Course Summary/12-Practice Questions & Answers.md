---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the difference between security governance and compliance.**

Security governance refers to the overall management approach through which senior executives direct and control the entire organization in terms of security. It involves setting the strategic direction, establishing policies, and ensuring that the right processes and controls are in place to manage security risks effectively. Compliance, on the other hand, means conforming to stated requirements such as laws, regulations, contracts, and policies. While governance provides the framework and oversight, compliance ensures adherence to specific rules and standards. For instance, a company can be fully compliant with GDPR regulations but still lack effective governance if the underlying processes and controls are weak.

**Q2. How can automation improve compliance in a DevSecOps environment?**

Automation in a DevSecOps environment can significantly enhance compliance by providing scalability, consistency, and ensuring legal obligations are met. By integrating automated tools into the CI/CD pipeline, organizations can perform tasks such as static application security testing (SAST), software composition analysis (SCA), and vulnerability scanning consistently across all projects. This reduces the risk of human error and ensures that security checks are performed uniformly. Additionally, automated compliance checks can be configured to flag any deviations from established policies, helping to maintain regulatory compliance throughout the development lifecycle.

**Q3. Describe how static application security testing (SAST) can be integrated into the code building and testing stages of a DevSecOps pipeline.**

Static Application Security Testing (SAST) can be integrated into the code building and testing stages of a DevSecOps pipeline by using tools that analyze source code without executing it. During the code building stage, SAST tools can scan the codebase for potential security vulnerabilities such as SQL injection, cross-site scripting (XSS), and buffer overflows. These tools can be configured to run automatically as part of the build process, ensuring that any issues are identified early. In the testing phase, SAST results can be reviewed alongside other testing outcomes to ensure comprehensive security coverage. Tools like SonarQube, Fortify, and Veracode are commonly used for SAST integration.

**Q4. What are some recent real-world examples of breaches that highlight the importance of integrating security governance and compliance into DevSecOps?**

One notable example is the Capital One data breach in 2019 (CVE-2019-11600). A hacker exploited a misconfigured web application firewall to access sensitive customer data. This breach highlighted the importance of integrating security governance and compliance into the DevSecOps pipeline. Proper governance would have ensured that security policies were strictly followed, and compliance checks would have identified the misconfiguration before it became a critical issue. Another example is the Equifax breach in 2017, which exposed personal information of millions of customers due to unpatched vulnerabilities. Both cases underscore the necessity of robust security governance and compliance practices in modern software development.

**Q5. Explain how security controls can be mapped from a specification into code in a DevSecOps context.**

In a DevSecOps context, security controls can be mapped from a specification into code by defining clear security requirements and integrating them into the development process. This typically involves creating a set of security policies and controls that align with organizational goals and regulatory requirements. These controls can then be translated into code using tools and frameworks that support policy enforcement. For example, Azure Policy Definitions allow administrators to create custom policies that enforce security best practices across resources. Similarly, AWS Config can be used to assess resource configurations against defined rules, ensuring compliance with security policies. By embedding these controls directly into the code, organizations can ensure that security is built into the system from the ground up.

**Q6. How can tools like AWS Config and Cloud Custodian help with enabling good security governance and compliance in a cloud environment?**

Tools like AWS Config and Cloud Custodian play a crucial role in enabling good security governance and compliance in a cloud environment by automating the monitoring and enforcement of security policies. AWS Config continuously monitors and records the configuration state of AWS resources, allowing organizations to track changes and ensure compliance with predefined rules. Cloud Custodian, on the other hand, is an open-source tool that enables organizations to define and enforce policies across multiple cloud providers. It supports actions such as tagging resources, enforcing security group rules, and identifying unused resources. By leveraging these tools, organizations can automate the enforcement of security policies, detect non-compliance issues, and take corrective actions promptly, thereby enhancing overall security governance and compliance.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/11-Using Compliance Code Examples from Microsoft Azure|Using Compliance Code Examples from Microsoft Azure]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]]
