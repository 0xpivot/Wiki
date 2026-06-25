---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Jenkins Pipeline with Docker and Maven

### Introduction to Jenkins Pipelines

Jenkins is a widely-used open-source automation server that provides continuous integration and continuous delivery (CI/CD) services. A Jenkins Pipeline is a way to model your continuous integration and continuous delivery process. It allows you to define a series of steps that will be executed in a specific order to automate your software development lifecycle.

A Jenkins Pipeline is defined using a Jenkinsfile, which is a text file containing the definition of the pipeline. This file is typically stored in the root directory of your project repository and is version-controlled along with the rest of your codebase. This ensures that your build process is repeatable and consistent across different environments.

### Understanding the Jenkinsfile Syntax

The Jenkinsfile uses a Groovy-based Domain-Specific Language (DSL) to define the pipeline. Each pipeline consists of one or more stages, and each stage can contain one or more steps. Stages are logical groupings of steps that represent distinct phases of your build process, such as "checkout", "build", "test", "deploy", etc.

Here is an example of a basic Jenkinsfile:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
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
                sh 'docker build -t myapp .'
                sh 'docker login -u username -p password'
                sh 'docker push myapp'
            }
        }
    }
}
```

In this example, the `agent` directive specifies that the pipeline can run on any available agent. The `stages` block defines four stages: `Checkout`, `Build`, `Test`, and `Deploy`. Each stage contains a `steps` block that defines the actions to be performed in that stage.

### Setting Up Maven in Jenkins Pipeline

Maven is a popular build automation tool used primarily for Java projects. To ensure that Maven commands are available throughout the pipeline, you need to define the `tools` attribute in the Jenkinsfile. This attribute specifies the tools that should be installed on the agent before the pipeline runs.

Here is an example of how to set up Maven in a Jenkinsfile:

```groovy
pipeline {
    agent any
    tools {
        maven 'Maven 3.6.3' // Replace with the name of your Maven installation
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

In this example, the `tools` block specifies that the Maven installation named `Maven 3.6.3` should be available on the agent. This ensures that the `mvn` command is available in the `Build` stage.

### Building a Docker Image in Jenkins Pipeline

Docker is a platform that allows developers to package their applications and dependencies into lightweight, portable containers. In a Jenkins Pipeline, you can use Docker to build and deploy your application.

To build a Docker image in a Jenkins Pipeline, you need to specify the Docker commands in the `steps` block of the appropriate stage. Here is an example:

```groovy
pipeline {
    agent any
    tools {
        maven 'Maven 3.6.3'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
    }
}
```

In this example, the `Build Docker Image` stage contains a `sh` step that runs the `docker build` command to build the Docker image.

### Pushing the Docker Image to Docker Hub

After building the Docker image, you can push it to a Docker registry such as Docker Hub. To do this, you need to log in to the Docker registry and then push the image.

Here is an example of how to push a Docker image to Docker Hub in a Jenkins Pipeline:

```groovy
pipeline {
    agent any
    tools {
        maven 'Maven 3.6.3'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                    sh 'docker tag myapp myregistry/myapp:latest'
                    sh 'docker push myregistry/myapp:latest'
                }
            }
        }
    }
}
```

In this example, the `Push Docker Image` stage uses the `withCredentials` step to securely access the Docker credentials stored in Jenkins. The `docker login` command logs in to Docker Hub, and the `docker push` command pushes the image to the specified registry.

### Full Example of a Jenkins Pipeline with Maven and Docker

Here is a complete example of a Jenkins Pipeline that checks out the code, builds the Maven project, builds the Docker image, and pushes it to Docker Hub:

```groovy
pipeline {
    agent any
    tools {
        maven 'Maven 3.6.3'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                    sh 'docker tag myapp myregistry/myapp:latest'
                    sh 'docker push myregistry/myapp:latest'
                }
            }
        }
    }
}
```

### Mermaid Diagrams for Jenkins Pipeline

To visualize the Jenkins Pipeline, you can use Mermaid diagrams. Here is an example of a Mermaid diagram that represents the stages and steps of the Jenkins Pipeline:

```mermaid
graph TD
    Checkout --> Build
    Build --> BuildDockerImage
    BuildDockerImage --> PushDockerImage
    subgraph Checkout
        Checkout --> CheckoutCode
    end
    subgraph Build
        Build --> BuildMavenProject
    end
    subgraph BuildDockerImage
        BuildDockerImage --> BuildDockerImage
    end
    subgraph PushDockerImage
        PushDockerImage --> LoginDockerHub
        LoginDockerHub --> TagDockerImage
        TagDockerImage --> PushDockerImage
    end
```

### Common Pitfalls and How to Prevent Them

#### 1. **Maven Installation Not Found**

**Problem:** If the Maven installation is not correctly configured, the `mvn` command will fail.

**Solution:** Ensure that the Maven installation is correctly configured in Jenkins. You can do this by navigating to `Manage Jenkins > Global Tool Configuration` and adding the Maven installation.

**Secure Code Fix:**
```groovy
pipeline {
    agent any
    tools {
        maven 'Maven 3.6.3' // Ensure this matches the name of your Maven installation
    }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

#### 2. **Docker Credentials Not Securely Stored**

**Problem:** If Docker credentials are not securely stored, they can be exposed to unauthorized users.

**Solution:** Use Jenkins credentials to securely store Docker credentials. You can do this by navigating to `Manage Jenkins > Manage Credentials > System`.

**Secure Code Fix:**
```groovy
pipeline {
    agent any
    tools {
        maven 'Maven 3.6.3'
    }
    stages {
        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                    sh 'docker tag myapp myregistry/myapp:latest'
                    sh 'docker push myregistry/myapp:latest'
                }
            }
        }
    }
}
```

### Real-World Examples and Recent CVEs

#### 1. **CVE-2021-25285: Jenkins Pipeline Script Security Plugin Vulnerability**

**Description:** A vulnerability in the Jenkins Pipeline Script Security Plugin allowed attackers to bypass security restrictions and execute arbitrary code.

**Impact:** This vulnerability could lead to remote code execution and compromise of the Jenkins server.

**Mitigation:** Ensure that the Jenkins Pipeline Script Security Plugin is updated to the latest version. Additionally, configure the plugin to restrict access to sensitive operations.

#### 2. **CVE-2022-22965: Docker API Authentication Bypass**

**Description:** A vulnerability in the Docker API allowed attackers to bypass authentication and gain unauthorized access to Docker resources.

**Impact:** This vulnerability could lead to unauthorized access to Docker images and containers.

**Mitigation:** Ensure that Docker is configured to require authentication for all API requests. Additionally, use TLS encryption to secure communication between the client and the Docker daemon.

### Hands-On Labs

To practice Jenkins Pipeline with Maven and Docker, you can use the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including Jenkins security.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice various security techniques, including Jenkins security.
- **DVWA (Damn Vulnerable Web Application)**: Another deliberately insecure web application that can be used to practice security techniques.

These labs provide a safe environment to practice and learn about Jenkins Pipeline with Maven and Docker.

### Conclusion

In this chapter, we covered the basics of Jenkins Pipelines, including how to define a Jenkinsfile, set up Maven, build a Docker image, and push it to Docker Hub. We also discussed common pitfalls and how to prevent them, as well as real-world examples and recent CVEs. By following the steps outlined in this chapter, you can create a robust and secure Jenkins Pipeline for your project.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/32-Jenkins Pipeline with Docker and Maven/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/32-Jenkins Pipeline with Docker and Maven/02-Practice Questions & Answers|Practice Questions & Answers]]
