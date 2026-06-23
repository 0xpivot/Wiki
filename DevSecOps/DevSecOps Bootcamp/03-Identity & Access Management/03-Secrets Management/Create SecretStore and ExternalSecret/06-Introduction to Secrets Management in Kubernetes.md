---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management in Kubernetes

In the realm of DevSecOps, managing secrets securely is paramount. Secrets such as API keys, database passwords, and other sensitive information must be handled with care to prevent unauthorized access and potential breaches. Kubernetes provides mechanisms to manage these secrets effectively, ensuring that sensitive data remains protected throughout the application lifecycle.

### What Are Secrets in Kubernetes?

A **Secret** in Kubernetes is an object that contains a small amount of sensitive data, such as a password, OAuth token, or SSH key. This data can then be consumed by pods. Storing sensitive data in a Secret object allows you to decouple it from your application code and manage it independently.

#### Why Use Secrets?

Using Secrets in Kubernetes offers several advantages:

- **Decoupling Sensitive Data**: By storing sensitive data outside of your application code, you reduce the risk of accidentally committing sensitive information to version control systems.
- **Dynamic Management**: Secrets can be updated independently of your application code, allowing you to rotate credentials without redeploying your application.
- **Access Control**: Kubernetes provides fine-grained access control over Secrets, enabling you to restrict which pods can access specific secrets.

### Creating a Secret in Kubernetes

To create a Secret in Kubernetes, you can use the `kubectl` command-line tool. Here’s an example of creating a Secret with a username and password:

```bash
kubectl create secret generic my-secret --from-literal=username=admin --from-literal=password=secretpassword
```

This command creates a Secret named `my-secret` with two key-value pairs: `username` and `password`.

#### Accessing Secrets in Pods

Pods can access Secrets by mounting them as files or environment variables. Here’s an example of a pod specification that mounts a Secret as a volume:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
  volumes:
  - name: secret-volume
    secret:
      secretName: my-secret
```

In this example, the Secret `my-secret` is mounted at `/etc/secrets` within the container. The container can then read the contents of the Secret from this path.

### External Secrets Management

While Kubernetes Secrets provide a basic mechanism for managing secrets, they may not be sufficient for more complex scenarios. For instance, you might want to store secrets in an external vault or manage them across multiple environments. This is where tools like `ExternalSecret` come into play.

#### What Is ExternalSecret?

`ExternalSecret` is a Kubernetes operator that allows you to fetch secrets from external secret stores (such as HashiCorp Vault, AWS Secrets Manager, etc.) and inject them into Kubernetes as native Secrets. This enables you to manage secrets externally while still benefiting from Kubernetes’ built-in Secret management capabilities.

#### Setting Up ExternalSecret

To set up `ExternalSecret`, you first need to install the operator. You can do this using `kubectl`:

```bash
kubectl apply -f https://raw.githubusercontent.com/external-secrets/external-secrets/master/deploy/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/external-secrets/external-secrets/master/deploy/operator.yaml
```

Once the operator is installed, you can define an `ExternalSecret` resource to fetch secrets from an external store. Here’s an example:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  backendType: vault
  backend:
    vault:
      auth:
        method: kubernetes
        role: my-role
      path: secret/data/my-secret
  dataFrom:
  - key: username
    name: username
  - key: password
    name: password
```

In this example, the `ExternalSecret` resource fetches secrets from a HashiCorp Vault at the path `secret/data/my-secret`. The `dataFrom` field specifies which keys from the external secret should be mapped to which keys in the Kubernetes Secret.

### Deploying ExternalSecret with Argo CD

Argo CD is a declarative GitOps continuous delivery tool for Kubernetes. To integrate `ExternalSecret` with Argo CD, you need to ensure that the `ExternalSecret` resource is included in your Git repository and deployed via Argo CD.

Here’s an example of how you might structure your Git repository:

```
├── argocd
│   ├── app-of-apps.yaml
│   └── apps
│       └── my-app
│           ├── kustomization.yaml
│           ├── external-secret.yaml
│           └── deployment.yaml
```

The `app-of-apps.yaml` file defines the top-level application that includes all sub-applications:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: app-of-apps
spec:
  applications:
  - name: my-app
    source:
      repoURL: https://github.com/myorg/myrepo.git
      targetRevision: HEAD
      path: argocd/apps/my-app
