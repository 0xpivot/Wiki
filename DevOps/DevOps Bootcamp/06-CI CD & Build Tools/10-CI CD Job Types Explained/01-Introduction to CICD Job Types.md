---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to CI/CD Job Types

Continuous Integration (CI) and Continuous Delivery (CD) are fundamental practices in modern software development, enabling teams to deliver high-quality software efficiently and reliably. In this chapter, we will delve into the various types of build jobs used in CI/CD pipelines, focusing on freestyle jobs, regular pipeline jobs, and multi-branch pipeline jobs. Each type serves a specific purpose and offers unique advantages depending on the project requirements and complexity.

### Freestyle Jobs

Freestyle jobs are the most basic type of build jobs in CI/CD systems. They are designed to execute a single task as a standalone job. This simplicity makes them ideal for individual steps in a larger workflow, such as testing, building, or deploying code.

#### What is a Freestyle Job?

A freestyle job is a configurable job type that allows users to define a series of build steps and post-build actions. These steps can include shell scripts, batch commands, or calls to external tools like Maven or Gradle. The primary advantage of freestyle jobs is their flexibility and ease of setup.

#### Why Use Freestyle Jobs?

Freestyle jobs are particularly useful in workflows where individual steps need to be executed independently. For example, in a continuous delivery workflow, each stage—such as testing, building, and deploying—can be handled by separate freestyle jobs. This modular approach ensures that each step can be tested and validated individually before moving on to the next.

#### How Does a Freestyle Job Work?

Let's consider a simple example where a freestyle job is used to compile and run unit tests for a Java application using Maven.

```bash
#!/bin/bash

# Step 1: Checkout the code
git clone https://github.com/example/repo.git

# Step 2: Navigate to the project directory
cd repo

# Step 3: Run Maven to compile and test
mvn clean install
```

In this example, the freestyle job performs the following steps:

1. **Checkout the Code**: Clones the repository from GitHub.
2. **Navigate to the Project Directory**: Changes the working directory to the cloned repository.
3. **Run Maven**: Executes the `mvn clean install` command to compile and run unit tests.

#### Pitfalls of Freestyle Jobs

While freestyle jobs offer flexibility, they can become cumbersome to manage in complex workflows. Each step must be explicitly defined, leading to potential errors if not carefully configured. Additionally, maintaining multiple freestyle jobs for different stages can become time-consuming and error-prone.

#### How to Prevent / Defend

To mitigate the risks associated with freestyle jobs, it is essential to:

1. **Automate Configuration Management**: Use tools like Ansible or Terraform to manage job configurations centrally.
2. **Implement Version Control**: Store job configurations in version control systems to track changes and revert to previous versions if necessary.
3. **Use Templates**: Create reusable templates for common tasks to reduce redundancy and ensure consistency.

### Regular Pipeline Jobs

Regular pipeline jobs are a more advanced type of build job that consolidates multiple steps into a single, cohesive pipeline. Unlike freestyle jobs, which handle individual tasks, regular pipeline jobs provide a comprehensive view of the entire workflow, making it easier to manage and monitor.

#### What is a Regular Pipeline Job?

A regular pipeline job is a job type that defines a series of stages, each representing a distinct phase in the build process. These stages can include tasks like building, testing, and deploying code. The primary advantage of regular pipeline jobs is their ability to provide a clear overview of the entire workflow, making it easier to identify bottlenecks and issues.

#### Why Use Regular Pipeline Jobs?

Regular pipeline jobs are ideal for projects that require a more structured and automated approach to CI/CD. By consolidating multiple steps into a single pipeline, teams can streamline their workflows and improve visibility into the build process.

#### How Does a Regular Pipeline Job Work?

