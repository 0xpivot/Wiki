---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Secure IaC Pipeline for EKS Provisioning Using Terraform

### Introduction to Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is a method of managing and provisioning computing resources through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows infrastructure to be treated like software, enabling developers to manage and provision resources in a consistent, repeatable manner. One of the most popular tools for IaC is Terraform, which allows you to define your infrastructure in declarative configuration files.

### Terraform Configuration for EKS Provisioning

In the context of provisioning Amazon Elastic Kubernetes Service (EKS), Terraform can be used to automate the creation and management of EKS clusters and associated resources. The process involves defining the desired state of your infrastructure in Terraform configuration files and then applying those configurations to create or update the actual infrastructure.

#### Removing Placeholder Commands

When setting up a Terraform-based pipeline for EKS provisioning, you might start with a placeholder command such as `echo "Placeholder command"`. This placeholder is typically used during initial setup or testing phases. Once you are ready to proceed with the actual Terraform commands, you should remove this placeholder and replace it with the appropriate Terraform commands.

```bash
# Remove the placeholder command
sed -i '/echo "Placeholder command"/d' script.sh
```

#### Executing Terraform Plan Command

The next step is to execute the `terraform plan` command, which generates an execution plan that outlines the changes Terraform will make to achieve the desired state. This plan is saved as an artifact for the deployment stage.

```bash
# Execute the Terraform plan command
terraform plan -out=tfplan
```

This command creates a file named `tfplan`, which contains the detailed plan of actions Terraform will take.

### Saving the Artifact

After generating the plan, you need to save this artifact for later use in the deployment stage. This ensures that the exact plan is executed consistently across different environments.

```bash
# Save the generated plan as an artifact
cp tfplan ./artifacts/
```

### Repeating the Configuration

To ensure consistency and avoid errors, it is often necessary to repeat the same configuration steps in different parts of the pipeline. This repetition helps maintain uniformity and reduces the likelihood of human error.

```bash
# Repeat the configuration steps
terraform init
terraform validate
terraform plan -out=tfplan
```

### Choosing the Right Docker Image

For the build stage of the pipeline, you need a Docker image that includes both the AWS CLI and Terraform. This ensures that the container can execute both AWS and Terraform commands seamlessly.

#### AWS CLI Image with Terraform Installed

One approach is to use an AWS CLI image and install Terraform on top of it. This can be done by creating a custom Dockerfile.

```Dockerfile
# Use the official AWS CLI image as the base
FROM amazon/aws-cli:latest

# Install Terraform
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://releases.hashicorp.com/terraform/1.0.0/terraform_1.0.0_linux_amd64.zip && \
    unzip terraform_1.0.0_linux_amd64.zip -d /usr/local/bin/ && \
    rm terraform_1.0.0_linux_amd64.zip
```

#### Terraform Official Image with AWS CLI Installed

Alternatively, you can use the official Terraform image and install the AWS CLI on top of it.

```Dockerfile
# Use the official Terraform image as the base
FROM hashicorp/terraform:light

# Install AWS CLI
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install awscli --upgrade
```

### Using Specific Tags for Docker Images

It is a best practice to use specific tags for Docker images rather than the `latest` tag. This ensures that you are using a known, stable version of the image, reducing the risk of unexpected behavior due to changes in the image.

```bash
# Pull the specific tagged image
docker pull hashicorp/terraform:1.0.0
```

### Real-World Example: CVE-2021-21277

A real-world example of the importance of using specific tags is the CVE-2021-21277 vulnerability in the AWS CLI. This vulnerability allowed unauthorized access to sensitive data due to insecure handling of credentials. By using a specific tag, you can ensure that you are using a version of the AWS CLI that has been patched for this vulnerability.

### How to Prevent / Defend

#### Detection

To detect potential issues with your IaC pipeline, you can use tools like `tfsec` to scan your Terraform configuration files for security vulnerabilities.

```bash
# Install tfsec
go get github.com/tfsec/tfsec/cmd/tfsec

# Scan the Terraform configuration
tfsec .
```

#### Prevention

To prevent security issues, follow these best practices:

1. **Use Specific Tags**: Always use specific tags for Docker images to avoid unexpected changes.
2. **Secure Credential Management**: Use AWS Secrets Manager or HashiCorp Vault to securely manage credentials.
3. **Least Privilege Principle**: Ensure that the AWS CLI and Terraform have only the minimum permissions required to perform their tasks.

#### Secure-Coding Fixes

Here is an example of a vulnerable Terraform configuration and its secure counterpart:

**Vulnerable Configuration**

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
}
```

**Secure Configuration**

```hcl
provider "aws" {
  region = "us-west-2"
  profile = "readonly"
}

resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl = "private"
}
```

### Complete Example

Here is a complete example of a Terraform configuration for EKS provisioning, including the necessary AWS and Terraform commands.

#### Terraform Configuration File

```hcl
provider "aws" {
  region = "us-west-2"
  profile = "readonly"
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn
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

#### Full HTTP Request and Response

Here is an example of a full HTTP request and response for executing the Terraform plan command.

**HTTP Request**

```http
POST /api/v1/jobs HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "job": {
    "name": "terraform-plan",
    "steps": [
      {
        "name": "execute-terraform-plan",
        "commands": [
          "terraform init",
          "terraform validate",
          "terraform plan -out=tfplan"
        ]
      }
    ]
  }
}
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "job": {
    "id": "12345",
    "status": "success",
    "output": "Terraform plan executed successfully."
  }
}
```

### Common Pitfalls

1. **Using Latest Tag**: Always use specific tags for Docker images to avoid unexpected changes.
2. **Insecure Credential Handling**: Ensure that credentials are managed securely using tools like AWS Secrets Manager or HashiCorp Vault.
3. **Insufficient Permissions**: Ensure that the AWS CLI and Terraform have only the minimum permissions required to perform their tasks.

### Conclusion

By following the best practices outlined in this chapter, you can ensure that your IaC pipeline for EKS provisioning is secure and reliable. Using specific tags for Docker images, securing credential management, and adhering to the least privilege principle are key steps in achieving this goal.

### Practice Labs

For hands-on practice with secure IaC pipelines for EKS provisioning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including IaC.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A Kubernetes-themed security challenge platform.
- **AWS Well-Architected Labs**: Provides guided labs for building secure and compliant AWS environments.

These labs provide practical experience in implementing secure IaC pipelines and can help solidify your understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[11-Secure IaC Pipeline for EKS Provisioning Using Terraform Part 1|Secure IaC Pipeline for EKS Provisioning Using Terraform Part 1]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/00-Overview|Overview]] | [[13-State Management in Terraform|State Management in Terraform]]
