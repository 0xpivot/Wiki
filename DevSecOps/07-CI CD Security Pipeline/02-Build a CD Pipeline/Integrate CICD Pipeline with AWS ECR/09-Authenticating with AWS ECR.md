---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Authenticating with AWS ECR

### Background Theory

Amazon Elastic Container Registry (ECR) is a managed Docker container registry service provided by AWS. To interact with ECR, you need to authenticate using AWS credentials. This authentication process ensures that only authorized users can push and pull images from the registry.

### Why Authenticate with AWS ECR?

Authenticating with ECR is essential for several reasons:
1. **Security**: Ensures that only authorized users can access the registry.
2. **Access Control**: Allows you to manage who can push and pull images based on IAM roles and policies.
3. **Integration**: Facilitates seamless integration with other AWS services, such as ECS and EKS.

### How to Authenticate with AWS ECR

To authenticate with ECR, you need to use the AWS Command Line Interface (CLI). The CLI provides a convenient way to obtain temporary credentials that can be used to authenticate with ECR.

#### Step-by-Step Process

1. **Install AWS CLI**: Ensure that the AWS CLI is installed on your machine.
2. **Configure AWS CLI**: Configure the AWS CLI with your access key and secret key.
3. **Get Login Credentials**: Use the `aws ecr get-login-password` command to obtain the login credentials.
4. **Login to ECR**: Use the obtained credentials to log in to ECR.

Here’s an example of how to authenticate with ECR using the AWS CLI:

```sh
# Get the login password for ECR
LOGIN_PASSWORD=$(aws ecr get-login-password --region us-west-2)

# Log in to ECR
docker login --username AWS --password-stdin https://<account-id>.dkr.ecr.us-west-2.amazonaws.com
```

### Pitfalls and Best Practices

#### Pitfall: Exposing Credentials

Exposing your AWS credentials in scripts or logs can lead to unauthorized access. Always ensure that credentials are handled securely and not logged or printed in plain text.

#### Best Practice: Use IAM Roles

Instead of using static access keys, consider using IAM roles for your CI/CD pipeline. IAM roles provide temporary credentials that are automatically rotated and can be scoped to specific permissions.

### How to Prevent / Defend

#### Detection

Regularly monitor your AWS console for any unauthorized access attempts. Use AWS CloudTrail to log and audit API calls made to your AWS resources.

#### Prevention

1. **IAM Roles**: Use IAM roles with least privilege permissions.
2. **Temporary Credentials**: Use temporary credentials obtained via IAM roles instead of static access keys.
3. **Secure Storage**: Store credentials securely using tools like AWS Secrets Manager.

### Real-World Example

A company experienced a security breach when an attacker gained access to their AWS ECR registry by exploiting hardcoded credentials in their CI/CD pipeline. The breach was prevented by switching to IAM roles and using temporary credentials for authentication.

---
<!-- nav -->
[[08-Introduction to Continuous Delivery (CD) Pipelines|Introduction to Continuous Delivery (CD) Pipelines]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[10-Handling Expired Tokens in CICD Pipelines|Handling Expired Tokens in CICD Pipelines]]
