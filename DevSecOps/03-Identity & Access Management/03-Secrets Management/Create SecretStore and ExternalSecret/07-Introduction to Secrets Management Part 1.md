---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management

### What is Secrets Management?

Secrets management is the practice of securely handling sensitive information such as passwords, API keys, and other credentials. In modern software development, especially in cloud-native environments, managing these secrets securely is crucial to maintaining the integrity and confidentiality of applications and data.

### Why is Secrets Management Important?

In today’s interconnected world, applications often rely on third-party services, databases, and APIs. Each of these dependencies requires authentication, typically through secrets. If these secrets are not managed properly, they can be exposed, leading to unauthorized access and potential breaches. Recent high-profile breaches, such as the Capital One breach in 2019 (CVE-2019-11510), highlight the importance of robust secrets management practices.

### How Does Secrets Management Work?

Secrets management involves several key steps:

1. **Storing Secrets Securely**: Secrets should be stored in a secure vault or store that is designed to protect them from unauthorized access.
2. **Access Control**: Access to secrets should be tightly controlled using role-based access control (RBAC) and least privilege principles.
3. **Rotation and Expiration**: Secrets should be rotated regularly to minimize the window of exposure if they are compromised.
4. **Monitoring and Auditing**: Access to secrets should be monitored and audited to detect and respond to suspicious activity.

### Tools and Technologies

Several tools and technologies are available for secrets management, including:

- **HashiCorp Vault**
- **AWS Secrets Manager**
- **Azure Key Vault**
- **Kubernetes Secrets**

In this chapter, we will focus on using AWS Secrets Manager and Kubernetes for secrets management.

---
<!-- nav -->
[[06-Introduction to Secrets Management in Kubernetes|Introduction to Secrets Management in Kubernetes]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[08-Introduction to Secrets Management Part 2|Introduction to Secrets Management Part 2]]
