---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Continuous Integration and Continuous Delivery (CI/CD) Pipelines

### Introduction to CI/CD Pipelines

Continuous Integration (CI) and Continuous Delivery (CD) are fundamental practices in modern software development. CI involves automatically building and testing code changes as they are committed to a version control system. CD extends CI by automatically deploying those changes to production or staging environments. Together, these practices ensure that code changes are integrated frequently, tested rigorously, and deployed reliably.

#### What is a CI/CD Pipeline?

A CI/CD pipeline is a series of steps that automate the process of building, testing, and deploying software. These steps typically include:

- **Source Code Management**: Version control systems like Git manage the source code.
- **Build**: Compiling the code into an executable form.
- **Test**: Running automated tests to ensure the code works as expected.
- **Deploy**: Automatically deploying the code to a target environment.

#### Why Use CI/CD Pipelines?

CI/CD pipelines offer several benefits:

- **Faster Feedback**: Developers receive immediate feedback on their code changes.
- **Reduced Bugs**: Automated testing catches issues early.
- **Improved Reliability**: Automated deployments reduce human error.
- **Increased Productivity**: Developers can focus on writing code rather than manual tasks.

### Formats for Defining CI/CD Pipelines

There are several formats for defining CI/CD pipelines, each with its own strengths and use cases.

#### Jenkinsfile

Jenkins is a popular open-source automation server that supports CI/CD pipelines. A `Jenkinsfile` is a script written in Groovy that defines the pipeline stages.

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'make'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'make deploy'
            }
        }
    }
}
```

#### Docker Compose

Docker Compose is used to define and run multi-container Docker applications. It uses a `docker-compose.yml` file to define services, networks, and volumes.

```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
  redis:
    image: "redis:alpine"
```

#### Kubernetes Manifests

Kubernetes is an orchestration platform for containerized applications. CI/CD pipelines can use Kubernetes manifests (`*.yaml`) to define and deploy applications.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:v1
        ports:
        - containerPort: 80
```

### Practical Example of a CI/CD Pipeline

Let's consider a practical example of a CI/CD pipeline using Jenkins.

#### Source Code Management

Assume we have a repository hosted on GitHub. The pipeline will trigger whenever changes are pushed to the master branch.

#### Build Stage

The build stage compiles the code and packages it into a distributable format.

```groovy
stage('Build') {
    steps {
        sh 'mvn clean package'
    }
}
```

#### Test Stage

The test stage runs automated tests to ensure the code works as expected.

```groovy
stage('Test') {
    steps {
        sh 'mvn test'
    }
}
```

#### Deploy Stage

The deploy stage deploys the packaged application to a target environment.

```groovy
stage('Deploy') {
    steps {
        sh 'scp target/my-app.jar user@server:/path/to/deploy/'
    }
}
```

### Hardening CI/CD Pipelines

Hardening is the process of reducing the attack surface of a system. In the context of CI/CD pipelines, hardening involves securing the pipeline itself and the artifacts it produces.

#### What is Hardening?

Hardening involves implementing security controls to minimize vulnerabilities and protect against attacks. This includes:

- **Access Control**: Limiting access to the pipeline and its components.
- **Encryption**: Encrypting sensitive data in transit and at rest.
- **Least Privilege**: Granting users and processes the minimum permissions necessary to perform their tasks.

#### Why is Hardening Important?

Hardening is crucial because CI/CD pipelines often handle sensitive information such as source code, credentials, and build artifacts. Without proper hardening, attackers could exploit vulnerabilities to gain unauthorized access or disrupt the pipeline.

#### How to Harden a CI/CD Pipeline

Here are some key steps to harden a CI/CD pipeline:

1. **Secure Access Control**:
   - Use role-based access control (RBAC) to limit who can access the pipeline.
   - Implement two-factor authentication (2FA) for critical actions.

2. **Encrypt Sensitive Data**:
   - Use encryption to protect sensitive data in transit and at rest.
   - Store secrets securely using tools like HashiCorp Vault or AWS Secrets Manager.

3. **Least Privilege**:
   - Ensure that build agents and other components have the minimum necessary permissions.
   - Use containerization to isolate build processes.

