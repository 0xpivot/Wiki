---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to DevSecOps Pipeline with Static and Dynamic Security Scans

In the realm of modern software development, the integration of security practices throughout the development lifecycle is crucial. This is where DevSecOps comes into play, combining the principles of DevOps with security best practices. A comprehensive DevSecOps pipeline includes various stages such as static code analysis, dynamic application security testing (DAST), and continuous deployment. In this chapter, we will delve deep into the complete DevSecOps pipeline, focusing on static and dynamic security scans, and how they integrate into the overall deployment process.

### What is DevSecOps?

DevSecOps is an approach to software development that integrates security practices into the DevOps lifecycle. Traditionally, security was often treated as an afterthought, added late in the development cycle. However, in DevSecOps, security is embedded at every stage of the development process, ensuring that applications are secure from the ground up.

#### Why DevSecOps Matters

The importance of DevSecOps lies in its ability to address security issues early and often, reducing the likelihood of vulnerabilities making it into production. By integrating security into the continuous integration and continuous deployment (CI/CD) pipeline, organizations can catch and fix security issues more efficiently, leading to more robust and secure applications.

### Components of a DevSecOps Pipeline

A typical DevSecOps pipeline consists of several key components:

1. **Source Code Management**: Version control systems like Git are used to manage the source code.
2. **Static Application Security Testing (SAST)**: Tools that analyze the source code for potential security vulnerabilities.
3. **Dependency Scanning**: Tools that check third-party libraries and dependencies for known vulnerabilities.
4. **Image Scanning**: Tools that scan container images for vulnerabilities.
5. **Dynamic Application Security Testing (DAST)**: Tools that test the application in a runtime environment.
6. **Continuous Integration (CI)**: Automated builds and tests.
7. **Continuous Deployment (CD)**: Automated deployment of the application.
8. **Manual Testing and Review**: Final checks and reviews before deployment.
9. **Production Deployment**: Manual or automated deployment to the production environment.

### Static Application Security Testing (SAST)

SAST tools analyze the source code to identify potential security vulnerabilities. These tools can detect issues such as SQL injection, cross-site scripting (XSS), buffer overflows, and other common security flaws.

#### How SAST Works

SAST tools work by parsing the source code and applying a set of rules or heuristics to identify patterns that may indicate security vulnerabilities. These tools can operate at different levels of abstraction, from high-level language constructs to low-level machine instructions.

##### Example: SonarQube

SonarQube is a popular SAST tool that provides a comprehensive suite of features for static code analysis. Here’s how you might configure SonarQube in a CI/CD pipeline:

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }
    }
}
```

In this example, the `withSonarQubeEnv` step sets up the necessary environment variables for SonarQube, and the `sh 'mvn sonar:sonar'` command triggers the analysis.

#### Common Pitfalls and How to Prevent Them

One common pitfall with SAST tools is false positives—issues flagged as potential vulnerabilities that turn out to be benign. To mitigate this, it’s important to configure the tool properly and to review the findings carefully.

**How to Prevent False Positives:**

- **Configure Rulesets**: Customize the rulesets to match your specific application and environment.
- **Review Findings**: Manually review the findings to ensure they are valid.
- **Use Contextual Analysis**: Some tools offer contextual analysis, which can help reduce false positives.

### Dependency Scanning

Dependency scanning tools check third-party libraries and dependencies for known vulnerabilities. This is crucial because many security breaches occur due to outdated or vulnerable dependencies.

#### How Dependency Scanning Works

Dependency scanning tools typically work by comparing the dependencies listed in your project (e.g., `package.json`, `requirements.txt`) against a database of known vulnerabilities. They can also check for outdated dependencies that may contain security patches.

##### Example: Snyk

Snyk is a popular dependency scanning tool that integrates seamlessly with CI/CD pipelines. Here’s how you might use Snyk in a pipeline:

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
            }
        }
        stage('Snyk Scan') {
            steps {
                sh 'snyk test --file=package.json'
            }
        }
    }
}
```

In this example, the `snyk test` command scans the dependencies listed in `package.json`.

#### Common Pitfalls and How to Prevent Them

