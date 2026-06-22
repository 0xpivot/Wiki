---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Hardening Steps

### What Are They?

Hardening steps involve securing the different components of the CI/CD pipeline to prevent unauthorized access and ensure the integrity of the code and artifacts.

### Why Are They Important?

Hardening steps are crucial for preventing security vulnerabilities and ensuring that the pipeline operates securely. This includes securing build servers, test environments, repositories, and network communication.

### How Do They Work?

#### Securing Build Servers

- **Limit access**: Restrict access to build servers to trusted personnel.
- **Regular updates**: Keep build servers up to date with the latest security patches.
- **Monitoring**: Implement monitoring to detect and alert on suspicious activity.

#### Securing Test Environments

- **Isolate environments**: Use ephemeral environments to isolate tests and prevent interference.
- **Regular updates**: Keep test environments up to date with the latest security patches.
- **Monitoring**: Implement monitoring to detect and alert on unusual activity.

#### Securing Repositories

- **Use HTTPS**: Ensure that all communication with repositories is encrypted.
- **Two-factor authentication**: Enable two-factor authentication for repository access.
- **Regular audits**: Perform regular audits of repository permissions and access logs.

#### Securing Network Communication

- **Use HTTPS**: Ensure that all communication with repositories and services is encrypted.
- **SSH keys**: Use SSH keys for secure access to servers and repositories.
- **Firewall rules**: Implement strict firewall rules to limit access to necessary services.

### Real-World Example: Recent Breach

In the Equifax data breach (CVE-2017-5638), attackers exploited a vulnerability in Apache Struts, which was due to outdated and unpatched versions of the software. This highlights the importance of hardening steps to prevent such vulnerabilities.

### How to Prevent / Defend

#### Secure Build Servers

- **Limit access**: Restrict access to build servers to trusted personnel.
- **Regular updates**: Keep build servers up to date with the latest security patches.
- **Monitoring**: Implement monitoring to detect and alert on suspicious activity.

#### Secure Test Environments

- **Isolate environments**: Use ephemeral environments to isolate tests and prevent interference.
- **Regular updates**: Keep test environments up to date with the latest security patches.
- **Monitoring**: Implement monitoring to detect and alert on unusual activity.

#### Secure Repositories

- **Use HTTPS**: Ensure that all communication with repositories is encrypted.
- **Two-factor authentication**: Enable two-factor authentication for repository access.
- **Regular audits**: Perform regular audits of repository permissions and access logs.

#### Secure Network Communication

- **Use HTTPS**: Ensure that all communication with repositories and services is encrypted.
- **SSH keys**: Use SSH keys for secure access to servers and repositories.
- **Firewall rules**: Implement strict firewall rules to limit access to necessary services.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/04-Hands-On Labs|Hands-On Labs]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/06-Network Communication|Network Communication]]
