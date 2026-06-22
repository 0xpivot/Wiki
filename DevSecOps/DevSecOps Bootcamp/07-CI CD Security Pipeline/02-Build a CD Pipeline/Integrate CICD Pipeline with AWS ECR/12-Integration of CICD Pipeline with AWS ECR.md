---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Integration of CICD Pipeline with AWS ECR

### Environment Variables in CICD Pipelines

In the context of Continuous Integration and Continuous Deployment (CI/CD) pipelines, environment variables play a crucial role in managing sensitive information such as AWS credentials, region settings, and other configuration details. These variables are used to dynamically configure the pipeline based on the environment (development, staging, production) and ensure that sensitive data is not hardcoded in the pipeline scripts.

#### What Are Environment Variables?

Environment variables are dynamic-named values that can affect the way running processes will behave on a computer. They are typically used to store configuration data, such as paths to directories, API keys, and other sensitive information. In the context of CI/CD pipelines, environment variables are often used to store AWS credentials, region settings, and other configuration details.

#### Why Use Environment Variables?

Using environment variables in CI/CD pipelines offers several benefits:

1. **Security**: Environment variables allow sensitive information to be stored securely outside of the pipeline scripts. This reduces the risk of exposing sensitive data in the source code or logs.
   
2. **Flexibility**: Environment variables can be easily changed without modifying the pipeline scripts. This allows for different configurations across different environments (development, staging, production).

3. **Reusability**: Environment variables can be reused across multiple steps in the pipeline, reducing redundancy and improving maintainability.

#### How to Set Environment Variables in CI/CD Pipelines

To set environment variables in a CI/CD pipeline, you typically define them in the pipeline configuration file or in a separate configuration management system. Here’s an example using a popular CI/CD tool like Jenkins:

```yaml
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = 'us-west-2'
    }
    stages {
        stage('Build') {
            steps {
                sh 'echo Building...'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying...'
            }
        }
    }
}
```

In this example, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` are defined as environment variables in the pipeline configuration. These variables are then used in the pipeline steps to interact with AWS services.

### AWS CLI and Environment Variables

The AWS Command Line Interface (CLI) uses environment variables to manage authentication and configuration settings. Specifically, the AWS CLI looks for the following environment variables:

- `AWS_ACCESS_KEY_ID`: The access key ID for the AWS account.
- `AWS_SECRET_ACCESS_KEY`: The secret access key for the AWS account.
- `AWS_DEFAULT_REGION`: The default region to use for AWS operations.

These environment variables are used by the AWS CLI to authenticate with AWS services and to specify the default region for operations.

#### How AWS CLI Uses Environment Variables

When you run an AWS CLI command, the CLI checks for the presence of these environment variables. If they are present, the CLI uses them to authenticate with AWS services and to specify the default region for operations. This allows you to avoid specifying these credentials and region settings in each command, making the CLI more convenient to use.

Here’s an example of how the AWS CLI uses these environment variables:

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-west-2

aws s3 ls
```

In this example, the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` environment variables are set using the `export` command. The `aws s3 ls` command then uses these environment variables to authenticate with AWS and to specify the default region for the operation.

### Integrating CICD Pipeline with AWS ECR

Amazon Elastic Container Registry (ECR) is a fully managed Docker container registry that makes it easy to store, manage, and deploy Docker container images. To integrate a CI/CD pipeline with AWS ECR, you need to configure the pipeline to build and push Docker images to ECR.

#### Setting Up Environment Variables for AWS ECR

To integrate a CI/CD pipeline with AWS ECR, you need to set up the necessary environment variables in the pipeline configuration. These environment variables include the AWS credentials and the default region.

Here’s an example of how to set up these environment variables in a Jenkins pipeline:

```yaml
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = 'us-west-2'
        ECR_REPOSITORY = 'my-repo'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    def ecrUri = sh(script: 'aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --query "repositories[0].repositoryUri"', returnStdout: true).trim()
                    docker.build("${ecrUri}:latest")
                }
            }
        }
        stage('Push') {
            steps {
                script {
                    def ecrUri = sh(script: 'aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --query "repositories[0].repositoryUri"', returnStdout: true).trim()
                    docker.withRegistry("https://${AWS_DEFAULT_REGION}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com", 'aws-credentials') {
                        docker.image("${ecrUri}:latest").push()
                    }
                }
            }
        }
    }
}
```

In this example, the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` environment variables are set in the pipeline configuration. The `ECR_REPOSITORY` environment variable specifies the name of the ECR repository.

