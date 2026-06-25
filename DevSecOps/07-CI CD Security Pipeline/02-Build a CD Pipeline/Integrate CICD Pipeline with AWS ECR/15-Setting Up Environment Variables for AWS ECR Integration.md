---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Setting Up Environment Variables for AWS ECR Integration

When integrating a Continuous Delivery (CD) pipeline with Amazon Elastic Container Registry (ECR), it is crucial to manage environment variables effectively. These variables will hold essential information such as the AWS region, account ID, and other configuration details. Proper management of these variables ensures that your pipeline remains flexible, maintainable, and secure.

### Why Use Environment Variables?

Environment variables are a fundamental aspect of modern software development and deployment practices. They allow you to externalize configuration settings from your codebase, making your application more adaptable to different environments (development, testing, production). This separation of concerns is particularly important in CD pipelines, where the same code might run in various contexts with different configurations.

#### Benefits of Using Environment Variables:

1. **Flexibility**: Easily change configurations without modifying the code.
2. **Security**: Avoid hardcoding sensitive information directly into your code.
3. **Maintainability**: Centralize configuration management, making it easier to update settings across multiple environments.
4. **Consistency**: Ensure that the same configuration is applied consistently across different stages of the pipeline.

### Setting Up AWS Region and Account ID

In the context of AWS ECR integration, two key pieces of information are the AWS region and the account ID. These values are required to interact with AWS services correctly and securely.

#### AWS Region

The AWS region specifies the geographical location where your resources are hosted. Choosing the correct region is important for minimizing latency and ensuring compliance with data sovereignty laws.

```mermaid
graph LR
    A[User] --> B[Choose Region]
    B --> C{Region Selection}
    C --> D[EU West 3]
    C --> E[US East 1]
    C --> F[AP South 1]
```

**Example:**
- **EU West 3**: `eu-west-3`
- **US East 1**: `us-east-1`
- **AP South 1**: `ap-south-1`

#### AWS Account ID

The AWS account ID uniquely identifies your AWS account. This identifier is necessary for constructing resource ARNs (Amazon Resource Names) and for authenticating API calls.

**Example:**
- **Account ID**: `123456789012`

### Setting Environment Variables

To set these environment variables, you can use a variety of methods depending on your CI/CD platform. Here, we'll demonstrate using GitLab CI/CD as an example.

#### GitLab CI/CD Example

In GitLab CI/CD, you can define environment variables in the `.gitlab-ci.yml` file or in the GitLab UI.

##### .gitlab-ci.yml Configuration

```yaml
variables:
  AWS_DEFAULT_REGION: "eu-west-3"
  AWS_ACCOUNT_ID: "123456789012"
  IMAGE_NAME: "my-image"
  IMAGE_TAG: "latest"

stages:
  - build
  - deploy

build_job:
  stage: build
  script:
    - echo "Building image $IMAGE_NAME:$IMAGE_TAG in region $AWS_DEFAULT_REGION"
    - docker build -t $IMAGE_NAME:$IMAGE_TAG .
    - docker tag $IMAGE_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG
    - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
    - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_NAME:$IMAGE_TAG
```

### Explanation of Each Variable

1. **AWS_DEFAULT_REGION**: Specifies the AWS region where your ECR repository is located.
2. **AWS_ACCOUNT_ID**: Identifies your AWS account.
3. **IMAGE_NAME**: The name of the Docker image.
4. **IMAGE_TAG**: The tag for the Docker image.

### How to Prevent / Defend

#### Detection

Ensure that your environment variables are not hardcoded in your codebase. Use tools like `grep` or static analysis tools to check for hardcoded values.

```sh
grep -r "aws_access_key_id" .
grep -r "aws_secret_access_key" .
```

#### Prevention

1. **Use Environment Variables**: Externalize configuration settings using environment variables.
2. **Secure Access Keys**: Never hardcode AWS access keys or secret keys in your code. Use IAM roles and policies instead.
3. **Least Privilege Principle**: Assign minimal permissions to IAM roles used in your pipeline.

#### Secure Code Fix

**Vulnerable Code:**

```yaml
variables:
  AWS_ACCESS_KEY_ID: "AKIAIOSFODNN7EXAMPLE"
  AWS_SECRET_ACCESS_KEY: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

**Fixed Code:**

```yaml
variables:
  AWS_DEFAULT_REGION: "eu-west-3"
  AWS_ACCOUNT_ID: "123456789012"
  IMAGE_NAME: "my-image"
  IMAGE_TAG: "latest"
```

### Real-World Examples

#### Recent Breaches

- **CVE-2021-20225**: A misconfiguration in AWS S3 buckets led to unauthorized access. This highlights the importance of proper configuration management and the use of environment variables to avoid hardcoding sensitive information.
- **AWS IAM Role Misconfiguration**: In 2022, several organizations experienced breaches due to misconfigured IAM roles, leading to unauthorized access to AWS resources.

### Conclusion

Setting up environment variables for AWS ECR integration is a critical step in building a robust CD pipeline. By following best practices and using environment variables effectively, you can ensure that your pipeline remains flexible, secure, and maintainable. Always remember to avoid hardcoding sensitive information and to follow the least privilege principle when assigning permissions.

### Practice Labs

For hands-on experience with integrating CICD pipelines with AWS ECR, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on AWS security and CI/CD pipelines.
- **CloudGoat**: Provides scenarios for practicing cloud security, including AWS ECR integration.
- **AWS Official Workshops**: Includes detailed guides and labs for setting up CI/CD pipelines with AWS services.

By completing these labs, you can gain practical experience and reinforce your understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[16-Setting Up Environment Variables Globally|Setting Up Environment Variables Globally]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[18-Setting Up the CD Pipeline|Setting Up the CD Pipeline]]
