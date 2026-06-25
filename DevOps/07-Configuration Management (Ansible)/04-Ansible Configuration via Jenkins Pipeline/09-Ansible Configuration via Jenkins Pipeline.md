---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Ansible Configuration via Jenkins Pipeline

### Introduction to Ansible and Jenkins Pipeline

Ansible is a configuration management tool similar to Ansible but designed specifically for managing infrastructure in a more dynamic and flexible manner. Jenkins Pipeline, on the other hand, is a powerful tool for defining and executing complex software delivery pipelines as code. Combining these two tools allows for automated and consistent deployment and management of infrastructure.

In this section, we will explore how to configure Ansible servers within a Jenkins Pipeline, focusing particularly on the challenges and solutions related to SSH keys.

### SSH Keys and Their Importance

SSH (Secure Shell) keys are used to authenticate users to remote systems securely. They consist of a public key and a private key. The public key is stored on the remote system, while the private key remains on the local machine. When a user attempts to connect to a remote system, the private key is used to prove identity.

#### Public and Private Keys

- **Public Key**: Stored on the remote system. It is used to verify the authenticity of the private key.
- **Private Key**: Kept securely on the local machine. It is used to sign data and prove identity.

#### SSH Key Generation

SSH keys can be generated using the `ssh-keygen` command:

```bash
ssh-keygen -t rsa -b 4096
```

This command generates an RSA key pair with a bit length of 4096.

### SSH Key Formats and Compatibility Issues

Recent versions of OpenSSH generate keys in a new format that starts with "Begin OpenSSH Private Key". However, older tools like Jenkins may not support this format, leading to compatibility issues.

#### New OpenSSH Private Key Format

The new format looks like this:

```plaintext
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

#### Old PEM Format

The older format, supported by most tools, looks like this:

```plaintext
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
```

### Configuring SSH Keys in Jenkins Pipeline

To configure Ansible servers within a Jenkins Pipeline, you need to ensure that the SSH keys are correctly set up and compatible with Jenkins.

#### Setting Up SSH Keys in Jenkins

1. **Add SSH Key to Jenkins**:
   - Navigate to `Manage Jenkins` > `Manage Credentials`.
   - Click on `Global credentials (unrestricted)` and then `Add Credentials`.
   - Select `SSH Username with private key`.
   - Enter the username (e.g., `root`).
   - Upload the private key file or paste the key content.

2. **Pipeline Configuration**:
   - Use the `withCredentials` step to access the SSH key within the pipeline.

```groovy
pipeline {
    agent any
    environment {
        SSH_KEY = credentials('jenkins-ssh-key')
    }
    stages {
        stage('Configure Ansible') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'jenkins-ssh-key', keyFileVariable: 'SSH_KEY_FILE', usernameVariable: 'SSH_USER')]) {
                        sh """
                            ssh -i ${SSH_KEY_FILE} ${SSH_USER}@ansible-server.example.com 'command'
                        """
                    }
                }
            }
        }
    }
}
```

### Handling SSH Key Format Compatibility

If you encounter issues due to the new OpenSSH private key format, you can convert the key to the older PEM format using the `ssh-keygen` command.

#### Converting SSH Keys

Use the following command to convert the key:

```bash
ssh-keygen -p -f ~/.ssh/id_rsa
```

This command prompts for the old passphrase and then converts the key to the older format.

#### Example Conversion

Assume you have a private key file named `id_rsa_new` in the new format. Convert it using:

```bash
ssh-keygen -p -f id_rsa_new
```

After conversion, the key should look like this:

```plaintext
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
```

### Real-World Examples and Breaches

#### Recent CVEs and Breaches

- **CVE-2021-21547**: A vulnerability in Jenkins allowed unauthorized access to credentials stored in the Jenkins master. Ensure that Jenkins is updated to the latest version and that credentials are properly secured.
- **DigitalOcean Breach**: In 2021, DigitalOcean experienced a breach that exposed customer metadata. Ensure that SSH keys are rotated regularly and that access controls are strictly enforced.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Regularly review audit logs for unauthorized access attempts.
- **Monitoring Tools**: Use tools like Splunk or ELK Stack to monitor SSH access patterns.

#### Prevention

- **Key Rotation**: Rotate SSH keys regularly to minimize exposure.
- **Access Controls**: Implement strict access controls and limit SSH access to necessary personnel.

#### Secure Coding Fixes

##### Vulnerable Code

```groovy
pipeline {
    agent any
    environment {
        SSH_KEY = credentials('jenkins-ssh-key')
    }
    stages {
        stage('Configure Ansible') {
            steps {
                script {
                    sh """
                        ssh -i ~/.ssh/id_rsa root@ansible-server.example.com 'command'
                    """
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
    environment {
        SSH_KEY = credentials('jenkins-ssh-key')
    }
    stages {
        stage('Configure Ansible') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'jenkins-ssh-key', keyFileVariable: 'SSH_KEY_FILE', usernameVariable: 'SSH_USER')]) {
                        sh """
                            ssh -i ${SSH_KEY_FILE} ${SSH_USER}@ansible-server.example.com 'command'
                        """
                    }
                }
            }
        }
    }
}
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive training on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide practical experience in configuring and securing SSH keys within a Jenkins Pipeline.

### Conclusion

Configuring Ansible servers within a Jenkins Pipeline requires careful handling of SSH keys to ensure compatibility and security. By understanding the different SSH key formats and using the appropriate tools and techniques, you can effectively manage and secure your infrastructure. Regular audits, key rotations, and strict access controls are essential to maintaining a secure environment.

---
<!-- nav -->
[[08-Introduction to SSH Keys and Formats|Introduction to SSH Keys and Formats]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/04-Ansible Configuration via Jenkins Pipeline/00-Overview|Overview]] | [[10-Configuring Jenkins Pipeline Script from Git|Configuring Jenkins Pipeline Script from Git]]
