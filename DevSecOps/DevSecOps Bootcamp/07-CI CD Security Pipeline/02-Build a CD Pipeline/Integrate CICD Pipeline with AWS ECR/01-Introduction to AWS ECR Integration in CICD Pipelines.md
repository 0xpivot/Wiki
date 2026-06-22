---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to AWS ECR Integration in CI/CD Pipelines

In the realm of DevSecOps, integrating Continuous Integration and Continuous Deployment (CI/CD) pipelines with Amazon Elastic Container Registry (ECR) is a critical step towards ensuring efficient and secure container management. This chapter delves into the process of setting up a CI/CD pipeline that leverages AWS ECR for storing and managing Docker images. We will cover the necessary steps, tools, and configurations required to achieve this integration, along with detailed explanations and practical examples.

### Background Theory

Before diving into the specifics, let's understand the foundational concepts:

#### What is AWS ECR?

Amazon Elastic Container Registry (ECR) is a fully managed Docker container registry service provided by AWS. It allows you to store, manage, and deploy Docker container images securely. ECR integrates seamlessly with other AWS services, making it an ideal choice for building scalable and reliable CI/CD pipelines.

#### Why Use AWS ECR?

- **Security**: ECR supports encryption at rest and in transit, ensuring your container images are protected.
- **Scalability**: ECR can handle large numbers of images and high throughput, making it suitable for enterprise-scale deployments.
- **Integration**: ECR integrates well with other AWS services like ECS, EKS, and Lambda, enabling streamlined workflows.

### Setting Up the Environment

To integrate a CI/CD pipeline with AWS ECR, you need to set up the environment correctly. This includes installing necessary tools and configuring your AWS account.

#### Installing AWS CLI

The first step is to install the AWS Command Line Interface (CLI). This tool allows you to interact with AWS services from the command line.

```bash
pip3 install awscli
```

This command installs the `awscli` package using `pip3`, the Python package manager. The `awscli` package provides a powerful interface to manage AWS resources, including ECR.

#### Configuring AWS CLI

After installing the AWS CLI, you need to configure it with your AWS credentials. This can be done using the following command:

```bash
aws configure
```

You will be prompted to enter your AWS Access Key ID, Secret Access Key, default region name, and default output format. These credentials are used to authenticate your interactions with AWS services.

### Creating an ECR Repository

Next, you need to create an ECR repository where your Docker images will be stored.

```bash
aws ecr create-repository --repository-name my-docker-repo
```

This command creates a new ECR repository named `my-docker-repo`. You can replace `my-docker-repo` with any name you prefer.

### Pushing Docker Images to ECR

Once the repository is created, you can push your Docker images to it. This involves tagging the image with the appropriate repository URI and then pushing it.

First, retrieve the repository URI:

```bash
aws ecr describe-repositories --repository-names my-docker-repo --query 'repositories[0].repositoryUri'
```

This command returns the URI of the repository, which looks something like `aws_account_id.dkr.ecr.region.amazonaws.com/my-docker-repo`.

Tag your Docker image with this URI:

```bash
docker tag my-docker-image:latest aws_account_id.dkr.ecr.region.amazonaws.com/my-docker-repo:latest
```

Then, push the image to ECR:

```bash
aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
docker push aws_account_id.dkr.ecr.region.amazonaws.com/my-docker-repo:latest
```

These commands log in to ECR using your AWS credentials and push the tagged image to the repository.

### Integrating with CI/CD Pipeline

Now that you have set up ECR, you can integrate it with your CI/CD pipeline. This typically involves automating the build, test, and deployment processes.

#### Example CI/CD Pipeline Configuration

Here is an example of a CI/CD pipeline configuration using Jenkins:

```yaml
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-docker-image .'
            }
        }
        stage('Test') {
            steps {
                sh 'docker run my-docker-image /bin/sh -c "pytest"'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    def repo_uri = sh(script: 'aws ecr describe-repositories --repository-names my-docker-repo --query "repositories[0].repositoryUri"', returnStdout: true).trim()
                    sh "docker tag my-docker-image:latest ${repo_uri}:latest"
                    sh 'aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com'
                    sh "docker push ${repo_uri}:latest"
                }
            }
        }
    }
}
```

This Jenkins pipeline defines three stages: Build, Test, and Deploy. The `Deploy` stage pushes the built Docker image to the ECR repository.

### Handling AWS Regions

AWS has multiple regions around the world, and services are typically created in a specific region. When interacting with ECR, you need to specify the region explicitly.

#### Specifying Region in Commands

For example, when creating a repository, you can specify the region:

```bash
aws ecr create-repository --repository-name my-docker-repo --region us-west-2
```

Similarly, when pushing an image, you need to ensure the region is correct:

```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.us-west-2.amazonaws.com
```

### AWS Account ID

Every AWS account has a unique identifier called the AWS Account ID. This ID is used to uniquely identify resources across different accounts.

#### Using Account ID in Commands

When working with ECR, you often need to reference the account ID in the repository URI:

```bash
aws_account_id.dkr.ecr.region.amazonaws.com/my-docker-repo
```

### Real-World Examples and Security Considerations

#### Recent Breaches and CVEs

Recent breaches involving container registries highlight the importance of securing your ECR setup. For example, the 2021 breach of a major container registry led to the exposure of sensitive data. To prevent such incidents, it is crucial to follow best practices for securing your ECR repositories.

#### Secure Coding Practices

- **Use Strong Authentication**: Always use strong authentication mechanisms like IAM roles and policies to control access to ECR.
- **Enable Encryption**: Enable encryption at rest and in transit for your ECR repositories.
- **Regular Audits**: Regularly audit your ECR repositories to ensure compliance with security policies.

### How to Prevent / Defend

#### Detection

- **Monitor Access Logs**: Monitor access logs to detect unauthorized access attempts.
- **Use AWS CloudTrail**: Enable AWS CloudTrail to log API calls made to ECR.

#### Prevention

- **IAM Policies**: Use IAM policies to restrict access to ECR repositories.
- **Encryption**: Enable encryption at rest and in transit for your ECR repositories.

#### Secure-Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-docker-image .'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    def repo_uri = sh(script: 'aws ecr describe-repositories --repository-names my-docker-repo --query "repositories[0].repositoryUri"', returnStdout: true).trim()
                    sh "docker tag my-docker-image:latest ${repo_uri}:latest"
                    sh 'aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com'
                    sh "docker push ${repo_uri}:latest"
                }
            }
        }
    }
}
```

**Secure Configuration:**

```yaml
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-docker-image .'
            }
        }
        stage('Test') {
            steps {
                sh 'docker run my-docker-image /bin/sh -c "pytest"'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    def repo_uri = sh(script: 'aws ecr describe-repositories --repository-names my-docker-repo --query "repositories[0].repositoryUri"', returnStdout: true).trim()
                    sh "docker tag my-docker-image:latest ${repo_uri}:latest"
                    sh 'aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.us-west-2.amazonaws.com'
                    sh "docker push ${repo_uri}:latest"
                }
            }
        }
    }
}
```

### Conclusion

Integrating a CI/CD pipeline with AWS ECR is a crucial step in modern DevSecOps practices. By following the steps outlined in this chapter, you can set up a secure and efficient pipeline that leverages the power of AWS ECR. Remember to follow best practices for security and regularly audit your setup to ensure compliance with security policies.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **CloudGoat**: A series of labs designed to help you learn about AWS security best practices.

By completing these labs, you can gain practical experience in integrating CI/CD pipelines with AWS ECR and other AWS services.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/02-Introduction to AWS Elastic Container Registry (ECR)|Introduction to AWS Elastic Container Registry (ECR)]]
