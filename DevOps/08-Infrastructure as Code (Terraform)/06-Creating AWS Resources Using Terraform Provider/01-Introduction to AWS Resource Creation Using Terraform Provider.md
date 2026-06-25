---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS Resource Creation Using Terraform Provider

In the realm of DevOps, infrastructure as code (IaC) tools like Terraform play a pivotal role in automating the provisioning and management of cloud resources. This chapter delves into the process of creating AWS resources using the Terraform provider, focusing specifically on fetching and utilizing Virtual Private Clouds (VPCs).

### What is Terraform?

Terraform is an open-source IaC tool developed by HashiCorp. It allows you to define and provision infrastructure across multiple cloud providers using a declarative configuration language called HCL (HashiCorp Configuration Language). Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud Platform, and many others.

### Why Use Terraform for AWS Resource Management?

Using Terraform for managing AWS resources offers several advantages:

1. **Consistency**: Terraform ensures that your infrastructure is consistent across different environments (development, staging, production).
2. **Automation**: Automates the creation, modification, and deletion of resources, reducing manual errors.
3. **Version Control**: Allows you to version control your infrastructure configurations, making it easier to track changes and collaborate with team members.
4. **Multi-Cloud Support**: Supports multiple cloud providers, enabling hybrid cloud strategies.

### What is a Virtual Private Cloud (VPC)?

A Virtual Private Cloud (VPC) is a logically isolated section of the AWS cloud where you can launch AWS resources in a virtual network that you define. A VPC enables you to have complete control over the IP address range, subnets, routing tables, gateways, and security settings.

### Fetching VPCs Using Terraform

To fetch VPCs using Terraform, you need to define a `data` resource. Data resources allow you to retrieve information about existing resources in your cloud environment. In the context of AWS, you can use the `aws_vpc` data source to fetch details about VPCs.

#### Parameters and Filters

When fetching VPCs, you can specify various parameters and filters to narrow down the results. These parameters include:

- **CIDR Block**: The IPv4 CIDR block associated with the VPC.
- **Default VPC**: Whether the VPC is the default VPC.
- **VPC ID**: The unique identifier of the VPC.
- **Tags**: Key-value pairs associated with the VPC.

Let's explore these parameters in detail.

### CIDR Block Parameter

The CIDR block parameter allows you to specify a specific IPv4 CIDR block to match against the VPCs. This is useful when you want to ensure that the VPC you are working with has a particular IP range.

```hcl
data "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}
```

### Default VPC Parameter

The default VPC parameter allows you to fetch the default VPC. By default, AWS creates a default VPC for each region unless explicitly disabled. This parameter is useful when you want to work with the default VPC.

```hcl
data "aws_vpc" "default" {
  default = true
}
```

### VPC ID Parameter

The VPC ID parameter allows you to specify the unique identifier of the VPC. This is useful when you already know the VPC ID and want to fetch details about that specific VPC.

```hcl
data "aws_vpc" "by_id" {
  id = "vpc-12345678"
}
```

### Tags Parameter

The tags parameter allows you to specify key-value pairs to match against the VPCs. This is useful when you want to fetch VPCs based on metadata.

```hcl
data "aws_vpc" "by_tag" {
  tags = {
    Environment = "Production"
  }
}
```

### Filter Attribute

The filter attribute allows you to define more custom criteria to fetch the VPC. This is useful when you need to apply complex filtering logic.

```hcl
data "aws_vpc" "custom_filter" {
  filter {
    name   = "tag:Environment"
    values = ["Production"]
  }

  filter {
    name   = "cidr-block"
    values = ["10.0.0.0/16"]
  }
}
```

### Example: Fetching a Default VPC

Let's walk through an example of fetching a default VPC and creating a subnet within that VPC.

```hcl
# Fetch the default VPC
data "aws_vpc" "default" {
  default = true
}

# Create a subnet within the default VPC
resource "aws_subnet" "example" {
  vpc_id     = data.aws_vpc.default.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}
```

### Explanation of the Code

1. **Data Source Definition**:
   - `data "aws_vpc" "default"`: Defines a data source to fetch the default VPC.
   - `default = true`: Specifies that we want to fetch the default VPC.

2. **Resource Definition**:
   - `resource "aws_subnet" "example"`: Defines a resource to create a subnet.
   - `vpc_id = data.aws_vpc.default.id`: References the ID of the default VPC fetched by the data source.
   - `cidr_block = "10.0.1.0/24"`: Specifies the CIDR block for the subnet.
   - `availability_zone = "us-west-2a"`: Specifies the availability zone for the subnet.

### How to Prevent / Defend

#### Detection

To detect misconfigurations or unauthorized access to VPCs, you can use AWS CloudTrail and AWS Config.

- **AWS CloudTrail**: Logs API calls made to your AWS account, including those related to VPCs. You can monitor these logs to detect unauthorized changes.
- **AWS Config**: Provides a detailed view of your AWS resource configurations and changes over time. You can use it to audit and validate your VPC configurations.

#### Prevention

- **IAM Policies**: Ensure that IAM policies are properly configured to restrict access to VPC-related actions.
- **Network ACLs and Security Groups**: Configure Network ACLs and Security Groups to control inbound and outbound traffic to your VPC.
- **Subnet Isolation**: Use private subnets and public subnets appropriately to isolate sensitive resources.

#### Secure-Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**:
```hcl
resource "aws_vpc" "insecure" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "insecure" {
  vpc_id     = aws_vpc.insecure.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}
```

**Secure Configuration**:
```hcl
resource "aws_vpc" "secure" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_subnet" "secure" {
  vpc_id     = aws_vpc.secure.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "secure-subnet"
  }
}
```

### Conclusion

In this chapter, we explored the process of fetching and utilizing VPCs using Terraform. We covered various parameters and filters that can be used to narrow down the results, and provided a detailed example of fetching a default VPC and creating a subnet within that VPC. Additionally, we discussed how to prevent and defend against potential security issues related to VPCs.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web application security.
- **OWASP Juice Shop**: An intentionally insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally insecure web application for learning web security.
- **WebGoat**: A deliberately insecure Java web application maintained by OWASP for security training purposes.

These labs provide practical experience in applying the concepts learned in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/06-Creating AWS Resources Using Terraform Provider/00-Overview|Overview]] | [[02-Introduction to AWS Resource Creation Using Terraform|Introduction to AWS Resource Creation Using Terraform]]
