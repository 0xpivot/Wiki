---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Infrastructure as Code (IaC) and Terraform

### Introduction to Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is a practice where infrastructure is defined using code rather than physical hardware configurations. This approach allows for automation, consistency, and version control of infrastructure configurations. One of the most popular tools for IaC is Terraform, developed by HashiCorp. Terraform allows you to define your infrastructure in a declarative language called HCL (HashiCorp Configuration Language).

#### Why Use IaC?

1. **Consistency**: By defining infrastructure in code, you ensure that the same configuration is applied consistently across different environments (development, testing, production).
2. **Automation**: IaC enables automated deployment and management of infrastructure, reducing human error and increasing efficiency.
3. **Version Control**: Infrastructure definitions can be stored in version control systems like Git, allowing you to track changes and revert to previous states if needed.
4. **Reproducibility**: With IaC, you can easily recreate your entire infrastructure from scratch, ensuring that you don't miss any critical configurations.

### Terraform Basics

Terraform uses a declarative language to describe the desired state of your infrastructure. This means you specify what you want, and Terraform figures out how to achieve it. Here’s a basic example of a Terraform configuration:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

In this example:
- `provider "aws"` specifies the AWS provider and the region.
- `resource "aws_instance" "example"` defines an EC2 instance resource.
- `ami` and `instance_type` specify the AMI and instance type.
- `tags` adds metadata to the instance.

### Creating and Managing EKS Clusters with Terraform

EKS (Elastic Kubernetes Service) is a managed Kubernetes service provided by AWS. To create and manage an EKS cluster using Terraform, you would typically define resources such as the EKS cluster, worker nodes, and IAM roles.

Here’s an example of a Terraform configuration for setting up an EKS cluster:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = [aws_subnet.example.id]
  }
}

resource "aws_iam_role" "example" {
  name = "example-role"

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

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}
```

This configuration sets up an EKS cluster with an associated IAM role and VPC/subnet.

### Recreating and Replicating Infrastructure

One of the key benefits of IaC is the ability to recreate or replicate infrastructure easily. If you have a working Terraform configuration, you can apply it to create the same infrastructure again and again.

For example, if you have a Terraform configuration that sets up an EKS cluster, you can run:

```bash
terraform init
terraform apply
```

This will initialize Terraform and apply the configuration, creating the specified resources.

### Verifying and Cleaning Up Resources

After you’ve created your infrastructure, you might want to verify that all resources have been properly set up. You can also clean up resources when they are no longer needed.

#### Listing Resources in Terraform State

To list all resources currently tracked by Terraform, you can use the `terraform state list` command:

```bash
terraform state list
```

This command outputs a list of all resources in the Terraform state. If the state is empty, it indicates that no resources are being tracked.

#### Cleaning Up Resources

To destroy all resources created by Terraform, you can run:

```bash
terraform destroy
```

This command will prompt you to confirm the destruction of resources. Once confirmed, Terraform will remove all resources defined in the configuration.

### Ensuring an Empty State

After destroying resources, you can check if the state is empty by running:

```bash
terraform state list
```

If the output is empty, it confirms that no resources are being tracked by Terraform.

### Real-World Example: CVE-2021-20225

A real-world example of the importance of IaC is the CVE-2021-20225, which affected AWS EKS clusters. This vulnerability allowed unauthorized access to sensitive data due to misconfigured IAM roles.

#### Vulnerable Configuration

Consider a scenario where an IAM role is misconfigured, allowing unauthorized access:

```hcl
resource "aws_iam_role" "example" {
  name = "example-role"

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
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
      },
    ]
  })
}
```

In this configuration, the `Principal` field allows any AWS account to assume the role, which is a significant security risk.

#### Secure Configuration

To secure the configuration, you should restrict the `Principal` to only trusted services:

```hcl
resource "aws_iam_role" "example" {
  name = "example-role"

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

By restricting the `Principal`, you ensure that only the EKS service can assume the role, preventing unauthorized access.

### How to Prevent / Defend

#### Detection

To detect misconfigured IAM roles, you can use tools like AWS Config or third-party security scanners like Aqua Security or Twistlock.

#### Prevention

1. **Use Least Privilege Principle**: Ensure that IAM roles have the minimum permissions required to perform their tasks.
2. **Regular Audits**: Regularly audit IAM roles and policies to identify and correct misconfigurations.
3. **Automated Scanning**: Use automated scanning tools to detect and alert on potential security issues.

#### Secure Coding Fixes

Compare the vulnerable and secure configurations side by side:

**Vulnerable Configuration:**

```hcl
resource "aws_iam_role" "example" {
  name = "example-role"

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
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
      },
    ]
  })
}
```

**Secure Configuration:**

```hcl
resource "aws_iam_role" "example" {
  name = "example-role"

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

### Hands-On Practice

For hands-on practice with EKS cluster setup and resource verification, consider the following labs:

- **PortSwigger Web Security Academy**: While primarily focused on web application security, this platform offers exercises that can help you understand the broader context of securing applications deployed on EKS.
- **AWS Official Workshops**: AWS provides several workshops and labs that cover EKS setup and management, including the Well-Architected Labs.
- **Pacu**: A penetration testing framework that includes modules for testing and exploiting misconfigurations in AWS services, including EKS.

These labs provide practical experience in setting up and managing EKS clusters securely.

### Conclusion

Using Infrastructure as Code (IaC) with Terraform simplifies the process of creating, managing, and verifying infrastructure. By ensuring consistent and reproducible configurations, you can avoid common pitfalls and secure your infrastructure effectively. Regular audits and the use of automated tools can further enhance the security of your EKS clusters.

---
<!-- nav -->
[[02-EKS Cluster Setup and Resource Verification|EKS Cluster Setup and Resource Verification]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/19-EKS Cluster Setup and Resource Verification/00-Overview|Overview]] | [[04-Understanding Network Connectivity in EKS Clusters|Understanding Network Connectivity in EKS Clusters]]
