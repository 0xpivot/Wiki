---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Introduction to Kubernetes Security: Provisioning an AWS EKS Cluster

### Background Theory

Kubernetes (often abbreviated as K8s) is an open-source system for automating deployment, scaling, and management of containerized applications. One of the most popular ways to deploy Kubernetes is through Amazon Elastic Kubernetes Service (EKS), which is a managed service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane.

In this section, we will cover the process of provisioning an EKS cluster using Infrastructure as Code (IaC) tools such as Terraform. This approach ensures that your infrastructure is defined in code, making it easier to manage, version control, and reproduce.

### Setting Up the Environment

To begin, ensure that you have the following tools installed:

- **Visual Studio Code**: A powerful code editor that supports various extensions for IaC languages like Terraform.
- **Terraform**: A tool for building, changing, and combining infrastructure safely and efficiently.
- **AWS CLI**: The command-line interface for AWS, which allows you to interact with AWS services programmatically.

#### Opening the Project in Visual Studio Code

The first step is to open the project in Visual Studio Code. This project contains the Terraform configuration files that will be used to provision the EKS cluster.

```markdown
Open the project in Visual Studio Code.
```

### Base Configuration Overview

Let's take a look at the base configuration file that provisions the ECS cluster. This file contains the necessary definitions to set up the EKS cluster on AWS.

#### Provider Definition

The provider definition specifies the cloud provider and the credentials required to interact with it. In this case, we are using the AWS provider.

```hcl
provider "aws" {
  region     = var.region
  access_key = var.access_key
  secret_key = var.secret_key
}
```

Here, `var.region`, `var.access_key`, and `var.secret_key` are variables that should be defined in a separate `.tfvars` file or passed via environment variables.

#### Admin User Access Keys

We are using an admin user on AWS, and we need to configure the access keys of that user. This is crucial for granting the necessary permissions to perform operations on AWS resources.

```hcl
variable "access_key" {
  description = "AWS access key"
  type        = string
}

variable "secret_key" {
  description = "AWS secret key"
  type        = string
}
```

### Creating a VPC for the Cluster

An EKS cluster requires a specific configuration of a Virtual Private Cloud (VPC) where it gets deployed. The VPC is created with a specific CIDR block, and from that CIDR block, we define CIDR blocks for private and public subnets in different Availability Zones (AZs).

#### Fetching Availability Zones

The number of AZs varies depending on the region. Some regions have two AZs, some have three, and some have four. To handle this variability, we fetch the AZs from the AWS API based on the configured region.

```hcl
data "aws_availability_zones" "available" {
  state = "available"

  filter {
    name   = "region"
    values = [var.region]
  }
}
```

#### Defining Subnets

Once we have the list of AZs, we can define the subnets for the VPC. We create both private and public subnets in different AZs.

```hcl
resource "aws_vpc" "eks_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_subnet" "private_subnets" {
  count               = length(data.aws_availability_zones.available.names)
  vpc_id              = aws_vpc.eks_vpc.id
  cidr_block          = element(var.private_subnet_cidrs, count.index)
  availability_zone   = element(data.aws_availability_zones.available.names, count.index)
  map_public_ip_on_launch = false
}

resource "aws_subnet" "public_subnets" {
  count               = length(data.aws_availability_zones.available.names)
  vpc_id              = aws_vpc.eks_vpc.id
  cidr_block          = element(var.public_subnet_cidrs, count.index)
  availability_zone   = element(data.aws_availability_zones.available.names, count.index)
  map_public_ip_on_launch = true
}
```

### Enabling a NAT Gateway

A NAT Gateway is a managed service that enables instances in the private subnets to connect to services outside the VPC. This is essential for allowing private subnets to communicate with the internet for tasks such as downloading dependencies or accessing external APIs.

