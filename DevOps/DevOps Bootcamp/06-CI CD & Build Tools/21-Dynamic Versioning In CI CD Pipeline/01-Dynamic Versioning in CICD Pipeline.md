---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Dynamic Versioning in CI/CD Pipeline

### Introduction to CI/CD Pipelines

Continuous Integration (CI) and Continuous Deployment (CD) pipelines are essential components of modern software development practices. These pipelines automate the process of building, testing, and deploying applications, ensuring that changes are integrated and validated quickly and reliably. A typical CI/CD pipeline includes stages such as building the application, running tests, packaging the application, and deploying it to various environments.

In the context of a Java Maven application, the pipeline might involve compiling the code, running unit tests, creating a JAR file, and then deploying the application using Docker containers. This setup ensures that the application is built and tested consistently across different environments, reducing the likelihood of integration issues.

### Dynamic Versioning in CI/CD

Dynamic versioning is a practice where the version number of an application is automatically incremented during the CI/CD process. This is particularly useful in environments where frequent releases are necessary, as it helps track the exact version of the application that is deployed in each environment.

#### Why Dynamic Versioning?

Dynamic versioning serves several purposes:

1. **Tracking Changes**: Each version number corresponds to a specific set of changes, making it easier to track and revert changes if necessary.
2. **Automation**: Automating the versioning process reduces the risk of human error and ensures consistency across deployments.
3. **Integration with Version Control Systems**: Dynamic versioning can be integrated with version control systems like Git, allowing the version number to reflect the commit hash or branch name.

#### How Dynamic Versioning Works

In a CI/CD pipeline, dynamic versioning typically involves the following steps:

1. **Version Increment**: Automatically increment the version number based on predefined rules (e.g., semantic versioning).
2. **Commit Version Update**: Commit the updated version number back to the version control system.
3. **Build and Deploy**: Use the updated version number during the build and deployment stages.

### Example: Java Maven Application with Docker

Let's consider a Java Maven application that uses Docker for deployment. The pipeline will include the following stages:

1. **Checkout Code**: Clone the repository from Git.
2. **Build JAR**: Compile the code and create a JAR file.
3. **Create Docker Image**: Build a Docker image from the JAR file.
4. **Deploy Docker Image**: Deploy the Docker image to a target environment.

#### Step-by-Step Implementation

1. **Checkout Code**:
    ```bash
    git clone https://github.com/your-repo.git
    ```

2. **Build JAR**:
    ```bash
    mvn clean package
    ```

3. **Create Docker Image**:
    ```Dockerfile
    FROM openjdk:11-jdk-slim
    COPY target/myapp.jar /usr/local/lib/myapp.jar
    ENTRYPOINT ["java", "-jar", "/usr/local/lib/myapp.jar"]
    ```

4. **Deploy Docker Image**:
    ```bash
    docker build -t myapp:latest .
    docker run -d --name myapp-container myapp:latest
    ```

### Automating Versioning with Jenkins

Jenkins is a popular CI/CD tool that supports automation of versioning and deployment processes. We can use Jenkins to automate the versioning and deployment of our Java Maven application.

#### Jenkins Shared Libraries

Jenkins shared libraries allow you to encapsulate common tasks and reuse them across multiple Jenkins jobs. This is particularly useful for tasks like versioning and deployment.

1. **Create a Shared Library**:
    - Create a new directory for the shared library.
    - Add a `vars` directory within the shared library directory.
    - Create a Groovy script for versioning and deployment.

    ```groovy
    // vars/versionAndDeploy.groovy
    def call() {
        // Increment version number
        sh 'mvn versions:set -DnewVersion=${BUILD_NUMBER}'
        
        // Commit version update
        sh 'git add pom.xml'
        sh 'git commit -m "Update version to ${BUILD_NUMBER}"'
        sh 'git push origin HEAD'
        
        // Build JAR
        sh 'mvn clean package'
        
        // Create Docker image
        sh 'docker build -t myapp:${BUILD_NUMBER} .'
        
        // Deploy Docker image
        sh 'docker run -d --name myapp-container myapp:${BUILD_NUMBER}'
    }
    ```

