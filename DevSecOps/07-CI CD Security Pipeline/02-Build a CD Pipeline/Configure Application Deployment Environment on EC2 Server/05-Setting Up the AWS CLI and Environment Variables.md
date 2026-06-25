---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Setting Up the AWS CLI and Environment Variables

### Background Theory

Before diving into the practical steps, it's important to understand the context and the underlying principles involved in setting up an application deployment environment on an EC2 server using the AWS Command Line Interface (CLI).

#### What is AWS CLI?

The AWS Command Line Interface (CLI) is a unified tool to manage your AWS services. With just one tool to download, you can work with services like Amazon S3 and Amazon EC2 through commands in your terminal window. This makes it easier to automate tasks and integrate AWS services into scripts.

#### Why Use AWS CLI?

Using the AWS CLI allows you to perform operations on AWS resources programmatically. This is particularly useful in continuous integration and continuous delivery (CI/CD) pipelines where automation is key. By automating tasks, you reduce the chances of human error and increase efficiency.

#### How Does AWS CLI Work?

The AWS CLI interacts with AWS services via API calls. To authenticate these calls, you need to provide AWS credentials, which include an Access Key ID and a Secret Access Key. These credentials are typically stored in environment variables or in a configuration file.

### Configuring AWS CLI

#### Installing AWS CLI

To install the AWS CLI, you can use package managers like `apt` for Debian-based systems. Here’s how you can install it:

```bash
sudo apt update
sudo apt install awscli
```

Once installed, you can verify the installation by checking the version:

```bash
aws --version
```

This command should output the version of the AWS CLI installed on your system.

#### Setting Environment Variables

After installing the AWS CLI, you need to configure it with your AWS credentials. This involves setting environment variables for the Access Key ID, Secret Access Key, and Default Region.

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=us-west-2
```

These environment variables are used by the AWS CLI to authenticate and specify the region for API calls.

### Using AWS CLI for ECR Login

#### What is ECR?

Amazon Elastic Container Registry (ECR) is a fully managed Docker container registry that makes it easy to store, manage, and deploy Docker container images. ECR integrates with Amazon ECS, AWS Fargate, and other AWS services to simplify your development workflow.

#### Logging into ECR

To push or pull images from an ECR repository, you need to log in to the ECR registry. This can be done using the AWS CLI.

```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
```

Here, `<account-id>` is your AWS account ID. This command retrieves a password from AWS and uses it to log in to the ECR registry.

### Example: Full Deployment Process

Let's walk through a complete example of setting up the environment and deploying an application.

#### Step 1: Install AWS CLI

```bash
sudo apt update
sudo apt install awscli
```

#### Step 2: Set Environment Variables

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-west-2
```

#### Step 3: Log in to ECR

```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
```

#### Step 4: Pull and Run a Docker Image

```bash
docker pull 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
docker run -d -p 8080:80 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
```

### Pitfalls and Common Mistakes

#### Exposing Credentials

One of the most critical mistakes is exposing your AWS credentials. Ensure that you do not commit these credentials to version control systems or share them publicly.

#### Incorrect Region Configuration

Using the wrong region can lead to errors. Always double-check that the region specified in your environment variables matches the region of your AWS resources.

### How to Prevent / Defend

#### Securely Storing Credentials

Instead of storing credentials in environment variables, consider using AWS IAM roles or AWS Secrets Manager.

##### Using IAM Roles

IAM roles can be attached to EC2 instances, allowing the instance to assume the role and access AWS resources without needing to store credentials.

```yaml
# Example IAM Role Policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": "*"
        }
    ]
}
```

##### Using AWS Secrets Manager

AWS Secrets Manager can securely store and retrieve secrets such as database credentials, API keys, and more.

```json
// Example Secrets Manager Secret
{
    "SecretString": "{\"accessKeyId\":\"AKIAIOSFODNN7EXAMPLE\",\"secretAccessKey\":\"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"}"
}
```

#### Hardening Configuration

Ensure that your AWS CLI configuration is hardened against unauthorized access.

##### IAM Policies

Use least privilege IAM policies to restrict access to only the necessary actions and resources.

```json
// Example IAM Policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:*"
            ],
            "Resource": "*"
        }
    ]
}
```

##### Secure SSH Access

Secure SSH access to your EC2 instances by disabling root login and using key-based authentication.

```bash
# Example SSH Configuration
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

### Real-World Examples

#### Recent Breaches

In 2021, several companies experienced breaches due to misconfigured AWS S3 buckets and exposed credentials. Ensuring proper configuration and securing credentials can prevent such incidents.

#### CVEs

CVE-2021-20225: A vulnerability in AWS CLI allowed attackers to execute arbitrary commands. Always keep your AWS CLI updated to the latest version.

### Conclusion

Setting up an application deployment environment on an EC2 server using the AWS CLI involves several steps, including installing the CLI, configuring environment variables, and logging into ECR. By following best practices and securing your credentials, you can ensure a robust and secure deployment process.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on AWS security and CI/CD pipelines.
- **CloudGoat**: Provides scenarios for practicing cloud security on AWS.
- **Pacu**: A framework for testing and exploiting AWS configurations.

By completing these labs, you can gain practical experience in setting up and securing your AWS environment.

---
<!-- nav -->
[[04-Configuring Application Deployment Environment on EC2 Server|Configuring Application Deployment Environment on EC2 Server]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Application Deployment Environment on EC2 Server/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Application Deployment Environment on EC2 Server/06-Practice Questions & Answers|Practice Questions & Answers]]
