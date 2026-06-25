---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes (often abbreviated as K8s) is an open-source system for automating deployment, scaling, and management of containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring proper access control. Access management in Kubernetes involves defining roles and permissions for users and services to interact with the cluster resources securely. This chapter will delve into configuring `Role` and `ClusterRole` using Infrastructure as Code (IaC) tools, specifically focusing on the Kubernetes provider in Terraform.

### Background Theory

Before diving into the practical aspects, it's essential to understand the theoretical underpinnings of Kubernetes access management.

#### What is Kubernetes Access Control?

Kubernetes uses Role-Based Access Control (RBAC) to manage access to the API server. RBAC allows you to grant permissions to users and services based on their roles within the organization. There are two primary types of roles in Kubernetes:

- **Role**: Defines permissions within a namespace.
- **ClusterRole**: Defines permissions across the entire cluster.

Both roles can be bound to subjects (users, groups, or service accounts) through `RoleBinding` and `ClusterRoleBinding`.

#### Why is Access Control Important?

Access control is crucial for several reasons:

- **Security**: Ensures that only authorized entities can perform actions within the cluster.
- **Compliance**: Helps organizations adhere to regulatory requirements by limiting access to sensitive resources.
- **Operational Efficiency**: Allows fine-grained control over who can perform specific tasks, reducing the risk of accidental or malicious changes.

### Configuring Kubernetes Provider in Terraform

To manage Kubernetes resources using Terraform, you need to configure the Kubernetes provider. This section will guide you through setting up the provider and referencing the EKS cluster dynamically.

#### Setting Up the Kubernetes Provider

First, you need to define the Kubernetes provider in your Terraform configuration. Here’s how you can set it up:

```hcl
provider "kubernetes" {
  host                   = var.kubernetes_host
  client_certificate     = var.client_certificate
  client_key             = var.client_key
  cluster_ca_certificate = var.cluster_ca_certificate
}
```

In this configuration:

- `host`: The URL of the Kubernetes API server.
- `client_certificate`: The path to the client certificate.
- `client_key`: The path to the client key.
- `cluster_ca_certificate`: The path to the CA certificate for the cluster.

#### Referencing the EKS Cluster Dynamically

When working with Amazon Elastic Kubernetes Service (EKS), you often need to reference the cluster details dynamically. This is particularly useful when you are creating the EKS cluster and want to use the provider immediately.

Here’s an example of how to configure the Kubernetes provider to reference an EKS cluster:

```hcl
provider "aws" {
  region = var.region
}

module "eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 18.0"

  cluster_name            = var.cluster_name
  cluster_version         = var.cluster_version
  subnets                 = var.subnets
  vpc_id                  = var.vpc_id
  node_groups             = var.node_groups
  enable_iam              = true
  additional_policies     = ["arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"]
  tags                    = var.tags
}

provider "kubernetes" {
  host                   = module.eks_cluster.endpoint
  client_certificate     = base64decode(module.eks_cluster.certificate_authority_data)
  client_key             = base64decode(module.eks_cluster.certificate_authority_data)
  cluster_ca_certificate = base64decode(module. eks_cluster.certificate_authority_data)
}
```

In this example:

- `module "eks_cluster"`: Defines the EKS cluster using the `terraform-aws-modules/eks/aws` module.
- `provider "kubernetes"`: References the EKS cluster details dynamically.

### Defining Roles and ClusterRoles

Now that the Kubernetes provider is configured, you can define `Role` and `ClusterRole` resources.

#### Role Definition

A `Role` defines permissions within a specific namespace. Here’s an example of defining a `Role`:

```hcl
resource "kubernetes_role" "example" {
  metadata {
    name      = "example-role"
    namespace = "default"
  }

  rule {
    api_groups   = [""]
    resources    = ["pods"]
    verbs        = ["get", "list", "watch"]
  }
}
```

In this example:

- `metadata.name`: The name of the role.
- `metadata.namespace`: The namespace where the role is defined.
- `rule.api_groups`: The API group to which the resource belongs.
- `rule.resources`: The resources to which the role applies.
- `rule.verbs`: The actions that the role can perform.

