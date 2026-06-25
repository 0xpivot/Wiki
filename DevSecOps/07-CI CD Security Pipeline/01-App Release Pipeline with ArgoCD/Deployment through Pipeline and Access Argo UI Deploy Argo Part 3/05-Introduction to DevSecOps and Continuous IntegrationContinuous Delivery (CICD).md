---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to DevSecOps and Continuous Integration/Continuous Delivery (CI/CD)

### What is DevSecOps?

DevSecOps is a set of practices that integrates security into the entire DevOps lifecycle. Traditionally, security was often treated as an afterthought, added late in the development process. However, with DevSecOps, security is embedded at every stage, from planning and coding to testing and deployment. This approach ensures that security is not just a responsibility of the security team but is shared across all teams involved in the software development process.

### What is CI/CD?

Continuous Integration/Continuous Delivery (CI/CD) is a set of practices that enables developers to deliver code changes more frequently and reliably. CI involves automatically building and testing code changes as they are committed to a version control system. CD extends this by automating the deployment of those changes to production environments.

### Why is CI/CD Important?

CI/CD helps organizations to:

- **Reduce time to market:** By automating the build, test, and deployment processes, teams can release new features and bug fixes much faster.
- **Improve quality:** Automated testing ensures that code changes are thoroughly tested before being deployed, reducing the likelihood of bugs making it to production.
- **Increase collaboration:** CI/CD encourages collaboration between development, operations, and security teams, ensuring that everyone is aligned and working towards the same goals.

### Real-World Example: Equifax Breach (CVE-2017-5638)

The Equifax breach in 2017, which exposed sensitive data of over 143 million people, could have been mitigated with better CI/CD practices. The breach was caused by a vulnerability in Apache Struts, which was not patched in a timely manner. A robust CI/CD pipeline with automated security scans and regular updates would have helped identify and mitigate such vulnerabilities earlier.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/04-Introduction to ArgoCD and Its Role in DevSecOps|Introduction to ArgoCD and Its Role in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Deployment through Pipeline and Access Argo UI Deploy Argo Part 3/06-Setting Up a CICD Pipeline with ArgoCD|Setting Up a CICD Pipeline with ArgoCD]]
