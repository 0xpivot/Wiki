---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Integrating Terraform into CI/CD Pipeline

### Background Theory

In modern DevOps practices, integrating infrastructure as code (IaC) tools like Terraform into continuous integration and continuous deployment (CI/CD) pipelines is essential for automating the provisioning and management of cloud resources. This integration ensures that infrastructure changes are version-controlled, tested, and deployed alongside application code, leading to more reliable and scalable systems.

### Setting Up Jenkins and SSH Agent Plugin

Before diving into the integration of Terraform, let's ensure that Jenkins is properly set up with the necessary plugins. In this scenario, we have already configured Jenkins and installed the SSH Agent plugin. The SSH Agent plugin allows Jenkins to manage SSH keys securely and use them to authenticate with remote servers during the build process.

#### Installing SSH Agent Plugin

To install the SSH Agent plugin in Jenkins:

1. Navigate to **Manage Jenkins** > **Manage Plugins**.
2. Go to the **Available** tab.
3. Search for **SSH Agent**.
4. Click **Install without restart**.

Once installed, the SSH Agent plugin can be used within Jenkins jobs to handle SSH keys securely.

### Hard-Coded Remote Server Address

In the initial setup, the remote server address was hardcoded in the Jenkinsfile. This approach is not ideal for several reasons:

1. **Manual Configuration**: Requires manual creation of the remote instance before executing the CI/CD pipeline.
2. **Security Risks**: Exposing the public IP address of the server in the Jenkinsfile poses a security risk.
3. **Maintenance Overhead**: Any change in the server's IP address requires manual updates in the Jenkinsfile.

#### Example of Hardcoded Remote Server Address

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sshagent(credentials: ['ssh-key']) {
                    sh 'ssh -o StrictHostKeyChecking=no user@192.168.1.100 "echo Deploying..."'
                }
            }
        }
    }
}
```

### Automating Server Provisioning with Terraform

To improve the automation and reliability of the CI/CD pipeline, we will integrate Terraform to provision the server dynamically. This approach ensures that the server is created automatically as part of the pipeline, eliminating the need for manual intervention.

#### Creating a Key Pair for the Server

The first step in provisioning a server with Terraform is to create an SSH key pair. This key pair will be used to authenticate with the server once it is provisioned.

##### Generating SSH Key Pair

```bash
ssh-keygen -t rsa -b 4096 -f terraform_key
```

This command generates an RSA key pair with a 4096-bit length and saves it to `terraform_key` and `terraform_key.pub`.

#### Terraform Configuration

Next, we need to configure Terraform to provision the server. Below is an example of a Terraform configuration file (`main.tf`) for creating an EC2 instance in AWS:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  key_name = "terraform_key"

  tags = {
    Name = "terraform-example"
  }
}
```

### Integrating Terraform into Jenkins Pipeline

Now that we have the Terraform configuration ready, we need to integrate it into the Jenkins pipeline. We will create a new stage called `provision_server` to handle the Terraform provisioning.

#### Jenkinsfile with Terraform Integration

Below is an example of a Jenkinsfile that integrates Terraform into the pipeline:

```groovy
pipeline {
    agent any
    environment {
        TF_VAR_aws_access_key = credentials('aws-access-key')
        TF_VAR_aws_secret_key = credentials('aws-secret-key')
    }
    stages {
        stage('Provision Server') {
            steps {
                script {
                    dir('terraform') {
                        sh 'terraform init'
                        sh 'terraform apply -auto-approve'
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    def server_ip = sh(script: 'terraform output server_ip', returnStdout: true).trim()
                    sshagent(credentials: ['ssh-key']) {
                        sh "ssh -o StrictHostKeyChecking=no user@$server_ip 'echo Deploying...'"
                    }
                }
            }
        }
    }
}
```

### Explanation of the Jenkinsfile

