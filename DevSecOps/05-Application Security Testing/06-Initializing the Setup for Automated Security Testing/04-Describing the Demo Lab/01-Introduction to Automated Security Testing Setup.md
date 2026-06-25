---
course: DevSecOps
topic: Initializing the Setup for Automated Security Testing
tags: [devsecops]
---

## Introduction to Automated Security Testing Setup

In this section, we will delve into the setup required for automated security testing within a DevSecOps environment. We will cover the components involved, their roles, and how they interact to create a robust and secure development pipeline. This includes setting up a Git server, a continuous integration (CI) server, and a Docker registry, all running within Docker containers managed by Docker Compose.

### Components Overview

The primary components of our setup include:

1. **Git Server**: We will use GitLab, an open-source solution for hosting and managing Git repositories.
2. **Continuous Integration (CI) Server**: Jenkins, another open-source tool, will serve as our CI server.
3. **Docker Registry**: A Docker registry will be used to store and manage Docker images.

All these components will run on a single server using Docker and Docker Compose. Let’s explore each component in detail.

### Git Server: GitLab

#### What is GitLab?

GitLab is an open-source platform for managing Git repositories. It provides a web-based interface for interacting with repositories, including features like issue tracking, code review, and continuous integration.

#### Why Use GitLab?

GitLab is chosen for several reasons:
- **Open Source**: It is free and can be customized to meet specific needs.
- **Feature-Rich**: It offers a wide range of features such as CI/CD pipelines, issue tracking, and project management.
- **Security**: GitLab includes built-in security features like two-factor authentication and access controls.

#### How Does GitLab Work?

GitLab operates by providing a web interface and API for managing Git repositories. Users can clone repositories, push changes, and collaborate through pull requests and issues.

#### Setting Up GitLab

To set up GitLab, we will use a Docker container. Here is the Docker Compose configuration for GitLab:

```yaml
version: '3'
services:
  gitlab:
    image: 'gitlab/gitlab-ce:latest'
    container_name: 'gitlab'
    hostname: 'gitlab.demo.local'
    ports:
      - '80:80'
      - '7722:22'
    volumes:
      - '/srv/gitlab/config:/etc/gitlab'
      - '/srv/gitlab/logs:/var/log/gitlab'
      - '/srv/gitlab/data:/var/opt/gitlab'
```

This configuration maps port 80 for HTTP traffic and port 7722 for SSH traffic. The `hostname` is set to `gitlab.demo.local`.

#### Security Considerations

- **Access Control**: Ensure that only authorized users can access the GitLab instance.
- **Two-Factor Authentication**: Enable two-factor authentication for added security.
- **Regular Updates**: Keep GitLab updated to the latest version to mitigate vulnerabilities.

#### Real-World Example

A notable breach involving GitLab was the **CVE-2020-14170**. This vulnerability allowed attackers to bypass authentication and gain unauthorized access to repositories. To prevent such attacks, ensure that your GitLab instance is regularly updated and patched.

### Continuous Integration (CI) Server: Jenkins

#### What is Jenkins?

Jenkins is an open-source automation server that provides a reliable and scalable system for automating all sorts of tasks from continuous integration and delivery of software to automation of complex workflows.

#### Why Use Jenkins?

Jenkins is chosen for several reasons:
- **Flexibility**: It supports a wide range of plugins and integrations.
- **Customizability**: It can be tailored to meet specific needs.
- **Community Support**: There is a large community of users and developers contributing to Jenkins.

#### How Does Jenkins Work?

Jenkins operates by defining jobs that execute a series of steps, often referred to as a pipeline. These steps can include building code, running tests, and deploying applications.

#### Setting Up Jenkins

To set up Jenkins, we will use a Docker container. Here is the Docker Compose configuration for Jenkins:

```yaml
version: '3'
services:
  jenkins:
    image: 'jenkins/jenkins:lts'
    container_name: 'jenkins'
    hostname: 'jenkins.demo.local'
    ports:
      - '8080:8080'
    volumes:
      - '/srv/jenkins:/var/jenkins_home'
```

This configuration maps port 8080 for accessing the Jenkins web interface. The `hostname` is set to `jenkins.demo.local`.

#### Security Considerations

- **Admin Access**: Restrict admin access to trusted users.
- **Plugin Management**: Regularly update and manage plugins to avoid vulnerabilities.
- **Secure Configuration**: Follow best practices for securing Jenkins configurations.

#### Real-World Example

A notable vulnerability involving Jenkins was the **CVE-2018-1000301**. This vulnerability allowed attackers to execute arbitrary code on Jenkins servers. To prevent such attacks, ensure that Jenkins is regularly updated and patched.

### Docker Registry

#### What is a Docker Registry?

A Docker registry is a storage and distribution system for Docker images. It allows users to upload and download images, making it easier to share and deploy applications.

#### Why Use a Docker Registry?

A Docker registry is chosen for several reasons:
- **Centralized Storage**: It provides a centralized location for storing Docker images.
- **Version Control**: It allows for version control of images.
- **Security**: It supports secure transmission of images using HTTPS.

#### How Does a Docker Registry Work?

A Docker registry operates by allowing users to push and pull images. Images are stored in a repository and can be tagged with versions.

#### Setting Up a Docker Registry

To set up a Docker registry, we will use a Docker container. Here is the Docker Compose configuration for the Docker registry:

```yaml
version: '3'
services:
  registry:
    image: 'registry:2'
    container_name: 'registry'
    hostname: 'registry.demo.local'
    ports:
      - '5000:5000'
    volumes:
      - '/srv/registry:/var/lib/registry'
```

