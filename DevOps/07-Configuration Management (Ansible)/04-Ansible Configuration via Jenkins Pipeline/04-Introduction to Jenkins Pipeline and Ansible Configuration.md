---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins Pipeline and Ansible Configuration

In the realm of DevOps, automation is key to maintaining efficiency and consistency across development and deployment processes. One of the most popular tools for continuous integration and delivery (CI/CD) is Jenkins. Jenkins provides a powerful framework for automating various tasks, including building, testing, and deploying applications. In this chapter, we will delve into how to use Jenkins pipelines to automate the configuration of EC2 instances using Ansible (likely a typo for Ansible).

### What is Jenkins?

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. It is widely used in the DevOps community to manage and automate the entire software development lifecycle.

### What is Ansible?

Ansible is an open-source IT automation tool that can help you automate your infrastructure provisioning, application deployment, and configuration management. It uses a simple language called YAML to define the desired state of your systems. Ansible is agentless, meaning it does not require any additional software to be installed on the target systems.

### Why Use Jenkins with Ansible?

Combining Jenkins and Ansible allows you to leverage the strengths of both tools. Jenkins can orchestrate the entire CI/CD process, while Ansible can handle the configuration management and provisioning of your infrastructure. This combination ensures that your infrastructure is consistently configured and deployed.

### Setting Up Jenkins Pipeline

To set up a Jenkins pipeline that triggers an Ansible playbook, we need to follow several steps:

1. **Install Required Plugins**: Jenkins requires specific plugins to execute commands on remote servers. One such plugin is the SSH Pipeline Steps plugin.
2. **Configure Jenkins Job**: Set up a Jenkins job that includes a pipeline script to execute the Ansible playbook.
3. **Execute Ansible Playbook**: Use the SSH Pipeline Steps plugin to execute the Ansible playbook on a remote server.

### Installing the SSH Pipeline Steps Plugin

The SSH Pipeline Steps plugin allows Jenkins to execute shell commands on remote servers. To install this plugin:

1. Log in to your Jenkins instance as an administrator.
2. Navigate to `Manage Jenkins` > `Manage Plugins`.
3. Click on the `Available` tab and search for `SSH Pipeline Steps`.
4. Check the box next to `SSH Pipeline Steps` and click `Install without restart`.

Once the plugin is installed, you can start configuring your Jenkins job to use it.

### Configuring Jenkins Job

Let's walk through the steps to configure a Jenkins job that executes an Ansible playbook on a remote server.

#### Step 1: Create a New Jenkins Job

1. Log in to your Jenkins instance.
2. Click on `New Item` to create a new job.
3. Enter a name for your job and select `Pipeline` as the job type.
4. Click `OK` to proceed.

#### Step 2: Define the Pipeline Script

In the pipeline script, we will use the SSH Pipeline Steps plugin to execute the Ansible playbook. Below is an example of how to do this:

```groovy
pipeline {
    agent any

    stages {
        stage('Configure EC2 Instances') {
            steps {
                sshPublisher(
                    publishers: [
                        sshPublisherConfig(
                            configName: 'remote-server',
                            transfers: [
                                sshTransfer(
                                    sourceFiles: 'playbook.yml',
                                    removePrefix: '',
                                    remoteDirectory: '/tmp'
                                )
                            ],
                            usePromotionTimestamp: false,
                            useWorkspaceInPromotion: false,
                            verbose: true
                        )
                    ]
                )

                sshScript(
                    remote: 'remote-server',
                    script: '''
                        ansible-playbook /tmp/playbook.yml
                    '''
                )
            }
        }
    }
}
```

### Explanation of the Pipeline Script

- **sshPublisher**: This step uploads the Ansible playbook (`playbook.yml`) to the remote server.
  - `configName`: The name of the SSH configuration defined in Jenkins.
  - `transfers`: Specifies the file to transfer and the destination directory on the remote server.
- **sshScript**: This step executes the Ansible playbook on the remote server.
  - `remote`: The name of the SSH configuration defined in Jenkins.
  - `script`: The shell command to execute on the remote server.

### SSH Configuration in Jenkins

Before running the pipeline, you need to configure the SSH settings in Jenkins:

1. Navigate to `Manage Jenkins` > `Configure System`.
2. Scroll down to the `Global Properties` section.
3. Add a new SSH configuration by clicking `Add` next to `SSH Remote Hosts`.
4. Enter a name for the configuration (e.g., `remote-server`).
5. Provide the hostname or IP address of the remote server.
6. Specify the username and private key for authentication.

### Example Ansible Playbook

Here is an example of an Ansible playbook that configures an EC2 instance:

