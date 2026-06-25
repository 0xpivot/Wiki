---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Automating Code Security Testing: Detecting New Secrets During Automated Security Testing

### Introduction to DevSecOps and Automated Security Testing

DevSecOps is an approach that integrates security practices into the continuous integration and delivery (CI/CD) pipeline. One critical aspect of DevSecOps is automating code security testing to identify vulnerabilities and security issues early in the development process. This chapter focuses on detecting new secrets during automated security testing, specifically using Jenkins and GitLab.

### Setting Up the Environment

To demonstrate the process, we start by pulling the code from GitHub and pushing it to a GitLab instance. This setup allows us to leverage GitLab's features for continuous integration and deployment.

#### Pulling Code from GitHub

First, clone the repository from GitHub:

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

#### Pushing Code to GitLab

Next, push the code to a GitLab instance. Ensure you have access to a GitLab account and a repository set up.

```bash
# Add GitLab remote
git remote add gitlab https://gitlab.com/your-username/your-repo.git

# Push code to GitLab
git push gitlab master
```

### Adding a Jenkinsfile

A Jenkinsfile is a script written in Groovy that defines the steps of a Jenkins pipeline. This file is committed to the repository and triggers the pipeline whenever changes are pushed.

#### Creating the Jenkinsfile

Create a `Jenkinsfile` in the root directory of your repository:

```groovy
pipeline {
    agent any

    stages {
        stage('Lint Dockerfile') {
            steps {
                sh 'docker run --rm hadolint/hadolint hadolint Dockerfile'
            }
        }

        stage('Detect Secrets') {
            steps {
                sh 'detect-secrets-hook pre-commit'
            }
        }
    }
}
```

This Jenkinsfile consists of two stages:

1. **Lint Dockerfile**: Lints the Dockerfile using Hadolint.
2. **Detect Secrets**: Uses `detect-secrets-hook` to check for new secrets.

### Understanding the Detect Secrets Tool

The `detect-secrets` tool is designed to find secrets in code repositories. It supports various types of secrets, such as API keys, passwords, and tokens. The tool uses a baseline to compare against new commits, ensuring only new secrets are detected.

#### Installing Detect Secrets

Install `detect-secrets` using pip:

```bash
pip install detect-secrets
```

#### Configuring Detect Secrets

Configure `detect-secrets` by creating a `.detect-secrets.yaml` file in the root directory:

```yaml
plugins:
  - plugin: HighEntropyString
    blacklisted_words:
      - "password"
      - "secret"
```

This configuration sets up the `HighEntropyString` plugin to detect high-entropy strings and blacklist specific words.

### Creating a Baseline

A baseline is a snapshot of the current state of secrets in the repository. This baseline is used to compare against new commits, identifying only new secrets.

#### Generating the Baseline

Generate the baseline using the following command:

```bash
detect-secrets scan --baseline .secrets.baseline
```

This command creates a `.secrets.baseline` file containing the current state of secrets.

### Committing Changes

Commit the `Jenkinsfile` and the `.secrets.baseline` file to the repository:

```bash
git add Jenkinsfile .secrets.baseline
git commit -m "Add Jenkins Pipeline configuration and Detect Secrets baseline"
git push origin master
```

### Triggering the Jenkins Pipeline

When the code is pushed to the GitLab repository, a webhook triggers the Jenkins pipeline. Jenkins fetches the `Jenkinsfile` and executes the defined stages.

#### Jenkins Pipeline Execution

The Jenkins pipeline performs the following steps:

1. **Lint Dockerfile**: Runs Hadolint to ensure the Dockerfile adheres to best practices.
2. **Detect Secrets**: Uses `detect-secrets-hook` to check for new secrets based on the baseline.

### Handling Secrets Detection

If new secrets are detected, the pipeline fails, preventing the commit from being merged. This ensures that sensitive information does not accidentally leak into the codebase.

#### Example of Secret Detection

Suppose a developer adds a new secret to the codebase:

```python
API_KEY = "abc123def456ghi789"
```

When the pipeline runs, `detect-secrets-hook` identifies this new secret and fails the build:

```plaintext
[Pipeline] { (Detect Secrets)
[Pipeline] sh
+ detect-secrets-hook pre-commit
New secrets found!
Aborting commit.
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
ERROR: script returned exit code 1
Finished: FAILURE
```

### How to Prevent / Defend Against Secret Leaks

#### Secure Coding Practices

1. **Use Environment Variables**: Store secrets in environment variables instead of hardcoding them in the codebase.
2. **Use Secret Management Tools**: Utilize tools like HashiCorp Vault or AWS Secrets Manager to manage secrets securely.
3. **Educate Developers**: Train developers on best practices for handling secrets and the importance of security.

#### Secure Configuration

1. **Enable Secret Scanning**: Ensure that secret scanning tools like `detect-secrets` are enabled and configured correctly.
2. **Set Up Webhooks**: Configure webhooks to trigger security scans automatically when code is pushed to the repository.
3. **Automate Remediation**: Set up automated remediation processes to address detected secrets promptly.

#### Real-World Examples

Recent breaches highlight the importance of automated secret detection:

- **CVE-2021-22204**: A misconfigured AWS S3 bucket exposed sensitive data due to hardcoded credentials in the codebase.
- **GitHub Token Leak**: In 2021, a GitHub token was leaked due to a developer accidentally committing it to the repository.

### Complete Example

#### Full HTTP Request and Response

Here is a complete example of a HTTP request and response for triggering the Jenkins pipeline:

```http
POST /job/your-job/build HTTP/1.1
Host: jenkins.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic YWRtaW46cGFzc3dvcmQ=

token=your-token
```

Response:

```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 00:00:00 GMT
Location: http://jenkins.example.com/job/your-job/1/
Content-Length: 0
```

#### Jenkinsfile with Secure Coding Fixes

Compare the insecure and secure versions of the Jenkinsfile:

**Insecure Version**

```groovy
pipeline {
    agent any

    stages {
        stage('Lint Dockerfile') {
            steps {
                sh 'docker run --rm hadolint/hadolint hadolint Dockerfile'
            }
        }

        stage('Detect Secrets') {
            steps {
                sh 'detect-secrets-hook pre-commit'
            }
        }
    }
}
```

**Secure Version**

```groovy
pipeline {
    agent any

    environment {
        API_KEY = credentials('api-key')
    }

    stages {
        stage('Lint Dockerfile') {
            steps {
                sh 'docker run --rm hadolint/hadolint hadolint Dockerfile'
            }
        }

        stage('Detect Secrets') {
            steps {
                sh 'detect-secrets-hook pre-commit'
            }
        }
    }
}
```

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide a controlled environment to practice and understand the concepts covered in this chapter.

### Conclusion

Automating code security testing is crucial for maintaining the integrity and security of your codebase. By integrating tools like `detect-secrets` into your CI/CD pipeline, you can proactively identify and mitigate potential security risks. This chapter provided a comprehensive guide to setting up and using these tools effectively, ensuring your code remains secure throughout the development lifecycle.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/04-Demo Detecting New Secrets during Automated Security Testing/01-Introduction to Automating Code Security Testing|Introduction to Automating Code Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/04-Demo Detecting New Secrets during Automated Security Testing/00-Overview|Overview]] | [[03-Automating Code Security Testing Detecting New Secrets|Automating Code Security Testing Detecting New Secrets]]
