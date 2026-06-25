---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to CICD Pipeline for EC2 Instance Deployment Using Terraform and Docker-compose

In this section, we will delve into the intricacies of setting up a Continuous Integration and Continuous Deployment (CI/CD) pipeline for deploying an application on an Amazon EC2 instance using Terraform and Docker-compose. This setup involves several key components, including infrastructure provisioning, security configurations, and deployment orchestration. Each step will be explained in detail, along with practical examples and potential pitfalls.

### Infrastructure Provisioning with Terraform

Terraform is an open-source infrastructure as code (IaC) tool that allows you to define and manage your infrastructure using declarative configuration files. In this context, we will use Terraform to provision an EC2 instance and configure necessary security settings.

#### Terraform Configuration File

Below is a sample Terraform configuration file (`main.tf`) that defines an EC2 instance:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_security_group" "example" {
  name        = "example"
  description = "Allow HTTP traffic"

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

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.example.id]

  tags = {
    Name = "example-instance"
  }
}
```

This configuration sets up an EC2 instance with a security group that allows HTTP traffic from any IP address.

### Security Group Configuration

The security group is crucial for controlling inbound and outbound traffic to the EC2 instance. In the above configuration, we allow HTTP traffic on port 80 from any IP address.

#### Security Group Rules

```hcl
resource "aws_security_group" "example" {
  name        = "example"
  description = "Allow HTTP traffic"

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

Here, `from_port` and `to_port` specify the range of ports to allow traffic on, and `cidr_blocks` specifies the IP addresses or ranges that are allowed to access these ports.

### Initialization Stage

Once the EC2 instance is provisioned, it enters an initialization stage where certain scripts are executed to set up the environment. This typically includes installing Docker and Docker-compose.

#### Initialization Script

A typical initialization script might look like this:

```bash
#!/bin/bash

# Update package lists
sudo apt-get update

# Install Docker
sudo apt-get install -y docker.io

# Install Docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

This script updates the package lists, installs Docker, and then installs Docker-compose.

### Jenkins Integration

Jenkins is used to orchestrate the CI/CD pipeline. Once the EC2 instance is running, Jenkins moves on to the deploy stage. However, it needs to wait until the initialization is complete before executing further commands on the server.

#### Jenkins Pipeline Configuration

Below is a sample Jenkins pipeline configuration (`Jenkinsfile`) that waits for the EC2 instance to initialize before proceeding with the deployment:

```groovy
pipeline {
    agent any

    stages {
        stage('Provision') {
            steps {
                script {
                    sh 'terraform init'
                    sh 'terraform apply -auto-approve'
                }
            }
        }
        stage('Wait for Initialization') {
            steps {
                timeout(time: 90, unit: 'SECONDS') {
                    script {
                        def instanceIp = sh(script: 'terraform output instance_ip', returnStdout: true).trim()
                        echo "Waiting for instance at ${instanceIp} to initialize..."
                        while (!sshCommand(instanceIp, 'echo "Initialization complete"')) {
                            sleep 10
                        }
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    def instanceIp = sh(script: 'terraform output instance_ip', returnStdout: true).trim()
                    sshCommand(instanceIp, 'docker-compose up -d')
                }
            }
        }
    }
}
```

This pipeline first provisions the EC2 instance using Terraform, then waits for the initialization to complete, and finally deploys the application using Docker-compose.

### SSH Access and Security Considerations

During the deployment process, Jenkins needs to establish an SSH connection to the EC2 instance. However, the initial attempt to establish this connection may fail due to security group restrictions.

#### Security Group Restriction Example

If the security group only allows access from a specific IP address, Jenkins may not be able to establish an SSH connection:

```hcl
resource "aws_security_group" "example" {
  name        = "example"
  description = "Allow SSH traffic from specific IP"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.1/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

In this example, only the IP address `192.168.1.1` is allowed to access port 22 (SSH).

### How to Prevent / Defend

To ensure Jenkins can establish an SSH connection to the EC2 instance, you need to allow the Jenkins server's IP address in the security group.

#### Secure Configuration

1. **Identify Jenkins Server IP**: Determine the IP address of the Jenkins server.
2. **Update Security Group**: Modify the security group to allow SSH traffic from the Jenkins server's IP address.

```hcl
resource "aws_security_group" "example" {
  name        = "example"
  description = "Allow SSH traffic from Jenkins server"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.1/32", "192.168.1.2/32"]  # Add Jenkins server IP
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

By allowing the Jenkins server's IP address, you ensure that Jenkins can establish an SSH connection to the EC2 instance.

### Real-World Examples and Pitfalls

#### Real-World Example: CVE-2021-26614

CVE-2021-26614 is a vulnerability in the AWS SDK for Java that could allow unauthorized access to AWS resources. This highlights the importance of securing your infrastructure and ensuring that your tools are up-to-date.

#### Pitfall: Incorrect Security Group Configuration

Incorrectly configuring the security group can lead to connectivity issues. Always verify that the necessary ports are open and that the correct IP addresses are allowed.

### Conclusion

Setting up a CI/CD pipeline for deploying an application on an EC2 instance using Terraform and Docker-compose involves several steps, including infrastructure provisioning, security configurations, and deployment orchestration. By following the detailed explanations and examples provided, you can ensure a smooth and secure deployment process.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can provide valuable insights into securing your infrastructure.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training.

These labs can help you gain practical experience in setting up and securing your CI/CD pipelines.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/04-CICD Pipeline for EC2 Instance Deployment Using Terraform And Docker-compose/00-Overview|Overview]] | [[02-Introduction to CICD Pipelines for EC2 Instance Deployment Using Terraform and Docker Compose|Introduction to CICD Pipelines for EC2 Instance Deployment Using Terraform and Docker Compose]]
