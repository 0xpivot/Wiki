---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS Resource Creation Using Terraform

In the realm of DevOps, infrastructure as code (IAC) is a critical practice that enables developers and operations teams to manage and provision infrastructure through code. One of the most popular tools for IAC is Terraform, developed by HashiCorp. This chapter will delve into creating AWS resources using the Terraform provider, focusing specifically on creating a Virtual Private Cloud (VPC) and a subnet within that VPC.

### What is a VPC?

A Virtual Private Cloud (VPC) is a logically isolated section of the AWS cloud where you can launch AWS resources in a virtual network that you define. A VPC allows you to have complete control over your network environment, including IP address ranges, subnets, routing tables, and gateways.

#### Why Use a VPC?

Using a VPC provides several benefits:

1. **Security**: You can isolate your resources from the public internet and other AWS accounts.
2. **Control**: You have full control over the network configuration, including IP addressing, routing, and security policies.
3. **Scalability**: You can easily scale your resources within the VPC as needed.

### What is a Subnet?

A subnet is a segment of an IP network. In the context of AWS, a subnet is a range of IP addresses within a VPC. Each subnet is associated with a specific Availability Zone (AZ), which is a distinct location within a region that has its own power, cooling, and networking infrastructure.

#### Why Use Subnets?

Subnets allow you to:

1. **Isolate Resources**: You can place different types of resources in different subnets for better isolation and security.
2. **Optimize Performance**: By placing resources in specific AZs, you can optimize performance and reduce latency.
3. **Manage Traffic**: You can control traffic flow between subnets using route tables and network ACLs.

### Creating a VPC and Subnet Using Terraform

To create a VPC and a subnet using Terraform, you need to define the necessary resources in a Terraform configuration file. Let's walk through the process step-by-step.

#### Step 1: Define the VPC

First, you need to define the VPC resource. Here is an example of how to do this:

```hcl
resource "aws_vpc" "example_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "example-vpc"
  }
}
```

In this configuration:

- `cidr_block` specifies the range of IP addresses for the VPC.
- `tags` allows you to add metadata to the VPC, such as a name.

#### Step 2: Define the Subnet

Next, you need to define the subnet within the VPC. Here is an example of how to do this:

```hcl
resource "aws_subnet" "example_subnet" {
  vpc_id     = aws_vpc.example_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "eu-west-3a"
  tags = {
    Name = "example-subnet"
  }
}
```

In this configuration:

- `vpc_id` references the VPC ID of the VPC you defined earlier.
- `cidr_block` specifies the range of IP addresses for the subnet.
- `availability_zone` specifies the AZ where the subnet will be created.
- `tags` allows you to add metadata to the subnet, such as a name.

### Referencing Resources in Terraform

Terraform allows you to reference resources that you have defined in the same context, even if they do not exist yet. This is done using the resource's name and the attribute you want to access.

For example, to reference the VPC ID of the VPC you defined earlier, you would use:

```hcl
aws_vpc.example_vpc.id
```

This gives you the whole object that will be created, and you can access the attributes of that object.

### Complete Example

Here is a complete example of creating a VPC and a subnet using Terraform:

```hcl
provider "aws" {
  region = "eu-west-3"
}

resource "aws_vpc" "example_vpc" {
  cidr_block = "1 0.0.0.0/16"
  tags = {
    Name = "example-vpc"
  }
}

resource "aws_subnet" "example_subnet" {
  vpc_id             = aws_vpc.example_vpc.id
  cidr_block         = "10.0.1.0/24"
  availability_zone  = "eu-west-3a"
  tags = {
    Name = "example-subnet"
  }
}
```

### Applying the Configuration

To apply the configuration, run the following commands:

```sh
terraform init
terraform plan
terraform apply
```

### Pitfalls and Best Practices

#### Common Mistakes

1. **Incorrect CIDR Block**: Ensure that the CIDR block for the VPC and subnet are correctly specified and do not overlap.
2. **Availability Zone**: Make sure the availability zone you specify exists in the region you are working in.
3. **Resource Dependencies**: Ensure that resources are properly referenced and dependencies are managed correctly.

#### Best Practices

1. **Use Tags**: Always use tags to label your resources for easy identification and management.
2. **CIDR Block Management**: Plan your CIDR blocks carefully to avoid conflicts and ensure scalability.
3. **Security Groups**: Use security groups to control inbound and outbound traffic to your subnets.

### Real-World Examples

#### Recent Breaches and CVEs

One notable breach involving misconfigured VPCs and subnets occurred in 2021, where a misconfigured security group allowed unauthorized access to sensitive data stored in S3 buckets. This highlights the importance of proper configuration and management of VPCs and subnets.

### How to Prevent / Defend

#### Detection

1. **AWS Config**: Use AWS Config to monitor changes to your VPC and subnet configurations.
2. **CloudTrail**: Enable CloudTrail to log API calls and user actions related to your VPC and subnets.

#### Prevention

1. **IAM Policies**: Use IAM policies to restrict access to VPC and subnet creation and modification.
2. **Security Groups**: Configure security groups to restrict inbound and outbound traffic to only necessary ports and protocols.

#### Secure Coding Fixes

**Vulnerable Code**

```hcl
resource "aws_vpc" "example_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "example-vpc"
  }
}

resource "aws_subnet" "example_subnet" {
  vpc_id             = aws_vpc.example_vpc.id
  cidr_block         = "10.0.1.0/24"
  availability_zone  = "eu-west-3a"
  tags = {
    Name = "example-subnet"
  }
}
```

**Secure Code**

```hcl
resource "aws_vpc" "example_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "example-vpc"
  }
}

resource "aws_security_group" "example_sg" {
  vpc_id = aws_vpc.example_vpc.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_subnet" "example_subnet" {
  vpc_id             = aws_vpc.example_vpc.id
  cidr_block         = "10.0.1.0/24"
  availability_zone  = "eu-west-3a"
  tags = {
    Name = "example-subnet"
  }
}
```

### Conclusion

Creating AWS resources using Terraform is a powerful way to manage your infrastructure as code. By defining VPCs and subnets in Terraform, you can ensure consistent and repeatable infrastructure deployments. Understanding how to reference resources and manage dependencies is crucial for successful Terraform configurations.

### Practice Labs

For hands-on practice with creating AWS resources using Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different aspects of web application security, including infrastructure setup.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: Another web application designed for security testing and training.
- **WebGoat**: An interactive, gamified training application for learning about web security vulnerabilities.

These labs provide practical experience in setting up and managing AWS resources using Terraform, helping you to master the skills covered in this chapter.

---
<!-- nav -->
[[01-Introduction to AWS Resource Creation Using Terraform Provider|Introduction to AWS Resource Creation Using Terraform Provider]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/06-Creating AWS Resources Using Terraform Provider/00-Overview|Overview]] | [[03-Introduction to AWS Resource Creation with Terraform|Introduction to AWS Resource Creation with Terraform]]
