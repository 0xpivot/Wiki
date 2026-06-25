---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Demo Setup

### What Is It?

The demo setup is a practical example of how a CI/CD pipeline looks in practice. This includes setting up build automation, test servers, repositories, and network communication.

### Why Is It Important?

A demo setup provides a concrete example of how the concepts discussed can be implemented in a real-world scenario. This helps solidify understanding and provides a reference for implementing similar setups.

### How Does It Work?

#### Setting Up Build Automation

- **Install Jenkins**: Install Jenkins on a build server.
- **Configure Jenkinsfile**: Define the build steps in a `Jenkinsfile`.
- **Integrate with repository**: Integrate Jenkins with the code repository.

#### Setting Up Test Servers

- **Create ephemeral environments**: Use Docker or Kubernetes to create ephemeral test environments.
- **Run tests**: Run automated tests against the built artifacts.

#### Setting Up Repositories

- **Set up Git repository**: Set up a Git repository for source code.
- **Set up artifact repository**: Set up an artifact repository like Nexus or Artifactory.

#### Setting Up Network Communication

- **Use HTTPS**: Ensure that all communication with repositories and services is encrypted.
- **SSH keys**: Use SSH keys for secure access to servers and repositories.

### Real-World Example: Recent Breach

In the SolarWinds supply chain attack (CVE-2020-1014), attackers compromised the build process, injecting malicious code into the Orion software updates. This highlights the importance of a secure demo setup to prevent such attacks.

### How to Prevent / Defend

#### Secure Demo Setup

- **Use HTTPS**: Ensure that all communication with repositories and services is encrypted.
- **SSH keys**: Use SSH keys for secure access to servers and repositories.
- **Regular updates**: Keep all components up to date with the latest security patches.
- **Monitoring**: Implement monitoring to detect and alert on suspicious activity.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/02-Building Automation and Test Servers|Building Automation and Test Servers]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Examining a CI CD Pipeline/04-Hands-On Labs|Hands-On Labs]]
