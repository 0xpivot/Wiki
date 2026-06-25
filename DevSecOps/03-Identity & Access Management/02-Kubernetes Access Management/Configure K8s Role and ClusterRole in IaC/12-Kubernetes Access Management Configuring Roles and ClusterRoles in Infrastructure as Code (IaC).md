---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is crucial for securing your cluster and ensuring that only authorized users and services can perform specific actions. In Kubernetes, access control is managed through a combination of roles, cluster roles, service accounts, and bindings. These components work together to define who can do what within the cluster.

### Understanding Roles and ClusterRoles

#### What Are Roles and ClusterRoles?

In Kubernetes, **roles** and **cluster roles** are used to define sets of permissions. A **role** is namespaced, meaning it applies to resources within a specific namespace. A **cluster role**, on the other hand, is cluster-wide and applies to resources across all namespaces.

- **Role**: Defines permissions within a specific namespace.
- **ClusterRole**: Defines permissions across the entire cluster.

#### Why Use Roles and ClusterRoles?

Using roles and cluster roles allows you to granularly control access to Kubernetes resources. By defining specific permissions, you can ensure that users and services have only the access they need to perform their tasks, adhering to the principle of least privilege (PoLP).

#### How Roles and ClusterRoles Work

Roles and cluster roles are defined using YAML files. These definitions specify the verbs (actions) that are allowed on certain resources. For example:

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

This role allows the `get`, `watch`, and `list` verbs on pods within the `default` namespace.

For a cluster role, the definition would look similar but without the `namespace` field:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

### Creating Roles and ClusterRoles in IaC

Infrastructure as Code (IaC) tools like Terraform, Ansible, and Helm can be used to manage Kubernetes roles and cluster roles. Here, we'll focus on Terraform as an example.

#### Terraform Example

Terraform is a popular IaC tool that can be used to define and manage Kubernetes resources, including roles and cluster roles.

First, you need to set up your Terraform environment to interact with your Kubernetes cluster. This typically involves setting up a provider block for Kubernetes.

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}
```

Next, you can define a role using the `kubernetes_role` resource:

```hcl
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
```

Similarly, you can define a cluster role using the `kubernetes_cluster_role` resource:

```hcl
resource "kubernetes_cluster_role" "pod_reader" {
  metadata {
    name = "pod-reader"
  }

  rule {
    api_groups   = [""]
    resources    = ["pods"]
    verbs        = ["get", "watch", "list"]
  }
}
```

### Binding Roles and ClusterRoles to Users and Service Accounts

Once roles and cluster roles are defined, they need to be bound to users or service accounts. This is done using role bindings and cluster role bindings.

#### RoleBinding Example

A role binding binds a role to a user or service account within a specific namespace:

```hcl
resource "kubernetes_role_binding" "pod_reader_binding" {
  metadata {
    name      = "pod-reader-binding"
    namespace = "default"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.pod_reader.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = "my-service-account"
    namespace = "default"
  }
}
```

#### ClusterRoleBinding Example

A cluster role binding binds a cluster role to a user or service account across the entire cluster:

```hcl
resource "kubernetes_cluster_role_binding" "pod_reader_binding" {
  metadata {
    name = "pod-reader-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.pod_reader.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = "my-service-account"
    namespace = "default"
  }
}
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 was a critical vulnerability in Kubernetes that allowed attackers to escalate privileges by manipulating the RBAC configuration. This vulnerability underscores the importance of properly configuring and managing roles and cluster roles.

#### Example: AWS IAM Role Assumption

The AWS IAM role assumption mechanism is often used in conjunction with Kubernetes to grant access to AWS resources. This is particularly useful when Kubernetes pods need to access AWS services like S3 or DynamoDB.

Here’s an example of how you might configure an AWS IAM role for a Kubernetes pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account
  containers:
  - name: my-container
    image: my-image
```

In this example, the pod uses a service account named `my-service-account`. You would then bind a role or cluster role to this service account to grant it the necessary permissions.

### Common Pitfalls and Best Practices

#### Pitfall: Overly Permissive Roles

One common pitfall is creating overly permissive roles that grant more access than necessary. This can lead to security vulnerabilities if an attacker gains access to a service account with broad permissions.

#### Best Practice: Principle of Least Privilege (PoLP)

Always adhere to the principle of least privilege. Define roles and cluster roles with the minimum set of permissions required to perform a task. Regularly review and audit your RBAC configurations to ensure they remain secure.

#### Pitfall: Missing Role Bindings

Another common issue is forgetting to bind roles or cluster roles to users or service accounts. Without proper bindings, even well-defined roles will not be effective.

#### Best Practice: Comprehensive Role Bindings

Ensure that all necessary role bindings are in place. Use IaC tools to manage these bindings consistently and reliably.

### How to Prevent / Defend

#### Detection

Regularly audit your Kubernetes RBAC configurations to identify any overly permissive roles or missing bindings. Tools like `kubectl auth can-i` can help you verify permissions.

#### Prevention

- **Use IaC Tools**: Manage roles and bindings using IaC tools like Terraform to ensure consistency and reliability.
- **Principle of Least Privilege**: Define roles with minimal permissions.
- **Regular Audits**: Conduct regular audits of RBAC configurations.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a role definition:

**Vulnerable Version:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: overly-permissive-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**Secure Version:**

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

### Hands-On Labs

To practice Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to Kubernetes security.
- **OWASP Juice Shop**: Provides a vulnerable application that can be deployed on Kubernetes.
- **Kubernetes Goat**: A deliberately insecure Kubernetes cluster for learning and testing.

These labs provide practical experience in configuring and managing Kubernetes roles and cluster roles.

### Conclusion

Properly configuring and managing Kubernetes roles and cluster roles is essential for securing your cluster. By adhering to best practices and using IaC tools, you can ensure that your Kubernetes environment remains secure and compliant with the principle of least privilege. Regular audits and reviews are key to maintaining a secure RBAC configuration.

---
<!-- nav -->
[[11-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 8|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 8]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[13-Kubernetes Access Management with Role and ClusterRole in Infrastructure as Code (IaC)|Kubernetes Access Management with Role and ClusterRole in Infrastructure as Code (IaC)]]
