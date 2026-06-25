---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform and Infrastructure Management

Terraform is an open-source infrastructure as code (IaC) tool developed by HashiCorp. It allows users to define and provision infrastructure resources in a declarative manner using a high-level configuration language called HCL (HashiCorp Configuration Language). This approach enables developers and operations teams to manage their infrastructure in a consistent, repeatable, and automated fashion.

### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is a practice where infrastructure is managed and provisioned through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This allows infrastructure to be treated like software, enabling version control, collaboration, and automation.

### Why Use Terraform?

Terraform provides several key benefits:

1. **Consistency**: By defining infrastructure in code, you ensure that your environment is consistently deployed across different environments (development, staging, production).
2. **Automation**: Terraform automates the provisioning and management of infrastructure, reducing manual errors and saving time.
3. **Version Control**: Infrastructure definitions can be stored in version control systems, allowing you to track changes and roll back to previous versions if needed.
4. **Multi-cloud Support**: Terraform supports a wide range of cloud providers and services, making it easy to manage hybrid and multi-cloud environments.

### Basic Concepts in Terraform

Before diving into the `terraform destroy` command, it's important to understand some fundamental concepts in Terraform:

1. **State File**: Terraform maintains a state file that tracks the current state of your infrastructure. This file is crucial for Terraform to know what resources exist and how they are configured.
2. **Providers**: Providers are plugins that allow Terraform to interact with different cloud platforms and services. Each provider has its own set of resources and data sources.
3. **Resources**: Resources represent the actual infrastructure components (e.g., EC2 instances, S3 buckets, RDS databases).
4. **Modules**: Modules are reusable components that encapsulate multiple resources and configurations. They help in organizing and reusing code.

### Example Terraform Configuration

Here is a simple example of a Terraform configuration file (`main.tf`) that creates a VPC and subnets in AWS:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
}
```

This configuration defines an AWS provider, a VPC, and a subnet within that VPC.

### Terraform Workflow

The typical workflow in Terraform includes the following steps:

1. **Initialization**: `terraform init` initializes the working directory and downloads necessary plugins.
2. **Planning**: `terraform plan` generates an execution plan based on the current state and the desired configuration.
3. **Applying**: `terraform apply` applies the changes described in the execution plan.
4. **Destroying**: `terraform destroy` removes all resources defined in the configuration.

---
<!-- nav -->
[[01-Introduction to Terraform Plan Command|Introduction to Terraform Plan Command]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/17-Terraform Plan Command Preview Without Application/00-Overview|Overview]] | [[03-Terraform Destroy Command|Terraform Destroy Command]]