1. **Environment Variables**: The `environment` block sets up environment variables for AWS access and secret keys, which are required by Terraform to interact with AWS.
2. **Provision Server Stage**: This stage initializes Terraform and applies the configuration to provision the server.
3. **Deploy Stage**: This stage retrieves the server's IP address from Terraform and deploys the application to the server using SSH.

### Mermaid Diagram of the Pipeline

```mermaid
graph TD
    A[Start] --> B[Provision Server]
    B --> C[Retrieve Server IP]
    C --> D[Deploy Application]
    D --> E[End]
```

### Common Pitfalls and How to Prevent Them

#### Hardcoding Secrets

Hardcoding secrets such as AWS access keys and SSH keys in the Jenkinsfile or Terraform configuration files is a significant security risk. Instead, use Jenkins credentials and Terraform environment variables to securely manage these secrets.

#### Example of Secure Secret Management

```groovy
pipeline {
    agent any
    environment {
        TF_VAR_aws_access_key = credentials('aws-access-key')
        TF_VAR_aws_secret_key = credentials('aws-secret-key')
    }
    stages {
        stage('Provision Server') {
            steps {
                script {
                    dir('terraform') {
                        sh 'terraform init'
                        sh 'terraform apply -auto-approve'
                    }
                }
            }
        }
    }
}
```

### Real-World Examples and Recent Breaches

#### Example: AWS Access Key Exposure

In 2021, a company exposed their AWS access keys in a publicly accessible repository, leading to unauthorized access to their cloud resources. This breach could have been prevented by using Jenkins credentials and environment variables to manage sensitive information securely.

### Detection and Prevention

#### Detection

Regularly audit your Jenkins jobs and Terraform configurations to ensure that sensitive information is not hardcoded. Use tools like `grep` to search for hardcoded secrets in your repositories.

```bash
grep -r 'access_key' .
```

#### Prevention

1. **Use Jenkins Credentials**: Store sensitive information in Jenkins credentials and reference them in your Jenkinsfile.
2. **Terraform Environment Variables**: Use environment variables to pass sensitive information to Terraform.
3. **Secure Storage Solutions**: Utilize secure storage solutions like HashiCorp Vault to manage and distribute secrets.

### Secure Code Fix

#### Vulnerable Code

```groovy
pipeline {
    agent any
    environment {
        TF_VAR_aws_access_key = 'AKIAIOSFODNN7EXAMPLE'
        TF_VAR_aws_secret_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    }
    stages {
        stage('Provision Server') {
            steps {
                script {
                    dir('terraform') {
                        sh 'terraform init'
                        sh 'terraform apply -auto-approve'
                    }
                }
            }
        }
    }
}
```

#### Fixed Code

```groovy
pipeline {
    agent any
    environment {
        TF_VAR_aws_access_key = credentials('aws-access-key')
        TF_VAR_aws_secret_key = credentials('aws-secret-key')
    }
    stages {
        stage('Provision Server') {
            steps {
                script {
                    dir('terraform') {
                        sh 'terraform init'
                        sh 'terraform apply -auto-approve'
                    }
                }
            }
        }
    }
}
```

### Conclusion

Integrating Terraform into a CI/CD pipeline with Jenkins provides a robust and automated way to manage cloud infrastructure. By following best practices for secret management and using secure coding techniques, you can ensure that your infrastructure remains secure and reliable.

### Practice Labs

For hands-on practice with integrating Terraform into CI/CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications and integrating IaC tools.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing and CI/CD integration.
- **Kubernetes Goat**: Focuses on Kubernetes security and can be used to practice integrating IaC tools with Kubernetes deployments.

These labs provide practical experience in applying the concepts learned in this chapter.

---
<!-- nav -->
[[03-Installing Terraform in Jenkins Container|Installing Terraform in Jenkins Container]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/11-Integrating Terraform into CICD Pipeline/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/11-Integrating Terraform into CICD Pipeline/05-Practice Labs|Practice Labs]]
