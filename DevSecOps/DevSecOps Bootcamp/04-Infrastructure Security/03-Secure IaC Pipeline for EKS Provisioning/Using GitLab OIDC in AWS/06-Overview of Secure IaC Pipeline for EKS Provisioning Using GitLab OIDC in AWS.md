---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Overview of Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS

In this section, we will delve into the process of creating a secure Infrastructure as Code (IaC) pipeline for provisioning Amazon Elastic Kubernetes Service (EKS) clusters using GitLab and OpenID Connect (OIDC). We will cover the entire workflow, including setting up a basic pipeline for a Terraform project, connecting to AWS, and ensuring secure access through roles and trust policies.

### Basic Pipeline for Terraform Project

The first step is to set up a basic pipeline for a Terraform project. Terraform is an infrastructure-as-code tool that allows you to define and provision your infrastructure using declarative configuration files. In this context, we will use Terraform to manage the provisioning of EKS clusters and other AWS resources.

#### Connecting to AWS Using Terraform

To connect to AWS using Terraform, you need to provide AWS credentials. These credentials are used to authenticate and authorize actions within the AWS environment. Typically, these credentials consist of an Access Key ID and a Secret Access Key.

```plaintext
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

However, hardcoding these credentials directly into your pipeline is highly insecure. This approach exposes sensitive information and makes it susceptible to unauthorized access and misuse.

### Using Roles for Secure Access

Instead of using hard-coded credentials, we will leverage AWS Identity and Access Management (IAM) roles. IAM roles allow you to grant permissions to entities that need temporary access to AWS resources. By using roles, you can ensure that your pipeline has the necessary permissions without exposing sensitive credentials.

#### Creating a GitLabCI Role in AWS

We will create an IAM role specifically for GitLab CI. This role will have the necessary permissions to interact with AWS resources, such as creating and managing EKS clusters.

```bash
aws iam create-role --role-name GitLabCI --assume-role-policy-document file://trust-policy.json
```

Here, `trust-policy.json` is a JSON file that defines the trust policy for the role. This policy specifies which entities are allowed to assume the role.

#### Defining a Trust Policy

A trust policy is a JSON document that specifies the conditions under which an entity can assume a role. In our case, we need to define a trust policy that allows GitLab CI to assume the role.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:gitlabci/repo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

This trust policy allows GitLab CI to assume the role based on the OIDC provider and specific conditions.

### Understanding OpenID Connect (OIDC)

OpenID Connect (OIDC) is an authentication protocol built on top of OAuth 2.0. It provides a way to authenticate users and obtain information about them in a secure manner. In our context, OIDC allows GitLab CI to authenticate with AWS and assume the role.

#### How OIDC Works

When GitLab CI runs a pipeline, it uses an OIDC token to authenticate with AWS. This token contains claims that identify the pipeline and its permissions. AWS verifies the token and allows the pipeline to assume the role specified in the trust policy.

### Setting Up the Pipeline

Now that we have the IAM role and trust policy set up, we can configure the GitLab CI pipeline to use these settings.

#### Example `.gitlab-ci.yml` Configuration

Here is an example of a `.gitlab-ci.yml` file that sets up the pipeline:

```yaml
stages:
  - build
  - deploy

variables:
  AWS_ROLE_ARN: arn:aws:iam::123456789012:role/GitLabCI
  AWS_WEB_IDENTITY_TOKEN_FILE: /tmp/aws-web-identity-token-file

build:
  stage: build
  script:
    - echo "Building the application..."
    - terraform init
    - terraform validate

