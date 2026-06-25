---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Creating a Secret Store in Kubernetes

### What is a Secret Store?

A Secret Store is a component that connects a secrets management system (like AWS Secrets Manager) to a Kubernetes cluster. This allows Kubernetes to fetch and manage secrets from an external source.

### Setting Up the Environment

To set up a Secret Store, we need to ensure that the necessary components are deployed and configured correctly. This includes deploying Open Policy Agent (OPA) and configuring the Secret Store.

#### Deploying Open Policy Agent (OPA)

Open Policy Agent (OPA) is a powerful tool for enforcing policies across your infrastructure. To deploy OPA, we need to create a deployment manifest and apply it to the Kubernetes cluster.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opa-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: opa
  template:
    metadata:
      labels:
        app: opa
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:latest
        ports:
        - containerPort: 8181
```

Apply the deployment using `kubectl`:

```sh
kubectl apply -f opa-deployment.yaml
```

#### Configuring the Secret Store

Next, we need to configure the Secret Store to connect to AWS Secrets Manager. This involves creating a `ClusterSecretStore` resource in Kubernetes.

```yaml
apiVersion: secrets-store.csi.k8s.io/v1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider: aws-secrets-manager
  parameters:
    region: us-east-1
```

Apply the Secret Store configuration:

```sh
kubectl apply -f cluster-secret-store.yaml
```

### Verifying the Secret Store

Once the Secret Store is configured, we can verify its status to ensure it is ready to fetch secrets.

```sh
kubectl describe clustersecretstore aws-secrets-manager
```

The output should indicate that the Secret Store is validated and ready.

### Fetching Secrets from AWS Secrets Manager

With the Secret Store configured, we can now fetch secrets from AWS Secrets Manager and store them as Kubernetes native secrets.

#### Creating an External Secret

An External Secret is a custom resource definition (CRD) that allows us to define how secrets should be fetched from an external source and stored in Kubernetes.

```yaml
apiVersion: externalsecrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: stripe-api-key
spec:
  backend:
    name: aws-secrets-manager
    region: us-east-1
  data:
  - key: stripe-api-key
    name: stripe-api-key
    property: api_key
```

Apply the External Secret:

```sh
kubectl apply -f external-secret.yaml
```

### Verifying the External Secret

Once the External Secret is applied, we can verify that the secret has been successfully fetched and stored in Kubernetes.

```sh
kubectl get secret stripe-api-key -o yaml
```

The output should show the secret stored as a Kubernetes native secret.

### Monitoring and Auditing

To ensure the security of secrets, it is important to monitor and audit access to them. This can be done using tools like Kubernetes audit logs and monitoring solutions like Prometheus and Grafana.

#### Enabling Audit Logs

Audit logs can be enabled in Kubernetes to track access to secrets.

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:secrets-store"]
  verbs: ["get", "list", "watch"]
  resources:
  - group: ""
    resources: ["secrets"]
```

Apply the audit policy:

```sh
kubectl apply -f audit-policy.yaml
```

#### Monitoring with Prometheus and Grafana

Prometheus can be used to monitor access to secrets, and Grafana can be used to visualize the data.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kubernetes-audit
spec:
  endpoints:
  - interval: 15s
    port: metrics
  selector:
    matchLabels:
      app: kubernetes-audit
```

Apply the ServiceMonitor:

```sh
kubectl apply -[service-monitor.yaml
```

### How to Prevent / Defend

#### Detection

To detect unauthorized access to secrets, you can use tools like Kubernetes audit logs and monitoring solutions like Prometheus and Grafana.

#### Prevention

To prevent unauthorized access to secrets, you can implement the following measures:

- **Role-Based Access Control (RBAC)**: Ensure that only authorized users and services have access to secrets.
- **Least Privilege Principle**: Grant the minimum permissions necessary to perform a task.
- **Regular Rotation**: Rotate secrets regularly to minimize the window of exposure if they are compromised.
- **Encryption at Rest**: Encrypt secrets at rest to protect them from unauthorized access.

#### Secure Coding Fixes

Here is an example of a vulnerable pattern and the corresponding secure coding fix:

**Vulnerable Pattern:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: insecure-secret
type: Opaque
data:
  password: cGFzc3dvcmQ=  # Base64 encoded password
```

**Secure Coding Fix:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secure-secret
type: Opaque
data:
  password: cGFzc3dvcmQ=  # Base64 encoded password
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-reader-binding
subjects:
- kind: ServiceAccount
  name: my-service-account
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### Conclusion

Secrets management is a critical aspect of DevSecOps. By using tools like AWS Secrets Manager and Kubernetes, you can securely manage secrets and ensure the integrity and confidentiality of your applications. Regular monitoring and auditing are essential to detect and prevent unauthorized access to secrets.

### Practice Labs

For hands-on experience with secrets management in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including secrets management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in managing secrets securely and detecting potential vulnerabilities.

---

This comprehensive chapter covers the fundamentals of secrets management in Kubernetes, including setting up a Secret Store, fetching secrets from AWS Secrets Manager, and securing access to secrets. It also includes detailed explanations, code examples, and practical labs to help you master the topic.

---
<!-- nav -->
[[11-Creating a Secret Store and External Secret|Creating a Secret Store and External Secret]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Create SecretStore and ExternalSecret/00-Overview|Overview]] | [[13-Creating a SecretStore and ExternalSecret|Creating a SecretStore and ExternalSecret]]
