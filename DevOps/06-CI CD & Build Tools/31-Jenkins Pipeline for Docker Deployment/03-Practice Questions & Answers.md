---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the process of deploying a Docker image from Jenkins to an EC2 instance.**

The process involves several steps:

1. **Building the Docker Image**: Jenkins checks out the code from the Git repository, builds the application, and creates a Docker image.
2. **Pushing the Docker Image**: The newly built Docker image is pushed to a private Docker repository.
3. **Setting Up SSH Credentials**: An SSH agent plugin is installed in Jenkins, and SSH credentials (including the PEM file) are created and stored in Jenkins.
4. **Updating the Jenkinsfile**: The Jenkinsfile is modified to include the SSH agent plugin syntax, specifying the SSH credentials and the EC2 instance details.
5. **Executing the SSH Command**: Jenkins uses the SSH agent plugin to SSH into the EC2 instance and executes the `docker run` command to start the container.
6. **Configuring Firewall Rules**: Ensure that the Jenkins server’s IP address is allowed to connect to the EC2 instance via the SSH port and that the application port is open.

**Q2. How would you configure the SSH agent plugin in Jenkins to deploy a Docker image to an EC2 instance?**

To configure the SSH agent plugin in Jenkins for deploying a Docker image to an EC2 instance, follow these steps:

1. **Install SSH Agent Plugin**: Go to Manage Jenkins > Manage Plugins, search for the SSH Agent plugin, and install it.
2. **Create SSH Credentials**: Navigate to Manage Jenkins > Manage Credentials > System > Global credentials (unrestricted). Click on Add Credentials, select SSH Username with private key, and provide the username and private key (PEM file).
3. **Update Jenkinsfile**: Modify the Jenkinsfile to include the SSH agent plugin syntax. Use the following Groovy syntax:

```groovy
pipeline {
    agent any
    environment {
        SSH_CREDENTIALS_ID = 'your-ssh-credentials-id'
        EC2_IP_ADDRESS = 'your-ec2-ip-address'
        DOCKER_IMAGE_NAME = 'your-docker-image-name'
    }
    stages {
        stage('Deploy') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS_ID]) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${SSH_USER}@${EC2_IP_ADDRESS} '
                            docker run -d -p 8080:8080 ${DOCKER_IMAGE_NAME}:latest
                        '
                    '''
                }
            }
        }
    }
}
```

Replace placeholders with actual values.

**Q3. Why is it necessary to configure firewall rules on the EC2 instance before deploying from Jenkins?**

It is necessary to configure firewall rules on the EC2 instance before deploying from Jenkins because:

1. **Security**: By default, all incoming traffic is blocked on an EC2 instance. Configuring firewall rules ensures that only authorized traffic is allowed.
2. **Access Control**: The firewall rules specify which IP addresses are permitted to connect to the EC2 instance. This prevents unauthorized access and ensures that only the Jenkins server can SSH into the EC2 instance.
3. **Port Accessibility**: Opening specific ports (e.g., SSH port 22 and application port 8080) ensures that the Jenkins server can connect to the EC2 instance and that the application is accessible over the network.

**Q4. How can you use the SSH agent plugin to deploy a Docker Compose application to an EC2 instance?**

To deploy a Docker Compose application to an EC2 instance using the SSH agent plugin, follow these steps:

1. **Prepare Docker Compose File**: Ensure that the Docker Compose file is included in the Git repository.
2. **Modify Jenkinsfile**: Update the Jenkinsfile to include the SSH agent plugin syntax and the necessary commands to copy the Docker Compose file and execute `docker-compose up`.

Example Jenkinsfile snippet:

```groovy
pipeline {
    agent any
    environment {
        SSH_CREDENTIALS_ID = 'your-ssh-credentials-id'
        EC2_IP_ADDRESS = 'your-ec2-ip-address'
        DOCKER_COMPOSE_FILE = 'path/to/docker-compose.yml'
    }
    stages {
        stage('Deploy Docker Compose') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS_ID]) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${SSH_USER}@${EC2_IP_ADDRESS} '
                            mkdir -p /opt/app && cd /opt/app &&
                            scp ${SSH_USER}@${JENKINS_SERVER_IP}:${DOCKER_COMPOSE_FILE} . &&
                            docker-compose up -d
                        '
                    '''
                }
            }
        }
    }
}
```

Replace placeholders with actual values.

**Q5. What are the limitations of manually deploying Docker containers to an EC2 instance using SSH, and how can Kubernetes help overcome these limitations?**

Limitations of manually deploying Docker containers to an EC2 instance using SSH include:

1. **Scalability Issues**: Manually managing multiple containers across multiple instances becomes cumbersome and error-prone.
2. **Complexity**: Managing container lifecycles, health checks, and scaling requires significant manual effort.
3. **Consistency**: Ensuring consistent deployment and management practices across multiple environments is challenging.

Kubernetes helps overcome these limitations by providing:

1. **Orchestration**: Kubernetes automates the deployment, scaling, and management of containerized applications.
2. **Health Checks and Self-Healing**: Kubernetes continuously monitors the health of containers and automatically restarts or reschedules unhealthy containers.
3. **Scaling**: Kubernetes supports horizontal scaling, allowing you to easily scale your application based on demand.
4. **Consistency**: Kubernetes provides a consistent framework for deploying and managing applications across different environments.

By using Kubernetes, you can simplify the deployment and management of Dockerized applications, ensuring scalability, reliability, and consistency.

---
<!-- nav -->
[[02-Jenkins Pipeline for Docker Deployment|Jenkins Pipeline for Docker Deployment]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/31-Jenkins Pipeline for Docker Deployment/00-Overview|Overview]]
