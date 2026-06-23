---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Introduction to Kubernetes Security: Provisioning an AWS EKS Cluster

### Background Theory

Kubernetes (often abbreviated as K8s) is an open-source system for automating deployment, scaling, and management of containerized applications. It was originally designed by Google and is now maintained by the Cloud Native Computing Foundation. Kubernetes provides a platform for automating deployment and management of containerized applications at scale. One of the key benefits of Kubernetes is its ability to run across different environments, including on-premises data centers, public clouds, and hybrid environments.

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to stand up or maintain your own Kubernetes control plane. EKS supports the Kubernetes API, so you can use existing tools to interact with the Kubernetes control plane. This allows you to focus on deploying and managing your applications rather than managing the underlying infrastructure.

### Setting Up an EKS Cluster with Terraform

Terraform is an open-source infrastructure as code (IaC) tool that enables you to define and provision your infrastructure using declarative configuration files. These configuration files are written in HashiCorp Configuration Language (HCL) and can be used to manage resources across multiple cloud providers, including AWS.

#### Step-by-Step Guide to Provisioning an EKS Cluster

1. **Install Terraform**: Ensure you have Terraform installed on your local machine. You can download it from the official website: <https://www.terraform.io/downloads.html>.

2. **Set Up AWS CLI**: Make sure you have the AWS Command Line Interface (CLI) configured with your AWS credentials. This can be done by running `aws configure` and providing your access key and secret key.

3. **Create a Terraform Project Directory**:
    ```bash
    mkdir eks-cluster
    cd eks-cluster
    ```

4. **Initialize Terraform**:
    ```bash
    terraform init
    ```

5. **Define the EKS Cluster Configuration**:
    Create a file named `main.tf` and add the following configuration:

    ```hcl
    provider "aws" {
      region = "us-west-2"
    }

    resource "aws_eks_cluster" "example" {
      name     = "example-cluster"
      role_arn = aws_iam_role.example.arn
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

    resource "aws_iam_role_policy_attachment" "example" {
      policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
      role_arn   = aws_iam_role.example.arn
    }

    resource "aws_eks_node_group" "example" {
      cluster_name    = aws_eks_cluster.example.name
      node_group_name = "example-node-group"
      node_role_arn   = aws_iam_instance_profile.example.arn
      subnet_ids      = [aws_subnet.example.id]
      scaling_config {
        desired_size = 2
        max_size     = 2
        min_size     = 2
      }
    }

    resource "aws_iam_instance_profile" "example" {
      name = "example-instance-profile"
      roles = [aws_iam_role.example.name]
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
              Service = "ec2.amazonaws.com"
            }
          },
        ]
      })
    }

    resource "aws_iam_role_policy_attachment" "example" {
      policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
      role_arn   = aws_iam_role.example.arn
    }

    resource "aws_vpc" "example" {
      cidr_block = "10.0.0.0/16"
    }

    resource "aws_subnet" "example" {
      vpc_id     = aws_vpc.example.id
      cidr_block = "10.0.1.0/24"
    }
    ```

6. **Plan the Infrastructure**:
    ```bash
    terraform plan
    ```

7. **Apply the Configuration**:
    ```bash
    terraform apply
    ```

### Explanation of Key Components

- **Provider Block**: Specifies the AWS provider and the region where the resources will be created.
- **IAM Role and Policy Attachments**: Define the necessary IAM roles and policies required for the EKS cluster and worker nodes.
- **EKS Cluster Resource**: Creates the EKS cluster with the specified name and role ARN.
- **EKS Node Group Resource**: Configures the node group for the EKS cluster, specifying the number of nodes and their roles.
- **VPC and Subnet Resources**: Define the VPC and subnet where the EKS cluster will be deployed.

### Security Best Practices

When setting up an EKS cluster, it is crucial to follow security best practices to ensure the confidentiality, integrity, and availability of your applications. Here are some key security considerations:

1. **Network Segmentation**: Use VPCs and subnets to segment your network and limit the exposure of your EKS cluster.
2. **IAM Roles and Policies**: Ensure that IAM roles and policies are properly configured to restrict access to the minimum necessary permissions.
3. **Encryption**: Enable encryption for EBS volumes and EFS filesystems to protect sensitive data.
4. **Security Groups**: Configure security groups to control inbound and outbound traffic to the EKS cluster.
5. **Pod Security Policies**: Implement pod security policies to enforce security controls at the pod level.

### Real-World Examples

One notable breach involving Kubernetes was the incident reported in 2020 where a misconfigured Kubernetes dashboard allowed unauthorized access to sensitive data. This highlights the importance of proper configuration and access control.

### How to Prevent / Defend

#### Vulnerable Configuration Example

```hcl
resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn
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
```

#### Secure Configuration Example

```hcl
resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn
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

resource "aws_iam_role_policy_attachment" "example" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role_arn   = aws_iam_role.example.arn
}
```

### Detection and Prevention

To detect and prevent unauthorized access, you can implement the following measures:

1. **Logging and Monitoring**: Enable CloudTrail and VPC Flow Logs to monitor and log all API calls and network traffic.
2. **Security Groups**: Use security groups to restrict inbound and outbound traffic to the EKS cluster.
3. **IAM Policies**: Regularly review and audit IAM policies to ensure they are properly configured and restricted to the minimum necessary permissions.
4. **Pod Security Policies**: Implement pod security policies to enforce security controls at the pod level.

### Hands-On Labs

For hands-on practice with EKS security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A set of Kubernetes security challenges designed to test and improve your Kubernetes security skills.

By following these steps and best practices, you can ensure that your EKS cluster is securely configured and protected against potential threats.

### Conclusion

Provisioning an EKS cluster with Terraform is a powerful way to automate the deployment and management of your Kubernetes infrastructure. By following security best practices and regularly auditing your configurations, you can ensure the security and reliability of your applications running on EKS.

---
<!-- nav -->
[[07-Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 6|Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 6]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Provision AWS EKS Cluster/00-Overview|Overview]] | [[09-Introduction to Kubernetes Security and Provisioning an AWS EKS Cluster|Introduction to Kubernetes Security and Provisioning an AWS EKS Cluster]]
