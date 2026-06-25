---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps

### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is a practice where infrastructure is defined and managed through machine-readable files, typically written in a high-level declarative language. This approach allows developers and operations teams to manage infrastructure changes in a consistent, repeatable, and automated manner. By treating infrastructure as code, organizations can leverage version control systems, continuous integration/continuous deployment (CI/CD) pipelines, and other software development practices to improve the reliability and security of their infrastructure.

### Why Use IaC?

The primary benefits of IaC include:

- **Consistency**: Ensures that environments are consistently provisioned and configured.
- **Repeatability**: Allows for the creation of identical environments across different stages (development, testing, production).
- **Automation**: Facilitates the automation of infrastructure provisioning and management tasks.
- **Version Control**: Enables tracking of changes to infrastructure configurations using version control systems.
- **Collaboration**: Improves collaboration among team members by providing a shared repository of infrastructure definitions.

### What is GitOps?

GitOps is an operational framework that extends the principles of IaC by using Git as the single source of truth for all infrastructure and application configurations. In a GitOps workflow, infrastructure and application configurations are stored in a Git repository, and changes are made through pull requests. This approach ensures that all changes are reviewed, tested, and audited before being applied to the live environment.

### Why Use GitOps?

The primary benefits of GitOps include:

- **Auditability**: Provides a clear audit trail of all changes made to infrastructure and applications.
- **Collaboration**: Enhances collaboration among team members by leveraging Git’s pull request model.
- **Automated Rollouts**: Enables automated rollouts and rollbacks of infrastructure and application changes.
- **Security**: Improves security by ensuring that all changes are reviewed and tested before being applied.

### Real-World Example: Recent Breaches and IaC/GitOps

One notable example of the importance of IaC and GitOps is the Capital One data breach in 2019. The breach was caused by a misconfigured firewall rule, which allowed unauthorized access to customer data. This incident highlights the critical importance of properly managing infrastructure configurations and ensuring that changes are tracked and reviewed.

In a GitOps-based workflow, such misconfigurations could have been detected and prevented through automated testing and review processes. By storing infrastructure configurations in a Git repository and requiring pull requests for changes, organizations can ensure that all changes are thoroughly reviewed and tested before being applied.

### Setting Up a CI/CD Pipeline for Infrastructure Code Using GitOps Principles

To build a CI/CD pipeline for infrastructure code using GitOps principles, we need to define and manage our infrastructure configurations using IaC tools and store them in a Git repository. We will then use a CI/CD pipeline to automate the process of building, testing, and deploying infrastructure changes.

#### Step 1: Define Infrastructure Configurations Using IaC Tools

We will use Terraform, a popular IaC tool, to define our infrastructure configurations. Terraform uses a declarative language called HCL (HashiCorp Configuration Language) to describe the desired state of the infrastructure.

```hcl
provider "aws" {
  region = var.region
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

In this example, we define an AWS EC2 instance using Terraform. The `provider` block specifies the AWS provider and the region where the instance will be created. The `resource` block defines the EC2 instance with the specified AMI and instance type.

#### Step 2: Store Infrastructure Configurations in a Git Repository

We will store our Terraform configurations in a Git repository. This allows us to track changes to our infrastructure configurations and collaborate with team members using Git’s pull request model.

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <repository-url>
git push -u origin master
```

#### Step 3: Set Up Environment Variables for Terraform

Terraform automatically picks up certain environment variables, such as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`. These variables are used to authenticate and configure the AWS provider.

```bash
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_DEFAULT_REGION=us-west-2
```

By setting these environment variables, we can avoid hardcoding sensitive credentials in our Terraform configurations.

#### Step 4: Configure CI/CD Pipeline

We will use a CI/CD tool, such as Jenkins or GitHub Actions, to automate the process of building, testing, and deploying infrastructure changes. Here is an example of a GitHub Actions workflow that builds and deploys Terraform configurations:

```yaml
name: Terraform CI/CD

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Terraform
      uses: hashicorp/setup-terraform@v1

    - name: Initialize Terraform
      run: terraform init

    - name: Validate Terraform
      run: terraform validate

    - name: Plan Terraform
      run: terraform plan

    - name: Apply Terraform
      run: terraform apply -auto-approve
