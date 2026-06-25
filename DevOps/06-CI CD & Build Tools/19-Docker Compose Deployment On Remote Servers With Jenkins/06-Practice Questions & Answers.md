---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the process of installing Docker Compose on an EC2 instance.**

To install Docker Compose on an EC2 instance, you need to follow these steps:

1. Download the Docker Compose binary from the official Docker documentation.
2. Make the downloaded binary executable by changing its permissions.
3. Verify the installation by checking the Docker Compose version.

Here is the command sequence:

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

This ensures that Docker Compose is installed and ready to be used on the EC2 instance.

**Q2. How do you create a Docker Compose file for a Java Maven application with a PostgreSQL database?**

To create a Docker Compose file for a Java Maven application with a PostgreSQL database, you need to define the services in a `docker-compose.yml` file. Here’s an example:

```yaml
version: '3.8'
services:
  java-maven-app:
    image: your-repo/java-maven-app:latest
    ports:
      - "8080:8080"
  postgres:
    image: postgres:13
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: myPWD
```

This file specifies the image names, ports to expose, and environment variables for the PostgreSQL service.

**Q3. How would you modify the Jenkinsfile to copy a Docker Compose file to an EC2 instance and execute Docker Compose commands?**

To modify the Jenkinsfile to copy a Docker Compose file to an EC2 instance and execute Docker Compose commands, you can use the following steps:

1. Use the `scp` command to copy the Docker Compose file to the EC2 instance.
2. Execute the Docker Compose command via SSH.

Here is an example Jenkinsfile snippet:

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh 'scp docker-compose.yml ec2-user@ec2-instance:/home/ec2-user/'
                    sh 'ssh ec2-user@ec2-instance "cd /home/ec2-user && docker-compose up -d"'
                }
            }
        }
    }
}
```

This Jenkinsfile uses SSH agent to handle the credentials and performs the necessary steps to deploy the application.

**Q4. How can you pass dynamic image tags to Docker Compose from a Jenkins pipeline?**

To pass dynamic image tags to Docker Compose from a Jenkins pipeline, you can use environment variables and shell scripts. Here’s how you can achieve this:

1. Define a placeholder in the Docker Compose file for the image tag.
2. Pass the dynamic image tag as an environment variable to a shell script.
3. Replace the placeholder in the Docker Compose file with the dynamic image tag.

Example Docker Compose file (`docker-compose.yml`):

```yaml
version: '3.8'
services:
  java-maven-app:
    image: your-repo/java-maven-app:${IMAGE_TAG}
    ports:
      - "8080:8080"
```

Jenkinsfile snippet:

```groovy
pipeline {
    agent any
    environment {
        IMAGE_TAG = '2.0' // This can be dynamically generated
    }
    stages {
        stage('Deploy') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh 'scp docker-compose.yml ec2-user@ec2-instance:/home/ec2-user/'
                    sh 'ssh ec2-user@ec2-instance "export IMAGE_TAG=${IMAGE_TAG} && cd /home/ec2-user && docker-compose up -d"'
                }
            }
        }
    }
}
```

This approach allows you to dynamically set the image tag in the Docker ComCompose file from the Jenkins pipeline.

**Q5. What are some optimizations you can apply to the Docker Compose and Jenkinsfile setup?**

Some optimizations you can apply to the Docker Compose and Jenkinsfile setup include:

1. Extracting common values into variables to avoid redundancy.
2. Using a Jenkins shared library to encapsulate reusable logic.
3. Dynamically generating version tags during the build process.
4. Passing only the version tag rather than the entire image name to reduce complexity.

For example, you can refactor the Jenkinsfile to use a shared library:

```groovy
@Library('my-shared-library') _

pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                deployApp(imageTag: '2.0', ec2Instance: 'ec2-user@ec2-instance')
            }
        }
    }
}
```

This shared library approach makes the pipeline more modular and easier to maintain.

---
<!-- nav -->
[[05-Passing Parameters to Shell Scripts in Jenkins|Passing Parameters to Shell Scripts in Jenkins]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/19-Docker Compose Deployment On Remote Servers With Jenkins/00-Overview|Overview]]
