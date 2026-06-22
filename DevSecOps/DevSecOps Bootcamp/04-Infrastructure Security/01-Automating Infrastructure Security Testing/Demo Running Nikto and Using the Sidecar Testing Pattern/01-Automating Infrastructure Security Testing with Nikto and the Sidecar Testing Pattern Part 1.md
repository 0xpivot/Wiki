---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Automating Infrastructure Security Testing with Nikto and the Sidecar Testing Pattern

### Introduction to Infrastructure Security Testing

Automating infrastructure security testing is a critical component of modern DevSecOps practices. By integrating security testing into the continuous integration and continuous deployment (CI/CD) pipeline, organizations can catch vulnerabilities early and reduce the risk of deploying insecure systems. One popular tool for automating web application security testing is Nikto, which can be integrated into CI/CD pipelines using various patterns, such as the sidecar testing pattern.

### What is Nikto?

Nikto is an open-source web server scanner that performs comprehensive checks for potential vulnerabilities, including outdated software versions, misconfigurations, and known security issues. It is widely used due to its ease of use and extensive database of known vulnerabilities.

#### How Nikto Works

Nikto operates by sending HTTP requests to a target web server and analyzing the responses. It uses a combination of predefined checks and user-defined configurations to identify potential security weaknesses. Here’s a high-level overview of the Nikto scanning process:

1. **Initialization**: Nikto starts by setting up the environment and loading the necessary configuration files.
2. **Target Identification**: The target web server is identified based on the provided URL or IP address.
3. **HTTP Requests**: Nikto sends a series of HTTP requests to the target server, varying the request types and payloads to test different aspects of the server.
4. **Response Analysis**: Each response is analyzed to determine if it matches any known vulnerabilities or misconfigurations.
5. **Reporting**: Nikto generates a detailed report summarizing the findings, which can be saved in various formats (e.g., HTML, XML).

#### Example Nikto Command

Here is an example of a basic Nikto command:

```bash
nikto -h http://example.com -output nikto_report.html
```

- `-h`: Specifies the target host.
- `-output`: Specifies the output file and format.

### The Sidecar Testing Pattern

The sidecar testing pattern is a design approach where a separate container (the sidecar) is used to perform specific tasks, such as security testing, alongside the main application container. This pattern allows for better isolation and more granular control over the testing process.

#### Benefits of the Sidecar Pattern

- **Isolation**: The sidecar container runs independently of the main application, reducing the risk of interference.
- **Modularity**: Different sidecars can be added or removed as needed, allowing for flexible and scalable testing strategies.
- **Resource Management**: Sidecar containers can be configured with specific resource limits, ensuring they do not impact the performance of the main application.

### Integrating Nikto with Jenkins Pipeline

Jenkins is a popular CI/CD tool that supports the automation of various tasks, including security testing. By integrating Nikto into a Jenkins pipeline, organizations can automate the process of scanning web applications during the build process.

#### Setting Up the Jenkins Pipeline

To integrate Nikto into a Jenkins pipeline, follow these steps:

1. **Create a Jenkinsfile**: Define the pipeline steps in a `Jenkinsfile` located in your project repository.
2. **Configure Docker**: Ensure that Docker is installed and configured on the Jenkins server.
3. **Launch the Sidecar Container**: Use Docker to launch a sidecar container that will run Nikto.
4. **Run Nikto**: Execute the Nikto scan within the sidecar container.
5. **Store and Publish Reports**: Save the Nikto report and publish it in Jenkins.

#### Example Jenkinsfile

Here is an example `Jenkinsfile` that integrates Nikto into a Jenkins pipeline:

```groovy
pipeline {
    agent { docker 'nikto' }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo.git'
            }
        }
        stage('Scan with Nikto') {
            steps {
                script {
                    // Ensure the reports directory exists
                    sh 'mkdir -p reports'
                    
                    // Run Nikto and disable the site files plugin
                    sh 'nikto -h http://example.com -Plugins "-sitefiles" -output reports/nikto_report.html'
                    
                    // Check the exit code of Nikto
                    def exitCode = sh(returnStatus: true, script: 'echo $?')
                    if (exitCode != 0) {
                        error 'Nikto scan failed'
                    }
                }
            }
        }
        stage('Publish Report') {
            steps {
                archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
            }
        }
    }
}
```

### Detailed Explanation of the Jenkinsfile

- **agent { docker 'nikto' }**: Specifies that the pipeline should run inside a Docker container named `nikto`.
- **stage('Checkout')**: Checks out the source code from the specified Git repository.
- **stage('Scan with Nikto')**: Runs the Nikto scan within the sidecar container.
  - `sh 'mkdir -p reports'`: Ensures that the `reports` directory exists.
  - `sh 'nikto -h http://example.com -Plugins "-sitefiles" -output reports/nikto_report.html'`: Runs Nikto against the specified target, disables the `sitefiles` plugin, and outputs the report to an HTML file.
  - `def exitCode = sh(returnStatus: true, script: 'echo $?')`: Captures the exit code of the Nikto command.
  - `if (exitCode !=  0) { error 'Nikto scan failed' }`: Raises an error if the Nikto scan fails.
- **stage('Publish Report')**: Archives the Nikto report for later review.

### Handling False Positives

False positives are common in security scans, and they can lead to wasted time and resources. To mitigate this issue, Nikto provides several configuration options to customize the scan and reduce false positives.

#### Disabling Plugins

One way to reduce false positives is to disable specific plugins that are known to generate false positives. In the example above, the `sitefiles` plugin is disabled using the `-Plugins "-sitefiles"` option.

#### Example of Disabling Plugins

```bash
nikto -h http://example.com -Plugins "-sitefiles"
```

### Real-World Examples and Recent CVEs

Recent breaches and CVEs have highlighted the importance of regular security testing. For example, the Log4j vulnerability (CVE-2021-44228) affected numerous web applications and demonstrated the need for continuous monitoring and testing.

#### Example: Log4j Vulnerability

The Log4j vulnerability allowed attackers to execute arbitrary code on affected servers. By integrating Nikto into the CI/CD pipeline, organizations could have detected and mitigated this vulnerability earlier.

### How to Prevent / Defend

#### Detection

- **Regular Scans**: Schedule regular Nikto scans to detect new vulnerabilities.
- **Monitoring**: Set up alerts to notify security teams of any issues found during scans.

#### Prevention

- **Patch Management**: Keep all software components up to date with the latest security patches.
- **Configuration Hardening**: Follow best practices for configuring web servers and applications to minimize exposure to known vulnerabilities.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a configuration file:

**Vulnerable Configuration:**

```yaml
server:
  port: 8080
security:
  enabled: false
```

**Secure Configuration:**

```yaml
server:
  port: 8080
security:
  enabled: true
  authentication:
    type: BASIC
```

### Hands-On Practice

For hands-on practice with Nikto and the sidecar testing pattern, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for web application security testing.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for security testing.

### Conclusion

Integrating Nikto into a CI/CD pipeline using the sidecar testing pattern is an effective way to automate infrastructure security testing. By following best practices and regularly updating configurations, organizations can significantly reduce the risk of deploying insecure systems.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/Demo Running Nikto and Using the Sidecar Testing Pattern/00-Overview|Overview]] | [[02-Automating Infrastructure Security Testing with Nikto and the Sidecar Testing Pattern|Automating Infrastructure Security Testing with Nikto and the Sidecar Testing Pattern]]
