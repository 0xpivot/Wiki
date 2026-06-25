---
course: DevSecOps
topic: Integrating Automated Security Testing into Azure Pipelines
tags: [devsecops]
---

## Introduction to Integrating Automated Security Testing into Azure Pipelines

In the realm of DevSecOps, integrating automated security testing into your continuous integration and delivery (CI/CD) pipelines is crucial for maintaining robust security throughout the software development lifecycle. This chapter delves into the various approaches for integrating automated security testing into Azure Pipelines, a popular CI/CD platform provided by Microsoft. We will explore the requirements, methodologies, and practical implementations to ensure that your applications are secure from the very beginning of the development process.

### Requirements for Integrating Automated Security Testing

Before diving into the specifics of integrating automated security testing, it is essential to understand the requirements and objectives:

1. **Improving Application Security**: The primary goal is to enhance the security posture of your existing application by incorporating security testing into the CI/CD pipeline.
2. **Modifying Existing Pipelines**: You will be working with an already defined Azure Pipeline and adding security testing tasks to it.
3. **Team Ingestion of Results**: The test results should be easily consumable by the development team to facilitate quick identification and resolution of security issues.

### Stages vs. Gates in Azure Pipelines

One of the fundamental decisions when integrating security testing into Azure Pipelines is whether to implement security testing in stages or gates. Understanding the differences between these two approaches is crucial for effective implementation.

#### Stages

Stages are components of the pipeline that represent distinct phases of the build, test, and deployment process. Each stage can contain multiple jobs, and within each job, you can define specific security tests.

**Key Characteristics of Stages:**
- **Control Within the Team**: The team has full control over the execution of security tests within the stages.
- **Part of the Pipeline**: Stages are integral parts of the pipeline and are executed sequentially or in parallel based on the pipeline definition.
- **Specific Security Tests**: Each stage can perform a specific type of security test, such as static code analysis, dynamic application security testing (DAST), or dependency scanning.

**Example of a Stage in Azure Pipelines:**

```yaml
stages:
- stage: Build
  jobs:
  - job: BuildJob
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: '10.x'
      displayName: 'Install Node.js'
    - script: npm install
      displayName: 'npm install'

- stage: Test
  dependsOn: Build
  jobs:
  - job: StaticCodeAnalysis
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: SonarCloudPrepare@1
      inputs:
        SonarCloud: 'sonarcloud-service-connection'
        organization: 'your-organization-name'
        projectKey: 'your-project-key'
        scannerMode: 'CLI'
        extraProperties: 'sonar.host.url=https://sonarcloud.io'
    - script: sonar-scanner
      displayName: 'Run SonarScanner'
```

**Explanation:**
- **Build Stage**: Contains a job to install Node.js and run `npm install`.
- **Test Stage**: Depends on the Build stage and contains a job for static code analysis using SonarCloud.

#### Gates

Gates are pre- or post-deployment steps that collect test results from multiple sources, including external testing tools. They serve as checkpoints to determine whether the application meets the required security standards before proceeding with deployment.

**Key Characteristics of Gates:**
- **External Sources**: Gates can ingest results from external testing tools, providing a comprehensive view of the application's security posture.
- **Control Outside the Team**: The decision to allow deployment often lies outside the development team, typically with security or compliance teams.
- **Collective Results**: Gates aggregate results from various security tests and use them to make informed decisions about deployment.

**Example of a Gate in Azure Pipelines:**

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Build
  jobs:
  - job: BuildJob
    steps:
    - script: echo Building...
      displayName: 'Build'

- stage: Test
  dependsOn: Build
  jobs:
  - job: StaticCodeAnalysis
    steps:
    - task: SonarCloudPrepare@1
      inputs:
        SonarCloud: 'sonarcloud-service-connection'
        organization: 'your-organization-name'
        projectKey: 'your-project-key'
        scannerMode: 'CLI'
        extraProperties: 'sonar.host.url=https://sonarcloud.io'
    - script: sonar-scanner
      displayName: 'Run SonarScanner'

- stage: Deploy
  dependsOn: Test
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - job: DeployJob
    steps:
    - script: echo Deploying...
      displayName: 'Deploy'

- stage: SecurityGate
  dependsOn: Deploy
  jobs:
  - job: SecurityCheck
    steps:
    - task: AzureCLI@2
      inputs:
        azureSubscription: 'your-subscription'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az security assessment create --name "SecurityAssessment" --definition-id "your-definition-id"
          az security assessment list --query "[?properties.status.code=='Failed']"
    - script: echo Security check passed
      displayName: 'Security Check Passed'
```

**Explanation:**
- **Build Stage**: Contains a job to build the application.
- **Test Stage**: Contains a job for static code analysis using SonarCloud.
- **Deploy Stage**: Depends on the Test stage and deploys the application.
- **SecurityGate Stage**: Aggregates results from various security tests and uses them to decide whether to proceed with deployment.

### Practical Examples and Real-World Scenarios

To illustrate the practical application of integrating automated security testing into Azure Pipelines, let's consider some real-world scenarios and recent CVEs.

#### Example 1: Static Code Analysis Using SonarQube

Static code analysis tools like SonarQube can identify potential security vulnerabilities in the codebase. For instance, consider the following scenario where a developer inadvertently introduces a SQL injection vulnerability.

**Vulnerable Code:**

```python
import sqlite3

