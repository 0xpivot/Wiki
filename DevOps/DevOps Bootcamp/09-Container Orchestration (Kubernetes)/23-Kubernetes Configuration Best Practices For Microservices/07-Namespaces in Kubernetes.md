---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Namespaces in Kubernetes

### What Are Namespaces?

Namespaces are logical partitions within a Kubernetes cluster. They allow you to divide resources and permissions among different teams or projects. Each namespace provides a scope for naming, which means that two resources can have the same name as long as they are in different namespaces.

### Why Use Namespaces?

Namespaces are crucial for managing large clusters with multiple teams or projects. They provide a way to isolate resources and control access. This isolation helps prevent conflicts between different parts of the system and simplifies management.

### How Do Namespaces Work?

Namespaces are created and managed using `kubectl`. You can create a namespace and then deploy resources into it. Each resource can belong to only one namespace.

#### Example: Creating a Namespace

```bash
kubectl create namespace my-namespace
```

#### Example: Deploying a Resource to a Namespace

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
spec:
  containers:
  - name: my-container
    image: my-image
```

### Best Practice: Isolate Resources

Isolating resources into namespaces helps prevent conflicts and simplifies management. Each team can have its own namespace, and resources can be organized accordingly.

#### Example: Multiple Teams Working in Different Namespaces

```bash
kubectl create namespace team-a
kubectl create namespace team-b
```

Each team can then deploy their resources into their respective namespaces.

### Roles and Role Bindings

Roles and Role Bindings are used to define and enforce permissions within a namespace. Roles define a set of permissions, and Role Bindings associate those roles with users or groups.

#### Example: Defining a Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: my-namespace
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

#### Example: Binding a Role to a User

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: my-namespace
subjects:
- kind: User
  name: jdoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Best Practice: Define Different Privileges

By defining different roles and role bindings, you can control access to resources within a namespace. This ensures that each team has the appropriate level of access.

### How to Prevent / Defend

#### Detection

Use `kubectl` to list and inspect namespaces and their associated roles and role bindings:

```bash
kubectl get namespaces
kubectl get roles --all-namespaces
kubectl get rolebindings --all-namespaces
```

#### Prevention

Ensure that roles and role bindings are defined consistently and that access is controlled appropriately. Use automation tools to enforce these practices.

#### Secure-Coding Fixes

Compare the following insecure and secure versions of a Role Binding:

**Insecure Version**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: my-namespace
subjects:
- kind: User
  name: jdoe
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**Secure Version**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: my-namespace
subjects:
- kind: User
  name: jdoe
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Recent Real-World Examples

In a recent breach, an organization failed to properly define and enforce roles and role bindings, leading to unauthorized access. Ensuring consistent role and role binding practices can help prevent such issues.

### Conclusion

Using labels and namespaces effectively is crucial for managing Kubernetes resources. By following best practices and ensuring proper labeling and isolation, you can improve the security and manageability of your cluster. Regularly review and audit your configurations to ensure they remain secure and effective.

### Practice Labs

For hands-on experience with Kubernetes configuration best practices, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about Kubernetes security.
- **kube-hunter**: A tool for discovering and exploiting vulnerabilities in Kubernetes clusters.

These labs provide practical experience in applying the concepts covered in this chapter.

---
<!-- nav -->
[[06-Liveness Probes|Liveness Probes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/23-Kubernetes Configuration Best Practices For Microservices/00-Overview|Overview]] | [[08-Single Point of Failure in Kubernetes Clusters|Single Point of Failure in Kubernetes Clusters]]
