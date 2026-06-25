---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins Shared Libraries

In the realm of continuous integration and continuous delivery (CI/CD), Jenkins has emerged as a leading tool due to its flexibility and extensive plugin ecosystem. One of the key features that enhance Jenkins' utility is the **Jenkins Shared Library**. This feature allows teams to share common code and logic across multiple projects, promoting consistency, reducing redundancy, and fostering collaboration.

### What is a Jenkins Shared Library?

A Jenkins Shared Library is a collection of reusable code that can be referenced and used within Jenkins pipelines. This library is typically stored in a separate Git repository and can contain Groovy scripts, classes, and methods that encapsulate common tasks such as building, testing, deploying, and notifying stakeholders.

#### Why Use Jenkins Shared Libraries?

1. **Code Reusability**: Avoid duplicating the same logic across multiple pipelines.
2. **Consistency**: Ensure that common tasks are performed consistently across different projects.
3. **Collaboration**: Promote knowledge sharing and collaboration among different teams.
4. **Maintenance**: Simplify maintenance by centralizing common logic in one place.

### Example Scenario

Consider a scenario where multiple teams within a company are developing microservices. Each team might be using different technologies, but they all need to push their artifacts to a company-wide Nexus repository, notify a company-wide Slack channel, and provide support through a common email address. Without a shared library, each team would have to implement this logic independently, leading to inconsistencies and redundant code.

### Creating a Jenkins Shared Library

To create a Jenkins Shared Library, follow these steps:

1. **Create a Git Repository**: Store the shared library in a Git repository.
2. **Define the Structure**: Organize the library into logical directories.
3. **Configure Jenkins**: Make the shared library available in Jenkins.

#### Step-by-Step Guide

1. **Create a Git Repository**

   Create a new Git repository to store your shared library. For example, you can name it `jenkins-shared-library`.

   ```bash
   git init jenkins-shared-library
   cd jenkins-shared-library
   ```

2. **Define the Structure**

   The typical structure of a Jenkins Shared Library includes the following directories:

   - `vars`: Contains global variables and functions.
   - `src`: Contains Java classes and Groovy scripts.
   - `resources`: Contains resource files like templates.

   Here’s an example directory structure:

   ```
   jenkins-shared-library/
   ├── vars/
   │   └── slackNotification.groovy
   ├── src/
   │   └── com/
   │       └── company/
   │           └── nexus/
   │               └── NexusPush.groovy
   └── resources/
       └── templates/
           └── emailTemplate.txt
   ```

3. **Write Shared Functions**

   Let’s write a simple function to notify a Slack channel.

   ```groovy
   // vars/slackNotification.groovy
   def call(String message) {
       slackSend(color: 'good', message: message)
   }
   ```

   And a function to push artifacts to a Nexus repository.

   ```groovy
   // src/com/company/nexus/NexusPush.groovy
   package com.company.nexus

   class NexusPush {
       def pushArtifact(String artifactPath) {
           // Logic to push artifact to Nexus
           echo "Pushing ${artifactPath} to Nexus"
       }
   }
   ```

4. **Configure Jenkins**

   To make the shared library available in Jenkins, you need to configure the Jenkins instance.

   - Go to **Manage Jenkins > Configure System**.
   - Scroll down to the **Global Pipeline Libraries** section.
   - Click **Add** and enter the details of your shared library repository.

   ```json
   {
     "name": "jenkins-shared-library",
     "defaultVersion": "master",
     "repository": "https://github.com/yourorg/jenkins-shared-library.git",
     "credentialsId": "your-github-credentials-id"
   }
   ```

### Using the Shared Library in a Jenkinsfile

Once the shared library is configured, you can use it in your Jenkinsfiles.

```groovy
// Jenkinsfile
@Library('jenkins-shared-library') _

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    def nexus = new com.company.nexus.NexusPush()
                    nexus.pushArtifact('path/to/artifact')
                }
            }
        }
        stage('Notify') {
            steps {
                slackNotification("Build completed successfully")
            }
        }
    }
}
```

### Real-World Examples

#### Example 1: Consistent Artifact Management

Imagine a company with multiple teams developing microservices. Each team needs to push their artifacts to a company-wide Nexus repository. By using a shared library, the logic for pushing artifacts can be centralized, ensuring consistency and reducing the risk of errors.

#### Example 2: Centralized Notification System

Another common requirement is to notify stakeholders via a company-wide Slack channel. A shared library can encapsulate this logic, making it easy for teams to integrate notifications into their pipelines.

### Pitfalls and Best Practices

#### Common Mistakes

1. **Overcomplicating the Library**: Keep the shared library simple and focused on common tasks.
2. **Inconsistent Naming Conventions**: Use consistent naming conventions to avoid confusion.
3. **Lack of Documentation**: Document the shared library thoroughly to ensure usability.

#### Best Practices

1. **Version Control**: Use version control to manage changes to the shared library.
2. **Testing**: Regularly test the shared library to ensure it works as expected.
3. **Documentation**: Provide comprehensive documentation for the shared library.

### How to Prevent / Defend

#### Detection

- **Static Code Analysis**: Use tools like SonarQube to analyze the shared library for potential issues.
- **Automated Testing**: Implement automated tests to verify the functionality of the shared library.

#### Prevention

- **Code Reviews**: Conduct regular code reviews to catch and fix issues early.
- **Access Controls**: Restrict access to the shared library repository to prevent unauthorized changes.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a function:

**Vulnerable Version**

```groovy
def pushArtifact(String artifactPath) {
    // Vulnerable code
    sh "curl -X POST http://nexus/repository/${artifactPath}"
}
```

**Secure Version**

```groovy
def pushArtifact(String artifactPath) {
    // Secure code
    def nexusUrl = env.NEXUS_URL
    sh "curl -X POST ${nexusUrl}/repository/${artifactPath}"
}
```

### Conclusion

Jenkins Shared Libraries are a powerful tool for promoting consistency, reusability, and collaboration in CI/CD pipelines. By centralizing common logic, teams can focus on their core tasks while ensuring that critical operations are performed correctly and consistently.

### Practice Labs

For hands-on practice with Jenkins Shared Libraries, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to CI/CD pipelines and shared libraries.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be integrated with Jenkins pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Useful for learning about web application security in the context of CI/CD.

By following these guidelines and practicing with real-world examples, you can master the use of Jenkins Shared Libraries in your DevOps workflows.

---
<!-- nav -->
[[01-Introduction to Jenkins Pipelines for Microservice Applications|Introduction to Jenkins Pipelines for Microservice Applications]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/33-Jenkins Pipelines for Microservice Applications/00-Overview|Overview]] | [[03-Initializing and Pushing to a Remote Repository|Initializing and Pushing to a Remote Repository]]
