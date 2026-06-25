---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Secrets Management in DevSecOps

### Introduction to Secrets Management

In the realm of DevSecOps, managing secrets securely is one of the most critical aspects of ensuring the confidentiality and integrity of your applications and infrastructure. Secrets management involves handling sensitive data such as API keys, passwords, encryption keys, and other confidential information. This chapter will delve into the concepts, mechanisms, and best practices for managing secrets effectively, specifically focusing on creating a `SecretStore` and an `ExternalSecret` in a Kubernetes environment.

### What is a Secret?

A **secret** in Kubernetes is an object that contains a small amount of sensitive data, such as a password, OAuth token, or SSH key. Secrets are designed to keep sensitive data out of your pods and containers, making them more secure. Instead of embedding secrets directly into your application code or configuration files, you store them in Kubernetes secrets and reference them where needed.

#### Why Use Secrets?

Using secrets in Kubernetes offers several benefits:

1. **Security**: Secrets are encrypted at rest and in transit, reducing the risk of exposure.
2. **Isolation**: Secrets are isolated from the application code, making it harder for unauthorized access.
3. **Flexibility**: You can manage secrets independently of your application code, allowing for easier updates and rotations.

### Creating a SecretStore

A **SecretStore** is a configuration object that defines how to access secrets stored externally. In the context of Kubernetes, a SecretStore typically points to an external secrets manager like AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault.

#### Steps to Create a SecretStore

To create a SecretStore, you need to define a configuration file that specifies the type of external secrets manager and the necessary credentials to access it.

```yaml
apiVersion: secrets-store.csi.k8s.io/v1
kind: SecretStore
metadata:
  name: my-secret-store
spec:
  provider: aws-secrets-manager
  parameters:
    region: us-east-1
    roleArn: arn:aws:iam::123456789012:role/my-role
```

This configuration file creates a SecretStore named `my-secret-store` that uses AWS Secrets Manager as the provider. The `region` parameter specifies the AWS region, and the `roleArn` parameter specifies the IAM role ARN that has the necessary permissions to access the secrets.

### Creating an ExternalSecret

An **ExternalSecret** is a custom resource definition (CRD) that allows you to fetch secrets from an external secrets manager and store them as Kubernetes secrets. This process automates the retrieval and management of secrets, making it easier to integrate with your applications.

#### Steps to Create an ExternalSecret

To create an ExternalSecret, you need to define a configuration file that references the SecretStore and specifies which secrets to fetch.

```yaml
apiVersion: externalsecrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: SecretStore
    name: my-secret-store
  target:
    name: my-kubernetes-secret
    creationPolicy: Owner
  data:
    - key: my-api-key
      name: api-key
      version: v1
```

This configuration file creates an ExternalSecret named `my-external-secret` that fetches the secret `my-api-key` from the `my-secret-store` and stores it as a Kubernetes secret named `my-kubernetes-secret`. The `refreshInterval` parameter specifies how often the secret should be refreshed.

### Verifying the Secret Retrieval

Once the ExternalSecret is created, you can verify that the secret has been successfully retrieved and stored in Kubernetes.

#### Checking the Service Account

To ensure that the service account has the necessary permissions to access the secret, you can check the service account configuration.

```sh
kubectl get serviceaccount online-boutique -o yaml
```

This command retrieves the service account configuration for the `online-boutique` namespace. Ensure that the service account has the necessary roles and bindings to access the secret.

#### Fetching the Secret

To fetch the secret from Kubernetes, you can use the `kubectl` command.

```sh
kubectl get secret my-kubernetes-secret -o json
```

This command retrieves the secret named `my-kubernetes-secret` and outputs it in JSON format. You can then decode the base64-encoded value to view the actual secret.

```sh
echo "base64_encoded_value" | base64 --decode
```

### Real-World Examples

#### Recent Breaches and CVEs

Recent breaches and CVEs highlight the importance of proper secrets management. For example, the **Capital One breach** in 2019 exposed sensitive customer data due to misconfigured AWS S3 buckets. Similarly, the **Twitter hack** in 2020 involved the theft of API keys, leading to the compromise of high-profile accounts.

These incidents underscore the need for robust secrets management practices, including:

- **Encryption**: Encrypting secrets both at rest and in transit.
- **Access Control**: Implementing strict access control policies to limit who can access secrets.
- **Audit Logging**: Maintaining detailed audit logs to track access and usage of secrets.

### How to Prevent / Defend

#### Detection

To detect unauthorized access to secrets, you can implement monitoring and logging mechanisms. For example, you can use tools like **Falco** or **Sysdig** to monitor system calls and detect suspicious activity.

```yaml
apiVersion: falco.org/v1
kind: FalcoRule
metadata:
  name: detect-secret-access
spec:
  rule: >
    (evt.type = open and evt.arg.path =~ "/etc/secrets/*")
  output: >
    Unauthorized access to secret detected: %proc.name %proc.cmdline
  priority: NOTICE
```

This Falco rule detects attempts to access files in the `/etc/secrets/` directory and logs an alert.

#### Prevention

To prevent unauthorized access to secrets, you can implement the following measures:

- **Role-Based Access Control (RBAC)**: Use RBAC to restrict access to secrets based on user roles and permissions.
- **Least Privilege Principle**: Grant users and services the minimum privileges necessary to perform their tasks.
- **Periodic Audits**: Conduct regular audits to review access logs and identify potential security issues.

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**

```python
import os

# Retrieve secret from environment variable
api_key = os.environ['API_KEY']

# Use the API key in an HTTP request
response = requests.get('https://api.example.com', headers={'Authorization': f'Bearer {api_key}'})
```

**Secure Code**

```python
import os
from kubernetes import client, config

# Load Kubernetes configuration
config.load_kube_config()

# Retrieve secret from Kubernetes
v1 = client.CoreV1Api()
secret = v1.read_namespaced_secret('my-kubernetes-secret', 'default')
api_key = secret.data['api-key'].decode('utf-8')

# Use the API key in an HTTP request
response = requests.get('https://api.example.com', headers={'Authorization': f'Bearer {api_key}'})
```

In the secure code, the API key is retrieved from a Kubernetes secret instead of an environment variable, reducing the risk of exposure.

### Hands-On Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Kubernetes Goat**: A Kubernetes-based security training platform for learning and testing Kubernetes security.

### Conclusion

Effective secrets management is crucial for maintaining the security and integrity of your applications and infrastructure. By using Kubernetes secrets and external secrets managers, you can automate the retrieval and management of secrets, reducing the risk of exposure. Always follow best practices for detection, prevention, and secure coding to ensure the confidentiality and integrity of your secrets.

---

This chapter provides a comprehensive guide to secrets management in DevSecOps, covering the concepts, mechanisms, and best practices for creating and managing secrets in a Kubernetes environment. By following these guidelines, you can ensure the security and integrity of your applications and infrastructure.

---
<!-- nav -->
[[13-Creating a SecretStore and ExternalSecret|Creating a SecretStore and ExternalSecret]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[15-Secrets Management in DevSecOps|Secrets Management in DevSecOps]]
