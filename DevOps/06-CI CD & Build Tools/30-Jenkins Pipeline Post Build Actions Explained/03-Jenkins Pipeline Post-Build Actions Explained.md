---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Jenkins Pipeline Post-Build Actions Explained

In this section, we will delve deep into the intricacies of Jenkins pipelines, focusing specifically on post-build actions and conditional execution based on changes in the codebase. We will cover the concepts of environment variables, Groovy scripting, and how to effectively manage and utilize these features within Jenkins pipelines.

### Conditional Execution Based on Code Changes

One of the most common use cases for Jenkins pipelines is to execute certain steps only if there have been changes in the codebase. This is particularly useful in scenarios where you want to avoid unnecessary builds or deployments, thereby saving resources and time.

#### Example Scenario

Consider a scenario where you only want to build your application if there are code changes made in the project. You can achieve this by using a conditional statement in your Jenkinsfile.

```groovy
pipeline {
    agent any
    environment {
        CODE_CHANGES = false
    }
    stages {
        stage('Check for Code Changes') {
            steps {
                script {
                    // Check for code changes using a Groovy script
                    def changes = sh(script: 'git diff --name-only HEAD~1 HEAD', returnStdout: true).trim()
                    if (!changes.isEmpty()) {
                        env.CODE_CHANGES = true
                    }
                }
            }
        }
        stage('Build Application') {
            when {
                expression { env.CODE_CHANGES == true }
            }
            steps {
                echo 'Building the application...'
                // Add your build steps here
            }
        }
    }
}
```

### Explanation of the Code

1. **Pipeline Definition**: The `pipeline` block defines the entire pipeline structure.
2. **Agent**: The `agent any` directive specifies that the pipeline can run on any available agent.
3. **Environment Variables**: The `environment` block initializes an environment variable `CODE_CHANGES` to `false`.
4. **Stages**: The `stages` block contains a series of stages that define the workflow.
5. **Check for Code Changes**:
    - **Script Block**: The `script` block allows you to execute arbitrary Groovy code.
    - **Git Diff Command**: The `sh` step runs a shell command to check for changes between the last two commits (`HEAD~1` and `HEAD`). The `returnStdout: true` option captures the output of the command.
    - **Conditional Logic**: If the output of the `git diff` command is not empty, it means there are code changes, and the `CODE_CHANGES` variable is set to `true`.
6. **Build Application**:
    - **When Block**: The `when` block uses an expression to conditionally execute the stage. In this case, the stage will only run if `env.CODE_CHANGES` is `true`.
    - **Steps**: The `steps` block contains the actual build steps.

### Environment Variables in Jenkinsfile

Jenkins provides several environment variables out of the box that can be used within your Jenkinsfile. These variables provide valuable information about the current build context.

#### Common Environment Variables

- **`BRANCH_NAME`**: The name of the current branch.
- **`BUILD_NUMBER`**: The unique identifier for the current build.
- **`GIT_COMMIT`**: The commit hash of the current build.
- **`WORKSPACE`**: The directory where the workspace is located.

#### Accessing Environment Variables

To access these environment variables, you can simply reference them in your Jenkinsfile. For example:

```groovy
pipeline {
    agent any
    environment {
        BRANCH_NAME = "${env.BRANCH_NAME}"
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
    }
    stages {
        stage('Print Environment Variables') {
            steps {
                echo "Branch Name: ${env.BRANCH_NAME}"
                echo "Build Number: ${env.BUILD_NUMBER}"
            }
        }
    }
}
```

### Finding Available Environment Variables

To discover all the available environment variables provided by Jenkins, you can navigate to the following URL in your Jenkins instance:

```
http://<jenkins-url>/pipeline-syntax/globals
```

This page lists all the global variables available in Jenkins, along with their descriptions and usage examples.

### Real-World Examples and Recent CVEs

While Jenkins itself is generally secure, improper use of environment variables and conditional logic can lead to vulnerabilities. For example, if sensitive information is stored in environment variables and exposed through logs or build artifacts, it can be exploited.

#### Example Vulnerability

Consider a scenario where a developer mistakenly stores a secret key in an environment variable and then prints it in the console output:

```groovy
pipeline {
    agent any
    environment {
        SECRET_KEY = "my-secret-key"
    }
    stages {
        stage('Print Secret Key') {
            steps {
                echo "Secret Key: ${env.SECRET_KEY}"
            }
        }
    }
}
```

This can lead to exposure of sensitive information. To prevent such issues, ensure that sensitive data is never printed in the console output and is properly secured using Jenkins credentials management.

### How to Prevent / Defend

#### Secure Handling of Sensitive Data

1. **Use Jenkins Credentials Management**: Store sensitive data such as API keys, passwords, etc., using Jenkins credentials management.
2. **Mask Sensitive Data**: Use the `maskPasswords` plugin to mask sensitive data in the console output.
3. **Secure Environment Variables**: Ensure that sensitive environment variables are not exposed in logs or build artifacts.

#### Example of Secure Handling

```groovy
pipeline {
    agent any
    environment {
        SECRET_KEY = credentials('my-secret-key')
    }
    stages {
        stage('Print Secret Key') {
            steps {
                echo "Secret Key: ${env.SECRET_KEY}"
            }
        }
    }
}
```

### Conclusion

In this section, we explored how to conditionally execute Jenkins pipeline stages based on code changes and how to effectively use environment variables within Jenkinsfiles. We also discussed the importance of securing sensitive data and preventing potential vulnerabilities. By following these best practices, you can ensure that your Jenkins pipelines are both efficient and secure.

### Practice Labs

For hands-on practice with Jenkins pipelines, consider the following well-known labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including Jenkins pipeline configurations.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which includes Jenkins integration scenarios.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training, which can be integrated with Jenkins for automated testing and deployment.

These labs provide practical experience in setting up and managing Jenkins pipelines, ensuring that you can apply the concepts learned in this section effectively.

---
<!-- nav -->
[[02-Jenkins Pipeline Post Build Actions Explained|Jenkins Pipeline Post Build Actions Explained]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/30-Jenkins Pipeline Post Build Actions Explained/00-Overview|Overview]] | [[04-Jenkins Pipeline Post-Build Actions User Input in Deployment Phases|Jenkins Pipeline Post-Build Actions User Input in Deployment Phases]]
