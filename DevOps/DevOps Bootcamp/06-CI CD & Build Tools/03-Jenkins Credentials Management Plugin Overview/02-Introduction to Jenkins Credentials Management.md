---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins Credentials Management

Jenkins is a widely-used open-source automation server that provides extensive support for continuous integration and continuous delivery (CI/CD) pipelines. One of the critical aspects of managing Jenkins effectively is handling sensitive information securely. This includes passwords, API keys, SSH keys, and other credentials required for various tasks within the CI/CD pipeline. The Jenkins Credentials Management plugin is designed to help manage these credentials securely and efficiently.

### What is the Jenkins Credentials Management Plugin?

The Jenkins Credentials Management plugin allows you to store and manage sensitive data such as passwords, SSH keys, and other credentials in a secure manner. These credentials can then be used in Jenkins jobs and pipelines without exposing them in plain text. The plugin provides a centralized repository for credentials and ensures that they are encrypted and protected.

#### Why Use Credentials Management?

Using the Credentials Management plugin offers several benefits:

1. **Security**: Credentials are stored securely and encrypted, reducing the risk of exposure.
2. **Organization**: Credentials can be organized and managed in a structured manner, making it easier to find and use them.
3. **Access Control**: You can control which users or projects have access to specific credentials, ensuring that sensitive information is not accessible to unauthorized parties.
4. **Reusability**: Credentials can be reused across multiple jobs and pipelines without needing to duplicate them.

### How Credentials Management Works

The Credentials Management plugin operates by storing credentials in a secure manner and providing mechanisms to access them within Jenkins jobs and pipelines. Here’s a high-level overview of how it works:

1. **Credential Storage**: Credentials are stored in Jenkins using encryption. They can be stored globally or scoped to specific projects.
2. **Credential Usage**: Credentials can be referenced in Jenkins jobs and pipelines using environment variables or other mechanisms provided by the plugin.
3. **Access Control**: Access to credentials can be controlled based on user roles and project scopes.

#### Credential Types

The Credentials Management plugin supports various types of credentials, including:

- **Username and Password**: Used for basic authentication.
- **SSH Username with Private Key**: Used for SSH connections.
- **Certificate**: Used for SSL/TLS certificates.
- **API Token**: Used for API authentication.
- **Username with Password**: Similar to username and password but with additional options.

### Organizing Credentials

One of the key features of the Credentials Management plugin is the ability to organize credentials in a hierarchical manner. This allows you to group related credentials together and control access at different levels.

#### Global vs. Project-Specific Credentials

Credentials can be stored either globally or scoped to specific projects. Global credentials are accessible to all projects, while project-specific credentials are only visible to the projects they are associated with.

```mermaid
flowchart LR
    A[Global Credentials] --> B[Project A]
    A --> C[Project B]
    D[Project-Specific Credentials] --> E[Project A]
    D --> F[Project B]
```

### Example: Managing Credentials in Jenkins

Let’s walk through an example of how to manage credentials in Jenkins using the Credentials Management plugin.

#### Step 1: Adding Credentials

To add a new credential, navigate to the Jenkins dashboard and go to `Manage Jenkins` > `Manage Credentials`. From there, select the domain where you want to add the credential (e.g., `System`, `Global`, or a specific project).

For this example, let’s add a username and password credential:

1. Click on `Add Credentials`.
2. Select the type of credential you want to add (e.g., `Username with password`).
3. Enter the username and password.
4. Optionally, provide a description and ID for the credential.
5. Click `OK` to save the credential.

Here’s an example of adding a username and password credential:

```mermaid
sequenceDiagram
    participant User
    participant Jenkins
    User->>Jenkins: Navigate to Manage Credentials
    Jenkins-->>User: Display Add Credentials form
    User->>Jenkins: Fill out form with username and password
    Jenkins-->>User: Save credential
```

#### Step 2: Using Credentials in a Pipeline

