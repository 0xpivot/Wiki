---
course: DevSecOps
topic: Integrating Automated Security Testing into Azure Pipelines
tags: [devsecops]
---

## Azure Pipelines Overview

### What is Azure Pipelines?

Azure Pipelines is a cloud-based continuous integration and continuous delivery (CI/CD) service provided by Microsoft. It allows developers to automate the building, testing, and deployment of their applications. Azure Pipelines supports a wide range of languages and platforms, including .NET, Java, Python, Node.js, and more.

### Why Use Azure Pipelines?

Azure Pipelines offers several benefits:

- **Scalability**: It can handle large-scale builds and deployments.
- **Integration**: It integrates seamlessly with other Azure services and third-party tools.
- **Flexibility**: It supports various build and deployment scenarios through YAML files.
- **Security**: It provides built-in security features, such as secret management and secure variable handling.

### How Does Azure Pipelines Work?

Azure Pipelines works by defining a series of tasks in a YAML file. These tasks can include building the code, running tests, deploying the application, and more. The pipeline is triggered by events such as code commits, pull requests, or scheduled times.

### Real-World Example: Recent CVEs

A recent CVE (CVE-2021-34277) involved a vulnerability in the Jenkins CI/CD server, which could allow attackers to execute arbitrary code. This highlights the importance of integrating security into CI/CD pipelines to prevent such vulnerabilities.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Demo Integrating Detection of Secrets in Azure Pipelines/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Demo Integrating Detection of Secrets in Azure Pipelines/02-Introduction to DevSecOps and Azure Pipelines|Introduction to DevSecOps and Azure Pipelines]]
