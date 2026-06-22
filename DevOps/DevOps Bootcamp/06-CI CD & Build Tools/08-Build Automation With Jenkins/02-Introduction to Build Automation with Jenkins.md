---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Build Automation with Jenkins

Build automation is a critical component of modern DevOps practices. It ensures that code changes can be tested, built, and deployed consistently and reliably. Jenkins is one of the most popular open-source continuous integration and continuous delivery (CI/CD) tools used for automating the software development process. In this chapter, we will delve into how to set up a Jenkins environment to automate the build process, including version incrementation, testing, building Docker images, and pushing them to a private Docker repository. We will also explore how to create a Jenkins shared library to make pipeline code reusable across different projects.

### What is Jenkins?

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. It is written in Java and supports a wide range of operating systems, including Windows, macOS, and various Linux distributions. Jenkins is highly extensible through its plugin ecosystem, which allows users to integrate with numerous tools and services.

#### Why Use Jenkins?

1. **Automation**: Jenkins automates repetitive tasks such as building, testing, and deploying applications.
2. **Integration**: It integrates seamlessly with version control systems like Git, SVN, and Mercurial.
3. **Plugins**: Jenkins has a vast collection of plugins that extend its functionality to support various tools and services.
4. **Scalability**: Jenkins can scale horizontally using a master-slave architecture, allowing it to handle large-scale builds and deployments.
5. **Community Support**: Being an open-source project, Jenkins has a large community of users and contributors who provide support and new features.

### Setting Up Jenkins

To get started with Jenkins, you need to install it on your machine. Here are the steps to install Jenkins on a Linux system:

1. **Install Java**: Jenkins requires Java to run. You can install OpenJDK using the following commands:
    ```bash
    sudo apt update
    sudo apt install default-jdk
    ```

2. **Add Jenkins Repository**:
    ```bash
    wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
    sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
    ```

3. **Install Jenkins**:
    ```bash
    sudo apt update
    sudo apt install jenkins
    ```

4. **Start Jenkins**:
    ```bash
    sudo systemctl start jenkins
    sudo systemctl enable jenkins
    ```

5. **Access Jenkins**: Open a web browser and navigate to `http://localhost:8080`. Follow the initial setup instructions to complete the installation.

### Configuring Automated Version Incrementation

Automated version incrementation is crucial for maintaining a consistent and traceable build history. Jenkins can be configured to automatically increment the version number of your application with each build.

#### Using the `Version Number Plugin`

The `Version Number Plugin` is a popular choice for managing version numbers in Jenkins. Here’s how to set it up:

1. **Install the Plugin**: Go to `Manage Jenkins` > `Manage Plugins`, search for `Version Number Plugin`, and install it.

2. **Configure the Plugin**: Once installed, go to `Manage Jenkins` > `Configure System` and scroll down to the `Version Number Plugin` section. Configure the plugin settings according to your requirements.

3. **Use the Plugin in Your Pipeline**: In your Jenkinsfile, you can use the `versionNumber` step to generate a version number. Here’s an example:

```groovy
pipeline {
    agent any
    stages {
        stage('Generate Version') {
            steps {
                script {
                    def version = versionNumber()
                    echo "Generated version: ${version}"
                }
            }
        }
    }
}
```

### Building a Scripted Pipeline

A scripted pipeline in Jenkins is defined using Groovy syntax. This approach provides more flexibility compared to declarative pipelines. Let’s walk through the steps to create a scripted pipeline that triggers automatically on code changes, tests the application, builds a Docker image, and pushes it to a private Docker repository.

#### Step-by-Step Guide

1. **Define the Pipeline**: Create a `Jenkinsfile` in your repository to define the pipeline.

2. **Trigger on Code Changes**: Use the `pollSCM` step to trigger the pipeline on code changes.

3. **Test the Application**: Run tests using a testing framework like JUnit.

4. **Build Docker Image**: Use the `docker.build` step to build a Docker image.

5. **Push to Private Docker Repository**: Use the `docker.push` step to push the image to a private Docker repository.

Here’s a complete example of a scripted pipeline:

```groovy
node {
    // Checkout code from SCM
    checkout scm

    // Define environment variables
    def dockerImageName = 'myapp'
    def dockerTag = versionNumber()

    // Run tests
    stage('Test') {
        sh 'mvn test'
    }

    // Build Docker image
    stage('Build Docker Image') {
        docker.build("${dockerImageName}:${dockerTag}")
    }

    // Push Docker image to private repository
    stage('Push Docker Image') {
        docker.withRegistry('https://registry.example.com', 'docker-credentials-id') {
            docker.push("${dockerImageName}:${dockerTag}")
        }
    }
}
```

### Creating a Jenkins Shared Library

A Jenkins shared library is a collection of Groovy scripts that can be reused across multiple pipelines. This promotes code reuse and consistency.

