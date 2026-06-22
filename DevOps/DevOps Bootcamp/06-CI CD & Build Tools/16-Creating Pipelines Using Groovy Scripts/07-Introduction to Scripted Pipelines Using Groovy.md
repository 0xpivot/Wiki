---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Scripted Pipelines Using Groovy

Scripted pipelines in Jenkins provide a powerful way to define complex build and deployment workflows using Groovy scripts. Groovy is a versatile scripting language that integrates seamlessly with Jenkins, allowing you to leverage its rich set of features to create sophisticated pipelines.

### What Is a Scripted Pipeline?

A scripted pipeline in Jenkins is defined using a Groovy script. This script contains the logic for building, testing, and deploying your application. Unlike freestyle jobs, which are configured through a GUI, scripted pipelines are defined programmatically, providing greater flexibility and control.

#### Benefits of Scripted Pipelines

1. **Complex Logic**: Scripted pipelines can handle complex logic, including conditional statements, loops, and parallel execution.
2. **Maintainability**: Groovy scripts are easier to maintain and version control compared to GUI configurations.
3. **Reusability**: You can reuse Groovy scripts across multiple pipelines, reducing redundancy and improving consistency.

### Example: Running Unit Tests and Integration Tests in Parallel

Let's revisit the scenario of running unit tests and integration tests in parallel. With a scripted pipeline, you can easily define this logic using Groovy.

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
            parallel {
                stage('Unit Tests') {
                    steps {
                        echo 'Running unit tests...'
                    }
                }
                stage('Integration Tests') {
                    steps {
                        echo 'Running integration tests...'
                    }
                }
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

### Conditional Logic in Scripted Pipelines

Scripted pipelines also support conditional logic, allowing you to make decisions based on certain conditions. For example, you might want to run a specific set of tests only if a particular branch is being built.

```groovy
pipeline {
    agent any
    environment {
        BRANCH_NAME = "${env.BRANCH_NAME}"
    }
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            when {
                expression { return env.BRANCH_NAME == 'master' }
            }
            steps {
                echo 'Running master-specific tests...'
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

### User Input in Scripted Pipelines

Another advantage of scripted pipelines is the ability to incorporate user input. For instance, you might want to prompt the user to select a version for the next step.

```groovy
pipeline {
    agent any
    stages {
        stage('Select Version') {
            steps {
                script {
                    def version = input id: 'versionInput', message: 'Select a version', parameters: [string(name: 'VERSION', defaultValue: '1.0.0', description: 'Enter the version')]
                    echo "Selected version: ${version}"
                }
            }
        }
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Deploy')  {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
```

### How to Prevent / Defend Against Issues

While scripted pipelines offer significant advantages, it's important to ensure that your pipelines are secure and maintainable. Here are some best practices:

#### Secure Coding Practices

1. **Use Environment Variables**: Store sensitive information like API keys and passwords in environment variables rather than hardcoding them in your scripts.
2. **Validate User Input**: Always validate user input to prevent injection attacks or other security vulnerabilities.
3. **Use Secure Libraries**: Ensure that any third-party libraries or plugins you use are up-to-date and free from known vulnerabilities.

#### Example of Secure Coding

Here’s an example of a secure Groovy script that uses environment variables and validates user input:

```groovy
pipeline {
    agent any
    environment {
        API_KEY = credentials('api-key')
    }
    stages {
        stage('Select Version') {
            steps {
                script {
                    def version = input id: 'versionInput', message: 'Select a version', parameters: [string(name: 'VERSION', defaultValue: '1.0.0', description: 'Enter the version')]
                    if (!version.matches('\\d+\\.\\d+\\.\\d+')) {
                        error("Invalid version format")
                    }
                    echo "Selected version: ${version}"
                }
            }
        }
        stage('Build') {
            steps {
                echo 'Building...'
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

#### Detection and Prevention

To detect and prevent issues in your scripted pipelines, consider the following:

1. **Code Reviews**: Regularly review your Groovy scripts to identify potential security vulnerabilities or inefficiencies.
2. **Automated Testing**: Implement automated testing for your pipelines to catch errors and security issues early.
3. **Monitoring and Logging**: Monitor your pipelines and log important events to detect and respond to issues promptly.

### Real-World Examples and Recent Breaches

Recent breaches and CVEs highlight the importance of securing your CI/CD pipelines. For example, the Log4j vulnerability (CVE-2021-44228) affected many systems, including CI/CD pipelines. Ensuring that your pipelines are secure and up-to-date is crucial to preventing such vulnerabilities.

### Hands-On Practice Labs

To gain practical experience with scripted pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security, including CI/CD pipelines.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing and CI/CD integration.
- **DVWA (Damn Vulnerable Web Application)**: Another resource for practicing web application security and integrating CI/CD pipelines.

By following these guidelines and best practices, you can effectively transition from freestyle jobs to scripted pipelines using Groovy, ensuring that your CI/CD processes are robust, maintainable, and secure.

---
<!-- nav -->
[[06-Introduction to Pipeline Creation Using Groovy Scripts|Introduction to Pipeline Creation Using Groovy Scripts]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/16-Creating Pipelines Using Groovy Scripts/00-Overview|Overview]] | [[08-Groovy Scripts in Jenkins|Groovy Scripts in Jenkins]]
