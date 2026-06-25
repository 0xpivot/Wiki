---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Compose Deployment on Remote Servers with Jenkins

In this chapter, we will delve into the process of deploying applications using Docker Compose on remote servers, specifically focusing on an EC2 instance, and automating this deployment with Jenkins. This approach is widely used in DevOps environments to streamline the deployment process and ensure consistency across different environments.

### What is Docker Compose?

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application’s services. Then, with a single command, you create and start all the services from your configuration.

#### Why Use Docker Compose?

1. **Simplicity**: Docker Compose simplifies the management of multi-container applications by allowing you to define all the services in a single file.
2. **Consistency**: By using a single configuration file, you ensure that the same environment is deployed consistently across different stages (development, testing, production).
3. **Automation**: Docker Compose integrates well with CI/CD pipelines, making it easier to automate the deployment process.

### Docker Compose YAML File

The Docker Compose YAML file (`docker-compose.yml`) defines the services, networks, and volumes required for your application. Here is an example of a `docker-compose.yml` file:

```yaml
version: '3'
services:
  web:
    image: my-web-app:latest
    ports:
      - "80:80"
  db:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: example
```

#### Explanation of Key Components

- **Version**: Specifies the version of the Docker Compose file format.
- **Services**: Defines the services that make up your application.
  - **web**: A service named `web` that uses the `my-web-app:latest` image.
  - **db**: A service named `db` that uses the `postgres:latest` image.
- **Ports**: Maps port 80 on the host to port 80 on the container.
- **Environment**: Sets environment variables for the `db` service.

### Installing Docker Compose on EC2 Instance

Before we can use Docker Compose on an EC2 instance, we need to ensure it is installed. Docker Compose is not included by default with Docker, so we need to install it separately.

#### Steps to Install Docker Compose

1. **Download Docker Compose**:
   ```sh
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```

2. **Apply Executable Permissions**:
   ```sh
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Verify Installation**:
   ```sh
   docker-compose --version
   ```

### Creating a Docker Compose File for Your Application

Once Docker Compose is installed, we need to create a `docker-compose.yml` file for our application. This file should define all the services required for your application.

#### Example `docker-compose.yml` File

```yaml
version: '3'
services:
  web:
    image: my-web-app:latest
    ports:
      - "80:80"
  db:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: example
```

### Adjusting Jenkinsfile to Execute Docker Compose Command

To automate the deployment process, we need to modify the Jenkinsfile to execute the Docker Compose command on the EC2 instance.

#### Example Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'docker build -t my-web-app .'
            }
        }

        stage('Deploy') {
            steps {
                sshagent(credentials: ['ec2-instance-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ec2-user@<EC2_INSTANCE_IP> '
                            docker-compose -f /path/to/docker-compose.yml up -d
                        '
                    '''
                }
            }
        }
    }
}
```

### Explanation of Jenkinsfile

- **Pipeline**: Defines the pipeline structure.
- **Agent**: Specifies the agent to run the pipeline.
- **Stages**: Defines the stages of the pipeline.
  - **Build**: Builds the Docker image.
  - **Deploy**: Deploys the application using Docker Compose.
- **SSH Agent**: Uses SSH credentials to connect to the EC2 instance.
- **SSH Command**: Executes the Docker Compose command on the EC2 instance.

### Full HTTP Request and Response Example

Here is an example of a full HTTP request and response when deploying the application using Jenkins:

#### HTTP Request

```http
POST /job/my-job/build HTTP/1.1
Host: jenkins.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=

json={"parameter": [{"name":"EC2_INSTANCE_IP", "value":"<EC2_INSTANCE_IP>"}]}
```

#### HTTP Response

```http
HTTP/1.1 201 Created
Date: Tue, 20 Mar 2023 12:00:00 GMT
Server: Jenkins
Location: http://jenkins.example.com/job/my-job/1/
Content-Length: 0
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Missing Docker Compose Installation

**Symptom**: The `docker-compose` command is not found on the EC2 instance.

**Prevention**:
- Ensure Docker Compose is installed on the EC2 instance before attempting to use it.
- Verify the installation by running `docker-compose --version`.

#### Pitfall 2: Incorrect Jenkins Credentials

**Symptom**: Jenkins fails to connect to the EC2 instance due to incorrect credentials.

**Prevention**:
- Double-check the SSH credentials used in the Jenkinsfile.
- Ensure the SSH key has the necessary permissions to access the EC2 instance.

#### Pitfall 3: Incorrect Docker Compose File Path

**Symptom**: The Docker Compose command fails due to an incorrect file path.

**Prevention**:
- Verify the path to the `docker-compose.yml` file on the EC2 instance.
- Use absolute paths to avoid issues with working directories.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-21366

CVE-2021-21366 is a vulnerability in Docker Compose that allows an attacker to execute arbitrary commands on the host system. This vulnerability was exploited in several breaches, highlighting the importance of keeping Docker Compose up to date and securing the environment.

#### Secure Coding Practices

To prevent such vulnerabilities, follow these secure coding practices:

1. **Keep Docker Compose Up to Date**: Regularly update Docker Compose to the latest version.
2. **Use Secure Credentials**: Store SSH keys securely and limit their permissions.
3. **Validate Input**: Ensure that all input parameters are validated and sanitized.

### How to Prevent / Defend

#### Detection

- **Logging**: Enable detailed logging for Docker Compose and Jenkins to monitor for suspicious activities.
- **Monitoring**: Use monitoring tools to detect unauthorized access attempts and unusual behavior.

#### Prevention

- **Secure Configuration**: Follow secure configuration guidelines for Docker Compose and Jenkins.
- **Access Control**: Implement strict access control policies to limit who can deploy and manage the application.

#### Secure-Coding Fixes

##### Vulnerable Code

```groovy
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                sshagent(credentials: ['ec2-instance-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ec2-user@<EC2_INSTANCE_IP> '
                            docker-compose -f /path/to/docker-compose.yml up -d
                        '
                    '''
                }
            }
        }
    }
}
```

##### Secure Code

```groovy
pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                sshagent(credentials: ['ec2-instance-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ec2-user@<EC2_INSTANCE_IP> '
                            docker-compose -f /path/to/docker-compose.yml up -d
                        '
                    '''
                }
            }
        }
    }
}
```

### Conclusion

In this chapter, we covered the process of deploying applications using Docker Compose on remote servers, specifically focusing on an EC2 instance, and automating this deployment with Jenkins. We explored the concepts, steps, and best practices involved in this process, including installing Docker Compose, creating a Docker Compose file, and adjusting the Jenkinsfile. We also discussed common pitfalls and provided secure coding practices to prevent potential vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in deploying and securing applications using Docker Compose and Jenkins.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/19-Docker Compose Deployment On Remote Servers With Jenkins/00-Overview|Overview]] | [[02-Introduction to Docker Compose and Deployment on Remote Servers with Jenkins|Introduction to Docker Compose and Deployment on Remote Servers with Jenkins]]
