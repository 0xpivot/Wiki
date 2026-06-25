---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized users and services can perform specific actions within the cluster. This is achieved through role-based access control (RBAC), which allows you to define roles and permissions at both the namespace and cluster levels.

In this section, we will delve into configuring `Role` and `ClusterRole` in Infrastructure as Code (IaC). These are fundamental concepts in Kubernetes RBAC that enable fine-grained access control.

### Understanding Roles and ClusterRoles

#### What are Roles and ClusterRoles?

- **Role**: A `Role` is a set of permissions that apply within a specific namespace. It defines what operations can be performed within that namespace.
- **ClusterRole**: A `ClusterRole` is similar to a `Role`, but it applies across the entire cluster, not just a single namespace.

#### Why Use Roles and ClusterRoles?

Using `Role` and `ClusterRole` allows you to enforce least privilege access, ensuring that users and services have only the necessary permissions to perform their tasks. This minimizes the risk of unauthorized access and potential security breaches.

#### How Roles and ClusterRoles Work

When a user or service attempts to perform an action in Kubernetes, the system checks the associated `Role` or `ClusterRole` to determine if the action is allowed. This is enforced by the API server, which verifies the permissions before executing the requested operation.

### Creating a Namespace

Before diving into `Role` and `ClusterRole`, let's start by creating a namespace. Namespaces are a way to divide cluster resources between multiple users or projects.

#### What is a Namespace?

A namespace is a logical division within a Kubernetes cluster. It allows you to isolate resources and manage them separately. Each namespace has its own set of resources, such as pods, services, and deployments.

#### Creating a Namespace

To create a namespace, you can use a YAML file. Here is an example:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
```

This YAML file defines a namespace named `my-namespace`. You can apply this configuration using `kubectl`:

```sh
kubectl apply -f namespace.yaml
```

### Configuring Roles and ClusterRoles

Now that we have a namespace, let's configure `Role` and `ClusterRole`.

#### Role Configuration

A `Role` is defined within a specific namespace. Here is an example of a `Role` that grants read access to pods within a namespace:

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

This `Role` allows the user to get, watch, and list pods within the `my-namespace` namespace.

#### ClusterRole Configuration

A `ClusterRole` is defined at the cluster level and can be bound to any namespace. Here is an example of a `ClusterRole` that grants read access to pods across the entire cluster:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: pod-reader-cluster
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This `ClusterRole` allows the user to get, watch, and list pods across the entire cluster.

### Binding Roles and ClusterRoles

Once you have defined `Role` and `ClusterRole`, you need to bind them to users or service accounts.

#### RoleBinding

A `RoleBinding` binds a `Role` to a user or service account within a specific namespace. Here is an example:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: my-namespace
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: my-namespace
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This `RoleBinding` binds the `pod-reader` `Role` to the `my-service-account` service account within the `my-namespace` namespace.

#### ClusterRoleBinding

A `ClusterRoleBinding` binds a `ClusterRole` to a user or service account across the entire cluster. Here is an example:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: pod-reader-cluster-binding
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: my-namespace
roleRef:
  kind: ClusterRole
  name: pod-reader-cluster
  apiGroup: rbac.authorization.k8s.io
```

This `ClusterRoleBinding` binds the `pod-reader-cluster` `ClusterRole` to the `my-service-account` service account across the entire cluster.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 was a vulnerability in Kubernetes that allowed an attacker to escalate privileges by manipulating the `ClusterRole` bindings. This highlights the importance of properly configuring and securing your `Role` and `ClusterRole` bindings.

#### Example: Kubernetes Dashboard Vulnerability

The Kubernetes Dashboard is a web-based UI for managing Kubernetes clusters. In 2019, a vulnerability was discovered that allowed attackers to gain unauthorized access to the dashboard. Properly configuring `Role` and `ClusterRole` bindings can help mitigate such risks.

### Pitfalls and Common Mistakes

#### Over-Privileged Roles

One common mistake is granting overly broad permissions to `Role` and `ClusterRole`. This can lead to security vulnerabilities if an attacker gains access to a service account with elevated privileges.

#### Missing RoleBindings

Another common mistake is forgetting to bind `Role` and `ClusterRole` to users or service accounts. Without proper bindings, the roles are ineffective.

### How to Prevent / Defend

#### Detection

To detect misconfigurations, you can use tools like `kube-bench` or `kubescape` to scan your cluster for security issues. These tools can identify over-privileged roles and missing bindings.

#### Prevention

- **Least Privilege Principle**: Always follow the principle of least privilege. Grant only the necessary permissions required for a task.
- **Regular Audits**: Regularly audit your `Role` and `ClusterRole` configurations to ensure they are up-to-date and secure.
- **Automated Scanning**: Use automated scanning tools to detect and remediate misconfigurations.

#### Secure Coding Fixes

Here is an example of a vulnerable `Role` configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: my-namespace
  name: over-privileged-role
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
```

**Secure Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: my-namespace
  name: secure-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

### Hands-On Labs

For practical experience with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab that simulates various Kubernetes security challenges, including RBAC misconfigurations.
- **OWASP WrongSecrets**: A series of challenges that cover various aspects of Kubernetes security, including RBAC.

These labs provide a safe environment to practice and reinforce your understanding of Kubernetes access management.

### Conclusion

Properly configuring `Role` and `ClusterRole` in Kubernetes is essential for maintaining a secure cluster. By following best practices and regularly auditing your configurations, you can minimize the risk of unauthorized access and potential security breaches.

---
<!-- nav -->
[[05-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 2|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 2]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[07-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 4|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 4]]
