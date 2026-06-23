---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Secure IaC Pipeline for EKS Provisioning Using Terraform

### Introduction to Infrastructure as Code (IaC)

Infrastructure as Code (IaC) is a practice that involves managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows developers and operations teams to manage infrastructure in a consistent, repeatable manner using code, which can be versioned, tested, and deployed like any other application code.

In the context of DevSecOps, IaC plays a crucial role in ensuring that infrastructure is provisioned securely and consistently across different environments. One popular tool for IaC is Terraform, which allows you to define your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL).

### Terraform Configuration Files

Terraform uses `.tf` files to define resources and their configurations. These files describe the desired state of your infrastructure, and Terraform ensures that the actual state matches the desired state. Additionally, Terraform supports variables, which allow you to parameterize your configuration files, making them more flexible and reusable.

#### Variables in Terraform

Variables in Terraform are placeholders that can be assigned values at runtime. They are defined in a `variables.tf` file and can be used throughout your Terraform configuration files. Here’s an example of defining variables:

```hcl
variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
}
```

These variables can then be referenced in your resource definitions:

```hcl
provider "aws" {
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
  region     = "us-west-2"
}
```

### Passing Variables to Terraform

There are several ways to pass variables to Terraform:

1. **TFVars File**: A `.tfvars` file contains key-value pairs that map to the variables defined in your `variables.tf` file.
2. **Command-Line Arguments**: You can pass variables directly via the command line using `-var` or `-var-file`.
3. **Environment Variables**: You can set environment variables with a `TF_VAR_` prefix, which Terraform will automatically pick up.

#### Environment Variables with TF_VAR Prefix

Using environment variables with a `TF_VAR_` prefix is a convenient way to pass sensitive information like credentials to Terraform without hardcoding them in your configuration files. This method is particularly useful in CI/CD pipelines where environment variables can be securely stored and managed.

Here’s how you can set environment variables in your shell:

```sh
export TF_VAR_aws_access_key_id="AKIAIOSFODNN7EXAMPLE"
export TF_VAR_aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

When you run `terraform apply`, Terraform will automatically pick up these environment variables and use them to populate the corresponding variables in your configuration.

### Example: Setting Up EKS with Terraform

Let’s walk through an example of setting up an Amazon Elastic Kubernetes Service (EKS) cluster using Terraform. We’ll use environment variables to pass sensitive information.

#### Step 1: Define Variables

First, define the necessary variables in `variables.tf`:

```hcl
variable "eks_cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
}
```

#### Step 2: Set Environment Variables

Set the environment variables in your shell:

```sh
export TF_VAR_eks_cluster_name="my-eks-cluster"
export TF_VAR_aws_access_key_id="AKIAIOSFODNN7EXAMPLE"
export TF_VAR_aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

#### Step 3: Define the EKS Cluster

Define the EKS cluster in `main.tf`:

```hcl
provider "aws" {
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
  region     = "us-west-2"
}

resource "aws_eks_cluster" "example" {
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = [aws_subnet.example.id]
  }
}

resource "aws_iam_role" "example" {
  name = "${var.eks_cluster_name}-role"

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

#### Step 4: Apply the Configuration

Run `terraform init` to initialize the Terraform working directory and then `terraform apply` to create the EKS cluster:

```sh
terraform init
terraform apply
```

### Handling Feature Branches in CI/CD Pipelines

In CI/CD pipelines, it’s common to work with feature branches. When using environment variables, ensure that the variables are available in all branches, including feature branches.

#### Example: GitLab CI/CD Settings

In GitLab CI/CD settings, you can configure environment variables that are available to all jobs in your pipeline. To make sure these variables are available in feature branches, you should uncheck the option that restricts variables to protected branches.

Here’s how you can set up environment variables in GitLab CI/CD:

1. Go to your project’s settings.
2. Navigate to `CI/CD` > `Variables`.
3. Add your environment variables with the `TF_VAR_` prefix.
4. Uncheck the box that restricts these variables to protected branches.

This ensures that the variables are available in all branches, including feature branches.

### Security Considerations

While using environment variables with the `TF_VAR_` prefix is convenient, it’s important to handle sensitive information securely. Here are some best practices:

1. **Use Secure Storage**: Store sensitive information like access keys and secrets in a secure storage solution like AWS Secrets Manager or HashiCorp Vault.
2. **Limit Exposure**: Ensure that environment variables are only exposed in the necessary environments and not hardcoded in your configuration files.
3. **Least Privilege Principle**: Assign the least privilege necessary to the roles and users involved in the provisioning process.

### How to Prevent / Defend

#### Detection

To detect misconfigurations or unauthorized access, you can use tools like AWS CloudTrail and AWS Config. These services provide detailed logs and compliance checks that can help you identify and remediate issues.

#### Prevention

1. **Secure Variable Management**: Use secure variable management solutions like HashiCorp Vault or AWS Secrets Manager to store and manage sensitive information.
2. **IAM Role Policies**: Ensure that IAM roles have the least privilege necessary to perform their tasks. Regularly review and audit IAM policies to ensure they remain secure.
3. **Automated Compliance Checks**: Use tools like AWS Config and AWS Trusted Advisor to automate compliance checks and ensure that your infrastructure adheres to best practices.

#### Secure Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```hcl
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  region     = "us-west-2"
}
```

**Secure Configuration:**

```hcl
provider "aws" {
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
  region     = "us-west-2"
}
```

With the secure configuration, sensitive information is passed via environment variables, reducing the risk of exposure.

### Conclusion

Using Terraform with environment variables is a powerful way to manage and provision infrastructure securely and consistently. By following best practices and using secure variable management solutions, you can ensure that your infrastructure remains secure throughout its lifecycle.

### Practice Labs

For hands-on experience with Terraform and EKS provisioning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including IaC and Kubernetes.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which can be deployed using Terraform.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster designed for security testing and learning.

These labs provide practical experience in setting up and securing infrastructure using Terraform and other DevSecOps tools.

---
<!-- nav -->
[[10-Real-World Examples and CVEs|Real-World Examples and CVEs]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/00-Overview|Overview]] | [[12-Secure IaC Pipeline for EKS Provisioning Using Terraform|Secure IaC Pipeline for EKS Provisioning Using Terraform]]
