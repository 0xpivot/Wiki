---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Parameterizing User ID and Group ID in Jenkins

When setting up a Jenkins pipeline, it's crucial to ensure that the container running Jenkins has the correct permissions to access and modify files and directories. This is achieved by parameterizing the `USER_ID` and `GROUP_ID` under which the Jenkins container runs. These parameters are essential because they help maintain proper file ownership and permissions, especially when interacting with other containers like the Dependency Check container.

### Why Parameterize User ID and Group ID?

Parameterizing the `USER_ID` and `GROUP_ID` allows you to dynamically set the user and group IDs based on the environment in which the Jenkins pipeline is running. This flexibility ensures that the Jenkins container can correctly interact with other containers and the host filesystem without encountering permission issues.

#### Example Configuration

Here’s an example of how you might configure the `Jenkinsfile` to parameterize the `USER_ID` and `GROUP_ID`:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        // Other stages...
    }
}
```

### Correct Permissions Enforcement

Once the `USER_ID` and `GROUP_ID` are set, you can enforce the correct permissions within the Jenkins pipeline. This is particularly important when dealing with dependencies and ensuring that the Jenkins container can correctly access and modify files.

#### Example Code Block

Here’s an example of how you might enforce correct permissions within a Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                """
            }
        }
        // Other stages...
    }
}
```

### Linting and Secret Detection

After setting up the correct permissions, the next step is to perform linting and secret detection on the codebase. Linting helps identify potential coding issues, while secret detection ensures that sensitive information is not inadvertently committed to the repository.

#### Linting

Linting tools analyze the codebase for potential issues such as syntax errors, unused variables, and other common programming mistakes. Popular linting tools include ESLint for JavaScript, Pylint for Python, and RuboCop for Ruby.

#### Secret Detection

Secret detection tools scan the codebase for sensitive information such as API keys, passwords, and other credentials. Tools like `git-secrets`, `truffleHog`, and `detect-secrets` are commonly used for this purpose.

#### Example Code Block

Here’s an example of how you might integrate linting and secret detection into your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                """
            }
        }
        // Other stages...
    }
}
```

### Code Quality Metrics System

The next step is to use a code quality metrics system to evaluate the overall health and maintainability of the codebase. Tools like SonarQube provide comprehensive analysis of code quality, including metrics such as code coverage, complexity, and duplication.

#### Example Code Block

Here’s an example of how you might integrate SonarQube into your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                sonar-scanner
                """
            }
        }
        // Other stages...
    }
}
```

### Testing Third-Party Libraries

Next, you should test for insecure or outdated third-party libraries. This is typically done using tools like Dependency Check, which scans the project dependencies for known vulnerabilities.

#### Example Code Block

Here’s an example of how you might integrate Dependency Check into your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                sonar-scanner
                dependency-check --project 'My Project'
                """
            }
        }
        // Other stages...
    }
}
```

### Building and Pushing Docker Image

After performing the necessary checks, the next step is to build the Docker image and push it to a registry. This ensures that the latest version of the application is available for deployment.

#### Example Code Block

Here’s an example of how you might build and push a Docker image in your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                sonar-scanner
                dependency-check --project 'My Project'
                """
            }
        }
        stage('Build and Push Image') {
            steps {
                sh """
                docker build -t my-image .
                docker tag my-image my-registry/my-image:latest
                docker push my-registry/my-image:latest
                """
            }
        }
        // Other stages...
    }
}
```

### Launching Sidecar Container

Once the Docker image is pushed to the registry, you can launch a sidecar container from the image. This sidecar container can be used for various purposes, such as logging, monitoring, or additional security checks.

#### Example Code Block

Here’s an example of how you might launch a sidecar container in your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                sonar-scanner
                dependency-check --project 'My Project'
                """
            }
        }
        stage('Build and Push Image') {
            steps {
                sh """
                docker build -t my-image .
                docker tag my-image my-registry/my-image:latest
                docker push my-registry/my-image:latest
                """
            }
        }
        stage('Launch Sidecar') {
            steps {
                sh """
                docker run -d --name sidecar-container my-registry/my-image:latest
                """
            }
        }
        // Other stages...
    }
}
```

### Testing the Container

The next step is to test the container itself. This involves running various security checks and tests to ensure that the container is secure and functioning as expected.

#### Example Code Block

Here’s an example of how you might test the container in your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                sonar-scanner
                dependency-check --project 'My Project'
                """
            }
        }
        stage('Build and Push Image') {
            steps {
                sh """
                docker build -t my-image .
                docker tag my-image my-registry/my-image:latest
                docker push my-registry/my-image:latest
                """
            }
        }
        stage('Launch Sidecar') {
            steps {
                sh """
                docker run -d --name sidecar-container my-registry/my-image:latest
                """
            }
        }
        stage('Test Container') {
            steps {
                sh """
                docker exec sidecar-container /path/to/test/script
                """
            }
        }
        // Other stages...
    }
}
```

### Testing the Infrastructure

The final stages involve testing the infrastructure itself. This includes using tools like Nikto and OWASP ZAP to perform dynamic application security testing.

#### Nikto

Nikto is a web server scanner that performs comprehensive tests against web servers to identify potential security issues. It can detect misconfigurations, outdated software, and other vulnerabilities.

#### OWASP ZAP

OWASP ZAP (Zed Attack Proxy) is a powerful tool for automated scanning and manual testing of web applications. It can detect a wide range of security vulnerabilities, including SQL injection, cross-site scripting (XSS), and others.

