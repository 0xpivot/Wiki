---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management

### What is Secrets Management?

Secrets management is the practice of securely storing, distributing, and managing sensitive information such as passwords, API keys, and encryption keys. This is crucial in modern software development, especially in environments where applications are deployed across multiple systems and clouds. Proper secrets management ensures that sensitive data remains confidential and is used only by authorized entities.

### Why is Secrets Management Important?

In today’s interconnected world, applications often rely on various third-party services, each requiring unique credentials. Managing these credentials manually can lead to significant security risks, such as unauthorized access and data breaches. By using a secrets management solution, organizations can:

- **Centralize** the storage of sensitive data.
- **Automate** the distribution and rotation of secrets.
- **Audit** access and usage of secrets.
- **Reduce** the risk of human error and insider threats.

### How Does Secrets Management Work?

Secrets management solutions typically involve the following components:

- **Secret Store**: A secure location where secrets are stored.
- **Secret Engine**: Tools and processes for generating, rotating, and revoking secrets.
- **Secret Consumer**: Applications or services that require access to secrets.
- **Access Control**: Mechanisms to ensure only authorized entities can access secrets.

### Recent Real-World Examples

One notable example is the **Capital One Data Breach** (CVE-2019-11510), where an attacker exploited a misconfigured web application firewall to gain unauthorized access to sensitive customer data. This breach highlighted the importance of properly securing and managing secrets, particularly API keys and credentials.

Another example is the **Twitter Breach** (CVE-2020-14720), where attackers gained access to internal Twitter tools by exploiting compromised credentials. This incident underscores the need for robust secrets management practices, including regular rotation and strict access controls.

---
<!-- nav -->
[[08-Introduction to Secrets Management Part 2|Introduction to Secrets Management Part 2]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[10-Introduction to Secrets Management|Introduction to Secrets Management]]
