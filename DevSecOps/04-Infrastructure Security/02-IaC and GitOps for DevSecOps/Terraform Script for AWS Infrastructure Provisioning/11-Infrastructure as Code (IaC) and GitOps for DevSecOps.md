---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Infrastructure as Code (IaC) and GitOps for DevSecOps

### Introduction to Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is a practice where infrastructure is defined using code rather than manual processes. This approach allows developers and operations teams to manage infrastructure in a consistent, repeatable manner. By treating infrastructure as code, you can leverage version control systems like Git, automate deployments, and ensure consistency across environments.

### Role-Based Access Control (RBAC) in AWS

In AWS, Role-Based Access Control (RBAC) is a critical component for managing access to resources. Roles allow you to define permissions that can be assumed by entities such as EC2 instances, Lambda functions, or users. This ensures that only authorized entities can perform specific actions within your AWS environment.

#### Trust Policy

A trust policy defines which entities can assume a role. In the context of EC2 instances, the trust policy specifies that an EC2 instance can assume the role. Here’s an example of a trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

This policy allows EC2 instances to assume the role by specifying `ec2.amazonaws.com` as the principal service.

#### Policy Attachment

Once a role is created with a trust policy, you need to attach policies to it to define the permissions. These policies specify what actions the role can perform on which resources. For example, you might attach a policy that grants SSM managed instance core and EC2 Container Registry full access permissions.

Here’s an example of a policy that grants these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:*",
        "ecr:*"
      ],
      "Resource": "*"
    }
  ]
}
```

This policy allows the role to perform any action related to SSM and ECR.

### Instance Profiles

An instance profile is a container for an IAM role that can be assigned to an EC2 instance. When an instance is associated with an instance profile, the instance assumes the permissions defined by the role.

To create an instance profile, you first create a role and attach the necessary policies. Then, you create an instance profile and associate the role with it.

Here’s an example of creating an instance profile using AWS CLI:

```sh
# Create a role
aws iam create-role --role-name MyInstanceRole --assume-role-policy-document file://trust-policy.json

# Attach a policy to the role
aws iam attach-role-policy --role-name MyInstanceRole --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Create an instance profile
aws iam create-instance-profile --instance-profile-name MyInstanceProfile

# Add the role to the instance profile
aws iam add-role-to-instance-profile --instance-profile-name MyInstanceProfile --role-name MyInstanceRole
```

### Creating Networking Resources

When provisioning infrastructure using IaC, it’s important to create all networking resources explicitly rather than relying on default VPCs. This ensures that your infrastructure is self-sufficient and can be easily cleaned up.

#### Example: Creating a VPC Using Terraform

Terraform is a popular IaC tool that allows you to define and provision infrastructure using declarative configuration files. Here’s an example of creating a VPC using Terraform:

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

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "public-subnet"
  }
}

resource "aws_internet_gateway" "example" {
  vpc_id = aws_vpc.example.id

  tags = {
    Name = "example-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.example.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.example.id
  }

  tags = {
    Name = "public-route-table"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
```

This Terraform configuration creates a VPC, a public subnet, an internet gateway, and a route table. The route table is associated with the public subnet to enable internet access.

### Best Practices for IaC and GitOps

#### Self-Sufficiency and Cleanup

Creating all resources explicitly ensures that your infrastructure is self-sufficient and can be easily cleaned up. This is particularly important in a DevSecOps environment where you need to maintain a clean and secure infrastructure.

#### Version Control and Collaboration

Using Git for version control allows you to track changes, collaborate with team members, and roll back to previous versions if needed. This is crucial for maintaining a secure and reliable infrastructure.

### Real-World Examples and CVEs

#### Example: CVE-2021-20225

CVE-2021-20225 is a vulnerability in AWS IAM that could allow unauthorized access to resources. This vulnerability highlights the importance of properly configuring IAM roles and policies.

#### Secure Configuration Example

Here’s an example of a secure IAM role configuration:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:DescribeAssociation",
        "ssm:GetParameter",
        "ssm:PutParameter",
        "ssm:SendCommand"
      ],
      "Resource": "*"
    }
  ]
}
```

This policy grants minimal necessary permissions for SSM operations, reducing the risk of unauthorized access.

### How to Prevent / Defend

#### Detection

Regularly audit your IAM roles and policies to ensure they are configured correctly. Use tools like AWS Config and AWS Trusted Advisor to monitor and detect misconfigurations.

#### Prevention

- **Least Privilege**: Grant only the minimum necessary permissions required for a role.
- **IAM Policies**: Use fine-grained policies to limit access to specific resources.
- **Version Control**: Use Git for version control to track changes and roll back if needed.

#### Secure Coding Fixes

Here’s an example of a vulnerable IAM policy and its secure counterpart:

**Vulnerable Policy:**

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

**Secure Policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:DescribeAssociation",
        "ssm:GetParameter",
        "ssm:PutParameter",
        "ssm:SendCommand"
      ],
      "Resource": "*"
    }
  ]
}
```

### Hands-On Labs

For hands-on practice with IaC and GitOps, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on IaC and GitOps.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **CloudGoat**: A set of labs designed to help you learn about securing AWS environments.

These labs provide practical experience in setting up and securing infrastructure using IaC and GitOps principles.

### Conclusion

By leveraging IaC and GitOps, you can ensure that your infrastructure is consistent, secure, and easily manageable. Properly configuring IAM roles and policies, creating explicit networking resources, and using version control are key practices for maintaining a secure and reliable infrastructure.

---
<!-- nav -->
[[10-Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2|Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/12-Practice Questions & Answers|Practice Questions & Answers]]
