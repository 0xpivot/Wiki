---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management with Vault

Vault is a tool designed to manage secrets securely. Secrets management is crucial in modern DevSecOps environments because it ensures that sensitive information such as API keys, passwords, and certificates are handled in a secure manner. Vault provides a centralized system for storing, managing, and distributing secrets. In this chapter, we will delve deep into how Vault works, including its architecture, secret engines, storage backends, and secure access mechanisms.

### What is Vault?

Vault is an open-source tool developed by HashiCorp. It is designed to securely store and manage secrets such as API keys, passwords, and certificates. Vault provides a centralized system for handling secrets, ensuring that they are encrypted and accessed securely. It also supports dynamic secrets, which are automatically rotated and updated, reducing the risk of exposure.

#### Why Use Vault?

Using Vault offers several benefits:

1. **Centralized Secret Management**: All secrets are stored in one place, making it easier to manage and audit.
2. **Encryption**: Secrets are encrypted both at rest and in transit, providing strong security.
3. **Dynamic Secrets**: Vault can generate and rotate secrets dynamically, reducing the risk of exposure.
4. **Access Control**: Vault provides fine-grained access control, allowing you to specify who can access which secrets.
5. **Audit Logging**: Vault logs all access to secrets, enabling you to track who accessed what and when.

### Vault Architecture

Vault's architecture consists of several key components:

- **Core**: The core of Vault handles authentication, authorization, and secret management.
- **Secret Engines**: These are plugins that handle specific types of secrets, such as database credentials or AWS access keys.
- **Storage Backends**: These are used to store the actual secrets and other metadata.
- **API**: Vault exposes a RESTful API for interacting with the system.

#### Core Components

The core of Vault is responsible for handling authentication, authorization, and secret management. It provides a secure environment for storing and accessing secrets.

#### Secret Engines

Secret engines are plugins that handle specific types of secrets. Each secret engine is designed to work with a particular type of secret, such as database credentials or AWS access keys. This allows Vault to support a wide range of secret types.

#### Storage Backends

Storage backends are used to store the actual secrets and other metadata. Vault supports several types of storage backends, including:

- **Relational Databases**: MySQL, PostgreSQL, etc.
- **HashiCorp Consul**: A distributed key-value store.
- **Cloud Managed Databases**: Services like Amazon RDS, Google Cloud SQL, etc.

### Setting Up Vault

To set up Vault, you first need to install the core of Vault. Once installed, you can enable different secret engines and configure storage backends.

#### Installing Vault

To install Vault, you can download the binary from the HashiCorp website or use package managers like `apt` or `yum`. Here’s an example of installing Vault using `apt`:

```bash
wget https://releases.hashicorp.com/vault/1.10.0/vault_1.10.0_linux_amd64.zip
unzip vault_1.10.0_linux_amd64.zip
sudo mv vault /usr/local/bin/
```

#### Initializing Vault

After installation, you need to initialize Vault. This process sets up the initial encryption keys and generates the root token.

```bash
vault init -key-shares=1 -key-threshold=1 -format=json > vault.json
```

This command initializes Vault with a single share and threshold, meaning you only need one key to unseal Vault. The output is saved to `vault.json`.

#### Unsealing Vault

To unseal Vault, you need to provide the unseal key generated during initialization.

```bash
vault operator unseal $(cat vault.json | jq -r '.unseal_keys_b64[0]')
```

This command unseals Vault using the first unseal key from the `vault.json` file.

### Enabling Secret Engines

Once Vault is initialized and unsealed, you can enable different secret engines. Each secret engine is designed to handle a specific type of secret.

#### Example: Enabling the AWS Secret Engine

To enable the AWS secret engine, you can use the following command:

```bash
vault secrets enable aws
```

This command enables the AWS secret engine, allowing you to manage AWS access keys and secrets.

### Configuring Storage Backends

Vault supports several types of storage backends, including relational databases, HashiCorp Consul, and cloud-managed databases. You need to configure the storage backend to store the actual secrets and other metadata.

