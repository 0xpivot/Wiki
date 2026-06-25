---
course: DevSecOps
topic: Integrating Automated Security Testing into Azure Pipelines
tags: [devsecops]
---

## Approaches to Integrating Automated Security Testing

There are several approaches to integrating automated security testing into Azure Pipelines. Each approach has its own advantages and trade-offs.

### Static Application Security Testing (SAST)

SAST involves analyzing the source code of an application to identify potential security vulnerabilities. Tools like SonarQube, Fortify, and Veracode can be used for SAST.

#### Example: Using SonarQube with Azure Pipelines

To integrate SonarQube with Azure Pipelines, you need to set up a pipeline that includes the necessary steps to analyze the source code.

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  sonarHostUrl: 'http://sonarqube.example.com'
  sonarLogin: 'your-sonar-token'

steps:
- task: SonarQubePrepare@4
  inputs:
    sonarQubeHost: 'SonarQube'
    sonarQubeVersion: 'LTS'
    sonarQubeProjectKey: 'my-project-key'
    sonarQubeProjectName: 'My Project'
    sonarQubeProjectVersion: '1.0'
    sonarQubeBranch: '$(Build.SourceBranch)'
    sonarQubeOrganization: 'my-org'

- script: |
    dotnet build --configuration Release
  displayName: 'Build project'

- task: SonarQubeAnalyze@4
  inputs:
    sonarQubeHost: 'SonarQube'

- task: SonarQubePublish@4
  inputs:
    sonarQubeHost: 'SonarQube'
```

### Dynamic Application Security Testing (DAST)

DAST involves testing the application while it is running to identify runtime vulnerabilities. Tools like OWASP ZAP, Burp Suite, and Acunetix can be used for DAST.

#### Example: Using OWASP ZAP with Azure Pipelines

To integrate OWASP ZAP with Azure Pipelines, you need to set up a pipeline that includes the necessary steps to scan the running application.

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  zapUrl: 'http://localhost:8080'

steps:
- script: |
    docker run -d -p 8080:8080 owasp/zap2docker-stable
  displayName: 'Start ZAP Docker container'

- script: |
    curl -X POST http://localhost:8080/JSON/core/action/newSession
    curl -X POST http://localhost:8080/JSON/sites/add -d "url=http://localhost:8080"
    curl -X POST http://localhost:8080/JSON/spider/action/scan -d "url=http://localhost:8080"
  displayName: 'Run ZAP scan'

- script: |
    curl -X POST http://localhost:8080/JSON/core/action/shutdown
  displayName: 'Stop ZAP Docker container'
```

### Dependency Scanning

Dependency scanning involves checking the dependencies of an application for known vulnerabilities. Tools like OWASP Dependency-Check, Snyk, and WhiteSource can be used for dependency scanning.

#### Example: Using OWASP Dependency-Check with Azure Pipelines

To integrate OWASP Dependency-Check with Azure Pipelines, you need to set up a pipeline that includes the necessary steps to scan the dependencies.

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: Maven@3
  inputs:
    mavenPomFile: 'pom.xml'
    goals: 'dependency-check:check'
  displayName: 'Run Dependency-Check'
```

### Code Quality Analysis

Code quality analysis involves checking the code for style, formatting, and other quality issues. Tools like ESLint, Pylint, and RuboCop can be used for code quality analysis.

#### Example: Using ESLint with Azure Pipelines

To integrate ESLint with Azure Pipelines, you need to set up a pipeline that includes the necessary steps to analyze the code.

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: NodeTool@0
  inputs:
    versionSpec: '14.x'
  displayName: 'Install Node.js'

- script: |
    npm install
  displayName: 'Install dependencies'

- script: |
    npx eslint .
  displayName: 'Run ESLint'
```

### How to Prevent / Defend

To effectively integrate automated security testing into Azure Pipelines, consider the following best practices:

- **Regular Updates**: Ensure that all security testing tools are regularly updated to the latest versions.
- **Configuration Hardening**: Harden the configuration of security testing tools to minimize false positives and false negatives.
- **Secure Coding Practices**: Implement secure coding practices to reduce the likelihood of introducing vulnerabilities in the first place.
- **Continuous Monitoring**: Continuously monitor the results of automated security testing to quickly address any identified issues.

### Summary

In this section, we covered the importance of integrating automated security testing into Azure Pipelines and explored different approaches to doing so. We provided detailed examples using popular security testing tools and demonstrated how to integrate them into Azure Pipelines.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Module Introduction/01-Introduction to Integrating Automated Security Testing into Azure Pipelines|Introduction to Integrating Automated Security Testing into Azure Pipelines]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Module Introduction/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Module Introduction/03-Importance of Automated Security Testing in CICD|Importance of Automated Security Testing in CICD]]
