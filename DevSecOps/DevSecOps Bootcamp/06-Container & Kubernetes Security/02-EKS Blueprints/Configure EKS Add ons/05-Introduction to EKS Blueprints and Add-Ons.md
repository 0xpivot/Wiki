---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Introduction to EKS Blueprints and Add-Ons

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing expertise in Kubernetes orchestration. EKS Blueprints provide pre-configured templates for deploying common Kubernetes applications and services. These blueprints include add-ons, which are additional services that enhance the functionality of your EKS cluster.

### What Are EKS Add-Ons?

EKS add-ons are pre-built, pre-configured services that extend the capabilities of an EKS cluster. They can include tools for monitoring, logging, security, and more. By using add-ons, you can quickly deploy and manage these services without having to manually configure them.

#### Why Use EKS Add-Ons?

Using EKS add-ons offers several benefits:

1. **Ease of Deployment**: Add-ons are pre-configured and can be deployed with minimal setup.
2. **Consistency**: Ensures that the same configurations are used across different environments.
3. **Maintenance**: Managed by AWS, ensuring updates and patches are applied automatically.
4. **Integration**: Seamlessly integrates with other AWS services.

### Configuring EKS Add-Ons Using Terraform

Terraform is an infrastructure as code (IaC) tool that allows you to define and provision infrastructure resources using declarative configuration files. In this section, we will explore how to configure EKS add-ons using Terraform modules.

#### Setting Up the Terraform Module

To configure EKS add-ons, you can use a Terraform module. Here’s an example of how to set up the module:

```hcl
module "eks_addons" {
  source = "terraform-aws-modules/eks/aws"
  version = "18.17.0"

  cluster_name = var.cluster_name
  vpc_id       = var.vpc_id
  subnets      = var.subnets
  oidc_issuer  = var.oidc_issuer

  addons = {
    "vpc-cni" = {
      enabled = true
    }
    "coredns" = {
      enabled = true
    }
    "kube-proxy" = {
      enabled = true
    }
  }
}
```

In this example, we are using the `terraform-aws-modules/eks` module to configure EKS add-ons. The `cluster_name`, `vpc_id`, `subnets`, and `oidc_issuer` variables are passed to the module to ensure that the add-ons are correctly configured for the specified EKS cluster.

### Understanding the EKS Cluster Configuration

Before configuring the add-ons, it’s important to understand the basic configuration of the EKS cluster. Here’s an example of how to create an EKS cluster using Terraform:

```hcl
resource "aws_eks_cluster" "example" {
  name     = var.cluster_name
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = var.subnets
  }

  enabled_cluster_log_types = ["api", "audit"]
}

resource "aws_iam_role" "example" {
  name = "${var.cluster_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}
```

This configuration creates an EKS cluster with the specified name, role ARN, and VPC configuration. The `enabled_cluster_log_types` attribute enables API and audit logs for the cluster.

### Referencing the EKS Cluster in Add-Ons

When configuring add-ons, you need to reference the EKS cluster to ensure that the add-ons are installed in the correct cluster. Here’s how the add-ons module references the EKS cluster:

```hcl
module "eks_addons" {
  source = "terraform-aws-modules/eks/aws"
  version = "18.17.0"

  cluster_name = aws_eks_cluster.example.name
  vpc_id       = aws_eks_cluster.example.vpc_config[0].subnet_ids[0]
  subnets      = aws_eks_cluster.example.vpc_config[0].subnet_ids
  oidc_issuer  = aws_eks_cluster.example.identity[0].oidc[0].issuer

  addons = {
    "vpc-cni" = {
      enabled = true
    }
    "coredns" = {
      enabled = true
    }
    "kube-proxy" = {
      enabled = true
    }
  }
}
```

In this example, the `cluster_name`, `vpc_id`, `subnets`, and `oidc_issuer` are directly referenced from the `aws_eks_cluster.example` resource. This ensures that the add-ons are correctly configured for the specified EKS cluster.

### Understanding OIDC Provider

The OIDC (OpenID Connect) provider is a crucial component of an EKS cluster. It provides a way to authenticate and authorize services within the cluster using AWS Identity and Access Management (IAM).

#### What is OIDC Provider?

An OIDC provider is a service that issues tokens to clients, allowing them to authenticate and authorize access to resources. In the context of EKS, the OIDC provider is used to enable IAM roles for service accounts (IRSA). This allows Kubernetes service accounts to assume IAM roles, providing fine-grained access control to AWS resources.