#### ClusterRole Definition

A `ClusterRole` defines permissions across the entire cluster. Here’s an example of defining a `ClusterRole`:

```hcl
resource "kubernetes_cluster_role" "example" {
  metadata {
    name = "example-cluster-role"
  }

  rule {
    api_groups   = [""]
    resources    = ["pods"]
    verbs        = ["get", "list", "watch"]
  }
}
```

In this example:

- `metadata.name`: The name of the cluster role.
- `rule.api_groups`: The API group to which the resource belongs.
- `rule.resources`: The resources to which the cluster role applies.
- `rule.verbs`: The actions that the cluster role can perform.

### Binding Roles and ClusterRoles

Once you have defined roles and cluster roles, you need to bind them to subjects (users, groups, or service accounts).

#### RoleBinding Example

Here’s an example of binding a `Role` to a service account:

```hcl
resource "kubernetes_role_binding" "example" {
  metadata {
    name      = "example-role-binding"
    namespace = "default"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.example.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = "example-service-account"
    namespace = "default"
  }
}
```

In this example:

- `role_ref`: References the `Role` to be bound.
- `subject`: Specifies the service account to which the role is bound.

#### ClusterRoleBinding Example

Here’s an example of binding a `ClusterRole` to a user:

```hcl
resource "kubernetes_cluster_role_binding" "example" {
  metadata {
    name = "example-cluster-role-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.example.metadata[0].name
  }

  subject {
    kind      = "User"
    name      = "example-user"
  }
}
```

In this example:

- `role_ref`: References the `ClusterRole` to be bound.
- `subject`: Specifies the user to which the cluster role is bound.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities highlight the importance of proper access management in Kubernetes clusters. For instance, the CVE-2021-25741 vulnerability in Kubernetes allowed unauthorized access to sensitive resources due to misconfigured RBAC policies.

#### CVE-2021-25741

This vulnerability allowed attackers to bypass RBAC restrictions and gain unauthorized access to sensitive resources. The issue was caused by a flaw in the way Kubernetes handled certain API requests.

**Impact**: Unauthorized access to sensitive resources.

**Mitigation**: Ensure that RBAC policies are correctly configured and regularly audited.

### How to Prevent / Defend

Proper access management is crucial for securing Kubernetes clusters. Here are some best practices and mitigation strategies:

#### Secure Coding Practices

Ensure that roles and bindings are defined securely. Here’s an example of a vulnerable and a secure configuration:

**Vulnerable Configuration**:

```hcl
resource "kubernetes_role" "vulnerable" {
  metadata {
    name      = "vulnerable-role"
    namespace = "default"
  }

  rule {
    api_groups   = [""]
    resources    = ["*"]
    verbs        = ["*"]
  }
}
```

**Secure Configuration**:

```hcl
resource "kubernetes_role" "secure" {
  metadata {
    name      = "secure-role"
    namespace = "default"
  }

  rule {
    api_groups   = [""]
    resources    = ["pods"]
    verbs        = ["get", "list", "watch"]
  }
}
```

#### Regular Audits

Regularly audit RBAC policies to ensure they are correctly configured. Use tools like `kubectl auth can-i` to check permissions.

#### Hardening Strategies

- **Least Privilege Principle**: Grant only the minimum necessary permissions.
- **Regular Updates**: Keep Kubernetes and related components up to date.
- **Monitoring and Logging**: Implement monitoring and logging to detect unauthorized access attempts.

### Conclusion

Proper access management in Kubernetes is essential for maintaining the security and integrity of your cluster. By configuring roles and cluster roles using IaC tools like Terraform, you can ensure that your cluster is secure and compliant with organizational policies. Regular audits and secure coding practices are key to preventing unauthorized access and mitigating potential vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about Kubernetes security.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters.

These labs provide practical experience in configuring and securing Kubernetes clusters.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/02-Introduction to Kubernetes Access Management|Introduction to Kubernetes Access Management]]
