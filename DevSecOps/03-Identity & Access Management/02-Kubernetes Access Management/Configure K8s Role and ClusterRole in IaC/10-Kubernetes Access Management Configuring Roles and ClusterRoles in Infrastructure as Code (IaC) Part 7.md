---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized users and services can perform specific actions within the cluster. At the core of Kubernetes access management are roles and role bindings, which define what actions a user or service account can perform and in which namespaces. Additionally, cluster roles and cluster role bindings extend these permissions across the entire cluster.

### Understanding Roles and Role Bindings

#### What Are Roles?

A **role** in Kubernetes is a set of permissions that defines what actions can be performed within a specific namespace. These permissions are defined using verbs (such as `get`, `list`, `watch`, `create`, `update`, `patch`, and `delete`) and resources (such as `pods`, `deployments`, `services`, etc.).

#### Why Use Roles?

Using roles allows you to granularly control access to resources within a namespace. This is crucial for maintaining security and ensuring that users only have the minimum necessary permissions to perform their tasks. By limiting access, you reduce the risk of accidental or malicious actions that could compromise your cluster.

#### How Do Roles Work?

Roles are defined using a YAML manifest. Here is an example of a role that grants read-only access to pods in a namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

In this example:
- `apiVersion` specifies the version of the API being used.
- `kind` specifies that this is a `Role`.
- `metadata` contains metadata about the role, including the namespace (`default`) and the name (`pod-reader`).
- `rules` define the permissions granted by the role. In this case, the role allows the verbs `get`, `list`, and `watch` on the `pods` resource.

#### Role Binding

A **role binding** associates a role with one or more subjects (users, groups, or service accounts). This binding specifies which subjects are granted the permissions defined by the role.

Here is an example of a role binding that associates the `pod-reader` role with a user named `developer`:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: RoleBinding
metadata:
  namespace: default
  name: read-pods
subjects:
- kind: User
  name: developer
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

In this example:
- `subjects` specifies the subject (in this case, a user named `developer`).
- `roleRef` references the role (`pod-reader`) that the subject is being bound to.

### Understanding Cluster Roles and Cluster Role Bindings

#### What Are Cluster Roles?

A **cluster role** is similar to a role, but it defines permissions that apply across the entire cluster, not just within a specific namespace. This makes cluster roles useful for defining administrative permissions that span multiple namespaces.

#### Why Use Cluster Roles?

Cluster roles are essential for managing administrative tasks that require access to resources across the entire cluster. For example, a cluster role might grant permissions to manage all deployments in the cluster, regardless of the namespace.

#### How Do Cluster Roles Work?

Cluster roles are defined similarly to roles, but they are not scoped to a specific namespace. Here is an example of a cluster role that grants read-only access to deployments across the entire cluster:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: deployment-reader
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
```

In this example:
- `apiVersion` specifies the version of the API being used.
- `kind` specifies that this is a `ClusterRole`.
- `metadata` contains metadata about the cluster role, including the name (`deployment-reader`).
- `rules` define the permissions granted by the cluster role. In this case, the cluster role allows the verbs `get`, `list`, and `watch` on the `deployments` resource.

#### Cluster Role Binding

A **cluster role binding** associates a cluster role with one or more subjects (users, groups, or service accounts). This binding specifies which subjects are granted the permissions defined by the cluster role.

Here is an example of a cluster role binding that associates the `deployment-reader` cluster role with a user named `admin`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-deployments
subjects:
- kind: User
  name: admin
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: deployment-reader
  apiGroup: rbac.authorization.k8s.io
```

