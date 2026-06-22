---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Web Server Configuration Using Terraform Modules

In the realm of DevOps, infrastructure as code (IaC) is a critical practice that enables teams to manage their infrastructure through code. One of the most popular tools for implementing IaC is Terraform, developed by HashiCorp. This chapter will delve into the process of configuring a web server using Terraform modules, focusing on the declaration of variables and referencing them within the `main.tf` file.

### Background Theory

Before diving into the specifics of Terraform modules, it's essential to understand the underlying principles of IaC and Terraform.

#### Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is a practice where infrastructure is defined and managed using code rather than manual processes. This approach offers several benefits:

1. **Reproducibility**: Infrastructure can be consistently reproduced across different environments.
2. **Version Control**: Infrastructure changes can be tracked and managed using version control systems.
3. **Automation**: Deployment and management tasks can be automated, reducing human error.
4. **Collaboration**: Multiple team members can work on the same infrastructure definitions.

#### Terraform Overview

Terraform is an open-source tool for building, changing, and versioning infrastructure safely and efficiently. It allows you to define your infrastructure in declarative configuration files, which are written in the HashiCorp Configuration Language (HCL).

Key features of Terraform include:

1. **Provider Support**: Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud, and many others.
2. **State Management**: Terraform maintains a state file that tracks the current state of your infrastructure.
3. **Modules**: Terraform modules allow you to encapsulate reusable components of your infrastructure.
4. **Variables and Outputs**: Terraform provides mechanisms to parameterize your configurations and expose outputs.

### Declaring Variables in Terraform

One of the fundamental aspects of Terraform is the ability to declare and use variables. Variables allow you to parameterize your infrastructure definitions, making them more flexible and reusable.

#### Creating the `variables.tf` File

The first step in declaring variables is to create a `variables.tf` file. This file will contain all the variables needed for your Terraform configuration.

```hcl
variable "vpc_id" {
  description = "The ID of the VPC"
}

variable "ip_prefix" {
  description = "The IP prefix for the subnet"
}

variable "image_name" {
  description = "The name of the AMI image"
}

variable "public_key_location" {
  description = "The location of the public SSH key"
}
```

Each variable is defined with a `description` attribute, which provides a brief explanation of the variable's purpose. In this example, we have defined four variables:

1. `vpc_id`: The ID of the VPC.
2. `ip_prefix`: The IP prefix for the subnet.
3. `image_name`: The name of the AMI image.
4. `public_key_location`: The location of the public SSH key.

#### Specifying Variable Types

While the above example leaves the variable types unspecified, it's often beneficial to explicitly define the types of your variables. This helps ensure that the correct data types are used and can catch errors early.

```hcl
variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "ip_prefix" {
  description = "The IP prefix for the subnet"
  type        = string
}

variable "image_name" {
  description = "The name of the AMI image"
  type        = string
}

variable "public_key_location" {
  description = "The location of the public SSH key"
  type        = string
}
```

By specifying the `type` attribute, we ensure that the variables are treated as strings. This is particularly useful when working with complex configurations where type mismatches can lead to errors.

### Referencing Variables in `main.tf`

Once the variables are declared in the `variables.tf` file, they need to be referenced in the `main.tf` file. This file contains the main Terraform configuration that defines the resources to be created.

#### Example `main.tf` File

Here is an example of how the `main.tf` file might look:

```hcl
module "web_server" {
  source = "./modules/web_server"

  vpc_id            = var.vpc_id
  ip_prefix         = var.ip_prefix
  image_name        = var.image_name
  public_key_location = var.public_key_location
}
```

In this example, we are referencing a module named `web_server`. The `source` attribute specifies the path to the module, and the variables are passed as arguments to the module.

### Using Modules in Terraform

Modules are a powerful feature of Terraform that allow you to encapsulate reusable components of your infrastructure. A module is essentially a directory containing one or more `.tf` files that define a set of resources.

#### Structure of a Module

A typical module structure might look like this:

