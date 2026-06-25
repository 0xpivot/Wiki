---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management in DevSecOps

In the realm of DevSecOps, managing secrets securely is one of the most critical aspects of ensuring the integrity and confidentiality of your applications and infrastructure. Secrets management involves handling sensitive information such as API keys, database passwords, and encryption keys. These secrets must be stored, accessed, and rotated in a way that minimizes exposure and ensures compliance with security policies.

### Why Secrets Management Matters

Secrets management is crucial because:

1. **Security**: Exposure of secrets can lead to unauthorized access to systems and data, potentially resulting in data breaches and financial losses.
2. **Compliance**: Many regulatory frameworks require strict controls over sensitive information.
3. **Operational Efficiency**: Automated secret management reduces the burden on developers and operations teams, allowing them to focus on other tasks.

### Traditional Approaches to Managing Secrets

Traditionally, secrets were often stored in plain text within configuration files or hardcoded into applications. This approach is highly insecure and prone to accidental exposure. To address these issues, modern DevSecOps practices advocate for the use of dedicated secrets management tools and techniques.

### Kubernetes Native Secrets

Kubernetes provides a built-in mechanism for managing secrets through the `Secret` resource. A `Secret` is an object that contains a small amount of sensitive data, such as a password, OAuth token, or SSH key. This data can then be consumed by pods in a secure manner.

#### Creating a Kubernetes Secret Manually

To create a Kubernetes secret manually, you can use the `kubectl` command-line tool. Here’s an example of creating a secret named `my-secret` with a username and password:

```bash
kubectl create secret generic my-secret --from-literal=username=admin --from-literal=password=secretpassword
```

This command creates a secret named `my-secret` with two key-value pairs: `username` and `password`.

#### Using Secrets in Pods

Once a secret is created, it can be used by pods in the cluster. Here’s an example of a pod specification that uses the `my-secret`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    env:
    - name: USERNAME
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: username
    - name: PASSWORD
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: password
```

### Challenges with Manual Secret Management

While Kubernetes secrets provide a basic level of security, they come with several challenges:

1. **Manual Updates**: If a secret value changes due to rotation or manual updates, the secret must be updated manually.
2. **Sync Issues**: There is no automatic synchronization between the secret store and the Kubernetes secret.
3. **Scalability**: Managing secrets across multiple applications and environments can become cumbersome.

### Introducing External Secrets

To address these challenges, the `ExternalSecret` controller was developed. This controller automatically synchronizes secrets from external secret stores into Kubernetes secrets. This ensures that secrets are always up-to-date and reduces the administrative overhead.

#### Components of External Secrets

The `ExternalSecret` controller consists of two main components:

1. **SecretStore**: Defines the connection details to the external secret store.
2. **ExternalSecret**: References the secret in the external store and specifies how it should be synchronized into Kubernetes.

### Creating a SecretStore

A `SecretStore` is a custom resource definition (CRD) that defines the connection details to the external secret store. Here’s an example of creating a `SecretStore` for AWS Secrets Manager:

```yaml
apiVersion: kubernetes-client.io/v1
kind: SecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      auth:
        roleArn: arn:aws:iam::123456789012:role/SecretsManagerRole
```

This `SecretStore` references an AWS IAM role that has permissions to access the AWS Secrets Manager.

### Creating an ExternalSecret

An `ExternalSecret` references a secret in the external store and specifies how it should be synchronized into Kubernetes. Here’s an example of creating an `ExternalSecret` that references a secret in AWS Secrets Manager:

```yaml
apiVersion: kubernetes-client.io/v1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
  target:
    name: my-kubernetes-secret
    creationPolicy: Owner
  data:
  - key: my-secret-key
    name: my-secret-name
