---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Introduction to Jenkins and Integrating Automated Security Testing

### What is Jenkins?

Jenkins is an open-source automation server that provides continuous integration and continuous delivery (CI/CD) services. It is widely used in software development to automate the building, testing, and deployment of applications. Jenkins supports a wide range of plugins that extend its functionality, including those for security testing.

### Why Integrate Automated Security Testing?

Integrating automated security testing into your Jenkins pipeline is crucial for ensuring that your application remains secure throughout its development lifecycle. Automated security testing helps identify vulnerabilities early in the development process, reducing the cost and complexity of fixing issues later.

### How Does Automated Security Testing Work in Jenkins?

Automated security testing in Jenkins typically involves integrating a security testing plugin into your pipeline. This plugin can scan your codebase for vulnerabilities, outdated dependencies, and other security issues. The results of these scans can then be integrated into your build process, allowing you to automatically fail builds if security issues are detected.

### Prerequisites

Before integrating automated security testing into your Jenkins pipeline, ensure you have:

- An existing Jenkins installation.
- A working pipeline in Jenkins.
- Access to the Jenkins web interface.
- Administrative privileges to install plugins.

### Example Project Setup

Let's consider an example project setup. We have a Jenkins pipeline that builds an image containing several security tools. The source for this project is hosted on GitHub, and the Jenkinsfile defines the pipeline stages.

```markdown
# Example Project Structure

- Jenkinsfile
- Dockerfile
- src/
  - main.py
```

### Jenkinsfile Overview

The `Jenkinsfile` defines the stages of the pipeline. In our example, the pipeline consists of three stages:

1. **Linting**: Checks the code for style and formatting issues.
2. **Building and Testing the Image**: Builds the Docker image and runs tests.
3. **Pushing to Registry**: Pushes the built image to a container registry.

Here is the `Jenkinsfile`:

```groovy
pipeline {
    agent any

    stages {
        stage('Linting') {
            steps {
                sh 'python -m flake8 src/'
            }
        }

        stage('Build and Test Image') {
            steps {
                script {
                    docker.build('my-security-tools')
                    docker.image('my-security-tools').inside {
                        sh 'pytest'
                    }
                }
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry('https://registry.example.com', 'credentials-id') {
                        docker.image('my-security-tools').push()
                    }
                }
            }
        }
    }
}
```

### Searching for a Security Testing Plugin

To integrate automated security testing, we need to find and install a suitable plugin. One popular choice is the **OWASP Dependency-Check** plugin, which scans for outdated or vulnerable third-party libraries.

#### Steps to Install the Plugin

1. **Log in to Jenkins**: Open the Jenkins web interface and log in with administrative credentials.
2. **Navigate to Manage Jenkins**: Click on the "Manage Jenkins" link in the left sidebar.
3. **Manage Plugins**: Click on "Manage Plugins" in the left sidebar.
4. **Find the OWASP Dependency-Check Plugin**: Search for "OWASP Dependency-Check" in the available plugins list.
5. **Install the Plugin**: Click on the "Install without restart" button to install the plugin.

### Modifying the Pipeline to Include Security Testing

Once the plugin is installed, we need to modify the `Jenkinsfile` to include the security testing stage.

#### Updated Jenkinsfile

```groovy
pipeline {
    agent any

    stages {
        stage('Linting') {
            steps {
                sh 'python -m flake8 src/'
            }
        }

        stage('Build and Test Image') {
            steps {
                script {
                    docker.build('my-security-tools')
                    docker.image('my-security-tools').inside {
                        sh 'pytest'
                    }
                }
            }
        }

        stage('Security Testing') {
            steps {
                dependencyCheck goals: 'check', skipOnSuccess: true
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry('https://registry.example.com', 'credentials-id') {
                        docker.image('my-security-tools').push()
                    }
                }
            }
        }
    }
}
```

### Explanation of the Security Testing Stage

