---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the Center for Internet Security (CIS) and what do they provide?**

The Center for Internet Security (CIS) is a community-driven nonprofit organization founded in 2000. They provide CIS controls and benchmarks, which are globally recognized best practices for securing IT systems and data. These benchmarks include secure configuration recommendations and detailed processes for auditing and remediating compliance issues across various technologies and platforms.

**Q2. How can CIS benchmarks help organizations ensure their IT systems are secure?**

CIS benchmarks offer a structured approach to securing IT systems by providing clear guidelines and best practices. Organizations can use these benchmarks to evaluate the current state of their systems against established security standards. This helps in identifying gaps and implementing necessary measures to harden and secure their IT infrastructure. For instance, the CIS benchmarks for AWS provide detailed steps to audit and remediate security configurations in AWS accounts.

**Q3. Explain the components of a CIS benchmark and how they assist in compliance.**

A CIS benchmark typically consists of several key components:
- **Security Recommendations**: Detailed best practices for securing specific technologies or platforms.
- **Audit Procedures**: Steps to verify compliance with the recommended security practices.
- **Remediation Guidance**: Instructions on how to address identified non-compliance issues and achieve secure configurations.

These components work together to ensure that organizations can systematically assess their security posture and take corrective actions to meet industry-standard security requirements.

**Q4. How can you apply CIS benchmarks to secure a Kubernetes environment?**

To secure a Kubernetes environment using CIS benchmarks, you would follow these steps:
1. **Download the CIS Benchmark for Kubernetes**: Obtain the specific CIS benchmark document for Kubernetes from the CIS website.
2. **Review the Security Controls**: Understand the security controls and best practices outlined in the document.
3. **Conduct Audits**: Use the audit procedures provided to check if your Kubernetes setup complies with the security controls.
4. **Implement Remediations**: If non-compliance is found, apply the remediation guidance to secure your Kubernetes environment.

For example, the CIS Kubernetes Benchmark includes controls such as ensuring that pod security policies are enabled and that sensitive information is not stored in plain text within pods.

**Q5. What recent real-world examples demonstrate the importance of following CIS benchmarks?**

One notable example is the SolarWinds supply chain attack (CVE-2020-1014), which compromised multiple organizations due to a vulnerability in SolarWinds software. Following CIS benchmarks could have helped mitigate the risk by ensuring that software updates were verified and that network monitoring was in place to detect unusual activity. The CIS benchmarks provide specific controls related to software integrity and network monitoring that could have helped organizations detect and respond to such threats more effectively.

**Q6. How does the CIS benchmark for AWS differ from general security best practices?**

The CIS benchmark for AWS provides specific security recommendations tailored to the AWS cloud environment. Unlike general security best practices, which might be more generic and applicable across various cloud platforms, the AWS CIS benchmark focuses on AWS-specific configurations and services. It includes detailed guidance on securing IAM roles, VPC settings, S3 bucket permissions, and other AWS-specific features. This specificity ensures that organizations can effectively secure their AWS environments according to industry standards.

**Q7. How can organizations ensure continuous compliance with CIS benchmarks?**

Organizations can ensure continuous compliance with CIS benchmarks through the following strategies:
1. **Regular Audits**: Conduct periodic audits using the CIS benchmark audit procedures to identify any deviations from the recommended security practices.
2. **Automated Monitoring**: Implement automated tools and scripts to continuously monitor compliance with CIS benchmarks.
3. **Training and Awareness**: Educate staff on the importance of CIS benchmarks and the steps required to maintain compliance.
4. **Integration with CI/CD**: Integrate CIS benchmark checks into the CI/CD pipeline to ensure that new deployments adhere to security standards.

By adopting these strategies, organizations can maintain a consistent and secure IT environment aligned with industry best practices.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/What are CIS Benchmarks/05-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/What are CIS Benchmarks/00-Overview|Overview]]
