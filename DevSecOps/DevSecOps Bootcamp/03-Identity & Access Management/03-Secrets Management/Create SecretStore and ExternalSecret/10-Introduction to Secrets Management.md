---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management

### What is Secrets Management?

Secrets management is the process of securely storing, distributing, and managing sensitive information such as passwords, API keys, and cryptographic keys. In modern software development, especially in cloud-native environments, secrets management is crucial for maintaining the security and integrity of applications and services.

### Why is Secrets Management Important?

In today’s interconnected world, applications often require access to various external services and resources. These interactions typically involve the use of sensitive credentials. Without proper secrets management, these credentials can be exposed, leading to unauthorized access and potential breaches. Recent high-profile breaches, such as the Capital One data breach in 2019 (CVE-2019-11510), highlight the importance of robust secrets management practices.

### How Does Secrets Management Work?

Secrets management involves several key components:

1. **Storage**: Securely storing secrets in a way that prevents unauthorized access.
2. **Distribution**: Safely distributing secrets to applications and services that need them.
3. **Rotation**: Periodically changing secrets to minimize the window of opportunity for an attacker.
4. **Audit**: Tracking and logging access to secrets to detect and respond to suspicious activity.

### Key Concepts in Secrets Management

#### Secret Store

A secret store is a centralized repository where secrets are stored securely. Examples of secret stores include HashiCorp Vault, AWS Secrets Manager, and Azure Key Vault. These stores provide mechanisms for encrypting and decrypting secrets, as well as controlling access through policies and permissions.

#### Secret Store Provider

A secret store provider is a specific implementation of a secret store that integrates with a particular cloud service or technology. For example, AWS Secrets Manager is a secret store provider for AWS, while Azure Key Vault is a provider for Azure.

#### External Secrets Operator

An external secrets operator is a tool that facilitates the integration between a secret store and applications running in a Kubernetes cluster. It allows applications to fetch secrets from the secret store and inject them into the environment.

---
<!-- nav -->
[[09-Introduction to Secrets Management Part 3|Introduction to Secrets Management Part 3]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[11-Creating a Secret Store and External Secret|Creating a Secret Store and External Secret]]