```hcl
resource "aws_nat_gateway" "nat_gateway" {
  count             = length(data.aws_availability_zones.available.names)
  allocation_id     = element(aws_eip.nat_gateway[count.index].id, count.index)
  subnet_id         = element(aws_subnet.public_subnets[count.index].id, count.index)
  depends_on        = [aws_internet_gateway.igw]

  tags = {
    Name = "nat-gateway-${count.index}"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

resource "aws_route_table_association" "public_subnet_association" {
  count          = length(data.aws_availability_zones.available.names)
  subnet_id      = element(aws_subnet.public_subnets[count.index].id, count.index)
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = element(aws_nat_gateway.nat_gateway[count.index].id, count.index)
  }

  tags = {
    Name = "private-route-table"
  }
}

resource "aws_route_table_association" "private_subnet_association" {
  count          = length(data.aws_availability_zones.available.names)
  subnet_id      = element([for i in range(length(data.aws_availability_zones.available.names)) : aws_subnet.private_subnets[i].id], count.index)
  route_table_id = aws_route_table.private_route_table.id
}
```

### Diagramming the Architecture

To better understand the architecture, let's visualize it using a Mermaid diagram.

```mermaid
graph LR
  subgraph VPC
    subgraph PublicSubnet1
      PublicSubnet1
    end
    subgraph PublicSubnet2
      PublicSubnet2
    end
    subgraph PrivateSubnet1
      PrivateSubnet1
    end
    subgraph PrivateSubnet2
      PrivateSubnet2
    end
  end
  InternetGateway --> PublicSubnet1
  InternetGateway --> PublicSubnet2
  NatGateway1 --> PrivateSubnet1
  NatGateway2 --> PrivateSubnet2
  PublicSubnet1 --> InternetGateway
  PublicSubnet2 --> InternetGateway
  PrivateSubnet1 --> NatGateway1
  PrivateSubnet2 --> NatGateway2
```

### Common Pitfalls and How to Prevent Them

#### Misconfiguration of Subnets

One common pitfall is misconfiguring the subnets, leading to issues with connectivity. Ensure that the CIDR blocks are correctly defined and that the subnets are properly associated with the route tables.

**Secure Configuration Example:**

```hcl
resource "aws_subnet" "private_subnets" {
  count               = length(data.aws_availability_zones.available.names)
  vpc_id              = aws_vpc.eks_vpc.id
  cidr_block          = element(var.private_subnet_cidrs, count.index)
  availability_zone   = element(data.aws_availability_zones.available.names, count.index)
  map_public_ip_on_launch = false
}

resource "aws_subnet" "public_subnets" {
  count               = length(data.aws_availability_zones.available.names)
  vpc_id              = aws_vpc.eks_vpc.id
  cidr_block          = element(var.public_subnet_cidrs, count.index)
  availability_zone   = element(data.aws_availability_zones.available.names, count.index)
  map_public_ip_on_launch = true
}
```

#### Incorrect Route Table Associations

Another common issue is incorrect route table associations, which can lead to routing problems. Ensure that the route tables are correctly associated with the subnets.

**Secure Configuration Example:**

```hcl
resource "aws_route_table_association" "public_subnet_association" {
  count          = length(data.aws_availability_zones.available.names)
  subnet_id      = element(aws_subnet.public_subnets[count.index].id, count.index)
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "private_subnet_association" {
  count          = length(data.aws_availability_zones.available.names)
  subnet_id      = element([for i in range(length(data.aws_availability_zones.available.names)) : aws_subnet.private_subnets[i].id], count.index)
  route_table_id = aws_route_table.private_route_table.id
}
```

### Real-World Examples and Breaches

#### Recent CVEs and Breaches

One notable breach involving misconfigured subnets and route tables was the Capital One data breach in 2019. The attacker exploited a misconfigured firewall rule, which allowed unauthorized access to sensitive data. This highlights the importance of proper configuration and validation of network settings.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about Kubernetes security.
- **kube-hunter**: A tool for hunting vulnerabilities in Kubernetes clusters.

These labs provide practical experience in setting up and securing Kubernetes clusters on AWS.

### Conclusion

Provisioning an EKS cluster involves careful configuration of the VPC, subnets, and route tables. By following best practices and validating configurations, you can ensure a secure and reliable Kubernetes cluster on AWS.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Provision AWS EKS Cluster/01-Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Using Terraform|Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Using Terraform]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Provision AWS EKS Cluster/00-Overview|Overview]] | [[03-Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 2|Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 2]]
