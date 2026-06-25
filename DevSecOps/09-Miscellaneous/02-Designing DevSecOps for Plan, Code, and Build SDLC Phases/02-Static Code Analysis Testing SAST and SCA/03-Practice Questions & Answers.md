---
course: DevSecOps
topic: Designing DevSecOps for Plan, Code, and Build SDLC Phases
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the difference between SAST and SCA.**

SAST (Static Application Security Testing) focuses on analyzing the source code of an application to identify potential security vulnerabilities within the code itself. It works by examining the actual lines of code written by developers and flagging any patterns or structures that could lead to security issues.

SCA (Software Composition Analysis), on the other hand, is concerned with identifying vulnerabilities in third-party libraries and open-source components used in the software. It checks these components against known vulnerability databases to ensure that the software does not include any compromised or outdated dependencies.

**Q2. How do false positives occur in SAST scans, and how can they be managed?**

False positives in SAST scans occur because the scanners primarily rely on the raw source code without having full contextual understanding of the application's logic and environment. This can lead to situations where legitimate code is flagged as potentially vulnerable due to specific patterns that match known vulnerability signatures.

To manage false positives, developers should:

1. Review the flagged issues carefully to understand the context of the code.
2. Use more sophisticated SAST tools that offer better contextual analysis.
3. Configure the SAST tool to exclude certain types of false positives based on organizational coding practices.
4. Regularly update the SAST tool to incorporate the latest vulnerability definitions and analysis techniques.

**Q3. Why is SCA becoming increasingly important in modern software development?**

SCA is becoming increasingly important because most modern software applications heavily rely on open-source components and third-party libraries. As the number of open-source components increases, so does the risk of integrating vulnerable code into the application. SCA helps identify and mitigate these risks by checking the open-source components against known vulnerabilities. This proactive approach ensures that the software remains secure and reduces the likelihood of security breaches caused by outdated or compromised dependencies.

For example, the Log4j vulnerability (CVE-2021-44228) highlighted the critical nature of SCA. Many organizations were unaware that their software included the vulnerable Log4j library, leading to widespread security issues. SCA tools could have helped identify and address this vulnerability earlier in the development process.

**Q4. What are the benefits of integrating SAST into the build pipeline?**

Integrating SAST into the build pipeline offers several key benefits:

1. **Early Detection**: By running SAST during the build process, security issues can be identified early in the development lifecycle, reducing the cost and effort required to fix them later.
2. **Automation**: SAST can be fully automated, ensuring that every build undergoes security analysis without manual intervention.
3. **Continuous Improvement**: Integrating SAST into the build pipeline supports continuous integration and continuous delivery (CI/CD) practices, enabling teams to maintain high security standards throughout the development process.
4. **Cost Reduction**: Finding and fixing security issues early in the development process is generally less expensive than addressing them after deployment.

**Q5. List some popular SAST tools and describe their main features.**

Some popular SAST tools include:

1. **SonarQube**: SonarQube is an open-source platform that provides code quality and security analysis. It supports multiple programming languages and integrates well with various CI/CD pipelines. SonarQube offers detailed reports and allows developers to track code quality over time.

2. **Fortify Static Code Analyzer**: Fortify is a commercial tool that performs deep static analysis to detect security vulnerabilities. It supports a wide range of programming languages and provides comprehensive reporting and remediation guidance.

3. **Checkmarx**: Checkmarx is another commercial SAST tool that specializes in detecting security vulnerabilities in web applications. It supports multiple languages and frameworks and provides detailed insights into the nature of detected vulnerabilities.

4. **Veracode Static Analysis**: Veracode is a cloud-based SAST solution that integrates seamlessly with various development environments. It supports multiple languages and provides detailed vulnerability reports along with actionable remediation advice.

These tools typically offer features such as language-specific analysis, support for multiple programming languages, integration with CI/CD pipelines, and detailed reporting capabilities.

---
<!-- nav -->
[[02-Introduction to Static Code Analysis Testing (SAST) and Software Composition Analysis (SCA)|Introduction to Static Code Analysis Testing (SAST) and Software Composition Analysis (SCA)]] | [[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/02-Designing DevSecOps for Plan, Code, and Build SDLC Phases/02-Static Code Analysis Testing SAST and SCA/00-Overview|Overview]]
