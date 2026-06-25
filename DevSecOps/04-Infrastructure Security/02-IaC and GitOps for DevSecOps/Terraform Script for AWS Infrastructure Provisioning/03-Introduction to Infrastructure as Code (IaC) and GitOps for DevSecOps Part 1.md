---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps

Infrastructure as Code (IaC) is a method of managing and provisioning computing infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. In the context of DevSecOps, IaC plays a crucial role in ensuring consistency, reliability, and security across environments. GitOps extends IaC principles by using Git as a single source of truth for declarative infrastructure and application configurations.

### Terraform Overview

Terraform is an open-source IaC tool developed by HashiCorp. It allows you to define and provision infrastructure using a high-level configuration language called HCL (HashiCorp Configuration Language). Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud, and many others.

#### Why Use Terraform?

- **Consistency**: Terraform ensures that your infrastructure is consistently deployed across different environments.
- **Version Control**: By storing your infrastructure definitions in a version control system like Git, you can track changes and collaborate effectively.
- **Automation**: Terraform automates the provisioning and management of infrastructure, reducing manual errors and improving efficiency.
- **Multi-cloud Support**: Terraform supports multiple cloud providers, making it easy to manage hybrid cloud environments.

### Modules in Terraform

Modules in Terraform are reusable components that encapsulate a set of resources and their dependencies. They allow you to abstract away the complexity of defining individual resources, making it easier to manage larger and more complex infrastructures.

#### Benefits of Using Modules

- **Reusability**: Modules can be reused across different projects, reducing duplication of effort.
- **Abstraction**: Modules hide the implementation details, making it easier to understand and maintain the overall architecture.
- **Encapsulation**: Modules encapsulate related resources, making it easier to manage dependencies and configurations.

### Example: Creating a VPC Module

Let's walk through an example of creating a VPC module using Terraform. A VPC (Virtual Private Cloud) is a logically isolated section of the AWS cloud where you can launch AWS resources in a virtual network that you define.

#### Step-by-Step Guide

1. **Define the Module Structure**

   Create a directory structure for your module:

   ```
   vpc/
   ├── main.tf
   ├── variables.tf
   └── outputs.tf
   ```

2. **Define Variables**

   In `variables.tf`, define the input variables for the VPC module:

   ```hcl
   variable "name" {
     description = "The name of the VPC"
     type        = string
   }

   variable "cidr_block" {
     description = "The CIDR block for the VPC"
     type        = string
   }

   variable "availability_zones" {
     description = "List of availability zones"
     type        = list(string)
   }
   ```

3. **Create the VPC Resource**

   In `main.tf`, define the VPC resource:

   ```hcl
   resource "aws_vpc" "main" {
     cidr_block = var.cidr_block
     tags       = {
       Name = var.name
     }
   }

   resource "aws_subnet" "private" {
     count               = length(var.availability_zones)
     vpc_id              = aws_vpc.main.id
     cidr_block          = cidrsubnet(var.cidr_block, 8, count.index)
     availability_zone   = element(var.availability_zones, count.index)
     map_public_ip_on_launch = false
     tags                = {
       Name = "${var.name}-private-${count.index}"
     }
   }

   resource "aws_subnet" "public" {
     count               = length(var.availability_zones)
     vpc_id              = aws_vpc.main.id
     cidr_block          = cidrsubnet(var.cidr_block, 8, count.index + length(var.availability_zones))
     availability_zone   = element(var.availability_zones, count.index)
     map_public_ip_on_launch = true
     tags                = {
       Name = "${var.name}-public-${count.index}"
     }
   }
   ```

4. **Define Outputs**

   In `outputs.tf`, define the outputs for the VPC module:

   ```hcl
   output "vpc_id" {
     value = aws_vvpc.main.id
   }

   output "private_subnets" {
     value = aws_subnet.private.*.id
   }

   output "public_subnets" {
     value = aws_subnet.public.*.id
   }
   ```

