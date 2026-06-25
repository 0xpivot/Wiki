---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Introduction to Secrets Management

### What Are Secrets?

In the context of software development and operations, **secrets** are sensitive information that should be kept confidential. This includes passwords, API keys, database connection strings, encryption keys, and other sensitive data. These secrets are crucial for the proper functioning of applications but can pose significant security risks if mishandled.

### Why Manage Secrets?

Managing secrets effectively is essential for maintaining the security and integrity of your applications. Poorly managed secrets can lead to unauthorized access, data breaches, and other security vulnerabilities. In this chapter, we will delve into the reasons why secrets management is necessary, explore various methods for managing secrets, and discuss best practices for securing sensitive information.

### The Problem with Committing Secrets to Code Repositories

One of the most common mistakes in software development is committing sensitive information directly into code repositories. This practice is fraught with risks:

- **Exposure in Git History**: Even if you remove a secret from the codebase, it remains in the Git history. Anyone with access to the repository can retrieve the secret using commands like `git log` or `git blame`.
- **Accidental Exposure**: Developers might inadvertently check in secrets due to human error. This can happen during rushed deployments or when developers are unaware of the sensitive nature of certain information.
- **Security Audits**: During security audits, auditors can easily find and report on the presence of secrets in the codebase, leading to compliance issues and potential fines.

#### Real-World Example: GitHub Data Breach

In 2021, a GitHub user mistakenly committed their AWS access key and secret key to a public repository. This led to unauthorized access to their AWS account, resulting in significant financial losses. This incident highlights the importance of avoiding such mistakes and implementing robust secrets management practices.

### Secret Scanning Tools

To mitigate the risk of accidental exposure, many organizations implement secret scanning tools. These tools automatically scan code repositories for sensitive information and alert developers when secrets are detected.

#### Example: TruffleHog

TruffleHog is an open-source tool that scans Git repositories for secrets. It supports various types of secrets, including AWS keys, Google API keys, and more. Here’s how you can use TruffleHog:

```bash
pip install trufflehog
trufflehog --entropy=False https://github.com/yourusername/yourrepository.git
```

This command scans the specified repository for secrets and outputs any findings.

### Rotating Exposed Secrets

If a secret is found in the Git history, it must be rotated immediately. This involves generating a new secret and updating all systems that rely on the old secret.

#### Example: Rotating AWS Access Keys

AWS provides a mechanism to rotate access keys. You can generate a new access key pair and update your applications to use the new keys.

```bash
# Generate a new access key
aws iam create-access-key --user-name your-user-name

# Output the new access key ID and secret access key
{
    "AccessKey": {
        "UserName": "your-user-name",
        "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "Status": "Active",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "CreateDate": "2023-10-01T00:00:00Z"
    }
}
```

After generating the new keys, update your applications to use the new access key ID and secret access key.

### Alternatives to Committing Secrets

Given the risks associated with committing secrets to code repositories, alternative methods must be employed to manage secrets securely.

#### Using Environment Variables

One approach is to use environment variables to store secrets. This method involves creating placeholders in the secret manifest file and referencing these placeholders from environment variables set in the CI/CD pipeline.

##### Example: GitLab CI/CD Pipeline

In GitLab, you can create environment variables in the CI/CD settings and reference them in your `.gitlab-ci.yml` file.

```yaml
stages:
  - build
  - deploy

variables:
  DATABASE_PASSWORD: $DATABASE_PASSWORD

build:
  stage: build
  script:
    - echo "Building with database password: $DATABASE_PASSWORD"

deploy:
  stage: deploy
  script:
    - echo "Deploying with database password: $DATABASE_PASSWORD"
```

However, this approach has several drawbacks:

- **Scalability Issues**: Managing multiple secrets across different environments can become cumbersome.
- **Risk of Exposure**: Secrets can be exposed during pipeline execution if not handled carefully.

### Using a Dedicated Secrets Manager

A dedicated secrets manager is designed specifically to handle secrets securely. These tools provide features such as encryption, access control, and audit logging, making them a more reliable solution for managing secrets.

#### Example: AWS Secrets Manager

AWS Secrets Manager is a service that helps you protect access to your applications, services, and IT resources without the upfront investment and on-going maintenance costs of operating your own infrastructure.

##### Setting Up AWS Secrets Manager

1. **Create a Secret**: Use the AWS Management Console or the AWS CLI to create a new secret.

```bash
aws secretsmanager create-secret \
    --name MyDatabaseSecret \
    --secret-string '{"username":"myuser","password":"mypassword"}'
```

2. **Retrieve a Secret**: Retrieve the secret value using the AWS CLI.

```bash
aws secretsmanager get-secret-value --secret-id MyDatabaseSecret
```

3. **Integrate with Applications**: Integrate your applications with AWS Secrets Manager to dynamically fetch secrets at runtime.

```python
import boto3

def get_secret():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='MyDatabaseSecret')
    return response['SecretString']

secret = get_secret()
print(secret)
```

### Best Practices for Secrets Management

#### How to Prevent / Defend

1. **Use a Dedicated Secrets Manager**: Leverage tools like AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault to manage secrets securely.
2. **Implement Access Controls**: Ensure that only authorized personnel have access to secrets. Use role-based access control (RBAC) to limit permissions.
3. **Audit Logs**: Enable audit logs to track who accessed which secrets and when. This helps in detecting unauthorized access attempts.
4. **Regular Rotation**: Rotate secrets regularly to minimize the window of opportunity for attackers.
5. **Secure Environment Variables**: Use encrypted environment variables and ensure they are not logged or exposed in pipeline output.

### Conclusion

Effective secrets management is crucial for maintaining the security and integrity of your applications. By avoiding the pitfalls of committing secrets to code repositories and leveraging dedicated secrets managers, you can significantly reduce the risk of unauthorized access and data breaches.

### Practice Labs

For hands-on experience with secrets management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on secure coding practices, including handling secrets.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security testing and penetration testing.
- **CloudGoat**: A series of labs for learning about cloud security best practices, including secrets management.

By following these best practices and engaging in hands-on labs, you can master the art of secrets management and ensure the security of your applications.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Why Secrets Manager are needed/02-Introduction to Secrets Management in Kubernetes|Introduction to Secrets Management in Kubernetes]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Why Secrets Manager are needed/00-Overview|Overview]] | [[04-Introduction to Secrets Management Part 2|Introduction to Secrets Management Part 2]]
