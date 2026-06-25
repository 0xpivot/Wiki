---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins Pipeline for Docker Deployment

In the realm of continuous integration and continuous deployment (CI/CD), Jenkins stands out as a powerful tool for automating the software development lifecycle. One of the key features of Jenkins is its ability to manage complex pipelines, including the deployment of Docker containers to various environments. This chapter will delve into the intricacies of setting up a Jenkins pipeline for Docker deployment, focusing particularly on the management of SSH credentials for secure access to remote servers.

### Understanding Credentials Management in Jenkins

Before diving into the specifics of SSH credentials, it’s essential to understand the broader context of credentials management in Jenkins. Jenkins provides a robust mechanism to store and manage sensitive information such as usernames, passwords, API tokens, and SSH keys. These credentials are stored securely and can be referenced within Jenkins jobs and pipelines.

#### Types of Credentials

Jenkins supports several types of credentials:

1. **Username with Password**: This is the most basic form of authentication, typically used for services like Docker Hub or Nexus.
2. **SSH Username with Private Key**: This type of credential is used for SSH-based authentication, which is crucial for accessing remote servers securely.
3. **API Token**: Used for services that require API access, such as GitHub or GitLab.
4. **Certificate**: Used for SSL/TLS encryption and authentication.

Each type of credential serves a specific purpose and is chosen based on the requirements of the service being accessed.

### SSH Credentials in Jenkins

SSH (Secure Shell) is a cryptographic network protocol for operating network services securely over an unsecured network. In Jenkins, SSH credentials are used to establish secure connections to remote servers, such as EC2 instances in AWS. This section will focus on managing SSH credentials in Jenkins.

#### Creating SSH Credentials

To create SSH credentials in Jenkins, follow these steps:

1. **Navigate to Credentials Management**:
   - Go to `Manage Jenkins` > `Manage Credentials`.
   - Select the domain where you want to store the credentials (e.g., `Global`).

2. **Add New Credentials**:
   - Click on `Add Credentials`.
   - Choose `SSH Username with private key`.

3. **Fill in the Details**:
   - **Username**: Enter the username for the remote server (e.g., `ec2-user`).
   - **Private Key**: Paste the contents of your SSH private key (PEM file).
   - **Passphrase**: If your SSH key has a passphrase, enter it here. Otherwise, leave it blank.

4. **Save the Credentials**:
   - Click `OK` to save the new SSH credentials.

Here is an example of creating SSH credentials in Jenkins:

```markdown
### Adding SSH Credentials in Jenkins

1. **Navigate to Credentials Management**:
   - Go to `Manage Jenkins` > `Manage Credentials`.
   - Select the domain where you want to store the credentials (e.g., `Global`).

2. **Add New Credentials**:
   - Click on `Add Credentials`.
   - Choose `SSH Username with private key`.

3. **Fill in the Details**:
   - **Username**: `ec2-user`
   - **Private Key**: 
     ```plaintext
     -----BEGIN RSA PRIVATE KEY-----
     MIIEowIBAAKCAQEA...
     -----END RSA PRIVATE KEY-----
     ```
   - **Passphrase**: Leave blank if no passphrase is required.

4. **Save the Credentials**:
   - Click `OK` to save the new SSH credentials.
```

### Using SSH Credentials in Jenkins Pipeline

Once the SSH credentials are created, they can be referenced in a Jenkins pipeline to execute commands on a remote server. This section will cover how to use the SSH agent plugin to manage SSH credentials within a pipeline.

#### SSH Agent Plugin

The SSH Agent plugin in Jenkins allows you to use SSH credentials within a pipeline. It provides a way to temporarily load SSH credentials into the environment, making them available for SSH operations.

##### Syntax for Using SSH Agent Plugin