```
/modules/
  /web_server/
    main.tf
    variables.tf
    outputs.tf
```

- `main.tf`: Contains the main Terraform configuration for the module.
- `variables.tf`: Defines the input variables for the module.
- `outputs.tf`: Defines the output values that the module exposes.

#### Example `main.tf` for the Module

Here is an example of what the `main.tf` file inside the `web_server` module might look like:

```hcl
resource "aws_instance" "web" {
  ami           = var.image_name
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.web.id]

  key_name = var.public_key_location

  user_data = <<-EOF
              #!/bin/bash
              echo "Hello, World!" > index.html
              nohup python -m SimpleHTTPServer 80 &
              EOF

  tags = {
    Name = "web-server"
  }
}

resource "aws_security_group" "web" {
  name        = "web-server-sg"
  description = "Security group for web server"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

This `main.tf` file defines an AWS EC2 instance and a security group. The instance uses the specified AMI image and public key, and the security group allows inbound traffic on port 80.

### Running Terraform Commands

Once the variables and modules are defined, you can run Terraform commands to plan and apply the changes.

#### Terraform Plan

The `terraform plan` command generates an execution plan, which shows the changes that will be made to your infrastructure.

```sh
terraform plan
```

This command will display the planned changes, allowing you to review them before applying them.

#### Terraform Apply

The `terraform apply` command applies the changes defined in the execution plan.

```sh
terraform apply
```

This command will prompt you to confirm the changes before applying them.

### Common Pitfalls and Best Practices

When working with Terraform modules and variables, there are several common pitfalls to avoid:

1. **Uninitialized Variables**: Ensure that all required variables are initialized before running Terraform commands.
2. **Type Mismatches**: Always specify the types of your variables to catch type mismatches early.
3. **Overly Complex Modules**: Keep modules simple and focused on a single task to improve maintainability.
4. **Hardcoded Values**: Avoid hardcoding values in your Terraform configurations; use variables instead.

### Real-World Examples and Recent Breaches

To illustrate the importance of proper configuration and security practices, consider the following real-world examples:

#### CVE-2021-20225: AWS IAM Policy Misconfiguration

In 2021, a misconfigured IAM policy allowed unauthorized access to sensitive AWS resources. This breach highlights the importance of properly securing and managing IAM policies.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

This overly permissive policy grants full access to all AWS resources, which can be exploited by malicious actors. To prevent such issues, ensure that IAM policies are tightly scoped and reviewed regularly.

#### Secure Configuration Example

Here is an example of a securely configured IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

This policy restricts access to specific EC2 actions, reducing the risk of unauthorized access.

### How to Prevent / Defend

To defend against common vulnerabilities and ensure secure configurations, follow these best practices:

1. **Use Least Privilege Principle**: Grant only the minimum permissions necessary for a given task.
2. **Regular Audits**: Perform regular audits of your infrastructure configurations to identify and remediate potential issues.
3. **Secure Coding Practices**: Follow secure coding practices, such as validating user inputs and sanitizing data.
4. **Automated Testing**: Implement automated testing to validate your configurations and catch errors early.

### Hands-On Labs

To gain practical experience with Terraform modules and web server configuration, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide a safe environment to practice and reinforce the concepts covered in this chapter.

### Conclusion

In this chapter, we have explored the process of configuring a web server using Terraform modules. We covered the declaration of variables, referencing them in the `main.tf` file, and using modules to encapsulate reusable components. We also discussed common pitfalls, real-world examples, and best practices for securing your infrastructure.

By following these guidelines and practicing with hands-on labs, you can build robust and secure web server configurations using Terraform.

---
<!-- nav -->
[[02-Introduction to Web Server Configuration Using Modules in Terraform|Introduction to Web Server Configuration Using Modules in Terraform]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/22-Web Server Configuration Module Extraction/00-Overview|Overview]] | [[04-Introduction to Web Server Configuration Using Terraform|Introduction to Web Server Configuration Using Terraform]]
