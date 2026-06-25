---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to EKS Clusters and Worker Nodes

In the context of modern cloud-native applications, Amazon Elastic Kubernetes Service (EKS) provides a managed Kubernetes environment that simplifies the deployment and management of containerized applications. One of the key components of an EKS cluster is the worker nodes, which are the compute resources that run the actual workloads.

### What Are Worker Nodes?

Worker nodes are the individual EC2 instances that form the compute layer of an EKS cluster. These nodes are responsible for running the pods, which are the smallest deployable units in Kubernetes. Each pod contains one or more containers and shares the same network namespace.

### Why Use Multiple Types of Worker Nodes?

Using multiple types of worker nodes allows you to optimize your cluster for different workloads. For example, you might want to have some nodes with high CPU and memory capacity for resource-intensive tasks, while others could be smaller and more cost-effective for less demanding jobs.

### How to Configure Worker Nodes Using Terraform

Terraform is an infrastructure as code (IaC) tool that allows you to define and provision your infrastructure using declarative configuration files. In the context of creating an EKS cluster, Terraform can be used to define the worker nodes and their configurations.

#### Example Configuration

Let's walk through an example configuration using Terraform to create an EKS cluster with multiple types of worker nodes.

```hcl
provider "aws" {
  region = "us-west-2"
}

module "eks_cluster" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name = "my-cluster"
  cluster_version = "1.21"

  vpc_id = "vpc-xxxxxxxx"
  subnet_ids = ["subnet-xxxxxxxx", "subnet-yyyyyyyy"]

  worker_groups = [
    {
      name            = "worker-group-1"
      instance_type   = "t2.small"
      desired_capacity = 2
    },
    {
      name            = "worker-group-2"
      instance_type   = "t2.medium"
      desired_capacity = 1
    }
  ]
}
```

### Explanation of the Configuration

- **Provider**: Specifies the AWS provider and the region where the resources will be created.
- **Module**: Uses the `terraform-aws-modules/eks/aws` module to create the EKS cluster.
- **Cluster Name**: The name of the EKS cluster.
- **Cluster Version**: The Kubernetes version to use for the cluster.
- **VPC ID**: The VPC where the cluster will be deployed.
- **Subnet IDs**: The subnets where the worker nodes will be placed.
- **Worker Groups**: Defines the worker groups with their respective instance types and desired capacities.

### Mermaid Diagram of the Architecture

```mermaid
graph TD
  A[Amazon EKS] -->|Deploys Pods| B[Worker Nodes]
  B -->|t2.small| C[Worker Group 1]
  B -->|t2.medium| D[Worker Group 2]
  C -->|EC2 Instance| E[Pods]
  D -->|EC2 Instance| F[Pods]
```

### Pricing Considerations

When creating an EKS cluster, you are charged for both the EKS control plane and the worker nodes. The EKS control plane costs approximately $0.10 per hour, while the worker nodes are billed based on the EC2 instance types and their usage.

### Real-World Examples

Consider a scenario where a company deploys a microservices architecture using EKS. They might have:

- **Worker Group 1**: t2.small instances for stateless services like API gateways.
- **Worker Group 2**: t2.medium instances for stateful services like databases.

This mixed approach ensures that the company can scale efficiently and manage costs effectively.

### Common Pitfalls and How to Avoid Them

#### Overprovisioning Resources

One common pitfall is overprovisioning resources, which can lead to unnecessary costs. To avoid this, regularly monitor the resource usage and adjust the worker node configurations accordingly.

#### Underprovisioning Resources

Underprovisioning can result in performance issues. Ensure that the worker nodes have sufficient resources to handle the workload.

### How to Prevent / Defend

#### Monitoring and Cost Management

Use AWS CloudWatch and AWS Cost Explorer to monitor the resource usage and costs. Set up alerts to notify you when the costs exceed a certain threshold.

#### Secure Configuration

Ensure that the worker nodes are configured securely. Use IAM roles and policies to restrict access to the necessary resources.

#### Example of Secure Configuration

```hcl
resource "aws_iam_role" "worker_node_role" {
  name = "worker-node-role"

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

resource "aws_iam_role_policy_attachment" "worker_node_policy" {
  role       = aws_iam_role.worker_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSCNIPolicy"
}
```

### Complete Example of HTTP Request and Response

When deploying the Terraform configuration, you would send an HTTP request to the AWS API to create the resources. Here is an example of the HTTP request and response:

```http
POST / HTTP/1.1
Host: ecs.us-west-2.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AmazonECS.CreateCluster
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-west-2/ecs/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=fe5f356c79821d4b1b1e84a5b40c9f6e215e9f8c9f9e2c7f6b7e9a2f4ca47e5b
X-Amz-Date: 20150101T000000Z

{
  "clusterName": "my-cluster",
  "tags": [
    {
      "key": "Environment",
      "value": "Production"
    }
  ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 102

{
  "cluster": {
    "clusterArn": "arn:aws:ecs:us-west-2:012345678910:cluster/my-cluster",
    "clusterName": "my-cluster",
    "status": "ACTIVE",
    "registeredContainerInstancesCount": 0,
    "runningTasksCount": 0,
    "pendingTasksCount": 0,
    "activeServicesCount": 0
  }
}
```

### Hands-On Labs

To practice creating EKS clusters using Terraform, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for learning about web security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security testing.

These labs provide a practical way to apply the concepts learned in this chapter.

### Conclusion

Creating an EKS cluster with multiple types of worker nodes using Terraform is a powerful way to manage your Kubernetes infrastructure. By understanding the configuration options and best practices, you can ensure that your cluster is optimized for performance and cost-effectiveness. Always monitor and secure your resources to prevent potential issues.

---
<!-- nav -->
[[04-Introduction to EKS Clusters and Terraform Modules|Introduction to EKS Clusters and Terraform Modules]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/10-Creating EKS Cluster Using Terraform Module/00-Overview|Overview]] | [[06-Introduction to Kubernetes Config Maps and Authentication|Introduction to Kubernetes Config Maps and Authentication]]