deploy:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - terraform plan
    - terraform apply --auto-approve
  before_script:
    - curl -o $AWS_WEB_IDENTITY_TOKEN_FILE https://gitlab-ci-token.s3.amazonaws.com/oidc-token
    - export AWS_ACCESS_KEY_ID=$(aws sts assume-role-with-web-identity --role-arn $AWS_ROLE_ARN --web-identity-token-file $AWS_WEB_IDENTITY_TOKEN_FILE --role-session-name gitlabci | jq -r '.Credentials.AccessKeyId')
    - export AWS_SECRET_ACCESS_KEY=$(aws sts assume-role-with-web-identity --role-arn $AWS_ROLE_
```

### Explanation of the Pipeline Configuration

Let's break down the pipeline configuration step by step:

1. **Stages**: Define the stages of the pipeline (`build` and `deploy`).
2. **Variables**: Set the `AWS_ROLE_ARN` and `AWS_WEB_IDENTITY_TOKEN_FILE` variables.
3. **Build Stage**: Initialize and validate the Terraform configuration.
4. **Deploy Stage**: Plan and apply the Terraform changes.
5. **Before Script**: Obtain the OIDC token and assume the role using the `aws sts assume-role-with-web-identity` command.

### Full Raw HTTP Messages

Here is an example of the full raw HTTP messages involved in the OIDC authentication process:

#### Request

```http
GET /oidc-token HTTP/1.1
Host: gitlab-ci-token.s3.amazonaws.com
Authorization: Bearer <oidc_token>
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Length: 123

{
  "access_token": "<access_token>",
  "expires_in": 3600,
  "refresh_token": "<refresh_token>",
  "token_type": "Bearer"
}
```

### Mermaid Diagrams

#### Trust Policy Diagram

```mermaid
graph TD
  A[GitLab CI] -->|OIDC Token| B[AWS]
  B -->|Assume Role| C[IAM Role]
  C -->|Permissions| D[AWS Resources]
```

#### Pipeline Flow Diagram

```mermaid
graph TD
  A[Build Stage] --> B[Terraform Init]
  B --> C[Terraform Validate]
  C --> D[Deploy Stage]
  D --> E[Obtain OIDC Token]
  E --> F[Assume IAM Role]
  F --> G[Terraform Plan]
  G --> H[Terraform Apply]
```

### Common Pitfalls and How to Prevent Them

#### Hardcoded Credentials

**Problem**: Exposing hardcoded credentials in the pipeline configuration.

**Solution**: Use IAM roles and trust policies to securely manage access.

#### Insufficient Permissions

**Problem**: Granting excessive permissions to the IAM role.

**Solution**: Follow the principle of least privilege and grant only the necessary permissions.

#### Incorrect Trust Policy

**Problem**: Misconfiguring the trust policy, leading to unauthorized access.

**Solution**: Carefully review and test the trust policy to ensure it meets the required conditions.

### Real-World Examples

#### Recent Breaches

- **Example 1**: A breach occurred due to hardcoded AWS credentials in a CI/CD pipeline. The attacker gained access to sensitive resources and exfiltrated data.
- **Example 2**: An organization experienced unauthorized access to their AWS environment because of misconfigured IAM roles and trust policies.

### How to Prevent / Defend

#### Detection

- **Monitor IAM Role Usage**: Use AWS CloudTrail to monitor the usage of IAM roles and detect any suspicious activity.
- **Audit Logs**: Regularly audit logs to identify any unauthorized access attempts.

#### Prevention

- **Use IAM Roles**: Always use IAM roles instead of hardcoded credentials.
- **Least Privilege Principle**: Grant only the necessary permissions to IAM roles.
- **Regular Audits**: Perform regular audits of IAM roles and trust policies to ensure they are correctly configured.

#### Secure Coding Fixes

**Vulnerable Code**

```yaml
variables:
  AWS_ACCESS_KEY_ID: AKIAIOSFODNN7EXAMPLE
  AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Secure Code**

```yaml
variables:
  AWS_ROLE_ARN: arn:aws:iam::123456789012:role/GitLabCI
  AWS_WEB_IDENTITY_TOKEN_FILE: /tmp/aws-web-identity-token-file
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in securing IaC pipelines and managing AWS resources securely.

By following this comprehensive guide, you will be well-equipped to set up a secure IaC pipeline for EKS provisioning using GitLab and OIDC in AWS.

---
<!-- nav -->
[[05-Overview of Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 1|Overview of Secure IaC Pipeline for EKS Provisioning Using GitLab OIDC in AWS Part 1]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Using GitLab OIDC in AWS/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Using GitLab OIDC in AWS/07-Practice Questions & Answers|Practice Questions & Answers]]
