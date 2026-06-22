---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform Basics for Infrastructure Provisioning

In the realm of DevOps, managing and provisioning infrastructure is a critical task. This process involves setting up the necessary resources and configurations to support the deployment of applications. Terraform is a powerful tool that simplifies this process by allowing you to define and manage your infrastructure as code. This chapter will delve into the basics of Terraform, its role in infrastructure provisioning, and how it compares to other tools like Ansible.

### What is Terraform?

Terraform is an open-source infrastructure as code (IaC) tool developed by HashiCorp. It allows you to define your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL). These configurations describe the desired state of your infrastructure, including virtual machines, storage, networking, and more. Terraform then translates these configurations into actions to create, modify, or destroy infrastructure resources.

#### Why Use Terraform?

1. **Consistency**: Terraform ensures that your infrastructure is consistent across different environments (development, testing, production) by defining it in code.
2. **Version Control**: Since Terraform configurations are code, they can be stored in version control systems like Git, allowing you to track changes and collaborate with others.
3. **Automation**: Terraform automates the provisioning and management of infrastructure, reducing manual errors and saving time.
4. **Multi-Cloud Support**: Terraform supports multiple cloud providers, making it easy to manage hybrid cloud environments.

### Infrastructure Provisioning vs. Application Deployment

Infrastructure provisioning and application deployment are two distinct but related processes in DevOps:

1. **Infrastructure Provisioning**: This involves setting up the necessary resources and configurations to support the deployment of applications. Examples include creating virtual private clouds (VPCs), spinning up servers, configuring security groups, and installing software.
2. **Application Deployment**: Once the infrastructure is prepared, applications can be deployed on it. This may involve deploying Docker containers, configuring databases, and setting up monitoring and logging.

These tasks are often handled by different teams or individuals within an organization. A DevOps team member might configure the infrastructure, while a developer deploys the applications.

### Example Scenario: Setting Up a VPC and Deploying Docker Containers

Let's walk through an example scenario where we use Terraform to set up a VPC and then deploy Docker containers on the prepared infrastructure.

#### Step 1: Define the VPC in Terraform

First, we define the VPC in a Terraform configuration file (`main.tf`):

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"
}
```

This configuration sets up an AWS VPC with a CIDR block of `10.0.0.0/16`.

#### Step 2: Create EC2 Instances

Next, we create EC2 instances within the VPC:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.example.id]
  subnet_id              = aws_subnet.example.id
}
```

We also need to define the security group and subnet:

```hcl
resource "aws_security_group" "example" {
  name        = "example"
  description = "Allow HTTP traffic"
  vpc_id      = aws_vpc.example.id

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

resource "aws_subnet" "example" {
  vpc_id            = aws_vpc.example.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}
```

#### Step 3: Install Docker on EC2 Instances

To install Docker on the EC2 instances, we can use a user data script:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.example.id]
  subnet_id              = aws_subnet.example.id

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              EOF
}
```

#### Step 4: Deploy Docker Containers

Once the infrastructure is set up, the developer can deploy Docker containers on the EC2 instances. This might involve pushing Docker images to a registry and running them on the instances.

### Terraform vs. Ansible

Many people wonder about the differences between Terraform and Ansible, especially since both are used for infrastructure management. Let's explore these differences:

1. **Purpose**:
   - **Terraform**: Primarily used for provisioning and managing infrastructure resources (e.g., VPCs, EC2 instances, security groups).
   - **Ansible**: Used for configuration management, application deployment, and orchestration.

2. **Configuration Language**:
   - **Terraform**: Uses HCL for defining infrastructure.
   - **Ansible**: Uses YAML for defining playbooks and roles.

3. **Execution Model**:
   - **Terraform**: Works by comparing the current state of the infrastructure with the desired state defined in the configuration files. It then applies the necessary changes to achieve the desired state.
   - **Ansible**: Executes tasks in a sequential manner, typically defined in playbooks. It can run ad-hoc commands or apply complex configurations.

4. **Resource Management**:
   - **Terraform**: Manages infrastructure resources across multiple cloud providers and on-premises environments.
   - **Ansible**: Can manage both infrastructure and application configurations, but is more focused on the latter.

### Real-World Example: CVE-2021-21277

A real-world example of the importance of proper infrastructure management is the CVE-2021-21277 vulnerability in Docker. This vulnerability allowed attackers to escalate privileges and execute arbitrary code on the host system. Properly configured and managed infrastructure can help mitigate such risks.

#### Vulnerable Configuration

Consider a vulnerable Docker configuration where the `dockerd` service runs with elevated privileges:

```yaml
# Vulnerable Docker daemon configuration
{
  "graph": "/var/lib/docker",
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "insecure-registries": [
    "127.0.0.1:5000"
  ]
}
```

#### Secure Configuration

To secure this configuration, ensure that the `dockerd` service runs with minimal privileges and that unnecessary features are disabled:

```yaml
# Secure Docker daemon configuration
{
  "graph": "/var/lib/docker",
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "insecure-registries": [],
  "disable-legacy-registry": true,
  "iptables": false,
  "ip-forward": false,
  "ip-masq": false,
  "userns-remap": "default"
}
```

### How to Prevent / Defend

#### Detection

To detect misconfigurations or vulnerabilities in your infrastructure, you can use tools like Trivy or tfsec:

```sh
# Using Trivy to scan Docker images
trivy image my-docker-image:latest

# Using tfsec to scan Terraform configurations
tfsec .
```

#### Prevention

1. **Secure Coding Practices**: Ensure that your Terraform configurations follow best practices and avoid common pitfalls.
2. **Regular Audits**: Regularly audit your infrastructure configurations to identify and address vulnerabilities.
3. **Least Privilege Principle**: Run services and applications with the least privilege necessary to perform their tasks.

#### Secure-Coding Fixes

Compare the vulnerable and secure versions of a Terraform configuration:

```hcl
# Vulnerable Terraform configuration
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.example.id]
  subnet_id              = aws_subnet.example.id

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              EOF
}

# Secure Terraform configuration
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.example.id]
  subnet_id              = aws_subnet.example.id

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io
              usermod -aG docker ubuntu
              EOF
}
```

### Hands-On Labs

For hands-on practice with Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on infrastructure security.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for security training.
- **WebGoat**: An interactive web application security training tool.

### Conclusion

Terraform is a powerful tool for managing and provisioning infrastructure as code. By understanding its capabilities and limitations, you can effectively use it to set up and maintain your infrastructure. Comparing Terraform to other tools like Ansible helps clarify their respective roles and strengths. Real-world examples and secure coding practices further reinforce the importance of proper infrastructure management.

By following the principles outlined in this chapter, you can ensure that your infrastructure is secure, efficient, and scalable.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/01-Terraform Basics for Infrastructure Provisioning/02-Introduction to Infrastructure as Code (IaC)|Introduction to Infrastructure as Code (IaC)]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/01-Terraform Basics for Infrastructure Provisioning/00-Overview|Overview]] | [[04-Introduction to Terraform|Introduction to Terraform]]
