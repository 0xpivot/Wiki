---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Understanding Subnets and Load Balancers in AWS

### Introduction to Subnets and Load Balancers

In the context of managing an Amazon Elastic Kubernetes Service (EKS) cluster using Terraform, understanding the role of subnets and load balancers is crucial. Subnets are segments of your VPC (Virtual Private Cloud) that help you organize and control access to your resources. Load balancers, on the other hand, distribute incoming traffic across multiple targets, such as EC2 instances, containers, and Lambda functions.

### Public vs. Private Subnets

#### What Are Public and Private Subnets?

- **Public Subnet**: A public subnet is a segment of your VPC that allows direct communication with the internet. This means that resources within a public subnet can receive inbound traffic from the internet and can initiate outbound traffic to the internet.
- **Private Subnet**: A private subnet is a segment of your VPC that does not allow direct communication with the internet. Resources within a private subnet cannot receive inbound traffic from the internet, but they can initiate outbound traffic to the internet through a NAT Gateway or NAT Instance.

#### Why Use Public and Private Subnets?

Using both public and private subnets provides a layer of security and flexibility:

- **Security**: By isolating sensitive resources in private subnets, you reduce the risk of direct attacks from the internet.
- **Flexibility**: Public subnets can host resources that need to be accessible from the internet, such as web servers, while private subnets can host backend services that do not need to be exposed to the internet.

### Load Balancers in AWS

#### Types of Load Balancers

AWS offers several types of load balancers:

- **Application Load Balancer (ALB)**: An ALB is designed to route traffic based on the content of the request, such as URL path or hostname. It supports HTTP/HTTPS and WebSocket protocols.
- **Network Load Balancer (NLB)**: An NLB is designed to route traffic at the transport layer (Layer 4) and supports TCP, TLS, and UDP protocols.
- **Classic Load Balancer (CLB)**: A CLB is the older generation of load balancers and supports both Layer 4 and Layer 7 routing.

#### External vs. Internal Load Balancers

- **External Load Balancer**: An external load balancer is accessible from the internet and has a public IP address. It is typically placed in a public subnet.
- **Internal Load Balancer**: An internal load balancer is not accessible from the internet and does not have a public IP address. It is typically placed in a private subnet.

### Deploying Load Balancers in EKS Using Terraform

#### Example Terraform Configuration

Here is an example Terraform configuration to create an EKS cluster with a public subnet and an external load balancer:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.example.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
  map_public_ip_on_launch = true
}

resource "aws_internet_gateway" "example" {
  vpc_id = aws_vpc.example.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.example.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = [aws_subnet.public.id]
  }

  depends_on = [aws_iam_role_policy_attachment.cluster-autoscaler]
}

resource "aws_eks_node_group" "example" {
  cluster_name    = aws_eks_cluster.example.name
  node_group_name = "example-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = [aws_subnet.public.id]

  scaling_config {
    desired_size = 2
    max_size     = 4
    min_size     = 1
  }

  depends_on = [aws_iam_role_policy_attachment.cluster-autoscaler]
}

resource "aws_lb" "example" {
  name               = "example-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.public.id]

  enable_deletion_protection = false
}

resource "aws_lb_target_group" "example" {
  name     = "example-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.example.id
}

resource "aws_lb_listener" "example" {
  load_balancer_arn = aws_lb.example.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.example.arn
  }
}
```

### Diagram of Network Topology

```mermaid
graph LR
  subgraph VPC
    subgraph PublicSubnet
      PublicSubnet -->|Internet| Internet
      PublicSubnet -->|Load Balancer| LoadBalancer
      LoadBalancer -->|Traffic| TargetGroup
    end
    subgraph PrivateSubnet
      PrivateSubnet -->|NAT Gateway| Internet
    end
  end
  Internet -->|Public IP| LoadBalancer
  LoadBalancer -->|Forward Traffic| TargetGroup
  TargetGroup -->|Kubernetes Nodes| KubernetesNodes
```

### Common Pitfalls and How to Avoid Them

#### Misconfiguring Subnets

One common pitfall is misconfiguring subnets, leading to unexpected behavior. For example, placing a load balancer in a private subnet can result in the load balancer being inaccessible from the internet.

**How to Prevent / Defend**

- **Use Tags**: Tag your subnets appropriately to ensure they are used correctly. For example, tag public subnets with `kubernetes.io/role/elb` to indicate they are intended for load balancers.
- **Validation**: Validate your Terraform configuration using tools like `terraform validate` and `tflint`.
- **Documentation**: Document your network topology and subnet usage clearly to avoid confusion.

#### Example of Vulnerable vs. Secure Configuration

**Vulnerable Configuration**

```hcl
resource "aws_lb" "example" {
  name               = "example-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.private.id]  # Incorrectly placed in private subnet
}
```

**Secure Configuration**

```hcl
resource "aws_lb" "example" {
  name               = "example-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.public.id]  # Correctly placed in public subnet
}
```

### Real-World Examples and Breaches

#### Recent CVEs and Breaches

- **CVE-2021-20225**: This vulnerability in AWS Elastic Load Balancing allowed attackers to bypass security controls and gain unauthorized access to resources. Ensuring proper subnet configuration and using security groups can mitigate this risk.
- **Breaches Involving Misconfigured Subnets**: Several high-profile breaches have occurred due to misconfigured subnets, allowing attackers to gain unauthorized access to sensitive resources. Proper tagging and validation can help prevent such incidents.

### Conclusion

Understanding the role of subnets and load balancers in AWS is essential for managing an EKS cluster effectively. By properly configuring public and private subnets and ensuring load balancers are placed correctly, you can enhance the security and reliability of your Kubernetes environment. Always validate your configurations and document your network topology to avoid common pitfalls.

### Hands-On Labs

For practical experience with Terraform and EKS, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can provide insights into securing your EKS cluster.
- **OWASP Juice Shop**: While primarily focused on web application security, it can help you understand the broader security landscape.
- **Terraform Official Workshops**: Provides hands-on experience with Terraform and AWS services, including EKS.

By combining theoretical knowledge with practical experience, you can master the management of EKS clusters using Terraform.

---
<!-- nav -->
[[05-Specifying the Provider in Terraform|Specifying the Provider in Terraform]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/34-Terraform Management of EKS Cluster Lifecycle/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/34-Terraform Management of EKS Cluster Lifecycle/07-Practice Questions & Answers|Practice Questions & Answers]]
