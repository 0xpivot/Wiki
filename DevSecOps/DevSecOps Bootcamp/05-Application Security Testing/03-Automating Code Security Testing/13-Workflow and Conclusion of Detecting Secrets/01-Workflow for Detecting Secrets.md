---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Workflow for Detecting Secrets

### Introduction

Automating code security testing is crucial in modern DevSecOps practices. One of the key aspects of this automation is the detection of secrets within the codebase. Secrets can include API keys, database credentials, encryption keys, and other sensitive information that, if exposed, can lead to significant security breaches. This chapter will delve into the workflow for detecting secrets, the tools involved, and how to integrate these processes into your continuous integration/continuous deployment (CI/CD) pipeline.

### Step-by-Step Workflow

#### 1. Generate a Baseline

The first step in the workflow is to generate a baseline. This baseline consists of two main components:

1. **List of Current Secrets**: This is a comprehensive list of all the secrets currently present in the codebase. These secrets might have been intentionally added for development purposes or accidentally committed.
   
2. **Configuration Settings for the Tool**: This includes the settings required to configure the tool you are using for secret detection. These settings can vary based on the specific tool but generally include parameters such as the types of secrets to look for, the locations to search, and the sensitivity of the detection.

**Example Configuration**:

```json
{
  "plugins": {
    "github": true,
    "google_api_key": true,
    "slack_token": true
  },
  "paths_to_search": [
    "src/",
    "config/"
  ],
  "exclude_paths": [
    ".git",
    "node_modules"
  ]
}
```

In this example, the `plugins` section specifies which types of secrets to detect, the `paths_to_search` section defines the directories to scan, and the `exclude_paths` section lists directories to ignore.

#### 2. Audit the List of Secrets

Once the baseline is generated, the next step is to audit the list of secrets. This involves checking each identified secret to determine whether it is a false positive or a legitimate secret. 

**False Positives**: False positives occur when the tool incorrectly identifies a piece of data as a secret. This can happen due to the tool's sensitivity settings or the presence of similar patterns in non-sensitive data.

**Legitimate Secrets**: Legitimate secrets are actual sensitive pieces of information that need to be managed carefully.

**Audit Process**:

```bash
detect-secrets audit --baseline baseline.json
```

This command runs the audit process using the baseline file `baseline.json`. The output will list each detected secret along with its location in the codebase.

**Example Output**:

```plaintext
Secret found at src/config.js:12
Secret type: Google API Key
Secret value: AIzaSyD1234567890abcdefg
```

#### 3. Add the Baseline to the Repository

After auditing the list of secrets, the next step is to add the baseline to the repository. This ensures that the baseline is version-controlled and can be referenced in future builds.

**Adding to Repository**:

```bash
git add baseline.json
git commit -m "Add initial baseline for secret detection"
git push origin main
```

#### 4. Compare Results with the Current Baseline

For every build or scan, the results should be compared with the current baseline. This comparison helps identify any new secrets that have been added since the last baseline was generated.

**Comparison Process**:

```bash
detect-secrets scan --baseline baseline.json
```

If new secrets are detected, the build should either warn or fail depending on the organization's policies.

**Example Output**:

```plaintext
New secret detected at src/new_config.js:15
Secret type: Slack Token
Secret value: xoxp-1234567890-abcdefg
```

#### 5. Update the Baseline

If new secrets are detected and deemed necessary, the baseline should be updated to reflect these changes. This ensures that the new secrets are included in future scans and comparisons.

**Updating the Baseline**:

```bash
detect-secrets audit --update-baseline baseline.json
```

This command updates the baseline file with the new secrets.

### Tools for Secret Detection

One of the most popular tools for secret detection is **Detect Secrets**. Detect Secrets is an open-source tool designed to find secrets in your codebase. It supports a wide range of secret types, including API keys, database credentials, and encryption keys.

#### Detect Secrets Architecture

Detect Secrets has a highly pluggable architecture, allowing users to customize the types of secrets to detect and the locations to search. This flexibility makes it suitable for various environments and codebases.

**Mermaid Diagram: Detect Secrets Architecture**

```mermaid
graph TD
  A[Detect Secrets] --> B[Plugins]
  B --> C[Google API Key]
  B --> D[Slack Token]
  B --> E[AWS Access Key]
  A --> F[Paths to Search]
  F --> G[src/]
  F --> H[config/]
  A --> I[Exclude Paths]
  I --> J[.git]
  I --> K[node_modules]
```

#### Customization

Detect Secrets is highly customizable, allowing users to tailor the tool to their specific needs. This customization can include adjusting the sensitivity of the detection, specifying the types of secrets to look for, and defining the paths to search.