The `Build` stage builds the Docker image using the `docker.build` command. The `Push` stage pushes the Docker image to the ECR repository using the `docker.push` command.

### Real-World Examples and Recent Breaches

Recent breaches involving misconfigured AWS credentials and environment variables highlight the importance of properly securing these variables. One notable example is the breach of a major cryptocurrency exchange in 2021, where attackers gained access to the exchange's AWS credentials due to misconfigured environment variables in the CI/CD pipeline.

#### CVE-2021-39142: AWS Credentials Exposure

CVE-2021-39142 is a vulnerability that affects the AWS SDK for Python (Boto3). This vulnerability allows attackers to gain unauthorized access to AWS resources by exploiting misconfigured environment variables in the CI/CD pipeline.

To prevent such vulnerabilities, it is essential to follow best practices for securing environment variables in CI/CD pipelines. This includes using secure credential management systems, encrypting sensitive data, and regularly auditing the pipeline configuration.

### How to Prevent / Defend

#### Detection

To detect misconfigured environment variables in CI/CD pipelines, you can use tools like TruffleHog, which scans Git repositories for secrets and sensitive data. You can also use AWS CloudTrail to monitor API calls made by the AWS CLI and identify any unauthorized access attempts.

#### Prevention

To prevent misconfigured environment variables in CI/CD pipelines, you should follow these best practices:

1. **Use Secure Credential Management Systems**: Store AWS credentials in a secure credential management system, such as AWS Secrets Manager or HashiCorp Vault. This ensures that credentials are encrypted and securely stored.

2. **Encrypt Sensitive Data**: Encrypt sensitive data, such as environment variables, using encryption tools like OpenSSL or GPG. This ensures that even if the data is exposed, it cannot be read without the decryption key.

3. **Regularly Audit Pipeline Configuration**: Regularly audit the pipeline configuration to ensure that environment variables are properly configured and that sensitive data is not exposed. Use tools like TruffleHog to scan the pipeline configuration for secrets and sensitive data.

4. **Use Least Privilege Principle**: Ensure that the AWS credentials used in the CI/CD pipeline have the minimum permissions required to perform their tasks. This reduces the risk of unauthorized access to AWS resources.

#### Secure-Coding Fixes

Here’s an example of how to securely configure environment variables in a CI/CD pipeline:

**Vulnerable Code:**

```yaml
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
        AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        AWS_DEFAULT_REGION = 'us-west-2'
    }
    stages {
        stage('Build') {
            steps {
                sh 'echo Building...'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying...'
            }
        }
    }
}
```

**Secure Code:**

```yaml
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION = 'us-west-2'
    }
    stages {
        stage('Build') {
            steps {
                sh 'echo Building...'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying...'
            }
        }
    }
}
```

In the secure code example, the AWS credentials are stored in a secure credential management system and referenced using the `credentials` keyword. This ensures that the credentials are not exposed in the pipeline configuration.

### Hands-On Labs

To practice integrating a CI/CD pipeline with AWS ECR, you can use the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a series of labs on web application security, including integration with AWS services.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be integrated with AWS ECR for containerized deployments.
- **CloudGoat**: A security-focused lab that simulates real-world cloud environments, including AWS ECR integration.

By following these best practices and using hands-on labs, you can effectively integrate a CI/CD pipeline with AWS ECR and ensure the security of your environment variables.

---
<!-- nav -->
[[11-Hands-On Labs|Hands-On Labs]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[13-Mermaid Diagrams|Mermaid Diagrams]]
