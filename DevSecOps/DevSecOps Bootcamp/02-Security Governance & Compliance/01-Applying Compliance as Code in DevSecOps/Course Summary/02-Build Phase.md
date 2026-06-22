---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Build Phase

### Integrating Security Controls into the Build Process

#### What is the Build Phase?

The build phase is the stage where the source code is compiled and packaged into a deployable artifact. During this phase, security controls can be integrated to ensure that the final product meets security requirements.

#### Why is the Build Phase Important?

The build phase is important because it is the last chance to catch and fix security issues before the application is deployed. By integrating security controls into the build process, teams can ensure that the final artifact is secure and compliant.

#### How Does Integration Work?

Security controls can be integrated into the build process using various techniques:

1. **Policy Enforcement**: Enforce security policies during the build process.
2. **Dependency Checks**: Ensure that all dependencies are secure and up-to-date.
3. **Code Signing**: Sign the final artifact to ensure its integrity.

#### Real-World Example: Spectre and Meltdown (CVE-2017-5753, CVE-2017-5715)

The Spectre and Meltdown vulnerabilities affected processors and required firmware updates. By integrating security checks into the build process, teams could ensure that the final artifact included the necessary updates.

#### Tools for Build Phase Security

Some popular tools for integrating security into the build process include:

- **Travis CI**
- **CircleCI**
- **Jenkins**
- **GitHub Actions**

#### Example Configuration: Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Security Check') {
            steps {
                sh 'trivy image my-image:latest'
            }
        }
    }
}
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/01-Introduction to DevSecOps and Compliance as Code|Introduction to DevSecOps and Compliance as Code]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/03-Code Building and Testing Stage|Code Building and Testing Stage]]
