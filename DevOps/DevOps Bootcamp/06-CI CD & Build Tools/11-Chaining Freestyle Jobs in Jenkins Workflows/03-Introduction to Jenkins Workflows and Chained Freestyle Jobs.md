---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins Workflows and Chained Freestyle Jobs

Jenkins is a widely used open-source automation server that provides continuous integration and continuous delivery (CI/CD) services. One of the key features of Jenkins is its ability to create complex workflows through chaining freestyle jobs. However, this approach has several limitations that have led to the development of more advanced workflow management systems within Jenkins.

### Background Theory

Before diving into the specifics of chaining freestyle jobs, it's important to understand the historical context and the evolution of CI/CD practices.

#### Historical Context

Jenkins was initially designed at a time when user interface (UI)-based tools were more prevalent than script-driven configurations. This means that most of the configuration and logic were handled through a graphical interface, which limited the flexibility and scalability of the system. Users could not easily customize or extend the functionality beyond what was provided by the UI.

#### Emergence of CI/CD Concepts

The rise of CI/CD practices brought about the need for more sophisticated and flexible workflow management systems. The traditional approach of chaining freestyle jobs became insufficient to handle the complexity and dynamic nature of modern CI/CD pipelines. This led to the development of more advanced tools and techniques within Jenkins, such as Pipeline as Code (PAC).

### Limitations of Chained Freestyle Jobs

Chained freestyle jobs in Jenkins have several inherent limitations:

1. **Limited Flexibility**: The UI-based configuration restricts users to predefined input fields and options. Customization is limited to what the plugin developers provide.
2. **Multiple Plugins**: Each additional functionality requires installing a separate plugin, leading to a fragmented and less maintainable setup.
3. **Complexity Management**: As workflows become more complex, managing multiple chained freestyle jobs becomes cumbersome and error-prone.

### Real-World Example: CVE-2021-21189

A real-world example of the limitations of UI-based configurations is the CVE-2021-21189 vulnerability in Jenkins. This vulnerability allowed attackers to execute arbitrary code on the Jenkins server by exploiting a flaw in the UI-based configuration of certain plugins. This highlights the importance of moving towards more secure and flexible configuration methods.

### Transition to Scripted Configuration

To address these limitations, Jenkins introduced the concept of Pipeline as Code (PAC), which allows users to define their CI/CD workflows using scripts written in Groovy. This approach offers several advantages:

1. **Flexibility**: Users can define custom logic and conditions directly in the script.
2. **Maintainability**: Scripts are easier to version control and manage compared to UI-based configurations.
3. **Scalability**: Complex workflows can be defined more efficiently and consistently.

### Example of a Simple Freestyle Job Chain

Let's consider a simple example of chaining freestyle jobs in Jenkins. Suppose we have two jobs: `Job A` and `Job B`. `Job A` builds the code, and `Job B` deploys the built artifacts.

```mermaid
graph TD
    A[Job A] --> B[Job B]
```

#### Job A: Build Code

```mermaid
sequenceDiagram
    participant JenkinsMaster
    participant JobA
    JenkinsMaster->>JobA: Trigger Build
    JobA-->>JenkinsMaster: Build Successful
```

#### Job B: Deploy Artifacts

```mermaid
sequenceDiagram
    participant JenkinsMaster
    participant JobB
    JenkinsMaster->>JobB: Trigger Deployment
    JobB-->>JenkinsMaster: Deployment Successful
```

### Moving to Pipeline as Code

To overcome the limitations of chained freestyle jobs, let's transition to a scripted pipeline using Groovy.

#### Example Pipeline Script

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building the code...'
                // Add build steps here
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying the artifacts...'
                // Add deployment steps here
            }
        }
    }
}
```

### Detailed Explanation of the Pipeline Script

1. **Pipeline Block**: The `pipeline` block defines the entire workflow.
2. **Agent Block**: The `agent` block specifies where the pipeline should run. In this case, `any` means it can run on any available agent.
3. **Stages Block**: The `stages` block contains a series of stages, each representing a distinct phase of the workflow.
4. **Stage Block**: Each `stage` block represents a specific task, such as building the code or deploying the artifacts.
5. **Steps Block**: The `steps` block contains the actual commands or actions to be executed in each stage.

### Full Raw HTTP Request and Response

When Jenkins triggers a job, it sends an HTTP POST request to the Jenkins API. Here is an example of a full HTTP request and response:

#### HTTP Request

```http
POST /job/JobA/build HTTP/1.1
Host: jenkins.example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Content-Type: application/x-www-form-urlencoded

token=your-token
```

#### HTTP Response

```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Jenkins
Location: http://jenkins.example.com/job/JobA/1/
Content-Length: 0
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Lack of Version Control

**Problem**: Without version control, changes to the pipeline script can be lost or overwritten.

**Solution**: Use a version control system like Git to store and manage pipeline scripts.

#### Pitfall 2: Hardcoded Credentials

**Problem**: Storing credentials directly in the pipeline script can lead to security vulnerabilities.

**Solution**: Use Jenkins credentials management to securely store and reference credentials.

#### Secure-Coding Fix

**Vulnerable Code**

```groovy
pipeline {
    agent any

    environment {
        DB_PASSWORD = 'my-secret-password'
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building the code...'
            }
        }
    }
}
```

**Fixed Code**

```groovy
pipeline {
    agent any

    environment {
        DB_PASSWORD = credentials('db-password')
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building the code...'
            }
        }
    }
}
```

### Conclusion

Chaining freestyle jobs in Jenkins has several limitations that make it unsuitable for complex CI/CD workflows. By transitioning to Pipeline as Code, users can achieve greater flexibility, maintainability, and scalability. This approach also helps mitigate common pitfalls and security risks associated with traditional UI-based configurations.

### Hands-On Lab Suggestions

For hands-on practice with Jenkins workflows, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on securing Jenkins pipelines.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice CI/CD pipeline security.
- **DVWA (Damn Vulnerable Web Application)**: Useful for practicing secure coding and pipeline management in a controlled environment.

By following these guidelines and practicing with real-world scenarios, you can gain a deep understanding of Jenkins workflows and effectively manage complex CI/CD pipelines.

---
<!-- nav -->
[[02-Introduction to Jenkins Pipeline Jobs|Introduction to Jenkins Pipeline Jobs]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/11-Chaining Freestyle Jobs in Jenkins Workflows/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/11-Chaining Freestyle Jobs in Jenkins Workflows/04-Practice Questions & Answers|Practice Questions & Answers]]
