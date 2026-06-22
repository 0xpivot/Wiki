---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins Declarative Pipeline Syntax

In the realm of continuous integration and continuous delivery (CI/CD), Jenkins stands out as a powerful tool that enables developers to automate their software development processes. One of the key features of Jenkins is its ability to define pipelines using Groovy scripts. These pipelines can be defined either using a **scripted** approach or a **declarative** approach. This chapter will focus on the declarative pipeline syntax, which was introduced to make it easier for users to get started with Jenkins pipelines.

### What is a Declarative Pipeline?

A declarative pipeline is a structured way of defining a CI/CD pipeline using a Groovy-based DSL (Domain Specific Language). The declarative syntax provides a predefined structure that simplifies the process of creating pipelines. While it may not be as flexible as the scripted pipeline, it offers a more straightforward and intuitive way to define complex workflows.

#### Why Use Declarative Pipelines?

Declarative pipelines are designed to be more user-friendly and maintainable compared to scripted pipelines. They provide a clear and consistent structure that makes it easier to understand and manage the pipeline logic. Additionally, declarative pipelines are more suitable for teams that are new to Jenkins or those who prefer a more declarative style of programming.

### Basic Structure of a Declarative Pipeline

The basic structure of a declarative pipeline includes several key components:

1. **Pipeline**: Declares that the script defines a pipeline.
2. **Agent**: Specifies where the pipeline should run.
3. **Stages**: Defines the different stages of the pipeline.
4. **Steps**: Specifies the actions to be performed within each stage.

Let's break down each component in detail.

#### `pipeline` Directive

The `pipeline` directive is the starting point of a declarative pipeline. It indicates that the following script defines a pipeline.

```groovy
pipeline {
    // Pipeline definition goes here
}
```

#### `agent` Directive

The `agent` directive specifies where the pipeline should run. It can be set to a specific label, a node, or a Docker image. The most commonly used value is `any`, which means the pipeline will run on any available Jenkins agent.

```groovy
pipeline {
    agent any
    // Other directives go here
}
```

The `agent any` directive is particularly useful when you have a Jenkins cluster with multiple agents. It allows the pipeline to run on the next available agent, ensuring efficient resource utilization.

#### `stages` Directive

The `stages` directive is where the actual work of the pipeline is defined. Each stage represents a distinct phase of the pipeline, such as building, testing, or deploying the application.

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Steps for building the application
            }
        }
        stage('Test') {
            steps {
                // Steps for testing the application
            }
        }
        stage('Deploy') {
            steps {
                // Steps for deploying the application
            }
        }
    }
}
```

Each stage can contain multiple steps, which are the individual actions performed within that stage.

### Example of a Simple Declarative Pipeline

Let's look at a simple example of a declarative pipeline that builds, tests, and deploys an application.

```groovy
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
                sh 'mvn test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/myapp.jar user@server:/opt/myapp/'
            }
        }
    }
}
```

In this example:
- The `agent any` directive ensures that the pipeline runs on any available Jenkins agent.
- The `stages` directive defines three stages: `Build`, `Test`, and `Deploy`.
- Each stage contains a `steps` directive that specifies the actions to be performed.

### Detailed Explanation of Each Component

#### `pipeline` Directive

The `pipeline` directive is the root element of a declarative pipeline. It encapsulates all other directives and steps. Here’s a more detailed breakdown:

```groovy
pipeline {
    // Agent directive
    agent any
    
    // Stages directive
    stages {
        // Stage definitions go here
    }
    
    // Optional post directive
    post {
        // Post-build actions go here
    }
}
```

#### `agent` Directive

The `agent` directive specifies where the pipeline should run. It can take various forms, including:

- `any`: Runs on any available agent.
- `label 'my-label'`: Runs on an agent with the specified label.
- `node { ... }`: Allows for more complex agent selection logic.
- `docker 'image-name'`: Runs the pipeline inside a Docker container.

Here’s an example using a specific label:

```groovy
pipeline {
    agent { label 'linux-agent' }
    stages {
        // Stage definitions go here
    }
}
```

#### `stages` Directive

The `stages` directive is where the actual workflow of the pipeline is defined. Each stage can have multiple steps, and stages can be nested within each other.

```groovy
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
                sh 'mvn test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/myapp.jar user@server:/opt/myapp/'
            }
        }
    }
}
```

### Nested Stages

You can also nest stages within each other to create more complex workflows. For example:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'mvn test'
                    }
                }
                stage('Integration Tests') {
                    steps {
                        sh 'mvn integration-test'
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/myapp.jar user@server:/opt/myapp/'
            }
        }
    }
}
```

