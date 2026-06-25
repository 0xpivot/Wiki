---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Build Triggers in Jenkins

In the context of continuous integration and continuous delivery (CI/CD), build triggers play a crucial role in automating the process of building, testing, and deploying software. Jenkins, one of the most popular open-source automation servers, provides several mechanisms to trigger builds based on different criteria. This chapter will delve into the various types of build triggers available in Jenkins, their use cases, and how to configure them effectively.

### Manual vs. Automatic Build Triggers

One of the primary decisions in setting up a CI/CD pipeline is whether to trigger builds automatically or manually. 

#### Automatic Build Triggers

Automatic build triggers are typically used for environments such as development and staging. These triggers ensure that changes are tested and integrated quickly, reducing the risk of issues accumulating over time. Common triggers include:

- **Commit-based Triggers**: Automatically trigger a build whenever a new commit is pushed to the repository. This ensures that every change is validated before it affects other parts of the system.
  
- **Pull Request Triggers**: Trigger builds when a pull request is opened or updated. This allows you to test changes in isolation before merging them into the main branch.

#### Manual Build Triggers

Manual build triggers are often used for production environments. This approach gives you more control over when and what gets deployed, ensuring that you can validate the changes thoroughly before making them live. 

### Scheduling Builds

Another common use case for build triggers is scheduling builds at specific times. This is particularly useful for long-running tests or maintenance tasks that should not interfere with regular development activities.

#### Use Case: Long-Running Selenium Tests

Consider a scenario where you have extensive Selenium tests that take around two hours to complete. Running these tests every time a commit is made would overload the Jenkins server and delay other builds. Instead, you can schedule these tests to run at night when the server load is lower.

```mermaid
sequenceDiagram
    participant Developer
    participant Jenkins
    participant TestServer
    Developer->>Jenkins: Commit Code
    Jenkins->>TestServer: Run Short Tests
    loop Nightly Schedule
        Jenkins->>TestServer: Run Long Selenium Tests
    end
```

#### Use Case: Maintenance Jobs

Maintenance jobs, such as cleaning up old builds or performing backups, can also be scheduled to run at specific times. This ensures that these tasks do not interfere with regular development activities.

### Configuring Build Triggers in Jenkins

To configure build triggers in Jenkins, you need to set up the appropriate triggers in your Jenkins job configurations. Here’s how to configure both automatic and manual triggers, along with scheduling.

#### Automatic Build Triggers

1. **Commit-based Triggers**:
   
   To configure a commit-based trigger, you need to integrate Jenkins with your version control system (VCS). For example, if you are using GitLab, you can set up a webhook in GitLab to notify Jenkins whenever a new commit is pushed.

   ```mermaid
sequenceDiagram
       participant Developer
       participant GitLab
       participant Jenkins
       Developer->>GitLab: Push Commit
       GitLab->>Jenkins: Webhook Notification
       Jenkins->>Jenkins: Trigger Build
```

   In Jenkins, you can configure the webhook URL in the job settings under "Build Triggers".

   ```yaml
   # Jenkinsfile Example
   pipeline {
       agent any
       triggers {
           gitlab()
       }
       stages {
           stage('Build') {
               steps {
                   sh 'make build'
               }
           }
           stage('Test') {
               steps {
                   sh 'make test'
               }
           }
       }
   }
   ```

2. **Pull Request Triggers**:
   
   To configure a pull request trigger, you need to set up a webhook in your VCS to notify Jenkins whenever a pull request is opened or updated.

   ```mermaid
sequenceDiagram
       participant Developer
       participant GitLab
       participant Jenkins
       Developer->>GitLab: Open Pull Request
       GitLab->>Jenkins: Webhook Notification
       Jenkins->>Jenkins: Trigger Build
```

   In Jenkins, you can configure the webhook URL in the job settings under "Build Triggers".

   ```yaml
   # Jenkinsfile Example
   pipeline {
       agent any
       triggers {
           pullRequest()
       }
       stages {
           stage('Build') {
               steps {
                   sh 'make build'
               }
           }
           stage('Test')
           {
               steps {
                   sh 'make test'
               }
           }
       }
   }
   ```

#### Manual Build Triggers

To configure a manual build trigger, you simply need to disable automatic triggers and rely on manual intervention to start the build.

