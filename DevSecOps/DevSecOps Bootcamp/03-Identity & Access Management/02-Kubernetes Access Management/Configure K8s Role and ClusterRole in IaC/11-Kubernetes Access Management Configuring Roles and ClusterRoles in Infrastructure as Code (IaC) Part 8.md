---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that users and services have the appropriate level of access to perform their tasks without compromising the security of the cluster. In Kubernetes, access control is managed through roles and role bindings, which define what actions can be performed and by whom.

### Understanding Roles and ClusterRoles

In Kubernetes, roles and cluster roles are used to define sets of permissions. A **role** is scoped to a specific namespace, meaning it can only grant permissions within that namespace. On the other hand, a **cluster role** is cluster-wide, allowing it to grant permissions across all namespaces.

#### Role

A role is defined within a specific namespace and can only grant permissions within that namespace. Here is an example of a role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This role grants `get`, `watch`, and `list` permissions on pods within the `default` namespace.

#### ClusterRole

A cluster role is defined at the cluster level and can grant permissions across all namespaces. Here is an example of a cluster role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: cluster-viewer
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "watch", "list"]
```

This cluster role grants `get`, `watch`, and `list` permissions on nodes and deployments across all namespaces.

### RoleBindings and ClusterRoleBindings

Once roles and cluster roles are defined, you need to bind them to subjects (users, groups, or service accounts) using role bindings and cluster role bindings.

#### RoleBinding

A role binding binds a role to subjects within a specific namespace. Here is an example of a role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This role binding grants the `pod-reader` role to the user `johndoe` within the `default` namespace.

#### ClusterRoleBinding

A cluster role binding binds a cluster role to subjects across all namespaces. Here is an example of a cluster role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-viewer-binding
subjects:
- kind: User
  name: admin
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-viewer
  apiGroup: rbac.authorization.k8s.io
```

This cluster role binding grants the `cluster-viewer` cluster role to the user `admin` across all namespaces.

### Configuring Roles and ClusterRoles in IaC

Infrastructure as Code (IaC) tools like Terraform, Helm, and Kustomize can be used to manage Kubernetes resources declaratively. Here, we will focus on using Terraform to configure roles and cluster roles.

#### Terraform Configuration

First, ensure you have the necessary Terraform provider for Kubernetes installed:

```sh
terraform init
```

Next, define the roles and cluster roles in your Terraform configuration:

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_role" "pod_reader" {
  metadata {
    name      = "pod-reader"
    namespace = "default"
  }

  rule {
    api_groups   = [""]
    resources    = ["pods"]
    verbs        = ["get", "watch", "list"]
  }
}

resource "kubernetes_cluster_role" "cluster_viewer" {
  metadata {
    name = "cluster-viewer"
  }

  rule {
    api_groups   = [""]
    resources    = ["nodes"]
    verbs        = ["get", "watch", "list"]
  }

  rule {
    api_groups   = ["apps"]
    resources    = ["deployments"]
    verbs        = ["get", "watch", "list"]
  }
}
```

Now, define the role bindings and cluster role bindings:

```hcl
resource "kubernetes_role_binding" "read_pods" {
  metadata {
    name      = "read-pods"
    namespace = "default"
  }

  subject {
    kind      = "User"
    name      = "johndoe"
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    kind     = "Role"
    name     = kubernetes_role.pod_reader.metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }
}

resource "kubernetes_cluster_role_binding" "cluster_viewer_binding" {
  metadata {
    name = "cluster-viewer-binding"
  }

  subject {
    kind      = "User"
    name      = "admin"
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    kind     = "ClusterRole"
    name     = kubernetes_cluster_role.cluster_viewer.metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }
}
```

Finally, apply the configuration:

```sh
terraform apply
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper access management in Kubernetes. For example, the Kubernetes API server was found to be vulnerable to a series of attacks due to misconfigured RBAC policies. One notable example is the CVE-2021-25741, which allowed attackers to escalate privileges by exploiting misconfigured RBAC rules.

### Common Pitfalls and How to Avoid Them

#### Overly Permissive Roles

One common pitfall is creating overly permissive roles that grant more permissions than necessary. This can lead to security risks if the role is compromised. To avoid this, follow the principle of least privilege, granting only the minimum set of permissions required to perform a task.

#### Misconfigured Role Bindings

Another pitfall is misconfiguring role bindings, leading to unintended access. Always double-check the subjects and roles being bound to ensure they align with your security policies.

### How to Prevent / Defend

#### Detection

Regularly audit your RBAC configurations to identify and remediate overly permissive roles and misconfigured bindings. Tools like `kubectl auth can-i` can help verify permissions.

#### Prevention

1. **Principle of Least Privilege**: Grant only the minimum set of permissions required.
2. **Regular Audits**: Conduct regular audits of RBAC configurations.
3. **Automated Scanning**: Use automated scanning tools like `kube-bench` to identify misconfigurations.

#### Secure Coding Fixes

Here is an example of a vulnerable role binding and its secure counterpart:

**Vulnerable Role Binding**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**Secure Role Binding**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader-restricted
  apiGroup: rbac.authorization.k8s.io
```

Where `pod-reader-restricted` is a more restricted role:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader-restricted
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get"]
```

### Hardening Recommendations

1. **Enable RBAC**: Ensure RBAC is enabled in your Kubernetes cluster.
2. **Use Namespaces**: Utilize namespaces to scope roles and limit permissions.
3. **Audit Logs**: Enable and monitor audit logs to detect unauthorized access attempts.

### Hands-On Labs

To practice configuring roles and cluster roles in IaC, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on Kubernetes security, including access management.
- **OWASP Juice Shop**: Provides a Kubernetes environment to practice securing access.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for practicing security hardening.

By following these steps and best practices, you can effectively manage access in your Kubernetes clusters, ensuring both functionality and security.

---
<!-- nav -->
[[10-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 7|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 7]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[12-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)]]
