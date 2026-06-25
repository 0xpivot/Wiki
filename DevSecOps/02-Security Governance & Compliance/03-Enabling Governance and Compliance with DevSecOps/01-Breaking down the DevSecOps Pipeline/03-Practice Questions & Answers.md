---
course: DevSecOps
topic: Enabling Governance and Compliance with DevSecOps
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of shifting left in the context of DevSecOps and why it is important.**

Shifting left in DevSecOps refers to the practice of integrating security practices earlier in the software development lifecycle (SDLC). Traditionally, security testing was performed late in the SDLC, often right before deployment. Shifting left means moving security activities to the leftmost part of the SDLC, i.e., the beginning. This includes activities such as static code analysis during the coding phase, software composition analysis during the build phase, and automated security testing during the testing phase.

It is important because it helps to identify and fix security issues earlier in the development process, which is more cost-effective. The cost of fixing a security issue increases significantly as the project progresses. Identifying and addressing security vulnerabilities early reduces the overall cost of software production and ensures that security is not an afterthought but an integral part of the development process.

**Q2. How does static code analysis (SAS) contribute to the DevSecOps pipeline? Provide an example of a tool used for SAS.**

Static code analysis (SAS) is a method of analyzing source code without executing it. It is used to detect potential security vulnerabilities and coding errors by scanning the code against a set of predefined rules and patterns. SAS contributes to the DevSecOps pipeline by enabling developers to identify and fix security issues early in the development process, thus reducing the likelihood of vulnerabilities making it to production.

An example of a tool used for SAS is SonarQube. SonarQube is an open-source platform that provides continuous inspection of code quality to detect bugs, code smells, and security vulnerabilities. It supports multiple programming languages and integrates well with various development environments and CI/CD pipelines.

**Q3. What is Software Composition Analysis (SCA), and why is it critical during the build phase of the DevSecOps pipeline?**

Software Composition Analysis (SCA) is a process used to identify open source and third-party components used in software applications. It involves scanning the codebase to detect any known vulnerabilities associated with these components. SCA is critical during the build phase because it helps ensure that the software being developed does not contain vulnerable components that could be exploited.

For example, if a software application uses an open-source library that has known vulnerabilities (such as a recently disclosed CVE), SCA tools can alert the development team about these risks. This allows the team to take corrective actions, such as updating the library or applying patches, before the software is deployed.

**Q4. How can traditional vulnerability scans complement the security checks in the DevSecOps pipeline?**

Traditional vulnerability scans are automated assessments that check systems for known vulnerabilities, misconfigurations, and other weaknesses. They complement the security checks in the DevSecOps pipeline by providing an additional layer of security validation. While static code analysis and software composition analysis focus on the code and its dependencies, vulnerability scans can detect issues that arise from the environment, configuration, or runtime aspects of the application.

For instance, a traditional vulnerability scan might identify misconfigured network settings or outdated system libraries that were not caught by earlier security checks. This holistic approach ensures that the software is secure from multiple perspectives, reducing the risk of exploitable vulnerabilities.

**Q5. Why is security considered an inhibitor to DevSecOps agility according to the 2017 DevSecOps community survey?**

Security is considered an inhibitor to DevSecOps agility because traditional security practices often involve time-consuming manual processes, extensive documentation, and rigorous compliance checks. These practices can slow down the development process, leading to delays and increased friction between security and development teams. For example, a lengthy approval process for deploying new features or changes can hinder the ability to quickly respond to market demands and customer needs.

To address this, modern DevSecOps practices aim to automate security checks and integrate them seamlessly into the CI/CD pipeline. This allows security to be a continuous and integrated part of the development process without slowing it down.

**Q6. Describe how a penetration test fits into the testing phase of the DevSecOps pipeline.**

A penetration test, or pen test, is a simulated cyber attack on a computer system to evaluate the security of the system. In the context of the DevSecOps pipeline, a penetration test is conducted during the testing phase to assess the security posture of the software application once it has been built.

Penetration tests help identify vulnerabilities that may have been missed by earlier security checks, such as static code analysis and software composition analysis. They simulate real-world attacks to uncover weaknesses that could be exploited by malicious actors. By conducting penetration tests, organizations can ensure that their software is robust and secure before it is deployed to production.

For example, a recent breach involving a popular software company (CVE-2021-XXXX) highlighted the importance of thorough penetration testing. The company had implemented various security measures but failed to catch a critical vulnerability that was exploited by attackers. Conducting regular and comprehensive penetration tests could have helped identify and mitigate such vulnerabilities earlier.

---
<!-- nav -->
[[02-Introduction to DevSecOps Pipeline|Introduction to DevSecOps Pipeline]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/03-Enabling Governance and Compliance with DevSecOps/01-Breaking down the DevSecOps Pipeline/00-Overview|Overview]]