4. **Regular Audits**:
   - Perform regular security audits to identify and mitigate vulnerabilities.
   - Monitor pipeline activity for suspicious behavior.

### Real-World Examples of CI/CD Pipeline Attacks

Several high-profile breaches have involved compromised CI/CD pipelines. Here are a few recent examples:

#### SolarWinds Supply Chain Attack (CVE-2020-1014)

In December 2020, SolarWinds was compromised through a supply chain attack. The attackers injected malicious code into the SolarWinds Orion software, which was then distributed to customers. This attack highlights the importance of securing the entire software supply chain, including CI/CD pipelines.

#### Kaseya VSA Ransomware Attack (CVE-2021-30116)

In July 2021, Kaseya's VSA software was compromised, leading to a widespread ransomware attack. The attackers exploited a vulnerability in the software to inject malicious code into customer environments. This attack underscores the need for robust security measures in CI/CD pipelines to prevent similar incidents.

### Integrating Automated Security Testing into CI/CD Pipelines

Automated security testing is a critical component of a CI/CD pipeline. It ensures that security vulnerabilities are identified and addressed early in the development cycle.

#### What is Automated Security Testing?

Automated security testing involves using tools to automatically scan code and infrastructure for security vulnerabilities. This includes static application security testing (SAST), dynamic application security testing (DAST), and infrastructure as code (IaC) scanning.

#### Why Integrate Automated Security Testing?

Integrating automated security testing into a CI/CD pipeline offers several benefits:

- **Early Detection**: Identifies vulnerabilities early in the development cycle.
- **Consistency**: Ensures that security checks are consistently applied.
- **Efficiency**: Automates repetitive tasks, freeing developers to focus on writing code.

#### Tools for Automated Security Testing

Several tools are available for automated security testing:

- **SonarQube**: Static code analysis tool that identifies security vulnerabilities.
- **OWASP ZAP**: Dynamic application security testing tool that scans web applications.
- **Trivy**: Vulnerability scanner for container images.
- **Checkov**: Infrastructure as code (IaC) scanner that identifies security misconfigurations.

#### Example: Integrating SonarQube into a Jenkins Pipeline

Here’s an example of how to integrate SonarQube into a Jenkins pipeline using a `Jenkinsfile`.

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        stage('Security Scan') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/my-app.jar user@server:/path/to/deploy/'
            }
        }
    }
}
```

### How to Prevent / Defend Against CI/CD Pipeline Attacks

#### Detection

- **Monitor Pipeline Activity**: Use logging and monitoring tools to track pipeline activity and detect anomalies.
- **Security Scanning**: Regularly scan the pipeline and its artifacts for vulnerabilities.

#### Prevention

- **Secure Access Control**: Implement RBAC and 2FA to limit access to the pipeline.
- **Encrypt Sensitive Data**: Use encryption to protect sensitive data in transit and at rest.
- **Least Privilege**: Ensure that build agents and other components have the minimum necessary permissions.

#### Secure Coding Fixes

Here’s an example of a vulnerable and secure version of a pipeline configuration:

**Vulnerable Configuration**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/my-app.jar user@server:/path/to/deploy/'
            }
        }
    }
}
```

**Secure Configuration**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-credentials', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]) {
                    sh 'mvn clean package'
                }
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-credentials', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]) {
                    sh 'scp -i $PASSWORD target/my-app.jar $USER@server:/path/to/deploy/'
                }
            }
        }
    }
}
```

### Conclusion

Integrating automated security testing into a CI/CD pipeline is essential for ensuring the security of your software. By hardening the pipeline and regularly scanning for vulnerabilities, you can significantly reduce the risk of attacks. Remember that security is always a trade-off, and it’s important to balance security with availability and usability.

### Practice Labs

For hands-on experience with integrating automated security testing into CI/CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning security testing.
- **Jenkins Official Documentation**: Provides detailed guides and tutorials on setting up and configuring Jenkins pipelines.

By following these resources and best practices, you can effectively integrate automated security testing into your CI/CD pipeline and enhance the overall security of your software development process.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/04-Module Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/04-Module Summary/02-Practice Questions & Answers|Practice Questions & Answers]]
