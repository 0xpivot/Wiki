---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management in DevSecOps

In the realm of DevSecOps, managing secrets securely is a critical aspect of ensuring the integrity and confidentiality of your applications and infrastructure. Secrets management involves handling sensitive data such as API keys, database passwords, and other confidential information. This chapter will delve into the specifics of creating a `SecretStore` and an `ExternalSecret` in a Kubernetes environment, focusing on the practical implementation and theoretical underpinnings.

### Background Theory

#### What Are Secrets?

Secrets are pieces of sensitive data that should be protected and kept confidential. In a Kubernetes context, secrets can include:

- API keys
- Database passwords
- SSH keys
- TLS certificates

These secrets are typically stored in a secure manner to prevent unauthorized access. Kubernetes provides built-in mechanisms to manage secrets, but these mechanisms may not be sufficient for all use cases, especially when dealing with dynamic secrets or secrets stored externally.

#### Why Manage Secrets Securely?

Managing secrets securely is crucial for several reasons:

1. **Confidentiality**: Ensuring that sensitive data remains confidential and is not exposed to unauthorized users.
2. **Integrity**: Maintaining the integrity of secrets to prevent tampering or unauthorized modifications.
3. **Compliance**: Adhering to regulatory requirements and industry standards that mandate secure handling of sensitive data.
4. **Operational Efficiency**: Automating the management of secrets to reduce manual errors and improve operational efficiency.

### Kubernetes Native Secrets

Before diving into `SecretStore` and `ExternalSecret`, it's important to understand how Kubernetes natively handles secrets.

#### Creating a Kubernetes Secret

A Kubernetes secret is a resource that stores sensitive data such as passwords, tokens, and keys. Here’s how you can create a basic Kubernetes secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # base64 encoded string
  password: cGFzc3dvcmQ=  # base64 encoded string
```

To apply this secret, you would run:

```sh
kubectl apply -f my-secret.yaml
```

This creates a secret named `my-secret` with two key-value pairs (`username` and `password`). The values are base64 encoded to ensure they are not easily readable.

### Limitations of Kubernetes Native Secrets

While Kubernetes secrets provide a basic mechanism for storing sensitive data, they have several limitations:

1. **Static Nature**: Kubernetes secrets are static and do not support dynamic updates or automatic rotation.
2. **Storage**: Secrets are stored in etcd, which is not designed for high-security storage of sensitive data.
3. **Access Control**: Access control for secrets is limited to namespace-level permissions, which may not be granular enough for complex environments.

### Introducing `SecretStore` and `ExternalSecret`

To overcome the limitations of Kubernetes native secrets, tools like `SecretStore` and `ExternalSecret` can be used. These tools allow you to store secrets externally and sync them with your Kubernetes cluster dynamically.

#### What is `SecretStore`?

`SecretStore` is a custom resource definition (CRD) that defines a connection to an external secret store. This allows you to specify where your secrets are stored and how they should be accessed.

#### What is `ExternalSecret`?

`ExternalSecret` is a CRD that defines how to retrieve secrets from an external secret store and inject them into your Kubernetes cluster. It supports various secret stores, including AWS Secrets Manager, HashiCorp Vault, and more.

### Creating a `SecretStore` and `ExternalSecret`

Let's walk through the process of creating a `SecretStore` and an `ExternalSecret` for a Stripe API key stored in AWS Secrets Manager.

#### Step 1: Define the `SecretStore`

First, you need to define the `SecretStore` that points to your external secret store. Here’s an example for AWS Secrets Manager:

```yaml
apiVersion: secrets-store.csi.k8s.io/v1
kind: SecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider: aws-secrets-manager
  parameters:
    region: us-east-1
```

This `SecretStore` specifies that it uses the `aws-secrets-manager` provider and sets the region to `us-east-1`.

#### Step 2: Define the `ExternalSecret`

Next, you need to define the `ExternalSecret` that retrieves the secret from the external store and injects it into your Kubernetes cluster. Here’s an example for a Stripe API key:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: stripe-api-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: stripe-api-secret
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: stripe-api-key
        remoteRef:
          key: stripe-api-key
```

