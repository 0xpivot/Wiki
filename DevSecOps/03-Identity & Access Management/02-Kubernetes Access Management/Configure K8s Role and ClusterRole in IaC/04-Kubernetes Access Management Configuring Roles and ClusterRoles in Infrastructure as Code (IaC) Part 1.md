---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized entities can interact with the cluster resources. This involves configuring roles and cluster roles, which define the permissions granted to users and services within the cluster. In this section, we will delve into the details of configuring these roles using Infrastructure as Code (IaC) tools such as Terraform.

### Understanding Kubernetes Roles and ClusterRoles

In Kubernetes, roles and cluster roles are used to define sets of permissions. A role is scoped to a namespace, meaning it applies only to resources within that namespace. On the other hand, a cluster role is cluster-wide, meaning it applies to all namespaces.

#### Role vs. ClusterRole

- **Role**: 
  - **Scope**: Namespace-specific.
  - **Use Case**: When you want to grant permissions to specific resources within a particular namespace.
  - **Example**: Granting read-only access to pods in a specific namespace.

- **ClusterRole**:
  - **Scope**: Cluster-wide.
  - **Use Case**: When you want to grant permissions across all namespaces.
  - **Example**: Granting administrative access to manage all namespaces.

### Configuring Roles and ClusterRoles Using Terraform

Terraform is a popular IaC tool that allows you to define and provision infrastructure resources in a declarative manner. When working with Kubernetes, Terraform can be used to create and manage roles and cluster roles.

#### Setting Up the Environment

Before diving into the configuration, ensure you have the necessary setup:

1. **Terraform Installed**: Ensure Terraform is installed on your system.
2. **Kubernetes Provider**: Add the Kubernetes provider to your Terraform configuration.
3. **EKS Module**: Use the `terraform-aws-modules/eks/aws` module to manage your Amazon EKS cluster.

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 18.0"

  cluster_name = "my-cluster"
  vpc_id       = "vpc-xxxxxxxx"
  subnet_ids   = ["subnet-xxxxxxxx", "subnet-yyyyyyyy"]
}
```

### Retrieving Dynamic Values from EKS

When configuring roles and cluster roles, you often need to reference dynamic values from your EKS cluster, such as the cluster endpoint and the cluster CA certificate.

#### Cluster Endpoint

The cluster endpoint is the URL that clients use to communicate with the Kubernetes API server. This value is returned by the EKS module as an attribute.

```hcl
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}
```

#### Cluster CA Certificate

The cluster CA certificate is used to verify the identity of the Kubernetes API server. This certificate is also returned by the EKS module as an attribute.

```hcl
output "cluster_certificate_authority_data" {
  value = module.eks.cluster_certificate_authority_data
}
```

### Decoding Base64 Encoded Data

The cluster CA certificate is typically returned in base64-encoded format. To use it in your Kubernetes configuration, you need to decode it.

#### Using Terraform Built-in Functions

Terraform provides a built-in function `base64decode` to decode base64-encoded strings.

```hcl
locals {
  decoded_cluster_ca = base64decode(module.eks.cluster_certificate_authority_data)
}
```

### Creating Roles and ClusterRoles

Now that you have the necessary dynamic values, you can proceed to create roles and cluster roles.

#### Example Role Configuration

Here’s an example of creating a role that grants read-only access to pods in a specific namespace.

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
```

#### Example ClusterRole Configuration

Here’s an example of creating a cluster role that grants administrative access to all namespaces.

```hcl
resource "kubernetes_cluster_role" "admin" {
  metadata {
    name = "admin"
  }

  rule {
    api_groups   = ["*"]
    resources    = ["*"]
    verbs        = ["*"]
  }
}
```

### Binding Roles and ClusterRoles to Users or Service Accounts

To apply the roles and cluster roles to users or service accounts, you need to create role bindings and cluster role bindings.

#### Example Role Binding

```hcl
resource "kubernetes_role_binding" "pod_reader_binding" {
  metadata {
    name      = "pod-reader-binding"
    namespace = "default"
  }

  subject {
    kind      = "ServiceAccount"
    name      = "my-service-account"
    namespace = "default"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.pod_reader.metadata[0].name
  }
}
```

#### Example Cluster Role Binding

```hcl
resource "kubernetes_cluster_role_binding" "admin_binding" {
  metadata {
    name = "admin-binding"
  }

  subject {
    kind      = "User"
    name      = "admin-user"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.admin.metadata[0].name
  }
}
```

### Real-World Examples and Recent CVEs

#### CVE-2021-25741: Kubernetes RBAC Misconfiguration

A recent CVE (CVE-2021-25741) highlighted the importance of properly configuring RBAC in Kubernetes. This vulnerability allowed unauthorized access due to misconfigured roles and role bindings.

**Example**: An attacker could exploit a misconfigured role binding that grants excessive permissions to a service account.

**Secure Configuration**:
- Ensure roles and cluster roles are tightly scoped.
- Regularly audit role bindings to ensure they are not granting unnecessary permissions.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable and monitor audit logs to detect unauthorized access attempts.
- **RBAC Audits**: Regularly review and audit RBAC configurations to identify and correct misconfigurations.

#### Prevention

- **Least Privilege Principle**: Always follow the principle of least privilege when assigning roles and permissions.
- **Automated Scanning Tools**: Use tools like `kube-bench` or `kubescape` to scan for misconfigurations and vulnerabilities.

#### Secure Coding Fixes

**Vulnerable Configuration**:
```yaml
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: excessive-permissions-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- kind: User
  name: untrusted-user
```

**Fixed Configuration**:
```yaml
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: limited-permissions-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
subjects:
- kind: User
  name: trusted-user
```

### Conclusion

Properly configuring roles and cluster roles in Kubernetes is essential for maintaining the security and integrity of your cluster. By using IaC tools like Terraform, you can automate and manage these configurations effectively. Regular audits and adherence to the principle of least privilege are key to preventing unauthorized access and ensuring a secure environment.

### Practice Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Kubernetes security.
- **OWASP Juice Shop**: Provides a vulnerable application to practice securing Kubernetes deployments.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for learning and practicing security.

By following these guidelines and practicing with real-world scenarios, you can master the art of securing your Kubernetes clusters through proper access management.

---
<!-- nav -->
[[03-Kubernetes Access Management Configuring Role and ClusterRole in Infrastructure as Code (IaC)|Kubernetes Access Management Configuring Role and ClusterRole in Infrastructure as Code (IaC)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[05-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 2|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 2]]