In this example:
- `subjects` specifies the subject (in this case, a user named ` `admin`).
- `roleRef` references the cluster role (`deployment-reader`) that the subject is being bound to.

### Configuring Roles and Cluster Roles in Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is the practice of managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. Kubernetes supports IaC through tools like Terraform, Ansible, and Helm.

#### Using Terraform to Define Roles and Role Bindings

Terraform is a popular IaC tool that can be used to define and manage Kubernetes roles and role bindings. Here is an example of how to define a role and role binding using Terraform:

```hcl
resource "kubernetes_role" "pod_reader" {
  metadata {
    name      = "pod-reader"
    namespace = "default"
  }

  rule {
    api_groups   = [""]
    resources    = ["pods"]
    verbs        = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding" "read_pods" {
  metadata {
    name      = "read-pods"
    namespace = "default"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.pod_reader.metadata[0].name
  }

  subject {
    kind      = "User"
    name      = "developer"
    api_group = "rbac.authorization.k8s.io"
  }
}
```

In this example:
- `kubernetes_role` defines a role named `pod-reader` in the `default` namespace.
- `kubernetes_role_binding` binds the `pod-reader` role to the user `developer`.

#### Using Terraform to Define Cluster Roles and Cluster Role Bindings

Similarly, you can define cluster roles and cluster role bindings using Terraform:

```hcl
resource "kubernetes_cluster_role" "deployment_reader" {
  metadata {
    name = "deployment-reader"
  }

  rule {
    api_groups   = ["apps"]
    resources    = ["deployments"]
    verbs        = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "read_deployments" {
  metadata {
    name = "read-deployments"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.deployment_reader.metadata[0].name
  }

  subject {
    kind      = "User"
    name      = "admin"
    api_group = "rbac.authorization.k8s.io"
  }
}
```

In this example:
- `kubernetes_cluster_role` defines a cluster role named `deployment-reader`.
- `kubernetes_cluster_role_binding` binds the `deployment-reader` cluster role to the user `admin`.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper access management in Kubernetes clusters. For example, the **CVE-2021-25741** vulnerability in Kubernetes allowed attackers to escalate privileges by manipulating the RBAC configuration. This vulnerability underscores the need for robust access controls and regular audits of RBAC configurations.

Another notable breach was the **SolarWinds supply chain attack**, which compromised multiple organizations' Kubernetes clusters. This attack demonstrated the importance of securing the entire supply chain, including the tools and configurations used to manage Kubernetes clusters.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Overly Permissive Roles**: Avoid creating roles with overly broad permissions. Instead, define roles with the minimum necessary permissions.
2. **Hard-Coded Secrets**: Avoid hard-coding secrets or sensitive information in your IaC definitions. Use secrets management tools like HashiCorp Vault or Kubernetes Secrets.
3. **Outdated RBAC Configurations**: Regularly review and update your RBAC configurations to ensure they remain secure and aligned with your organization's policies.

#### Best Practices

1. **Least Privilege Principle**: Follow the principle of least privilege by granting users and service accounts only the permissions they need to perform their tasks.
2. **Regular Audits**: Conduct regular audits of your RBAC configurations to identify and remediate any potential security issues.
3. **Use IaC Tools**: Leverage IaC tools like Terraform to manage your RBAC configurations in a consistent and repeatable manner.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can use Kubernetes audit logs. Audit logs record all API calls made to the Kubernetes API server, allowing you to monitor and analyze access patterns.

Here is an example of how to enable audit logging in Kubernetes:

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:default"]
- level: Request
  users: ["system:serviceaccount:kube-system:default"]
- level: RequestResponse
  users: ["system:serviceaccount:kube-system:default"]
```

In this example:
- `level` specifies the level of detail to log (Metadata, Request, or RequestResponse).
- `users` specifies the users or service accounts to log.

#### Prevention

To prevent unauthorized access, follow these best practices:

1. **Use Strong Authentication Mechanisms**: Ensure that all users and service accounts are authenticated using strong mechanisms such as OAuth2 or X.509 certificates.
2. **Limit Namespace Access**: Restrict access to specific namespaces using roles and role bindings.
3. **Regularly Review RBAC Configurations**: Conduct regular reviews of your RBAC configurations to ensure they remain secure and aligned with your organization's policies.

#### Secure Coding Fixes

Here is an example of a vulnerable role binding and its secure counterpart:

**Vulnerable Role Binding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: default
  name: read-pods
subjects:
- kind: User
  name: developer
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**Secure Role Binding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: default
  name: read-pods
subjects:
- kind: User
  name: developer
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

In this example, the secure role binding follows the principle of least privilege by granting the `developer` user only the necessary permissions to read pods in the `default` namespace.

### Conclusion

Proper access management is critical for securing your Kubernetes clusters. By understanding and implementing roles, role bindings, cluster roles, and cluster role bindings, you can ensure that only authorized users and service accounts have the necessary permissions to perform their tasks. Leveraging IaC tools like Terraform can help you manage your RBAC configurations in a consistent and repeatable manner. Regular audits and following best practices can further enhance the security of your Kubernetes clusters.

### Practice Labs

For hands-on experience with Kubernetes access management, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including some that touch on Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application that includes challenges related to Kubernetes security.
- **Kubernetes Goat**: A Kubernetes-based security training platform that provides hands-on experience with various security concepts, including access management.

By completing these labs, you can gain practical experience with Kubernetes access management and improve your skills in securing Kubernetes clusters.

---
<!-- nav -->
[[09-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 6|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 6]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[11-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 8|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 8]]