This configuration maps port 5000 for accessing the Docker registry. The `hostname` is set to `registry.demo.local`.

#### Security Considerations

- **TLS Encryption**: Ensure that communication with the registry is encrypted using TLS.
- **Access Control**: Implement access control to restrict who can push and pull images.
- **Regular Backups**: Regularly back up the registry to prevent data loss.

#### Real-World Example

A notable vulnerability involving Docker registries was the **CVE-2019-12735**. This vulnerability allowed attackers to bypass authentication and gain unauthorized access to images. To prevent such attacks, ensure that your Docker registry is regularly updated and patched.

### Docker and Docker Compose

#### What is Docker?

Docker is a platform that uses OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries, and configuration files; they can communicate with each other through well-defined channels.

#### Why Use Docker?

Docker is chosen for several reasons:
- **Portability**: Applications packaged in Docker containers can run consistently across different environments.
- **Isolation**: Containers provide isolation, reducing conflicts between applications.
- **Efficiency**: Docker containers are lightweight and efficient compared to traditional virtual machines.

#### How Does Docker Work?

Docker operates by creating and managing containers. Containers are created from Docker images, which are built from Dockerfiles.

#### What is Docker Compose?

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration.

#### How Does Docker Compose Work?

Docker Compose reads a `docker-compose.yml` file and starts all the services defined in it. This makes it easy to manage multiple containers and their dependencies.

#### Setting Up Docker and Docker Compose

To set up Docker and Docker Compose, follow these steps:

1. **Install Docker**: Install Docker on your server.
2. **Install Docker Compose**: Install Docker Compose on your server.
3. **Create Docker Compose File**: Create a `docker-compose.yml` file with the configurations for GitLab, Jenkins, and the Docker registry.

Here is an example `docker-compose.yml` file:

```yaml
version: '3'
services:
  gitlab:
    image: 'gitlab/gitlab-ce:latest'
    container_name: 'gitlab'
    hostname: 'gitlab.demo.local'
    ports:
      - '80:80'
      - '7722:22'
    volumes:
      - '/srv/gitlab/config:/etc/gitlab'
      - '/srv/gitlab/logs:/var/log/gitlab'
      - '/srv/gitlab/data:/var/opt/gitlab'

  jenkins:
    image: 'jenkins/jenkins:lts'
    container_name: 'jenkins'
    hostname: 'jenkins.demo.local'
    ports:
      - '8080:8080'
    volumes:
      - '/srv/jenkins:/var/jenkins_home'

  registry:
    image: 'registry:2'
    container_name: 'registry'
    hostname: 'registry.demo.local'
    ports:
      - '5000:5000'
    volumes:
      - '/srv/registry:/var/lib/registry'
```

#### Security Considerations

- **Container Isolation**: Ensure that containers are properly isolated from each other.
- **Image Scanning**: Regularly scan Docker images for vulnerabilities.
- **Network Security**: Secure the network connections between containers.

#### Real-World Example

A notable vulnerability involving Docker was the **CVE-2019-14287**. This vulnerability allowed attackers to escape the container and gain access to the host system. To prevent such attacks, ensure that Docker is regularly updated and patched.

### Workflow for Automated Security Testing

#### What is the Workflow?

The workflow for automated security testing involves pushing code to the GitLab server, triggering a CI job in Jenkins, and deploying the application using Docker images from the registry.

#### Steps in the Workflow

1. **Push Code to GitLab**: Developers push code to the GitLab repository.
2. **Trigger CI Job in Jenkins**: The push triggers a CI job in Jenkins.
3. **Build and Test**: Jenkins builds the code and runs tests.
4. **Deploy Application**: Jenkins deploys the application using Docker images from the registry.

#### Example Workflow

Here is an example of a simple CI/CD pipeline in Jenkins:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://gitlab.demo.local/my-repo.git', branch: 'main'
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
                script {
                    docker.withRegistry('https://registry.demo.local:5000', 'docker-credentials') {
                        def app = docker.build("my-app:${env.BUILD_ID}")
                        app.push("${env.BUILD_ID}")
                    }
                }
            }
        }
    }
}
```

#### Security Considerations

- **Code Quality**: Ensure that the code pushed to GitLab meets quality standards.
- **Test Coverage**: Ensure that tests cover all critical parts of the application.
- **Deployment Security**: Ensure that the deployment process is secure and follows best practices.

#### Real-World Example

A notable breach involving CI/CD pipelines was the **CVE-2021-22555**. This vulnerability allowed attackers to inject malicious code into the CI/CD pipeline. To prevent such attacks, ensure that your CI/CD pipeline is regularly updated and patched.

### Hands-On Labs

To practice setting up and configuring the components discussed, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive web application that teaches about web application security.

These labs will help you gain practical experience in setting up and securing a DevSecOps environment.

### Conclusion

In this section, we have covered the setup required for automated security testing within a DevSecOps environment. We explored the components involved, their roles, and how they interact to create a robust and secure development pipeline. By following the steps and best practices outlined, you can ensure that your development environment is secure and efficient.

### Further Reading

For further reading and deeper understanding, consider the following resources:

- **Docker Documentation**: Official documentation for Docker.
- **Jenkins Documentation**: Official documentation for Jenkins.
- **GitLab Documentation**: Official documentation for GitLab.
- **OWASP Cheat Sheets**: Security best practices and guidelines.

By leveraging these resources, you can continue to enhance your knowledge and skills in DevSecOps and automated security testing.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/06-Initializing the Setup for Automated Security Testing/05-Describing the Demo Lab/00-Overview|Overview]] | [[02-Initializing the Setup for Automated Security Testing|Initializing the Setup for Automated Security Testing]]
