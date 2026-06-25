---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Creating a Jenkins Pipeline

A Jenkins pipeline is defined using a Jenkinsfile, which is a script written in Groovy. This script defines the stages and steps of the pipeline.

### Example Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'mvn clean install'
            }
        }
        stage('Verify Software Build Materials') {
            steps {
                dependencyTrackServer 'http://localhost:8080', 'Tools Image Project'
            }
        }
    }
}
```

### Explanation of the Jenkinsfile

- **agent any**: Specifies that the pipeline can run on any available agent.
- **stage('Build')**: Defines the build stage, where the Maven build command is executed.
- **stage('Verify Software Build Materials')**: Defines the verification stage, where the Dependency Track plugin is used to analyze the dependencies.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Integrating Automated Security Testing into a Jenkins Pipeline Using Plugins/02-Introduction to Jenkins and Integrating Automated Security Testing|Introduction to Jenkins and Integrating Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Integrating Automated Security Testing into a Jenkins Pipeline Using Plugins/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Integrating Automated Security Testing into a Jenkins Pipeline Using Plugins/04-Hands-On Labs|Hands-On Labs]]
