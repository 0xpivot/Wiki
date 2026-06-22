---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to AWS Elastic Container Registry (ECR)

AWS Elastic Container Registry (ECR) is a managed Docker container registry service provided by Amazon Web Services (AWS). It allows users to store, manage, and deploy Docker images securely and reliably. ECR integrates seamlessly with other AWS services, such as Amazon ECS (Elastic Container Service) and AWS Fargate, making it a popular choice for containerized applications in the cloud.

### What is AWS ECR?

AWS ECR is designed to store Docker images in a private registry, ensuring that these images are accessible only to authorized users within your AWS account. This service provides features such as:

- **Security**: ECR supports image scanning to identify vulnerabilities and compliance issues.
- **Scalability**: ECR can handle large numbers of images and high throughput, making it suitable for large-scale deployments.
- **Integration**: ECR integrates with other AWS services, simplifying the management and deployment of containerized applications.

### Why Use AWS ECR?

Using AWS ECR offers several benefits:

- **Security**: ECR uses AWS Identity and Access Management (IAM) policies to control access to your repositories. Additionally, ECR supports encryption at rest and in transit.
- **Ease of Use**: ECR is fully managed, meaning you don't have to worry about setting up and maintaining your own container registry.
- **Integration**: ECR integrates with other AWS services, allowing you to build end-to-end CI/CD pipelines.

### How Does AWS ECR Work?

When you create a repository in ECR, you can push Docker images to it using the `docker push` command. ECR handles the storage and retrieval of these images, ensuring they are available for deployment.

#### Example: Creating an ECR Repository

To create an ECR repository, you can use the AWS Management Console or the AWS CLI. Here’s an example using the AWS CLI:

```bash
aws ecr create-repository --repository-name my-docker-repo
```

This command creates a new repository named `my-docker-repo`.

### Logging into ECR

To push images to an ECR repository, you need to authenticate with the registry. This is done using the AWS CLI, which retrieves a temporary access token for the registry.

#### Example: Authenticating with ECR

The following command retrieves the necessary credentials to log into the ECR repository:

```bash
$(aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com)
```

This command does the following:

- `aws ecr get-login-password`: Retrieves a temporary password for the ECR repository.
- `docker login`: Logs into the ECR repository using the retrieved password.

### Why Use AWS CLI for Authentication?

Using the AWS CLI for authentication is more secure than hardcoding credentials into your application or scripts. The AWS CLI retrieves a temporary access token, which is valid for a short period (typically one hour). This reduces the risk of exposing static credentials.

### Security Implications

Using the AWS CLI for authentication provides several security benefits:

- **Temporary Tokens**: The access tokens retrieved by the AWS CLI are temporary and expire after one hour. This limits the window of opportunity for unauthorized access.
- **IAM Policies**: You can control access to ECR repositories using IAM policies, ensuring that only authorized users can push or pull images.
- **Encryption**: ECR supports encryption at rest and in transit, ensuring that your images are protected.

### Real-World Examples

Recent breaches and vulnerabilities have highlighted the importance of secure authentication mechanisms. For example, the 2021 SolarWinds breach involved unauthorized access to Docker registries. Using secure authentication methods, such as those provided by AWS ECR, can help mitigate such risks.

### How to Prevent / Defend

To ensure the security of your ECR repositories, follow these best practices:

- **Use IAM Policies**: Restrict access to ECR repositories using IAM policies. Ensure that only authorized users have the necessary permissions.
- **Enable Image Scanning**: Enable image scanning in ECR to identify vulnerabilities and compliance issues in your Docker images.
- **Use Temporary Tokens**: Use the AWS CLI to retrieve temporary access tokens for ECR repositories, reducing the risk of exposing static credentials.

#### Example: Secure Configuration

Here’s an example of a secure configuration for an ECR repository:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPushPull",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<account-id>:role/<role-name>"
      },
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:<region>:<account-id>:repository/<repo-name>"
    }
  ]
}
```

This IAM policy restricts access to the specified ECR repository, ensuring that only authorized users can push or pull images.

### Conclusion

Integrating a CI/CD pipeline with AWS ECR provides a secure and reliable way to manage Docker images. By using the AWS CLI for authentication and following best practices for security, you can ensure that your containerized applications are deployed safely and efficiently.

### Practice Labs

To gain hands-on experience with integrating a CI/CD pipeline with AWS ECR, consider the following labs:

- **PortSwigger Web Security Academy**: Offers labs on securing Docker images and using ECR.
- **OWASP Juice Shop**: Provides a lab on deploying Docker images to ECR.
- **CloudGoat**: Includes scenarios on securing ECR repositories and managing access.

These labs will help you understand the practical aspects of working with AWS ECR in a CI/CD pipeline.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/01-Introduction to AWS ECR Integration in CICD Pipelines|Introduction to AWS ECR Integration in CICD Pipelines]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[03-Introduction to Continuous Delivery (CD) Pipelines with AWS ECR Part 1|Introduction to Continuous Delivery (CD) Pipelines with AWS ECR Part 1]]
