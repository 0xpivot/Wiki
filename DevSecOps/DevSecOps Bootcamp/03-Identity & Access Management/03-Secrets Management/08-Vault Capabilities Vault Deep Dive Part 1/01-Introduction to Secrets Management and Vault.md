---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management and Vault

In the realm of DevSecOps, secrets management is a critical aspect that ensures the confidentiality and integrity of sensitive information such as passwords, API keys, and other credentials. One of the most robust tools for managing these secrets is HashiCorp Vault. This chapter delves deep into the capabilities of Vault, focusing on its encryption-as-a-service feature and how it enhances the security of sensitive data.

### Background Theory

Before diving into the specifics of Vault, it's essential to understand the importance of secrets management and the regulatory landscape surrounding it.

#### Importance of Secrets Management

Secrets management is crucial because sensitive data, such as Personal Identifiable Information (PII), must be protected to comply with various regulations and avoid hefty penalties. In many jurisdictions, companies are legally required to safeguard user data. For instance, the General Data Protection Regulation (GDPR) in the European Union imposes severe fines for non-compliance.

#### Government Regulations and Penalties

Regulations like GDPR, HIPAA (Health Insurance Portability and Accountability Act), and CCPA (California Consumer Privacy Act) mandate strict protection of user data. Non-compliance can result in significant financial penalties and reputational damage. Therefore, securing sensitive data is not just a technical requirement but a legal necessity.

### Database Credentials and Layered Security

One of the primary types of sensitive data that needs protection is database credentials. These credentials allow access to databases containing valuable information, including PII. To ensure the security of these credentials, a multi-layered approach is necessary.

#### Multi-Layered Security

The principle of layered security involves implementing multiple security measures to protect sensitive data. This approach ensures that even if one layer is compromised, others remain intact, providing an additional barrier against unauthorized access.

### Vault's Encryption-as-a-Service Feature

Vault provides an encryption-as-a-service feature that simplifies the process of securing sensitive data. This feature handles the entire lifecycle of encryption keys, ensuring that data is encrypted securely.

#### How Encryption-as-a-Service Works

Vault's encryption-as-a-service feature operates by generating and managing encryption keys. When data is stored in a database, Vault encrypts it using these keys. The keys themselves are securely managed by Vault, ensuring that they are not exposed to unauthorized parties.

```mermaid
sequenceDiagram
    participant User
    participant Vault
    participant Database
    User->>Vault: Request to encrypt data
    Vault->>Database: Encrypt data using Vault-managed keys
    Database-->>User: Encrypted data stored
```

### Storing Database Credentials in Vault

Vault can store database credentials securely, either encrypted or issued as dynamic short-lived credentials. This approach adds an extra layer of security, as even if a hacker gains access to the database, they cannot decrypt the data without the encryption keys managed by Vault.

#### Dynamic Short-Lived Credentials

Dynamic short-lived credentials are a powerful feature of Vault. Instead of using static credentials that remain valid indefinitely, Vault can issue temporary credentials that expire after a short period. This reduces the window of opportunity for an attacker to misuse stolen credentials.

```mermaid
sequenceDiagram
    participant User
    participant Vault
    participant Database
    User->>Vault: Request for dynamic credentials
    Vault->>Database: Issue short-lived credentials
    Database-->>User: Access granted with short-lived credentials
```

### Real-World Examples and Breaches

To illustrate the importance of secrets management and the risks associated with poor practices, let's look at some recent real-world examples and breaches.

#### Example: Capital One Data Breach (CVE-2019-11510)

In 2019, Capital One suffered a massive data breach that exposed the personal information of over 100 million customers. The breach occurred due to misconfigured web application firewall rules, allowing an attacker to access sensitive data stored in Amazon Web Services (AWS).

```mermaid
sequenceDiagram
    participant Attacker
    participant WebAppFirewall
    participant AWS
    Attacker->>WebAppFirewall: Exploit misconfigured rules
    WebAppFirewall-->>Attacker: Access to AWS resources
    Attacker->>AWS: Steal sensitive data
```

#### How to Prevent / Defend

To prevent such breaches, it's crucial to implement robust secrets management practices:

1. **Use Vault for Secret Management**: Store and manage secrets using Vault to ensure they are encrypted and securely handled.
2. **Implement Dynamic Short-Lived Credentials**: Use Vault to issue short-lived credentials that expire after a short period, reducing the risk of misuse.
3. **Regular Audits and Monitoring**: Regularly audit and monitor access to sensitive data to detect and respond to suspicious activities promptly.

### Complete Example: Securing Database Credentials with Vault

Let's walk through a complete example of securing database credentials using Vault. We'll cover the setup, configuration, and usage of Vault to manage and encrypt database credentials.

#### Step 1: Install and Configure Vault

First, install and configure Vault. This involves setting up a Vault server and initializing it.

```bash
# Install Vault
wget https://releases.hashicorp.com/vault/1.10.3/vault_1.10.3_linux_amd64.zip
unzip vault_1.10.3_linux_amd64.zip
sudo mv vault /usr/local/bin/

# Initialize Vault
vault init -key-shares=1 -key-threshold=1 -format=json > init.json
```

#### Step 2: Unseal Vault

Unseal Vault using the unseal key obtained during initialization.

```bash
vault operator unseal $(cat init.json | jq -r '.unseal_keys_b64[]')
```

#### Step 3: Enable the Database Secret Engine

Enable the database secret engine in Vault to manage database credentials.

```bash
vault secrets enable database
```

#### Step 4: Configure the Database Connection

Configure the connection details for the database in Vault.

```json
{
  "plugin_name": "postgresql-database-plugin",
  "allowed_roles": "readonly",
  "connection_url": "postgresql://{{username}}:{{password}}@localhost:5432/mydb?sslmode=disable"
}
```

#### Step 5: Create a Role for Database Credentials

Create a role in Vault to define the permissions and behavior of the database credentials.

```json
{
  "db_name": "mydb",
  "creation_statements": [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";"
  ],
  "default_ttl": "1h",
  "max_ttl": "24h"
}
```

#### Step 6: Retrieve and Use Database Credentials

Retrieve database credentials from Vault and use them to access the database.

```bash
vault read database/creds/readonly
```

### Full HTTP Request and Response Example

Here's a complete example of retrieving database credentials from Vault via an HTTP request and response.

#### HTTP Request

```http
POST /v1/database/creds/readonly HTTP/1.1
Host: localhost:8200
X-Vault-Token: s.TOKEN
Content-Type: application/json
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Vault-Wrap-TTL: 0s
X-Vault-Version: 1
X-Vault-Request-ID: 12345678-1234-1234-1234-1234567890ab
X-Vault-Content-Type: json
Date: Mon, 01 Jan 2024 00:00:00 GMT

{
  "request_id": "12345678-1234-1234-1234-1234567890ab",
  "lease_id": "",
  "renewable": false,
  "lease_duration": 0,
  "data": {
    "username": "readonly_user",
    "password": "secure_password"
  },
  "wrap_info": null,
  "warnings": null,
  "auth": null
}
```

### Common Pitfalls and Detection

While using Vault for secrets management offers significant benefits, there are common pitfalls to be aware of:

1. **Misconfiguration**: Incorrect configuration of Vault can lead to vulnerabilities. Ensure that all settings are correctly configured and regularly audited.
2. **Key Exposure**: Exposing encryption keys can compromise the entire system. Use Vault's key management features to keep keys secure.
3. **Insufficient Monitoring**: Lack of monitoring can delay the detection of unauthorized access. Implement robust monitoring and alerting mechanisms.

### How to Prevent / Defend

To defend against potential threats, follow these best practices:

1. **Secure Configuration**: Ensure that Vault is configured securely, following best practices and guidelines.
2. **Regular Audits**: Conduct regular audits of Vault configurations and access logs to detect and respond to suspicious activities.
3. **Monitoring and Alerting**: Implement monitoring and alerting mechanisms to detect unauthorized access attempts and respond promptly.

### Hands-On Practice Labs

For hands-on practice with Vault and secrets management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on web security, including secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another insecure web application for learning security concepts.
- **CloudGoat**: A series of labs for practicing cloud security, including secrets management with Vault.

By following these steps and best practices, you can effectively manage and secure sensitive data using Vault, ensuring compliance with regulatory requirements and protecting your organization from potential breaches.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/08-Vault Capabilities Vault Deep Dive Part 1/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/08-Vault Capabilities Vault Deep Dive Part 1/02-Introduction to Secrets Management|Introduction to Secrets Management]]
