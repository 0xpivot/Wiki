---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Setting Up the CD Pipeline

### Step 1: Source Control

First, ensure your code is stored in a version control system like GitHub. This allows you to track changes and collaborate with team members.

```markdown
# Example GitHub Repository Structure
```

### Step 2: Build Image

Next, create a Dockerfile to define how your application should be built and packaged into an image.

```dockerfile
# Dockerfile
FROM node:14

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
```

### Step 3: Test and Security Checks

Before deploying the application, run automated tests and security checks. One common tool for security checks is RetireJS, which scans for known vulnerabilities in JavaScript libraries.

#### Configuring RetireJS

RetireJS can be configured to run as part of the CD pipeline. However, it's important to configure it to allow failures so that the pipeline does not fail if security issues are found.

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-image:$BUILD_NUMBER .'
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        stage('Security Check') {
            steps {
                script {
                    try {
                        sh 'retire --outputformat json > security-report.json'
                    } catch (err) {
                        echo 'Security check failed, but allowing pipeline to continue.'
                    }
                }
            }
        }
        stage('Push to ECR') {
            steps {
                sh 'aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com'
                sh 'docker tag my-image:$BUILD_NUMBER <account-id>.dkr.ecr.<region>.amazonaws.com/juice-shop:$BUILD_NUMBER'
                sh 'docker push <account-id>.dkr.ecr.<region>.amazonaws.com/juice-shop:$BUILD_NUMBER'
            }
        }
    }
}
```

### Explanation of the Jenkinsfile

- **Build Stage**: Builds the Docker image with a unique tag based on the build number.
- **Test Stage**: Runs automated tests.
- **Security Check Stage**: Runs RetireJS to scan for vulnerabilities. The `try-catch` block ensures that the pipeline continues even if the security check fails.
- **Push to ECR Stage**: Logs into ECR and pushes the built image to the registry.

### Step 4: Deploy to AWS EC2

Finally, deploy the Dockerized application to an AWS EC2 instance. This involves creating an EC2 instance and configuring it to pull and run the Docker image from ECR.

```yaml
# Example EC2 User Data Script
#!/bin/bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker pull <account-id>.dkr.ecr.<region>.amazonaws.com/juice-shop:$BUILD_NUMBER
docker run -d -p 8080:8080 <account-id>.dkr.ecr.<region>.amazonaws.com/juice-shop:$BUILD_NUMBER
```

### Explanation of the EC2 User Data Script

- **Install Docker**: Installs Docker on the EC2 instance.
- **Start Docker Service**: Starts the Docker service.
- **Login to ECR**: Logs into ECR using AWS CLI.
- **Pull and Run Image**: Pulls the Docker image from ECR and runs it.

---
<!-- nav -->
[[17-Setting Up Environment Variables for AWS ECR Integration|Setting Up Environment Variables for AWS ECR Integration]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]] | [[19-Tagging and Pushing Docker Images to ECR|Tagging and Pushing Docker Images to ECR]]
