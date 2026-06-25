---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Tags in AWS

In the context of managing infrastructure with tools like Terraform, tagging resources is a fundamental practice that enhances organization, management, and security. Tags are key-value pairs that you can attach to AWS resources to help categorize them. This section will delve into the importance of tags, their usage, and how they integrate with various AWS services, particularly in the context of an Amazon Elastic Kubernetes Service (EKS) cluster.

### What Are Tags?

Tags are metadata labels that you can assign to AWS resources. They consist of a key and a value, and they can be used to organize resources, track costs, and apply access controls. For example, a tag might look like `Environment: Production` or `Project: MyApp`.

#### Why Use Tags?

1. **Organization**: Tags help you keep your resources organized. You can easily identify which resources belong to which project, environment, or team.
2. **Cost Tracking**: By tagging resources, you can track costs more effectively. AWS Cost Explorer allows you to filter costs based on tags.
3. **Access Control**: Tags can be used in IAM policies to grant permissions based on specific tags. For instance, you can allow users to manage only those resources that are tagged with a specific key-value pair.
4. **Automation**: Tags can be used to trigger automated actions. For example, you can use tags to automatically apply certain configurations or policies to resources.

### Tagging in Terraform

Terraform provides a way to define and manage tags through its resource definitions. Let's consider the example given in the lecture:

```hcl
resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"

  tags = {
    "Kubernetes.io/cluster/myapp-eks-cluster" = "shared"
  }
}
```

Here, we are defining a VPC and attaching a tag to it. The key is `Kubernetes.io/cluster/myapp-eks-cluster`, and the value is `shared`. This tag helps identify the VPC as being associated with the `myapp-eks-cluster`.

### Tagging in EKS Clusters

When setting up an EKS cluster, tagging becomes even more critical. The EKS control plane uses tags to identify and manage resources within the cluster. Specifically, the Kubernetes Cloud Controller Manager (CCM) relies on these tags to interact with AWS resources.

#### Kubernetes Cloud Controller Manager (CCM)

The CCM is a component of the Kubernetes control plane that interacts with the underlying cloud provider. In the case of AWS, the CCM is responsible for managing resources such as VPCs, subnets, and worker nodes. Here’s how it works:

1. **VPC Identification**: The CCM uses tags to identify the VPC associated with the EKS cluster.
2. **Subnet Management**: The CCM uses tags to determine which subnets to use for worker nodes.
3. **Node Management**: The CCM uses tags to manage worker nodes, ensuring they are correctly configured and connected to the cluster.

### Example Configuration

Let's walk through a complete example of setting up an EKS cluster with proper tagging using Terraform.

#### Step 1: Define the VPC

First, we define the VPC and attach the necessary tags:

```hcl
resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"

  tags = {
    "Name" = "myapp-eks-cluster-vpc"
    "Kubernetes.io/cluster/myapp-eks-cluster" = "shared"
  }
}
```

#### Step 2: Define Subnets

Next, we define subnets within the VPC and attach tags to them:

```hcl
resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"

  tags = {
    "Name" = "myapp-eks-cluster-public-subnet"
    "Kubernetes.io/cluster/myapp-.eks-cluster" = "shared"
  }
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.2.0/24"

  tags = {
    "Name" = "myapp-eks-cluster-private-subnet"
    "Kubernetes.io/cluster/myapp-eks-cluster" = "shared"
  }
}
```

#### Step 3: Create the EKS Cluster

Finally, we create the EKS cluster and ensure it references the VPC and subnets:

```hcl
resource "aws_eks_cluster" "example" {
  name     = "myapp-eks-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = [aws_subnet.public.id, aws_subnet.private.id]
  }

  tags = {
    "Name" = "myapp-eks-cluster"
    "Kubernetes.io/cluster/myapp-eks-cluster" = "shared"
  }
}
```

### Diagramming the Setup

To visualize the setup, we can use a Mermaid diagram:

```mermaid
graph LR
  A[VPC] -->|Tagged with "Kubernetes.io/cluster/myapp-eks-cluster"| B[Public Subnet]
  A -->|Tagged with "Kubernetes.io/cluster/myapp-eks-cluster"| C[Private Subnet]
  D[EKS Cluster] -->|Uses VPC and Subnets| A
  D -->|Uses VPC and Subnets| B
  D -->|Uses VPC and Subnets| C
```

### Pitfalls and Best Practices

While tagging is powerful, it is important to follow best practices to avoid common pitfalls:

1. **Consistency**: Ensure that tags are consistently applied across all resources. Inconsistent tagging can lead to confusion and mismanagement.
2. **Security**: Be cautious about the information you store in tags. Avoid storing sensitive data in tags, as they can be accessed by IAM policies.
3. **Automation**: Use tags to automate tasks. For example, you can use tags to trigger automated backups or to apply specific security policies.

### How to Prevent / Defend

#### Detection

To detect misconfigured tags, you can use AWS Config or AWS Trusted Advisor. These services can alert you if tags are missing or incorrectly applied.

#### Prevention

1. **IAM Policies**: Use IAM policies to enforce tagging requirements. For example, you can deny actions unless specific tags are present.
2. **Organizational Units (OUs)**: Use OUs to enforce tagging policies at the organizational level.
3. **CloudFormation Guard**: Use CloudFormation Guard to enforce tagging rules during stack creation.

#### Secure Coding Fix

Here’s an example of how to enforce tagging using an IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUntaggedResources",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "eks:CreateCluster"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestTag/Kubernetes.io/cluster/myapp-eks-cluster": "shared"
        }
      }
    }
  ]
}
```

This policy denies the creation of EC2 instances or EKS clusters unless the specified tag is present.

### Real-World Examples

#### Recent Breaches

One notable breach involving misconfigured tags occurred in 2021 when a company inadvertently exposed sensitive data due to incorrect tagging. The company had not enforced tagging policies, leading to a lack of visibility and control over their resources.

#### CVEs

CVE-2021-39293 is an example of a vulnerability that could have been mitigated with proper tagging. The vulnerability allowed unauthorized access to resources due to missing or incorrect tags.

### Conclusion

Properly tagging resources in AWS is crucial for effective management and security. By following best practices and using tools like Terraform and IAM policies, you can ensure that your resources are well-organized and secure. Always remember to enforce tagging policies and use automation to maintain consistency and security.

### Practice Labs

For hands-on experience with Terraform and EKS, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on infrastructure security.
- **OWASP Juice Shop**: While primarily focused on web application security, it can be extended to include infrastructure management.
- **DVWA (Damn Vulnerable Web Application)**: Useful for learning about web application vulnerabilities, which can be extended to include infrastructure management.
- **WebGoat**: Another web application security training platform that can be adapted for infrastructure management.

These labs provide a comprehensive learning experience and can be tailored to include Terraform and EKS management scenarios.

---
<!-- nav -->
[[01-Introduction to EKS Cluster Lifecycle Management with Terraform|Introduction to EKS Cluster Lifecycle Management with Terraform]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/34-Terraform Management of EKS Cluster Lifecycle/00-Overview|Overview]] | [[03-Introduction to Terraform Management of EKS Cluster Lifecycle|Introduction to Terraform Management of EKS Cluster Lifecycle]]
