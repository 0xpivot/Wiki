---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure IaC Pipeline for EKS Provisioning

In the realm of DevSecOps, Infrastructure as Code (IaC) plays a pivotal role in ensuring that infrastructure is managed and provisioned in a consistent, repeatable, and secure manner. This chapter focuses on configuring a secure IaC pipeline for Amazon Elastic Kubernetes Service (EKS) provisioning using GitLab as the Continuous Integration/Continuous Deployment (CI/CD) platform. Specifically, we will delve into setting up authentication with GitLab as an Identity Provider (IdP) for AWS.

### Background Theory

#### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is a practice of managing and provisioning computing infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows for version control, automated testing, and continuous integration/continuous deployment (CI/CD) practices to be applied to infrastructure management.

#### Why Use IaC?

Using IaC offers several benefits:
- **Consistency**: Ensures that environments are consistently deployed across development, testing, and production stages.
- **Repeatability**: Allows for the same infrastructure to be deployed multiple times without manual intervention.
- **Version Control**: Infrastructure changes can be tracked and rolled back if necessary.
- **Automation**: Facilitates automation of infrastructure provisioning and management tasks.

#### What is Amazon Elastic Kubernetes Service (EKS)?

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing expertise in Kubernetes cluster setup and management. EKS supports open-source Kubernetes applications and is compatible with all Kubernetes tools.

### Setting Up the Pipeline

To set up a secure IaC pipeline for EKS provisioning, we need to configure GitLab to authenticate with AWS using temporary credentials. This ensures that GitLab does not require permanent access to AWS resources, thereby enhancing security.

#### Step 1: Establish Connection Between GitLab and AWS

The first step is to establish a connection between GitLab and AWS. This involves obtaining temporary credentials from AWS that GitLab can use to authenticate and execute Terraform scripts.

##### Using AWS CLI Image

We will use the AWS Command Line Interface (CLI) to interact with AWS services. The AWS CLI provides a way to manage AWS services using commands from the terminal.

```yaml
image: amazon/aws-cli:latest
```

This configuration specifies the use of the latest version of the AWS CLI Docker image.

##### Creating a Job in GitLab

Next, we create a job in GitLab to establish the connection. We will name this job `build`.

```yaml
stages:
  - build

build:
  stage: build
  image: amazon/aws-cli:latest
  script:
    - echo "Connecting to AWS..."
```

This job uses the AWS CLI image and includes a simple `echo` command as a placeholder.

### Detailed Steps for Establishing the Connection

#### Configuring AWS CLI

Before we proceed, ensure that the AWS CLI is properly configured. This involves setting up AWS credentials and configuring the default region.

```sh
aws configure
```

This command prompts you to enter your AWS Access Key ID, Secret Access Key, default region name, and default output format.

#### Retrieving Temporary Credentials

To retrieve temporary credentials, we use the AWS Security Token Service (STS). STS allows you to request temporary security credentials for AWS Identity and Access Management (IAM) users or roles.

```sh
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/example-role --role-session-name ExampleSession
```

This command assumes the specified IAM role and returns temporary credentials.

#### Storing Temporary Credentials

The temporary credentials returned by STS include an Access Key ID, Secret Access Key, and a Session Token. These credentials are valid for a limited time and should be stored securely.

```json
{
  "Credentials": {
    "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "SessionToken": "AQoDYXdzEJr...EXAMPLE...",
    "Expiration": "2023-10-10T12:34:56Z"
  }
}
```

These credentials can be stored in environment variables or passed directly to the Terraform commands.

### Terraform Configuration

Once the connection is established, we can proceed to configure Terraform to use the temporary credentials.

#### Initializing Terraform

First, initialize Terraform to download the necessary providers and modules.

```sh
terraform init
```

#### Applying Terraform Configuration

Next, apply the Terraform configuration to provision the EKS cluster.

```sh
terraform plan
terraform apply
```

### Mermaid Diagrams

#### Pipeline Topology

A mermaid diagram can help visualize the pipeline topology.

```mermaid
graph TD
  A[GitLab] --> B[AWS CLI]
  B --> C[Assume Role]
  C --> D[Terraform Plan]
  D --> E[Terraform Apply]
  E --> F[EKS Cluster]
```

### Real-World Examples

#### Recent Breaches

One notable breach involving misconfigured IAM roles was the Capital One data breach in 2019. The attacker exploited a misconfigured web application firewall to gain unauthorized access to sensitive data.

#### Secure Coding Practices

To prevent such breaches, follow these secure coding practices:

1. **Least Privilege Principle**: Ensure that IAM roles have the minimum necessary permissions.
2. **Temporary Credentials**: Use temporary credentials instead of permanent access keys.
3. **Regular Audits**: Regularly audit IAM roles and policies to identify and mitigate potential risks.

### How to Prevent / Defend

#### Detection

Use AWS CloudTrail to log API calls made to AWS services. Monitor CloudTrail logs for suspicious activity.

```sh
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRole
```

#### Prevention

1. **IAM Policies**: Define strict IAM policies that limit access to specific resources.
2. **MFA**: Enable Multi-Factor Authentication (MFA) for IAM users.
3. **Rotation**: Rotate access keys and secret keys regularly.

#### Secure-Coding Fixes

Compare the insecure and secure versions of IAM policies.

**Insecure Policy**
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

**Secure Policy**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:*",
        "ec2:*",
        "iam:GetRole",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

### Complete Example

#### Full Pipeline Configuration

Here is a complete example of the GitLab CI/CD pipeline configuration.

```yaml
image: amazon/aws-cli:latest

stages:
  - build
  - deploy

variables:
  AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
  AWS_SESSION_TOKEN: $AWS_SESSION_TOKEN

build:
  stage: build
  script:
    - echo "Connecting to AWS..."
    - aws sts assume-role --role-arn arn:aws:iam::123456789012:role/example-role --role-session-name ExampleSession > temp_credentials.json
    - export AWS_ACCESS_KEY_ID=$(jq -r '.Credentials.AccessKeyId' temp_credentials.json)
    - export AWS_SECRET_ACCESS_KEY=$(jq -r '.Credentials.SecretAccessKey' temp_credentials.json)
    - export AWS_SESSION_TOKEN=$(jq -r '.Credentials.SessionToken' temp_credentials.json)

deploy:
  stage: deploy
  script:
    - terraform init
    - terraform plan
    - terraform apply --auto-approve
```

### Conclusion

By following the steps outlined in this chapter, you can set up a secure IaC pipeline for EKS provisioning using GitLab as the CI/CD platform. This approach ensures that your infrastructure is managed in a consistent, repeatable, and secure manner, reducing the risk of security breaches and improving overall system reliability.

### Practice Labs

For hands-on practice, consider the following labs:
- **PortSwigger Web Security Academy**: Offers comprehensive training on web security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.
- **WebGoat**: An interactive web application designed to teach web application security lessons.

These labs provide practical experience in setting up and securing IaC pipelines, helping you master the skills required for DevSecOps.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Configure Authentication with GitLab Identity Provider/00-Overview|Overview]] | [[02-Configuring Authentication with GitLab Identity Provider for EKS Provisioning Part 1|Configuring Authentication with GitLab Identity Provider for EKS Provisioning Part 1]]
