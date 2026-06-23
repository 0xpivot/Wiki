---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Infrastructure as Code (IaC)

### What is Infrastructure as Code?

Infrastructure as Code (IaC) is a practice where infrastructure is managed and provisioned through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows for automation, consistency, and version control of infrastructure configurations, making it easier to manage and scale environments.

### Why Use Infrastructure as Code?

Using IaC offers several benefits:

1. **Consistency**: Ensures that environments are consistently deployed across development, testing, and production stages.
2. **Version Control**: Allows tracking changes to infrastructure configurations, similar to how code is version-controlled.
3. **Automation**: Facilitates automated deployment and scaling of resources.
4. **Reproducibility**: Makes it easy to reproduce environments, reducing the risk of configuration drift.

### How Does Infrastructure as Code Work?

In IaC, infrastructure is defined using declarative or imperative languages. Declarative languages describe the desired state of the infrastructure, while imperative languages describe the steps to achieve the desired state. Common tools used for IaC include Terraform, Ansible, and CloudFormation.

### Example: Terraform

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

This Terraform configuration defines an AWS EC2 instance in the `us-west-2` region.

### Real-World Example: AWS Security Group Misconfiguration

A common misconfiguration in IaC is overly permissive security groups. For example, a security group might allow all inbound traffic, which can lead to unauthorized access.

#### Vulnerable Configuration

```hcl
resource "aws_security_group" "example" {
  name        = "example-sg"
  description = "Example security group"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

#### Secure Configuration

```hcl
resource "aws_security_group" "example" {
  name        = "example-sg"
  description = "Example security group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
}
```

### How to Prevent / Defend

1. **Use Security Best Practices**: Ensure security groups are configured to allow only necessary traffic.
2. **Automated Scanning Tools**: Use tools like Checkov or Terrascan to scan IaC for security issues.
3. **Regular Audits**: Conduct regular audits of IaC configurations to ensure compliance with security policies.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/16-Creating Pipelines Using Groovy Scripts/09-Hands-On Practice|Hands-On Practice]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/16-Creating Pipelines Using Groovy Scripts/00-Overview|Overview]] | [[11-Jenkins Pipeline Execution|Jenkins Pipeline Execution]]