```

The `kustomization.yaml` file in the `my-app` directory includes the `external-secret.yaml`:

```yaml
resources:
- deployment.yaml
- external-secret.yaml
```

The `external-secret.yaml` file contains the definition of the `ExternalSecret` resource:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  backendType: vault
  backend:
    vault:
      auth:
        method: kubernetes
        role: my-role
      path: secret/data/my-secret
  dataFrom:
  - key: username
    name: username
  - key: password
    name:
```

When you commit these changes to your Git repository and push them, Argo CD will automatically sync the changes and deploy the `ExternalSecret` resource.

### Pitfalls and Best Practices

#### Common Mistakes

- **Hardcoding Secrets**: Avoid hardcoding secrets directly in your application code or configuration files. Instead, use Kubernetes Secrets or external secret stores.
- **Insufficient Access Control**: Ensure that only authorized pods can access specific secrets. Use Kubernetes RBAC to enforce strict access control policies.
- **Insecure Transmission**: When transmitting secrets, ensure that they are encrypted both in transit and at rest. Use TLS for secure communication and encryption algorithms for storing secrets.

#### Best Practices

- **Use External Secret Stores**: Store sensitive data in external secret stores like HashiCorp Vault or AWS Secrets Manager. This allows you to manage secrets independently of your application code.
- **Automate Secret Rotation**: Implement automated secret rotation to minimize the window of exposure for compromised secrets.
- **Audit and Monitor**: Regularly audit and monitor access to secrets to detect and respond to unauthorized access attempts.

### Real-World Examples

#### Recent Breaches

- **Capital One Data Breach (CVE-2019-11510)**: In 2019, Capital One suffered a massive data breach due to misconfigured AWS S3 buckets. The attacker was able to access sensitive customer data because the S3 buckets were publicly accessible. This highlights the importance of securing sensitive data and implementing proper access controls.
- **Twitter Hack (CVE-2020-14720)**: In July 2020, Twitter suffered a high-profile hack where the accounts of several prominent individuals were compromised. The attackers gained access to Twitter’s internal systems by exploiting a vulnerability in the company’s Single Sign-On (SSO) system. This underscores the need for robust authentication and authorization mechanisms.

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Implement comprehensive logging and monitoring to detect unauthorized access attempts. Use tools like ELK Stack or Splunk to aggregate and analyze logs.
- **Security Information and Event Management (SIEM)**: Use SIEM tools to correlate security events and detect anomalies. This helps in identifying potential security incidents in real-time.

#### Prevention

- **Access Control**: Implement strict access control policies using Kubernetes RBAC. Ensure that only authorized pods can access specific secrets.
- **Encryption**: Encrypt secrets both in transit and at rest. Use TLS for secure communication and strong encryption algorithms for storing secrets.
- **Automated Audits**: Regularly perform automated audits to check for misconfigurations and vulnerabilities. Use tools like `kube-bench` or `cis-kube-bench` to validate compliance with security best practices.

#### Secure Coding Fixes

##### Vulnerable Code Example

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
    - name: DB_PASSWORD
      value: secretpassword
```

##### Secure Code Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    envFrom:
    - secretRef:
        name: db-secret
```

In the secure code example, the `DB_PASSWORD` is fetched from a Kubernetes Secret named `db-secret`, rather than being hardcoded in the pod specification.

### Conclusion

Managing secrets securely is a critical aspect of DevSecOps. By leveraging Kubernetes Secrets and tools like `ExternalSecret`, you can ensure that sensitive data remains protected throughout the application lifecycle. Always follow best practices for securing secrets, and regularly audit and monitor access to detect and respond to potential security incidents.

### Practice Labs

For hands-on practice with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including topics related to secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including handling sensitive data.
- **Kubernetes Goat**: A series of challenges designed to test your Kubernetes security knowledge, including secrets management.

By completing these labs, you can gain practical experience in managing secrets securely in a Kubernetes environment.

---
<!-- nav -->
[[05-Introduction to Secrets Management in DevSecOps|Introduction to Secrets Management in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[07-Introduction to Secrets Management Part 1|Introduction to Secrets Management Part 1]]