One common issue with dependency scanning is the reliance on public databases of vulnerabilities, which may not always be up-to-date. Additionally, some dependencies may not be covered by these databases.

**How to Prevent Outdated Dependencies:**

- **Regular Scans**: Run dependency scans regularly to catch new vulnerabilities.
- **Automate Updates**: Use tools that automatically update dependencies to their latest versions.
- **Monitor Vulnerability Feeds**: Stay informed about new vulnerabilities by monitoring feeds like NVD (National Vulnerability Database).

### Image Scanning

Container images are increasingly used in modern applications, and it’s essential to ensure that these images are free from vulnerabilities. Image scanning tools analyze container images to identify potential security issues.

#### How Image Scanning Works

Image scanning tools typically work by analyzing the layers of a container image and checking them against a database of known vulnerabilities. They can also check for misconfigurations and other security issues.

##### Example: Clair

Clair is an open-source image scanner that can be integrated into CI/CD pipelines. Here’s how you might use Clair:

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-image .'
            }
        }
        stage('Clair Scan') {
            steps {
                sh 'clair-scanner --image my-image'
            }
        }
    }
}
```

In this example, the `clair-scanner` command scans the `my-image` container image.

#### Common Pitfalls and How to Prevent Them

One common issue with image scanning is the potential for false negatives—vulnerabilities that are not detected. This can happen if the image contains custom layers that are not covered by the vulnerability database.

**How to Prevent False Negatives:**

- **Custom Layers**: Ensure that custom layers are thoroughly reviewed and scanned.
- **Regular Updates**: Keep the vulnerability database up-to-date.
- **Manual Reviews**: Conduct manual reviews of custom layers to catch potential issues.

### Dynamic Application Security Testing (DAST)

DAST tools test the application in a runtime environment to identify security vulnerabilities. Unlike SAST, which analyzes the source code, DAST simulates attacks on the running application to identify weaknesses.

#### How DAST Works

DAST tools typically work by sending malicious input to the application and observing the response. They can detect issues such as SQL injection, XSS, and other runtime vulnerabilities.

##### Example: ZAP (Zed Attack Proxy)

ZAP is a popular DAST tool that can be integrated into CI/CD pipelines. Here’s how you might use ZAP:

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Deploy to Test Environment') {
            steps {
                sh 'docker-compose up -d'
            }
        }
        stage('ZAP Scan') {
            steps {
                sh 'zap-baseline.py -t http://localhost:8080 -r zap-report.html'
            }
        }
    }
}
```

In this example, the `zap-baseline.py` script runs a DAST scan on the application running at `http://localhost:8080`.

#### Common Pitfalls and How to Prevent Them

One common issue with DAST is the potential for false positives—issues flagged as potential vulnerabilities that turn out to be benign. Additionally, DAST can miss vulnerabilities that are not triggered by the specific inputs used during the scan.

**How to Prevent False Positives:**

- **Configure Rulesets**: Customize the rulesets to match your specific application and environment.
- **Review Findings**: Manually review the findings to ensure they are valid.
- **Use Contextual Analysis**: Some tools offer contextual analysis, which can help reduce false positives.

### Continuous Integration (CI) and Continuous Deployment (CD)

CI and CD are integral parts of the DevSecOps pipeline. CI ensures that the codebase is always in a working state, while CD automates the deployment process.

#### How CI/CD Works

CI/CD pipelines automate the build, test, and deployment processes. They typically consist of multiple stages, each of which performs a specific task.

##### Example: Jenkins Pipeline