The `dependencyCheck` step uses the OWASP Dependency-Check plugin to scan the project for vulnerabilities. The `goals: 'check'` parameter specifies that the plugin should perform a security check. The `skipOnSuccess: true` parameter ensures that the build will not fail if no vulnerabilities are found.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-44228 (Log4j)

The Log4j vulnerability (CVE-2021-44228) is a critical remote code execution flaw that affected many Java applications. By integrating automated security testing, you can detect and mitigate such vulnerabilities early in the development process.

#### Example: CVE-2022-22965 (Spring Framework)

Another example is the Spring Framework vulnerability (CVE-2022-22965), which allowed attackers to execute arbitrary code. Automated security testing can help identify and address such vulnerabilities before they are exploited.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Ignoring Vulnerabilities**: Failing to address identified vulnerabilities can leave your application exposed to attacks.
2. **False Positives**: Automated security testing may generate false positives, leading to unnecessary work. Ensure you validate findings.
3. **Outdated Scanners**: Using outdated scanners can miss new vulnerabilities. Keep your security tools up to date.

#### Best Practices

1. **Regular Updates**: Regularly update your security testing tools and plugins to ensure they detect the latest vulnerabilities.
2. **Validation**: Validate findings from automated security testing to avoid false positives.
3. **Continuous Integration**: Integrate security testing into your CI/CD pipeline to ensure it is performed consistently.

### How to Prevent / Defend

#### Detection

To detect vulnerabilities, regularly run automated security tests as part of your CI/CD pipeline. Use tools like OWASP Dependency-Check to scan for outdated or vulnerable dependencies.

#### Prevention

To prevent vulnerabilities, follow these steps:

1. **Keep Dependencies Up to Date**: Regularly update your dependencies to the latest versions.
2. **Use Secure Coding Practices**: Follow secure coding practices to minimize the introduction of vulnerabilities.
3. **Implement Security Policies**: Implement security policies and guidelines within your organization to ensure consistent security practices.

#### Secure-Coding Fixes

Compare the vulnerable and secure versions of a code snippet:

**Vulnerable Code**

```python
import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)
logging.debug('This is a debug message')
```

**Secure Code**

```python
import logging
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'default',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
})
logger = logging.getLogger(__name__)
logger.debug('This is a debug message')
```

### Configuration Hardening

Ensure your Jenkins configuration is hardened to prevent unauthorized access and potential security issues.

#### Jenkins Configuration

1. **Enable Security**: Enable security features in Jenkins to restrict access to authorized users.
2. **Use Strong Credentials**: Use strong credentials for accessing Jenkins and its plugins.
3. **Limit Permissions**: Limit permissions to the minimum necessary for users and plugins.

### Complete Example

#### Full HTTP Request and Response

When interacting with Jenkins via API, ensure you handle HTTP requests and responses securely.

**HTTP Request**

```http
POST /job/my-job/buildWithParameters HTTP/1.1
Host: jenkins.example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Content-Type: application/x-www-form-urlencoded

token=my-token&param1=value1&param2=value2
```

**HTTP Response**

```http
HTTP/1.1 201 Created
Date: Tue, 01 Aug 2023 12:00:00 GMT
Location: http://jenkins.example.com/job/my-job/123/
Content-Length: 0
```

### Practice Labs

For hands-on practice with integrating automated security testing into Jenkins pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive training on web security, including CI/CD pipelines.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another vulnerable web application for security testing.

### Conclusion

Integrating automated security testing into your Jenkins pipeline is essential for maintaining the security of your application. By following best practices and using appropriate tools, you can effectively detect and mitigate vulnerabilities throughout the development lifecycle.

---
<!-- nav -->
[[03-Introduction to Jenkins and Dependency Track Integration|Introduction to Jenkins and Dependency Track Integration]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Installing Jenkins Plugins/00-Overview|Overview]] | [[05-Configuring the Dependency Track Plugin in Jenkins|Configuring the Dependency Track Plugin in Jenkins]]
