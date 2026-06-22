---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of the `manage_aws_auth_config_map` attribute in the EKS cluster configuration.**

The `manage_aws_auth_config_map` attribute in the EKS cluster configuration is used to enable or disable the modification of the AWS authentication config map (`aws-auth`) by the EKS service. When set to `true`, it allows EKS to modify the `aws-auth` config map, enabling the addition of custom entries to map AWS IAM roles/users to Kubernetes roles/users. This config map is crucial for integrating AWS IAM roles with Kubernetes roles, providing a bridge between AWS resources and Kubernetes permissions.

**Q2. How would you create an IAM role for a Kubernetes admin using Terraform? Provide a sample Terraform code snippet.**

To create an IAM role for a Kubernetes admin using Terraform, you can use the `aws_iam_role` resource. Here is a sample Terraform code snippet:

```hcl
variable "admin_user_arn" {
  description = "ARN of the AWS user who will assume the admin role"
}

resource "aws_iam_role" "external_admin" {
  name = "external-admin"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.admin_user_arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  inline_policy {
    name = "external_admin_policy"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "eks:Describe*",
            "eks:List*"
          ]
          Resource = "*"
        }
      ]
    })
  }
}
```

This code defines an IAM role named `external-admin` that can be assumed by the specified AWS user (`admin_user_arn`). The role includes an inline policy that grants read-only access to EKS cluster configurations.

**Q3. Why is it important to separate the EKS cluster administration from the Kubernetes cluster administration? Provide a recent real-world example to illustrate this point.**

Separating EKS cluster administration from Kubernetes cluster administration is crucial for maintaining clear boundaries and ensuring proper security practices. This separation ensures that administrative actions related to the underlying AWS infrastructure (EKS) are distinct from the Kubernetes cluster operations, which can be managed via Kubernetes-specific mechanisms like RBAC.

A recent real-world example is the incident involving the Capital One data breach in 2019. Although not directly related to Kubernetes, the breach highlighted the importance of strict access controls and separation of duties. If administrative access to the Kubernetes cluster had been tightly controlled and separated from general AWS administrative tasks, it might have reduced the risk of unauthorized access and potential breaches.

By separating EKS administration from Kubernetes administration, organizations can enforce stricter access controls and ensure that only authorized personnel can perform critical operations, reducing the risk of accidental or malicious changes to the cluster.

**Q4. How would you map an AWS IAM role to a Kubernetes role using the `aws-auth` config map? Provide a sample Terraform code snippet.**

To map an AWS IAM role to a Kubernetes role using the `aws-auth` config map, you can use the `kubernetes_config_map` resource in Terraform. Here is a sample Terraform code snippet:

```hcl
locals {
  aws_auth_config_map = {
    mapRoles = [
      {
        rolearn = aws_iam_role.external_admin.arn
        username = "kubernetes-admin"
        groups = ["system:masters"]
      },
      {
        rolearn = aws_iam_role.external_developer.arn
        username = "kubernetes-developer"
        groups = []
      }
    ]
  }
}

resource "kubernetes_config_map" "aws_auth" {
  metadata {
    name = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    "mapRoles" = jsonencode(local.aws_auth_config_map.mapRoles)
  }
}
```

This code snippet defines a `kubernetes_config_map` resource named `aws-auth` in the `kube-system` namespace. It maps the `external-admin` IAM role to the `kubernetes-admin` user in Kubernetes and assigns it to the `system:masters` group, while the `external-developer` IAM role is mapped to the `kubernetes-developer` user without any group assignments.

**Q5. Why is it important to adhere to security best practices such as not assigning human users to the `system:masters` group in Kubernetes? Provide a recent real-world example to illustrate this point.**

Adhering to security best practices such as not assigning human users to the `system:masters` group in Kubernetes is crucial for maintaining strict access controls and minimizing the risk of unauthorized access and potential breaches. The `system:masters` group in Kubernetes provides full administrative access to the cluster, which can be highly dangerous if misused.

A recent real-world example is the incident involving the Cloudflare outage in 2020. While not directly related to Kubernetes, the incident highlighted the importance of strict access controls and the risks associated with granting excessive permissions. If human users had been granted full administrative access to the Kubernetes cluster, it could have led to unauthorized changes or breaches, similar to what happened in the Cloudflare incident.

By adhering to security best practices and avoiding the assignment of human users to the `system:masters` group, organizations can ensure that only automated pipelines and necessary processes have full administrative access to the cluster, reducing the risk of accidental or malicious changes.

---
<!-- nav -->
[[11-Kubernetes Access Management|Kubernetes Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]]
