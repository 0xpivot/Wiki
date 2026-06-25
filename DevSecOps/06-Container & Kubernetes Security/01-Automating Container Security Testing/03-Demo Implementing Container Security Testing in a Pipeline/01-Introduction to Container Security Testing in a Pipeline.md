---
course: DevSecOps
topic: Automating Container Security Testing
tags: [devsecops]
---

## Introduction to Container Security Testing in a Pipeline

Container security testing is a critical component of modern DevSecOps practices. Containers encapsulate applications and their dependencies, making them portable and consistent across different environments. However, this portability also introduces security challenges, such as vulnerabilities within the base images, misconfigurations, and runtime attacks. To address these issues, integrating container security testing into the continuous integration/continuous deployment (CI/CD) pipeline is essential.

### Background Theory

Containers are lightweight, standalone, executable packages that include everything needed to run an application: code, runtime, system tools, libraries, and settings. They rely on the underlying operating system kernel and share it with other containers, which makes them more efficient than virtual machines (VMs).

#### Key Concepts

- **Docker**: A popular platform for developing, shipping, and running applications inside containers.
- **Jenkins**: An open-source automation server used to automate parts of the software development process, including building, testing, and deploying applications.
- **CI/CD Pipeline**: A series of steps that automate the process of integrating code changes from multiple contributors, building the software, and deploying it to production.

### Setting Up the Environment

For this demonstration, we will be working with the **OWASP Juice Shop** project, a deliberately insecure web application designed for security training. We will integrate container security testing into its existing Jenkins pipeline.

#### Prerequisites

- **Docker**: Ensure Docker is installed and running on your machine.
- **Jenkins**: Set up a Jenkins instance and configure it to work with your Git repository.
- **Git Repository**: Clone the OWASP Juice Shop repository to your local machine.

```bash
git clone https://github.com/bkimminich/juice-shop.git
cd juice-shop
```

### Creating a New Branch

Before making any changes, it's crucial to create a new branch to isolate your modifications.

```bash
git checkout -b container-scanning
```

### Modifying the Jenkinsfile

The `Jenkinsfile` defines the pipeline stages and steps. We will add three new stages: `Build Image`, `Push to Registry`, and `Scanner`.

#### Adding Variables

First, define a variable to store the Docker image name.

```groovy
def dockerImage = 'juice-shop'
```

#### Build Image Stage

This stage builds the Docker image based on the `Dockerfile` in the repository.

```groovy
stage('Build Image') {
    steps {
        script {
            def tag = "${dockerImage}:${env.BRANCH_NAME}"
            sh "docker build -t ${tag} ."
        }
    }
}
```

#### Push to Registry Stage

This stage pushes the built Docker image to a registry server.

```groovy
stage('Push to Registry') {
    steps {
        script {
            def tag = "${dockerImage}:${env.BRANCH_NAME}"
            sh "docker push ${tag}"
        }
    }
}
```

### Scanner Stage

This stage scans the Docker image for vulnerabilities and ensures that the build fails if the policy check fails.

#### Using Trivy for Scanning

Trivy is a vulnerability scanner for containers and other artifacts. We will use Trivy to scan the Docker image.

```groovy
stage('Scanner') {
    steps {
        script {
            def tag = "${dockerImage}:${env.BRANCH_NAME}"
            sh "trivy image --exit-code 1 --severity CRITICAL,HIGH ${tag}"
        }
    }
}
```

### Full Jenkinsfile Example

Here is the complete `Jenkinsfile` with the added stages:

```groovy
pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'juice-shop'
    }
    stages {
        stage('Build Image') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "docker build -t ${tag} ."
                }
            }
        }
        stage('Push to Registry') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "docker push ${tag}"
                }
            }
        }
        stage('Scanner') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "trivy image --exit-code 1 --severity CRITICAL,HIGH ${tag}"
                }
            }
        }
    }
}
```

### How to Prevent / Defend

#### Detection

To detect vulnerabilities in Docker images, use tools like Trivy, Clair, or Anchore. These tools scan the images for known vulnerabilities and provide detailed reports.

#### Prevention

1. **Use Secure Base Images**: Always start with trusted base images from reputable sources.
2. **Regularly Update Dependencies**: Keep all dependencies up-to-date to avoid known vulnerabilities.
3. **Implement Security Policies**: Define and enforce security policies using tools like Open Policy Agent (OPA) or Aqua Security.

#### Secure Code Fix

Compare the vulnerable and secure versions of the `Jenkinsfile`:

**Vulnerable Version**

```groovy
pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'juice-shop'
    }
    stages {
        stage('Build Image') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "docker build -t ${tag} ."
                }
            }
        }
        stage('Push to Registry') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "docker push ${tag}"
                }
            }
        }
    }
}
```

**Secure Version**

```groovy
pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'juice-shop'
    }
    stages {
        stage('Build Image') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "docker build -t ${tag} ."
                }
            }
        }
        stage('Push to Registry') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "docker push ${tag}"
                }
            }
        }
        stage('Scanner') {
            steps {
                script {
                    def tag = "${DOCKER_IMAGE}:${env.BRANCH_NAME}"
                    sh "trivy image --exit-code 1 --severity CRITICAL,HIGH ${tag}"
                }
            }
        }
    }
}
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21315**: A vulnerability in the Docker daemon allowed unauthorized access to the host system.
- **CVE-2021-21316**: Another vulnerability in the Docker daemon allowed attackers to execute arbitrary code on the host system.

These vulnerabilities highlight the importance of regular updates and security testing in containerized environments.

### Hands-On Labs

For practical experience with container security testing, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security, including container security.
- **OWASP Juice Shop**: Provides a deliberately insecure web application for security training.
- **Kubernetes Goat**: Focuses on Kubernetes security and provides hands-on exercises.

### Conclusion

Integrating container security testing into the CI/CD pipeline is essential for maintaining the security and integrity of containerized applications. By using tools like Trivy and following best practices, you can ensure that your containers are free from vulnerabilities and securely configured.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/01-Automating Container Security Testing/03-Demo Implementing Container Security Testing in a Pipeline/00-Overview|Overview]] | [[02-Automating Container Security Testing in a Pipeline|Automating Container Security Testing in a Pipeline]]