#### How OIDC Provider Works

When an EKS cluster is created, an OIDC provider is automatically attached to it. This provider is used to issue tokens to Kubernetes service accounts. Here’s how it works:

1. **Token Issuance**: The OIDC provider issues tokens to Kubernetes service accounts.
2. **Token Verification**: The tokens are verified by AWS services to ensure that the service account has the necessary permissions.
3. **Access Control**: IAM roles are associated with the service accounts, providing access to AWS resources.

#### Example of OIDC Provider Configuration

Here’s an example of how to configure the OIDC provider for an EKS cluster:

```hcl
resource "aws_eks_cluster" "example" {
  name     = var.cluster_name
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = var.subnets
  }

  enabled_cluster_log_types = ["api", "audit"]

  identity {
    oidc {
      issuer = "https://oidc.eks.${data.aws_region.current.name}.amazonaws.com/id/${aws_eks_cluster.example.id}"
    }
  }
}
```

In this example, the `identity` block configures the OIDC provider for the EKS cluster. The `issuer` attribute specifies the URL of the OIDC provider.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Incorrect Configuration**: Ensure that the add-ons are correctly configured for the specified EKS cluster.
2. **Missing Dependencies**: Make sure that all dependencies, such as IAM roles and VPC configurations, are correctly set up.
3. **Security Risks**: Be cautious when granting permissions to service accounts. Ensure that the least privilege principle is followed.

#### Best Practices

1. **Use Modules**: Use Terraform modules to simplify the configuration and ensure consistency.
2. **Automate Updates**: Use automated processes to update the add-ons and ensure that they are always up-to-date.
3. **Monitor Logs**: Enable and monitor logs to detect any issues or unauthorized access attempts.

### Real-World Examples and Recent CVEs

#### Real-World Example: Misconfigured OIDC Provider

A recent breach involved a misconfigured OIDC provider that allowed unauthorized access to AWS resources. The attacker was able to exploit a misconfigured service account that had excessive permissions.

**Example Configuration**:

```hcl
resource "aws_iam_role" "example" {
  name = "${var.cluster_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "example-policy"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = "*"
          Effect = "Allow"
          Resource = "*"
        },
      ]
    })
  }
}
```

In this example, the `inline_policy` block grants excessive permissions to the service account, allowing unauthorized access to AWS resources.

**How to Prevent / Defend**:

1. **Least Privilege Principle**: Ensure that service accounts have the minimum necessary permissions.
2. **Regular Audits**: Regularly audit IAM roles and policies to detect and correct misconfigurations.
3. **Monitoring**: Enable and monitor logs to detect any unauthorized access attempts.

### Complete Example: Full Configuration and Results

#### Full Configuration

Here’s a complete example of how to configure an EKS cluster and add-ons using Terraform:

```hcl
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "subnets" {
  description = "List of subnet IDs"
  type        = list(string)
}

provider "aws" {
  region = data.aws_region.current.name
}

data "aws_region" "current" {}

resource "aws_iam_role" "example" {
  name = "${var.cluster_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "example-policy"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = "ec2:*"
          Effect = "Allow"
          Resource = "*"
        },
      ]
    })
  }
}

resource "aws_eks_cluster" "example" {
  name     = var.cluster_name
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = var.subnets
  }

  enabled_cluster_log_types = ["api", "audit"]

  identity {
    oidc {
      issuer = "https://oidc.eks.${data.aws_region.current.name}.amazonaws.com/id/${aws_eks_cluster.example.id}"
    }
  }
}

module "eks_addons" {
  source = "terraform-aws-modules/eks/aws"
  version = "18.17.0"

  cluster_name = aws_eks_cluster.example.name
  vpc_id       = aws_eks_cluster.example.vpc_config[0].subnet_ids[0]
  subnets      = aws_eks_cluster.example.vpc_config[0].subnet
```

---
<!-- nav -->
[[04-Introduction to EKS Blueprints and Add-Ons Part 4|Introduction to EKS Blueprints and Add-Ons Part 4]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Configure EKS Add ons/00-Overview|Overview]] | [[06-Introduction to EKS Blueprints and Add-ons Configuration Part 1|Introduction to EKS Blueprints and Add-ons Configuration Part 1]]
