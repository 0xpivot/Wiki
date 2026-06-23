---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management in DevSecOps

In the realm of DevSecOps, managing secrets securely is one of the most critical aspects of ensuring the integrity and confidentiality of your applications and infrastructure. Secrets management involves handling sensitive data such as API keys, database passwords, and other confidential information. This chapter will delve into the creation of a `SecretStore` and an `ExternalSecret` in a Kubernetes environment, focusing on integrating with AWS Secrets Manager.

### Background Theory

Before diving into the practical steps, it's essential to understand the theoretical underpinnings of secrets management in a Kubernetes context.

#### What is a Secret?

A `Secret` in Kubernetes is an object that contains a small amount of sensitive data, such as a password, OAuth token, or SSH key. Secrets are designed to be used more securely than environment variables or config maps. They are stored in etcd encrypted at rest and can be mounted as files in a pod or provided through environment variables.

#### Why Use Secrets?

Using `Secrets` ensures that sensitive data is not exposed in plain text within your application code or configuration files. This reduces the risk of accidental exposure and makes it easier to manage and rotate credentials.

#### How Secrets Work

When a `Secret` is created, it is stored in etcd, which is the distributed key-value store used by Kubernetes. The data in a `Secret` is base64 encoded, providing a basic level of obfuscation. However, it's important to note that base64 encoding is not encryption; it merely hides the data from casual inspection.

### Integrating with AWS Secrets Manager

AWS Secrets Manager is a service that helps you protect access to your applications, services, and IT resources without requiring you to manage and protect the underlying credentials. By integrating AWS Secrets Manager with Kubernetes, you can centralize the management of secrets and ensure they are securely stored and accessed.

#### What is AWS Secrets Manager?

AWS Secrets Manager is a fully managed service that helps you protect access to your applications, services, and IT resources. It enables you to easily rotate, manage, and retrieve database credentials, API keys, and other secrets throughout their lifecycle.

#### Why Use AWS Secrets Manager?

Using AWS Secrets Manager provides several benefits:

- **Centralized Management**: All your secrets are stored in a centralized location, making it easier to manage and audit them.
- **Automatic Rotation**: You can configure automatic rotation of secrets, reducing the risk of long-lived credentials.
- **Secure Access**: Secrets are encrypted both at rest and in transit, ensuring they are protected from unauthorized access.

### Creating a `SecretStore`

The first step in integrating AWS Secrets Manager with Kubernetes is to create a `SecretStore`. A `SecretStore` is a custom resource definition (CRD) that defines the connection to the secrets manager.

#### Step-by-Step Guide

1. **Define the `SecretStore` CRD**:
   - The `SecretStore` CRD specifies the connection details to the secrets manager.
   - In this case, we are connecting to AWS Secrets Manager.

```yaml
apiVersion: secrets-store.csi.k8s.io/v1
kind: SecretStore
metadata:
  name: aws-secret-store
spec:
  provider: aws
  parameters:
    region: us-east-1
```

2. **Apply the `SecretStore` CRD**:
   - Apply the `SecretStore` CRD to the Kubernetes cluster using `kubectl`.

```sh
kubectl apply -f aws-secret-store.yaml
```

3. **Verify the `SecretStore`**:
   - Check that the `SecretStore` has been successfully created.

```sh
kubectl get secretstores.csi.k8s.io
```

### Creating an `ExternalSecret`

Once the `SecretStore` is set up, you can create an `ExternalSecret` to retrieve secrets from AWS Secrets Manager.

#### Step-by-Step Guide

1. **Define the `ExternalSecret` CRD**:
   - The `ExternalSecret` CRD specifies the secrets to be retrieved from the `SecretStore`.
   - In this case, we are retrieving a secret named `my-secret` from AWS Secrets Manager.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  secretStoreRef:
    kind: SecretStore
    name: aws-secret-store
  target:
    name: my-kubernetes-secret
    creationPolicy: Owner
  dataFrom:
  - extract:
      key: my-secret
      name: my-secret-key
```

2. **Apply the `ExternalSecret` CRD**:
   - Apply the `ExternalSecret` CRD to the Kubernetes cluster using `kubectl`.

```sh
kubectl apply -f my-external-secret.yaml
```

3. **Verify the `ExternalSecret`**:
   - Check that the `ExternalSecret` has been successfully created and that the secret has been retrieved from AWS Secrets Manager.

```sh
kubectl get externalsecrets
kubectl get secret my-kubernetes-secret -o yaml
```

### Full Example

Here is a complete example of creating a `SecretStore` and an `ExternalSecret`:

#### `aws-secret-store.yaml`

```yaml
apiVersion: secrets-store.csi.k8s.io/v1
kind: SecretStore
metadata:
  name: aws-secret-store
spec:
  provider: aws
  parameters:
    region: us-east-1
```

#### `my-external-secret.yaml`

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  secretStoreRef:
    kind: SecretStore
    name: aws-secret-store
  target:
    name: my-kubernetes-secret
    creationPolicy: Owner
  dataFrom:
  - extract:
      key: my-secret
      name: my-secret-key
```

### Applying the Configuration

```sh
kubectl apply -f aws-secret-store.yaml
kubectl apply -f my-外部秘密.yaml
```

### Verification

```sh
kubectl get secretstores.csi.k8s.io
kubectl get externalsecrets
kubectl get secret my-kubernetes-secret -o yaml
```

### Real-World Examples

#### Recent CVEs and Breaches

One notable breach involving secrets management was the Capital One breach in 2019. The attacker gained access to sensitive data, including personal information of customers, by exploiting a misconfigured server. This highlights the importance of properly securing and managing secrets.

#### Secure Coding Practices

To prevent such breaches, it's crucial to follow secure coding practices:

- **Use Environment Variables**: Avoid hardcoding secrets in your application code.
- **Rotate Secrets Regularly**: Implement automatic rotation of secrets to reduce the window of opportunity for attackers.
- **Audit Access Logs**: Regularly review access logs to detect any unauthorized access attempts.

### How to Prevent / Defend

#### Detection

- **Monitor Access Logs**: Use tools like AWS CloudTrail to monitor access to secrets.
- **Set Up Alerts**: Configure alerts for any suspicious activity related to secrets.

#### Prevention

- **Use IAM Policies**: Restrict access to secrets using IAM policies.
- **Enable Encryption**: Ensure that secrets are encrypted both at rest and in transit.

#### Secure-Coding Fixes

##### Vulnerable Code

```python
import os

# Hardcoded secret
db_password = "my-secret-password"
```

##### Fixed Code

```python
import os

# Retrieve secret from environment variable
db_password = os.getenv("DB_PASSWORD")
```

### Conclusion

Managing secrets securely is a critical aspect of DevSecOps. By integrating AWS Secrets Manager with Kubernetes, you can centralize the management of secrets and ensure they are securely stored and accessed. Following secure coding practices and implementing proper detection and prevention mechanisms can help mitigate the risk of breaches.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning security concepts.

These labs provide a practical way to apply the concepts learned in this chapter and gain hands-on experience with secrets management in a Kubernetes environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[02-Introduction to Secrets Management in DevSecOps Part 2|Introduction to Secrets Management in DevSecOps Part 2]]
