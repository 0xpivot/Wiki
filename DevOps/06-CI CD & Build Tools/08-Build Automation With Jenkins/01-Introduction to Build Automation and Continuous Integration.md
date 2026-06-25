---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Build Automation and Continuous Integration

Build automation and continuous integration (CI) are fundamental concepts in modern software development, particularly within the DevOps paradigm. These practices aim to streamline the development lifecycle, ensuring that code changes can be integrated quickly and reliably into the main codebase. This chapter will delve into these concepts, focusing on Jenkins as a powerful tool for implementing them.

### What is Build Automation?

Build automation refers to the process of automating the tasks involved in compiling source code into executable programs. Traditionally, developers would manually compile their code, link libraries, and package the final product. This manual process was time-consuming and prone to human error. Build automation tools automate these steps, ensuring consistency and reducing the likelihood of errors.

#### Why is Build Automation Important?

1. **Consistency**: Automated builds ensure that the same steps are followed every time, leading to consistent results.
2. **Speed**: Automation significantly reduces the time required to compile and package code, allowing for faster iterations.
3. **Error Reduction**: Automated processes reduce the chance of human error, such as forgetting to include a necessary library or misconfiguring a build parameter.
4. **Scalability**: As projects grow larger and more complex, manual builds become impractical. Automation scales with the project size.

### What is Continuous Integration?

Continuous Integration (CI) is a practice where developers frequently merge their code changes into a shared repository, after which automated builds and tests are run. The goal is to catch integration issues early, making them easier and cheaper to fix.

#### Why is Continuous Integration Important?

1. **Early Detection of Issues**: By integrating code frequently, issues are detected earlier, reducing the cost and complexity of fixing them.
2. **Improved Collaboration**: CI encourages frequent communication and collaboration among team members.
3. **Quality Assurance**: Automated testing ensures that the code meets quality standards before being merged into the main branch.
4. **Faster Feedback Loop**: Developers receive immediate feedback on their changes, enabling quicker adjustments and improvements.

### Jenkins: A Popular Build Automation Tool

Jenkins is an open-source automation server that provides extensive support for continuous integration and delivery. It is highly extensible through numerous plugins and supports a wide range of build tools and languages.

#### Setting Up Jenkins

To get started with Jenkins, you need to deploy it on a server. In this example, we will use DigitalOcean, a popular cloud provider.

```bash
# Install Java
sudo apt update
sudo apt install default-jdk

# Download and install Jenkins
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt update
sudo apt install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

Once Jenkins is installed, access it via your browser at `http://<your-server-ip>:8080`. Follow the initial setup instructions to unlock Jenkins and install suggested plugins.

### Creating Your First Freestyle Job

A freestyle job in Jenkins is a basic type of job that allows you to define a series of build steps. Here’s how to create one:

1. **Log in to Jenkins** and click on "New Item".
2. **Enter a name** for your job and select "Freestyle project". Click "OK".
3. **Configure Source Code Management**: Select "Git" and enter the URL of your repository.
4. **Add Build Steps**: You can add various build steps, such as executing shell commands or running Maven builds.
5. **Save the Configuration**.

Here’s an example of a simple freestyle job configuration:

```yaml
# Jenkinsfile for a freestyle job
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/your-repo.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean install'
            }
        }
    }
}
```

### Configuring Credentials and Plugins

Credentials management in Jenkins allows you to securely store sensitive information such as API keys, passwords, and SSH keys. Plugins extend Jenkins’ functionality, supporting various tools and integrations.

#### Adding Credentials

1. **Navigate to Manage Jenkins** > **Manage Credentials**.
2. **Click on Store in Jenkins** and then **Global credentials**.
3. **Add a new credential**, selecting the appropriate type (e.g., username and password).

#### Installing Plugins

1. **Navigate to Manage Jenkins** > **Manage Plugins**.
2. **Select the Available tab** and search for the desired plugin.
3. **Install the plugin** and restart Jenkins if prompted.

### Integrating Docker in the Build Process

Docker is a containerization platform that allows you to package your application and its dependencies into a lightweight, portable container. Integrating Docker into your build process ensures that your application runs consistently across different environments.

