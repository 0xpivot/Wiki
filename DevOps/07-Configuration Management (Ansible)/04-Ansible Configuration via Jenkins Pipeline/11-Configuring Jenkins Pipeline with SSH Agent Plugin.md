---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Configuring Jenkins Pipeline with SSH Agent Plugin

Now that we have covered the basics of SSH keys and their formats, let's move on to configuring Jenkins pipelines using the SSH Agent plugin.

### What Is the SSH Agent Plugin?

The SSH Agent plugin in Jenkins allows you to use SSH keys within your Jenkins pipelines. It provides a convenient way to handle SSH keys securely and automate tasks that require SSH connections.

### Installing the SSH Agent Plugin

Before you can use the SSH Agent plugin, you need to install it in your Jenkins instance. You can do this by navigating to the Jenkins dashboard, selecting "Manage Jenkins," and then clicking "Manage Plugins." From there, search for "SSH Agent" and install it.

### Setting Up SSH Credentials in Jenkins

Once the plugin is installed, you need to set up the SSH credentials in Jenkins. This involves creating a new credential and associating it with your Jenkins job.

1. **Navigate to Credentials Management**:
    - Go to "Manage Jenkins" > "Manage Credentials."
    - Click on "Global credentials (unrestricted)" or "System."

2. **Create a New Credential**:
    - Click on "Add Credentials."
    - Select "SSH Username with private key" as the type.
    - Enter the username and paste the private key in the "Private Key" field.
    - Provide a description and click "OK."

### Using the SSH Agent Plugin in a Jenkins Pipeline

With the SSH credentials set up, you can now use the SSH Agent plugin in your Jenkins pipeline to perform tasks that require SSH connections.

#### Example Jenkinsfile

Here is an example of a Jenkinsfile that uses the SSH Agent plugin to copy files from Jenkins to a remote server:

```groovy
pipeline {
    agent any
    environment {
        SSH_CREDENTIALS_ID = 'my-ssh-credentials-id'
    }
    stages {
        stage('Copy Files') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS_ID]) {
                    sh 'scp /path/to/file user@remote:/path/to/destination'
                }
            }
        }
    }
}
```

### Explanation of the Jenkinsfile

1. **Agent**: Specifies the agent to run the pipeline on.
2. **Environment**: Defines an environment variable `SSH_CREDENTIALS_ID` that holds the ID of the SSH credentials.
3. **Stages**: Defines the stages of the pipeline.
4. **Stage 'Copy Files'**: Contains the steps to copy files using SSH.
5. **sshagent**: Uses the SSH Agent plugin to handle the SSH credentials.
6. **sh**: Executes the `scp` command to copy files.

### Full Raw HTTP Messages

While the example above does not involve HTTP messages, it is important to understand how HTTP messages are structured and how they relate to Jenkins pipelines. Here is an example of a full HTTP request and response for a Jenkins API call:

#### HTTP Request
```http
POST /job/my-job/build?token=my-token HTTP/1.1
Host: jenkins.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic YWRtaW46cGFzc3dvcmQ=

json={"parameter": [{"name": "SSH_CREDENTIALS_ID", "value": "my-ssh-credentials-id"}]}
```

#### HTTP Response
```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache-Coyote/1.1
Location: http://jenkins.example.com/job/my-job/1/
Content-Length: 0
```

### Mermaid Diagram: Jenkins Pipeline Flow

Here is a mermaid diagram illustrating the flow of a Jenkins pipeline that uses the SSH Agent plugin:

```mermaid
graph TD
    A[Start] --> B[Define Environment Variables]
    B --> C[Set Up SSH Credentials]
    C --> D[Run SSH Agent Step]
    D --> E[Execute SCP Command]
    E --> F[End]
```

### Common Pitfalls and Best Practices

When working with SSH keys and Jenkins pipelines, there are several common pitfalls to avoid:

1. **Incorrect Key Formats**: Ensure that the SSH keys are in the correct format for the tools you are using.
2. **Exposure of SSH Keys**: Avoid exposing SSH keys in plain text or in insecure locations.
3. **Misconfigured Credentials**: Ensure that the SSH credentials are correctly configured and associated with the Jenkins job.
4. **Insufficient Permissions**: Ensure that the user associated with the SSH key has sufficient permissions on the remote server.

### How to Prevent / Defend

To prevent issues related to SSH keys and Jenkins pipelines:

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

### Practice Labs

For hands-on practice with Jenkins pipelines and SSH keys, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web security, including some that involve Jenkins pipelines.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing, including scenarios involving Jenkins pipelines.
- **DVWA (Damn Vulnerable Web Application)**: Another vulnerable web application for practicing security testing, with scenarios involving Jenkins pipelines.

By following these guidelines and practices, you can ensure that your Jenkins pipelines are secure and efficient, leveraging the power of SSH keys and the SSH Agent plugin effectively.

---
<!-- nav -->
[[10-Configuring Jenkins Pipeline Script from Git|Configuring Jenkins Pipeline Script from Git]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/04-Ansible Configuration via Jenkins Pipeline/00-Overview|Overview]] | [[12-Enabling Configuration Management via Jenkins Pipeline|Enabling Configuration Management via Jenkins Pipeline]]
