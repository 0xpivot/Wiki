---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management

### What Are Secrets?

In the context of DevSecOps, secrets are sensitive pieces of information that must be protected. These can include:

- **Database Credentials**: Usernames and passwords used to access databases.
- **API Tokens**: Access tokens required to interact with external services such as Google, Facebook, Twitter, or Stripe.
- **Encryption Keys**: Keys used to encrypt and decrypt data.
- **SSH Keys**: Keys used for secure shell access to servers.

These secrets are critical because unauthorized access to them can lead to severe security breaches, including data theft, unauthorized transactions, and more.

### Why Are Secrets Important?

Secrets are essential because they control access to sensitive resources. Without proper management, these secrets can be exposed, leading to significant security risks. For instance, if an attacker gains access to a database password, they can potentially read, modify, or delete sensitive data. Similarly, if an API key is compromised, an attacker could perform unauthorized actions on behalf of the service, such as making fraudulent transactions or accessing user data.

### Real-World Examples

#### Recent Breaches Involving Secrets

- **Capital One Data Breach (CVE-2019-11510)**: In 2019, Capital One suffered a massive data breach where an attacker accessed sensitive customer data by exploiting a misconfigured web application firewall. The attacker gained access to API keys and other secrets, which allowed them to bypass security measures and access the data.
  
- **Twitter Hack (July 2020)**: In July 2020, high-profile Twitter accounts were hacked, and tweets were posted from these accounts. The attackers gained access to internal Twitter tools and used API keys to post unauthorized tweets. This incident highlighted the importance of securing API keys and other secrets.

### Managing Secrets in Applications

Applications often require access to various resources, such as databases, external APIs, and encryption services. To manage these accesses securely, applications need to handle secrets effectively. Let's explore some common scenarios where secrets are used.

#### Database Access

Consider an application that interacts with multiple databases. Each database requires a set of credentials to ensure secure access. These credentials typically include a username and password. The application must securely store and retrieve these credentials to avoid unauthorized access.

#### External API Access

Many applications integrate with external services, such as social media platforms (Google, Facebook, Twitter) or payment providers (Stripe). These integrations require API tokens or keys, which are sensitive and must be protected.

### Challenges in Managing Secrets

Managing secrets presents several challenges:

1. **Secure Storage**: Secrets must be stored securely to prevent unauthorized access.
2. **Access Control**: Only authorized components should have access to secrets.
3. **Rotation**: Secrets should be rotated periodically to minimize the impact of a potential breach.
4. **Audit**: There should be mechanisms to track who accessed the secrets and when.

### Solutions for Secrets Management

To address these challenges, various solutions exist for managing secrets in applications. We will focus on Kubernetes, a popular container orchestration platform, but the principles apply to other environments as well.

### Kubernetes Secrets Management

Kubernetes provides built-in mechanisms to manage secrets securely. Let's explore these mechanisms in detail.

#### Secret Objects

In Kubernetes, secrets are stored as `Secret` objects. A `Secret` object contains a set of key-value pairs, where each key represents a secret name and each value represents the secret data.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded string
  password: cGFzc3dvcmQ=  # Base64 encoded string
```

In this example, the `username` and `password` are base64-encoded strings. This encoding ensures that the secrets are not easily readable in plain text.

#### Using Secrets in Pods

Pods can reference secrets to access sensitive data. Here’s an example of a pod that uses a secret:

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
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

In this example, the pod references the `db-secret` secret and extracts the `username` and `password` values to set environment variables.

#### Secret Encryption at Rest

Kubernetes supports encrypting secrets at rest using the `Secret Encryption` feature. This feature allows you to encrypt secrets using a master key, which is stored outside of Kubernetes.

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aesgcm:
      keys:
      - name: key1
        secret: VGhpcyBpcyBhIHNlY3JldCBraWU=
```

In this example, the `secrets` resource is encrypted using the AES-GCM provider with a specified key.

### How to Prevent / Defend Against Secret Exposure

#### Detection

To detect potential exposure of secrets, you can use tools like `kube-bench`, which checks your Kubernetes cluster against CIS benchmarks. Additionally, you can monitor logs and audit trails to detect unauthorized access attempts.

#### Prevention

1. **Use Strong Access Controls**: Ensure that only authorized components have access to secrets.
2. **Rotate Secrets Regularly**: Rotate secrets periodically to minimize the impact of a potential breach.
3. **Encrypt Secrets at Rest**: Use encryption to protect secrets stored in Kubernetes.
4. **Monitor and Audit**: Regularly monitor and audit access to secrets to detect any unauthorized access.

#### Secure Coding Fixes

Here’s an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code:**

```python
import os

# Hardcoded database credentials
DB_USERNAME = "admin"
DB_PASSWORD = "password"

def connect_to_db():
    # Connect to database using hardcoded credentials
    pass
```

**Secure Code:**

```python
import os

# Retrieve database credentials from environment variables
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def connect_to_db():
    # Connect to database using environment variables
    pass
```

In the secure code, the database credentials are retrieved from environment variables, which can be set using Kubernetes secrets.

### Conclusion

Secrets management is a critical aspect of DevSecOps. By understanding the importance of secrets, the challenges in managing them, and the solutions provided by Kubernetes, you can ensure that your applications remain secure. Always follow best practices for storing, accessing, and rotating secrets to minimize the risk of exposure.

### Practice Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on managing secrets in web applications.
- **CloudGoat**: Provides scenarios for managing secrets in cloud environments.
- **Kubernetes Goat**: Focuses on Kubernetes-specific scenarios for managing secrets.

By completing these labs, you can gain practical experience in managing secrets securely in your applications.

---
<!-- nav -->
[[05-Introduction to Secrets Management Part 3|Introduction to Secrets Management Part 3]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Why Secrets Manager are needed/00-Overview|Overview]] | [[07-AWS Secrets Manager|AWS Secrets Manager]]
