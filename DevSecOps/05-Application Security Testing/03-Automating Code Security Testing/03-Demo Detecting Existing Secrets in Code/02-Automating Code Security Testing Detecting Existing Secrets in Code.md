---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Automating Code Security Testing: Detecting Existing Secrets in Code

### Introduction to Code Security Testing

Automating code security testing is a critical component of modern DevSecOps practices. One of the most common issues in software development is the accidental inclusion of sensitive information, such as API keys, passwords, or private keys, within the codebase. These secrets can be inadvertently committed to version control systems like Git, leading to potential security breaches. This chapter will focus on using automated tools to detect and mitigate these issues, specifically using TruffleHog as an example.

### Setting Up the Environment

Before diving into the specifics of detecting secrets, we need to set up our environment. We will be working with the OWASP Juice Shop, a deliberately insecure web application designed for security training. Let's begin by cloning the repository:

```bash
git clone https://github.com/bkimminich/juice-shop.git
```

This command clones the entire repository from GitHub. Once the repository is cloned, we can proceed to the next steps.

### Using TruffleHog to Detect Secrets

TruffleHog is a tool designed to find high entropy strings in Git repositories, which often indicate the presence of secrets. To use TruffleHog, we first need to ensure it is installed. TruffleHog is written in Python, so we need to have Python installed on our system.

#### Installing TruffleHog

To install TruffleHog, we can use pip, the Python package installer:

```bash
pip install trufflehog
```

Once TruffleHog is installed, we can run it against our cloned repository:

```bash
trufflehog juice-shop
```

This command will scan the entire repository, including its commit history, for any high entropy strings that may indicate the presence of secrets.

### Understanding TruffleHog's Functionality

TruffleHog works by analyzing the contents of the repository and identifying strings that have high entropy. High entropy strings are those that contain a large amount of randomness, which is often indicative of secrets like API keys or passwords.

#### How TruffleHog Works Under the Hood

TruffleHog uses a combination of techniques to identify potential secrets:

1. **Entropy Calculation**: TruffleHog calculates the entropy of each string in the repository. Strings with high entropy are more likely to be secrets.
2. **Pattern Matching**: TruffleHog also uses regular expressions to match known patterns of secrets, such as API keys or passwords.
3. **Commit History Analysis**: TruffleHog scans the entire commit history of the repository, including deleted commits, to ensure that no secrets are missed.

### Analyzing the Output

When we run TruffleHog against the Juice Shop repository, we get a list of potential secrets found in the repository. Here is an example of the output:

```plaintext
{
    "commit": "abc123",
    "path": "src/main.js",
    "line": 42,
    "reason": "High Entropy String",
    "anonymized": "REDACTED",
    "original": "secret_api_key"
}
```

This output indicates that TruffleHog found a high entropy string in the `main.js` file at line 42. The original string was `secret_api_key`, but it has been anonymized to `REDACTED` in the output.

### Handling False Positives

It is important to note that TruffleHog may produce false positives. Not all high entropy strings are necessarily secrets. Therefore, it is crucial to manually review the findings to determine their validity.

#### Example of a False Positive

Consider the following output:

```plaintext
{
    "commit": "def456",
    "path": "src/utils.js",
    "line": 123,
    "reason": "High Entropy String",
    "anonymized": "REDACTED",
    "original": "random_string_1234567890"
}
```

In this case, the string `random_string_1234567890` may have high entropy but is not a secret. Manually reviewing the context of the string helps in determining whether it is a false positive.

### Preventing Secrets in Code

Preventing secrets from being committed to the codebase is a critical aspect of code security. Here are some best practices to follow:

#### Secure Coding Practices

1. **Environment Variables**: Store secrets in environment variables rather than hardcoding them in the code.
2. **Configuration Management**: Use configuration management tools like Ansible or Terraform to manage secrets securely.
3. **Secrets Management Tools**: Use dedicated secrets management tools like HashiCorp Vault or AWS Secrets Manager to store and manage secrets.

#### Example of Secure Coding

Here is an example of how to securely manage secrets using environment variables:

```javascript
const API_KEY = process.env.API_KEY;
```

In this example, the API key is stored in an environment variable and accessed via `process.env`. This ensures that the secret is not hardcoded in the codebase.

### Hardening the Repository

Hardening the repository involves taking additional steps to ensure that secrets are not accidentally committed. Here are some steps to consider:

1. **Pre-commit Hooks**: Implement pre-commit hooks to automatically run TruffleHog before each commit.
2. **Continuous Integration (CI)**: Integrate TruffleHog into the CI pipeline to automatically scan the repository for secrets.
3. **Regular Audits**: Perform regular audits of the repository to ensure that no secrets are present.

#### Example of Pre-commit Hook

Here is an example of a pre-commit hook that runs TruffleHog:

```bash
#!/bin/sh
trufflehog --entropy-only .
if [ $? -ne 0 ]; then
  echo "TruffleHog found potential secrets. Aborting commit."
  exit 1
fi
```

This script runs TruffleHog before each commit and aborts the commit if any potential secrets are found.

### Real-World Examples

Several real-world examples highlight the importance of preventing secrets in code. One notable example is the 2019 GitHub data breach, where an attacker gained access to GitHub's internal systems by exploiting a secret stored in a public repository.

#### CVE-2019-10229

CVE-2019-10229 is a vulnerability that allowed attackers to gain unauthorized access to GitHub's internal systems by exploiting a secret stored in a public repository. This highlights the importance of ensuring that secrets are not committed to public repositories.

### Conclusion

Automating code security testing is essential for preventing secrets from being committed to the codebase. Tools like TruffleHog can help identify potential secrets, but it is crucial to manually review the findings to ensure accuracy. By following best practices and hardening the repository, we can significantly reduce the risk of secrets being exposed.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including code security.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide practical experience in detecting and preventing secrets in code, helping to reinforce the concepts covered in this chapter.

### Summary

In summary, automating code security testing is a critical aspect of modern DevSecOps practices. By using tools like TruffleHog, we can detect potential secrets in the codebase and take steps to prevent them from being committed. Following best practices and hardening the repository further reduces the risk of secrets being exposed.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/03-Demo Detecting Existing Secrets in Code/01-Introduction to Automating Code Security Testing|Introduction to Automating Code Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/03-Demo Detecting Existing Secrets in Code/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/03-Demo Detecting Existing Secrets in Code/03-Practice Questions & Answers|Practice Questions & Answers]]
