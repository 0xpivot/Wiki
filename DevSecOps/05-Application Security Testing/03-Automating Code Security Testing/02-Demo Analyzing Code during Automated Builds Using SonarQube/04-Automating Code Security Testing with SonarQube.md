---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Automating Code Security Testing with SonarQube

### Introduction to Code Security Testing

Automating code security testing is a critical component of modern DevSecOps practices. It ensures that code is scanned for vulnerabilities and security issues at various stages of the development lifecycle, from initial commit to deployment. One of the most popular tools for this purpose is SonarQube, which provides comprehensive analysis of code quality, including security vulnerabilities.

### Understanding SonarQube

SonarQube is an open-source platform designed to analyze code quality and security. It supports multiple programming languages and integrates seamlessly with continuous integration (CI) pipelines. The primary goal of SonarQube is to provide developers with immediate feedback on the quality and security of their code, enabling them to address issues early in the development process.

#### Key Features of SonarQube

- **Code Quality Analysis**: SonarQube checks for coding standards, design issues, and potential bugs.
- **Security Vulnerability Detection**: It identifies security vulnerabilities such as SQL injection, cross-site scripting (XSS), and buffer overflows.
- **Maintainability Metrics**: SonarQube provides metrics on code maintainability, helping teams understand the long-term sustainability of their codebase.
- **Integration with CI/CD Pipelines**: SonarQube can be integrated with various CI/CD tools like Jenkins, GitLab CI, and CircleCI to automate the analysis process.

### Setting Up SonarQube in a CI Pipeline

To integrate SonarQube into your CI pipeline, you need to configure the pipeline to run the SonarQube scanner. This typically involves setting up environment variables and configuring the build steps to execute the scanner.

#### Example Configuration

Let's consider a simple example using a Docker-based CI pipeline. Here’s how you can set up SonarQube in a Jenkins pipeline:

```yaml
pipeline {
    agent { docker 'maven:3.6-jdk-8' }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQube Scanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }
    }
}
```

In this example, the `withSonarQubeEnv` step sets up the necessary environment variables for the SonarQube scanner. The `sonar-scanner` command runs the analysis on the codebase.

### Configuring SonarQube Scanner

The SonarQube scanner requires several properties to be configured correctly. These properties can be set via environment variables or a `sonar-project.properties` file.

#### Example `sonar-project.properties` File

```properties
# Required metadata
sonar.projectKey=my_project_key
sonar.projectName=My Project Name
sonar.projectVersion=1.0

# Path to source directories (required)
sonar.sources=src/main/java

# Language
sonar.language=java

# Encoding of the source code
sonar.sourceEncoding=UTF-8
```

This file specifies the project key, name, version, source directories, language, and encoding. Adjust these settings according to your project structure.

### Running the SonarQube Scanner

Once the configuration is set up, you can run the SonarQube scanner as part of your CI pipeline. The scanner will analyze the code and report findings back to the SonarQube server.

#### Example Command

```sh
sonar-scanner
```

This command triggers the analysis process. Depending on the size of the codebase, this step can take some time. To avoid holding up the entire CI process, you can run the scanner asynchronously.

### Asynchronous Scanning

Running the SonarQube scanner asynchronously means that the analysis does not block the main CI pipeline. Instead, it runs in the background, allowing the pipeline to continue with other tasks.

#### Example Asynchronous Setup

You can configure the scanner to run asynchronously by scheduling it to run at specific times, such as nightly. This can be done using cron jobs or similar scheduling mechanisms.

```yaml
pipeline {
    agent { docker 'maven:3.6-jdk-8' }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQube Scanner'
                    withSonarQubeEnv('SonarQ[ue') {
                        sh "nohup ${scannerHome}/bin/sonar-scanner > /dev/null 2>&1 &"
                    }
                }
            }
        }
    }
}
```

In this example, the `nohup` command runs the scanner in the background, allowing the pipeline to proceed without waiting for the analysis to complete.

### Viewing SonarQube Results

After the analysis is complete, you can view the results in the SonarQube dashboard. The dashboard provides detailed metrics on code quality, security, and maintainability.

#### Example Dashboard Metrics

- **Reliability**: Measures the likelihood of the code causing runtime failures.
- **Security**: Identifies security vulnerabilities and risks.
- **Maintainability**: Evaluates the ease of maintaining and evolving the codebase.

### Diving into Security Hotspots

SonarQube highlights security hotspots, which are areas of the code that require immediate attention due to potential security risks. These hotspots can include issues like SQL injection, XSS, and other vulnerabilities.

