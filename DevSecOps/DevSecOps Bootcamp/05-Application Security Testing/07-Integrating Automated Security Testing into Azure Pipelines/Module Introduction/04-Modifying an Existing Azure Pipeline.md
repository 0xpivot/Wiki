---
course: DevSecOps
topic: Integrating Automated Security Testing into Azure Pipelines
tags: [devsecops]
---

## Modifying an Existing Azure Pipeline

Now that we have covered the different approaches to integrating automated security testing, let's walk through the process of modifying an existing Azure Pipeline to include automated security testing.

### Step-by-Step Guide

1. **Identify the Existing Pipeline**: Locate the existing Azure Pipeline that you want to modify.
2. **Add Security Testing Steps**: Add the necessary steps to the pipeline to perform automated security testing.
3. **Configure Security Testing Tools**: Configure the security testing tools to work with your pipeline.
4. **Test the Pipeline**: Test the modified pipeline to ensure that it runs correctly and identifies any security issues.

#### Example: Modifying an Existing Pipeline

Suppose you have an existing Azure Pipeline that builds and deploys a .NET Core application. You want to add SAST using SonarQube to this pipeline.

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

- script: |
    dotnet publish -c Release -o ./publish
  displayName: 'Publish project'

- task: CopyFiles@2
  inputs:
    Contents: '**'
    TargetFolder: '$(Build.ArtifactStagingDirectory)'

- task: PublishBuildArtifacts@1
  inputs:
    PathtoPublish: '$(Build.ArtifactStagingDirectory)'
    ArtifactName: 'drop'
    publishLocation: 'Container'
```

### How to Prevent / Defend

To effectively modify an existing Azure Pipeline to include automated security testing, consider the following best practices:

- **Thorough Testing**: Thoroughly test the modified pipeline to ensure that it runs correctly and identifies any security issues.
- **Documentation**: Document the changes made to the pipeline and the rationale behind them.
- **Security Policies**: Implement security policies to enforce the use of automated security testing in all pipelines.
- **Training**: Provide training to developers on how to use and interpret the results of automated security testing.

### Summary

In this section, we walked through the process of modifying an existing Azure Pipeline to include automated security testing. We provided a detailed example using SonarQube and demonstrated how to integrate it into an existing pipeline.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Module Introduction/03-Importance of Automated Security Testing in CICD|Importance of Automated Security Testing in CICD]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Module Introduction/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Module Introduction/05-Conclusion|Conclusion]]
