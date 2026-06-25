---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Finalizing the Automation Pipeline with Terraform and Ansible

In this section, we will delve into the final stages of automating the entire server setup process using Terraform and Ansible. This involves creating the necessary infrastructure, configuring it, and ensuring that the setup is automated from start to finish. We will cover the destruction of existing resources, creation of new ones, and the use of provisioners to execute Ansible commands on the newly created instances.

### Destroying Existing Resources

Before setting up new resources, it is crucial to clean up any existing infrastructure to avoid conflicts and ensure a fresh start. This is particularly important in a development environment where changes are frequent and iterative.

#### Terraform Workflow

Terraform uses a declarative approach to manage infrastructure. To destroy existing resources, you would typically run the `terraform destroy` command. This command prompts Terraform to delete all the resources defined in your Terraform configuration files.

```bash
terraform destroy
```

This command will prompt you to confirm the action:

```
Do you really want to destroy?
  Terraform will destroy all your managed infrastructure, after which they will not exist anymore.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes
```

Upon confirmation, Terraform will proceed to delete all the resources defined in your configuration.

### Creating New Resources

After destroying the existing resources, we can now create new ones. In this example, we will focus on creating a Virtual Private Cloud (VPC), Subnets, Internet Gateway, and Security Groups, followed by an EC2 instance.

#### Terraform Configuration

Let's look at a complete Terraform configuration that sets up these resources:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "example-vpc"
  }
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "example-subnet"
  }
}

resource "aws_internet_gateway" "example" {
  vpc_id = aws_vpc.example.id

  tags = {
    Name = "example-internet-gateway"
  }
}

resource "aws_security_group" "example" {
  name        = "allow_all"
  description = "Allow all inbound traffic"
  vpc_id      = aws_vpc.example.id

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

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  subnet_id = aws_subnet.example.id
  vpc_security_group_ids = [aws_security_group.example.id]

  tags = {
    Name = "example-instance"
  }
}
```

### Provisioning the EC2 Instance with Ansible

Once the EC2 instance is created, we can use a provisioner to execute Ansible commands on it. A provisioner is a mechanism in Terraform that allows you to perform actions on the resource being created.

#### Available Provisioners

Terraform provides several types of provisioners:

- **local-exec**: Executes a command locally on the machine running Terraform.
- **remote-exec**: Executes a command on the remote machine (the one being created).
- **file**: Copies files to the remote machine.

For our use case, we will use the `local-exec` provisioner to run Ansible commands.

#### Using `local-exec` Provisioner

Here’s how you can add a `local-exec` provisioner to the EC2 instance configuration:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  subnet_id = aws_subnet.example.id
  vpc_security_group_ids = [aws_security_group.example.id]

  tags = {
    Name = "example-instance"
  }

  provisioner "local-exec" {
    command = "ansible apply --target ${self.private_ip}"
  }
}
```

### Explanation of the Provisioner

The `local-exec` provisioner runs a command locally on the machine where Terraform is executed. In this case, the command is `ansible apply --target ${self.private_ip}`, which applies Ansible configurations to the EC2 instance identified by its private IP address.

#### Why Use `local-exec`?

Using `local-exec` is beneficial because it allows you to run commands on the local machine, which can be more flexible and easier to manage than running commands directly on the remote machine. Additionally, it ensures that the command is executed immediately after the resource is created, ensuring that the provisioning steps are completed before the resource is considered ready.

### Real-World Example: Recent Breaches and CVEs

To understand the importance of automation and proper provisioning, consider recent breaches and vulnerabilities:

- **CVE-2021-21972**: This vulnerability in AWS Elastic Load Balancing (ELB) allowed unauthorized access to internal services. Proper automation and provisioning can help mitigate such risks by ensuring that security groups and network configurations are correctly set up.
- **SolarWinds Supply Chain Attack (CVE-2020-1014)**: This attack compromised multiple organizations by injecting malicious code into SolarWinds software updates. Automated provisioning and configuration management can help detect and prevent such attacks by ensuring that all systems are configured securely and consistently.

### How to Prevent / Defend

#### Detection

To detect potential issues, you can use tools like AWS Config and AWS Trusted Advisor to monitor your infrastructure for compliance and security issues. Additionally, you can set up logging and monitoring using AWS CloudTrail and Amazon CloudWatch.

#### Prevention

1. **Secure Configuration Management**: Ensure that all infrastructure is defined in code and version-controlled. This helps maintain consistency and allows for easy auditing and rollbacks.
2. **Least Privilege Principle**: Configure security groups and IAM roles to follow the principle of least privilege. Limit access to only what is necessary.
3. **Regular Audits**: Regularly audit your infrastructure for compliance and security issues. Use tools like AWS Security Hub and third-party scanners like Aqua Security or Twistlock.

#### Secure Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```hcl
resource "aws_security_group" "example" {
  name        = "allow_all"
  description = "Allow all inbound traffic"
  vpc_id      = aws_vpc.example.id

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

**Secure Configuration:**

```hcl
resource "aws_security_group" "example" {
  name        = "secure_sg"
  description = "Secure security group"
  vpc_id      = aws_vpc.example.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

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

### Hands-On Labs

To practice and reinforce your understanding, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers infrastructure security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for practicing web security.
- **WebGoat**: An interactive web application for learning about web security.

These labs provide practical experience in setting up and securing infrastructure, which is essential for mastering DevOps practices.

### Conclusion

Automating server setup with Terraform and Ansible is a powerful way to ensure consistent and secure infrastructure. By understanding the concepts, tools, and best practices covered in this section, you can build robust and secure systems that are resilient to common vulnerabilities and breaches.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/03-Automating Server Setup with Terraform and Ansible/03-Automating Server Setup with Terraform and Ansible|Automating Server Setup with Terraform and Ansible]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/03-Automating Server Setup with Terraform and Ansible/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/03-Automating Server Setup with Terraform and Ansible/05-Practice Questions & Answers|Practice Questions & Answers]]
