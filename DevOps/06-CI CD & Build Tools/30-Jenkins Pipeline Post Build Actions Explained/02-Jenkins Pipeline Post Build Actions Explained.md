---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Jenkins Pipeline Post Build Actions Explained

In the context of continuous integration and delivery (CI/CD), Jenkins is one of the most widely used tools. A Jenkins pipeline is a way to model your entire software delivery process, from checking code into a version control system to deploying the built software to production. One crucial aspect of Jenkins pipelines is the ability to perform actions after the build process is completed, known as post-build actions. These actions can be configured using the `post` directive within a Jenkinsfile.

### Understanding the Jenkinsfile

A Jenkinsfile is a text file that contains the instructions for a Jenkins pipeline. It is written in Groovy and defines the steps that Jenkins should take to build, test, and deploy your application. The Jenkinsfile is typically stored in the root directory of your project repository.

#### Basic Syntax of a Jenkinsfile

Here is a basic example of a Jenkinsfile:

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

This Jenkinsfile defines three stages: `Build`, `Test`, and `Deploy`. Each stage contains a set of steps that are executed sequentially.

### Post Directive in Jenkinsfile

The `post` directive allows you to specify actions that should be taken after the pipeline completes, regardless of whether the build was successful or not. This is particularly useful for cleanup tasks, notifications, or other post-processing activities.

#### Syntax of the Post Directive

The `post` directive can be added at the end of the Jenkinsfile, outside the `stages` block. Here is an example:

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
    post {
        always {
            echo 'This will always run.'
        }
        success {
            echo 'This will run only if the build succeeds.'
        }
        failure {
            echo 'This will run only if the build fails.'
        }
    }
}
```

### Conditions in the Post Block

The `post` block supports several conditions that determine when the specified actions should be executed:

- **always**: Executes the action regardless of the build outcome.
- **success**: Executes the action only if the build succeeds.
- **failure**: Executes the action only if the build fails.
- **changed**: Executes the action if the build status has changed since the previous build.
- **unstable**: Executes the action if the build is unstable (e.g., tests fail but the build itself succeeds).

#### Example with Multiple Conditions

Here is a more comprehensive example that demonstrates the use of multiple conditions:

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
    post {
        always {
            echo 'This will always run.'
        }
        success {
            echo 'This will run only if the build succeeds.'
            // Send an email notification
            mail to: 'team@example.com',
                 subject: 'Build Successful',
                 body: 'The build was successful.'
        }
        failure {
            echo 'This will run only if the build fails.'
            // Send an email notification
            mail to: 'team@example.com',
                 subject: 'Build Failed',
                 body: 'The build failed.'
        }
        changed {
            echo 'This will run if the build status has changed.'
        }
        unstable {
            echo 'This will run if the build is unstable.'
        }
    }
}
```

### Real-World Examples and Use Cases

Post-build actions are often used for various purposes, such as sending notifications, archiving artifacts, or cleaning up resources. Here are some real-world examples:

#### Sending Email Notifications

Email notifications are a common use case for post-build actions. You can send emails to notify the development team about the build status.

```groovy
post {
    always {
        echo 'This will always run.'
    }
    success {
        echo 'This will run only if the build succeeds.'
        mail to: 'team@example.com',
             subject: 'Build Successful',
             body: 'The build was successful.'
    }
    failure {
        echo 'This will run only if the build fails.'
        mail to: 'team@example.com',
             subject: 'Build Failed',
             body: 'The build failed.'
    }
}
```

#### Archiving Artifacts

Another common use case is archiving build artifacts. This can be useful for debugging purposes or for keeping a record of the build output.

```groovy
post {
    always {
        echo 'This will always run.'
    }
    success {
        echo 'This will run only if the build succeeds.'
        archiveArtifacts artifacts: '**/*.jar', fingerprint: true
    }
    failure {
        echo 'This will run only if the build fails.'
    }
}
```

### Pitfalls and Best Practices

While post-build actions are powerful, they can also introduce issues if not used carefully. Here are some common pitfalls and best practices:

#### Avoiding Infinite Loops

Ensure that the actions in the `post` block do not cause infinite loops. For example, avoid triggering a new build within a post-build action.

#### Handling Errors Gracefully

Make sure that the actions in the `post` block handle errors gracefully. For example, if sending an email fails, ensure that the build does not fail as a result.

#### Logging and Debugging

Use logging and debugging techniques to understand what is happening during the post-build actions. This can help you diagnose issues and improve the reliability of your pipeline.

### How to Prevent / Defend

To ensure the security and reliability of your Jenkins pipeline, follow these best practices:

#### Secure Configuration Management

Ensure that your Jenkins configuration is secure. Use role-based access control (RBAC) to restrict access to sensitive information and actions.

#### Regular Audits

Regularly audit your Jenkins configurations and pipelines to identify and mitigate potential security risks.

#### Secure Coding Practices

Follow secure coding practices when writing your Jenkinsfiles. Use parameterized builds and avoid hardcoding sensitive information.

#### Example of Vulnerable vs. Secure Code

Here is an example of a vulnerable Jenkinsfile and its secure counterpart:

**Vulnerable Jenkinsfile**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
    }
    post {
        always {
            echo 'This will always run.'
        }
        success {
            echo 'This will run only if the build succeeds.'
            mail to: 'team@example.com',
                 subject: 'Build Successful',
                 body: 'The build was successful.'
        }
        failure {
            echo 'This will run only if the build fails.'
            mail to: 'team@example.com',
                 subject: 'Build Failed',
                 body: 'The build failed.'
        }
    }
}
```

**Secure Jenkinsfile**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
    }
    post {
        always {
            echo 'This will always run.'
        }
        success {
            echo 'This will run only if the build succeeds.'
            mail to: params.EMAIL_RECIPIENT,
                 subject: 'Build Successful',
                 body: 'The build was successful.'
        }
        failure {
            echo 'This will run only if the build fails.'
            mail to: params.EMAIL_RECIPIENT,
                 subject: 'Build Failed',
                 body: 'The build failed.'
        }
    }
}
```

In the secure version, the email recipient is passed as a parameter, which can be set securely through Jenkins configuration.

### Conclusion

Post-build actions in Jenkins pipelines are a powerful feature that allows you to automate various tasks after the build process is completed. By understanding the syntax and conditions available in the `post` directive, you can create robust and reliable pipelines that meet your specific needs. Always follow best practices to ensure the security and reliability of your Jenkins pipelines.

### Practice Labs

For hands-on practice with Jenkins pipelines and post-build actions, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that involve Jenkins pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application that includes challenges related to CI/CD pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Another web application with vulnerabilities, which can be used to practice securing CI/CD pipelines.
- **WebGoat**: An interactive web application that teaches web security principles, including some related to CI/CD pipelines.

These labs provide practical experience in setting up and securing Jenkins pipelines, including the use of post-build actions.

---
<!-- nav -->
[[01-Jenkins Pipeline Parameters and Post-Build Actions|Jenkins Pipeline Parameters and Post-Build Actions]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/30-Jenkins Pipeline Post Build Actions Explained/00-Overview|Overview]] | [[03-Jenkins Pipeline Post-Build Actions Explained|Jenkins Pipeline Post-Build Actions Explained]]
