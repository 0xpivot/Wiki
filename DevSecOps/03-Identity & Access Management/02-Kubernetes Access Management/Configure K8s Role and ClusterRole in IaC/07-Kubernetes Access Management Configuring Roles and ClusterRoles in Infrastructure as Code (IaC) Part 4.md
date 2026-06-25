---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Background Theory

Kubernetes is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. One of the key aspects of managing a Kubernetes cluster is ensuring proper access control to its resources. This is achieved through Role-Based Access Control (RBAC), which allows administrators to define roles and permissions for users and services.

In Kubernetes, roles and cluster roles are two types of resources used to define permissions:

- **Role**: A role is a set of permissions that apply to a specific namespace. It defines what actions can be performed on resources within that namespace.
- **ClusterRole**: A cluster role is similar to a role but applies across the entire cluster, not just a single namespace.

These roles are then bound to subjects (users, groups, service accounts) via role bindings and cluster role bindings.

### Namespace Configuration

A namespace in Kubernetes is a way to divide cluster resources between multiple users or projects. Each namespace provides a scope for names, allowing multiple teams to use the same names for different resources without conflict.

#### Example Namespace Configuration

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: online-boutique
```

This configuration creates a namespace named `online-boutique`. Developers working on the `online-boutique` microservices application will operate within this namespace.

### Creating a Kubernetes Role

The next step is to create a role that defines the permissions for developers within the `online-boutique` namespace. This ensures that developers can only access and modify resources within their own namespace and cannot interfere with other namespaces.

#### Role Definition

Let's define a role named `namespace-viewer` that grants read-only access to certain resources within the `online-boutique` namespace.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: online-boutique
  name: namespace-viewer
rules:
- apiGroups: [""]
  resources: ["pods", "services", "deployments"]
  verbs: ["get", "list", "watch"]
```

This role allows developers to perform the following actions:
- **Get**: Retrieve information about specific resources.
- **List**: List all instances of a resource type.
- **Watch**: Watch for changes to resources.

#### Explanation of Key Components

- **apiGroups**: Specifies the API group to which the resources belong. An empty string (`""`) indicates the core API group.
- **resources**: Lists the resources to which the role applies. In this case, `pods`, `services`, and `deployments`.
- **verbs**: Defines the actions that can be performed on the specified resources. Here, `get`, `list`, and `watch` are read-only operations.

### Role Binding

To associate the `namespace-viewer` role with a subject (such as a service account or user), we need to create a role binding.

#### Role Binding Definition

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: namespace-viewer-binding
  namespace: online-boutique
subjects:
- kind: ServiceAccount
  name: developer-sa
  namespace: online-boutique
roleRef:
  kind: Role
  name: namespace-viewer
  apiGroup: rbac.authorization.k8s.io
```

This role binding associates the `namespace-viewer` role with the `developer-sa` service account within the `online-boutique` namespace.

### ClusterRole Configuration

While roles are namespace-scoped, cluster roles are cluster-wide. They are useful for defining permissions that span multiple namespaces or the entire cluster.

#### Example ClusterRole

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-reader
rules:
- apiGroups: [""]
  resources: ["nodes", "pods"]
  verbs: ["get", "list", "watch"]
```

This cluster role allows read-only access to nodes and pods across the entire cluster.

### ClusterRoleBinding

To bind a cluster role to a subject, we use a cluster role binding.

#### ClusterRoleBinding Definition

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-reader-binding
subjects:
- kind: User
  name: admin-user
roleRef:
  kind: ClusterRole
  name: cluster-reader
  apiGroup: rbac.authorization.k8s.io
```

This cluster role binding associates the `cluster-reader` cluster role with the `admin-user`.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 is a critical vulnerability in Kubernetes that allows an attacker with cluster-admin privileges to bypass RBAC restrictions and execute arbitrary commands on the cluster. This highlights the importance of properly configuring and securing RBAC policies.

#### Secure Coding Practices

To prevent such vulnerabilities, ensure that:
- Roles and cluster roles are defined with the minimum necessary permissions.
- Role bindings and cluster role bindings are tightly controlled and reviewed regularly.
- Regular audits are conducted to identify and mitigate potential security risks.

### How to Prevent / Defend

#### Detection

Use tools like `kubectl auth can-i` to check if a given user or service account has the necessary permissions.

```sh
kubectl auth can-i get pods --as=system:serviceaccount:online-boutique:developer-sa
```

#### Prevention

- **Least Privilege Principle**: Grant roles and cluster roles the minimum necessary permissions.
- **Regular Audits**: Conduct regular reviews of RBAC configurations to identify and mitigate potential security risks.
- **Secure Coding**: Ensure that roles and role bindings are defined securely and reviewed regularly.

#### Secure-Coding Fixes

**Vulnerable Code**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: online-boutique
  name: namespace-viewer
rules:
- apiGroups: [""]
  resources: ["pods", "services", "deployments"]
  verbs: ["*"]
```

**Fixed Code**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: online-boutique
  name: namespace-viewer
rules:
- apiGroups: [""]
  resources: ["pods", "services", "deployments"]
  verbs: ["get", "list", "watch"]
```

### Hands-On Labs

For practical experience with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges focused on Kubernetes security.
- **kube-hunter**: A tool for discovering security issues in Kubernetes clusters.

### Conclusion

Properly configuring roles and cluster roles in Kubernetes is crucial for maintaining a secure and well-managed environment. By following the principles of least privilege and conducting regular audits, you can significantly reduce the risk of unauthorized access and potential security breaches.

---
<!-- nav -->
[[06-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 3|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 3]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[08-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 5|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 5]]
