---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to EKS Clusters and Infrastructure Management

In the context of modern DevOps practices, managing infrastructure efficiently and reliably is crucial. Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane. This allows teams to focus more on application development rather than the underlying infrastructure.

### Why Use EKS?

EKS provides several benefits:

1. **Managed Control Plane**: AWS manages the Kubernetes control plane, ensuring high availability and reliability.
2. **Integration with AWS Services**: Seamless integration with other AWS services such as VPC, IAM, and CloudWatch.
3. **Scalability**: Ability to scale worker nodes based on demand.
4. **Security**: Enhanced security features like IAM roles for service accounts and VPC isolation.

### Infrastructure Management with Terraform

Terraform is an open-source infrastructure as code (IaC) tool that allows you to define and provision infrastructure in a declarative manner. It supports a wide range of cloud providers, including AWS. Terraform uses a language called HCL (HashiCorp Configuration Language) to define infrastructure resources.

#### Why Use Terraform?

1. **Declarative Configuration**: Define your infrastructure in code, making it easier to manage and version control.
2. **Consistency**: Ensure consistency across environments by using the same configuration files.
3. **Automation**: Automate the provisioning and management of infrastructure resources.
4. **Multi-cloud Support**: Supports multiple cloud providers, allowing you to build hybrid infrastructures.

### Example: Creating EKS Clusters with Terraform

Let's walk through an example of creating 10 EKS clusters using Terraform. This will serve as the basis for our subsequent Python program to gather and display cluster information.

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "example" {
  count = 10

  name     = "cluster-${count.index}"
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = [aws_subnet.example.id]
  }

  depends_on = [aws_iam_role_policy_attachment.example]
}

resource "aws_iam_role" "example" {
  name = "example"

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

resource "aws_iam_role_policy_attachment" "example" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role_arn   = aws_iam_role.example.arn
}
```

### Explanation of the Terraform Code

1. **Provider Block**: Specifies the AWS provider and the region.
2. **Resource Block**: Defines the `aws_eks_cluster` resource with a `count` attribute to create 10 clusters.
3. **IAM Role**: Creates an IAM role for the EKS cluster.
4. **IAM Policy Attachment**: Attaches the necessary policy to the IAM role.

### Running the Terraform Code

To apply the Terraform configuration, run the following commands:

```sh
terraform init
terraform apply
```

This will create 10 EKS clusters in the specified region.

---
<!-- nav -->
[[03-Introduction to EKS Cluster Management Using Python and Terraform|Introduction to EKS Cluster Management Using Python and Terraform]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/01-EKS Cluster Overview Using Python And Terraform/00-Overview|Overview]] | [[05-Gathering Information About EKS Clusters Using Python|Gathering Information About EKS Clusters Using Python]]