The SSH Agent plugin uses the following syntax in a Jenkinsfile:

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy Docker') {
            steps {
                sshagent(credentials: ['ssh-credentials-id']) {
                    sh 'ssh -o StrictHostKeyChecking=no ec2-user@<remote-server-ip> "docker login -u <username> -p <password>"'
                    sh 'ssh -o StrictHostKeyChecking=no ec2-user@<remote-server-ip> "docker pull <image-name>:<tag>"'
                    sh 'ssh -o StrictHostKeyChecking=no ec2-user@<remote-server-ip> "docker run -d --name <container-name> <image-name>:<tag>"'
                }
            }
        }
    }
}
```

Here is a detailed breakdown of the pipeline:

1. **Agent**: Specifies the agent where the pipeline will run.
2. **Stages**: Defines the stages of the pipeline.
3. **Steps**: Contains the steps executed within each stage.
4. **sshagent**: A block that loads the specified SSH credentials into the environment.
5. **sh**: Executes shell commands within the SSH session.

#### Example Jenkinsfile

Below is a complete example of a Jenkinsfile that deploys a Docker container to an EC2 instance using SSH credentials:

```groovy
pipeline {
    agent any
    environment {
        REMOTE_SERVER_IP = '<remote-server-ip>'
        DOCKER_IMAGE_NAME = '<image-name>'
        DOCKER_TAG = '<tag>'
        CONTAINER_NAME = '<container-name>'
    }
    stages {
        stage('Deploy Docker') {
            steps {
                sshagent(credentials: ['ssh-credentials-id']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ec2-user@$REMOTE_SERVER_IP "docker login -u <username> -p <password>"
                        ssh -o StrictHost
                    """
                }
            }
        }
    }
}
```

### Common Pitfalls and Best Practices

When working with SSH credentials in Jenkins, there are several common pitfalls to avoid:

1. **Hardcoding Credentials**: Avoid hardcoding credentials directly in the Jenkinsfile. Use the credentials management feature to securely store and reference credentials.
2. **SSH Key Passphrases**: Ensure that SSH keys are protected with passphrases to enhance security.
3. **Strict Host Key Checking**: Disable strict host key checking (`-o StrictHostKeyChecking=no`) only for testing purposes. In production, ensure proper host key verification to prevent man-in-the-middle attacks.

### How to Prevent / Defend

#### Detection

To detect unauthorized access or misuse of SSH credentials, implement the following measures:

1. **Audit Logs**: Enable audit logs for SSH access and monitor them regularly.
2. **Alerts**: Set up alerts for suspicious activities, such as failed login attempts or unauthorized commands.

#### Prevention

To prevent unauthorized access and misuse of SSH credentials, follow these best practices:

1. **Use Strong Passphrases**: Protect SSH keys with strong passphrases.
2. **Limit Access**: Restrict SSH access to only necessary users and IP addresses.
3. **Regular Audits**: Conduct regular audits of SSH access logs to identify and address potential security issues.

#### Secure Coding Fixes

Here is an example of a vulnerable Jenkinsfile and its secure counterpart:

**Vulnerable Jenkinsfile**:
```groovy
pipeline {
    agent any
    stages {
        stage('Deploy Docker') {
            steps {
                sh 'ssh -o StrictHostKeyChecking=no ec2-user@<remote-server-ip> "docker login -u <username> -p <password>"'
            }
        }
    }
}
```

**Secure Jenkinsfile**:
```groovy
pipeline {
    agent any
    environment {
        REMOTE_SERVER_IP = '<remote-server-ip>'
    }
    stages {
        stage('Deploy Docker') {
            steps {
                sshagent(credentials: ['ssh-credentials-id']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ec2-user@$REMOTE_SERVER_IP "docker login -u <username> -p <password>"
                    """
                }
            }
        }
    }
}
```

### Real-World Examples

Recent breaches and vulnerabilities related to SSH credentials include:

1. **CVE-2021-20225**: A vulnerability in the OpenSSH server allowed attackers to bypass authentication checks.
2. **CVE-2021-3560**: A flaw in the OpenSSH client allowed attackers to inject arbitrary commands during the SSH handshake process.

These examples highlight the importance of securing SSH credentials and implementing robust security measures.

### Conclusion

Managing SSH credentials in Jenkins is a critical aspect of securing remote server access in CI/CD pipelines. By following best practices and using the SSH Agent plugin effectively, you can ensure that your Jenkins pipelines are both secure and efficient.

### Practice Labs

For hands-on practice with Jenkins and Docker deployment, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on web application security, including Jenkins and Docker.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including CI/CD pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Another popular lab for practicing web application security.

By engaging with these labs, you can gain practical experience in setting up and securing Jenkins pipelines for Docker deployment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/31-Jenkins Pipeline for Docker Deployment/00-Overview|Overview]] | [[02-Jenkins Pipeline for Docker Deployment|Jenkins Pipeline for Docker Deployment]]