5. **Use the Module**

   In your main Terraform configuration, use the VPC module:

   ```hcl
   module "vpc" {
     source = "./vpc"

     name                  = "main-vpc"
     cidr_block            = "10.0.0.0/16"
     availability_zones    = ["us-west-2a", "us-west-2b", "us-west-2c"]
   }
   ```

### Security Groups in Terraform

Security groups are a fundamental component of AWS security. They act as virtual firewalls that control inbound and outbound traffic to your instances.

#### Creating Security Groups

1. **Define Security Group Resources**

   In your Terraform configuration, define the security group resources:

   ```hcl
   resource "aws_security_group" "main" {
     name        = "main-security-group"
     description = "Main security group for EC2 instances"
     vpc_id      = module.vpc.vpc_id

     ingress {
       from_port   = 0
       to_port     = 0
       protocol    = "-1"
       cidr_blocks = [module.vpc.cidr_block]
     }

     egress {
       from_port   = 0
       to_port     = 0
       protocol    = "-1"
       cidr_blocks = ["0.0.0.0/0"]
     }
   }

   resource "aws_security_group" "application" {
     name        = "application-security-group"
     description = "Application security group for EC2 instances"
     vpc_id      = module.vpc.vpc_id

     ingress {
       from_port   = 0
       to_port     = 0
       protocol    = "-1"
       cidr_blocks = [module.vpc.cidr_block]
     }

     ingress {
       from_port   = 3000
       to_port     = 3000
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

2. **Attach Security Groups to Instances**

   Attach the security groups to your EC2 instances:

   ```hcl
   resource "aws_instance" "main" {
     ami           = "ami-0c55b159cbfafe1f0"
     instance_type = "t2.micro"
     subnet_id     = module.vpc.public_subnets[0]

     security_groups = [
       aws_security_group.main.name,
       aws_security_group.application.name
     ]
   }
   ```

### Real-World Examples and CVEs

#### Example: CVE-2021-20225

CVE-2021-20225 is a critical vulnerability in AWS Elastic Load Balancing (ELB) that could allow unauthorized access to internal resources. This vulnerability highlights the importance of properly configuring security groups and network ACLs.

**Impact**: An attacker could bypass security controls and gain unauthorized access to internal resources.

**Mitigation**: Ensure that security groups are configured to allow only necessary inbound traffic and that network ACLs are properly configured to restrict access.

```hcl
resource "aws_security_group" "secure_sg" {
  name        = "secure-sg"
  description = "Secure security group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
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

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Enable detailed logging and monitoring for your security groups and network ACLs. Use tools like AWS CloudTrail and AWS Config to monitor changes and detect unauthorized access attempts.
- **Regular Audits**: Conduct regular audits of your security group configurations to ensure they align with your security policies.

#### Prevention

- **Least Privilege Principle**: Configure security groups to allow only the minimum necessary inbound and outbound traffic.
- **Network Segmentation**: Use network segmentation to isolate sensitive resources and limit the blast radius of potential attacks.

#### Secure Coding Fixes

Compare the insecure and secure versions of a security group configuration:

**Insecure Version**

```hcl
resource "aws_security_group" "insecure_sg" {
  name        = "insecure-sg"
  description = "Insecure security group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
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

**Secure Version**

```hcl
resource "aws_security_group" "secure_sg" {
  name        = "secure-sg"
  description = "Secure security group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
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

### Hands-On Labs

For practical experience with Terraform and IaC, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on IaC and cloud security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.
- **WebGoat**: An interactive web application security training tool.

These labs provide a comprehensive learning experience and help you apply the concepts learned in a practical setting.

### Conclusion

In this chapter, we explored the fundamentals of Infrastructure as Code (IaC) and GitOps in the context of DevSecOps. We delved into the use of Terraform for provisioning AWS infrastructure, focusing on the creation of VPC modules and security groups. We also discussed real-world examples and vulnerabilities, along with mitigation strategies and secure coding practices. By following these guidelines, you can ensure that your infrastructure is consistent, reliable, and secure.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/02-Introduction to IaC and GitOps for DevSecOps|Introduction to IaC and GitOps for DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/00-Overview|Overview]] | [[04-Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2|Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2]]