#### Steps to Create a Shared Library

1. **Create a Git Repository**: Create a new Git repository to store your shared library.

2. **Define the Structure**: The shared library should have a specific structure. Here’s an example:

    ```
    src/
      org/
        mycompany/
          pipeline/
            steps/
              MyStep.groovy
            libraries/
              MyLibrary.groovy
    vars/
      myVar.groovy
    ```

3. **Define Shared Functions**: Write Groovy functions in the `vars` directory to define reusable steps.

4. **Configure Jenkins**: In Jenkins, go to `Manage Jenkins` > `Global Pipeline Libraries` and add your shared library.

Here’s an example of a shared function in `myVar.groovy`:

```groovy
def call(String name) {
    echo "Hello, ${name}!"
}
```

In your pipeline, you can now use this shared function:

```groovy
pipeline {
    agent any
    stages {
        stage('Say Hello') {
            steps {
                script {
                    myVar 'World'
                }
            }
        }
    }
}
```

### Real-World Examples and Security Considerations

#### Example: CVE-2021-21234

CVE-2021-21234 is a security vulnerability in Jenkins that allows remote code execution. This vulnerability affects Jenkins versions prior to 2.289.3 and 2.277.4.

**Impact**: An attacker could exploit this vulnerability to execute arbitrary code on the Jenkins server.

**Prevention**:
1. **Update Jenkins**: Ensure that Jenkins is updated to the latest version.
2. **Security Hardening**: Apply security hardening measures such as disabling unnecessary plugins and securing Jenkins credentials.

**Detection**:
1. **Monitor Logs**: Regularly monitor Jenkins logs for suspicious activities.
2. **Use Security Tools**: Utilize security tools like SonarQube to scan Jenkins configurations for vulnerabilities.

#### Example: Docker Image Vulnerabilities

Docker images can contain vulnerabilities that can be exploited by attackers. For example, CVE-2020-14386 is a vulnerability in the Docker daemon that allows privilege escalation.

**Impact**: An attacker could exploit this vulnerability to gain root access to the host system.

**Prevention**:
1. **Scan Images**: Use tools like Trivy or Clair to scan Docker images for vulnerabilities.
2. **Use Secure Base Images**: Use base images from trusted sources and ensure they are regularly updated.

**Detection**:
1. **Continuous Scanning**: Implement continuous scanning of Docker images during the build process.
2. **Regular Audits**: Conduct regular audits of Docker images to identify and remediate vulnerabilities.

### Pitfalls and Common Mistakes

1. **Hardcoding Credentials**: Avoid hardcoding credentials in your Jenkinsfiles. Use Jenkins credentials management instead.
2. **Ignoring Security Best Practices**: Always follow security best practices, such as keeping Jenkins and plugins up to date.
3. **Not Testing Pipelines**: Ensure that your pipelines are thoroughly tested to avoid unexpected issues during production.

### How to Prevent / Defend

#### Detection

1. **Monitoring**: Use monitoring tools to track Jenkins activity and detect anomalies.
2. **Logging**: Enable detailed logging to capture all actions performed by Jenkins.

#### Prevention

1. **Secure Configuration**: Follow secure configuration guidelines for Jenkins, such as enabling CSRF protection and using strong passwords.
2. **Regular Updates**: Keep Jenkins and all plugins up to date to mitigate known vulnerabilities.

#### Secure Coding Fixes

**Vulnerable Code**:
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

**Fixed Code**:
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'maven-credentials', usernameVariable: 'MAVEN_USERNAME', passwordVariable: 'MAVEN_PASSWORD')]) {
                    sh 'mvn -Dmaven.repo.username=$MAVEN_USERNAME -Dmaven.repo.password=$MAVEN_PASSWORD clean package'
                }
            }
        }
    }
}
```

### Conclusion

In this chapter, we covered the fundamentals of build automation with Jenkins, including automated version incrementation, building Docker images, and creating a shared library. We also explored real-world examples and security considerations to ensure that your Jenkins setup is robust and secure. By following these best practices, you can effectively automate your build processes and maintain a high level of security in your DevOps pipeline.

### Practice Labs

For hands-on experience with Jenkins and build automation, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including some that involve Jenkins.
- **OWASP Juice Shop**: A deliberately insecure web application that includes challenges related to CI/CD pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Another web application with security vulnerabilities that can be used to practice CI/CD pipeline security.

These labs provide practical experience in setting up and securing Jenkins environments, making them invaluable resources for mastering build automation with Jenkins.

---
<!-- nav -->
[[01-Introduction to Build Automation and Continuous Integration|Introduction to Build Automation and Continuous Integration]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/08-Build Automation With Jenkins/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/08-Build Automation With Jenkins/03-Practice Questions & Answers|Practice Questions & Answers]]