```mermaid
sequenceDiagram
    participant Developer
    participant Jenkins
    Developer->>Jenkins: Manually Trigger Build
    Jenkins->>Jenkins: Start Build
```

In Jenkins, you can disable automatic triggers and rely on the "Build Now" button to start the build manually.

```yaml
# Jenkinsfile Example
pipeline {
    agent any
    triggers {
        // No automatic triggers
    }
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
    }
}
```

#### Scheduling Builds

To schedule builds, you can use the "Build Periodically" option in Jenkins. This allows you to specify a cron expression to define when the build should be triggered.

```mermaid
sequenceDiagram
    participant Jenkins
    Jenkins->>Jenkins: Schedule Build
    Jenkins->>Jenkins: Trigger Build at Specified Time
```

In Jenkins, you can configure the cron expression in the job settings under "Build Triggers".

```yaml
# Jenkinsfile Example
pipeline {
    agent any
    triggers {
        cron('H 2 * * *') // Run daily at 2 AM
    }
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
    }
}
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper build trigger configurations. For instance, the SolarWinds breach in 2020 involved attackers compromising the build process to inject malicious code into legitimate software updates. This underscores the need for robust security practices in CI/CD pipelines.

#### Secure Coding Practices

To prevent such attacks, it is essential to implement secure coding practices and use tools like static code analysis and dynamic analysis to identify potential vulnerabilities.

```mermaid
sequenceDiagram
    participant Developer
    participant Jenkins
    participant StaticCodeAnalysisTool
    participant DynamicAnalysisTool
    Developer->>Jenkins: Commit Code
    Jenkins->>StaticCodeAnalysisTool: Analyze Code
    StaticCodeAnalysisTool-->>Jenkins: Report Vulnerabilities
    Jenkins->>DynamicAnalysisTool: Run Tests
    DynamicAnalysisTool-->>Jenkins: Report Results
```

### How to Prevent / Defend

#### Detection

To detect unauthorized build triggers, you can monitor Jenkins logs and set up alerts for suspicious activity. Tools like Splunk or ELK Stack can help you analyze logs and identify anomalies.

#### Prevention

To prevent unauthorized build triggers, you should:

1. **Use Role-Based Access Control (RBAC)**: Ensure that only authorized users can trigger builds.
   
2. **Enable Two-Factor Authentication (2FA)**: Add an extra layer of security to Jenkins access.

3. **Implement Secure Coding Practices**: Use tools like SonarQube for static code analysis and OWASP ZAP for dynamic analysis.

4. **Regularly Update and Patch**: Keep Jenkins and all plugins up to date to protect against known vulnerabilities.

#### Secure-Coding Fixes

Here’s an example of how to secure a Jenkins pipeline by implementing RBAC and 2FA:

```yaml
# Jenkinsfile Example
pipeline {
    agent any
    environment {
        JENKINS_SECURITY = 'enabled'
    }
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
    }
    post {
        always {
            echo 'Pipeline completed'
        }
    }
}
```

### Complete Example: Full HTTP Request and Response

When configuring build triggers, you might interact with Jenkins via HTTP requests. Here’s an example of a full HTTP request and response for triggering a build manually:

```http
POST /job/my-job/build HTTP/1.1
Host: jenkins.example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Content-Type: application/x-www-form-urlencoded

token=my-token
```

Response:

```http
HTTP/1.1 201 Created
Date: Tue, 14 Mar 2023 12:00:00 GMT
Location: http://jenkins.example.com/job/my-job/1/
Content-Length: 0
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security and includes modules on CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in setting up and securing CI/CD pipelines, including Jenkins and GitLab integrations.

### Conclusion

Understanding and properly configuring build triggers in Jenkins is crucial for maintaining a robust CI/CD pipeline. By leveraging automatic, manual, and scheduled triggers, you can ensure that your builds are executed efficiently and securely. Always follow secure coding practices and regularly update your tools to stay ahead of potential threats.

---
<!-- nav -->
[[03-Introduction to Automating Build Triggers with Jenkins and GitLab|Introduction to Automating Build Triggers with Jenkins and GitLab]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/06-Automating Build Triggers With Jenkins And GitLab/00-Overview|Overview]] | [[05-Introduction to Build Triggers with Jenkins and GitLab|Introduction to Build Triggers with Jenkins and GitLab]]
