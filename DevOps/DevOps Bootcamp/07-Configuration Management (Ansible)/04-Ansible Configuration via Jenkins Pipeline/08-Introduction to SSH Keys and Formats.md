---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to SSH Keys and Formats

In the context of DevOps and continuous integration/continuous deployment (CI/CD) pipelines, managing secure connections between servers and tools is crucial. One of the most common methods for establishing secure connections is through Secure Shell (SSH) keys. SSH keys provide a way to authenticate users and systems without requiring passwords, making them ideal for automated processes like those used in Jenkins pipelines.

### What Are SSH Keys?

SSH keys consist of two parts: a private key and a public key. The private key is kept secret and is used to encrypt data, while the public key is shared and used to decrypt data. In the context of Jenkins, SSH keys are often used to establish secure connections between Jenkins and remote servers, allowing Jenkins to perform tasks such as copying files or executing commands.

### SSH Key Formats

SSH keys can exist in different formats, and understanding these formats is important for ensuring compatibility with various tools and systems. Two common formats are:

1. **OpenSSH Format**: This is the default format used by OpenSSH, the most widely used SSH implementation. It is compatible with most modern systems and tools.
2. **Classic OpenSSH Format**: This is an older format that may be required by certain legacy systems or tools.

#### Converting SSH Key Formats

Sometimes, you may need to convert an SSH key from one format to another. For example, you might have a private key in the new OpenSSH format but need it in the classic OpenSSH format to work with Jenkins. This conversion can be done using tools like `ssh-keygen`.

```bash
ssh-keygen -p -m PEM -f /path/to/private_key
```

This command converts the private key to the classic OpenSSH format. The `-m PEM` option specifies the format, and `-f` specifies the path to the private key file.

### Example: Converting SSH Key Formats

Let's walk through an example of converting an SSH key from the new OpenSSH format to the classic OpenSSH format.

1. **Original Private Key**:
    ```plaintext
    -----BEGIN OPENSSH PRIVATE KEY-----
    ...
    -----END OPENSSH PRIVATE KEY-----
    ```

2. **Converted Private Key**:
    ```plaintext
    -----BEGIN RSA PRIVATE KEY-----
    ...
    -----END RSA PRIVATE KEY-----
    ```

The original private key starts with `-----BEGIN OPENSSH PRIVATE KEY-----`, while the converted private key starts with `-----BEGIN RSA PRIVATE KEY-----`. This conversion ensures that the key is compatible with Jenkins and other tools that require the classic format.

### Why Convert SSH Key Formats?

Converting SSH key formats is necessary when working with tools or systems that require specific key formats. For instance, Jenkins may require the classic OpenSSH format for its SSH agent plugin to function correctly. Without proper conversion, you may encounter errors or issues when trying to establish secure connections.

### Real-World Example: CVE-2021-20225

A real-world example of the importance of proper SSH key management is the CVE-2021-20225 vulnerability in GitLab. This vulnerability allowed attackers to bypass authentication checks by manipulating SSH keys. Proper key management and format conversion can help mitigate such vulnerabilities.

### How to Prevent / Defend

To prevent issues related to SSH key formats and ensure secure connections:

1. **Use Strong Key Formats**: Always use strong key formats and ensure they are compatible with the tools you are using.
2. **Regularly Update Keys**: Regularly update and rotate SSH keys to minimize the risk of unauthorized access.
3. **Secure Key Storage**: Store SSH keys securely, ideally in a secure key management system like HashiCorp Vault or AWS Secrets Manager.
4. **Audit Key Usage**: Regularly audit the usage of SSH keys to ensure they are being used appropriately and not exposed to unauthorized parties.

### Secure Code Fix

Here is an example of how to securely manage SSH keys in a Jenkins pipeline:

#### Vulnerable Code
```groovy
pipeline {
    agent any
    stages {
        stage('Copy Files') {
            steps {
                sshagent(credentials: ['my-ssh-key']) {
                    sh 'scp /path/to/file user@remote:/path/to/destination'
                }
            }
        }
    }
}
```

#### Fixed Code
```groovy
pipeline {
    agent any
    environment {
        SSH_KEY = credentials('my-ssh-key')
    }
    stages {
        stage('Copy Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh 'scp /path/to/file user@remote:/path/to/destination'
                }
            }
        }
    }
}
```

In the fixed code, the SSH key is stored securely in an environment variable, reducing the risk of exposure.

---
<!-- nav -->
[[07-Introduction to Jenkins Pipeline and SSH Agent Plugin|Introduction to Jenkins Pipeline and SSH Agent Plugin]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/04-Ansible Configuration via Jenkins Pipeline/00-Overview|Overview]] | [[09-Ansible Configuration via Jenkins Pipeline|Ansible Configuration via Jenkins Pipeline]]
