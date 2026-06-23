---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management with Role and ClusterRole in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is crucial for securing your cluster and ensuring that only authorized users and services can perform specific actions. At the core of Kubernetes access control are two key concepts: **Roles** and **ClusterRoles**. These roles define the permissions that can be granted to users, groups, or service accounts within the cluster.

### Roles vs. ClusterRoles

- **Roles**: Define permissions within a specific namespace. They are bound to a namespace and can only affect resources within that namespace.
- **ClusterRoles**: Define permissions across the entire cluster. They are not bound to any namespace and can affect resources across all namespaces.

### Configuration in Infrastructure as Code (IaC)

Infrastructure as Code (IaC) tools like Terraform allow you to manage your Kubernetes resources declaratively. This means you can define your roles and cluster roles in code, making them version-controlled and reproducible.

#### Example: Defining a ClusterRole in Terraform

Let's walk through an example of defining a `ClusterRole` and a `ClusterRoleBinding` using Terraform. We'll create a `ClusterRole` named `cluster-viewer` that grants read-only access to all resources in all API groups.

```hcl
resource "kubernetes_cluster_role" "cluster_viewer" {
  metadata {
    name = "cluster-viewer"
  }

  rule {
    api_groups   = ["*"]
    resources    = ["*"]
    verbs        = ["get", "list", "watch"]
  }
}
```

In this configuration:

- `api_groups`: Specifies the API groups to which the permissions apply. `"*"` means all API groups.
- `resources`: Specifies the resources to which the permissions apply. `"*"` means all resources.
- `verbs`: Specifies the actions that can be performed. `"get"`, `"list"`, and `"watch"` are read-only operations.

### ClusterRoleBinding

Once the `ClusterRole` is defined, you need to bind it to a user or service account using a `ClusterRoleBinding`.

```hcl
resource "kubernetes_cluster_role_binding" "admin_user" {
  metadata {
    name = "admin-user-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.cluster_viewer.metadata[0].name
  }

  subject {
    kind      = "User"
    name      = "admin-user"
  }
}
```

In this configuration:

- `role_ref`: References the `ClusterRole` we defined earlier.
- `subject`: Specifies the user or service account to which the role is being bound.

### Full Example with Terraform

Here is the complete Terraform configuration for defining a `ClusterRole` and a `ClusterRoleBinding`:

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_cluster_role" "cluster_viewer" {
  metadata {
    name = "cluster-viewer"
  }

  rule {
    api_groups   = ["*"]
    resources    = ["*"]
    verbs        = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "admin_user" {
  metadata {
    name = "admin-user-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.cluster_viewer.metadata[0].name
  }

  subject {
    kind      = "User"
    name      = "admin-user"
  }
}
```

### Explanation of Key Concepts

#### API Groups

API groups are logical collections of resources in Kubernetes. Examples include `apps`, `batch`, `extensions`, etc. By specifying `"*"` in the `api_groups` field, you grant permissions to all API groups.

#### Resources

Resources are the objects managed by Kubernetes, such as pods, deployments, services, etc. Specifying `"*"` in the `resources` field grants permissions to all resources.

#### Verbs

Verbs represent the actions that can be performed on resources. Common verbs include:

- `get`: Retrieve a specific resource.
- `list`: Retrieve a list of resources.
- `watch`: Watch for changes to a resource.
- `create`: Create a new resource.
- `update`: Update an existing resource.
- `delete`: Delete a resource.

By specifying `["get", "list", "watch"]`, you grant read-only access to the resources.

### Real-World Example: CVE-2021-25741

CVE-2021-25741 is a critical vulnerability in Kubernetes that allows an attacker to escalate their privileges by manipulating the RBAC (Role-Based Access Control) system. This vulnerability highlights the importance of properly configuring and managing your roles and bindings.

#### How to Prevent / Defend

To prevent such vulnerabilities, ensure that:

1. **Least Privilege Principle**: Grant the minimum necessary permissions to users and service accounts.
2. **Regular Audits**: Regularly review and audit your RBAC configurations to ensure they are up-to-date and secure.
3. **Secure Configurations**: Use secure configurations and avoid overly permissive roles.

#### Secure Coding Practices

Here is an example of a vulnerable `ClusterRole` configuration and its secure counterpart:

**Vulnerable Configuration:**

```hcl
resource "kubernetes_cluster_role" "vulnerable_role" {
  metadata {
    name = "vulnerable-role"
  }

  rule {
    api_groups   = ["*"]
    resources    = ["*"]
    verbs        = ["*"]
  }
}
```

**Secure Configuration:**

```hcl
resource "kubernetes_cluster_role" "secure_role" {
  metadata {
    name = "secure-role"
  }

  rule {
    api_groups   = ["apps"]
    resources    = ["deployments", "replicasets"]
    verbs        = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
}
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Overly Permissive Roles**: Avoid granting more permissions than necessary.
2. **Misconfigured Bindings**: Ensure that roles are correctly bound to the intended subjects.
3. **Outdated Configurations**: Regularly review and update your RBAC configurations.

#### Best Practices

1. **Use Namespaces**: Whenever possible, use `Roles` instead of `ClusterRoles` to limit permissions to specific namespaces.
2. **Granular Permissions**: Define granular permissions based on the specific actions required by users or service accounts.
3. **Automated Audits**: Implement automated tools to regularly audit your RBAC configurations.

### Hands-On Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A series of challenges designed to teach Kubernetes security concepts.
- **OWASP WrongSecrets**: A set of challenges that cover various aspects of Kubernetes security, including RBAC.

These labs provide practical experience in configuring and managing Kubernetes roles and bindings.

### Conclusion

Properly configuring and managing Kubernetes roles and bindings is essential for securing your cluster. By using Infrastructure as Code tools like Terraform, you can ensure that your configurations are version-controlled and reproducible. Always follow best practices and regularly audit your configurations to maintain a secure environment.

This comprehensive guide should provide you with a deep understanding of Kubernetes access management and equip you with the knowledge to effectively configure and manage roles and bindings in your Kubernetes clusters.

---
<!-- nav -->
[[12-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[14-Kubernetes Access Management Part 1|Kubernetes Access Management Part 1]]
