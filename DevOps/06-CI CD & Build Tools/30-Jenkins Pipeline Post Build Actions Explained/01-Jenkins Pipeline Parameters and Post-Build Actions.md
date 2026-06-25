---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Jenkins Pipeline Parameters and Post-Build Actions

In this section, we will delve into the concept of Jenkins pipeline parameters and how they can be utilized effectively within the pipeline stages. We'll cover the various types of parameters available, their usage in conditional expressions, and how to implement them in a Jenkins pipeline. Additionally, we will discuss post-build actions and their importance in automating the build process.

### Understanding Jenkins Pipeline Parameters

Jenkins pipeline parameters allow you to pass dynamic values into your pipeline at runtime. This is particularly useful when you want to customize the behavior of your pipeline based on user input or external factors. There are several types of parameters available in Jenkins:

1. **String Parameter**: A simple string input.
2. **Text Parameter**: A multi-line text input.
3. **Boolean Parameter**: A yes/no or true/false input.
4. **Choice Parameter**: A list of predefined choices.
5. **File Parameter**: An uploaded file.

#### Choice Parameter

A choice parameter allows you to provide a list of predefined options that the user can select from. This is particularly useful when you want to limit the input to a specific set of values.

**Example:**

Let's say you want to define a choice parameter for selecting a version name. Here’s how you can define it in a Jenkins pipeline:

```groovy
pipeline {
    agent any
    parameters {
        choice(name: 'VERSION_NAME', choices: ['v1.0', 'v1.1', 'v1.2'], description: 'Select the version name')
    }
    stages {
        stage('Build') {
            steps {
                echo "Building version ${params.VERSION_NAME}"
            }
        }
    }
}
```

In this example, the `choice` parameter `VERSION_NAME` provides three options (`v1.0`, `v1.1`, `v1.2`). The selected value can be accessed using `${params.VERSION_NAME}` within the pipeline.

#### Boolean Parameter

A boolean parameter allows you to enable or disable certain stages or actions within the pipeline. This is useful when you want to conditionally execute parts of the pipeline based on user input.

**Example:**

Let's define a boolean parameter to control whether tests should be executed:

```groovy
pipeline {
    agent any
    parameters {
        booleanParam(name: 'EXECUTE_TESTS', defaultValue: true, description: 'Run tests?')
    }
    stages {
        stage('Build') {
            steps {
                echo "Building the application"
            }
        }
        stage('Test') {
            when {
                expression { return params.EXECUTE_TESTS }
            }
            steps {
                echo "Running tests"
            }
        }
    }
}
```

In this example, the `booleanParam` `EXECUTE_TESTS` is set to `true` by default. The `when` expression checks if `EXECUTE_TESTS` is `true` before executing the `Test` stage.

### Using Parameters in Conditional Expressions

Parameters can be used in conditional expressions to control the execution flow of the pipeline. This is achieved using the `when` directive in Jenkins pipelines.

**Example:**

Here’s an expanded example that demonstrates the use of both `choice` and `boolean` parameters in conditional expressions:

```groovy
pipeline {
    agent any
    parameters {
        choice(name: 'VERSION_NAME', choices: ['v1.0', 'v1.1', 'v1.2'], description: 'Select the version name')
        booleanParam(name: 'EXECUTE_TESTS', defaultValue: true, description: 'Run tests?')
    }
    stages {
        stage('Build') {
            steps {
                echo "Building version ${params.VERSION_NAME}"
            }
        }
        stage('Test') {
            when {
                expression { return params.EXECUTE_TESTS }
            }
            steps {
                echo "Running tests for version ${params.VERSION_NAME}"
            }
        }
    }
}
```

In this example, the `Build` stage always runs, but the `Test` stage only runs if `EXECUTE_TESTS` is `true`.

### Post-Build Actions

Post-build actions are tasks that are performed after the main build process is completed. These actions can include notifications, archiving artifacts, or triggering downstream jobs. Jenkins provides several built-in post-build actions, and you can also define custom actions.

**Example:**

Let's define a post-build action to send an email notification upon successful completion of the build:

```groovy
pipeline {
    agent any
    parameters {
        choice(name: 'VERSION_NAME', choices: ['v1.0', 'v1.1', 'v1.2'], description: 'Select the version name')
        booleanParam(name: 'EXECUTE_TESTS', defaultValue: true, description: 'Run tests?')
    }
    stages {
        stage('Build') {
            steps {
                echo "Building version ${params.VERSION_NAME}"
            }
        }
        stage('Test') {
            when {
                expression { return params.EXECUTE_TESTS }
            }
            steps {
                echo "Running tests for version ${params.VERSION_NAME}"
            }
        }
    }
    post {
        success {
            mail to: 'build@company.com', subject: 'Build Successful', body: 'The build was successful.'
        }
    }
}
```

In this example, the `post` block defines a `success` condition that sends an email notification upon successful completion of the build.

### Real-World Examples and Security Considerations

#### Real-World Example: CVE-2021-21234

CVE-2021-21234 is a critical vulnerability in Jenkins that allows remote code execution. This vulnerability can be exploited if an attacker gains access to the Jenkins server and manipulates the pipeline parameters.

**Example Exploit:**

An attacker might manipulate the `EXECUTE_TESTS` parameter to bypass security checks and execute arbitrary code.

**Secure Coding Fix:**

To prevent such vulnerabilities, ensure that all pipeline parameters are validated and sanitized before use. Use secure coding practices and validate user inputs to prevent injection attacks.

**Vulnerable Code:**

```groovy
pipeline {
    agent any
    parameters {
        string(name: 'COMMAND', defaultValue: 'echo "Hello World"', description: 'Command to execute')
    }
    stages {
        stage('Execute Command') {
            steps {
                sh "${params.COMMAND}"
            }
        }
    }
}
```

**Fixed Code:**

```groovy
pipeline {
    agent any
    parameters {
        string(name: 'COMMAND', defaultValue: 'echo "Hello World"', description: 'Command to execute')
    }
    stages {
        stage('Validate Command') {
            steps {
                script {
                    def safeCommand = params.COMMAND.replaceAll(/[^a-zA-Z0-9\s]/, '')
                    sh "${safeCommand}"
                }
            }
        }
    }
}
```

In the fixed code, the `replaceAll` method is used to sanitize the `COMMAND` parameter, removing any potentially harmful characters.

### How to Prevent / Defend

#### Detection

To detect potential vulnerabilities in Jenkins pipelines, use static code analysis tools like SonarQube or Checkmarx. These tools can identify insecure coding practices and potential security issues.

#### Prevention

1. **Parameter Validation**: Always validate and sanitize user inputs to prevent injection attacks.
2. **Least Privilege Principle**: Run Jenkins agents with the least privilege necessary to perform their tasks.
3. **Regular Updates**: Keep Jenkins and all plugins up to date to mitigate known vulnerabilities.
4. **Security Plugins**: Use security-focused plugins like the Script Security Plugin to restrict the execution of potentially dangerous scripts.

#### Secure-Coding Fixes

Show the vulnerable pattern and the corrected secure version side by side:

**Vulnerable Pattern:**

```groovy
pipeline {
    agent any
    parameters {
        string(name: 'COMMAND', defaultValue: 'echo "Hello World"', description: 'Command to execute')
    }
    stages {
        stage('Execute Command') {
            steps {
                sh "${params.COMMAND}"
            }
        }
    }
}
```

**Secure Pattern:**

```groovy
pipeline {
    agent any
    parameters {
        string(name: 'COMMAND', defaultValue: 'echo "Hello World"', description: 'Command to execute')
    }
    stages {
        stage('Validate Command') {
            steps {
                script {
                    def safeCommand = params.COMMAND.replaceAll(/[^a-zA-Z0-9\s]/, '')
                    sh "${safeCommand}"
                }
            }
        }
    }
}
```

### Hands-On Labs

For practical experience with Jenkins pipeline parameters and post-build actions, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to understand and mitigate common security vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.

These labs provide a controlled environment to experiment with Jenkins pipelines and understand the practical implications of parameter usage and post-build actions.

By thoroughly understanding and implementing these concepts, you can create more robust and secure Jenkins pipelines that meet the demands of modern DevOps environments.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/30-Jenkins Pipeline Post Build Actions Explained/00-Overview|Overview]] | [[02-Jenkins Pipeline Post Build Actions Explained|Jenkins Pipeline Post Build Actions Explained]]
