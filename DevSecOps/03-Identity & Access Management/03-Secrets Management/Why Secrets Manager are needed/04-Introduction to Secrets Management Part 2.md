---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management

In the realm of DevSecOps, managing secrets is a critical aspect of ensuring the security and integrity of applications and systems. Secrets, such as database passwords, API keys, and encryption keys, are sensitive pieces of information that must be protected from unauthorized access. This chapter delves into the importance of secrets management, particularly within the context of Kubernetes, and explores various tools and techniques to securely manage these secrets.

### What Are Secrets?

Secrets are sensitive data that should be kept confidential. They include:

- **Database Credentials**: Usernames and passwords used to access databases.
- **API Keys**: Tokens used to authenticate API requests.
- **Encryption Keys**: Used to encrypt and decrypt data.
- **SSH Keys**: Used for secure remote access to servers.

These secrets are essential for the operation of many applications but pose significant security risks if mishandled.

### Why Secrets Management Is Needed

#### Local Storage Risks

One of the primary reasons secrets management is necessary is the inherent risks associated with storing secrets locally on individual engineers' laptops. Consider the following scenarios:

- **Laptop Theft or Loss**: If an engineer's laptop is stolen or lost, the secrets stored on it become exposed.
- **Improper Handling**: Engineers might not follow proper security practices, leading to accidental exposure of secrets.
- **Insufficient Protection**: Local storage often lacks robust security measures, making it easier for attackers to gain access.

#### Example: Recent Breaches

Recent breaches highlight the dangers of poor secrets management:

- **CVE-2021-44228 (Log4Shell)**: This vulnerability allowed attackers to execute arbitrary code on affected systems. In many cases, the attackers used compromised secrets to gain deeper access.
- **SolarWinds Supply Chain Attack**: This attack involved the compromise of build systems, leading to the distribution of malicious software. Poor secrets management could have exacerbated the situation by allowing attackers to gain access to more systems.

### Kubernetes and Secrets Management

Kubernetes provides built-in mechanisms to manage secrets, but these mechanisms have limitations. For instance, creating secrets directly in the cluster using `kubectl create secret` poses several challenges:

- **Human Access Control**: In environments where no human user should be able to create anything in the cluster, direct creation of secrets is not feasible.
- **Local Storage Issues**: Storing secrets locally on engineers' laptops is insecure and unreliable.

### External Secrets Management Tools

To address these challenges, external secrets management tools are often employed. These tools provide a centralized and secure way to manage secrets across different environments and applications. Some popular tools include:

- **AWS Secrets Manager**
- **Azure Key Vault**
- **Google Cloud Secret Manager**
- **HashiCorp Vault**

### AWS Secrets Manager

AWS Secrets Manager is a service that helps you protect access to your applications, services, and IT resources without requiring you to implement complex key management infrastructure. Here’s how it works:

#### Creating a Secret

To create a secret in AWS Secrets Manager, you can use the AWS Management Console, AWS CLI, or AWS SDKs. Below is an example using the AWS CLI:

```bash
aws secretsmanager create-secret \
    --name MySecret \
    --secret-string '{"username":"myuser","password":"mypassword"}'
```

#### Retrieving a Secret

To retrieve a secret, you can use the following command:

```bash
aws secretsmanager get-secret-value \
    --secret-id MySecret
```

The response will include the secret value:

```json
{
    "ARN": "arn:aws:secretsmanager:us-west-2:123456789012:secret:MySecret-abc123",
    "Name": "MySecret",
    "VersionId": "EXAMPLE1-90ab-cdef-fedc-ba987EXAMPLE",
    "SecretString": "{\"username\":\"myuser\",\"password\":\"mypassword\"}",
    "VersionStages": [
        "AWSCURRENT"
    ],
    "CreatedDate": 1523762400.052,
    "LastChangedDate": 1523762400.052,
    "LastAccessedDate": 1523762400.052,
    "DeletedDate": 1523762400.052
}
```

### Azure Key Vault

Azure Key Vault is a cloud-based service that enables you to store and manage cryptographic keys and secrets used to access your applications and services. Here’s how to create and retrieve a secret using Azure CLI:

#### Creating a Secret

```bash
az keyvault secret set --name MySecret --value "mysecretvalue" --vault-name MyKeyVault
```

#### Retrieving a Secret

```bash
az keyvault secret show --name MySecret --vault-name MyKeyVault
```

The response will include the secret value:

```json
{
    "attributes": {
        "created": 1523762400,
        "enabled": true,
        "expires": null,
        "notBefore": null,
        "recoveryLevel": "Recoverable+Purgeable",
        "updated": 1523762400
    },
    "contentType": null,
    "id": "https://MyKeyVault.vault.azure.net/secrets/MySecret/1234567890",
    "managed": false,
    "name": "MySecret",
    "tags": {},
    "value": "mysecretvalue"
}
```

### Google Cloud Secret Manager

Google Cloud Secret Manager is a service that allows you to store, manage, and access secrets throughout their lifecycle. Here’s how to create and retrieve a secret using gcloud CLI:

#### Creating a Secret

```bash
gcloud secrets create MySecret --replication-policy="automatic"
```

#### Adding a Secret Version

```bash
gcloud secrets versions add MySecret --payload-file=secret.txt
```

#### Retrieving a Secret

```bash
gcloud secrets versions access latest --secret=MySecret
```

The response will include the secret value:

```plaintext
mysecretvalue
```

### HashiCorp Vault

HashiCorp Vault is a tool for securely accessing secrets. It is a unified solution to centralize secrets management, providing robust security features. Here’s how to create and retrieve a secret using Vault CLI:

#### Initializing Vault

First, initialize Vault:

```bash
vault init -key-shares=1 -key-threshold=1 -format=json > vault-keys.json
```

#### Unsealing Vault

Unseal Vault using the generated key:

```bash
vault unseal $(cat vault-keys.json | jq -r '.unseal_keys_b64[]')
```

#### Enabling a Secret Engine

Enable a secret engine, such as the generic secret backend:

```bash
vault secrets enable -path=secret generic
```

#### Writing a Secret

Write a secret to the secret backend:

```bash
vault kv put secret/mysecret username=myuser password=mypassword
```

#### Reading a Secret

Read the secret from the secret backend:

```bash
vault kv get secret/mysecret
```

The response will include the secret value:

```plaintext
Key              Value
----             -----
password         mypassword
username         myuser
```

### Integrating External Secrets with Kubernetes

External secrets management tools can be integrated with Kubernetes to securely manage secrets. Here’s an example using HashiCorp Vault and the `external-secrets` operator:

#### Installing the `external-secrets` Operator

Install the `external-secrets` operator using Helm:

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets
```

#### Configuring the `external-secrets` Operator

Configure the `external-secrets` operator to fetch secrets from HashiCorp Vault:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mysecret
spec:
  backend:
    vault:
      path: secret/mysecret
  dataFrom:
    - key: username
      name: username
    - key: password
      name: password
  secretTemplate:
    metadata:
      name: mysecret
    type: Opaque
```

This configuration will create a Kubernetes secret named `mysecret` with the values fetched from HashiCorp Vault.

### How to Prevent / Defend

#### Detection

To detect unauthorized access to secrets, implement monitoring and logging:

- **Audit Logs**: Enable audit logs in your secrets management tools to track access and modifications.
- **Monitoring**: Set up alerts for unusual access patterns or changes to secrets.

#### Prevention

To prevent unauthorized access to secrets, implement the following best practices:

- **Least Privilege**: Ensure users and services have the minimum permissions required to perform their tasks.
- **Rotation**: Regularly rotate secrets to minimize the window of opportunity for attackers.
- **Encryption**: Encrypt secrets both at rest and in transit.

#### Secure Coding Fixes

Here’s an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**

```python
import os

# Hardcoded secret
db_password = "mypassword"

# Connect to database
conn = db.connect(host='localhost', user='myuser', password=db_password)
```

**Secure Code**

```python
import os
from external_secrets import get_secret

# Fetch secret from external secrets manager
db_password = get_secret('mysecret', 'password')

# Connect to database
conn = db.connect(host='localhost', user='myuser', password=db_password)
```

### Conclusion

Secrets management is a critical aspect of DevSecOps, especially in Kubernetes environments. By leveraging external secrets management tools like AWS Secrets Manager, Azure Key Vault, Google Cloud Secret Manager, and HashiCorp Vault, you can ensure that secrets are securely managed and accessed. Implementing best practices for detection, prevention, and secure coding will further enhance the security of your applications and systems.

### Practice Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security, including secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

By completing these labs, you can gain practical experience in managing secrets securely in a Kubernetes environment.

---
<!-- nav -->
[[03-Introduction to Secrets Management Part 1|Introduction to Secrets Management Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Why Secrets Manager are needed/00-Overview|Overview]] | [[05-Introduction to Secrets Management Part 3|Introduction to Secrets Management Part 3]]
