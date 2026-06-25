---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the role of the Jenkinsfile in a CI/CD pipeline.**

The Jenkinsfile is a script that defines the steps and stages of a Jenkins pipeline. It acts as a blueprint for the entire CI/CD process, specifying actions such as building, testing, and deploying code. By defining these steps in a version-controlled file, teams can ensure consistency and transparency in their development workflow. For example, in the given scenario, the Jenkinsfile specifies stages like linting, code quality control, and running a web vulnerability scan using tools like SonarCube and NICTO.

**Q2. How does GitLab trigger a Jenkins pipeline?**

GitLab triggers a Jenkins pipeline through webhooks. When a developer pushes code to the GitLab repository, GitLab sends a webhook notification to Jenkins. This notification signals Jenkins to start a new pipeline for the updated code. This integration ensures that the pipeline runs automatically whenever changes are made to the repository, facilitating continuous integration and continuous delivery.

**Q3. Describe the purpose and functionality of the SonarCube server in the context of the pipeline.**

SonarCube is a static code analysis tool that helps identify bugs, vulnerabilities, and code smells in the source code. In the context of the pipeline, SonarCube performs static analysis on the code and reports the findings to an external server. These reports help developers understand the quality of the code and address any issues before deployment. For instance, in the given scenario, the pipeline pushes the results of the static analysis to the SonarCube server, allowing developers to review and fix any identified issues.

**Q4. What does it mean when a pipeline stage flags a build as "unstable"? Provide an example from the lecture.**

When a pipeline stage flags a build as "unstable," it means that the build has passed but with some warnings or minor issues that might affect the stability or security of the application. In the given scenario, the NICTO stage flagged the build as unstable because it detected web server scanner issues. This indicates that while the application may still function, there are potential security vulnerabilities that need to be addressed before the application is deployed.

**Q5. How do ephemeral environments contribute to the security and reliability of the pipeline?**

Ephemeral environments, such as Docker containers, are temporary and isolated environments used during the pipeline stages. They ensure that each test or build step is performed in a clean and consistent state, reducing the risk of contamination from previous builds or tests. This isolation enhances security by preventing persistent vulnerabilities or malicious code from affecting subsequent builds. Additionally, tearing down these environments after use helps maintain a secure and reliable pipeline by ensuring that no residual data or configurations remain.

**Q6. Discuss recent real-world examples where vulnerabilities were discovered in CI/CD pipelines.**

One notable example is the 2021 SolarWinds supply chain attack, where attackers compromised the SolarWinds software update mechanism, injecting malicious code into legitimate updates. This demonstrates how vulnerabilities in the CI/CD pipeline can lead to widespread security breaches. Another example is the 2020 GitHub Actions vulnerability (CVE-2020-1752), where attackers exploited a flaw in the GitHub Actions feature to gain unauthorized access to repositories. These incidents highlight the importance of securing CI/CD pipelines to prevent similar attacks.

---
<!-- nav -->
[[02-Integrating Automated Security Testing into a CICD Pipeline|Integrating Automated Security Testing into a CICD Pipeline]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/01-Demo Reviewing a Generic CI CD Pipeline/00-Overview|Overview]]
