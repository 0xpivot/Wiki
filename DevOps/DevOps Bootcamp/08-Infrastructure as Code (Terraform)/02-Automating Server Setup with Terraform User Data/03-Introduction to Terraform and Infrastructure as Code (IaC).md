---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform and Infrastructure as Code (IaC)

### What is Terraform?

Terraform is an open-source infrastructure as code (IaC) tool developed by HashiCorp. It allows you to define and provision your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL). Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud Platform, and many others. By using Terraform, you can manage your infrastructure in a consistent and repeatable manner, reducing the risk of human error and ensuring that your environment is always in sync with your desired state.

### Why Use Terraform?

The primary reasons for using Terraform include:

1. **Consistency**: Terraform ensures that your infrastructure is consistently deployed across different environments (development, testing, production).
2. **Repeatability**: You can easily recreate your entire infrastructure from scratch using the same configuration files.
3. **Version Control**: Since Terraform configurations are plain text files, they can be stored in version control systems like Git, allowing you to track changes and collaborate with team members.
4. **Automation**: Terraform automates the provisioning and management of your infrastructure, reducing the need for manual intervention.

### How Does Terraform Work?

Terraform operates by defining your infrastructure in configuration files. These files describe the resources you want to create, such as virtual machines, load balancers, databases, and more. Terraform uses a provider system to interact with different cloud platforms. Each provider is responsible for creating and managing resources specific to a particular cloud service.

Here’s a simple example of a Terraform configuration file that creates an AWS EC2 instance:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

In this example, the `provider` block specifies the AWS region, and the `resource` block defines an EC2 instance with a specific AMI and instance type.

### Limitations of Terraform

While Terraform is powerful for managing infrastructure, it has limitations when it comes to post-deployment tasks such as installing software, configuring services, or running scripts on the deployed servers. Once the infrastructure is set up, Terraform does not provide mechanisms to perform these tasks directly. Instead, you typically switch to other tools or methods to handle these operations.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/02-Automating Server Setup with Terraform User Data/02-Introduction to Infrastructure as Code (IaC)|Introduction to Infrastructure as Code (IaC)]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/02-Automating Server Setup with Terraform User Data/00-Overview|Overview]] | [[04-Automating Server Setup with Terraform User Data|Automating Server Setup with Terraform User Data]]
