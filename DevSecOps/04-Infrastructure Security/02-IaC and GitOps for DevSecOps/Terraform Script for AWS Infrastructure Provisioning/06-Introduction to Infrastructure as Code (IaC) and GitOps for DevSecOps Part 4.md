---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps

Infrastructure as Code (IaC) is a practice in which infrastructure is defined using declarative configuration files rather than being manually provisioned and configured. This approach allows for automation, consistency, and version control of infrastructure configurations. GitOps is a set of practices that extends IaC by using Git as a single source of truth for all infrastructure-related changes. This ensures that all changes are reviewed, tested, and deployed through a CI/CD pipeline, providing a high level of visibility and control.

### Background Theory

In the context of DevSecOps, IaC and GitOps play a crucial role in ensuring that security is integrated into the development lifecycle. By defining infrastructure as code, teams can apply the same principles of continuous integration and delivery to their infrastructure as they do to their application code. This leads to more consistent, reliable, and secure infrastructure.

#### Key Concepts

- **Declarative Configuration**: Instead of specifying how to configure infrastructure, you define what the desired state should be. Tools like Terraform automatically determine the steps required to achieve this state.
- **Version Control**: Using a version control system like Git allows teams to track changes to infrastructure definitions, collaborate effectively, and roll back changes if necessary.
- **Automation**: Automation tools like Terraform can provision and manage infrastructure based on the declarative configuration files. This reduces human error and ensures consistency across environments.

### Example: Terraform Script for AWS Infrastructure Provisioning

Let's walk through an example of a Terraform script that provisions an AWS infrastructure. This script will create a VPC, security groups, EC2 instances, and grant necessary permissions via IAM roles.

#### Prerequisites

Before diving into the script, ensure you have the following:

- **Terraform Installed**: Download and install Terraform from the official website.
- **AWS CLI Configured**: Ensure your AWS CLI is configured with the necessary credentials.

### Terraform Script Breakdown

Below is a complete Terraform script that provisions a VPC, security groups, and EC2 instances in AWS.

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

resource "aws_security_group" "example" {
  name        = "example-sg"
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

  tags = {
    Name = "example-sg"
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

### IAM Permissions Required

To execute the above Terraform script, the IAM user needs specific permissions. Let's break down the required permissions:

1. **EC2 Full Access**:
   - This includes permissions to manage EC2 instances, security groups, and VPCs.
   
2. **IAM Full Access**:
   - This includes permissions to manage IAM roles and policies.
   
3. **SSM Systems Manager Read-Only Access**:
   - This includes permissions to read SSM parameters and documents.

#### Creating IAM Policies

First, create an IAM policy for EC2 full access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*"
      ],
      "Resource": "*"
    }
  ]
}
```

Next, create an IAM policy for IAM full access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:*"
      ],
      "Resource": "*"
    }
  ]
}
```

Finally, create an IAM policy for SSM Systems Manager read-only access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath"
      ],
      "Resource": "*"
    }
  ]
}
```

### Creating an IAM User and Attaching Policies

Now, create an IAM user and attach the policies:

1. **Create IAM User**:
   - Go to the IAM console and create a new user.
   - Attach the created policies to the user.

2. **Generate Access Key Credentials**:
   - Generate an access key for the user.
   - Store the access key securely (e.g., in a secrets manager).

### Setting Up Terraform Environment Variables

Set up the environment variables for Terraform:

```sh
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

### Running Terraform Commands

Initialize Terraform:

```sh
terraform init
```

Plan the infrastructure changes:

```sh
terraform plan
```

Apply the changes:

```sh
terraform apply
```

### Mermaid Diagrams

#### Network Topology

```mermaid
graph LR
  A[Internet] --> B[VPC]
  B --> C[Security Group]
  C --> D[EC2 Instance]
```

#### Request/Response Flow

```mermaid
sequenceDiagram
  participant Client
  participant Terraform
  participant AWS
  Client->>Terraform: Run terraform apply
  Terraform->>AWS: Create VPC
  AWS-->>Terraform: VPC Created
  Terraform->>AWS: Create Security Group
  AWS-->>Terraform: Security Group Created
  Terraform->>AWS: Create EC2 Instance
  AWS-->>Terraform: EC2 Instance Created
  Terraform-->>Client: Infrastructure Deployed
```

### Common Pitfalls and How to Prevent Them

#### Overly Permissive IAM Policies

**Problem**: Using overly permissive IAM policies can lead to security vulnerabilities.

**Solution**: Use least privilege principles and restrict permissions to only what is necessary.

**Example**:

- **Vulnerable Policy**:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ec2:*"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

- **Secure Policy**:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ec2:RunInstances",
          "ec2:DescribeInstances",
          "ec2:CreateSecurityGroup",
          "ec2:AuthorizeSecurityGroupIngress"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

#### Storing Secrets Insecurely

**Problem**: Storing access keys and other secrets insecurely can lead to unauthorized access.

**Solution**: Use a secrets manager to store and manage sensitive data.

**Example**:

- **Vulnerable Practice**:
  ```sh
  export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
  export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  ```

- **Secure Practice**:
  ```sh
  export AWS_ACCESS_KEY_ID=$(aws_secrets_manager_get secret_name)
  export AWS_SECRET_ACCESS_KEY=$(aws_secrets_manager_get secret_name)
  ```

### Detection and Prevention

#### Detection

- **Audit Logs**: Enable AWS CloudTrail to log API calls made to your AWS account.
- **IAM Access Advisor**: Use IAM Access Advisor to see which services a user or role has accessed.

#### Prevention

- **Least Privilege**: Grant users and roles only the minimum permissions necessary to perform their tasks.
- **Regular Audits**: Regularly review IAM policies and access patterns to identify and mitigate potential risks.

### Real-World Examples

#### Recent Breaches

- **CVE-2021-44228 (Log4j)**: While not directly related to IaC, the Log4j vulnerability highlights the importance of securing infrastructure configurations. Ensuring that all components of your infrastructure are up-to-date and patched is critical.

- **AWS S3 Bucket Exposure**: In 2021, several high-profile incidents involved misconfigured S3 buckets leading to data exposure. Proper IaC practices can help prevent such misconfigurations.

### Conclusion

By integrating IaC and GitOps into your DevSecOps workflow, you can ensure that your infrastructure is consistently and securely managed. Terraform provides a powerful toolset for provisioning and managing infrastructure, while IAM policies ensure that permissions are appropriately restricted. By following best practices and regularly auditing your configurations, you can minimize the risk of security vulnerabilities.

### Hands-On Labs

For hands-on practice with Terraform and AWS, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on infrastructure security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for practicing security testing.
- **CloudGoat**: A set of vulnerable AWS environments for learning cloud security.
- **flaws.cloud**: Provides vulnerable AWS environments for learning cloud security.
- **Pacu**: A collection of AWS exploitation modules for learning cloud security.

These labs provide practical experience in setting up and securing infrastructure using IaC and GitOps principles.

---
<!-- nav -->
[[05-Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 3|Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 3]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/00-Overview|Overview]] | [[07-Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps|Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps]]
