---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS

In this chapter, we will delve into the process of setting up a secure Infrastructure as Code (IaC) pipeline for Amazon Elastic Kubernetes Service (EKS) provisioning using GitLab OpenID Connect (OIDC) in AWS. This approach ensures that the provisioning process is automated, secure, and follows best practices for DevSecOps.

### Background Theory

#### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is the practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This allows for automation, consistency, and version control of infrastructure configurations.

#### Why Use IaC?

Using IaC provides several benefits:

- **Consistency**: Ensures that environments are consistently configured across development, testing, and production stages.
- **Automation**: Reduces manual errors and speeds up deployment processes.
- **Version Control**: Allows tracking of changes and rollbacks to previous states.
- **Reproducibility**: Makes it easy to recreate environments, which is crucial for disaster recovery and scaling.

#### What is Amazon Elastic Kubernetes Service (EKS)?

Amazon EKS is a managed service that makes it easy to run Kubernetes on AWS without needing expertise in Kubernetes orchestration. EKS supports the Kubernetes API, so you can use existing tools and plugins to interact with your cluster and applications.

### Why Automate EKS Provisioning?

Automating EKS provisioning through an IaC pipeline ensures that the cluster setup is consistent and secure. Manual provisioning often leads to inconsistencies and potential security vulnerabilities. By automating this process, we can:

- Ensure that only authorized roles have access to the cluster.
- Limit the scope of permissions to the minimum required for the task.
- Automatically enforce security policies and best practices.

### Using GitLab OIDC in AWS

GitLab OpenID Connect (OIDC) is a protocol that enables secure authentication between GitLab and AWS. This integration allows GitLab to act as an identity provider (IdP) for AWS, enabling secure access to AWS resources without the need for long-lived credentials.

#### What is OpenID Connect (OIDC)?

OpenID Connect (OIDC) is an authentication protocol built on top of OAuth 2.0. It allows clients to verify the identity of users based on the authentication performed by an authorization server, as well as to obtain basic profile information about the users.

#### Why Use GitLab OIDC?

Using GitLab OIDC in AWS provides several advantages:

- **Secure Authentication**: Eliminates the need for long-lived credentials, reducing the risk of credential theft.
- **Fine-grained Access Control**: Allows for precise control over which GitLab users or groups can access specific AWS resources.
- **Integration with CI/CD Pipelines**: Enables seamless integration with GitLab CI/CD pipelines, allowing for automated and secure provisioning of EKS clusters.

### Setting Up the Secure IaC Pipeline

To set up a secure IaC pipeline for EKS provisioning using GitLab OIDC in AWS, we need to follow these steps:

1. **Configure GitLab OIDC in AWS**.
2. **Set up Terraform for EKS provisioning**.
3. **Integrate GitLab CI/CD with Terraform**.
4. **Implement Role-Based Access Control (RBAC)**.
5. **Ensure Secure Configuration Management**.

### Step-by-Step Implementation

#### Step 1: Configure GitLab OIDC in AWS

To configure GitLab OIDC in AWS, we need to create an IAM Identity Provider and an IAM Role that trusts the GitLab OIDC provider.

##### Creating an IAM Identity Provider

First, we need to create an IAM Identity Provider that points to the GitLab OIDC endpoint.

```bash
aws iam create-open-id-connect-provider \
    --url https://gitlab.com \
    --client-id-list client_id_1,client_id_2 \
    --thumbprint-list thumbprint_1,thumbprint_2
```

##### Creating an IAM Role

Next, we create an IAM Role that trusts the GitLab OIDC provider.

```bash
aws iam create-role \
    --role-name GitLabOIDCRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": "arn:aws:iam::123456789012:oidc-provider/gitlab.com"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "gitlab:aud": "client_id_1",
                        "gitlab:sub": "user:username"
                    }
                }
            }
        ]
    }'
```

##### Attaching Policies to the IAM Role

We attach the necessary policies to the IAM Role to grant it the required permissions.

```bash
aws iam attach-role-policy \
    --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy \
    --role-name GitLabOIDCRole
```

#### Step 2: Set up Terraform for EKS Provisioning

Terraform is a popular IaC tool that allows us to define our infrastructure in code. We will use Terraform to provision an EKS cluster.

##### Initializing Terraform

First, we initialize Terraform to download the necessary providers.

```bash
terraform init
```

##### Defining the EKS Cluster

We define the EKS cluster in a `main.tf` file.

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
      }
    ]
  })
}
```

##### Applying the Terraform Configuration

We apply the Terraform configuration to create the EKS cluster.

```bash
terraform apply
```

#### Step 3: Integrate GitLab CI/CD with Terraform

To integrate GitLab CI/CD with Terraform, we need to create a `.gitlab-ci.yml` file that defines the CI/CD pipeline.

```yaml
stages:
  - validate
  - plan
  - apply

validate:
  stage: validate
  script:
    - terraform validate

plan:
  stage: plan
  script:
    - terraform plan -out=tfplan

apply:
  stage: apply
  script:
    - terraform apply tfplan
  when: manual
```

#### Step 4: Implement Role-Based Access Control (RBAC)

To ensure that only authorized roles have access to the EKS cluster, we implement RBAC.

##### Creating an IAM Policy

We create an IAM Policy that grants the necessary permissions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters"
      ],
      "Resource": "*"
    }
  ]
}
```

##### Attaching the Policy to the IAM Role

We attach the policy to the IAM Role.

```bash
aws iam attach-role-policy \
    --policy-arn arn:aws:iam::123456789012:policy/EKSPolicy \
    --role-name GitLabOIDCRole
```

#### Step 5: Ensure Secure Configuration Management

To ensure secure configuration management, we need to follow best practices such as:

- **Use Secrets Management**: Store sensitive information like credentials in a secrets manager.
- **Enable Encryption**: Enable encryption for all data at rest and in transit.
- **Audit Logs**: Enable audit logs to track all changes made to the infrastructure.

### Pitfalls and Common Mistakes

#### Pitfall 1: Using Long-Lived Credentials

Using long-lived credentials increases the risk of credential theft. Always use short-lived credentials or temporary tokens.

#### Pitfall 2: Inadequate Access Control

Inadequate access control can lead to unauthorized access to the EKS cluster. Always implement RBAC and limit permissions to the minimum required.

#### Pitfall 3: Lack of Audit Logs

Lack of audit logs makes it difficult to track changes and detect unauthorized access. Always enable audit logs and monitor them regularly.

### How to Prevent / Defend

#### Detection

- **Monitor Audit Logs**: Regularly monitor audit logs to detect any unauthorized access or suspicious activity.
- **Use Security Tools**: Use security tools like AWS CloudTrail and AWS Config to monitor and audit infrastructure changes.

#### Prevention

- **Use Short-Lived Credentials**: Use short-lived credentials or temporary tokens instead of long-lived credentials.
- **Implement RBAC**: Implement RBAC to ensure that only authorized roles have access to the EKS cluster.
- **Enable Encryption**: Enable encryption for all data at rest and in transit.

#### Secure Coding Fixes

##### Vulnerable Code

```hcl
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
      }
    ]
  })
}
```

##### Fixed Code

```hcl
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
          Federated = "arn:aws:iam::123456789012:oidc-provider/gitlab.com"
        }
        Condition = {
          StringEquals = {
            "gitlab:aud" = "client_id_1",
            "gitlab:sub"[...]

---
<!-- nav -->
[[01-Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 1|Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 1]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Using GitLab OIDC in AWS/00-Overview|Overview]] | [[03-Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS|Introduction to Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS]]
