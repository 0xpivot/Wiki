---
course: DevSecOps
topic: Integrating Automated Security Testing into Azure Pipelines
tags: [devsecops]
---

## Integrating Automated Security Testing into Azure Pipelines

### Background Theory

In the realm of DevSecOps, integrating automated security testing into your Continuous Integration/Continuous Deployment (CI/CD) pipeline is crucial. This ensures that security checks are performed automatically and consistently throughout the development lifecycle. Azure Pipelines is a powerful tool that allows developers to automate their build, test, and deployment processes. By incorporating security testing into these pipelines, teams can catch vulnerabilities early, reducing the risk of security breaches.

### Setting Up the Pipeline

To integrate automated security testing into an Azure Pipeline, we start by defining the resources required for the pipeline. In this context, resources refer to the containers that will be used during the execution of the pipeline.

#### Defining Containers

Containers provide a consistent environment for executing tasks within the pipeline. One common approach is to use a container that includes all necessary tools and dependencies for security testing. In the given example, we define a container called `Tools Image`.

```yaml
resources:
  containers:
    - container: toolsImage
      image: GoFWD/ToolsDImage:latest
```

Here, `GoFWD/ToolsDImage` is the name of the Docker image hosted on DockerHub, and `latest` specifies the version of the image to be used.

#### Running as Root

Azure Pipelines has specific requirements for Linux-based containers. One such requirement is that the container must be able to install additional packages or perform certain operations that require elevated privileges. Therefore, the container must run as the root user (User ID 0).

```yaml
resources:
  containers:
    - container: toolsImage
      image: GoFWD/ToolsDImage:latest
      options: --user 0
```

The `options` field allows us to pass additional arguments to the Docker run command. Here, `--user 0` specifies that the container should run as the root user.

### Committing the Pipeline Definition

Once the pipeline definition is set up, it needs to be committed to the repository. This ensures that the pipeline configuration is version-controlled and can be tracked alongside the rest of the codebase.

```bash
git add .
git commit -m "ci: Add automated security testing to Azure Pipeline"
```

The commit message follows the Conventional Commits standard, which helps in maintaining a clear and consistent commit history. The prefix `ci:` indicates that this commit is related to continuous integration.

### Monitoring the Pipeline Execution

After committing the changes, the pipeline will automatically pick up the new configuration and start executing the defined stages. To monitor the progress, navigate to the pipelines menu in the Azure DevOps interface.

#### Checking the Pipeline Run

Click on the pipeline run to view the detailed status of each stage. The new stage that was added for automated security testing will be executed as part of the pipeline.

### Example Scenario: Detecting Secrets in Code

One common security issue in code repositories is the accidental inclusion of sensitive information, such as API keys or passwords. Automated security testing can help identify such secrets.

#### Using a Tool for Secret Detection

A popular tool for detecting secrets in code is `trufflehog`. This tool scans the codebase for patterns that match known secret formats and alerts the team if any are found.

To integrate `trufflehog` into the Azure Pipeline, we can use a script task within the pipeline definition.

```yaml
stages:
- stage: Build
  jobs:
  - job: BuildJob
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: Bash@3
      inputs:
        targetType: 'inline'
        script: |
          trufflehog --regex --entropy=False --max-depth=10 .
```

This script runs `trufflehog` to scan the current directory (`.`) for secrets. The `--regex` flag enables regex-based detection, and `--entropy=False` disables entropy-based detection to focus on known patterns.

### Pitfalls and Common Mistakes

#### Incorrect Configuration

One common mistake is misconfiguring the pipeline resources or tasks. For example, if the `options` field is omitted, the container might not have the necessary permissions to execute certain commands, leading to failures.

#### False Positives

Automated security testing tools can sometimes generate false positives, especially if they are not finely tuned to the specific codebase. It is important to review the results and adjust the tool's settings as needed.

### How to Prevent / Defend

#### Secure Coding Practices

Implementing secure coding practices is the first line of defense against security issues. This includes:

- **Avoiding Hardcoded Secrets**: Store sensitive information in environment variables or secure vaults.
- **Using Environment-Specific Configurations**: Ensure that different environments (development, staging, production) use appropriate configurations.

#### Secure Pipeline Configuration

- **Limit Permissions**: Ensure that the pipeline runs with the minimum necessary permissions. Avoid running as root unless absolutely required.
- **Regularly Update Tools**: Keep security tools and dependencies up-to-date to benefit from the latest security patches and features.

#### Example: Correcting Vulnerable Code

Consider a scenario where a hardcoded API key is included in the codebase.

**Vulnerable Code:**

```python
import requests

API_KEY = 'your_api_key_here'
response = requests.get('https://api.example.com', headers={'Authorization': f'Bearer {API_KEY}'})
```

**Secure Code:**

```python
import os
import requests

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")
response = requests.get('https://api.example.com', headers={'Authorization': f'Bearer {API_KEY}'})
```

By using environment variables, the API key is kept out of the codebase, reducing the risk of exposure.

### Real-World Examples

#### Recent Breaches

One notable breach involving hardcoded secrets occurred in 2021 when a developer accidentally committed a GitHub Actions workflow file containing a private key. This led to unauthorized access to the repository and potential data exfiltration.

#### CVEs Related to Secret Exposure

CVE-2021-22204: A vulnerability in GitHub Actions allowed attackers to access sensitive information due to improperly configured workflows. This highlights the importance of securing pipeline configurations and avoiding hardcoded secrets.

### Hands-On Labs

For practical experience with integrating automated security testing into Azure Pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on secure coding practices and automated security testing.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing techniques.
- **Azure DevOps Documentation**: Official documentation and tutorials on setting up and configuring Azure Pipelines.

### Conclusion

Integrating automated security testing into Azure Pipelines is a critical step in ensuring the security of your applications. By setting up the necessary resources, committing the pipeline configuration, and monitoring the execution, you can catch vulnerabilities early and reduce the risk of security breaches. Always follow secure coding practices and regularly update your tools to stay ahead of potential threats.

---
<!-- nav -->
[[03-Integrating Automated Security Testing into Azure Pipelines Part 1|Integrating Automated Security Testing into Azure Pipelines Part 1]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/Demo Integrating Detection of Secrets in Azure Pipelines/00-Overview|Overview]] | [[05-Integrating Automated Security Testing into Azure Pipelines Part 3|Integrating Automated Security Testing into Azure Pipelines Part 3]]