def get_user_data(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
```

**Secure Code:**

```python
import sqlite3

def get_user_data(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    return result
```

**SonarQube Integration in Azure Pipelines:**

```yaml
stages:
- stage: Build
  jobs:
  - job: BuildJob
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - script: pip install -r requirements.txt
      displayName: 'Install dependencies'

- stage: Test
  dependsOn: Build
  jobs:
  - job: StaticCodeAnalysis
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: SonarCloudPrepare@1
      inputs:
        SonarCloud: 'sonarcloud-service-connection'
        organization: 'your-organization-name'
        projectKey: 'your-project-key'
        scannerMode: 'CLI'
        extraProperties: 'sonar.host.url=https://sonarcloud.io'
    - script: sonar-scanner
      displayName: 'Run SonarScanner'
```

**Explanation:**
- **Build Stage**: Installs dependencies.
- **Test Stage**: Runs static code analysis using SonarQube.

#### Example 2: Dynamic Application Security Testing (DAST)

Dynamic application security testing tools like OWASP ZAP can simulate attacks on the running application to identify vulnerabilities. Consider a scenario where an application is vulnerable to Cross-Site Scripting (XSS).

**Vulnerable Code:**

```html
<!DOCTYPE html>
<html>
<body>

<h2>User Input</h2>

<p id="demo"></p>

<script>
var user_input = "<script>alert('XSS')</script>";
document.getElementById("demo").innerHTML = user_input;
</script>

</body>
</html>
```

**Secure Code:**

```html
<!DOCTYPE html>
<html>
<body>

<h2>User Input</h2>

<p id="demo"></p>

<script>
var user_input = "<script>alert('XSS')</script>";
document.getElementById("demo").textContent = user_input;
</script>

</body>
</html>
```

**OWASP ZAP Integration in Azure Pipelines:**

```yaml
stages:
- stage: Build
  jobs:
  - job: BuildJob
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - script: npm install
      displayName: 'Install dependencies'

- stage: Test
  dependsOn: Build
  jobs:
  - job: DynamicSecurityTesting
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: OWASPZAP@1
      inputs:
        zapVersion: 'latest'
        targetUrl: 'http://localhost:3000'
        reportFormat: 'html'
        reportName: 'zap-report.html'
```

**Explanation:**
- **Build Stage**: Installs dependencies.
- **Test Stage**: Runs dynamic security testing using OWASP ZAP.

### Common Pitfalls and Best Practices

When integrating automated security testing into Azure Pipelines, several common pitfalls can arise. Here are some best practices to avoid these issues:

1. **Ensure Comprehensive Coverage**: Make sure that all critical areas of the application are covered by security tests.
2. **Regularly Update Tools**: Keep security testing tools up-to-date to ensure they can detect the latest vulnerabilities.
3. **Integrate with CI/CD**: Ensure that security tests are integrated seamlessly into the CI/CD pipeline to provide timely feedback.
4. **Automate Remediation**: Automate the process of fixing identified vulnerabilities to reduce the time and effort required.

### How to Prevent / Defend

To effectively defend against security threats, it is crucial to implement robust detection and prevention mechanisms. Here are some strategies:

1. **Detection:**
   - **Monitor Logs**: Regularly monitor logs for suspicious activities.
   - **Use Security Information and Event Management (SIEM) Systems**: Implement SIEM systems to correlate and analyze security events.

2. **Prevention:**
   - **Implement Secure Coding Practices**: Follow secure coding guidelines to minimize the introduction of vulnerabilities.
   - **Use Security Policies**: Define and enforce security policies across the organization.

3. **Secure-Coding Fixes:**
   - **Vulnerable Pattern vs. Secure Version**: Compare vulnerable code patterns with their secure counterparts to understand the necessary changes.

4. **Configuration Hardening:**
   - **Secure Configuration Management**: Ensure that all configurations are hardened against common security threats.

### Conclusion

Integrating automated security testing into Azure Pipelines is a critical step in ensuring the security of your applications. By understanding the requirements, methodologies, and practical implementations, you can effectively enhance your application's security posture. Whether you choose to implement security testing in stages or gates, the key is to maintain comprehensive coverage, regular updates, and seamless integration with your CI/CD pipeline.

### Practice Labs

For hands-on experience with integrating automated security testing into Azure Pipelines, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about web security vulnerabilities and how to test for them.
- **OWASP Juice Shop**: A deliberately insecure web application to practice security testing techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning security testing.

These labs provide real-world scenarios and challenges to help you master the integration of automated security testing into Azure Pipelines.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/02-Approaches on Integrating Automated Security Testing with Azure Pipelines/00-Overview|Overview]] | [[02-Integrating Automated Security Testing into Azure Pipelines|Integrating Automated Security Testing into Azure Pipelines]]
