---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST)

In the realm of DevSecOps, ensuring secure continuous deployment is paramount. This involves integrating security practices into the continuous integration and continuous delivery (CI/CD) pipeline. One critical aspect of this is managing access securely, particularly within cloud environments like AWS. In this chapter, we delve into the best practices for securing access to AWS using IAM roles and short-lived credentials, along with dynamic application security testing (DAST).

### Background Theory

#### IAM Roles and Short-Lived Credentials

IAM (Identity and Access Management) roles are a fundamental component of AWS security. They allow you to define permissions for users, groups, and services. IAM roles are especially useful in a CI/CD pipeline because they can be assumed by services, such as EC2 instances, to perform specific tasks without needing long-term credentials.

Short-lived credentials are temporary access keys that expire after a certain period. These are crucial for reducing the window of opportunity for an attacker to misuse stolen credentials. By using short-lived credentials, you minimize the risk associated with long-term credentials being compromised.

### Step-by-Step Mechanics

#### Creating a GitLab User Instead of Using Root Credentials

The first step in securing access is to create a dedicated GitLab user with limited permissions. This user should only have access to the necessary services and resources required for the CI/CD pipeline.

**Why This Matters:**
Using a dedicated user with limited permissions significantly reduces the potential damage if credentials are compromised. A root user, on the other hand, has full access to all resources, which could lead to catastrophic consequences if misused.

**How It Works:**
When you create a GitLab user, you assign specific permissions to that user. For example, the user might only have access to the `EC2` and `S3` services but not to `IAM` or `RDS`.

**Example:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "s3:*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Pitfalls:**
- **Overly Broad Permissions:** Ensure that the permissions assigned to the GitLab user are as narrow as possible. Overly broad permissions can still pose a significant risk.
- **Credential Exposure:** Ensure that the credentials are stored securely in the CI/CD settings of the GitLab project. Avoid hardcoding them in scripts or repositories.

#### Closing the Back Door with SSH Port

Another important step is to close the SSH port to EC2 instances and use AWS Systems Manager (SSM) for access. This eliminates the need for static SSH keys, which can be a significant security risk.

**Why This Matters:**
Static SSH keys are often stored in plain text files, making them susceptible to theft. By using SSM, you can manage access without needing to store these keys.

**How It Works:**
AWS Systems Manager allows you to manage instances without needing direct SSH access. You can run commands, install software, and manage configurations using SSM.

**Example:**
```bash
aws ssm send-command --instance-ids i-1234567890abcdef0 --document-name "AWS-RunShellScript" --parameters commands="echo Hello World"
```

**Pitfalls:**
- **SSM Configuration:** Ensure that SSM is properly configured on your EC2 instances. Misconfiguration can lead to issues with access and management.
- **IAM Permissions:** Ensure that the IAM role attached to the EC2 instance has the necessary permissions to use SSM.

### Real-World Examples

#### Recent Breaches and CVEs

Several high-profile breaches have highlighted the importance of secure access management. For example:

- **CVE-2021-26614:** This vulnerability in AWS allowed unauthorized access to S3 buckets due to misconfigured IAM policies. Ensuring that IAM roles have the least privilege necessary can help mitigate such risks.
- **SolarWinds Supply Chain Attack:** This attack involved the compromise of build pipelines, highlighting the need for secure CI/CD processes. Using dedicated users and short-lived credentials can help prevent such attacks.

### Complete Code Examples

#### IAM Role Creation

Here’s an example of creating an IAM role with limited permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "s3:GetObject"
      ],
      "Resource": "*"
    }
  ]
}
```

#### GitLab CI/CD Configuration

Here’s an example of configuring GitLab CI/CD to use the IAM role:

```yaml
stages:
  - build
  - deploy

build_job:
  stage: build
  script:
    - echo "Building the application..."
  artifacts:
    paths:
      - dist/

deploy_job:
  stage: deploy
  script:
    - aws configure set region us-east-1
    - aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabRole --role-session-name GitLabSession
    - aws s3 cp dist/ s3://my-bucket/
```

### Mermaid Diagrams

#### IAM Role and Short-Lived Credentials

```mermaid
sequenceDiagram
  participant User as GitLab User
  participant IAM as IAM Service
  participant EC2 as EC2 Instance
  participant S3 as S3 Bucket
  User->>IAM: Assume IAM Role
  IAM-->>User: Provide Temporary Credentials
  User->>EC2: Access EC2 Instance via SSM
  User->>S3: Access S3 Bucket
```

### How to Prevent / Defend

#### Detection

To detect unauthorized access, ensure that you have proper logging and monitoring in place. AWS CloudTrail and AWS Config can help track API calls and resource changes.

**Example:**
```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRole
```

#### Prevention

- **Least Privilege Principle:** Always assign the minimum necessary permissions to IAM roles.
- **Short-Lived Credentials:** Use temporary credentials that expire after a short period.
- **Monitoring and Alerts:** Set up alerts for suspicious activities using AWS CloudWatch and AWS GuardDuty.

#### Secure Coding Fixes

**Vulnerable Code:**
```yaml
deploy_job:
  stage: deploy
  script:
    - aws configure set aws_access_key_id AKIAIOSFODNN7EXAMPLE
    - aws configure set aws_secret_access_key wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    - aws s3 cp dist/ s3://my-bucket/
```

**Secure Code:**
```yaml
deploy_job:
  stage: deploy
  script:
    - aws configure set region us-east-1
    - aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabRole --role-session-name GitLabSession
    - aws s3 cp dist/ s3://my-bucket/
```

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy:** Offers exercises on secure CI/CD pipelines.
- **OWASP Juice Shop:** Provides a vulnerable web application for practicing secure deployment.
- **CloudGoat:** A series of labs designed to teach cloud security principles, including IAM roles and short-lived credentials.

By following these best practices and understanding the underlying concepts, you can significantly enhance the security of your CI/CD pipeline and protect your cloud resources.

---
<!-- nav -->
[[01-Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 1|Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 1]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/00-Overview|Overview]] | [[03-Secure Access to AWS with IAM Roles and Short-Lived Credentials|Secure Access to AWS with IAM Roles and Short-Lived Credentials]]
