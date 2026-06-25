---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the steps involved in provisioning an EKS cluster using Terraform.**

The process of provisioning an EKS cluster using Terraform involves several steps:

1. **Define the Provider**: Specify the AWS provider with the required credentials and region.
2. **Create VPC Configuration**: Define the VPC, including private and public subnets across multiple availability zones (AZs).
3. **Provision EKS Cluster**: Use the `aws_eks_cluster` resource to create the EKS cluster, specifying the VPC and subnets.
4. **Install Add-Ons**: Enable default add-ons such as VPC CNI, kube-proxy, and coredns.
5. **Configure Node Group**: Set up a node group with the desired number of worker nodes, specifying the minimum and maximum sizes.
6. **Initialize Terraform**: Run `terraform init` to download the necessary providers and modules.
7. **Plan and Apply**: Execute `terraform plan` to review the changes, followed by `terraform apply` to create the cluster.

**Q2. How would you automate the provisioning and configuration of an EKS cluster using Terraform?**

To automate the provisioning and configuration of an EKS cluster using Terraform, follow these steps:

1. **Set Up Terraform Project**: Create a directory structure for your Terraform project, including `.tf` files for configuration and `.tfvars` for variable definitions.
2. **Define Variables**: Use `.tfvars` to store sensitive data like AWS access keys and other configuration parameters.
3. **Write Terraform Configuration**: Define resources such as VPC, EKS cluster, and node group in `.tf` files.
4. **Initialize Terraform**: Run `terraform init` to initialize the project and download necessary providers.
5. **Plan and Apply**: Use `terraform plan` to preview the changes and `terraform apply` to create the resources.
6. **Clean Up**: Use `terraform destroy` to clean up resources when no longer needed.

Here’s an example of a basic Terraform configuration:

```hcl
provider "aws" {
  region = var.region
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.example.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  vpc_config {
    subnet_ids = [aws_subnet.public.id]
  }
}

resource "aws_eks_node_group" "example" {
  cluster_name    = aws_eks_cluster.example.name
  node_group_name = "example-node-group"
  subnet_ids      = [aws_subnet.public.id]

  scaling_config {
    desired_size = 4
    max_size     = 20
    min_size     = 2
  }
}
```

**Q3. Why is it important to use the latest version of Kubernetes in an EKS cluster?**

Using the latest version of Kubernetes in an EKS cluster is crucial for several reasons:

1. **Security Patches**: Newer versions often include critical security patches that address vulnerabilities found in older versions. For example, the recent CVE-2023-2023 affected Kubernetes versions prior to 1.27, highlighting the importance of keeping up-to-date.
2. **Feature Enhancements**: Newer versions introduce new features and improvements that can enhance the functionality and performance of your cluster.
3. **Bug Fixes**: Newer versions typically include bug fixes that improve stability and reliability.
4. **Compatibility**: Using the latest version ensures compatibility with the latest tools and plugins, reducing the risk of encountering issues due to outdated dependencies.

**Q4. How would you configure proper access management for an EKS cluster?**

Proper access management for an EKS cluster involves several steps:

1. **IAM Roles and Policies**: Define IAM roles and policies that grant the necessary permissions to users and services. For example, you can create a role for the Kubernetes control plane and another for worker nodes.
2. **Service Accounts**: Use Kubernetes service accounts to manage permissions within the cluster. Assign roles and permissions to these service accounts.
3. **RBAC (Role-Based Access Control)**: Implement RBAC to control access to resources within the cluster. Define roles and role bindings to specify who can perform what actions.
4. **Security Token Service (STS)**: Use AWS STS to request temporary credentials with limited privileges. This helps in managing access securely without exposing long-term credentials.
5. **Audit Logs**: Enable audit logs to monitor and track access and activities within the cluster.

Example of creating an IAM role for EKS:

```hcl
resource "aws_iam_role" "eks_role" {
  name = "eks-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_role.name
}
```

**Q5. What are the best practices for managing costs associated with an EKS cluster?**

Managing costs associated with an EKS cluster involves several best practices:

1. **Auto-Scaling**: Configure auto-scaling for node groups to ensure that the cluster scales up and down based on demand, avoiding unnecessary costs.
2. **Cost Optimization**: Limit the maximum number of nodes in a node group to avoid excessive costs. For example, setting the maximum to 20 as shown in the lecture.
3. **Shut Down Clusters**: Ensure that the cluster is shut down or destroyed when not in use to avoid incurring costs.
4. **Use Spot Instances**: Consider using spot instances for worker nodes to reduce costs, although this requires careful management to handle interruptions.
5. **Monitor Usage**: Regularly monitor the usage and costs associated with the cluster using AWS Cost Explorer or similar tools.

By following these practices, you can effectively manage the costs of running an EKS cluster while ensuring that it meets your performance and scalability requirements.

---
<!-- nav -->
[[13-Introduction to Kubernetes Security|Introduction to Kubernetes Security]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Provision AWS EKS Cluster/00-Overview|Overview]]
