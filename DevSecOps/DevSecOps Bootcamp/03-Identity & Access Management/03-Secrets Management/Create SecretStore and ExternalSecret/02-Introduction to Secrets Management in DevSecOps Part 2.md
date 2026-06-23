---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management in DevSecOps

### What is Secrets Management?

Secrets management is the practice of securely handling sensitive information such as API keys, passwords, and encryption keys within an application. In the context of DevSecOps, this involves ensuring that these secrets are stored, transmitted, and used in a secure manner throughout the development, testing, and production environments.

### Why is Secrets Management Important?

Secrets management is crucial because sensitive data, if compromised, can lead to significant security breaches. For instance, a recent breach involving a misconfigured AWS S3 bucket exposed sensitive data, including API keys and access tokens, leading to unauthorized access and potential financial loss. This highlights the importance of proper secrets management practices.

### How Does Secrets Management Work?

Secrets management typically involves several key components:

1. **Encryption**: Encrypting secrets to ensure they cannot be read in plain text.
2. **Access Control**: Controlling who can access the secrets and under what conditions.
3. **Rotation**: Regularly rotating secrets to minimize the window of exposure.
4. **Storage**: Secure storage mechanisms to protect secrets from unauthorized access.

### Components of Secrets Management in Kubernetes

In Kubernetes, secrets management is handled through various mechanisms, including `Secret` objects and third-party tools like `ExternalSecret`.

#### Kubernetes Secret Object

A `Secret` object in Kubernetes is used to store sensitive data such as passwords, tokens, and keys. These secrets are stored in the Kubernetes API server and can be mounted as files in pods or used as environment variables.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded value
  password: cGFzc3dvcmQ=  # Base64 encoded value
```

### Creating a SecretStore and ExternalSecret

The `SecretStore` and `ExternalSecret` are components provided by the `kubeseal` and `external-secrets` projects, respectively. These tools help manage secrets stored externally and integrate them into Kubernetes.

#### SecretStore

A `SecretStore` is a custom resource definition (CRD) that defines the connection to an external secrets backend, such as HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault.

```yaml
apiVersion: getambassador.io/v2
kind: SecretStore
metadata:
  name: my-secret-store
spec:
  provider:
    vault:
      server: https://vault.example.com
      path: secret/data/my-secrets
```

#### ExternalSecret

An `ExternalSecret` is a CRD that references a `SecretStore` and specifies how to retrieve secrets from the external backend.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-external-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: my-secret-store
    kind: SecretStore
  target:
    name: my-target-secret
    creationPolicy: Owner
  dataFrom:
  - extract:
      key: username
      name: username
  - extract:
      key: password
      name: password
```

### Integrating Secrets Management into Application Deployment

When deploying an application in Kubernetes, it is essential to integrate secrets management into the deployment process. This ensures that sensitive data is handled securely and is available to the application when needed.

#### Example: Online Boutique Application

Consider an online boutique application that requires access to sensitive data such as database credentials and API keys. We can create a `SecretStore` and `ExternalSecret` to manage these secrets.

```yaml
# SecretStore for HashiCorp Vault
apiVersion: getambassador.io/v2
kind: SecretStore
metadata:
  name: vault-secret-store
spec:
  provider:
    vault:
      server: https://vault.example.com
      path: secret/data/my-secrets

# ExternalSecret for retrieving secrets
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: online-boutique-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-secret-store
    kind: SecretStore
  target:
    name: online-boutique-secret
    creationPolicy: Owner
  dataFrom:
  - extract:
      key: db_username
      name: db-username
  - extract:
      key: db_password
      name: db-password
  - extract:
      key: api_key
      name: api-key
```

### Deploying the Application with Secrets

Once the `SecretStore` and `ExternalSecret` are defined, we can deploy the application and mount the secrets as environment variables or files in the pods.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: online-boutique
spec:
  replicas: 3
  selector:
    matchLabels:
      app: online-boutique
  template:
    metadata:
      labels:
        app: online-boutique
    spec:
      containers:
      - name: online-boutique
        image: myregistry/online-boutique:latest
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: online-boutique-secret
              key: db-username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: online-boutique-secret
              key: db-password
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: online-b-secr
              key: api-key
```

### Structuring the Customization Project

To organize the Kubernetes manifest files, we can create a `components` folder to group together different Kubernetes resources related to the application.

```markdown
components/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ...
├── secrets/
│   ├── secret-store.yaml
│   ├── external-secret.yaml
│   └── ...
└── ...
```

### Real-World Examples and Breaches

Recent breaches highlight the importance of proper secrets management. For example, a misconfigured AWS S3 bucket exposed sensitive data, including API keys and access tokens, leading to unauthorized access and potential financial loss.

### How to Prevent / Defend

#### Detection

Regularly audit and monitor access to secrets to detect any unauthorized access. Tools like Kubernetes Audit Logs and Security Information and Event Management (SIEM) systems can help in monitoring and detecting suspicious activities.

#### Prevention

1. **Encrypt Secrets**: Ensure that secrets are encrypted both at rest and in transit.
2. **Access Control**: Implement strict access control policies to limit who can access the secrets.
3. **Secret Rotation**: Regularly rotate secrets to minimize the window of exposure.
4. **Secure Storage**: Use secure storage mechanisms to protect secrets from unauthorized access.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code to understand the differences.

**Vulnerable Code:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded value
  password: cGFzc3dvcmQ=  # Base64 encoded value
```

**Secure Code:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded value
  password: cGFzc3dvcmQ=  # Base64 encoded value
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: myregistry/my-app:latest
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

### Conclusion

Proper secrets management is essential in DevSecOps to ensure the security of sensitive data. By using tools like `SecretStore` and `ExternalSecret`, we can securely manage and integrate secrets into our applications. Regular audits, strict access controls, and secure coding practices are crucial to preventing breaches and ensuring the confidentiality of sensitive data.

### Practice Labs

For hands-on experience with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide practical experience in managing secrets and securing applications in a controlled environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/01-Introduction to Secrets Management in DevSecOps Part 1|Introduction to Secrets Management in DevSecOps Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[03-Introduction to Secrets Management in DevSecOps Part 3|Introduction to Secrets Management in DevSecOps Part 3]]
