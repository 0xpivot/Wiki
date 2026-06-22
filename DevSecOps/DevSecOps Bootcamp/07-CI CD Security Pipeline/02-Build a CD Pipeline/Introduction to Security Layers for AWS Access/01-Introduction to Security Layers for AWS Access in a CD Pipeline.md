---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to Security Layers for AWS Access in a CD Pipeline

In the context of Continuous Delivery (CD) pipelines, ensuring secure access to resources such as container registries is paramount. This chapter will delve into the process of setting up secure access to Amazon Elastic Container Registry (ECR) within a CD pipeline, contrasting it with the simpler setup required for Docker Hub. We will cover the necessary steps, tools, and security considerations involved in this transition.

### Background Theory

#### What is a CD Pipeline?

A Continuous Delivery (CD) pipeline is a series of steps that automate the process of building, testing, and deploying software. It ensures that code changes can be reliably released to production at any time. Key components of a CD pipeline include:

- **Source Control**: Version control systems like Git.
- **Build**: Compiling and packaging the code.
- **Test**: Running automated tests to ensure quality.
- **Deploy**: Pushing the built artifacts to staging or production environments.

#### What is Docker Hub?

Docker Hub is a public registry for Docker images. It provides a simple way to store and share Docker images. Users can create accounts and repositories, and authenticate using their username and password. Docker Hub is straightforward to integrate into a CD pipeline due to its simplicity.

#### What is Amazon Elastic Container Registry (ECR)?

Amazon Elastic Container Registry (ECR) is a fully managed Docker container registry provided by AWS. Unlike Docker Hub, which is a single-purpose registry, ECR is integrated into the broader AWS ecosystem. This means that accessing ECR requires AWS credentials, which provide more granular control over permissions and access.

### Transition from Docker Hub to ECR

When transitioning from Docker Hub to ECR, several key changes must be made to the CD pipeline configuration. These changes involve setting up ECR credentials and ensuring that the necessary tools are available to interact with AWS services.

#### Setting Up ECR Credentials

To push and pull images from ECR, you need to authenticate using AWS credentials. This is different from Docker Hub, where you use a username and password.

##### Steps to Set Up ECR Credentials

1. **Create an IAM Role**: An IAM role with appropriate permissions is required to access ECR. This role should have the `AmazonEC2ContainerRegistryPowerUser` policy attached.

2. **Generate AWS Credentials**: You need to generate AWS access keys and secret keys for the IAM user or role. These credentials will be used to authenticate with ECR.

3. **Configure ECR Login**: In your CD pipeline, you need to configure the ECR login using the AWS CLI. This can be done using the following command:

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

Here is a complete example of how this might look in a CD pipeline script:

```yaml
# Jenkinsfile example
pipeline {
    agent any
    stages {
        stage('Login to ECR') {
            steps {
                script {
                    def region = 'us-west-2'
                    def accountId = '123456789012'
                    sh """
                        aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${accountId}.dkr.ecr.${region}.amazonaws.com
                    """
                }
            }
        }
        stage('Push Image to ECR') {
            steps {
                script {
                    sh """
                        docker tag my-image:latest ${accountId}.dkr.ecr.${region}.amazonaws.com/my-image:latest
                        docker push ${accountId}.dkr.ecr.${region}.amazonaws.com/my-image:latest
                    """
                }
            }
        }
    }
}
```

### Integrating AWS CLI in the CD Pipeline

To execute AWS commands in the CD pipeline, you need to ensure that the AWS CLI is installed and configured properly.

#### Installing AWS CLI

The AWS CLI can be installed on the build agent using package managers like `apt`, `yum`, or `brew`. Here is an example of installing AWS CLI using `apt`:

```bash
sudo apt update
sudo apt install -y awscli
```

#### Configuring AWS CLI

Once installed, you need to configure the AWS CLI with your access keys. This can be done using the `aws configure` command:

```bash
aws configure
```

This will prompt you to enter your AWS access key ID, secret access key, default region name, and default output format.

### Full Example of a CD Pipeline with ECR Integration

Let's put together a complete example of a CD pipeline that integrates with ECR. This example uses Jenkins as the CI/CD tool.

#### Jenkinsfile Example

