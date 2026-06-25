---
course: DevSecOps
topic: Integrating Automated Security Testing into Azure Pipelines
tags: [devsecops]
---

## Integrating Automated Security Testing into Azure Pipelines

### Introduction to Azure Pipelines

Azure Pipelines is a powerful continuous integration and continuous delivery (CI/CD) service provided by Microsoft. It enables developers to automate their build, test, and deployment processes. By integrating automated security testing into Azure Pipelines, organizations can ensure that their applications are secure throughout the development lifecycle.

### Native Method for Automated Security Testing

One of the primary ways to integrate automated security testing into Azure Pipelines is through the native method. This involves configuring your pipeline to run security tests as part of the build or release process.

#### Configuring the Pipeline

To configure the pipeline, you need to define the tasks that will run the security tests. These tasks can be added to the pipeline definition in YAML format. Here’s an example of how to set up a pipeline to run a security test using a Docker container:

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

jobs:
- job: RunSecurityTests
  steps:
  - task: Docker@2
    inputs:
      command: 'build'
      dockerfile: '**/Dockerfile'
      tags: '$(Build.BuildId)'
  - script: |
      docker run --rm $(Build.BuildId)
    displayName: 'Run Security Tests'
```

#### Explanation of the Configuration

- **Trigger**: Specifies the branches that trigger the pipeline. In this case, the pipeline is triggered whenever changes are pushed to the `main` branch.
- **Pool**: Defines the virtual machine image used to run the pipeline. Here, we use an Ubuntu-based image.
- **Jobs**: Defines the jobs that make up the pipeline. Each job can have multiple steps.
- **Task**: The `Docker@2` task builds the Docker image defined in the `Dockerfile`.
- **Script**: Runs the Docker container to execute the security tests.

### Using Third-Party Tooling via Extensions

Another approach to integrating automated security testing is by using third-party tooling via extensions. Azure DevOps Marketplace offers a variety of extensions that can be integrated into Azure Pipelines.

#### Example: Using OWASP ZAP Extension

OWASP ZAP (Zed Attack Proxy) is a popular open-source web application security scanner. An extension for ZAP is available in the Azure DevOps Marketplace.

#### Installing the Extension

1. Go to the Azure DevOps Marketplace.
2. Search for "OWASP ZAP".
3. Install the extension.

#### Configuring the Pipeline with ZAP

Once installed, you can configure your pipeline to use ZAP for security testing. Here’s an example of how to set up the pipeline:

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

jobs:
- job: RunSecurityTests
  steps:
  - task: ZAPScan@1
    inputs:
      zapVersion: 'latest'
      targetUrl: 'http://localhost:8080'
      reportType: 'html'
      reportName: 'zap-report.html'
```

#### Explanation of the Configuration

- **ZAPScan@1**: Task to run ZAP scan.
- **zapVersion**: Specifies the version of ZAP to use.
- **targetUrl**: URL of the application to be scanned.
- **reportType**: Type of report to generate.
- **reportName**: Name of the report file.

### Using External Scanning Tools

External scanning tools can also be integrated into Azure Pipelines. These tools can be run as part of the pipeline to perform security testing.

#### Example: Using Trivy for Container Image Scanning

Trivy is a lightweight and versatile security scanner for container images. It can be integrated into Azure Pipelines to scan Docker images for vulnerabilities.

#### Configuring the Pipeline with Trivy

Here’s an example of how to set up the pipeline to use Trivy:

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

jobs:
- job: RunSecurityTests
  steps:
  - task: Docker@2
    inputs:
      command: 'build'
      dockerfile: '**/Dockerfile'
      tags: '$(Build.BuildId)'
  - script: |
      trivy image $(Build.BuildId)
    displayName: 'Run Trivy Scan'