```

This workflow checks out the code, sets up Terraform, initializes the Terraform configuration, validates the configuration, plans the changes, and applies the changes.

### Handling Environment-Specific Variables

In addition to the environment variables that Terraform automatically picks up, we may need to set additional environment-specific variables, such as a runner registration token or an environment prefix. These variables can be set as environment variables in the CI/CD pipeline.

```bash
export RUNNER_REGISTRATION_TOKEN=your-registration-token
export ENVIRONMENT_PREFIX=prod
```

Alternatively, we can set these variables using the `TF_VAR_` prefix, which is recognized by Terraform.

```bash
export TF_VAR_runner_registration_token=your-registration-token
export TF_VAR_environment_prefix=prod
```

### How to Prevent / Defend

#### Detection

To detect misconfigurations and vulnerabilities in your infrastructure, you can use tools such as Terraform Validate, which checks for syntax errors and logical issues in your Terraform configurations.

```bash
terraform validate
```

Additionally, you can use security scanning tools, such as Trivy or tfsec, to scan your Terraform configurations for security vulnerabilities.

```bash
trivy iac .
tfsec .
```

#### Prevention

To prevent misconfigurations and vulnerabilities, you should follow best practices for managing infrastructure configurations:

- **Use Version Control**: Store your infrastructure configurations in a Git repository to track changes and collaborate with team members.
- **Automate Testing**: Use a CI/CD pipeline to automate the process of building, testing, and deploying infrastructure changes.
- **Use Secure Defaults**: Configure your infrastructure with secure defaults, such as disabling unnecessary services and enabling encryption.
- **Limit Permissions**: Limit the permissions of your infrastructure configurations to the minimum required to perform their functions.
- **Review Changes**: Require pull requests for changes to your infrastructure configurations to ensure that all changes are thoroughly reviewed and tested.

#### Secure Coding Fixes

Here is an example of a vulnerable Terraform configuration and the corresponding secure configuration:

**Vulnerable Configuration**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl    = "public-read"
}
```

**Secure Configuration**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl    = "private"
}
```

In the secure configuration, we set the ACL to `private` to prevent public access to the S3 bucket.

### Conclusion

By using IaC and GitOps principles, organizations can improve the consistency, repeatability, and security of their infrastructure configurations. By defining infrastructure configurations using IaC tools, storing them in a Git repository, and automating the process of building, testing, and deploying infrastructure changes using a CI/CD pipeline, organizations can ensure that their infrastructure is consistently provisioned and configured, and that all changes are thoroughly reviewed and tested.

### Practice Labs

For hands-on practice with IaC and GitOps, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs for learning web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning web application security.
- **CloudGoat**: A series of labs for learning cloud security concepts using AWS.
- **flaws.cloud**: A collection of labs for learning cloud security concepts using various cloud providers.
- **Pacu**: A Python-based tool for automating cloud security assessments.
- **Kubernetes Goat**: A series of labs for learning Kubernetes security concepts.
- **OWASP WrongSecrets**: A series of challenges for learning cryptography and secure coding concepts.
- **kube-hunter**: A tool for discovering and exploiting security vulnerabilities in Kubernetes clusters.

These labs provide practical experience with IaC and GitOps principles and help reinforce the concepts learned in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Build CICD Pipeline for Infrastructure Code using GitOps Principles/03-Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 1|Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 1]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Build CICD Pipeline for Infrastructure Code using GitOps Principles/00-Overview|Overview]] | [[05-Introduction to Infrastructure as Code (IaC) and GitOps Part 1|Introduction to Infrastructure as Code (IaC) and GitOps Part 1]]