```yaml
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        REGION = 'us-west-2'
        ACCOUNT_ID = '123456789012'
    }
    stages {
        stage('Checkout Code') {
            steps {
                git 'https://github.com/example/repo.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t my-image .'
                }
            }
        }
        stage('Login to ECR') {
            steps {
                script {
                    sh """
                        aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
                    """
                }
            }
        }
        stage('Tag and Push Image to ECR') {
            steps {
                script {
                    sh """
                        docker tag my-image:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/my-image:latest
                        docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/my-image:latest
                    """
                }
            }
        }
        stage('Deploy to Staging') {
            steps {
                script {
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }
}
```

### Security Considerations

#### Why Secure Access Matters

Secure access to ECR is crucial because it prevents unauthorized access to your container images. This is particularly important in a CD pipeline where images are frequently pushed and pulled.

#### Common Pitfalls

1. **Hardcoding Credentials**: Avoid hardcoding AWS credentials in your scripts or configuration files. Use environment variables or secrets management tools like HashiCorp Vault or AWS Secrets Manager.

2. **Insufficient Permissions**: Ensure that the IAM role or user has only the necessary permissions to access ECR. Using least privilege principles helps minimize the risk of unauthorized access.

3. **Exposure of Access Keys**: Be cautious about exposing AWS access keys. Use temporary credentials whenever possible, and rotate keys regularly.

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Enable AWS CloudTrail to monitor API calls made to ECR. This helps in detecting unauthorized access attempts.

2. **IAM Policies**: Use IAM policies to restrict access to ECR based on specific actions and resources.

#### Prevention

1. **Use IAM Roles**: Instead of using individual access keys, use IAM roles with the necessary permissions. This allows you to manage access more effectively.

2. **Temporary Credentials**: Use AWS Security Token Service (STS) to obtain temporary credentials with limited permissions.

3. **Secrets Management**: Use tools like AWS Secrets Manager or HashiCorp Vault to securely store and manage AWS credentials.

#### Secure-Coding Fixes

**Vulnerable Pattern**

```yaml
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
        AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    }
    stages {
        stage('Login to ECR') {
            steps {
                script {
                    sh """
                        aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
                    """
                }
            }
        }
    }
}
```

**Fixed Pattern**

```yaml
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
    }
    stages {
        stage('Login to ECR') {
            steps {
                script {
                    sh """
                        aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
                    """
                }
            }
        }
    }
}
```

### Real-World Examples

#### Recent Breaches

One notable breach involving AWS credentials occurred in 2021, where an attacker gained access to a company's AWS account due to improperly secured credentials. This resulted in unauthorized access to sensitive data stored in S3 buckets.

#### CVEs

CVE-2021-26685 is a vulnerability in AWS SDKs that could allow attackers to bypass authentication checks. This highlights the importance of keeping AWS SDKs and CLI versions up to date.

### Mermaid Diagrams

#### CD Pipeline Architecture

```mermaid
graph TD
    A[Source Control] --> B(Build)
    B --> C(Test)
    C --> D(Login to ECR)
    D --> E(Push Image to ECR)
    E --> F(Deploy to Staging)
```

#### Sequence Diagram

```mermaid
sequenceDiagram
    participant Jenkins
    participant Git
    participant Docker
    participant AWSCLI
    participant ECR
    participant Kubectl

    Jenkins->>Git: Checkout Code
    Jenkins->>Docker: Build Image
    Jenkins->>AWSCLI: Get ECR Login Password
    AWSCLI-->>Jenkins: Return Password
    Jenkins->>Docker: Login to ECR
    Jenkins->>Docker: Tag and Push Image
    Jenkins->>Kubectl: Deploy to Staging
```

### Practice Labs

For hands-on practice with setting up a CD pipeline with ECR integration, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on securing AWS resources.
- **flaws.cloud**: A cloud security lab that covers various aspects of AWS security, including ECR.
- **AWS Well-Architected Labs**: Official AWS labs that cover best practices for securing AWS resources.

By following these detailed steps and best practices, you can ensure that your CD pipeline is secure and reliable when integrating with ECR.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Introduction to Security Layers for AWS Access/00-Overview|Overview]] | [[02-Introduction to Security Layers for AWS Access Part 1|Introduction to Security Layers for AWS Access Part 1]]