In this example, the `Test` stage is split into two parallel stages: `Unit Tests` and `Integration Tests`.

### `post` Directive

The `post` directive is used to define actions that should be taken after the pipeline completes, regardless of whether it succeeds or fails. Common uses include sending notifications, archiving artifacts, or cleaning up resources.

```groovy
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
                sh 'mvn test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/myapp.jar user@server:/opt/myapp/'
            }
        }
    }
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            echo 'This will always run.'
        }
    }
}
```

### Real-World Examples and Recent CVEs

Declarative pipelines are widely used in real-world CI/CD setups. For instance, consider a scenario where a company uses Jenkins to automate the deployment of a web application. The pipeline might include stages for building the application, running unit tests, running integration tests, and deploying the application to a staging environment.

However, vulnerabilities can arise if the pipeline is not properly secured. For example, a recent CVE (CVE-2021-21234) highlighted a vulnerability in Jenkins where an attacker could execute arbitrary code by manipulating the pipeline script. To mitigate such risks, it is crucial to ensure that the pipeline scripts are properly validated and sanitized.

### How to Prevent / Defend

To prevent and defend against potential vulnerabilities in Jenkins pipelines, consider the following best practices:

1. **Validate Input**: Ensure that all input to the pipeline is properly validated and sanitized to prevent injection attacks.
2. **Use Secure Credentials**: Store sensitive information, such as passwords and API keys, securely using Jenkins credentials management.
3. **Limit Permissions**: Restrict the permissions of Jenkins agents to minimize the potential damage in case of a breach.
4. **Regular Updates**: Keep Jenkins and all plugins up to date to ensure that you have the latest security patches.
5. **Audit and Monitor**: Regularly audit and monitor pipeline executions to detect any suspicious activity.

### Secure Coding Practices

Here’s an example of a vulnerable pipeline script and its secure counterpart:

#### Vulnerable Script

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests=true'
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/myapp.jar ${DEPLOY_USER}@${DEPLOY_HOST}:/opt/myapp/'
            }
        }
    }
}
```

#### Secure Script

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests=true'
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'deploy-credentials', usernameVariable: 'DEPLOY_USER', passwordVariable: 'DEPLOY_PASSWORD')]) {
                    sh 'scp -P 22 -o StrictHostKeyChecking=no -i /path/to/private/key target/myapp.jar ${DEPLOY_USER}@${DEPLOY_HOST}:/opt/myapp/'
                }
            }
        }
    }
}
```

In the secure script, sensitive credentials are stored securely using Jenkins credentials management, and SSH keys are used for authentication instead of plain-text passwords.

### Hands-On Practice

To gain practical experience with Jenkins declarative pipelines, consider working through the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice securing CI/CD pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Another insecure web application that can be used to practice securing pipelines.

These labs provide a safe environment to experiment with Jenkins pipelines and learn how to secure them effectively.

### Conclusion

Declarative pipelines in Jenkins provide a powerful and flexible way to automate CI/CD processes. By understanding the basic structure and components of a declarative pipeline, you can create robust and maintainable pipelines that help streamline your software development lifecycle. Always remember to follow best practices for security to protect your pipelines from potential vulnerabilities.

---
<!-- nav -->
[[02-Introduction to Freestyle Jobs and Their Limitations|Introduction to Freestyle Jobs and Their Limitations]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/16-Creating Pipelines Using Groovy Scripts/00-Overview|Overview]] | [[04-Introduction to Jenkins Pipeline and Groovy Scripts|Introduction to Jenkins Pipeline and Groovy Scripts]]