This `ExternalSecret` specifies that it retrieves the secret named `stripe-api-key` from the `aws-secrets-manager` `SecretStore` and injects it into a Kubernetes secret named `stripe-api-secret`.

#### Step 3: Apply the Definitions

To apply these definitions, you would run:

```sh
kubectl apply -f secretstore.yaml
kubectl apply -f externalsecret.yaml
```

### Refresh Interval

One of the key features of `ExternalSecret` is the ability to configure a refresh interval. This determines how often the secret is synced from the external store to the Kubernetes cluster.

#### Configuring Refresh Interval

In the `ExternalSecret` definition, you can set the `refreshInterval` parameter to specify how often the secret should be refreshed. Here’s an example:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: stripe-api-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: stripe-api-secret
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: stripe-api-key
        remoteRef:
          key: stripe-api-key
  refreshInterval: 1h
```

This configuration sets the refresh interval to 1 hour. If the secret changes in the external store, it will be synced to the Kubernetes cluster within this interval.

### Real-World Examples

#### Recent Breaches and CVEs

Several recent breaches and CVEs highlight the importance of secure secrets management:

- **CVE-2021-20225**: A vulnerability in AWS Secrets Manager allowed unauthorized access to secrets.
- **CVE-2021-39296**: A vulnerability in Kubernetes secrets allowed unauthorized access to sensitive data.

These vulnerabilities underscore the need for robust secrets management practices, including the use of external secret stores and dynamic syncing mechanisms.

### Pitfalls and Common Mistakes

#### Misconfigurations

One common pitfall is misconfiguration of the `SecretStore` or `ExternalSecret`. Ensure that the provider and parameters are correctly specified.

#### Insufficient Permissions

Another common issue is insufficient permissions. Ensure that the necessary permissions are granted to access the external secret store.

### How to Prevent / Defend

#### Detection

To detect potential issues with secrets management, you can use tools like:

- **Falco**: A runtime security tool that can detect unauthorized access to secrets.
- **Trivy**: A vulnerability scanner that can identify misconfigured secrets.

#### Prevention

To prevent unauthorized access to secrets, follow these best practices:

- **Use Strong Authentication**: Ensure that strong authentication mechanisms are in place for accessing the external secret store.
- **Limit Permissions**: Grant the minimum necessary permissions to access secrets.
- **Monitor Access**: Regularly monitor access logs to detect any unauthorized access attempts.

#### Secure Coding Fixes

Here’s an example of a vulnerable `ExternalSecret` configuration and the corresponding secure fix:

**Vulnerable Configuration:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: stripe-api-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: stripe-api-secret
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: stripe-api-key
        remoteRef:
          key: stripe-api-key
```

**Secure Fix:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: stripe-api-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: stripe-api-secret
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: stripe-api-key
        remoteRef:
          key: stripe-api-key
  refreshInterval: 1h
```

The secure fix includes setting a refresh interval to ensure that the secret is regularly synced from the external store.

### Conclusion

Managing secrets securely is a critical aspect of DevSecOps. By using tools like `SecretStore` and `ExternalSecret`, you can store secrets externally and sync them dynamically with your Kubernetes cluster. This approach ensures that your secrets remain secure and up-to-date. Always follow best practices for secure coding and monitoring to prevent unauthorized access to sensitive data.

### Practice Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications, including handling secrets.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security techniques.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes exercises on secrets management.

By completing these labs, you can gain practical experience in managing secrets securely in a Kubernetes environment.

---
<!-- nav -->
[[02-Introduction to Secrets Management in DevSecOps Part 2|Introduction to Secrets Management in DevSecOps Part 2]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[04-Introduction to Secrets Management in DevSecOps Part 4|Introduction to Secrets Management in DevSecOps Part 4]]