**Customization Example**:

```json
{
  "plugins": {
    "google_api_key": {
      "blacklist": ["AIzaSy"]
    }
  },
  "paths_to_search": [
    "src/",
    "config/"
  ],
  "exclude_paths": [
    ".git",
    "node_modules"
  ]
}
```

In this example, the `blacklist` parameter is used to exclude certain patterns from being detected as Google API keys.

### Advantages of Using Secret Detection Tools

#### Quick Wins

One of the primary advantages of using secret detection tools is the ability to achieve quick wins. These tools can quickly identify and flag sensitive information, allowing teams to address security issues promptly.

#### Overview of Current Status

Another significant advantage is the creation of an overview of the current status of secrets in the codebase. This overview provides visibility into the types and locations of secrets, making it easier to manage and secure them.

#### Gradual Removal

Having an overview of the current status also facilitates the gradual removal of secrets from the codebase. Teams can prioritize the removal of high-risk secrets and systematically reduce the overall risk.

### Compatibility

Most secret detection tools are compatible with existing tooling and workflows. They typically support Git-based workflows and can integrate seamlessly with CI/CD pipelines.

**Git Integration**:

Secret detection tools often understand Gitignore files, allowing them to exclude certain directories from the scan. This ensures that only relevant parts of the codebase are scanned.

**Plain Text Files**:

Almost all secret detection tools work with plain text files, making them suitable for a wide range of codebases and languages.

### Real-World Examples

#### Recent Breaches

Recent breaches have highlighted the importance of secret management. For example, in 2021, a breach involving a misconfigured AWS S3 bucket led to the exposure of sensitive data. This incident underscores the need for robust secret detection and management practices.

#### CVEs

CVEs related to secret exposure have also increased in recent years. For instance, CVE-2021-3129 involved the exposure of AWS access keys in a Docker image. This CVE highlights the importance of scanning Docker images for secrets.

### How to Prevent / Defend

#### Detection

To effectively detect secrets, organizations should integrate secret detection tools into their CI/CD pipelines. This ensures that every build or scan includes a secret detection step.

**Detection Example**:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install detect-secrets
      - name: Run secret detection
        run: detect-secrets scan --baseline baseline.json
```

In this example, the secret detection step is integrated into a GitHub Actions workflow.

#### Prevention

Preventing secret exposure involves several strategies:

1. **Environment Variables**: Store secrets in environment variables rather than hardcoding them in the codebase.
   
2. **Secret Management Tools**: Use secret management tools like HashiCorp Vault or AWS Secrets Manager to securely store and manage secrets.

3. **Code Reviews**: Implement strict code reviews to catch any accidental inclusion of secrets in the codebase.

#### Secure Coding Fixes

**Vulnerable Code**:

```javascript
const config = {
  db: {
    username: 'admin',
    password: 'password123'
  }
};
```

**Secure Code**:

```javascript
const config = {
  db: {
    username: process.env.DB_USERNAME,
    password: process.env.DB_PASSWORD
  }
};
```

In the secure version, the secrets are stored in environment variables, reducing the risk of exposure.

#### Configuration Hardening

Hardening configurations involves securing the settings of the secret detection tool and ensuring that the tool itself is configured securely.

**Hardened Configuration**:

```json
{
  "plugins": {
    "google_api_key": {
      "blacklist": ["AIzaSy"]
    }
  },
  "paths_to_search": [
    "src/",
    "config/"
  ],
  "exclude_paths": [
    ".git",
    "node_modules"
  ],
  "sensitivity": "high"
}
```

In this example, the `sensitivity` parameter is set to `high`, increasing the tool's sensitivity to potential secrets.

### Hands-On Labs

For hands-on practice with secret detection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on secret detection and management.
- **OWASP Juice Shop**: Provides a vulnerable application for practicing secret detection.
- **DVWA**: Another vulnerable application for practicing security testing.

These labs provide practical experience in integrating secret detection into CI/CD pipelines and managing secrets effectively.

### Conclusion

Automating code security testing, particularly secret detection, is essential in modern DevSecOps practices. By following the workflow outlined in this chapter, organizations can effectively detect and manage secrets in their codebases. Integrating secret detection tools into CI/CD pipelines ensures that security is a core part of the development process, reducing the risk of exposure and enhancing overall security posture.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/13-Workflow and Conclusion of Detecting Secrets/00-Overview|Overview]] | [[02-Automating Code Security Testing Workflow and Conclusion of Detecting Secrets|Automating Code Security Testing Workflow and Conclusion of Detecting Secrets]]