Here’s an example of a Jenkins pipeline that includes SAST, dependency scanning, image scanning, and DAST:

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }
        stage('Snyk Scan') {
            steps {
                sh 'snyk test --file=package.json'
            }
        }
        stage('Clair Scan') {
            steps {
                sh 'clair-scanner --image my-image'
            }
        }
        stage('Deploy to Test Environment') {
            steps {
                sh 'docker-compose up -d'
            }
        }
        stage('ZAP Scan') {
            steps {
                sh 'zap-baseline.py -t http://localhost:8080 -r zap-report.html'
            }
        }
        stage('Manual Testing') {
            steps {
                echo 'Perform manual testing and review.'
            }
        }
        stage('Deploy to Production') {
            steps {
                echo 'Manually trigger deployment to production.'
            }
        }
    }
}
```

In this example, the pipeline includes stages for building, analyzing the code with SonarQube, scanning dependencies with Snyk, scanning the container image with Clair, deploying to a test environment, running a DAST scan with ZAP, performing manual testing, and deploying to production.

#### Common Pitfalls and How to Prevent Them

One common issue with CI/CD is the potential for security vulnerabilities to make it into production if the pipeline is not properly configured. Additionally, manual testing and review are critical to catching issues that automated tools may miss.

**How to Prevent Security Issues in CI/CD:**

- **Configure Security Tools**: Ensure that all security tools are properly configured and integrated into the pipeline.
- **Manual Testing**: Perform thorough manual testing and review before deploying to production.
- **Automated Deployments**: Use automated deployments to reduce the risk of human error.

### Manual Testing and Review

Manual testing and review are critical components of the DevSecOps pipeline. While automated tools can catch many issues, they cannot replace human judgment and expertise.

#### How Manual Testing Works

Manual testing involves reviewing the application for security vulnerabilities and conducting functional testing to ensure that the application works as intended.

##### Example: Manual Testing Checklist

Here’s an example of a manual testing checklist:

- **Security Review**: Review the application for security vulnerabilities.
- **Functional Testing**: Test the application for functionality.
- **Performance Testing**: Test the application for performance.
- **Usability Testing**: Test the application for usability.

#### Common Pitfalls and How to Prevent Them

One common issue with manual testing is the potential for human error. Additionally, manual testing can be time-consuming and resource-intensive.

**How to Prevent Human Error:**

- **Checklists**: Use checklists to ensure that all aspects of the application are tested.
- **Training**: Train testers on the proper techniques for manual testing.
- **Automation**: Use automation to assist with manual testing.

### Production Deployment

Once all the previous stages have been completed successfully, the application can be deployed to production. This is typically done manually to ensure that the application is ready for production.

#### How Production Deployment Works

Production deployment involves deploying the application to the production environment. This is typically done manually to ensure that the application is ready for production.

##### Example: Manual Deployment

Here’s an example of a manual deployment process:

- **Review Reports**: Review the reports generated by the security tools.
- **Manual Testing**: Perform manual testing and review.
- **Deploy to Production**: Deploy the application to the production environment.

#### Common Pitfalls and How to Prevent Them

One common issue with production deployment is the potential for security vulnerabilities to make it into production. Additionally, manual deployment can be time-consuming and resource-intensive.

**How to Prevent Security Issues in Production Deployment:**

- **Review Reports**: Review the reports generated by the security tools.
- **Manual Testing**: Perform thorough manual testing and review.
- **Automated Deployments**: Use automated deployments to reduce the risk of human error.

### Conclusion

In conclusion, a comprehensive DevSecOps pipeline includes various stages such as static code analysis, dependency scanning, image scanning, dynamic application security testing, continuous integration, continuous deployment, manual testing, and production deployment. By integrating security practices into the CI/CD pipeline, organizations can catch and fix security issues more efficiently, leading to more robust and secure applications.

### Practice Labs

To gain hands-on experience with DevSecOps, consider the following practice labs:

- **PortSwigger Web Security Academy**: Focuses on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: Another deliberately insecure web application for practicing web security.
- **WebGoat**: An interactive training application for learning web security.
- **CloudGoat**: Focuses on cloud security and AWS-specific challenges.
- **flaws.cloud**: Provides a series of cloud-based challenges for practicing cloud security.
- **Pacu**: A collection of AWS security tools for penetration testing.
- **Kubernetes Goat**: Focuses on Kubernetes security and container orchestration.
- **OWASP WrongSecrets**: A series of challenges for practicing secure coding and security best practices.
- **kube-hunter**: A tool for discovering and exploiting security issues in Kubernetes clusters.

These labs provide practical experience with the concepts covered in this chapter, allowing you to apply your knowledge in a real-world context.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/02-Overview of Complete DevSecOps Pipeline with Static and Dynamic Security Scans/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/02-Overview of Complete DevSecOps Pipeline with Static and Dynamic Security Scans/02-Practice Questions & Answers|Practice Questions & Answers]]
