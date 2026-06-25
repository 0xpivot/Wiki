---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Terraform Configuration for EKS Provisioning

### Background Theory

Infrastructure as Code (IaC) is a practice of managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. Terraform is one of the most popular IaC tools, allowing users to define and provision complex cloud infrastructures using declarative configuration files written in the HashiCorp Configuration Language (HCL).

Elastic Kubernetes Service (EKS) is a managed Kubernetes service provided by Amazon Web Services (AWS). It allows users to run Kubernetes clusters in the AWS cloud without having to manage the underlying infrastructure. To provision an EKS cluster using Terraform, we need to define the necessary resources in our Terraform configuration files.

### Setting Up the Environment

Before we can start provisioning an EKS cluster with Terraform, we need to ensure that our environment is properly set up. This includes installing the AWS Command Line Interface (CLI) and configuring access credentials.

#### Installing AWS CLI

The AWS CLI is a powerful tool that allows us to interact with AWS services from the command line. To install the AWS CLI, we can use the following commands:

```bash
pip install awscli --upgrade --user
```

This command installs the latest version of the AWS CLI using `pip`, the Python package installer. The `--user` flag ensures that the installation is done in the user's home directory, avoiding potential permission issues.

#### Establishing Connection with AWS

Once the AWS CLI is installed, we need to configure it with our AWS access credentials. This can be done using the `aws configure` command:

```bash
aws configure
```

When prompted, enter your AWS Access Key ID and Secret Access Key. These credentials are used to authenticate with AWS and grant access to the required services.

### Terraform Configuration

Now that our environment is set up, we can proceed to create the Terraform configuration for provisioning an EKS cluster.

#### Example Terraform Configuration

Here is an example of a Terraform configuration file (`main.tf`) for provisioning an EKS cluster:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn
  vpc_config {
    subnet_ids = [aws_subnet.example.id]
  }
}

resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}
```

In this configuration, we define an AWS provider with the desired region. We then create an EKS cluster resource and an IAM role resource. The IAM role is assumed by the EKS service to manage the cluster.

### Pipeline Stages and Jobs

To automate the provisioning process, we can set up a CI/CD pipeline using a tool like Jenkins or GitLab CI. Each stage in the pipeline corresponds to a specific task, such as building and deploying the infrastructure.

#### Build Job

The build job is responsible for initializing the Terraform configuration and creating the necessary resources. Here is an example of a build job script:

```bash
#!/bin/bash

# Install AWS CLI
pip install awscli --upgrade --user

# Configure AWS CLI
aws configure <<EOF
AKIAIOSFODNN7EXAMPLE
wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
us-west-2
json
EOF

# Initialize Terraform
terraform init

# Apply Terraform configuration
terraform apply -auto-approve
```

This script installs the AWS CLI, configures it with the provided credentials, initializes the Terraform configuration, and applies the changes.

#### Deploy Job

The deploy job is similar to the build job but is executed in a separate environment. Here is an example of a deploy job script:

```bash
#!/bin/bash

# Install AWS CLI
pip install awscli --upgrade --user

# Configure AWS CLI
aws configure <<EOF
AKIAIOSFODNN7EXAMPLE
wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
us-west-2
json
EOF

# Initialize Terraform
terraform init

# Apply Terra
```

### Diagrams and Topologies

To better understand the flow of the pipeline, we can use mermaid diagrams to visualize the stages and jobs.

```mermaid
graph TD
  A[Build Job] --> B[Deploy Job]
  A --> C[Install AWS CLI]
  A --> D[Configure AWS CLI]
  A --> E[Initialize Terraform]
  A --> F[Apply Terraform Configuration]
  B --> G[Install AWS CLI]
  B --> H[Configure AWS CLI]
  B --> I[Initialize Terraform]
  B --> J[Apply Terraform Configuration]
```

### Pitfalls and Common Mistakes

One common mistake is assuming that the environment variables set in one job persist across different stages. As mentioned earlier, each job runs in its own isolated environment, so any setup steps need to be repeated in each job.

Another pitfall is not properly securing the AWS credentials used in the pipeline. Exposing these credentials can lead to unauthorized access to your AWS account.

### How to Prevent / Defend

#### Detection

To detect unauthorized access to your AWS account, you can enable AWS CloudTrail and monitor the logs for suspicious activity. Additionally, you can use AWS Identity and Access Management (IAM) policies to restrict access to sensitive resources.

#### Prevention

To prevent unauthorized access, you should follow these best practices:

1. **Use IAM Roles**: Instead of using static access keys, use IAM roles to grant permissions to your EKS cluster. This ensures that the permissions are tightly controlled and can be revoked at any time.

2. **Secure Credentials**: Store your AWS credentials securely using a secrets management solution like AWS Secrets Manager or HashiCorp Vault. Avoid hardcoding credentials in your scripts or configuration files.

3. **Least Privilege Principle**: Follow the principle of least privilege by granting only the minimum permissions required to perform a task. This reduces the risk of accidental or malicious misuse of permissions.

#### Secure Coding Fixes

Here is an example of a vulnerable Terraform configuration and its secure counterpart:

**Vulnerable Configuration**

```hcl
provider "aws" {
  region = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

**Secure Configuration**

```hcl
provider "aws" {
  region = "us-west-2"
}
```

In the secure configuration, we rely on the IAM role associated with the EKS cluster to provide the necessary permissions, eliminating the need to store credentials in the configuration file.

### Real-World Examples

A recent example of a breach involving misconfigured AWS credentials is the Capital One data breach in 2019. The attacker exploited a misconfigured web application firewall rule to gain unauthorized access to the company's AWS S3 buckets, compromising sensitive customer data.

### Hands-On Labs

For hands-on practice with secure IaC pipelines for EKS provisioning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including some that touch on IaC and cloud security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which can be deployed using Terraform and EKS.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes exercises on securing IaC pipelines.

These labs provide practical experience in setting up and securing IaC pipelines for EKS provisioning, helping you to master the concepts covered in this chapter.

---
<!-- nav -->
[[13-State Management in Terraform|State Management in Terraform]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/00-Overview|Overview]] | [[15-Terraform Configuration for EKS Provisioning Part 2|Terraform Configuration for EKS Provisioning Part 2]]