2. **Use the Shared Library in Jenkinsfile**:
    ```groovy
    // Jenkinsfile
    @Library('my-shared-library') _

    pipeline {
        agent any
        stages {
            stage('Version and Deploy') {
                steps {
                    versionAndDeploy()
                }
            }
        }
    }
    ```

### Container Orchestration Tools

For more complex applications, Docker Compose may not be sufficient to manage the containers. In such cases, container orchestration tools like Kubernetes are used.

#### Kubernetes Deployment

Kubernetes is a powerful container orchestration platform that allows you to manage and scale containerized applications. Here’s how you can deploy a Java Maven application using Kubernetes.

1. **Create a Docker Image**:
    ```Dockerfile
    FROM openjdk:11-jdk-slim
    COPY target/myapp.jar /usr/local/lib/myapp.jar
    ENTRYPOINT ["java", "-jar", "/usr/local/lib/myapp.jar"]
    ```

2. **Build and Push Docker Image**:
    ```bash
    docker build -t myapp:latest .
    docker tag myapp:latest myregistry.com/myapp:latest
    docker push myregistry.com/myapp:latest
    ```

3. **Create Kubernetes Deployment**:
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: myapp-deployment
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: myapp
      template:
        metadata:
          labels:
            app: myapp
        spec:
          containers:
          - name: myapp
            image: myregistry.com/myapp:latest
            ports:
            - containerPort: 8080
    ```

4. **Apply Kubernetes Deployment**:
    ```bash
    kubectl apply -f deployment.yaml
    ```

### Real-World Examples and CVEs

#### CVE-2021-21277: Docker Compose Vulnerability

CVE-2021-21277 is a vulnerability in Docker Compose that allows attackers to execute arbitrary commands on the host machine. This vulnerability highlights the importance of using container orchestration tools like Kubernetes, which provide better security and isolation.

#### Secure Coding Practices

To prevent vulnerabilities like CVE-2021-21277, follow these secure coding practices:

1. **Use Least Privilege Principle**: Ensure that containers run with the least privileges necessary.
2. **Validate Inputs**: Validate all inputs to prevent injection attacks.
3. **Keep Dependencies Updated**: Regularly update dependencies to patch known vulnerabilities.

### How to Prevent / Defend

#### Detection

- **Static Analysis**: Use static analysis tools like SonarQube to identify potential security issues in the code.
- **Dependency Scanning**: Use tools like Snyk to scan for vulnerable dependencies.

#### Prevention

- **Least Privilege Principle**: Run containers with minimal permissions.
- **Regular Updates**: Keep all dependencies and tools up to date.
- **Secure Configuration**: Follow secure configuration guidelines for Docker and Kubernetes.

#### Secure-Coding Fixes

**Vulnerable Code**:
```groovy
sh 'docker run -d --name myapp-container myapp:latest'
```

**Secure Code**:
```groovy
sh 'docker run --security-opt=no-new-privileges -d --name myapp-container myapp:latest'
```

### Conclusion

Dynamic versioning in CI/CD pipelines is a crucial practice that helps track changes and automate the deployment process. By using tools like Jenkins and container orchestration platforms like Kubernetes, you can ensure that your application is built, tested, and deployed securely and efficiently.

### Practice Labs

For hands-on experience with CI/CD pipelines and dynamic versioning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **CloudGoat**: Provides hands-on labs for learning cloud security concepts.
- **Kubernetes Goat**: Offers practical exercises for learning Kubernetes security.

By completing these labs, you can gain a deeper understanding of how to implement and secure CI/CD pipelines in real-world scenarios.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/21-Dynamic Versioning In CI CD Pipeline/00-Overview|Overview]] | [[02-Dynamic Versioning in CICD Pipelines|Dynamic Versioning in CICD Pipelines]]