#### Example Security Hotspot

Consider a Java application with a method that constructs a SQL query based on user input:

```java
public List<User> getUsers(String username) {
    String sql = "SELECT * FROM users WHERE username = '" + username + "'";
    return jdbcTemplate.query(sql, new UserRowMapper());
}
```

This code is vulnerable to SQL injection because it directly concatenates user input into the SQL query. SonarQube would flag this as a security hotspot.

#### Secure Coding Fix

To fix this issue, you should use parameterized queries:

```java
public List<User> getUsers(String username) {
    String sql = "SELECT * FROM users WHERE username = ?";
    return jdbcTemplate.query(sql, new Object[]{username}, new UserRowMapper());
}
```

This approach prevents SQL injection by ensuring that user input is treated as a parameter rather than part of the SQL statement.

### Real-World Examples and CVEs

Recent breaches and CVEs often highlight the importance of automated code security testing. For example, the Log4j vulnerability (CVE-2021-44228) affected numerous applications due to insecure logging configurations. Tools like SonarQube can help identify and mitigate such issues early in the development process.

### How to Prevent / Defend

#### Detection

Regularly running SonarQube scans helps detect security vulnerabilities and code quality issues. Integrating SonarQube into your CI pipeline ensures that these scans are performed automatically with each build.

#### Prevention

- **Secure Coding Practices**: Follow secure coding guidelines and best practices to minimize vulnerabilities.
- **Code Reviews**: Conduct regular code reviews to catch issues before they make it to production.
- **Dependency Management**: Keep dependencies up-to-date and use tools like Snyk or WhiteSource to monitor for known vulnerabilities.

#### Secure-Coding Fixes

Compare the vulnerable code with the secure version side by side to understand the changes required:

**Vulnerable Code**

```java
public List<User> getUsers(String username) {
    String sql = "SELECT * FROM users WHERE username = '" + username + "'";
    return jdbcTemplate.query(sql, new UserRowMapper());
}
```

**Secure Code**

```java
public List<User> getUsers(String username) {
    String sql = "SELECT * FROM users WHERE username = ?";
    return jdbcTemplate.query(sql, new Object[]{username}, new UserRowMapper());
}
```

### Complete Example: Full HTTP Request and Response

When integrating SonarQube with a CI/CD pipeline, you often need to configure HTTP requests and responses. Here’s an example of a full HTTP request and response for triggering a SonarQube analysis:

#### HTTP Request

```http
POST /api/qualitygates/project_status HTTP/1.1
Host: sonarqube.example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Content-Type: application/json

{
  "projectKey": "my_project_key",
  "branch": "main"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 123

{
  "projectStatus": {
    "status": "OK",
    "conditions": [
      {
        "metric": "coverage",
        "value": "80%",
        "level": "INFO"
      },
      {
        "metric": "security_rating",
        "value": "A",
        "level": "OK"
      }
    ]
  }
}
```

### Mermaid Diagrams

#### CI/CD Pipeline with SonarQube Integration

```mermaid
graph TD
    A[Checkout] --> B[Build]
    B --> C[SonarQube Analysis]
    C --> D[Test]
    D --> E[Deploy]
```

#### SonarQube Analysis Flow

```mermaid
sequenceDiagram
    participant CI_Pipeline
    participant SonarQube_Scanner
    participant SonarQube_Server

    CI_Pipeline->>SonarQube_Scanner: Trigger Scan
    SonarQube_Scanner->>SonarQube_Server: Send Analysis Data
    SonarQube_Server-->>SonarQube_Scanner: Return Results
    SonarQube_Scanner-->>CI_Pipeline: Report Findings
```

### Hands-On Labs

For practical experience with automating code security testing using SonarQube, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web app for security training.
- **WebGoat**: An interactive training application for learning about web application security.

These labs provide real-world scenarios to apply the concepts learned in this chapter.

### Conclusion

Automating code security testing with SonarQube is a powerful way to ensure the quality and security of your codebase. By integrating SonarQube into your CI/CD pipeline, you can catch and address issues early, reducing the risk of vulnerabilities making it to production. Regular scanning, secure coding practices, and code reviews are essential components of a robust DevSecOps strategy.

---
<!-- nav -->
[[03-Introduction to SonarQube for Code Security Testing|Introduction to SonarQube for Code Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/02-Demo Analyzing Code during Automated Builds Using SonarQube/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/02-Demo Analyzing Code during Automated Builds Using SonarQube/05-Practice Questions & Answers|Practice Questions & Answers]]