Once the credential is added, you can use it in a Jenkins pipeline. Here’s an example of a pipeline that uses a username and password credential:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                script {
                    def credentials = credentials('my-credentials-id')
                    sh """
                        git clone https://${credentials.username}:${credentials.password}@github.com/my-repo.git
                    """
                }
            }
        }
    }
}
```

In this example, `my-credentials-id` is the ID of the credential you added earlier. The `credentials` function retrieves the credential, and the `sh` step uses it to clone a Git repository.

### Access Control and Scoping

Access control is a crucial aspect of managing credentials securely. The Credentials Management plugin allows you to control which users or projects have access to specific credentials.

#### Scoping Credentials to Projects

When adding a credential, you can specify whether it should be global or scoped to a specific project. This ensures that credentials are only visible to the projects that need them.

```mermaid
flowchart LR
    A[Global Credentials] --> B[Project A]
    A --> C[Project B]
    D[Project-Specific Credentials] --> E[Project A]
    D --> F[Project B]
```

#### Example: Creating Project-Specific Credentials

To create a project-specific credential, follow these steps:

1. Navigate to the project where you want to add the credential.
2. Go to `Configure` and scroll down to the `Credentials` section.
3. Click on `Add` to add a new credential.
4. Select the type of credential and fill out the details.
5. Click `Save` to add the credential.

Here’s an example of creating a project-specific SSH key credential:

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sshagent(credentials: ['my-ssh-key']) {
                    sh """
                        ssh user@server 'cd /path/to/project && git pull'
                    """
                }
            }
        }
    }
}
```

In this example, `my-ssh-key` is the ID of the SSH key credential that was added to the project.

### Real-World Examples and Recent Breaches

Recent breaches involving Jenkins and credentials management highlight the importance of securing sensitive information. For example, in 2021, a vulnerability in Jenkins (CVE-2021-21180) allowed attackers to bypass authentication and gain unauthorized access to Jenkins instances. This vulnerability could have been exploited to steal credentials stored in Jenkins.

To prevent such vulnerabilities, it is essential to keep Jenkins and its plugins up to date, use strong access controls, and regularly audit credentials.

### How to Prevent / Defend

#### Detection

To detect potential issues with credentials management, you can:

1. **Audit Logs**: Regularly review Jenkins audit logs to identify any unauthorized access attempts.
2. **Monitoring**: Set up monitoring to alert you if credentials are accessed outside of expected times or locations.
3. **Security Scanning**: Use security scanning tools to identify vulnerabilities in Jenkins configurations.

#### Prevention

To prevent unauthorized access to credentials, you can:

1. **Keep Jenkins Updated**: Ensure that Jenkins and all plugins are up to date with the latest security patches.
2. **Use Strong Access Controls**: Configure access controls to limit who can view and use credentials.
3. **Regular Audits**: Perform regular audits of credentials to ensure they are being used appropriately.

#### Secure Coding Fixes

Here’s an example of a vulnerable pipeline and its secure counterpart:

**Vulnerable Pipeline:**

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                sh """
                    git clone https://username:password@github.com/my-repo.git
                """
            }
            }
        }
    }
}
```

**Secure Pipeline:**

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                script {
                    def credentials = credentials('my-credentials-id')
                    sh """
                        git clone https://${credentials.username}:${credentials.password}@github.com/my-repo.git
                    """
                }
            }
        }
    }
}
```

In the secure pipeline, the credentials are retrieved using the `credentials` function, which ensures that the credentials are not exposed in plain text.

### Configuration Hardening

To further harden your Jenkins configuration, you can:

1. **Enable CSRF Protection**: Ensure that Cross-Site Request Forgery (CSRF) protection is enabled in Jenkins.
2. **Limit API Access**: Restrict access to the Jenkins API to only trusted sources.
3. **Use HTTPS**: Ensure that all communication with Jenkins is encrypted using HTTPS.

### Hands-On Labs

To practice managing credentials in Jenkins, you can use the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers exercises on managing credentials securely in Jenkins.
- **OWASP Juice Shop**: Provides a vulnerable application that you can use to practice securing credentials.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios where you can practice securing credentials in a real-world context.

By following these practices and using the provided resources, you can effectively manage credentials in Jenkins and ensure the security of your CI/CD pipelines.

---
<!-- nav -->
[[01-Introduction to Jenkins Credentials Management Plugin|Introduction to Jenkins Credentials Management Plugin]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/03-Jenkins Credentials Management Plugin Overview/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/03-Jenkins Credentials Management Plugin Overview/03-Jenkins Credentials Management Plugin Overview|Jenkins Credentials Management Plugin Overview]]
