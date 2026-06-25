---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins and Docker Integration

In the context of modern DevOps practices, integrating Jenkins with Docker is a powerful combination that enables efficient and scalable continuous integration and delivery (CI/CD) pipelines. This chapter delves into the process of attaching Docker volumes to a Jenkins container, which is crucial for managing persistent data and ensuring that builds and deployments are reproducible and reliable.

### Background Theory

#### Jenkins Overview

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. It is widely used in CI/CD pipelines to automate the testing and deployment of applications. Jenkins supports various types of jobs, including freestyle projects, pipeline jobs, and matrix projects.

#### Docker Overview

Docker is a platform that uses OS-level virtualization to deliver software in packages called containers. Containers are lightweight and portable, allowing developers to package their applications along with all their dependencies into a single unit. Docker containers run consistently across different environments, making them ideal for CI/CD workflows.

### Integrating Jenkins with Docker

To integrate Jenkins with Docker, you need to ensure that Docker is installed and accessible within the Jenkins environment. This can be achieved by either installing Docker on the host machine where Jenkins runs or by using a Docker-in-Docker (DinD) setup, where Jenkins itself runs in a Docker container with access to another Docker daemon.

#### Docker-in-Docker Setup

A DinD setup allows Jenkins to run inside a Docker container while still having access to the Docker daemon. This is particularly useful in cloud environments where you might want to run Jenkins in a containerized environment.

```yaml
version: '3'
services:
  jenkins:
    image: jenkins/jenkins:lts
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    privileged: true
volumes:
  jenkins_home:
```

In this setup, `/var/run/docker.sock` is mounted into the Jenkins container, giving Jenkins access to the Docker daemon running on the host. The `privileged: true` option ensures that the container has elevated privileges necessary for interacting with the Docker daemon.

### Adding a Dockerfile to the Repository

The first step in integrating Docker with Jenkins is to create a `Dockerfile` in your repository. This file contains instructions for building a Docker image. In the given scenario, the `Dockerfile` is created in the `Jenkins Jobs` branch of the repository.

#### Example Dockerfile

Here is an example of a `Dockerfile` that builds a Java application:

```dockerfile
# Use an official OpenJDK runtime as a parent image
FROM openjdk:11-jdk-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the jar file
CMD ["java", "-jar", "target/myapp.jar"]
```

This `Dockerfile` starts with an official OpenJDK image, sets the working directory, copies the local files into the container, exposes port 8080, and specifies the command to run the application.

### Configuring Jenkins Job to Build Docker Image

Once the `Dockerfile` is in place, you need to configure the Jenkins job to build the Docker image. This involves adding a step to the Jenkins job configuration to execute Docker commands.

#### Jenkins Job Configuration

1. **Remove Unnecessary Steps**: Since the `package` step already executes tests, you can remove it from the Jenkins job configuration.
2. **Add Execute Shell Step**: Add a new step to execute shell commands. This step will run Docker commands to build the image.

```yaml
stages {
    stage('Build') {
        steps {
            sh 'mvn clean package'
        }
    }
    stage('Docker Build') {
        steps {
            sh 'docker build -t java-maven-app:1.0 .'
        }
    }
}
```

In this configuration, the `Build` stage runs the Maven `clean package` command, and the `Docker Build` stage builds the Docker image with the specified tag.

### Full Example of Jenkins Pipeline

Here is a complete example of a Jenkins pipeline script that integrates Maven and Docker:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo.git'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Docker Build') {
            steps {
                sh 'docker build -t java-maven-app:1.0 .'
            }
        }
    }
}
```

### Attaching Docker Volumes to Jenkins Container

Attaching Docker volumes to a Jenkins container is essential for persisting data such as build artifacts, logs, and configurations. This ensures that the data remains intact even if the Jenkins container is restarted or rebuilt.

#### Example of Volume Mounting

```yaml
version: '3'
services:
  jenkins:
    image: jenkins/jenkins:lts
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - ./builds:/var/jenkins_home/builds
volumes:
  jenkins_home:
```

In this example, the `jenkins_home` volume persists Jenkins data, and the `./builds` volume mounts a local directory to store build artifacts.

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Incorrect Dockerfile Syntax

**Explanation**: An incorrect `Dockerfile` can lead to build failures or unexpected behavior.

**Prevention**:
- Ensure the `Dockerfile` syntax is correct.
- Use Docker's `docker build --no-cache` to force a rebuild and catch errors.

#### Pitfall 2: Insufficient Permissions

**Explanation**: Jenkins may lack the necessary permissions to interact with the Docker daemon.

**Prevention**:
- Ensure the Jenkins container has the `privileged` flag set.
- Verify that the Docker socket (`/var/run/docker.sock`) is correctly mounted.

#### Pitfall 3: Data Loss Due to Missing Volumes

**Explanation**: Without proper volume mounting, Jenkins data can be lost upon container restart.

**Prevention**:
- Always mount volumes for persistent data storage.
- Regularly back up important data.

### Real-World Examples and CVEs

#### Example: Docker Hub Breach (CVE-2019-12735)

In 2019, Docker Hub experienced a breach that exposed user credentials. This highlights the importance of securing Docker images and credentials.

**Mitigation**:
- Use Docker Content Trust to verify image integrity.
- Store sensitive information securely using secrets management tools like HashiCorp Vault.

### Conclusion

Integrating Jenkins with Docker is a powerful way to streamline CI/CD processes. By following best practices and understanding the underlying concepts, you can ensure that your Jenkins jobs are efficient, reliable, and secure.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in applying the concepts covered in this chapter.

---
<!-- nav -->
[[02-Introduction to Docker and Jenkins Integration|Introduction to Docker and Jenkins Integration]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/05-Attaching Docker Volumes To Jenkins Container/00-Overview|Overview]] | [[04-Attaching Docker Volumes to Jenkins Container|Attaching Docker Volumes to Jenkins Container]]
