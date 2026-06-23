---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning

In this chapter, we will delve into the process of creating a secure Infrastructure as Code (IaC) pipeline to provision an Amazon Elastic Kubernetes Service (EKS) cluster using GitLab CI/CD and AWS. This setup ensures that the entire infrastructure is managed through code, providing consistency, traceability, and security. We will focus on extending secure access management from GitLab CI/CD to AWS, leveraging OpenID Connect (OIDC) for authentication and authorization.

### Background Theory

#### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is the practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This allows for automation, consistency, and version control of infrastructure configurations.

#### Why Use IaC?

- **Consistency**: Ensures that environments are consistent across development, testing, and production stages.
- **Traceability**: Every change to the infrastructure is tracked via version control systems like Git.
- **Automation**: Reduces manual errors and speeds up deployment processes.
- **Security**: Allows for better control and auditing of infrastructure changes.

### Setting Up the Environment

To set up a secure IaC pipeline for EKS provisioning, we need to ensure that GitLab CI/CD can securely interact with AWS. This involves configuring GitLab to use AWS Identity and Access Management (IAM) roles via OIDC.

#### Step-by-Step Setup

1. **Create an IAM Role in AWS**:
    - Navigate to the IAM console in the AWS Management Console.
    - Create a new role and select "Web identity" as the trusted entity type.
    - Choose "GitLab" as the provider and specify the URL of your GitLab instance.
    - Attach policies to the role that grant permissions to create and manage EKS clusters.

2. **Configure GitLab to Use OIDC**:
    - In your GitLab project, navigate to the CI/CD settings.
    - Under "Variables", add the necessary environment variables such as `AWS_ROLE_ARN` and `AWS_WEB_IDENTITY_TOKEN_FILE`.
    - Ensure that these variables are protected to prevent unauthorized access.

### Example Configuration

Here is an example of how to configure the `.gitlab-ci.yml` file to use OIDC:

```yaml
stages:
  - build
  - deploy

variables:
  AWS_ROLE_ARN: "arn:aws:iam::123456789012:role/GitLabOIDCRole"
  AWS_WEB_IDENTITY_TOKEN_FILE: "/tmp/web-identity-token"

build:
  stage: build
  script:
    - echo "Building the application..."

deploy:
  stage: deploy
  script:
    - aws sts assume-role-with-web-identity --role-arn $AWS_ROLE_ARN --role-session-name GitLabSession --web-identity-token-file $AWS_WEB_IDENTITY_TOKEN_FILE --duration-seconds 3600 > /tmp/aws_credentials
    - export AWS_ACCESS_KEY_ID=$(cat /tmp/aws_credentials | jq -r '.Credentials.AccessKeyId')
    - export AWS_SECRET_ACCESS_KEY=$(cat /tmp/aws_credentials | jq -r '.Credentials.SecretAccessKey')
    - export AWS_SESSION_TOKEN=$(cat /tmp/aws_credentials | jq -r '.Credentials.SessionToken')
    - terraform init
    - terraform apply -auto-approve
```

### Explanation of the Configuration

- **Stages**: Defines the stages of the CI/CD pipeline (`build` and `deploy`).
- **Variables**: Sets the environment variables required for AWS authentication.
- **build**: A placeholder for building the application.
- **deploy**: Uses AWS CLI to assume the role with OIDC and then runs Terraform to provision the EKS cluster.

### Real-World Examples and Recent Breaches

#### Real-World Example: Capital One Data Breach

In 2019, Capital One suffered a massive data breach due to misconfigured AWS S3 buckets. This highlights the importance of secure IaC practices to prevent such incidents. By using IaC, organizations can ensure that their infrastructure is consistently configured and audited.

#### Recent CVEs: AWS IAM Policy Misconfiguration

CVE-2021-20225 highlighted a vulnerability in AWS IAM policies where overly permissive policies could lead to unauthorized access. This underscores the need for strict access controls and secure IaC pipelines.

### Common Pitfalls and How to Avoid Them

#### Pitfall 1: Overly Permissive IAM Policies

- **What**: IAM policies that grant excessive permissions can lead to security vulnerabilities.
- **Why**: Overly permissive policies can allow unauthorized actions, leading to data breaches or unauthorized access.
- **How to Prevent**: Use least privilege principles and regularly audit IAM policies.

#### Pitfall 2: Hardcoding Secrets in IaC Files

- **What**: Storing sensitive information like API keys or passwords directly in IaC files.
- **Why**: This exposes secrets to anyone with access to the repository.
- **How to Prevent**: Use secret management tools like AWS Secrets Manager or HashiCorp Vault.

### Secure Coding Practices

#### Vulnerable Code Example

```hcl
resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = "arn:aws:iam::123456789012:role/example-role"
}
```

#### Secure Code Example

```hcl
resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = var.role_arn
}

variable "role_arn" {
  description = "The ARN of the IAM role to associate with the EKS cluster."
  type        = string
}
```

### Detection and Prevention

#### Detection

- **Use AWS Config**: Monitor changes to IAM roles and policies.
- **Enable AWS CloudTrail**: Log API calls and monitor for suspicious activity.

#### Prevention

- **Least Privilege Principle**: Grant only the minimum permissions necessary.
- **Regular Audits**: Conduct regular security audits of IAM policies and IaC files.

### Conclusion

By following the steps outlined in this chapter, you can set up a secure IaC pipeline for EKS provisioning using GitLab CI/CD and AWS. This ensures that your infrastructure is managed consistently and securely, reducing the risk of security breaches and unauthorized access.

### Practice Labs

For hands-on experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers IaC and CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **CloudGoat**: A series of labs designed to help you understand and secure AWS services.

These labs provide practical experience in setting up and securing IaC pipelines, ensuring that you can apply the concepts learned in this chapter effectively.

---
<!-- nav -->
[[03-Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS|Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Using GitLab OIDC in AWS/00-Overview|Overview]] | [[05-Overview of Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 1|Overview of Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 1]]
