---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Enabling Configuration Management via Jenkins Pipeline

### Background Theory

Configuration management is a critical aspect of DevOps practices, ensuring consistency and reliability across environments. Tools like Ansible play a pivotal role in automating the provisioning and configuration of infrastructure. Jenkins, a widely-used continuous integration and delivery (CI/CD) tool, can be integrated with Ansible to automate the deployment and configuration of applications and infrastructure.

In this context, we'll explore how to enable configuration management via a Jenkins pipeline, specifically focusing on copying necessary files to a remote server and setting up SSH keys for secure access.

### Copying Files to Remote Server

The process of copying files to a remote server is fundamental in many DevOps workflows. This can involve copying configuration files, scripts, or even entire application packages. In the given scenario, we are copying Docker Compose files to a remote server to execute `docker-compose up` commands.

#### Steps to Copy Files

1. **Prepare the Files**: Ensure the files you want to copy are ready on your local machine.
2. **Set Up SSH Access**: Establish SSH access to the remote server.
3. **Use SCP or rsync**: Utilize tools like `scp` or `rsync` to transfer files securely.

```bash
# Example using scp
scp /path/to/local/file user@remote-server:/path/to/destination

# Example using rsync
rsync -avz /path/to/local/file user@remote-server:/path/to/destination
```

### SSH Private Key for EC2 Instances

For AWS EC2 instances, an SSH private key (PEM file) is required to establish secure connections. This key is crucial for both accessing the instance and executing Ansible playbooks.

#### PEM File Format

The PEM file is in the OpenSSH format, which is a standard format for storing private keys. This format is widely supported by various SSH clients and servers.

```plaintext
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
```

### Storing PEM File in Jenkins

To use the PEM file within a Jenkins pipeline, it needs to be stored as a credential in Jenkins. This ensures that sensitive information is securely managed and not exposed in plain text.

#### Creating SSH Credentials in Jenkins

1. **Navigate to Credentials Management**:
   - Go to `Manage Jenkins` > `Manage Credentials`.
2. **Add New Credentials**:
   - Click on `Global credentials (unrestricted)` and then `Add Credentials`.
3. **Fill in the Details**:
   - Kind: `SSH Username with private key`
   - Scope: `Global`
   - ID: `EC2 server key`
   - Username: `ec2-user`
   - Private Key: Paste the contents of the PEM file.

```mermaid
sequenceDiagram
    participant User
    participant Jenkins
    participant EC2Instance
    User->>Jenkins: Create SSH Credential
    Jenkins->>EC2Instance: Connect using SSH
    EC2Instance-->>Jenkins: Confirm connection
```

### Using Credentials in Jenkins Pipeline

Once the PEM file is stored as a credential in Jenkins, it can be referenced in the Jenkins pipeline script.

#### Jenkins Pipeline Script

Below is an example of a Jenkins pipeline script that copies files to a remote server using the stored SSH credentials.

```groovy
pipeline {
    agent any
    environment {
        SSH_CREDENTIALS_ID = 'EC2 server key'
    }
    stages {
        stage('Copy Files') {
            steps {
                sshPublisher(
                    publishers: [
                        sshPublisherConfig(
                            configName: 'Remote Server',
                            transfers: [
                                sshTransfer(
                                    sourceFiles: '/path/to/local/files',
                                    removePrefix: '/path/to/local',
                                    remoteDirectory: '/path/to/remote',
                                    execCommand: 'chmod +x /path/to/remote/script.sh'
                                )
                            ],
                            usePromotionTimestamp: false,
                            useWorkspaceInPromotion: false,
                            cleanRemote: false,
                            failOnMissing: true,
                            continueOnError: false,
                            keepAllVersions: false,
                            verbose: true
                        )
                    ]
                )
            }
        }
    }
}
```

### Secure Handling of SSH Keys

Handling SSH keys securely is paramount to maintaining the integrity and confidentiality of your infrastructure. Here are some best practices:

1. **Limit Access**: Restrict access to the PEM file to only those who need it.
2. **Rotate Keys Regularly**: Periodically rotate SSH keys to minimize exposure.
3. **Use Strong Encryption**: Ensure that the PEM file is encrypted with strong encryption algorithms.
4. **Audit Usage**: Regularly audit the usage of SSH keys to detect any unauthorized access.

### Real-World Examples

#### Recent Breaches

One notable breach involving SSH keys occurred in 2021 when a misconfigured AWS S3 bucket exposed thousands of SSH keys. This incident highlights the importance of securing and managing SSH keys properly.

#### Secure Coding Practices

Here’s an example of how to securely handle SSH keys in a Jenkins pipeline:

```groovy
pipeline {
    agent any
    environment {
        SSH_CREDENTIALS_ID = 'EC2 server key'
    }
    stages {
        stage('Secure Copy') {
            steps {
                script {
                    def sshKey = credentials(SSH_CREDENTIALS_ID)
                    sh """
                        ssh -i ${sshKey.privateKey} ec2-user@remote-server 'mkdir -p /path/to/remote'
                        scp -i ${sshKey.privateKey} /path/to/local/file ec2-user@remote-server:/path/to/remote/
                    """
                }
            }
        }
    }
}
```

### How to Prevent / Defend

#### Detection

- **Monitor SSH Access**: Use tools like AWS CloudTrail to monitor SSH access attempts.
- **Audit Logs**: Regularly review logs for any suspicious activity related to SSH keys.

#### Prevention

- **Use IAM Policies**: Implement strict IAM policies to limit access to SSH keys.
- **Enable Multi-Factor Authentication (MFA)**: Require MFA for accessing systems that use SSH keys.

#### Secure-Coding Fixes

Compare the insecure and secure versions of handling SSH keys in a Jenkins pipeline:

**Insecure Version**

```groovy
pipeline {
    agent any
    environment {
        SSH_KEY_PATH = '/path/to/pem'
    }
    stages {
        stage('Copy Files') {
            steps {
                sh """
                    ssh -i ${SSH_KEY_PATH} ec2-user@remote-server 'mkdir -p /path/to/remote'
                    scp -i ${SSH_KEY_PATH} /path/to/local/file ec2-user@remote-server:/path/to/remote/
                """
            }
        }
    }
}
```

**Secure Version**

```groovy
pipeline {
    agent any
    environment {
        SSH_CREDENTIALS_ID = 'EC2 server key'
    }
    stages {
        stage('Secure Copy') {
            steps {
                script {
                    def sshKey = credentials(SSH_CREDENTIALS_ID)
                    sh """
                        ssh -i ${sshKey.privateKey} ec2-user@remote-server 'mkdir -p /path/to/remote'
                        scp -i ${sshKey.privateKey} /path/to/local/file ec2-user@remote-server:/path/to/remote/
                    """
                }
            }
        }
    }
}
```

### Hands-On Labs

For practical experience with Jenkins and Ansible, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security testing and CI/CD pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Useful for learning about web application vulnerabilities and integrating with CI/CD tools.

These labs provide a comprehensive environment to practice and understand the concepts discussed.

By thoroughly covering the background, mechanics, and practical aspects of enabling configuration management via Jenkins pipeline, this chapter aims to equip readers with the knowledge and skills needed to implement secure and efficient DevOps practices.

---
<!-- nav -->
[[11-Configuring Jenkins Pipeline with SSH Agent Plugin|Configuring Jenkins Pipeline with SSH Agent Plugin]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/04-Ansible Configuration via Jenkins Pipeline/00-Overview|Overview]] | [[13-Enabling Configuration via Jenkins Pipeline|Enabling Configuration via Jenkins Pipeline]]
