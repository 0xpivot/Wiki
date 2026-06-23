---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Setting Up Jenkins for DevSecOps

### Introduction to Jenkins

Jenkins is an open-source automation server that provides extensive support for continuous integration and continuous delivery (CI/CD) pipelines. It is widely used in DevSecOps environments to automate the building, testing, and deployment of applications. Jenkins supports a vast array of plugins that can be integrated to extend its functionality, including plugins for integrating automated security testing.

### Installing Jenkins with Basic Git Pipeline and Pipeline StageView Plugins

To get started with Jenkins, you need to install it along with some essential plugins. In this section, we will cover the installation process and the setup of two important plugins: Basic Git Pipeline and Pipeline StageView.

#### Installation Process

The installation process typically involves setting up Jenkins using Docker. Here’s a step-by-step guide:

1. **Pull the Jenkins Docker Image**:
    ```sh
    docker pull jenkins/jenkins:lts
    ```

2. **Run Jenkins Container**:
    ```sh
    docker run -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
    ```

3. **Access Jenkins**:
    Open a browser and navigate to `http://localhost:8080`. You will see the initial setup page.

4. **Install Required Plugins**:
    During the initial setup, you will be prompted to install suggested plugins. Select the following plugins:
    - **Basic Git Pipeline**: This plugin provides a simple way to create a Jenkins pipeline from a Git repository.
    - **Pipeline Stage View**: This plugin provides a visual representation of the stages in a Jenkins pipeline.

5. **Create Admin User**:
    After installing the plugins, Jenkins will ask you to create an admin user. Fill in the required details:
    - **Username**: Choose a unique username.
    - **Password**: Enter a strong, secure password.
    - **Full Name**: Your name.
    - **Email Address**: A valid email address.

    ```sh
    Username: admin
    Password: SuperSecurePassword123!
    Full Name: John Doe
    Email Address: john.doe@example.com
    ```

    Click on **Save and Continue**.

6. **Verify Setup**:
    Once you click on **Save and Continue**, Jenkins will display the address that was filled in during the Docker Compose setup. Congratulations! You have successfully configured and installed your Jenkins instance.

### Understanding Jenkins Plugins

Jenkins plugins are extensions that enhance the functionality of the core Jenkins server. They can provide additional features such as source control management, build tools, and security integrations.

#### Basic Git Pipeline Plugin

The Basic Git Pipeline plugin simplifies the creation of Jenkins pipelines from a Git repository. It automatically generates a Jenkinsfile based on the contents of the repository.

- **Purpose**: Automates the creation of Jenkins pipelines from Git repositories.
- **Syntax**: No specific syntax is required; the plugin automatically detects the repository structure.
- **Example**: If you have a Git repository with a Jenkinsfile, the plugin will automatically create a pipeline job for you.

#### Pipeline Stage View Plugin

The Pipeline Stage View plugin provides a visual representation of the stages in a Jenkins pipeline. This helps in monitoring the progress and identifying bottlenecks.

- **Purpose**: Visualizes the stages in a Jenkins pipeline.
- **Syntax**: No specific syntax is required; the plugin automatically detects the stages defined in the Jenkinsfile.
- **Example**: If you have a Jenkinsfile with multiple stages, the plugin will display a visual representation of these stages.

### Configuring Jenkins for Continuous Integration

Once Jenkins is set up, you can configure it to perform continuous integration tasks. This involves setting up jobs that automatically build and test your code whenever changes are pushed to the repository.

#### Example Jenkinsfile

Here is an example of a Jenkinsfile that defines a simple CI pipeline:

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'make deploy'
            }
        }
    }
}
```

### Integrating Automated Security Testing

In a DevSecOps environment, it is crucial to integrate automated security testing into the CI/CD pipeline. This ensures that security vulnerabilities are detected early in the development cycle.

#### Example of Integrating Security Testing

Here is an example of how to integrate security testing into a Jenkins pipeline:

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Security Test') {
            steps {
                sh 'make security-test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'make deploy'
            }
        }
    }
}
```

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-21234

CVE-2021-21234 is a critical vulnerability in Jenkins that allows remote code execution. This vulnerability highlights the importance of integrating security testing into the CI/CD pipeline.

- **Impact**: Allows attackers to execute arbitrary code on the Jenkins server.
- **Mitigation**: Ensure that Jenkins is kept up-to-date with the latest security patches.

### How to Prevent / Defend

#### Detection

To detect security vulnerabilities in Jenkins, you can use various tools and techniques:

- **Static Code Analysis**: Tools like SonarQube can analyze the codebase for security vulnerabilities.
- **Dynamic Analysis**: Tools like OWASP ZAP can perform dynamic analysis on the application.

#### Prevention

To prevent security vulnerabilities in Jenkins, follow these best practices:

- **Keep Jenkins Updated**: Regularly update Jenkins to the latest version to ensure you have the latest security patches.
- **Use Secure Credentials**: Store sensitive credentials securely using Jenkins credentials management.
- **Limit Access**: Restrict access to Jenkins to only authorized users.

#### Secure Coding Fixes

Here is an example of a vulnerable Jenkinsfile and its secure counterpart:

**Vulnerable Jenkinsfile**:
```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'make deploy'
            }
        }
    }
}
```

**Secure Jenkinsfile**:
```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Security Test') {
            steps {
                sh 'make security-test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'make deploy'
            }
        }
    }
}
```

### Conclusion

Setting up Jenkins with the necessary plugins and integrating automated security testing is a crucial step in a DevSecOps environment. By following the steps outlined in this chapter, you can ensure that your Jenkins instance is configured securely and that security vulnerabilities are detected early in the development cycle.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.
- **WebGoat**: An interactive training application for learning about web application security.

These labs will help you gain practical experience in setting up Jenkins and integrating automated security testing into your CI/CD pipeline.

---
<!-- nav -->
[[02-Setting Up Jenkins Using Docker Compose|Setting Up Jenkins Using Docker Compose]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/03-Demo Getting Jenkins up and Running/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/03-Demo Getting Jenkins up and Running/04-Practice Questions & Answers|Practice Questions & Answers]]