#### Example Code Block

Here’s an example of how you might integrate Nikto and OWASP ZAP into your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                sonar-scanner
                dependency-check --project 'My Project'
                """
            }
        }
        stage('Build and Push Image') {
            steps {
                sh """
                docker build -t my-image .
                docker tag my-image my-registry/my-image:latest
                docker push my-registry/my-image:latest
                """
            }
        }
        stage('Launch Sidecar') {
            steps {
                sh """
                docker run -d --name sidecar-container my-registry/my-image:latest
                """
            }
        }
        stage('Test Container') {
            steps {
                sh """
                docker exec sidecar-container /path/to/test/script
                """
            }
        }
        stage('Infrastructure Testing') {
            steps {
                sh """
                nikto -h http://my-server
                zap-baseline.py -t http://my-server -r report.html
                """
            }
        }
    }
}
```

### Handling Test Failures

One important aspect of the Jenkins pipeline is how it handles test failures. In this case, the pipeline does not use hard quality gating. Instead, if a test fails, the build is marked as unstable rather than failing outright. This approach allows developers to address issues without blocking the entire pipeline.

#### Example Code Block

Here’s an example of how you might handle test failures in your Jenkins pipeline:

```groovy
pipeline {
    agent { docker { image 'jenkinsci/jnlp-slave:latest' } }
    parameters {
        string(name: 'JENKINS_USER_ID', defaultValue: '1000', description: 'User ID for Jenkins container')
        string(name: 'JENKINS_GROUP_ID', defaultValue: '1000', description: 'Group ID for Jenkins container')
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    env.JENKINS_USER_ID = params.JENKINS_USER_ID
                    env.JENKINS_GROUP_ID = params.JENKINS_GROUP_ID
                }
            }
        }
        stage('Check Code') {
            steps {
                sh """
                chown -R ${env.JENKINS_USER_ID}:${env.JENKINS_GROUP_ID} .
                npm install eslint
                eslint .
                git-secrets --register-aws
                git-secrets --scan
                sonar-scanner
                dependency-check --project 'My Project'
                """
            }
        }
        stage('Build and Push Image') {
            steps {
                sh """
                docker build -t my-image .
                docker tag my-image my-registry/my-image:latest
                docker push my-registry/my-image:latest
                """
            }
        }
        stage('Launch Sidecar') {
            steps {
                sh """
                docker run -d --name sidecar-container my-registry/my-image:latest
                """
            }
        }
        stage('Test Container') {
            steps {
                sh """
                docker exec sidecar-container /path/to/test/script
                """
            }
        }
        stage('Infrastructure Testing') {
            steps {
                sh """
                nikto -h http://my-server
                zap-baseline.py -t http://my-server -r report.html
                """
            }
        }
    }
    post {
        failure {
            echo 'Build failed but will be marked as unstable.'
            currentBuild.result = 'UNSTABLE'
        }
    }
}
```

### How to Prevent / Defend

To ensure that your Jenkins pipeline is secure and robust, it’s essential to implement various security measures and best practices.

#### Secure Coding Practices

Ensure that your code follows secure coding practices. This includes using linting tools to catch potential issues, implementing secret detection to prevent sensitive information leaks, and using code quality metrics systems to maintain high-quality code.

#### Hardening the Jenkins Environment

Hardening the Jenkins environment involves securing the Jenkins server itself, ensuring that it is up-to-date with the latest security patches, and configuring it securely. This includes disabling unnecessary plugins, securing Jenkins with strong authentication mechanisms, and limiting access to sensitive information.

#### Regular Security Audits

Regularly perform security audits and penetration testing on your Jenkins pipeline and the applications it builds. This helps identify and mitigate potential security vulnerabilities before they can be exploited.

#### Example Secure Configuration

Here’s an example of a secure Jenkins configuration:

```yaml
# Jenkins Configuration as Code (JCasC)
jenkins:
  systemMessage: 'Welcome to Jenkins!'
  securityRealm:
    local:
      allowsSignup: false
  authorizationStrategy:
    globalMatrix:
      permissions:
        - 'hudson.model.Hudson.Administer:admin'
        - 'hudson.model.Item.Build:authenticated'
        - 'hudson.model.Item.Configure:authenticated'
        - 'hudson.model.Item.Create:authenticated'
        - 'hudson.model.Item.Delete:authenticated'
        - 'hudson.model.Item.Discover:authenticated'
        - 'hudson.model.Item.Read:anonymous'
  scmCheckoutRetryCount: 3
  views:
    - all:
        name: 'All'
```

### Conclusion

Automating infrastructure security testing is a critical component of DevSecOps. By integrating tools like linters, secret detectors, code quality metrics systems, and dynamic application security scanners into your Jenkins pipeline, you can ensure that your applications are secure and robust. Additionally, by handling test failures appropriately and implementing various security measures, you can further enhance the security of your Jenkins environment.

### Practice Labs

For hands-on practice with automating infrastructure security testing, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including dynamic application security testing.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide practical experience in identifying and mitigating security vulnerabilities, making them ideal for mastering the concepts covered in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/02-Demo Implementing OWASP ZAP and All Automated Security Tests/02-Automating Infrastructure Security Testing|Automating Infrastructure Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/02-Demo Implementing OWASP ZAP and All Automated Security Tests/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/02-Demo Implementing OWASP ZAP and All Automated Security Tests/04-Practice Questions & Answers|Practice Questions & Answers]]