Let's consider a simple example where a regular pipeline job is used to build, test, and deploy a Java application using Jenkins.

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
                sh 'scp target/myapp.jar user@server:/var/www/html/'
            }
        }
    }
}
```

In this example, the regular pipeline job performs the following stages:

1. **Build**: Compiles the code using Maven.
2. **Test**: Runs unit tests using Maven.
3. **Deploy**: Copies the compiled JAR file to a remote server using SCP.

#### Pitfalls of Regular Pipeline Jobs

While regular pipeline jobs offer a more structured approach, they can become complex to manage in large-scale projects. Each stage must be carefully defined, and any changes to the pipeline require updates to the configuration.

#### How to Prevent / Defend

To mitigate the risks associated with regular pipeline jobs, it is essential to:

1. **Use Modular Stages**: Break down the pipeline into smaller, modular stages to improve maintainability.
2. **Implement Error Handling**: Add error handling mechanisms to catch and report issues during the build process.
3. **Use Version Control**: Store pipeline configurations in version control systems to track changes and revert to previous versions if necessary.

### Multi-Branch Pipeline Jobs

Multi-branch pipeline jobs are the most advanced type of build jobs, designed to handle multiple branches in a Git repository. Unlike regular pipeline jobs, which handle a single branch, multi-branch pipeline jobs can automatically create and manage pipelines for multiple branches based on a defined configuration.

#### What is a Multi-Branch Pipeline Job?

A multi-branch pipeline job is a job type that automatically creates and manages pipelines for multiple branches in a Git repository. This job type is ideal for projects that require frequent branching and merging, such as feature branches or release branches.

#### Why Use Multi-Branch Pipeline Jobs?

Multi-branch pipeline jobs are particularly useful in projects that involve frequent branching and merging. By automating the creation and management of pipelines for multiple branches, teams can streamline their workflows and improve efficiency.

#### How Does a Multi-Branch Pipeline Job Work?

Let's consider a simple example where a multi-branch pipeline job is used to build and test multiple branches in a Git repository using Jenkins.

```groovy
pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    def branches = ['main', 'feature-1', 'feature-2']
                    branches.each { branch ->
                        echo "Building branch ${branch}"
                        sh "git checkout ${branch}"
                        sh 'mvn clean package'
                    }
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    def branches = ['main', 'feature-1', 'feature-2']
                    branches.each { branch ->
                        echo "Testing branch ${branch}"
                        sh "git checkout ${branch}"
                        sh 'mvn test'
                    }
                }
            }
        }
    }
}
```

In this example, the multi-branch pipeline job performs the following stages:

1. **Build**: Compiles the code for each specified branch using Maven.
2. **Test**: Runs unit tests for each specified branch using Maven.

#### Pitfalls of Multi-Branch Pipeline Jobs

While multi-branch pipeline jobs offer a powerful way to manage multiple branches, they can become complex to configure and maintain. Each branch must be explicitly defined, and any changes to the pipeline require updates to the configuration.

#### How to Prevent / Defend

To mitigate the risks associated with multi-branch pipeline jobs, it is essential to:

1. **Use Dynamic Branch Detection**: Configure the pipeline to dynamically detect and manage branches based on a regular expression.
2. **Implement Error Handling**: Add error handling mechanisms to catch and report issues during the build process.
3. **Use Version Control**: Store pipeline configurations in version control systems to track changes and revert to previous versions if necessary.

### Real-World Examples

To illustrate the practical application of these concepts, let's consider a recent real-world example involving a breach in a CI/CD pipeline.

#### Example: CVE-2021-22205

CVE-2021-22205 is a critical vulnerability in Jenkins that allows attackers to execute arbitrary code on the Jenkins master. This vulnerability highlights the importance of securing CI/CD pipelines against unauthorized access and code execution.

#### Vulnerable Code

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
                sh 'scp target/myapp.jar user@server:/var/www/html/'
            }
        }
    }
}
```

#### Secure Code

To prevent such vulnerabilities, it is essential to implement proper security measures, such as:

1. **Use SSH Keys**: Replace hardcoded credentials with SSH keys for secure authentication.
2. **Enable Security Plugins**: Enable security plugins like the Jenkins Security Plugin to enforce access controls.
3. **Use Role-Based Access Control (RBAC)**: Implement RBAC to restrict access to sensitive operations.

```groovy
pipeline {
    agent any

    environment {
        SSH_KEY = credentials('ssh-key-id')
    }

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
                sshagent(credentials: ['ssh-key-id']) {
                    sh 'scp target/myapp.jar user@server:/var/www/html/'
                }
            }
        }
    }
}
```

### Hands-On Labs

To gain practical experience with CI/CD job types, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web application security, including CI/CD pipelines.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing and CI/CD integration.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web security skills, including CI/CD pipeline setup.

By completing these labs, you can apply the theoretical knowledge gained in this chapter to real-world scenarios, enhancing your understanding and proficiency in CI/CD job types.

### Conclusion

In this chapter, we have explored the various types of build jobs used in CI/CD pipelines, including freestyle jobs, regular pipeline jobs, and multi-branch pipeline jobs. Each type serves a specific purpose and offers unique advantages depending on the project requirements and complexity. By understanding the strengths and weaknesses of each job type, you can design and implement efficient and secure CI/CD pipelines for your projects.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/10-CI CD Job Types Explained/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/10-CI CD Job Types Explained/02-Practice Questions & Answers|Practice Questions & Answers]]