```

#### Explanation of the Configuration

- **Docker@2**: Task to build the Docker image.
- **Script**: Runs Trivy to scan the Docker image.

### Choosing the Right Method

When choosing between the native method, third-party tooling via extensions, and external scanning tools, it’s important to consider the advantages and limitations of each approach.

#### Advantages and Limitations

- **Native Method**:
  - **Advantages**: Seamless integration with Azure Pipelines, no additional setup required.
  - **Limitations**: Limited to built-in capabilities, may lack advanced features.

- **Third-Party Tooling via Extensions**:
  - **Advantages**: Access to a wide range of tools, flexibility in choosing the right tool for the job.
  - **Limitations**: Requires installation and configuration of extensions, potential compatibility issues.

- **External Scanning Tools**:
  - **Advantages**: Highly customizable, access to specialized tools.
  - **Limitations**: Requires additional setup and configuration, may require manual intervention.

### Real-World Examples

#### Recent CVEs and Breaches

Automated security testing can help identify and mitigate vulnerabilities before they are exploited. Here are some recent examples:

- **CVE-2021-44228 (Log4j)**: A critical vulnerability in the Log4j library that could allow remote code execution. Automated security testing could have identified this vulnerability early.
- **SolarWinds Supply Chain Attack**: A sophisticated cyberattack that compromised SolarWinds Orion software. Automated security testing could have detected malicious code in the software.

### How to Prevent / Defend

#### Detection

- **Regular Security Scans**: Schedule regular security scans as part of the CI/CD pipeline.
- **Real-Time Monitoring**: Implement real-time monitoring to detect and respond to security incidents.

#### Prevention

- **Secure Coding Practices**: Follow secure coding practices to minimize vulnerabilities.
- **Configuration Hardening**: Harden configurations to reduce attack surfaces.

#### Secure-Coding Fixes

Here’s an example of a vulnerable code and its secure version:

**Vulnerable Code**:
```python
import os
import subprocess

def execute_command(command):
    subprocess.run(command, shell=True)

execute_command(os.environ['USER_INPUT'])
```

**Secure Code**:
```python
import subprocess

def execute_command(command):
    subprocess.run(command.split(), check=True)

execute_command("ls")
```

#### Configuration Hardening

Here’s an example of hardening an Nginx configuration:

**Vulnerable Configuration**:
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;
    }
}
```

**Hardened Configuration**:
```nginx
server {
    listen 80 default_server;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ =404;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

### Complete Example: Full HTTP Request and Response

Here’s an example of a full HTTP request and response:

**HTTP Request**:
```http
GET /api/v1/users HTTP/1.1
Host: example.com
User-Agent: curl/7.64.1
Accept: */*
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**HTTP Response**:
```http
HTTP/1.1 200 OK
Date: Tue, 21 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 123
Connection: keep-alive
Server: nginx/1.19.10

{
    "users": [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Smith"}
    ]
}
```

### Mermaid Diagrams

#### Pipeline Architecture

```mermaid
graph TD
    A[Source Control] --> B[Build]
    B --> C[Test]
    C --> D[Deploy]
    D --> E[Post-Deployment Tests]
```

#### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Pipeline
    participant Scanner
    participant Report

    User->>Pipeline: Trigger Build
    Pipeline->>Scanner: Run Security Test
    Scanner-->>Report: Generate Report
    Report-->>User: Send Report
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide practical experience in integrating automated security testing into Azure Pipelines.

### Conclusion

Integrating automated security testing into Azure Pipelines is crucial for ensuring the security of applications throughout the development lifecycle. By leveraging native methods, third-party tooling via extensions, and external scanning tools, organizations can effectively identify and mitigate vulnerabilities. Regular security scans, real-time monitoring, and secure coding practices are essential for maintaining a secure environment. Hands-on practice through labs like PortSwigger Web Security Academy, OWASP Juice Shop, and DVWA can further enhance these skills.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/05-Module Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/05-Module Summary/02-Practice Questions & Answers|Practice Questions & Answers]]
