---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure IaC Pipeline for EKS Provisioning

In the realm of DevSecOps, Infrastructure as Code (IaC) plays a pivotal role in ensuring that infrastructure is managed and deployed in a consistent, repeatable manner. One of the most popular tools for IaC is Terraform, which allows developers and operations teams to define and provision infrastructure using declarative configuration files. In this chapter, we will delve into the process of setting up a secure IaC pipeline for Amazon Elastic Kubernetes Service (EKS) provisioning using Terraform.

### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is a practice where infrastructure is defined and managed using code rather than physical hardware configurations. This approach enables teams to manage infrastructure in a version-controlled manner, making it easier to track changes, collaborate, and automate deployments. Terraform is one of the leading tools used for IaC, providing a robust framework for defining and deploying infrastructure across various cloud providers.

### Why Use Terraform for EKS Provisioning?

Terraform is particularly well-suited for provisioning EKS clusters because it provides a declarative way to define and manage Kubernetes infrastructure. By using Terraform, you can ensure that your EKS cluster is consistently deployed and configured across different environments. Additionally, Terraform integrates seamlessly with AWS, allowing you to leverage the full range of AWS services and features.

### Overview of the EKS Provisioning Process

The process of provisioning an EKS cluster using Terraform involves several key steps:

1. **Define the Infrastructure**: Write Terraform configuration files to define the desired state of your EKS cluster.
2. **Initialize Terraform**: Set up the necessary plugins and providers required to interact with AWS.
3. **Plan the Deployment**: Review the proposed changes to your infrastructure before applying them.
4. **Apply the Configuration**: Deploy the defined infrastructure to AWS.
5. **Integrate with CI/CD Pipeline**: Automate the deployment process by integrating Terraform with a CI/CD pipeline.

### Example Terraform Configuration for EKS Cluster

Let's start by looking at a basic Terraform configuration for an EKS cluster. Below is an example of how you might define an EKS cluster using Terraform:

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

This configuration defines an EKS cluster named `example-cluster` in the `us-west-2` region. It also creates an IAM role that the EKS cluster will assume.

### Integrating with a CI/CD Pipeline

To ensure that changes to the Terraform configuration are applied automatically, you can integrate Terraform with a CI/CD pipeline. This integration ensures that any changes pushed to the repository trigger a pipeline that updates the AWS infrastructure.

#### Example CI/CD Pipeline Configuration

Here is an example of a GitLab CI/CD pipeline configuration that triggers a Terraform apply when changes are pushed to the repository:

```yaml
stages:
  - validate
  - plan
  - apply

validate:
  stage: validate
  script:
    - terraform init
    - terraform validate

plan:
  stage: plan
  script:
    - terraform init
    - terraform plan -out=tfplan

apply:
  stage: apply
  script:
    - terraform init
    - terraform apply -auto-approve tfplan
  when: manual
```

This pipeline includes three stages: `validate`, `plan`, and `apply`. The `validate` stage initializes Terraform and validates the configuration. The `plan` stage generates a plan file (`tfplan`) that outlines the changes to be made. Finally, the `apply` stage applies the changes to the AWS infrastructure.

### How to Prevent / Defend

#### Detection

To detect unauthorized changes to your infrastructure, you can set up monitoring and alerting mechanisms. AWS CloudTrail can be used to log API calls made to your AWS account, including those made by Terraform. You can configure CloudTrail to send logs to Amazon S3 and set up alerts using Amazon CloudWatch.

#### Prevention

To prevent unauthorized changes, you can implement strict access controls and least privilege principles. Ensure that only authorized users have the necessary permissions to modify the Terraform configuration and trigger the CI/CD pipeline. You can also use AWS Identity and Access Management (IAM) policies to restrict access to specific resources.

#### Secure Coding Fixes

Below is an example of a vulnerable Terraform configuration and its secure counterpart:

**Vulnerable Configuration:**

```hcl
resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "*"
        }
      },
    ]
  })
}
```

**Secure Configuration:**

```hcl
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

In the secure configuration, the `Principal` field is restricted to the `eks.amazonaws.com` service, preventing unauthorized services from assuming the role.

### Real-World Examples and Recent Breaches

Recent breaches involving misconfigured infrastructure highlight the importance of secure IaC practices. For example, the 2021 SolarWinds breach involved attackers exploiting a supply chain vulnerability to compromise multiple organizations. While this breach did not directly involve Terraform, it underscores the importance of securing your infrastructure and ensuring that only authorized changes are made.

### Conclusion

In this chapter, we have explored the process of setting up a secure IaC pipeline for EKS provisioning using Terraform. We covered the basics of IaC, the benefits of using Terraform for EKS, and provided a detailed example of a Terraform configuration and CI/CD pipeline. We also discussed how to prevent and detect unauthorized changes to your infrastructure and provided secure coding fixes for common vulnerabilities.

### Practice Labs

For hands-on experience with secure IaC pipelines for EKS provisioning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including IaC.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes.
- **CloudGoat**: A series of labs designed to help you learn about AWS security best practices.

These labs provide practical experience in setting up and securing IaC pipelines for EKS provisioning.

---

This chapter aims to provide a comprehensive understanding of setting up a secure IaC pipeline for EKS provisioning using Terraform. By following the steps outlined and implementing the best practices discussed, you can ensure that your infrastructure is consistently deployed and securely managed.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/02-Introduction to Secure IaC Pipeline for EKS Provisioning Part 2|Introduction to Secure IaC Pipeline for EKS Provisioning Part 2]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/00-Overview|Overview]] | [[04-Introduction to Secure IaC Pipeline for EKS Provisioning|Introduction to Secure IaC Pipeline for EKS Provisioning]]
