---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Automating Code Security Testing: Detecting New Secrets

### Introduction to Secret Detection in Codebases

In the realm of DevSecOps, one critical aspect is ensuring that sensitive information, such as API keys, database credentials, and other secrets, does not inadvertently end up in the codebase. This can happen due to human error, oversight, or even malicious intent. The detection of these secrets is crucial to maintaining the security posture of an organization.

#### What Are Secrets?

Secrets are pieces of sensitive data that should remain confidential. They include:

- **API Keys**: Used to authenticate requests to APIs.
- **Database Credentials**: Username and password combinations used to access databases.
- **SSH Keys**: Used for secure remote connections.
- **Tokens**: Used for authentication and authorization in various systems.

#### Why Detect Secrets in Codebases?

Detecting secrets in codebases is essential because:

- **Exposure Risk**: If secrets are committed to a public repository, they can be easily accessed by unauthorized individuals.
- **Compliance Issues**: Many regulations require the protection of sensitive data. Exposure can lead to legal consequences.
- **Reputation Damage**: Public exposure of secrets can damage an organization's reputation.

### How Secrets Can End Up in Codebases

Secrets can end up in codebases through various means:

- **Human Error**: Developers might accidentally commit sensitive files or copy-paste code containing secrets.
- **Misconfiguration**: Incorrectly configured build scripts or environment variables might expose secrets.
- **Malicious Intent**: An insider threat might intentionally commit secrets to cause harm.

### Real-World Examples

Recent breaches highlight the importance of secret detection:

- **GitHub Data Breach (CVE-2021-22205)**: In 2021, GitHub experienced a data breach where sensitive information was exposed due to misconfigured repositories.
- **Tesla Data Leak (2021)**: Tesla faced a data leak where sensitive internal documents were exposed on a public GitHub repository.

These incidents underscore the need for robust secret detection mechanisms.

### Automating Secret Detection

Automating secret detection is a key practice in DevSecOps. Tools like `TruffleHog`, `GitGuardian`, and `Gitleaks` can be integrated into the CI/CD pipeline to scan for secrets.

#### TruffleHog Example

TruffleHog is a tool that detects high entropy strings that may be secrets. Here’s how to set it up:

```bash
pip install trufflehog
trufflehog --entropy=True .
```

This command scans the current directory for secrets.

#### GitGuardian Example

GitGuardian provides a more comprehensive solution with real-time scanning capabilities. Here’s how to integrate it into a CI/CD pipeline using GitHub Actions:

```yaml
name: Secret Detection

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  secret-detection:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Install GitGuardian
      run: |
        curl -s https://get.gitguardian.com | bash

    - name: Run GitGuardian
      run: |
        ggshield secret scan --all
```

This workflow integrates GitGuardian into the CI/CD pipeline to scan for secrets on every push and pull request.

### Detecting New Secrets During Automated Security Testing

Let's delve deeper into the scenario where the detect new secret stage fails because secrets were added to the codebase without verification.

#### Scenario Explanation

Consider a CI/CD pipeline where a new commit introduces a file containing a secret. The pipeline includes a secret detection stage that fails if any secrets are found.

```yaml
name: Secret Detection Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  secret-detection:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Install GitGuardian
      run: |
        curl -s https://get.gitguardian.com | bash

    - name: Run GitGuardian
      run: |
        ggshield secret scan --all
      env:
        GG_API_KEY: ${{ secrets.GG_API_KEY }}
```

If a developer commits a file with a secret, the `ggshield secret scan --all` command will fail, indicating that secrets were detected.

### Full HTTP Request and Response Example

Here’s a full HTTP request and response example showing how a secret might be exposed via an HTTP request:

```http
POST /api/v1/data HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer <secret_token>

{
  "data": "sensitive information"
}
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 34

{
  "status": "success",
  "message": "Data received"
}
```

In this example, the `Authorization` header contains a secret token. If this request is logged or intercepted, the secret could be exposed.

### How to Prevent / Defend Against Secret Exposure

#### Secure Coding Practices

1. **Environment Variables**: Store secrets in environment variables rather than hardcoding them.
2. **Configuration Management**: Use tools like Ansible, Terraform, or Kubernetes secrets management to manage secrets securely.
3. **Least Privilege Principle**: Ensure that services and applications have the minimum permissions necessary.

#### Detection Mechanisms

1. **Static Analysis Tools**: Integrate tools like TruffleHog, GitGuardian, or Gitleaks into the CI/CD pipeline.
2. **Real-Time Scanning**: Use tools like GitGuardian that provide real-time scanning capabilities.

#### Secure Code Fix Example

**Vulnerable Code**:

```python
import requests

def fetch_data():
    url = "https://example.com/api/v1/data"
    headers = {
        "Authorization": "Bearer my_secret_token"
    }
    response = requests.get(url, headers=headers)
    return response.json()
```

**Secure Code**:

```python
import os
import requests

def fetch_data():
    url = "https://example.com/api/v1/data"
    headers = {
        "Authorization": f"Bearer {os.getenv('SECRET_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    return response.json()
```

In the secure version, the secret token is stored in an environment variable (`SECRET_TOKEN`) and accessed using `os.getenv`.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Ignoring Warnings**: Ignoring warnings from secret detection tools can lead to exposure.
2. **Manual Oversight**: Relying solely on manual checks can result in missed secrets.
3. **Incomplete Scans**: Not scanning all parts of the codebase can leave vulnerabilities unaddressed.

#### Best Practices

1. **Regular Audits**: Regularly audit the codebase for secrets.
2. **Training and Awareness**: Train developers on secure coding practices and the importance of secret management.
3. **Continuous Monitoring**: Continuously monitor the codebase for secrets using automated tools.

### Hands-On Labs

To gain practical experience with secret detection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on secure coding practices and secret management.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice finding and fixing secrets.
- **DVWA (Damn Vulnerable Web Application)**: Another vulnerable web application for practicing security testing.

### Conclusion

Automating secret detection is a critical component of DevSecOps. By integrating tools like TruffleHog, GitGuardian, and Gitleaks into the CI/CD pipeline, organizations can proactively identify and mitigate the risk of secret exposure. Understanding the mechanics of secret detection, the potential risks, and the best practices for prevention is essential for maintaining a secure codebase.

---
<!-- nav -->
[[02-Automating Code Security Testing Detecting New Secrets During Automated Security Testing|Automating Code Security Testing Detecting New Secrets During Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/04-Demo Detecting New Secrets during Automated Security Testing/00-Overview|Overview]] | [[04-Setting Up a Pipeline for Automated Security Testing|Setting Up a Pipeline for Automated Security Testing]]