```yaml
---
- name: Configure EC2 Instance
  hosts: all
  become: yes
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present

    - name: Ensure Apache is running
      service:
        name: apache2
        state: started
        enabled: yes
```

This playbook installs and starts the Apache web server on the remote server.

### Full Example with Raw HTTP Messages

When interacting with Jenkins, you might need to send HTTP requests to trigger builds or retrieve build information. Below is an example of a full HTTP request and response:

#### HTTP Request

```http
POST /job/your-job-name/build HTTP/1.1
Host: jenkins.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic YWRtaW46cGFzc3dvcmQ=

token=your-token
```

#### HTTP Response

```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Jenkins
X-Jenkins: 2.375.3
X-Jenkins-Session: 1234567890abcdef
Location: http://jenkins.example.com/job/your-job-name/1/
Content-Length: 0
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Incorrect SSH Configuration

**Issue**: If the SSH configuration is incorrect, Jenkins will fail to connect to the remote server.

**Prevention**:
- Double-check the SSH configuration details (hostname, username, private key).
- Test the SSH connection manually before configuring it in Jenkins.

#### Pitfall 2: Missing Permissions

**Issue**: The user running the Ansible playbook might lack necessary permissions to perform certain tasks.

**Prevention**:
- Ensure the user has the required permissions.
- Use `become: yes` in the Ansible playbook to escalate privileges.

#### Pitfall 3: Network Issues

**Issue**: Network issues can prevent Jenkins from connecting to the remote server.

**Prevention**:
- Verify network connectivity between Jenkins and the remote server.
- Check firewall rules and ensure they allow traffic between the two systems.

### How to Prevent / Defend

#### Detection

- Monitor Jenkins logs for errors related to SSH connections or Ansible playbook execution.
- Use monitoring tools to track the status of Jenkins jobs and Ansible playbooks.

#### Prevention

- Secure the Jenkins environment by following best practices for securing Jenkins installations.
- Use strong authentication methods (e.g., SSH keys) instead of passwords.
- Regularly update Jenkins and its plugins to protect against vulnerabilities.

#### Secure Coding Fixes

Below is an example of a vulnerable Jenkins pipeline script and its secure counterpart:

**Vulnerable Script**

```groovy
pipeline {
    agent any

    stages {
        stage('Configure EC2 Instances') {
            steps {
                sshScript(
                    remote: 'remote-server',
                    script: '''
                        ansible-playbook /tmp/playbook.yml
                    '''
                )
            }
        }
    }
}
```

**Secure Script**

```groovy
pipeline {
    agent any

    stages {
        stage('Configure EC2 Instances') {
            steps {
                sshPublisher(
                    publishers: [
                        sshPublisherConfig(
                            configName: 'remote-server',
                            transfers: [
                                sshTransfer(
                                    sourceFiles: 'playbook.yml',
                                    removePrefix: '',
                                    remoteDirectory: '/tmp'
                                )
                            ],
                            usePromotionTimestamp: false,
                            useWorkspaceInPromotion: false,
                            verbose: true
                        )
                    ]
                )

                sshScript(
                    remote: 'remote-server',
                    script: '''
                        ansible-playbook /tmp/playbook.yml
                    '''
                )
            }
        }
    }
}
```

### Real-World Examples and Recent Breaches

#### Example 1: CVE-2021-21234

**Description**: A vulnerability in Jenkins allowed attackers to execute arbitrary code on the Jenkins server.

**Impact**: Attackers could gain unauthorized access to the Jenkins server and potentially compromise the entire infrastructure.

**Mitigation**: Ensure Jenkins is updated to the latest version and apply security patches regularly.

#### Example 2: Jenkins Credentials Leaks

**Description**: Misconfigured Jenkins instances exposed sensitive credentials, leading to unauthorized access.

**Impact**: Attackers could use the leaked credentials to gain access to other systems and services.

**Mitigation**: Use strong authentication methods and regularly audit Jenkins configurations to identify and fix misconfigurations.

### Hands-On Labs

For practical experience with Jenkins and Ansible, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

### Conclusion

In this chapter, we covered how to use Jenkins pipelines to automate the configuration of EC2 instances using Ansible. We discussed the installation and configuration of the SSH Pipeline Steps plugin, provided a detailed example of a Jenkins pipeline script, and highlighted common pitfalls and how to prevent them. By following these guidelines, you can effectively automate your infrastructure provisioning and deployment processes.

---
<!-- nav -->
[[03-Introduction to Ansible and Jenkins Integration|Introduction to Ansible and Jenkins Integration]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/04-Ansible Configuration via Jenkins Pipeline/00-Overview|Overview]] | [[05-Introduction to Jenkins Pipeline and Ansible Integration|Introduction to Jenkins Pipeline and Ansible Integration]]
