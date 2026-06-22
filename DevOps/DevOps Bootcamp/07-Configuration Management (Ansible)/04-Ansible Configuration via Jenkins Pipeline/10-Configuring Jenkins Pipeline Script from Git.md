---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Configuring Jenkins Pipeline Script from Git

In this section, we will delve into configuring a Jenkins pipeline script from a Git repository. This process involves setting up a Jenkins job to pull a pipeline script from a Git repository, execute it, and manage the necessary configurations and credentials securely.

### Setting Up the Jenkins Job

To begin, we need to create a new Jenkins job that will pull the pipeline script from a Git repository. Here’s a step-by-step guide:

1. **Create a New Jenkins Job**:
    - Navigate to the Jenkins dashboard.
    - Click on "New Item".
    - Enter a name for your job and select "Pipeline" as the job type.
    - Click "OK".

2. **Configure the Pipeline Script Source**:
    - In the job configuration page, scroll down to the "Pipeline" section.
    - Select "Pipeline script from SCM".
    - Choose "Git" as the SCM.
    - Enter the URL of your Git repository.
    - Provide the credentials for accessing the Git repository.
    - Specify the branch name from which the pipeline script should be pulled.

Here is an example of how the Jenkinsfile might look:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean install'
            }
        }
        stage('Deploy') {
            steps {
                sh 'ansible-playbook deploy.yml'
            }
        }
    }
}
```

### Example Jenkinsfile Breakdown

- **agent any**: Specifies that the pipeline can run on any available agent.
- **stages**: Defines the different stages of the pipeline.
- **stage('Build')**: Represents the build stage where the `mvn clean install` command is executed.
- **stage('Deploy')**: Represents the deployment stage where the Ansible playbook `deploy.yml` is executed.

### SSH Key Management

The Jenkins job needs to manage SSH keys securely to interact with remote servers. This involves copying the SSH key to the Jenkins server and configuring the Ansible playbook to use it.

#### Copying SSH Keys to the Jenkins Server

1. **SSH into the Jenkins Server**:
    - Use the following command to SSH into the Jenkins server:
      ```sh
      ssh root@jenkins-server-ip
      ```

2. **Copy SSH Keys**:
    - Copy the SSH key to the Jenkins server:
      ```sh
      cp /path/to/id_rsa ~/.ssh/
      ```

3. **Set Permissions**:
    - Ensure the SSH key has the correct permissions:
      ```sh
      chmod 600 ~/.ssh/id_rsa
      ```

### Ansible Configuration

The Ansible configuration file (`ansible.cfg`) specifies the location of the SSH key and other settings.

#### Example ansible.cfg

```ini
[defaults]
inventory = /path/to/inventory
private_key_file = /root/.ssh/id_rsa
remote_user = ec2-user
```

### Inventory File

The inventory file lists the remote servers and their details.

#### Example inventory

```ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
```

### Playbook Configuration

The playbook (`deploy.yml`) defines the tasks to be executed on the remote servers.

#### Example deploy.yml

```yaml
---
- hosts: webservers
  become: yes
  tasks:
    - name: Install Apache
      yum:
        name: httpd
        state: present
    - name: Start Apache
      service:
        name: httpd
        state: started
        enabled: yes
```

### Jenkins Pipeline Execution

Once the Jenkins job is configured, you can trigger a build. The pipeline will execute the steps defined in the Jenkinsfile, including building the Maven project and deploying using Ansible.

### Security Considerations

One critical aspect of managing Jenkins pipelines is ensuring that sensitive information, such as SSH keys, is handled securely. The transcript mentions a security issue related to exposing the private key file.

#### Vulnerability Explanation

The warning indicates that the private key file is being exposed due to insecure handling within the Jenkins pipeline script. Specifically, the Groovy string interpolation mechanism is leaking the key content.

#### Vulnerable Code Example

```groovy
pipeline {
    agent any
    environment {
        SSH_KEY = readFile('/root/.ssh/id_rsa')
    }
    stages {
        stage('Build') {
            steps {
                sh 'echo ${SSH_KEY}'
            }
        }
    }
}
```

#### Secure Code Example

To prevent this exposure, the SSH key should be managed securely using Jenkins credentials and environment variables.

```groovy
pipeline {
    agent any
    environment {
        SSH_KEY = credentials('ssh-key-id')
    }
    stages {
        stage('Build') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'ssh-key-id', keyFileVariable: 'SSH_KEY_FILE')]) {
                    sh 'echo $SSH_KEY_FILE'
                }
            }
        }
    }
}
```

### How to Prevent / Defend

#### Detection

- **Jenkins Plugin**: Use plugins like the "Credentials Binding Plugin" to detect and mitigate insecure handling of credentials.
- **Logging**: Monitor Jenkins logs for any suspicious activities related to credential handling.

#### Prevention

- **Use Jenkins Credentials**: Store sensitive information like SSH keys in Jenkins credentials store.
- **Environment Variables**: Use environment variables to pass credentials securely.
- **Secure String Interpolation**: Avoid direct string interpolation of sensitive data in scripts.

#### Secure-Coding Fixes

- **Before Fix**:
  ```groovy
  pipeline {
      agent any
      environment {
          SSH_KEY = readFile('/root/.ssh/id_rsa')
      }
      stages {
          stage('Build') {
              steps {
                  sh 'echo ${SSH_KEY}'
              }
          }
      }
  }
  ```

- **After Fix**:
  ```groovy
  pipeline {
      agent any
      environment {
          SSH_KEY = credentials('ssh-key-id')
      }
      stages {
          stage('Build') {
              steps {
                  withCredentials([sshUserPrivateKey(credentialsId: 'ssh-key-id', keyFileVariable: 'SSH_KEY_FILE')]) {
                      sh 'echo $SSH_KEY_FILE'
                  }
              }
          }
      }
  }
  ```

### Real-World Examples

#### Recent Breaches

- **CVE-2021-25282**: A vulnerability in Jenkins allowed unauthorized access to sensitive information due to insecure handling of credentials.
- **CVE-2022-3715**: Another Jenkins vulnerability exposed sensitive data through insecure logging mechanisms.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on securing Jenkins pipelines.
- **OWASP Juice Shop**: Provides scenarios for practicing secure Jenkins pipeline configurations.
- **DVWA**: Useful for understanding and practicing secure coding practices in Jenkins pipelines.

By following these guidelines and best practices, you can ensure that your Jenkins pipelines are both functional and secure.

---
<!-- nav -->
[[09-Ansible Configuration via Jenkins Pipeline|Ansible Configuration via Jenkins Pipeline]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/04-Ansible Configuration via Jenkins Pipeline/00-Overview|Overview]] | [[11-Configuring Jenkins Pipeline with SSH Agent Plugin|Configuring Jenkins Pipeline with SSH Agent Plugin]]
