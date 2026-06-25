---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## ConfigMaps and Secrets in Kubernetes Pods

### Introduction to ConfigMaps and Secrets

In Kubernetes, `ConfigMaps` and `Secrets` are two essential mechanisms for managing configuration data and sensitive information, respectively. These resources allow you to decouple your application's configuration from its codebase, making it easier to manage and update configurations dynamically.

#### What are ConfigMaps?

A `ConfigMap` is a Kubernetes object that stores configuration data as key-value pairs. This data can be consumed by pods in various ways, such as environment variables, command-line arguments, or as files mounted into the pod's filesystem. ConfigMaps are particularly useful for storing non-sensitive configuration data, such as application settings, connection strings, or default values.

#### Why Use ConfigMaps?

Using ConfigMaps offers several advantages:

1. **Decoupling Configuration from Code**: By externalizing configuration data, you can change configurations without rebuilding or redeploying your application.
2. **Dynamic Updates**: You can update the configuration data independently of the application, allowing for dynamic changes without downtime.
3. **Version Control**: Configuration data can be version-controlled separately from the application code, making it easier to track changes and rollbacks.

#### How ConfigMaps Work

When a pod references a `ConfigMap`, Kubernetes injects the data into the pod based on the specified method. This can be done via environment variables, command-line arguments, or as files mounted into the pod's filesystem.

#### Example: ConfigMap for MongoDB Express

Let's consider an example where we use a `ConfigMap` to configure MongoDB Express. MongoDB Express is a web-based user interface for MongoDB databases.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mongo-express-config
data:
  ME_CONFIG_MONGODB_SERVER: localhost
  ME_CONFIG_MONGODB_PORT: "27017"
```

This `ConfigMap` defines two key-value pairs that will be used to configure MongoDB Express. The keys correspond to environment variables that MongoDB Express expects.

To use this `ConfigMap` in a pod, you can reference it in the pod's definition:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongo-express-pod
spec:
  containers:
  - name: mongo-express
    image: mongoexpress/mongo-express
    envFrom:
    - configMapRef:
        name: mongo-express-config
```

Here, the `envFrom` field tells Kubernetes to inject the environment variables defined in the `ConfigMap` into the container.

### What are Secrets?

A `Secret` is a Kubernetes object that stores sensitive data, such as passwords, API keys, or certificates. Unlike `ConfigMaps`, `Secrets` are designed to handle sensitive information securely. The data stored in a `Secret` is base64-encoded, which helps prevent accidental exposure.

#### Why Use Secrets?

Using `Secrets` provides several benefits:

1. **Security**: Sensitive data is stored securely and is not exposed in plain text within the cluster.
2. **Isolation**: Secrets are isolated from the application code, reducing the risk of accidental exposure.
3. **Dynamic Management**: Like `ConfigMaps`, `Secrets` can be updated dynamically without redeploying the application.

#### How Secrets Work

When a pod references a `Secret`, Kubernetes injects the data into the pod based on the specified method. This can be done via environment variables, command-line arguments, or as files mounted into the pod's filesystem.

#### Example: Secret for MongoDB Credentials

Let's consider an example where we use a `Secret` to store MongoDB credentials.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded "username"
  password: cGFzc3dvcmQ=  # Base64 encoded "password"
```

This `Secret` defines two key-value pairs that store the MongoDB username and password. The values are base64-encoded to ensure security.

To use this `Secret` in a pod, you can reference it in the pod's definition:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongodb-pod
spec:
  containers:
  - name: mongodb
    image: mongo
    env:
    - name: MONGO_INITDB_ROOT_USERNAME
      valueFrom:
        secretKeyRef:
          name: mongodb-secret
          key: username
    - name: MONGO_INITDB_ROOT_PASSWORD
      valueFrom:
        secretKeyRef:
          name:  mongodb-secret
          key: password
```

Here, the `env` field tells Kubernetes to inject the environment variables defined in the `Secret` into the container.

### ConfigMaps and Secrets as Files

Both `ConfigMaps` and `Secrets` can also be used to provide files to pods. This is particularly useful when applications expect configuration data to be stored in files rather than environment variables.

#### Example: ConfigMap as a File

