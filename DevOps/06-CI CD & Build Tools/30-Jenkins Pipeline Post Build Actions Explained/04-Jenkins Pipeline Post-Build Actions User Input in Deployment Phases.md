---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Jenkins Pipeline Post-Build Actions: User Input in Deployment Phases

In the context of continuous integration and continuous delivery (CI/CD) pipelines, Jenkins is a widely-used automation server that helps teams integrate changes to the application more frequently, and in a more reliable way. One of the key features of Jenkins is its ability to incorporate user input during various stages of the pipeline, particularly during post-build actions such as deployment phases. This allows for greater flexibility and control over the deployment process, enabling users to specify details like the target environment or the version of the artifact to be deployed.

### Background Theory

Before diving into the specifics of incorporating user input in Jenkins pipelines, it's essential to understand the broader context of CI/CD and Jenkins itself.

#### Continuous Integration and Continuous Delivery (CI/CD)

Continuous Integration (CI) is a development practice where developers regularly merge their code changes into a central repository after which automated builds and tests are run. Continuous Delivery (CD) extends CI by ensuring that the software can be released to production at any time through automated testing and deployment processes.

#### Jenkins Overview

Jenkins is an open-source automation server written in Java. It supports thousands of plugins to support building, deploying, and automating any project. Jenkins is highly extensible and can be customized to suit a wide range of needs, including:

- **Build Automation**: Automate the build process for your applications.
- **Test Automation**: Run automated tests to ensure code quality.
- **Deployment Automation**: Automate the deployment process to various environments.
- **Pipeline as Code**: Define the entire CI/CD pipeline using code, typically in a `Jenkinsfile`.

### Incorporating User Input in Jenkins Pipelines

One of the powerful features of Jenkins pipelines is the ability to incorporate user input during various stages of the pipeline. This is particularly useful in deployment phases where users might want to specify details like the target environment or the version of the artifact to be deployed.

#### Defining the `input` Block

To allow user input in a Jenkins pipeline, you can use the `input` block. This block is defined within the pipeline script and allows you to pause the pipeline execution and wait for user input before proceeding.

Here’s a step-by-step guide on how to define and use the `input` block:

1. **Define the `input` Block**:
   - The `input` block is defined at the same level as other pipeline steps.
   - You need to provide a `message` parameter to inform the user about the input required.
   - Optionally, you can define additional parameters like `ok`, `parameters`, etc.

2. **Example of an `input` Block**:
   ```groovy
   pipeline {
       agent any
       stages {
           stage('Build') {
               steps {
                   echo 'Building...'
               }
           }
           stage('Deploy') {
               steps {
                   input message: 'Select the environment to deploy to', ok: 'Done'
                   echo 'Deploying to selected environment...'
               }
           }
       }
   }
   ```

### Detailed Explanation of the `input` Block

Let's break down the components of the `input` block:

- **Message Parameter**:
  - The `message` parameter is a required field that informs the user about the input required.
  - Example: `message: 'Select the environment to deploy to'`
  
- **OK Parameter**:
  - The `ok` parameter defines the label for the button that the user clicks to confirm their input.
  - Example: `ok: 'Done'`
  
- **Parameters Block**:
  - The `parameters` block allows you to define specific input parameters that the user can provide.
  - These parameters can include text fields, dropdown menus, checkboxes, etc.
  - Example:
    ```groovy
    input message: 'Select the environment to deploy to', ok: 'Done', parameters: [
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Choose the environment')
    ]
    ```

### Real-World Examples

Let's consider a real-world scenario where a company uses Jenkins for their CI/CD pipeline. They have multiple environments (development, staging, production) and want to allow users to specify which environment the built artifact should be deployed to.

#### Scenario: Deploying to a Specific Environment

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building the artifact...'
            }
        }
        stage('Deploy') {
            steps {
                input message: 'Select the environment to deploy to', ok: 'Done', parameters: [
                    choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Choose the environment')
                ]
                script {
                    def env = params.ENVIRONMENT
                    echo "Deploying to ${env} environment..."
                }
            }
        }
    }
}
```

### Pitfalls and Best Practices

While incorporating user input in Jenkins pipelines can be very powerful, there are several pitfalls to be aware of:

- **Security Risks**:
  - Allowing user input can introduce security risks if not properly validated and sanitized.
  - Ensure that user inputs are validated and sanitized to prevent injection attacks or other vulnerabilities.

- **User Experience**:
  - Make sure the messages and prompts are clear and concise to avoid confusion.
  - Provide default values or sensible defaults to reduce user burden.

### How to Prevent / Defend

#### Detection and Prevention

- **Input Validation**:
  - Always validate user inputs to ensure they meet expected criteria.
  - Use regular expressions or predefined lists to validate input values.

- **Sanitization**:
  - Sanitize user inputs to remove any potentially harmful characters or patterns.
  - Use libraries or functions designed for sanitizing user inputs.

#### Secure Coding Fixes

- **Vulnerable Code Example**:
  ```groovy
  input message: 'Enter the environment name', ok: 'Done', parameters: [
      string(name: 'ENVIRONMENT', defaultValue: 'dev', description: 'Enter the environment name')
  ]
  script {
      def env = params.ENVIRONMENT
      sh "scp myapp.jar user@${env}:~/"
  }
  ```
  
- **Secure Code Example**:
  ```groovy
  input message: 'Enter the environment name', ok: 'Done', parameters: [
      string(name: 'ENVIRONMENT', defaultValue: 'dev', description: 'Enter the environment name')
  ]
  script {
      def env = params.ENVIRONMENT.trim()
      if (!env.matches('[a-zA-Z0-9]+')) {
          error "Invalid environment name: ${env}"
      }
      sh "scp myapp.jar user@${env}:~/"
  }
  ```

### Conclusion

Incorporating user input in Jenkins pipelines can greatly enhance the flexibility and control of your CI/CD processes. By carefully defining and validating user inputs, you can ensure that your deployments are both efficient and secure. Remember to always validate and sanitize user inputs to prevent potential security risks.

### Practice Labs

For hands-on experience with Jenkins pipelines and user input, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web security, including some that touch on CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which can be integrated with Jenkins pipelines for learning purposes.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that can be used to learn about web security and CI/CD practices.

These labs provide practical scenarios where you can apply the concepts learned in this chapter.

---
<!-- nav -->
[[03-Jenkins Pipeline Post-Build Actions Explained|Jenkins Pipeline Post-Build Actions Explained]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/30-Jenkins Pipeline Post Build Actions Explained/00-Overview|Overview]] | [[05-Jenkins Pipeline Post-Build Actions and Conditional Stages|Jenkins Pipeline Post-Build Actions and Conditional Stages]]