#### Example: Configuring a Relational Database Backend

To configure a relational database backend, you need to specify the connection details and other parameters.

```bash
vault write sys/storage/mysql \
    plugin_name=mysql-builtin \
    connection_details='{"connection_url":"root:password@tcp(localhost:3306)/vault"}'
```

This command configures Vault to use a MySQL database as the storage backend.

### Secure Access Mechanisms

To ensure that secrets are accessed securely, Vault provides several mechanisms, including authentication, authorization, and secure login mechanisms.

#### Authentication

Vault supports several authentication methods, including:

- **Token-Based Authentication**: Users authenticate using a token.
- **LDAP Authentication**: Users authenticate using LDAP.
- **Kubernetes Authentication**: Users authenticate using Kubernetes service accounts.

#### Authorization

Vault provides fine-grained authorization, allowing you to specify who can access which secrets. This is done using policies, which define the permissions for users and groups.

#### Secure Login Mechanisms

Vault provides secure login mechanisms to ensure that only authorized users can access secrets. This includes:

- **Two-Factor Authentication (2FA)**: Users can enable 2FA for additional security.
- **Multi-Factor Authentication (MFA)**: Users can use multiple factors for authentication.

### Real-World Examples

Vault has been used in several real-world scenarios to manage secrets securely. Here are a few examples:

#### Example: Managing AWS Credentials

In a scenario where you need to manage AWS credentials, you can use the AWS secret engine in Vault. This allows you to generate and rotate AWS access keys and secrets dynamically.

#### Example: Managing Database Credentials

In a scenario where you need to manage database credentials, you can use the database secret engine in Vault. This allows you to generate and rotate database credentials dynamically.

### Recent CVEs and Breaches

Several recent CVEs and breaches have highlighted the importance of secrets management. Here are a few examples:

#### Example: CVE-2021-2109

CVE-2021-2109 was a vulnerability in Vault that allowed unauthorized access to secrets. This highlights the importance of keeping Vault up to date and securing access mechanisms.

#### Example: Capital One Data Breach

The Capital One data breach in 2019 was caused by a misconfigured firewall, which allowed unauthorized access to sensitive data. This highlights the importance of securing access to secrets and monitoring access logs.

### How to Prevent / Defend

To prevent and defend against vulnerabilities in Vault, you need to follow several best practices:

#### Detection

- **Monitoring**: Monitor access logs to detect unauthorized access.
- **Alerting**: Set up alerts for suspicious activity.

#### Prevention

- **Access Control**: Use fine-grained access control to restrict access to secrets.
- **Secure Configuration**: Ensure that Vault is configured securely, including using strong encryption and secure storage backends.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and a secure configuration:

**Vulnerable Configuration**

```json
{
  "backend": "mysql",
  "connection_details": {
    "connection_url": "root:password@tcp(localhost:3306)/vault"
  }
}
```

**Secure Configuration**

```json
{
  "backend": "mysql",
  "connection_details": {
    "connection_url": "vault_user:strong_password@tcp(localhost:3306)/vault"
  },
  "encryption_key": "strong_encryption_key"
}
```

### Conclusion

Vault is a powerful tool for managing secrets securely. By understanding its architecture, secret engines, storage backends, and secure access mechanisms, you can effectively use Vault to manage secrets in your DevSecOps environment. Remember to follow best practices for detection, prevention, and secure coding to ensure that your secrets are handled securely.

### Practice Labs

For hands-on practice with Vault, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a lab on using Vault for secrets management.
- **OWASP Juice Shop**: Includes a lab on integrating Vault with a web application.
- **DVWA**: Provides a lab on using Vault for managing database credentials.

These labs will help you gain practical experience with Vault and apply the concepts learned in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/How Vault works Vault Deep Dive Part 2/02-Introduction to Secrets Management and HashiCorp Vault|Introduction to Secrets Management and HashiCorp Vault]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/How Vault works Vault Deep Dive Part 2/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/How Vault works Vault Deep Dive Part 2/04-Introduction to Secrets Management|Introduction to Secrets Management]]