#### Building a Docker Image

1. **Create a Dockerfile** in your project root.
2. **Configure Jenkins to build the Docker image**.

Example Dockerfile:

```dockerfile
# Dockerfile
FROM openjdk:11-jdk-slim
WORKDIR /app
COPY target/myapp.jar /app/
CMD ["java", "-jar", "myapp.jar"]
```

Example Jenkinsfile for building a Docker image:

```yaml
pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'myapp'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/your-repo.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean install'
            }
        }
        stage('Docker Build') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }
    }
}
```

#### Pushing the Docker Image to a Private Registry

1. **Configure Jenkins to push the Docker image** to a private registry.
2. **Use Docker credentials** to authenticate with the registry.

Example Jenkinsfile for pushing the Docker image:

```yaml
pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'myapp'
        REGISTRY_URL = 'registry.example.com'
        REGISTRY_CREDENTIALS_ID = 'docker-credentials-id'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/your-repo.git', branch: 'main'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean install'
            }
        }
        stage('Docker Build') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }
        stage('Docker Push') {
            steps {
                script {
                    docker.withRegistry(REGISTRY_URL, REGISTRY_CREDENTIALS_ID) {
                        docker.image("${DOCKER_IMAGE}").push()
                    }
                }
            }
        }
    }
}
```

### Scripted Pipeline Jobs

Scripted pipelines allow you to define the build process using Groovy scripts. This approach provides more flexibility and control compared to declarative pipelines.

#### Writing a Jenkinsfile

A Jenkinsfile is a Groovy script that defines the build process. Here’s an example of a scripted pipeline:

```groovy
node {
    stage('Checkout') {
        git url: 'https://github.com/your-repo.git', branch: 'main'
    }
    stage('Build') {
        sh 'mvn clean install'
    }
    stage('Test') {
        sh 'mvn test'
    }
    stage('Deploy') {
        sh 'scp target/myapp.jar user@server:/path/to/deploy/'
    }
}
```

### Multi-Branch Pipeline

Multi-branch pipelines allow you to manage multiple branches of your Git repository within a single Jenkins job. This is useful for handling feature branches, pull requests, and other branches.

#### Creating a Multi-Branch Pipeline

1. **Navigate to New Item** and select "Multibranch Pipeline".
2. **Configure the source code management** to point to your Git repository.
3. **Define the branch sources** and specify the branch patterns to include.

Example Jenkinsfile for a multi-branch pipeline:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", url: 'https://github.com/your-repo.git'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean install'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'scp target/myapp.jar user@server:/path/to/deploy/'
            }
        }
    }
}
```

### How to Prevent / Defend

#### Secure Coding Practices

1. **Validate Inputs**: Ensure that all inputs are validated to prevent injection attacks.
2. **Use Secure Libraries**: Keep your dependencies up-to-date and avoid using libraries with known vulnerabilities.
3. **Least Privilege Principle**: Run your builds with the least privileges necessary.

#### Hardening Jenkins

1. **Enable Security**: Configure Jenkins to require authentication and enable role-based access control.
2. **Limit Plugin Usage**: Only install necessary plugins and keep them updated.
3. **Regular Audits**: Perform regular security audits and vulnerability scans.

#### Real-World Examples

- **CVE-2018-19487**: A critical vulnerability in Jenkins allowed remote code execution. Ensure you have the latest security patches installed.
- **CVE-2020-14143**: Another vulnerability in Jenkins allowed unauthorized access to sensitive data. Regularly review and update your Jenkins configurations.

### Conclusion

This chapter has provided a comprehensive guide to build automation and continuous integration using Jenkins. From setting up Jenkins to creating complex multi-branch pipelines, you now have the knowledge to implement robust CI/CD workflows in your projects. Remember to follow secure coding practices and regularly audit your Jenkins configurations to ensure the security and reliability of your builds.

### Practice Labs

For hands-on experience with Jenkins and build automation, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications, including CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including CI/CD.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical scenarios to reinforce the concepts learned in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/08-Build Automation With Jenkins/00-Overview|Overview]] | [[02-Introduction to Build Automation with Jenkins|Introduction to Build Automation with Jenkins]]