Let's consider an example where we use a `ConfigMap` to provide a configuration file to a pod.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: configmap-file
data:
  config.txt: |
    server = "localhost"
    port = 8080
```

This `ConfigMap` defines a file named `config.txt` with some configuration data.

To use this `ConfigMap` in a pod, you can mount it as a volume:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-pod
spec:
  containers:
  - name: app
    image: myapp
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: configmap-file
```

Here, the `volumeMounts` field tells Kubernetes to mount the `ConfigMap` as a volume at `/etc/config`.

#### Example: Secret as a File

Let's consider an example where we use a `Secret` to provide a file containing sensitive data to a pod.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-file
type: Opaque
data:
  secret.txt: cGFzc3dvcmQ=  # Base64 encoded "password"
```

This `Secret` defines a file named `secret.txt` with some sensitive data.

To use this `Secret` in a pod, you can mount it as a volume:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: myapp
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secret
  volumes:
  - name: secret-volume
    secret:
      secretName: secret-file
```

Here, the `volumeMounts` field tells Kubernetes to mount the `Secret` as a volume at `/etc/secret`.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-25741

CVE-2021-25741 is a critical vulnerability in Kubernetes that allows attackers to bypass authentication and authorization controls. This vulnerability can be exploited to gain unauthorized access to `ConfigMaps` and `Secrets`, leading to potential data leaks and unauthorized access to sensitive information.

#### Example: CVE-2022-25636

CVE-2022-25636 is another critical vulnerability in Kubernetes that allows attackers to escalate privileges and gain unauthorized access to `ConfigMaps` and `Secrets`. This vulnerability can be exploited to read and modify sensitive data stored in `Secrets`.

### How to Prevent / Defend

#### Detection

To detect unauthorized access to `ConfigMaps` and `Secrets`, you can enable audit logging in Kubernetes. Audit logs record all API calls made to the Kubernetes API server, including those related to `ConfigMaps` and `Secrets`.

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:default"]
- level: Request
  verbs: ["get", "list", "watch"]
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
```

This audit policy records metadata for all API calls made by the `default` service account in the `kube-system` namespace and records the full request for all `get`, `list`, and `watch` operations on `Secrets` and `ConfigMaps`.

#### Prevention

To prevent unauthorized access to `ConfigMaps` and `Secrets`, you should follow these best practices:

1. **Role-Based Access Control (RBAC)**: Use RBAC to restrict access to `ConfigMaps` and `Secrets` to only authorized users and services.
2. **Encryption at Rest**: Encrypt `Secrets` at rest using tools like `Vault` or `KMS`.
3. **Least Privilege Principle**: Grant the minimum necessary permissions to access `ConfigMaps` and `Secrets`.

#### Secure Coding Fixes

Here is an example of a vulnerable `Secret` definition and its secure counterpart:

**Vulnerable Secret Definition:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: insecure-secret
type: Opaque
data:
  password: cGFzc3dvcmQ=  # Base64 encoded "password"
```

**Secure Secret Definition:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secure-secret
type: Opaque
data:
  password: cGFzc3dvcmQ=  # Base64 encoded "password"
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
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

In the secure version, we have added RBAC to restrict access to the `Secret`.

### Hands-On Labs

For hands-on practice with `ConfigMaps` and `Secrets`, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Kubernetes security, including `ConfigMaps` and `Secrets`.
- **OWASP Juice Shop**: Provides a vulnerable web application that you can deploy in Kubernetes and practice securing with `ConfigMaps` and `Secrets`.
- **Kubernetes Goat**: A red team exercise platform that includes challenges related to `ConfigMaps` and `Secrets`.

By following these guidelines and practicing with real-world examples, you can effectively manage configuration data and sensitive information in Kubernetes using `ConfigMaps` and `Secrets`.

---
<!-- nav -->
[[01-Introduction to ConfigMaps and Secrets in Kubernetes|Introduction to ConfigMaps and Secrets in Kubernetes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/37-Using ConfigMaps and Secrets in Kubernetes Pods/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/37-Using ConfigMaps and Secrets in Kubernetes Pods/03-Practice Questions & Answers|Practice Questions & Answers]]
