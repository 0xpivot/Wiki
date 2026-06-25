---
course: DevSecOps
topic: Differentiating the Pros and Cons of Automated Security Testing
tags: [devsecops]
---

## Blocking Builds on Security Failures

### What is Build Blocking?

Build blocking refers to the practice of preventing a build from proceeding to further stages (such as deployment) if certain conditions are not met. In the context of security testing, build blocking ensures that insecure components are not deployed to production environments.

### Why Does Build Blocking Matter?

Build blocking is crucial because it enforces strict security policies throughout the development lifecycle. By blocking builds that fail security tests, organizations can prevent insecure code from reaching end-users, reducing the risk of security breaches.

### How Does Build Blocking Work?

Build blocking typically involves integrating security testing tools into the CI/CD pipeline. When a security test fails, the pipeline is halted, and the build is not allowed to proceed. This ensures that only secure components are deployed.

#### Example: Build Blocking with Jenkins and SonarQube

Here’s how build blocking can be implemented using Jenkins and SonarQube:

```yaml
# Jenkinsfile example with build blocking
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
                sh 'mvn sonar:sonar'
            }
        }
        stage('Quality Gate') {
            steps {
                script {
                    def qg = waitForQualityGate()
                    if (qg.status != 'OK') {
                        error "Pipeline aborted due to quality gate failure: ${qg.status}"
                    }
                }
            }
        }
    }
}
```

In this example, the `Quality Gate` stage waits for the SonarQube quality gate to pass. If the quality gate fails, the pipeline is aborted, preventing the deployment of insecure code.

### Real-World Example: Build Blocking in Production Environments

Consider a financial institution that deploys critical applications to production environments. By implementing build blocking, the institution ensures that only secure components are deployed, reducing the risk of security breaches that could compromise sensitive data.

### Pitfalls of Build Blocking

While build blocking is effective, it can also lead to delays in the development process if security tests are overly stringent. This can cause frustration among developers and slow down the release cycle.

### How to Prevent / Defend

To balance security and development speed, it is important to configure build blocking rules carefully. This includes setting appropriate thresholds for security issues and providing clear feedback to developers on how to resolve issues.

```yaml
# Example of configuring SonarQube quality gate
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
```

These settings ensure that the pipeline waits for the quality gate to pass and sets a timeout to avoid indefinite waiting.

---
<!-- nav -->
[[12-4. Logging and Monitoring|4. Logging and Monitoring]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/05-Differentiating the Pros and Cons of Automated Security Testing/The Pros and Cons of Automated Security Testing/00-Overview|Overview]] | [[14-Changing Test Results Over Time|Changing Test Results Over Time]]
