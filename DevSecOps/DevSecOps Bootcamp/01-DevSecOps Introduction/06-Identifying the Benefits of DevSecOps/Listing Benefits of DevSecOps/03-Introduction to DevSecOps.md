---
course: DevSecOps
topic: Identifying the Benefits of DevSecOps
tags: [devsecops]
---

## Introduction to DevSecOps

### What is DevSecOps?

DevSecOps is a methodology that integrates security practices into the DevOps pipeline. Traditionally, security was often treated as a separate phase, typically occurring late in the development cycle. This approach often led to significant delays and increased costs due to the need for extensive rework. DevSecOps aims to embed security throughout the entire software development lifecycle (SDLC), ensuring that security is a shared responsibility among all team members, including developers, operations staff, and security professionals.

### Why is DevSecOps Important?

The importance of DevSecOps lies in its ability to address security concerns early in the development process, thereby reducing the overall cost and time required to fix security vulnerabilities. By integrating security into the continuous integration and continuous deployment (CI/CD) pipeline, organizations can achieve faster release cycles while maintaining a high level of security.

### How Does DevSecOps Work?

DevSecOps operates on the principle of shifting left, which means moving security activities earlier in the development process. This includes:

- **Static Application Security Testing (SAST)**: Analyzing source code for potential security vulnerabilities.
- **Dynamic Application Security Testing (DAST)**: Testing applications in a runtime environment.
- **Interactive Application Security Testing (IAST)**: Combining SAST and DAST techniques to provide more accurate results.
- **Dependency Scanning**: Checking for known vulnerabilities in third-party libraries and dependencies.
- **Security Code Reviews**: Manual reviews of code by security experts.
- **Automated Security Testing**: Integrating security testing tools into the CI/CD pipeline.

### Real-World Example: Equifax Breach (CVE-2017-5638)

In 2017, Equifax suffered a massive data breach that exposed sensitive information of approximately 143 million individuals. The breach was caused by a vulnerability in the Apache Struts framework, which was not patched in a timely manner. This incident highlights the importance of integrating security into the development process to ensure that vulnerabilities are identified and addressed early.

```mermaid
graph LR
    A[Development] --> B[Code Commit]
    B --> C[Static Analysis]
    C --> D[Dynamic Analysis]
    D --> E[Dependency Scanning]
    E --> F[Security Code Review]
    F --> G[Deployment]
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/06-Identifying the Benefits of DevSecOps/Listing Benefits of DevSecOps/02-Introduction to DevSecOps Part 2|Introduction to DevSecOps Part 2]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/06-Identifying the Benefits of DevSecOps/Listing Benefits of DevSecOps/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/06-Identifying the Benefits of DevSecOps/Listing Benefits of DevSecOps/04-Benefits of DevSecOps|Benefits of DevSecOps]]
