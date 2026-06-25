---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management in DevSecOps

In the realm of DevSecOps, managing secrets securely is one of the most critical aspects of ensuring the confidentiality and integrity of your applications and infrastructure. Secrets can include API keys, database passwords, SSH keys, and other sensitive information that, if compromised, could lead to significant security breaches. This chapter will delve into the concepts, tools, and best practices for managing secrets in a Kubernetes environment using an External Secrets Controller.

### What Are Secrets?

Secrets are sensitive data such as passwords, tokens, or private keys that are used by applications and services. In Kubernetes, secrets are a special type of object that allows you to store and manage sensitive data securely. By using secrets, you can avoid hardcoding sensitive information directly into your application code or configuration files, which can lead to accidental exposure.

### Why Manage Secrets Securely?

Managing secrets securely is crucial because unauthorized access to these secrets can result in severe consequences, including:

- **Data breaches**: Unauthorized access to sensitive data.
- **Service disruptions**: Compromise of credentials leading to service outages.
- **Financial losses**: Costs associated with recovering from a breach.
- **Reputation damage**: Loss of trust from customers and partners.

Recent real-world examples include:

- **CVE-2021-20225**: A vulnerability in Kubernetes allowed attackers to read secrets stored in etcd, leading to potential exposure of sensitive data.
- **AWS S3 Bucket Exposure**: Multiple incidents where misconfigured S3 buckets led to the exposure of sensitive data, including secrets.

### How Secrets Work in Kubernetes

Kubernetes provides built-in support for managing secrets through the `Secret` object. However, managing secrets manually can become cumbersome, especially in large-scale environments. This is where an External Secrets Controller comes into play.

### External Secrets Controller Overview

The External Secrets Controller is a tool that automates the process of fetching secrets from external secret stores (such as AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault) and injecting them into Kubernetes as `Secret` objects. This approach ensures that secrets are managed externally and only fetched into the cluster when needed, reducing the risk of exposure.

### Prerequisites

Before diving into the demo, ensure you have the following prerequisites set up:

- A running Kubernetes cluster.
- Access to an external secret store (e.g., AWS Secrets Manager).
- The External Secrets Controller installed in your cluster.

### Installing the External Secrets Controller

To install the External Secrets Controller, you can use the Helm chart provided by the project. Here’s how to install it:

```bash
helm repo add external-secrets https://external-secrets.github.io/kubernetes-external-secrets/
helm repo update
helm install external-secrets external-secrets/kubernetes-external-secrets --namespace external-secrets --create-namespace
```

This command installs the External Secrets Controller in a new namespace called `external-secrets`.

### Checking CRDs

After installing the External Secrets Controller, you should verify that the necessary Custom Resource Definitions (CRDs) are present in your cluster. CRDs allow you to define custom resources that extend the capabilities of Kubernetes.

To list all CRDs:

```bash
kubectl get crds
```

To filter for CRDs related to the External Secrets Controller:

```bash
kubectl get crds | grep external-secrets
```

You should see two relevant CRDs:

- `clustersecretstores.k8s.external-secrets.io`
- `externalsecrets.k8s.external-secrets.io`

These CRDs represent the `ClusterSecretStore` and `ExternalSecret` resources, respectively.

### Creating a Cluster Secret Store

A `ClusterSecretStore` is a resource that defines the connection details to an external secret store. For this example, we will configure it to connect to AWS Secrets Manager.

Here’s an example of a `ClusterSecretStore` manifest:

```yaml
apiVersion: k8s.external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      region: us-east-1
      auth:
        roleArn: arn:aws:iam::123456789012:role/ExternalSecretsControllerRole
```

Apply this manifest to your cluster:

```bash
kubectl apply -f cluster-secret-store.yaml
```

### Creating an External Secret

An `ExternalSecret` is a resource that references a secret stored in an external secret store and specifies how it should be injected into the cluster as a `Secret` object.

Here’s an example of an `ExternalSecret` manifest:

```yaml
apiVersion: k8s.external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: my-k8s-secret
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: my-secret-key
        remoteRef:
          key: my-secret-name
```

Apply this manifest to your cluster:

```bash
kubectl apply -f external-secret.yaml
```

### Verifying the Secret Injection

Once the `ExternalSecret` is created, the External Secrets Controller will fetch the secret from AWS Secrets Manager and inject it into the cluster as a `Secret` object.

To verify:

```bash
kubectl get secrets my-k8s-secret -o yaml
```

This command should display the contents of the `my-k8s-secret` object, which contains the data fetched from AWS Secrets Manager.

### Pitfalls and Best Practices

#### Common Mistakes

- **Hardcoding Secrets**: Avoid hardcoding secrets directly into your application code or configuration files.
- **Improper Permissions**: Ensure that the External Secrets Controller has the minimal necessary permissions to access the external secret store.
- **Misconfiguration**: Double-check the configuration of the `ClusterSecretStore` and `ExternalSecret` resources to avoid errors.

#### Best Practices

- **Use Strong Authentication**: Utilize strong authentication mechanisms (e.g., IAM roles) to secure access to the external secret store.
- **Regular Audits**: Regularly audit the usage and access patterns of secrets to detect any anomalies.
- **Least Privilege Principle**: Apply the least privilege principle to limit the permissions of the External Secrets Controller.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable and monitor audit logs for both the external secret store and the Kubernetes cluster to detect unauthorized access attempts.
- **Security Tools**: Use security tools like Falco or Sysdig to monitor and alert on suspicious activities related to secrets.

#### Prevention

- **IAM Roles**: Use IAM roles with limited permissions to control access to the external secret store.
- **Encryption**: Ensure that secrets are encrypted both at rest and in transit.

#### Secure Coding Fixes

**Vulnerable Code Example**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  password: cGFzc3dvcmQ=  # Base64 encoded password
```

**Secure Code Example**:

```yaml
apiVersion: k8s.external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: my-k8s-secret
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: my-secret-key
        remoteRef:
          key: my-secret-name
```

### Conclusion

Managing secrets securely is a critical aspect of DevSecOps. By using an External Secrets Controller, you can automate the process of fetching secrets from external secret stores and injecting them into your Kubernetes cluster. This approach reduces the risk of exposure and ensures that secrets are managed securely.

### Practice Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on secrets management and secure coding practices.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes challenges related to secrets management.
- **Kubernetes Goat**: A security-focused Kubernetes lab that includes exercises on managing secrets securely.

By completing these labs, you can gain practical experience in implementing and securing secrets in a Kubernetes environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Deploy External Secrets Controller Demo Part 1/00-Overview|Overview]] | [[02-Introduction to Secrets Management in DevSecOps|Introduction to Secrets Management in DevSecOps]]