```

This `ExternalSecret` references the `my-secret-key` in the AWS Secrets Manager and synchronizes it into a Kubernetes secret named `my-kubernetes-secret`.

### Automatic Sync with External Secrets

One of the key benefits of using `ExternalSecret` is the automatic synchronization of secrets. When a secret value changes in the external store, the `ExternalSecret` controller automatically updates the corresponding Kubernetes secret. This ensures that secrets are always up-to-date without manual intervention.

### Refresh Interval

The `ExternalSecret` controller supports a refresh interval, which determines how often the secret is checked for updates. This can be configured in the `ExternalSecret` specification:

```yaml
apiVersion: kubernetes-client.io/v1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
  target:
    name: my-kubernetes-secret
    creationPolicy: Owner
  refreshInterval: 1h
  data:
  - key: my-secret-key
    name: my-secret-name
```

In this example, the secret is checked for updates every hour.

### Configuration of External Secrets

The `ExternalSecret` controller requires proper configuration to work correctly. This includes setting up the necessary IAM roles and permissions in the external secret store.

#### Example Configuration for AWS Secrets Manager

Here’s an example of configuring an IAM role for AWS Secrets Manager:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    }
  ]
}
```

This policy grants the role permission to retrieve secrets from AWS Secrets Manager.

### Cluster-Wide vs Namespace-Specific Secret Stores

The `SecretStore` can be defined at either the cluster-wide level or at the namespace-specific level. This allows for flexibility in managing secrets across multiple applications and environments.

#### Cluster-Wide Secret Store

A cluster-wide `SecretStore` is defined in the `kube-system` namespace and can be referenced by any `ExternalSecret` in the cluster:

```yaml
apiVersion: kubernetes-client.io/v1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: kube-system
spec:
  provider:
    aws:
      auth:
        roleArn: arn:aws:iam::123456789012:role/SecretsManagerRole
```

#### Namespace-Specific Secret Store

A namespace-specific `SecretStore` is defined in a specific namespace and can only be referenced by `ExternalSecret` resources in that namespace:

```yaml
apiVersion: kubernetes-client.io/v1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: my-namespace
spec:
  provider:
    aws:
      auth:
        roleArn: arn:aws:iam::123456789012:role/SecretsManagerRole
```

### Real-World Examples and Breaches

Several high-profile breaches have occurred due to mismanagement of secrets. For example, the Capital One breach in 2019 exposed sensitive customer data due to a misconfigured AWS S3 bucket. Proper secrets management could have prevented this breach.

### How to Prevent / Defend

#### Detection

To detect mismanaged secrets, you can use tools like TruffleHog, which scans repositories for secrets and other sensitive data. Additionally, you can implement continuous monitoring of your infrastructure to detect unauthorized access attempts.

#### Prevention

1. **Use Dedicated Secrets Management Tools**: Tools like HashiCorp Vault, AWS Secrets Manager, and Azure Key Vault provide robust mechanisms for managing secrets.
2. **Automate Secret Rotation**: Implement automated secret rotation to ensure that secrets are regularly updated.
3. **Least Privilege Principle**: Ensure that IAM roles and permissions are granted based on the least privilege principle.
4. **Secure Coding Practices**: Avoid hardcoding secrets in your applications and use environment variables or configuration files to manage secrets.

#### Secure Code Fix

Here’s an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code:**

```python
import os

def get_api_key():
    return os.environ.get('API_KEY')
```

**Secure Code:**

```python
import os
from kubernetes import client, config

def get_api_key():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret("my-secret", "default")
    api_key = secret.data['api-key']
    return api_key.decode('utf-8')
```

In the secure code, the API key is retrieved from a Kubernetes secret rather than being hardcoded or stored in an environment variable.

### Conclusion

Effective secrets management is essential for maintaining the security and integrity of your applications and infrastructure. By leveraging tools like `ExternalSecret`, you can automate the synchronization of secrets from external stores into Kubernetes, reducing the administrative overhead and ensuring that secrets are always up-to-date.

### Practice Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications, including managing secrets.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security techniques.
- **Kubernetes Goat**: Focuses on Kubernetes security and includes exercises on managing secrets.

By completing these labs, you can gain practical experience in implementing and securing secrets in a Kubernetes environment.

---
<!-- nav -->
[[03-Introduction to Secrets Management in DevSecOps Part 3|Introduction to Secrets Management in DevSecOps Part 3]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[05-Introduction to Secrets Management in DevSecOps|Introduction to Secrets Management in DevSecOps]]
